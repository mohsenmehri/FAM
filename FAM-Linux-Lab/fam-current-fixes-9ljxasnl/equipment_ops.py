"""Bounded Equipment Management API for FAM.

The browser submits device credentials over its existing HTTPS FAM session.
The FAM server itself then opens one direct, bounded SSH session to the device
through the one-shot ``equipment_probe.py`` helper (Windows OpenSSH ssh.exe).
No device credential, job, or CLI output is stored in FAM's database, files,
URL, command line, or normal logs.  No connector broker or connector endpoints are registered.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import time

from flask import g, jsonify
try:
    from .equipment_probe import descriptions_table, ProbeError, ENV_PASSTHROUGH
    from .equipment_guard import EquipmentGuard, AdmissionError
except ImportError:
    from equipment_probe import descriptions_table, ProbeError, ENV_PASSTHROUGH
    from equipment_guard import EquipmentGuard, AdmissionError

INTERFACE = re.compile(r"[A-Za-z][A-Za-z0-9/.-]{0,63}\Z")
# Same allowlist as equipment_probe.USERNAME: the name is passed to ssh.exe -l
# and echoed into the askpass prompt, so control/option-like input is refused here.
USERNAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._@\\-]{0,63}\Z")
# Outer wall clock for the helper process per operation.  It must exceed
# equipment_probe.HELPER_DEADLINE (30 / 85 s) so the backend never kills the
# helper while it is still supervising an ssh.exe child. Replacement allows
# 150s helper / 160s executor, below the existing 180s admission lease.
EXECUTOR_TIMEOUT = {"status": 40, "inspect": 65, "descriptions": 40, "recover": 95, "diagnose": 95, "replacement-plan": 80, "replacement-apply": 160, "group-plan": 110, "group-apply": 160, "mac-plan": 95, "mac-apply": 95}
# RFC1918 plus the user-authorized building/shared-address range (RFC6598).
# Deliberately not all of 100/8 or arbitrary public targets.
ALLOWED_IPV4_NETWORKS = tuple(ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10"))


def _secrets(value):
    """Every credential bound to this request, empties dropped.

    A caller-supplied enable secret is a second credential; an empty string
    would match every response body, so it is filtered instead of trusted.
    """
    return tuple(secret for secret in (value.get("username"), value.get("password"), value.get("enable")) if secret)


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


# Which rule rejected a request, never what its secret value was.
_INPUT_REASON = {
    "shape": "شکل درخواست با قالب ثابت فام نمی‌خواند (کلید کم یا اضافه).",
    "types": "IP، نام کاربری یا رمز عبور رشته نیست.",
    "host": "IP قابل تشخیص نیست.",
    "network": "IP در فهرست شبکه‌های مجاز داخلی نیست.",
    "blank": "برای حساب انتخاب‌شده (RADIUS یا محلی) نام کاربری یا رمز عبور وارد نشده است؛ گفت‌وگوی حساب را کامل کنید.",
    "username": "نام کاربری با قالب اتصال تجهیزات نمی‌خواند.",
    "password": "رمز عبور باید ۱ تا ۵۱۲ نویسه باشد.",
    "passwordChars": "رمز عبور فقط می‌تواند نویسهٔ ASCII قابل‌چاپ باشد.",
    "enable": "رمز enable فقط می‌تواند ۱ تا ۵۱۲ نویسهٔ ASCII قابل‌چاپ باشد.",
    "recovery": "نام پورت یا رشتهٔ تأیید معتبر نیست.",
}


def _input_failure(exc):
    """The generic 400 line plus the rule that fired, so a dead end is readable."""
    reason = str(exc or "").strip()
    base = "IP داخلی مجاز، نام کاربری و رمز تجهیز معتبر نیست."
    if reason in _INPUT_REASON:
        return base + " علت: " + _INPUT_REASON[reason]
    # A reasonless ValueError did not come from these rules: name whose it was
    # instead of letting it masquerade as a credential problem.
    return base + " علت: خطای ناشناخته از لایهٔ خواندن بدنه؛ پاسخ سرور را ببینید."


def _input(value, *, recovery=False, diagnosis=False):
    optional = {"enable"} if isinstance(value, dict) and "enable" in value else set()
    expected = {"host", "username", "password"} | optional | ({"interface", "ticket"} if recovery else {"clientIp", "clientMac"} if diagnosis else set())
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("shape")
    host, username, password = value["host"], value["username"], value["password"]
    if not isinstance(host, str) or not isinstance(username, str) or not isinstance(password, str):
        raise ValueError("types")
    try:
        address = ipaddress.ip_address(host.strip())
    except ValueError as exc:
        raise ValueError("host") from exc
    if not isinstance(address, ipaddress.IPv4Address) or not any(address in network for network in ALLOWED_IPV4_NETWORKS):
        raise ValueError("network")
    username = username.strip()
    # An empty credential is a different problem from a bad one: it means the
    # account dialog was never completed for the selected RADIUS/local mode (or
    # it expired), and the operator has to be told exactly that.
    if not username or not password:
        raise ValueError("blank")
    if not USERNAME.fullmatch(username) or not 1 <= len(password) <= 512:
        raise ValueError("username" if not USERNAME.fullmatch(username) else "password")
    # The password only ever travels through an environment variable into the
    # ssh.exe child; keep it to printable ASCII so no code-page translation or
    # control character can alter it on the way.
    if not all(0x20 <= ord(char) <= 0x7E for char in password):
        raise ValueError("passwordChars")
    # The enable secret is optional and deliberately separate from the login
    # password: on real devices the two are almost never the same string.  It
    # uses the same printable-ASCII bound and only ever travels into the ssh
    # child stdin, never argv, a URL or stored state.
    enable = value.get("enable", "")
    if not isinstance(enable, str) or (enable and not (1 <= len(enable) <= 512 and all(0x20 <= ord(char) <= 0x7E for char in enable))):
        raise ValueError("enable")
    result = {"host": str(address), "username": username, "password": password}
    if enable:
        result["enable"] = enable
    if recovery:
        interface, ticket = value["interface"], value["ticket"]
        if not isinstance(interface, str) or not INTERFACE.fullmatch(interface) or not isinstance(ticket, str) or not 40 <= len(ticket) <= 1024:
            raise ValueError("recovery")
        result |= {"interface": interface, "ticket": ticket}
    if diagnosis:
        if __package__:from .equipment_diagnostics import client
        else:from equipment_diagnostics import client
        target=client(value['clientIp'],value['clientMac'])
        result.update(clientIp=target['ip'],clientMac=target['mac'])
    return result


def _ticket(app, *, user_id, host, username, interface, context=None):
    # The browser needs an opaque one-time ticket, not a copy of its username.
    user_digest = hashlib.sha256(username.encode("utf-8")).hexdigest()
    body={"u": user_id, "h": host, "n": user_digest, "i": interface, "e": int(time.time()) + 300, "j": secrets.token_hex(16)}
    if context is not None:body["context"]=context
    payload = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
    tag = hmac.new(app.config["EQUIPMENT_TICKET_KEY"], payload, hashlib.sha256).digest()
    return _b64(payload) + "." + _b64(tag)


def _verify_ticket(app, value, *, user_id, host, username, interface, context=None):
    try:
        encoded, signature = value.split(".", 1)
        payload, tag = _unb64(encoded), _unb64(signature)
        expected = hmac.new(app.config["EQUIPMENT_TICKET_KEY"], payload, hashlib.sha256).digest()
        decoded = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    user_digest = hashlib.sha256(username.encode("utf-8")).hexdigest()
    return (hmac.compare_digest(tag, expected) and isinstance(decoded, dict) and
            decoded == {"u": user_id, "h": host, "n": user_digest, "i": interface, "e": decoded.get("e"), "j": decoded.get("j"), **({"context":context} if context is not None else {})} and
            type(decoded.get("e")) is int and int(time.time()) <= decoded["e"] <= int(time.time())+300 and
            isinstance(decoded.get("j"),str) and re.fullmatch(r"[a-f0-9]{32}",decoded["j"]) is not None)


def _helper_environment(app):
    """Environment for the helper: minimal allowlisted OS environment plus the
    explicit ssh.exe / host-key settings.  No device credential is placed here;
    the helper receives the job on stdin only."""
    env = {key:os.environ[key] for key in ENV_PASSTHROUGH if key in os.environ}
    for key, name in (("EQUIPMENT_SSH", "FAM_EQUIPMENT_SSH"), ("EQUIPMENT_KNOWN_HOSTS", "FAM_EQUIPMENT_KNOWN_HOSTS"),
                      ("EQUIPMENT_HOST_KEY_POLICY", "FAM_EQUIPMENT_HOST_KEY_POLICY"), ("EQUIPMENT_RUNTIME_DIR", "FAM_EQUIPMENT_RUNTIME_DIR")):
        value = app.config.get(key)
        if value:
            env[name] = str(value)
    return env


def _execute(app, payload):
    override = app.config.get("EQUIPMENT_EXECUTOR")
    if override is not None:
        return override(payload)
    executable = Path(app.config["EQUIPMENT_PYTHON"])
    helper = Path(app.config["EQUIPMENT_HELPER"])
    if not executable.is_file() or not helper.is_file():
        return {"ok": False, "error": "connection_failed"}
    timeout = EXECUTOR_TIMEOUT.get(payload.get("operation"), EXECUTOR_TIMEOUT["status"])
    try:
        completed = subprocess.run(
            [str(executable), str(helper)], input=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout, check=False, env=_helper_environment(app),
        )
        result = json.loads(completed.stdout.decode("utf-8"))
    except subprocess.TimeoutExpired:
        if payload.get("operation") == "mac-apply":return {"ok":False,"error":"mac_uncertain"}
        return {"ok": False, "error": (("group_uncertain" if payload.get("operation")=="group-apply" else "replacement_uncertain") if payload.get("operation") in {"replacement-apply","group-apply"} else "recovery_uncertain") if payload.get("operation") in {"recover","replacement-apply","group-apply"} else "connection_timeout"}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        if payload.get("operation") == "mac-apply":return {"ok":False,"error":"mac_uncertain"}
        return {"ok": False, "error": (("group_uncertain" if payload.get("operation")=="group-apply" else "replacement_uncertain") if payload.get("operation") in {"replacement-apply","group-apply"} else "recovery_uncertain") if payload.get("operation") in {"recover","replacement-apply","group-apply"} else "connection_failed"}
    return result if isinstance(result, dict) else {"ok": False, "error": "connection_failed"}


# These are structural classifications only.  Do not render a raw helper
# field or device output: an unexpected reason falls back to the generic text.
_STATUS_REASON_TEXT = {
    'cli_error': 'سوییچ یکی از فرمان‌های ثابت بررسی را رد کرد.',
    'paged': 'خروجی جدول صفحه‌بندی شد و کامل دریافت نشد.',
    'missing_header': 'سرستون جدول وضعیت در پاسخ دیده نشد.',
    'no_rows': 'سرستون جدول دیده شد، ولی هیچ ردیفی قابل شناسایی نبود.',
    'partial': 'یک یا چند ردیف جدول ناقص، ناشناخته یا تکراری بود.',
}


def _failure(value):
    code = value.get("error") if isinstance(value, dict) else ""
    if code == 'status_unreadable' and isinstance(value,dict):
        reason=value.get('statusReason')
        if isinstance(reason,str) and reason in _STATUS_REASON_TEXT:
            return 'جدول کامل وضعیت پورت‌ها قابل تأیید نیست؛ وضعیت نامشخص است، نه بدون خطا. علت: '+_STATUS_REASON_TEXT[reason]
    return {
        "enable_required": "حساب تجهیز در حالت کاربر (user EXEC) وارد شد؛ فرمان‌های وضعیت به سطح امتیاز نیاز دارد. رمز enable را در گفت‌وگوی حساب وارد کنید و دوباره بررسی کنید؛ هیچ فرمانی اجرا نشد و تغییری اعمال نشده است.",
        "enable_failed": "رمز enable پذیرفته نشد و سطح امتیاز باز نشد؛ هیچ فرمانی اجرا نشد و دوباره تلاش نمی‌شود.",
        "enable_unconfirmed": "درخواست رمز enable یا سطح دسترسی سوییچ قابل تأیید نبود؛ رمز دوباره فرستاده نشد و فرمان بررسی ارسال نشد.",
        "mac_unsupported_platform": "این پلتفرم یا خروجی آن برای این روش قابل تأیید نیست؛ تغییری انجام نشد.",
        "mac_preflight": "پیش‌بررسی پورت، فرمان‌ها یا حفاظت قابل تأیید نیست؛ تغییری انجام نشد.",
        "mac_not_violation": "علت این پورت خطای Port Security نیست؛ تغییری انجام نشد.",
        "mac_changed": "وضعیت یا تنظیمات پورت نسبت به پیش‌بررسی تغییر کرده است؛ تغییری انجام نشد.",
        "mac_quarantined": "رفع کامل تأیید نشد؛ پورت بسته و حفاظت تأیید شد. پیش از اقدام دوباره همان پورت را بررسی کنید.",
        "mac_uncertain": "نتیجه نامشخص است و ممکن است پورت خاموش مانده باشد؛ همان پورت را بررسی کنید. تلاش خودکار دیگری انجام نمی‌شود.",
        "group_preflight": "پیش‌بررسی گروهی کامل نیست؛ فقط پورت access تک‌کلاینت VLAN 100 و رکورد MAC قابل تأیید پشتیبانی می‌شود. پورت قبلی باید خالی/بسته و فاقد binding ثابت برای MAC جابه‌جاشده باشد. تغییری اعمال نشد.",
        "group_old_port_active": "پورت قبلی MAC هنوز متصل یا خطادار است؛ برای جلوگیری از قطع کلاینت فعال حذف انجام نشد. ابتدا جابه‌جایی را با کارشناس بررسی کنید.",
        "group_changed": "شواهد یا تنظیمات گروه از زمان تأیید تغییر کرده؛ تغییری اعمال نشد. دوباره پیش‌بررسی کنید.",
        "group_quarantined": "عملیات گروه کامل نشد؛ همهٔ پورت‌های هدف در shutdown و حفاظت مورد انتظار بررسی شدند. پورت قبلی یا رکوردهای حذف‌شده خودکار برنمی‌گردند؛ بررسی کارشناس لازم است.",
        "group_uncertain": "اثر عملیات گروه نامشخص است؛ ممکن است MAC، IPSG یا binding تغییر کرده باشد. بسته‌بودن/حفاظت همهٔ اعضا تأیید نشد. فوراً پورت‌های هدف و پورت‌های قبلی احتمالی همان سوئیچ را بررسی کنید؛ تکرار خودکار انجام نمی‌شود.",
        "replacement_preflight": "پیش‌بررسی تعویض MAC قابل تأیید نیست: پورت باید access VLAN 100، تک‌کلاینت و دارای IPSG باشد؛ در حالت IP دستی دقیقاً یک binding ثابت و مجوز متناظر Inspection لازم است. تغییری اعمال نشد.",
        "replacement_sticky": "MAC قبلی به‌صورت Sticky/Configured روی پورت ثبت شده است؛ حذف آن در این مسیر مجاز نیست. کارشناس باید همان رکورد را بررسی کند؛ تغییری اعمال نشد.",
        "replacement_changed": "تنظیمات نسبت به پیش‌نمایش تغییر کرده است؛ دوباره بررسی و تأیید کنید. تغییری اعمال نشد.",
        "replacement_quarantined": "تعویض MAC کامل نشد؛ پورت در shutdown و IPSG فعال بررسی شد. پورت را خودکار باز نکنید؛ بررسی کارشناس لازم است.",
        "replacement_uncertain": "اثر عملیات نامشخص است؛ ممکن است IPSG یا binding موقتاً برداشته شده باشد. حفاظت/بسته‌بودن پورت تأیید نشد. فوراً همان پورت را با کارشناس بررسی کنید؛ عملیات تکرار نمی‌شود.",
        "unsupported_platform": "مدل یا نسخهٔ IOS این تجهیز با پروفایل تشخیص WS-C2960-24TT-L قابل تأیید نیست؛ تغییری اعمال نشد.",
        "diagnosis_unreadable": "شواهد تشخیص کامل یا قابل تأیید نیست؛ محل کلاینت نامشخص است. هیچ تغییری اعمال نشد.",
        "recovery_uncertain": "اثر عملیات روی پورت نامشخص است؛ ممکن است shutdown اجرا شده باشد. عملیات متوقف شد؛ پیش از هر اقدام، وضعیت همان پورت را با اپراتور مجاز بررسی کنید. فعال‌سازی خودکار انجام نمی‌شود.",
        "equipment_busy": "تجهیز یا ظرفیت SSH مشغول است؛ عملیات جدیدی اجرا نشد. پس از پایان درخواست قبلی، دوباره وضعیت را بررسی کنید.",
        "ticket_consumed": "این تأیید قبلاً مصرف شده است؛ دوباره بررسی و پورت را تأیید کنید.",
        "authentication_failed": "نام کاربری یا رمز تجهیز پذیرفته نشد.",
        "connection_timeout": "اتصال SSH به تجهیز در زمان مجاز پاسخ نداد.",
        "connection_failed": "بررسی تجهیز انجام نشد؛ دسترسی SSH و وضعیت تجهیز را بررسی کنید.",
        "descriptions_unreadable": "خروجی show int des کامل یا قابل تأیید نیست؛ متن خام دیگری نمایش داده نمی‌شود.",
        "status_unreadable": "اتصال انجام شد اما جدول کامل وضعیت پورت‌ها قابل تأیید نیست؛ وضعیت نامشخص است، نه بدون خطا.",
    }.get(code, "بررسی تجهیز انجام نشد.")


def _ports_or_fail(result, fail):
    if isinstance(result,dict) and result.get('error')=='equipment_busy':fail(429,_failure(result))
    # 428 is the single signal the browser acts on: it reopens the account
    # dialog with the enable field required instead of showing a dead end.
    if isinstance(result,dict) and result.get('error')=='enable_required':fail(428,_failure(result))
    raw_ports = result.get("ports") if isinstance(result, dict) else None
    if not isinstance(result, dict) or result.get("ok") is not True or not isinstance(raw_ports, list):
        fail(502, _failure(result))
    ports = []
    seen = set()
    for item in raw_ports:
        if (not isinstance(item, dict) or set(item) != {"interface", "description"} or
                not isinstance(item["interface"], str) or not INTERFACE.fullmatch(item["interface"]) or
                not isinstance(item["description"], str) or len(item["description"]) > 128 or
                "\r" in item["description"] or "\n" in item["description"] or item["interface"] in seen):
            fail(502, _failure(result))
        seen.add(item["interface"])
        ports.append({"interface": item["interface"], "description": item["description"]})
    return sorted(ports, key=lambda item: item["interface"])


def register_equipment_ops(app, *, data, fail, allowed):
    """Register authenticated browser endpoints for direct server-to-device SSH."""

    guard = EquipmentGuard(app.config['DB_PATH'])
    app.extensions['equipment_guard'] = guard

    def run(payload, ticket=None):
        try:
            with guard.admit(payload['host'],ticket):
                return _execute(app,payload)
        except AdmissionError as error:
            return {'ok':False,'error':error.code}

    def authorize(operation=None,host=None):
        if not app.config["EQUIPMENT_OPS_ENABLED"]:
            fail(404, "مدیریت تجهیزات فعال نشده است.")
        if not allowed(g.user,operation=operation,host=host):
            fail(403, "مجوز مدیریت تجهیزات لازم است.")

    @app.post("/api/equipment/check")
    def equipment_check():
        authorize()
        body = data()
        try:
            value = _input(body)
        except ValueError as exc:
            fail(400, _input_failure(exc))
        authorize("status",value["host"])
        result = run({"operation": "status", **value})
        ports = _ports_or_fail(result, fail)
        tickets = {item["interface"]: _ticket(app, user_id=g.user["id"], host=value["host"], username=value["username"], interface=item["interface"]) for item in ports}
        return jsonify(host=value["host"], source="server-ssh", checkedAt=int(time.time()*1000), errDisabledPorts=ports, recoveryTickets=tickets)

    @app.post('/api/equipment/inspect')
    def equipment_inspect():
        authorize('status')
        body=data()
        try:value=_input(body)
        except ValueError as exc:fail(400,_input_failure(exc))
        authorize('status',value['host'])
        result=run({'operation':'inspect',**value})
        ports=_ports_or_fail(result,fail)
        description={'error':_failure({'error':'descriptions_unreadable'})}
        raw=result.get('descriptions')
        if isinstance(raw,dict) and raw.get('ok') is True:
            try:
                output,redacted=descriptions_table(raw.get('output'),value['username'],value['password'],value.get('enable',''))
                description={'output':output,'redacted':redacted or raw.get('redacted') is True}
            except ProbeError:pass
        timings=result.get('timings',{})
        timings={k:timings[k] for k in ('preparationMs','sshMs') if isinstance(timings,dict) and type(timings.get(k)) is int and 0<=timings[k]<=65000}
        return jsonify(host=value['host'],source='server-ssh',checkedAt=int(time.time()*1000),errDisabledPorts=ports,
            recoveryTickets={p['interface']:_ticket(app,user_id=g.user['id'],host=value['host'],username=value['username'],interface=p['interface']) for p in ports},
            descriptions=description,timings=timings)

    @app.post('/api/equipment/descriptions')
    def equipment_descriptions():
        authorize('descriptions')
        body=data()
        try:value=_input(body)
        except ValueError as exc:fail(400,_input_failure(exc))
        authorize('descriptions',value['host'])
        result=run({'operation':'descriptions',**value})
        if not isinstance(result,dict) or result.get('ok') is not True:fail(428 if isinstance(result,dict) and result.get('error')=='enable_required' else 429 if isinstance(result,dict) and result.get('error')=='equipment_busy' else 502,_failure(result))
        try:output,redacted=descriptions_table(result.get('output'),value['username'],value['password'],value.get('enable',''))
        except ProbeError:fail(502,_failure({'error':'descriptions_unreadable'}))
        return jsonify(host=value['host'],source='server-ssh',checkedAt=int(time.time()*1000),command='show interfaces description',output=output,redacted=redacted or result.get('redacted') is True)

    @app.post('/api/equipment/diagnose')
    def equipment_diagnose():
        authorize('diagnose')
        body=data()
        try:value=_input(body,diagnosis=True)
        except (ValueError,TypeError):fail(400,'IP یا MAC کلاینت و مشخصات اتصال معتبر نیست؛ حداقل یکی از IP/MAC لازم است.')
        authorize('diagnose',value['host'])
        result=run({'operation':'diagnose',**value})
        if not isinstance(result,dict) or result.get('ok') is not True:
            fail(429 if isinstance(result,dict) and result.get('error')=='equipment_busy' else 502,_failure(result))
        try:
            if __package__:from .equipment_diagnostics import validate_report
            else:from equipment_diagnostics import validate_report
            report=validate_report(result.get('report'))
            if report['client']!={'ip':value['clientIp'],'mac':value['clientMac']}:raise ValueError('wrong client')
            if any(secret.casefold() in json.dumps(report).casefold() for secret in _secrets(value)):raise ValueError('sensitive output')
        except (ValueError,TypeError,KeyError):fail(502,_failure({'error':'diagnosis_unreadable'}))
        return jsonify(host=value['host'],source='server-ssh',checkedAt=int(time.time()*1000),report=report)

    @app.post("/api/equipment/recover")
    def equipment_recover():
        fail(503, 'عملیات تغییر تجهیزات موقتاً غیرفعال است؛ بررسی ایمنی SSH لازم است.')
        authorize("recover")
        body = data()
        try:
            value = _input(body, recovery=True)
        except ValueError:
            fail(400, "درخواست بازیابی معتبر نیست.")
        authorize("recover",value["host"])
        ticket=value.pop("ticket")
        if not _verify_ticket(app, ticket, user_id=g.user["id"], host=value["host"], username=value["username"], interface=value["interface"]):
            fail(409, "تأیید بررسی این پورت منقضی شده است؛ ابتدا وضعیت را دوباره بررسی کنید.")
        result = run({"operation": "recover", **value},ticket)
        if not isinstance(result, dict) or result.get("ok") is not True or result.get("recovery") not in {"recovered", "still_errdisabled", "not_errdisabled"}:
            code=result.get('error') if isinstance(result,dict) else None
            code=code if code in {'equipment_busy','ticket_consumed'} else 'recovery_uncertain'
            return jsonify(error=_failure({'error':code}),code=code,requiresRecheck=True), (409 if code=='ticket_consumed' else 429 if code=='equipment_busy' else 502)
        return jsonify(host=value["host"], interface=value["interface"], recovery=result["recovery"])


    def mac_recovery_input(apply=False):
        raw=data()
        fields={'host','username','password','interface'}|({'enable'} if isinstance(raw,dict) and 'enable' in raw else set())|({'ticket','planHash'} if apply else set())
        try:
            if not isinstance(raw,dict) or set(raw)!=fields:raise ValueError('schema')
            if __package__:from . import equipment_mac_recovery as mac_recovery
            else:import equipment_mac_recovery as mac_recovery
            value=_input({key:raw[key] for key in ('host','username','password','enable') if key in raw})
            mac_recovery.interface(raw['interface'])
            value['interface']=raw['interface']
            if apply:
                if not isinstance(raw['planHash'],str) or not mac_recovery.HASH.fullmatch(raw['planHash']) or not isinstance(raw['ticket'],str) or not 40<=len(raw['ticket'])<=1024:raise ValueError('approval')
                value.update(planHash=raw['planHash'],ticket=raw['ticket'])
            return value
        except (ValueError,TypeError,KeyError):fail(400,'درخواست پورت فیزیکی یا تأیید معتبر نیست.')

    @app.post('/api/equipment/mac-recovery/plan')
    def mac_recovery_plan():
        authorize('recover');value=mac_recovery_input()
        authorize('status',value['host']);authorize('recover',value['host'])
        result=run({'operation':'mac-plan',**value})
        if not isinstance(result,dict) or result.get('ok') is not True:
            fail(428 if isinstance(result,dict) and result.get('error')=='enable_required' else 429 if isinstance(result,dict) and result.get('error')=='equipment_busy' else 502,_failure(result))
        try:
            if __package__:from . import equipment_mac_recovery as mac_recovery
            else:import equipment_mac_recovery as mac_recovery
            if set(result)!={'ok','plan'}:raise ValueError('result')
            plan=mac_recovery.validate_plan(result['plan'])
            if plan['interface']!=value['interface']:raise ValueError('target')
        except (ValueError,TypeError,KeyError):fail(502,_failure({'error':'mac_preflight'}))
        context='mac-recovery:'+plan['planHash']
        ticket=_ticket(app,user_id=g.user['id'],host=value['host'],username=value['username'],interface=value['interface'],context=context)
        return jsonify(host=value['host'],source='server-ssh',plan=plan,ticket=ticket)

    @app.post('/api/equipment/mac-recovery/apply')
    def mac_recovery_apply():
        fail(503, 'عملیات تغییر تجهیزات موقتاً غیرفعال است؛ بررسی ایمنی SSH لازم است.')
        authorize('recover');value=mac_recovery_input(True)
        authorize('status',value['host']);authorize('recover',value['host'])
        ticket=value.pop('ticket');context='mac-recovery:'+value['planHash']
        if not _verify_ticket(app,ticket,user_id=g.user['id'],host=value['host'],username=value['username'],interface=value['interface'],context=context):
            fail(409,'تأیید این پورت منقضی یا نامعتبر است؛ دوباره پیش‌بررسی کنید.')
        result=run({'operation':'mac-apply',**value},ticket)
        code=result.get('error') if isinstance(result,dict) else None
        try:
            if not isinstance(result,dict) or set(result)!={'ok','interface','state','protectionPreserved'} or result['ok'] is not True or result['interface']!=value['interface'] or result['state'] not in ('not_errdisabled','still_errdisabled') or result['protectionPreserved'] is not True:
                raise ValueError('result')
        except (ValueError,TypeError,KeyError):
            safe={'equipment_busy','ticket_consumed','mac_changed','mac_not_violation','mac_preflight','mac_unsupported_platform','mac_quarantined','enable_required','enable_failed','enable_unconfirmed'}
            code=code if code in safe else 'mac_uncertain'
            return jsonify(error=_failure({'error':code}),code=code,requiresRecheck=True), (429 if code=='equipment_busy' else 409 if code in ('ticket_consumed','mac_changed') else 502)
        return jsonify(host=value['host'],source='server-ssh',interface=value['interface'],state=result['state'],protectionPreserved=True)

    def replacement_input(apply=False):
        raw=data(); fields={'host','username','password','interface','staticIp'}|({'enable'} if isinstance(raw,dict) and 'enable' in raw else set())|({'ticket','planHash'} if apply else set())
        try:
            if not isinstance(raw,dict) or set(raw)!=fields:raise ValueError('schema')
            value=_input({k:raw[k] for k in ('host','username','password','enable') if k in raw})
            if __package__:from . import equipment_replacement as r
            else:import equipment_replacement as r
            r.interface(raw['interface'])
            if type(raw['staticIp']) is not bool:raise ValueError('static')
            value.update(interface=raw['interface'],staticIp=raw['staticIp'])
            if apply:
                if not isinstance(raw['planHash'],str) or not r.HASH.fullmatch(raw['planHash']) or not isinstance(raw['ticket'],str) or not 40<=len(raw['ticket'])<=1024:raise ValueError('ticket')
                value.update(ticket=raw['ticket'],planHash=raw['planHash'])
            return value
        except (ValueError,TypeError,KeyError):fail(400,'پورت access معتبر و گزینهٔ IP دستی لازم است؛ IP جدید یا دستور آزاد پذیرفته نمی‌شود.')

    @app.post('/api/equipment/replacement/plan')
    def replacement_plan():
        authorize('recover');value=replacement_input()
        authorize('status',value['host']);authorize('recover',value['host'])
        result=run({'operation':'replacement-plan',**value})
        if not isinstance(result,dict) or result.get('ok') is not True:fail(428 if isinstance(result,dict) and result.get('error')=='enable_required' else 429 if isinstance(result,dict) and result.get('error')=='equipment_busy' else 502,_failure(result))
        try:
            if __package__:from . import equipment_replacement as r
            else:import equipment_replacement as r
            plan=r.validate_plan(result.get('plan'))
            if plan['interface']!=value['interface'] or plan['staticIp']!=value['staticIp']:raise ValueError('target')
            if any(secret.casefold() in json.dumps(plan).casefold() for secret in _secrets(value)):raise ValueError('secret')
        except (ValueError,TypeError,KeyError):fail(502,_failure({'error':'replacement_preflight'}))
        context='replacement:'+str(int(value['staticIp']))+':'+plan['planHash']
        ticket=_ticket(app,user_id=g.user['id'],host=value['host'],username=value['username'],interface=value['interface'],context=context)
        return jsonify(host=value['host'],source='server-ssh',plan=plan,ticket=ticket)

    @app.post('/api/equipment/replacement/apply')
    def replacement_apply():
        fail(503, 'عملیات تغییر تجهیزات موقتاً غیرفعال است؛ بررسی ایمنی SSH لازم است.')
        authorize('recover');value=replacement_input(True)
        authorize('status',value['host']);authorize('recover',value['host'])
        ticket=value.pop('ticket');context='replacement:'+str(int(value['staticIp']))+':'+value['planHash']
        if not _verify_ticket(app,ticket,user_id=g.user['id'],host=value['host'],username=value['username'],interface=value['interface'],context=context):fail(409,'پیش‌بررسی و تأیید همین پورت منقضی یا نامعتبر است.')
        result=run({'operation':'replacement-apply',**value},ticket)
        code=result.get('error') if isinstance(result,dict) else None
        try:
            if not isinstance(result,dict) or set(result)!={'ok','replacement','interface','staticIp','ip','oldMac','newMac','protectionRestored'} or result['ok'] is not True or result['replacement']!='replaced' or result['protectionRestored'] is not True:raise ValueError('result')
            if __package__:from . import equipment_replacement as r
            else:import equipment_replacement as r
            if result['interface']!=value['interface'] or type(result['staticIp']) is not bool or result['staticIp']!=value['staticIp'] or r.unicast(result['newMac'])!=result['newMac']:raise ValueError('target')
            if result['oldMac'] and r.unicast(result['oldMac'])!=result['oldMac']:raise ValueError('MAC')
            if value['staticIp']:
                if not result['oldMac'] or result['oldMac']==result['newMac'] or str(ipaddress.IPv4Address(result['ip']))!=result['ip']:raise ValueError('IP')
            elif result['ip']!='':raise ValueError('IP')
            if any(secret.casefold() in json.dumps(result).casefold() for secret in _secrets(value)):raise ValueError('secret')
        except (ValueError,TypeError,KeyError):
            safe={'equipment_busy','ticket_consumed','replacement_changed','replacement_preflight','replacement_sticky','unsupported_platform','replacement_quarantined'}
            code=code if code in safe else 'replacement_uncertain'
            return jsonify(error=_failure({'error':code}),code=code,requiresRecheck=True), (429 if code=='equipment_busy' else 409 if code=='ticket_consumed' else 502)
        return jsonify(host=value['host'],**{k:v for k,v in result.items() if k!='ok'})


    def group_input(apply=False):
        raw=data();fields={'host','username','password','interfaces','mode','staticIp'}|({'ticket','planHash'} if apply else set())|({'enable'} if isinstance(raw,dict) and 'enable' in raw else set())
        try:
            if not isinstance(raw,dict) or set(raw)!=fields:raise ValueError('schema')
            if __package__:from . import equipment_group as group
            else:import equipment_group as group
            value=_input({k:raw[k] for k in ('host','username','password','enable') if k in raw})
            ports=group.interfaces(raw['interfaces'])
            if not isinstance(raw['mode'],str) or raw['mode'] not in ('recover','replace') or type(raw['staticIp']) is not bool or (raw['mode']=='recover' and raw['staticIp']):raise ValueError('mode')
            value.update(interfaces=ports,mode=raw['mode'],staticIp=raw['staticIp'])
            if apply:
                if not isinstance(raw['planHash'],str) or not group.r.HASH.fullmatch(raw['planHash']) or not isinstance(raw['ticket'],str) or not 40<=len(raw['ticket'])<=1024:raise ValueError('approval')
                value.update(ticket=raw['ticket'],planHash=raw['planHash'])
            return value
        except (ValueError,TypeError,KeyError):fail(400,'فهرست دقیق پورت‌های Fa0/1 تا Fa0/24 و حالت عملیات معتبر لازم است؛ IP/MAC جدید یا فرمان آزاد پذیرفته نمی‌شود.')

    @app.post('/api/equipment/group/plan')
    def group_plan():
        authorize('recover');value=group_input()
        authorize('status',value['host']);authorize('recover',value['host'])
        result=run({'operation':'group-plan',**value})
        # The UI may offer the separate, no-MAC-deletion recovery workflow when
        # this exact classic-2960 profile is unsupported. Other failures never
        # trigger a fallback or an authentication retry.
        if isinstance(result,dict) and result.get('error')=='unsupported_platform':
            return jsonify(error=_failure(result),code='unsupported_platform'),502
        if not isinstance(result,dict) or result.get('ok') is not True:fail(428 if isinstance(result,dict) and result.get('error')=='enable_required' else 429 if isinstance(result,dict) and result.get('error')=='equipment_busy' else 502,_failure(result))
        try:
            if __package__:from . import equipment_group as group
            else:import equipment_group as group
            plan=group.validate_plan(result.get('plan'))
            if (plan['interfaces'],plan['mode'],plan['staticIp'])!=(value['interfaces'],value['mode'],value['staticIp']):raise ValueError('wrong target')
            # validate_plan permits only fixed literals, ports, IP/MAC values and
            # a digest; it has no raw-output/free-text field. Substring-searching
            # serialized JSON for credentials also searches keys/literals and
            # rejected perfectly valid short, letters-only credentials.
        except (ValueError,TypeError,KeyError):fail(502,_failure({'error':'group_preflight'}))
        context='group:'+value['mode']+':'+str(int(value['staticIp']))+':'+plan['planHash']
        ticket=_ticket(app,user_id=g.user['id'],host=value['host'],username=value['username'],interface=','.join(value['interfaces']),context=context)
        return jsonify(host=value['host'],source='server-ssh',plan=plan,ticket=ticket)

    @app.post('/api/equipment/group/apply')
    def group_apply():
        fail(503, 'عملیات تغییر تجهیزات موقتاً غیرفعال است؛ بررسی ایمنی SSH لازم است.')
        authorize('recover');value=group_input(True)
        authorize('status',value['host']);authorize('recover',value['host'])
        ticket=value.pop('ticket');context='group:'+value['mode']+':'+str(int(value['staticIp']))+':'+value['planHash']
        if not _verify_ticket(app,ticket,user_id=g.user['id'],host=value['host'],username=value['username'],interface=','.join(value['interfaces']),context=context):fail(409,'تأیید گروه منقضی یا نامعتبر است؛ دوباره همان اعضا را بررسی کنید.')
        result=run({'operation':'group-apply',**value},ticket)
        if __package__:from . import equipment_group as group
        else:import equipment_group as group
        code=result.get('error') if isinstance(result,dict) else None
        try:
            if not isinstance(result,dict) or set(result)!={'ok','mode','interfaces','rows','protectionRestored','removed'} or result['ok'] is not True or result['protectionRestored'] is not True or result['mode']!=value['mode'] or result['interfaces']!=value['interfaces']:raise ValueError('result')
            if not isinstance(result['rows'],list) or len(result['rows'])!=len(value['interfaces']):raise ValueError('rows')
            if __package__:from . import equipment_group as group
            else:import equipment_group as group
            for port,row in zip(value['interfaces'],result['rows']):
                if not isinstance(row,dict) or set(row)!={'interface','ip','oldMac','expectedMac','newMac','state'} or row['interface']!=port:raise ValueError('row')
                for key in ('oldMac','expectedMac','newMac'):
                    if not isinstance(row[key],str) or (row[key] and group.r.unicast(row[key])!=row[key]):raise ValueError('MAC')
                if value['mode']=='recover':
                    if row['state'] not in ('recovered','still_errdisabled') or row['ip']!='' or row['newMac']!='':raise ValueError('state')
                else:
                    if row['state']!='replaced' or not row['newMac'] or row['newMac']==row['oldMac'] or (row['expectedMac'] and row['expectedMac']!=row['newMac']):raise ValueError('new MAC')
                    if value['staticIp']:
                        if not row['oldMac'] or str(ipaddress.IPv4Address(row['ip']))!=row['ip']:raise ValueError('IP')
                    elif row['ip']!='':raise ValueError('IP')
            # Validate actual cleanup identities too, including narrowly approved
            # fresh discoveries during replacement (same switch/idle access policy).
            check_items=[{k:row[k] for k in ('interface','ip','oldMac','expectedMac')} for row in result['rows']]
            if value['mode']=='replace':
                for item,row in zip(check_items,result['rows']):item['expectedMac']=row['newMac']
            group.validate_plan({'mode':value['mode'],'interfaces':value['interfaces'],'staticIp':value['staticIp'],'items':check_items,'removals':result['removed'],'planHash':value['planHash'],'relocationPolicy':'idle-access-vlan100'})
            if value['mode']=='replace' and len({row['newMac'] for row in result['rows']})!=len(result['rows']):raise ValueError('duplicate new MAC')
            # Every result field is strictly typed/allowlisted above; never
            # return a raw helper field or search JSON keys for a short secret.
        except (ValueError,TypeError,KeyError):
            safe={'equipment_busy','ticket_consumed','group_changed','group_preflight','group_old_port_active','unsupported_platform','group_quarantined','mac_not_violation'}
            code=code if code in safe else 'group_uncertain'
            old_ports=result.get('affectedOldPorts',[]) if isinstance(result,dict) else []
            try:
                if not isinstance(old_ports,list) or len(old_ports)>24:raise ValueError('ports')
                if old_ports:old_ports=group.interfaces(old_ports)
                if any(port in value['interfaces'] for port in old_ports):raise ValueError('target')
            except (ValueError,TypeError,NameError):old_ports=[]
            message=_failure({'error':code})+(' پورت قبلی احتمالاً تغییرکرده: '+', '.join(old_ports) if old_ports else '')
            return jsonify(error=message,code=code,requiresRecheck=True,affectedOldPorts=old_ports), (429 if code=='equipment_busy' else 409 if code=='ticket_consumed' else 502)
        return jsonify(host=value['host'],**{k:v for k,v in result.items() if k!='ok'})
