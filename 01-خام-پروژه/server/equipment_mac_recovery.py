"""Explicit, port-scoped recovery for a sticky-MAC port-security violation.

The operator sees the old sticky MAC and the last violating source MAC, then
confirms that the latter is the authorized endpoint. The only write removes
that one stale sticky entry and bounces that exact interface; Port Security,
its maximum, violation mode and unrelated interface configuration remain on.
No save, arbitrary CLI, or retry is performed.
"""
from __future__ import annotations

import hashlib
import json
import re
import time

try:
    from . import equipment_probe as p
except ImportError:
    import equipment_probe as p

HASH = re.compile(r"[a-f0-9]{64}\Z")
MAC = re.compile(r"(?:[0-9a-fA-F]{4}\.){2}[0-9a-fA-F]{4}\Z")
IFACE = re.compile(r"(?:Fa(?:stEthernet)?0/(?:[1-9]|1[0-9]|2[0-4])|Gi(?:gabitEthernet)?0/(?:0|[1-9]|[1-4][0-9]|50))\Z", re.I)


def interface(value: str) -> str:
    if not isinstance(value, str) or not IFACE.fullmatch(value):
        raise ValueError("interface")
    prefix, number = value.split("0/", 1)
    return ("Fa" if prefix.lower().startswith("fa") else "Gi") + "0/" + str(int(number))


def mac(value: str) -> str:
    if not isinstance(value, str) or not MAC.fullmatch(value):
        raise ValueError("mac")
    compact = value.replace(".", "").lower()
    if compact == "000000000000" or compact == "ffffffffffff" or int(compact[:2], 16) & 1:
        raise ValueError("unicast")
    return ".".join(compact[i:i + 4] for i in (0, 4, 8))


def commands(port: str):
    port = interface(port)
    return (
        "terminal length 0",
        "show running-config interface " + port,
        "show port-security interface " + port,
        "show port-security address",
        "show interfaces status",
        "exit",
    )


def _blocks(output: str, expected):
    if (not isinstance(output, str) or len(output) > 524288 or "--More--" in output or
            re.search(r"[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]", output.replace("\r\n", "\n"))):
        raise ValueError("output")
    lines = output.replace("\r\n", "\n").splitlines()
    marks = []
    for index, line in enumerate(lines):
        match = re.fullmatch(r"[^\s#>]{1,96}[#>]\s*(.+)", line.strip())
        if match and match[1] in (*expected, "exit"):
            marks.append((index, match[1]))
        elif match and match[1] not in {"", "terminal length 0"}:
            raise ValueError("unexpected command")
    if [name for _, name in marks] != [*expected, "exit"]:
        raise ValueError("boundaries")
    sections = []
    for index in range(len(expected)):
        text = "\n".join(lines[marks[index][0] + 1:marks[index + 1][0]])
        if p.cli_errors(text):
            raise ValueError("cli")
        sections.append(text)
    return sections


def _canonical_interface(value: str) -> str:
    match = re.fullmatch(r"(Fa(?:stEthernet)?|Gi(?:gabitEthernet)?)0/(\d+)", value, re.I)
    if not match:
        raise ValueError("interface row")
    return ("Fa" if match[1].lower().startswith("fa") else "Gi") + "0/" + str(int(match[2]))


def _interface_config(text: str, port: str, *, allow_shutdown=False):
    port = interface(port)
    lines = [line.strip() for line in text.splitlines() if line.strip() and line.strip() != "!"]
    start = []
    for index, line in enumerate(lines):
        match = re.fullmatch(r"interface\s+([^\s]+)", line, re.I)
        if match:
            try:
                if _canonical_interface(match[1]) == port:
                    start.append(index)
            except ValueError:
                continue
    if len(start) != 1 or lines.count("end") != 1 or lines.index("end") <= start[0]:
        raise ValueError("config boundary")
    cfg = lines[start[0] + 1:lines.index("end")]
    if any(line.lower().startswith("interface ") for line in cfg):
        raise ValueError("nested config")
    lowered = [line.lower() for line in cfg]
    if (lowered.count("switchport mode access") != 1 or
            lowered.count("switchport access vlan 100") != 1 or
            lowered.count("switchport port-security") != 1):
        raise ValueError("not protected access vlan")
    if not allow_shutdown and any(line == "shutdown" for line in lowered):
        raise ValueError("administrative state")
    if any(line == "no shutdown" for line in lowered):
        raise ValueError("unexpected no shutdown")
    if any(line.startswith(("switchport trunk", "switchport voice", "channel-group", "authentication ", "dot1x ", "switchport protected", "ip verify source")) for line in lowered):
        raise ValueError("shared or source-guard port")
    if any(line.startswith("switchport port-security violation ") and line != "switchport port-security violation shutdown" for line in lowered):
        raise ValueError("violation mode")
    if any(line.startswith("switchport port-security maximum ") and line != "switchport port-security maximum 1" for line in lowered):
        raise ValueError("multiple clients")
    mac_lines = [line for line in lowered if line.startswith("switchport port-security mac-address ")]
    if mac_lines.count("switchport port-security mac-address sticky") != 1:
        raise ValueError("sticky learning disabled")
    entries = []
    for line in mac_lines:
        if line == "switchport port-security mac-address sticky":
            continue
        match = re.fullmatch(r"switchport port-security mac-address sticky (" + MAC.pattern[:-2] + r")", line, re.I)
        if not match:
            raise ValueError("unsupported secure address config")
        entries.append(mac(match[1]))
    if len(entries) > 1:
        raise ValueError("multiple sticky addresses")
    return {"lines": tuple(lowered), "sticky": entries[0] if entries else ""}


def _port_security(text: str):
    fields = {}
    wanted = {
        "port security": "enabled",
        "port status": "status",
        "violation mode": "mode",
        "maximum mac addresses": "maximum",
        "total mac addresses": "total",
        "configured mac addresses": "configured",
        "sticky mac addresses": "sticky_count",
        "last source address:vlan": "last_source",
        "security violation count": "violations",
    }
    for line in text.splitlines():
        source = re.fullmatch(r"\s*Last Source Address\s*:\s*Vlan\s*:\s*(.*?)\s*", line, re.I)
        if source:
            if "last_source" in fields:
                raise ValueError("duplicate security field")
            fields["last_source"] = source[1].strip()
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized = re.sub(r"\s+", " ", key.strip()).lower()
        if normalized in wanted:
            name = wanted[normalized]
            if name in fields:
                raise ValueError("duplicate security field")
            fields[name] = value.strip()
    required = set(wanted.values())
    if set(fields) != required:
        raise ValueError("incomplete port-security output")
    if fields["enabled"].lower() != "enabled" or fields["mode"].lower() != "shutdown":
        raise ValueError("port-security disabled")
    for key in ("maximum", "total", "configured", "sticky_count", "violations"):
        if not re.fullmatch(r"\d+", fields[key]):
            raise ValueError("bad port-security count")
        fields[key] = int(fields[key])
    match = re.fullmatch(r"(" + MAC.pattern[:-2] + r")\s*:\s*(\d{1,4})", fields["last_source"], re.I)
    if not match:
        raise ValueError("last source unavailable")
    raw_mac, raw_vlan = match[1], int(match[2])
    if raw_mac.replace(".", "").lower() == "000000000000" and raw_vlan == 0:
        fields["last_mac"], fields["last_vlan"] = "", 0
    else:
        fields["last_mac"] = mac(raw_mac)
        fields["last_vlan"] = raw_vlan
    fields["status"] = re.sub(r"\s+", "-", fields["status"].strip().lower())
    return fields


def _secure_table(text: str):
    rows = []
    header = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or re.fullmatch(r"[-= ]+", line):
            continue
        normalized = " ".join(line.split()).lower()
        if normalized in {
            "secure mac address table",
            "vlan mac address type ports remaining age",
            "vlan mac address type ports remaining age (mins)",
            "(mins)",
        }:
            if normalized.startswith("vlan "):
                header = True
            continue
        if re.fullmatch(r"(?:Total Addresses in System(?: \(excluding one mac per port\))?|Max Addresses limit in System(?: \(excluding one mac per port\))?)\s*:\s*\d+", line, re.I):
            continue
        if not header:
            raise ValueError("missing secure table header")
        match = re.fullmatch(r"(\d{1,4})\s+(" + MAC.pattern[:-2] + r")\s+(SecureSticky|SecureDynamic|SecureConfigured)\s+(Fa(?:stEthernet)?0/(?:[1-9]|1[0-9]|2[0-4])|Gi(?:gabitEthernet)?0/(?:0|[1-9]|[1-4][0-9]|50))\s+(?:-|\d+)", line, re.I)
        if not match:
            raise ValueError("malformed secure row")
        vlan = int(match[1])
        if not 1 <= vlan <= 4094:
            raise ValueError("invalid vlan")
        rows.append({"vlan": vlan, "mac": mac(match[2]), "kind": match[3].lower(), "interface": _canonical_interface(match[4])})
        if len(rows) > 4096:
            raise ValueError("too many rows")
    if not header:
        raise ValueError("missing secure table")
    return rows


def _status(text: str, port: str):
    table = p.validate_status_output(text)
    matches = []
    for row in p._table_rows(table):
        try:
            normalized = _canonical_interface(row[0])
        except ValueError:
            continue
        if normalized == port:
            matches.append(row)
    if len(matches) != 1:
        raise ValueError("port state unavailable")
    return matches[0][2].lower()


def snapshot(output: str, port: str, *, allow_shutdown=False):
    port = interface(port)
    _, cfg_text, security_text, secure_text, status_text = _blocks(output, commands(port)[:-1])
    cfg = _interface_config(cfg_text, port, allow_shutdown=allow_shutdown)
    security = _port_security(security_text)
    secure = _secure_table(secure_text)
    state = _status(status_text, port)
    local = [row for row in secure if row["interface"] == port]
    return {"interface": port, "config": cfg, "security": security, "secure": secure, "local": local, "state": state}


def preflight(s):
    """Plan a bounded sticky-learning reset for an err-disabled access port.

    MAC identities are deliberately not used for authorization in this mode.
    Port Security and its one-address/shutdown policy must already be enabled;
    the existing sticky entries on the failed port are cleared and sticky
    learning is re-enabled so the attached endpoint can be learned again.
    """
    port = s["interface"]
    security = s["security"]
    if s["state"] not in {"err-disabled", "errdisable", "errdisabled", "disabled"}:
        raise ValueError("not port-security err-disabled")
    if security["status"] not in {"secure-shutdown", "secure-down", "err-disabled", "errdisable", "errdisabled"}:
        raise ValueError("not port-security down")
    if (security["maximum"] != 1 or security["total"] not in {0, 1} or
            security["configured"] != 0 or security["sticky_count"] not in {0, 1} or
            security["violations"] < 1 or security["last_vlan"] not in {0, 100}):
        raise ValueError("not a single-client sticky violation")
    if "switchport port-security mac-address sticky" not in s["config"]["lines"]:
        raise ValueError("sticky learning disabled")
    if len(s["local"]) > 1 or any(
        row["vlan"] != 100 or row["kind"] != "securesticky" or
        (s["config"]["sticky"] and row["mac"] != s["config"]["sticky"])
        for row in s["local"]
    ):
        raise ValueError("local secure table is ambiguous")
    if s["config"]["sticky"] and s["local"] and s["local"][0]["mac"] != s["config"]["sticky"]:
        raise ValueError("config and secure table disagree")
    return {
        "interface": port,
        "maximum": security["maximum"],
        "reason": "psecure-violation",
        "total": security["total"],
        "violations": security["violations"],
        "macPolicy": "clear-and-relearn",
    }


def _digest(s, plan):
    stable = {
        "interface": plan["interface"], "maximum": plan["maximum"],
        "reason": plan["reason"], "total": plan["total"],
        "violations": plan["violations"], "macPolicy": plan["macPolicy"],
        "state": s["state"], "securityStatus": s["security"]["status"],
        "lastMac": s["security"]["last_mac"], "vlan": s["security"]["last_vlan"],
        "config": s["config"]["lines"],
    }
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_plan(value):
    expected = {"interface", "maximum", "planHash", "reason", "total", "violations", "macPolicy"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("plan schema")
    port = interface(value["interface"])
    if (port != value["interface"] or value["reason"] != "psecure-violation" or
            value["macPolicy"] != "clear-and-relearn" or
            not isinstance(value["planHash"], str) or not HASH.fullmatch(value["planHash"]) or
            type(value["maximum"]) is not int or value["maximum"] != 1 or
            type(value["total"]) is not int or value["total"] not in {0, 1} or
            type(value["violations"]) is not int or value["violations"] < 1):
        raise ValueError("plan values")
    return value


def recovery_commands(plan):
    """Reset only the selected port, retain security, relearn sticky, and save."""
    return (
        "terminal length 0", "configure terminal", "interface " + plan["interface"],
        "shutdown", "no switchport port-security mac-address sticky",
        "switchport port-security", "switchport port-security mac-address sticky",
        "no shutdown", "end", "write memory", "exit",
    )


def conflict_clear_commands(port, address):
    port, address = interface(port), mac(address)
    return (
        "terminal length 0", "configure terminal", "interface " + port,
        "no switchport port-security mac-address sticky " + address,
        "end", "write memory", "exit",
    )


def _write(job, cmds, deadline):
    output = p.session_output(job, cmds, deadline, 25)
    echoed = []
    for line in output.replace("\r\n", "\n").splitlines():
        match = re.fullmatch(r"[^\s#>]{1,96}[#>]\s*(.*)", line.strip())
        if match and match[1] in cmds:
            echoed.append(match[1])
    if p.cli_errors(output) or echoed != list(cmds):
        raise ValueError("write not verified")


def _read(job, port, deadline, *, allow_shutdown=False, session_cap=25):
    return snapshot(p.session_output(job, commands(port), deadline, session_cap), port, allow_shutdown=allow_shutdown)


def _monitor(job, port, plan, deadline, seconds=15):
    """Poll the selected port during the full window and return immediately on re-error."""
    stop = time.monotonic() + seconds
    current = None
    while True:
        current = _read(job, port, deadline, session_cap=5)
        _verify_protection(current, plan)
        if _is_errdisabled(current["state"]):
            return current
        remaining = stop - time.monotonic()
        if remaining <= 0:
            return current
        time.sleep(min(1.0, remaining))


def _verify_protection(s, plan):
    security = s["security"]
    if "switchport port-security" not in s["config"]["lines"] or "switchport port-security mac-address sticky" not in s["config"]["lines"]:
        raise ValueError("port-security or sticky learning changed")
    if (security["enabled"].lower() != "enabled" or security["mode"].lower() != "shutdown" or
            security["maximum"] != 1 or security["configured"] != 0 or
            security["total"] not in {0, 1} or security["sticky_count"] not in {0, 1}):
        raise ValueError("port-security changed")
    if len(s["local"]) > 1 or any(row["vlan"] != 100 or row["kind"] != "securesticky" for row in s["local"]):
        raise ValueError("local secure state is ambiguous")


def _is_errdisabled(state):
    return state in {"err-disabled", "errdisable", "errdisabled"}


def _conflicting_sticky(snapshot, port):
    address = snapshot["security"]["last_mac"]
    if not address or snapshot["security"]["last_vlan"] != 100:
        return None
    matches = [row for row in snapshot["secure"] if row["vlan"] == 100 and row["mac"] == address and row["kind"] == "securesticky" and row["interface"] != port]
    if len(matches) != 1:
        return None
    return matches[0]


def run(job, apply=False):
    port = interface(job["interface"])
    workdir = p.runtime_directory()
    askpass = None
    deadline = p.Deadline(145)
    try:
        askpass = p.prepare_askpass(workdir)
        job = {**job, "_askpass": (askpass, workdir)}
        before = _read(job, port, deadline, allow_shutdown=True)
        try:
            raw_plan = preflight(before)
        except ValueError as exc:
            raise p.ProbeError("mac_not_violation" if str(exc) == "not port-security err-disabled" else "mac_preflight") from None
        digest = _digest(before, raw_plan)
        plan = validate_plan({**raw_plan, "planHash": digest})
        if not apply:
            return {"ok": True, "plan": plan}
        if job.get("planHash") != digest:
            raise p.ProbeError("mac_changed")

        try:
            after = None
            # One initial reset plus at most two conflict-aware retries. Each
            # reset gets a full 15-second poll window; a detected Err-disabled
            # state advances immediately instead of waiting out the window.
            for attempt in range(3):
                if attempt:
                    conflict = _conflicting_sticky(after, port)
                    if conflict:
                        _write(job, conflict_clear_commands(conflict["interface"], conflict["mac"]), deadline)
                        cleared = _read(job, port, deadline, allow_shutdown=True)
                        _verify_protection(cleared, plan)
                        if any(row["vlan"] == 100 and row["mac"] == conflict["mac"] and
                               row["interface"] == conflict["interface"] and row["kind"] == "securesticky"
                               for row in cleared["secure"]):
                            return {"ok": True, "interface": port, "state": "still_errdisabled", "protectionPreserved": True}
                    _write(job, recovery_commands(plan), deadline)
                else:
                    _write(job, recovery_commands(plan), deadline)
                after = _monitor(job, port, plan, deadline, 15)
                if not _is_errdisabled(after["state"]):
                    return {"ok": True, "interface": port, "state": "not_errdisabled", "protectionPreserved": True}
            return {"ok": True, "interface": port, "state": "still_errdisabled", "protectionPreserved": True}
        except p.ProbeError:
            raise
        except Exception:
            raise p.ProbeError("mac_uncertain") from None
    finally:
        p._cleanup_runtime(workdir, askpass)
