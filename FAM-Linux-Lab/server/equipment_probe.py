"""One-shot Cisco IOS equipment probe used only by the FAM backend.

The process reads one JSON document from stdin and writes one sanitized JSON
result to stdout.  It runs directly on the FAM server and connects to the
device with the Windows OpenSSH client (``ssh.exe``) -- not Netmiko/Paramiko.

Security contract
-----------------
* The device password is never placed on a command line, in a URL, in the
  database, in a file, or in a log.  It lives only in the environment of the
  short-lived ``ssh.exe`` child; ``SSH_ASKPASS`` points at a tiny helper
  script that merely echoes that environment variable.  The script itself
  never contains the password and is deleted in ``finally``.
* Only the single legacy cipher ``aes128-cbc`` is appended to the OpenSSH
  default cipher list (``-o Ciphers=+aes128-cbc``).  ``3des-cbc``,
  ``aes192-cbc`` and ``aes256-cbc`` are never offered.
* Host keys are verified with a dedicated ``known_hosts`` file.  The default
  policy is ``strict`` (requires an independently pre-trusted key);
  explicit ``accept-new`` is TOFU, not equivalent to strict.  Host-key checking is never
  disabled.
* Only fixed reads / bounded recovery / separately confirmed port-MAC replacement exist. There is
  no terminal, free-form command, ``enable``, ``write memory`` or ``copy``.
* Banners, prompts, arbitrary CLI and ssh diagnostics never leave this process.
  The explicitly requested interface-description table alone may be displayed,
  with credential-bearing description fields redacted and no persistent copy.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

INTERFACE = re.compile(r"[A-Za-z][A-Za-z0-9/.-]{0,63}\Z")
# Device user names are passed with -l and appear in the ASKPASS prompt.
# A strict allowlist keeps option-like and control-character input out.
USERNAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._@\\-]{0,63}\Z")
# RFC1918 plus the user-authorized building/shared-address range (RFC6598).
# Deliberately not all of 100/8 or arbitrary public targets.
ALLOWED_IPV4_NETWORKS = tuple(ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10"))
CLI_ERROR = re.compile(r"^\s*%\s+\S")  # IOS "% Invalid input ..." (syslog lines are "%LINK-5-..." without a space)

# Exactly one temporary legacy exception.  Never widen this.
LEGACY_CIPHER_OPTION = "Ciphers=+aes128-cbc"
FORBIDDEN_CIPHERS = ("3des-cbc", "aes192-cbc", "aes256-cbc")
HOST_KEY_POLICIES = {"accept-new": "accept-new", "strict": "yes"}
SECRET_ENV = "FAM_EQUIPMENT_SSH_SECRET"

# Timeout budget.  ``SESSION_TIMEOUT`` bounds one ssh.exe process (connect +
# authenticate + fixed commands).  ``HELPER_DEADLINE`` bounds this whole
# helper per operation (status = 1 session, recovery = up to 3 sessions).
# ``equipment_ops.EXECUTOR_TIMEOUT`` must stay above these values so that the
# FAM backend never kills this helper while ssh.exe is still being supervised.
CONNECT_TIMEOUT = 10
SESSION_TIMEOUT = 25
INSPECT_SESSION_TIMEOUT = 2 * SESSION_TIMEOUT
HELPER_DEADLINE = {"status": 30, "inspect": 55, "descriptions": 30, "recover": 85, "diagnose": 85, "replacement-plan": 70, "replacement-apply": 150, "group-plan": 100, "group-apply": 150}
MAX_OUTPUT_BYTES = 1024 * 1024

STATUS_COMMANDS = ("terminal length 0", "show interfaces status", "exit")
DESCRIPTION_COMMANDS = ("terminal length 0", "show interfaces description", "exit")
INSPECT_COMMANDS = ("terminal length 0", "show interfaces status", "show interfaces description", "exit")

# POSIX OpenSSH can execute a tiny /bin/sh helper directly.
# Neither its source nor its executable contains a credential. The source is
# constant; the password is read only by the child from its environment and is
# printed only for prompts containing "password" -- never a host-key question.
ASKPASS_SH_SOURCE = r'''#!/bin/sh
[ "$#" -eq 1 ] || exit 1
case "$1" in
  *[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]*)
    [ -n "$FAM_EQUIPMENT_SSH_SECRET" ] || exit 1
    printf '%s\n' "$FAM_EQUIPMENT_SSH_SECRET"
    ;;
  *) exit 1 ;;
esac
'''

# Win32 OpenSSH uses CreateProcess, which cannot directly execute a .cmd/.ps1
# file. Build a tiny .NET Framework executable in the per-session directory.
# Neither its source nor its executable contains a credential. The source is
# constant; the password is read only by the child from its environment.
ASKPASS_SOURCE = r'''using System;
using System.Text;
class FamAskpass {
    static int Main(string[] args) {
        if (args.Length != 1 ||
            args[0].IndexOf("password", StringComparison.OrdinalIgnoreCase) < 0)
            return 1; // Never answer a host-key confirmation or other challenge.
        string password = Environment.GetEnvironmentVariable("FAM_EQUIPMENT_SSH_SECRET");
        if (String.IsNullOrEmpty(password)) return 1;
        Console.OutputEncoding = new UTF8Encoding(false);
        Console.WriteLine(password);
        return 0;
    }
}
'''


def prepare_askpass(workdir):
    """Build a secret-free, executable ASKPASS helper (bounded 5 s).

    Windows: compile a tiny .NET Framework executable with csc.exe.
    POSIX (Linux): install a tiny /bin/sh helper.  Both variants contain no
    credential; the secret is read only from the child environment and is
    printed only for password prompts, never host-key questions.
    """
    if os.name != "nt":
        source = os.path.join(workdir, "askpass.sh")
        with open(source, "w", encoding="ascii") as handle:
            handle.write(ASKPASS_SH_SOURCE)
        os.chmod(source, 0o700)
        return source
    root = os.environ.get("SystemRoot", r"C:\Windows")
    compiler = next((os.path.join(root, "Microsoft.NET", framework, "v4.0.30319", "csc.exe")
                     for framework in ("Framework64", "Framework")
                     if os.path.isfile(os.path.join(root, "Microsoft.NET", framework, "v4.0.30319", "csc.exe"))), None)
    if not compiler:
        raise ProbeError("connection_failed")
    source = os.path.join(workdir, "askpass.cs")
    executable = os.path.join(workdir, "askpass.exe")
    with open(source, "w", encoding="ascii") as handle:
        handle.write(ASKPASS_SOURCE)
    result = subprocess.run(
        [compiler, "/nologo", "/noconfig", "/target:exe", "/out:" + executable, source],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={key: os.environ[key] for key in ENV_PASSTHROUGH if key in os.environ},
        timeout=5, check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode != 0 or not os.path.isfile(executable):
        raise ProbeError("connection_failed")
    return executable


# Only this subset of the parent environment is visible to ssh.exe / the askpass
# helper.  Windows and POSIX need different minimal sets; neither set ever
# includes a device credential.
ENV_PASSTHROUGH_WINDOWS = (
    "SystemRoot", "SystemDrive", "windir", "ComSpec", "PATHEXT", "Path", "PATH",
    "TEMP", "TMP", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "HOME", "USERNAME",
    "ProgramData", "APPDATA", "LOCALAPPDATA", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
)
ENV_PASSTHROUGH_POSIX = (
    "PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TZ", "TMPDIR",
)
ENV_PASSTHROUGH = ENV_PASSTHROUGH_WINDOWS if os.name == "nt" else ENV_PASSTHROUGH_POSIX


def respond(value):
    sys.stdout.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()


class ProbeError(Exception):
    """Carries only a stable, redacted error code."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


# --------------------------------------------------------------------------- #
# Parsing                                                                     #
# --------------------------------------------------------------------------- #
PROMPT_PREFIX = re.compile(r"^[^\s#>]{1,64}[#>]\s*(?=[Pp]ort\b)")
KNOWN_STATUSES = {
    "connected", "notconnect", "err-disabled", "disabled", "inactive", "monitoring", "sfpabsent",
    "faulty", "suspended", "xcvrabsen", "linkflape", "nooperem", "errdisable", "errdisabled", "channel-",
}


def _strip_prompt(line: str) -> str:
    """Without a PTY, IOS may print its prompt directly before the header."""
    return PROMPT_PREFIX.sub("", line, count=1)


def _header_columns(line: str):
    """Return (name_start, status_start, status_end) from the IOS header row."""
    lowered = line.lower()
    if not lowered.startswith("port"):
        return None
    status = lowered.find("status", 4)
    if status < 0:
        return None
    name = lowered.find("name", 4, status)
    vlan = lowered.find("vlan", status + 6)
    return (name if name >= 0 else status, status, vlan if vlan >= 0 else len(line))


def _clean_description(value: str) -> str:
    value = value.strip()
    # IOS uses -- when the Name column is empty.  Keep the bounded label only.
    if value in {"--", "-", "N/A"}:
        return ""
    return value[:128]


def _table_rows(output: str):
    """Yield (interface, name, status) for each data row of ``show interfaces status``.

    Column offsets from the header row are used so that port names containing
    spaces (or words such as "disabled") are never mistaken for a status.  A
    whitespace-split fallback handles rows that are not aligned to the header.
    """
    columns = None
    for raw in output.splitlines():
        line = _strip_prompt(raw.rstrip("\r"))
        if not line.strip():
            continue
        header = _header_columns(line)
        if header:
            columns = header
            continue
        fields = line.split()
        if not fields or not INTERFACE.fullmatch(fields[0]):
            continue
        interface = fields[0]
        if columns and len(line) > columns[1]:
            name_start, status_start, _ = columns
            aligned = line[status_start - 1].isspace() and not line[status_start].isspace()
            positional = line[status_start:].split()
            if aligned and positional and positional[0].lower() in KNOWN_STATUSES:
                yield interface, line[name_start:status_start], positional[0]
                continue
        # Non-aligned fixtures/devices: status must be followed by a VLAN and
        # the duplex/speed/type columns, never just a word in a description.
        for index in range(len(fields) - 5, 0, -1):
            if (fields[index].lower() in KNOWN_STATUSES and
                    re.fullmatch(r"[0-9]+|trunk|routed|unassigned", fields[index + 1], re.I)):
                yield interface, " ".join(fields[1:index]), fields[index]
                break


def has_status_table(output: str) -> bool:
    """True only when the device really answered ``show interfaces status``."""
    return any(_header_columns(_strip_prompt(line.rstrip("\r"))) for line in output.splitlines())


def cli_errors(output: str) -> bool:
    return any(CLI_ERROR.match(line) for line in output.splitlines())


def errdisabled_interfaces(output: str):
    """Return only an interface and its displayed status-name/description.

    Statuses such as ``disabled``, ``connected`` and ``notconnect`` are never
    reported; only explicit err-disabled status variants count.  This deliberately
    returns no raw CLI line or other device data.
    """
    ports = {}
    for interface, name, status in _table_rows(output):
        if status.lower() not in {"err-disabled", "errdisable", "errdisabled"}:
            continue
        ports.setdefault(interface, _clean_description(name))
    return [{"interface": interface, "description": ports[interface]} for interface in sorted(ports)]


def errdisabled_ports(output: str):
    """Compatibility helper for the recovery pre-/post-check."""
    return [item["interface"] for item in errdisabled_interfaces(output)]


# --------------------------------------------------------------------------- #
# ssh.exe transport                                                           #
# --------------------------------------------------------------------------- #
def ssh_executable() -> str:
    configured = os.environ.get("FAM_EQUIPMENT_SSH", "").strip()
    candidates = [configured] if configured else []
    system_root = os.environ.get("SystemRoot") or os.environ.get("windir")
    if system_root:
        candidates.append(os.path.join(system_root, "System32", "OpenSSH", "ssh.exe"))
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    if os.name == "nt":
        # Never pick up an arbitrary ssh from PATH (e.g. an MSYS build) on the
        # server: only the configured or in-box Windows OpenSSH client is used.
        raise ProbeError("connection_failed")
    found = shutil.which("ssh")
    if not found:
        raise ProbeError("connection_failed")
    return found


def known_hosts_file() -> str:
    configured = os.environ.get("FAM_EQUIPMENT_KNOWN_HOSTS", "").strip()
    path = configured or os.path.join(os.path.dirname(os.path.abspath(__file__)), "private", "equipment_known_hosts")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    return path


def runtime_directory() -> str:
    """Space-free private directory for the per-session askpass helper."""
    configured = os.environ.get("FAM_EQUIPMENT_RUNTIME_DIR", "").strip()
    path = configured or os.path.join(os.path.dirname(known_hosts_file()), "tmp")
    try:
        os.makedirs(path, exist_ok=True)
        return tempfile.mkdtemp(prefix="session-", dir=path)
    except OSError:
        return tempfile.mkdtemp(prefix="fam-equipment-")


def host_key_policy() -> str:
    value = os.environ.get("FAM_EQUIPMENT_HOST_KEY_POLICY", "strict").strip().lower()
    try:
        return HOST_KEY_POLICIES[value]
    except KeyError as exc:  # An unknown policy must never silently relax checking.
        raise ProbeError("connection_failed") from exc


def ssh_arguments(executable: str, host: str, username: str, known_hosts: str, policy: str):
    """Fixed, auditable argv.  The password is never part of it."""
    options = (
        LEGACY_CIPHER_OPTION,
        "StrictHostKeyChecking=" + policy,
        "UserKnownHostsFile=" + ('"%s"' % known_hosts if os.name == "nt" and any(char.isspace() for char in known_hosts) else known_hosts),
        "UpdateHostKeys=no",
        "CheckHostIP=no",
        "HashKnownHosts=no",
        "ConnectTimeout=%d" % CONNECT_TIMEOUT,
        "ConnectionAttempts=1",
        "ServerAliveInterval=5",
        "ServerAliveCountMax=3",
        "NumberOfPasswordPrompts=1",
        "PreferredAuthentications=keyboard-interactive,password",
        "PubkeyAuthentication=no",
        "KbdInteractiveAuthentication=yes",
        "PasswordAuthentication=yes",
        "GSSAPIAuthentication=no",
        "BatchMode=no",
        "ClearAllForwardings=yes",
        "ForwardAgent=no",
        "ForwardX11=no",
        "PermitLocalCommand=no",
        "ControlMaster=no",
        "ControlPath=none",
        "RequestTTY=no",
        "EscapeChar=none",
        "LogLevel=ERROR",
    )
    argv = [executable, "-F", "NUL" if os.name == "nt" else "/dev/null", "-T", "-p", "22"]
    for option in options:
        argv += ["-o", option]
    argv += ["-l", username, host]
    return argv


def _child_environment(askpass_path: str, password: str):
    env = {}
    for key in ENV_PASSTHROUGH:
        value = os.environ.get(key)
        # Windows environment names are case-insensitive; never emit duplicates.
        if value is not None and key.upper() not in {name.upper() for name in env}:
            env[key] = value
    system_root = env.get("SystemRoot") or env.get("windir")
    if system_root and "ComSpec" not in env:
        env["ComSpec"] = os.path.join(system_root, "System32", "cmd.exe")
    # DISPLAY makes OpenSSH <= 8.3 use the askpass program when no console is
    # attached; SSH_ASKPASS_REQUIRE=force does the same on OpenSSH >= 8.4.
    env.update({
        "DISPLAY": "fam-equipment:0",
        "SSH_ASKPASS": askpass_path,
        "SSH_ASKPASS_REQUIRE": "force",
        SECRET_ENV: password,
    })
    # Deterministic English prompts regardless of the server locale, so the
    # askpass password check and the output parsing never depend on LANG.
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    return env


def _creation_flags() -> int:
    # No console is attached, so ssh.exe cannot fall back to an interactive
    # password prompt; it must use SSH_ASKPASS or fail.
    return getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def _cleanup_runtime(workdir,askpass=None):
    try:
        if askpass:os.remove(askpass)
    except OSError:pass
    shutil.rmtree(workdir,ignore_errors=True)


def run_ssh(job, commands, timeout: float):
    """Run one bounded ssh.exe session; return (returncode, stdout, stderr, timed_out)."""
    for name in FORBIDDEN_CIPHERS:
        if name in LEGACY_CIPHER_OPTION:
            raise ProbeError("connection_failed")
    executable = ssh_executable()
    argv = ssh_arguments(executable, job["host"], job["username"], known_hosts_file(), host_key_policy())
    script = ("\n".join(commands) + "\n").encode("ascii")
    shared = job.get('_askpass')
    workdir = shared[1] if shared else runtime_directory()
    askpass = shared[0] if shared else None
    started = time.monotonic()
    process = None
    try:
        if askpass is None:askpass = prepare_askpass(workdir)
        prepared = time.monotonic()
        process = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_child_environment(askpass, job["password"]),
            cwd=workdir,
            creationflags=_creation_flags(),
            start_new_session=(os.name != "nt"),
        )
        try:
            out, err = process.communicate(script, timeout=max(1.0, timeout - (time.monotonic() - started)))
            timed_out = False
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
            timed_out = True
        if '_timings' in job:
            job['_timings'].update(preparationMs=round((prepared-started)*1000),sshMs=round((time.monotonic()-prepared)*1000))
        if len(out)>MAX_OUTPUT_BYTES:raise ProbeError('connection_failed')
        return process.returncode, out[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"), err[:65536].decode("utf-8", "replace"), timed_out
    finally:
        if process is not None and process.poll() is None:
            process.kill()
        # Shared only within one bounded recovery request, never across users.
        # Its owner removes the secret-free executable in its own finally.
        if not shared:_cleanup_runtime(workdir,askpass)


def classify_failure(stderr: str, timed_out: bool) -> str:
    text = stderr.lower()
    if timed_out:
        return "connection_timeout"
    if "ssh_askpass" in text:
        # The askpass helper could not be started: a server-side setup problem.
        return "connection_failed"
    if "permission denied" in text or "authentication failed" in text or "too many authentication failures" in text:
        return "authentication_failed"
    if "host key verification failed" in text or "remote host identification has changed" in text or ("host key for" in text and "has changed" in text):
        return "connection_failed"
    if "timed out" in text or "timeout" in text:
        return "connection_timeout"
    return "connection_failed"


class Deadline:
    def __init__(self, seconds: float):
        self.until = time.monotonic() + seconds

    def session_timeout(self, cap=SESSION_TIMEOUT) -> float:
        remaining = self.until - time.monotonic()
        if remaining <= 1:
            raise ProbeError("connection_timeout")
        return min(cap, remaining)


def session_output(job, commands, deadline: Deadline, session_cap=SESSION_TIMEOUT) -> str:
    code, out, err, timed_out = run_ssh(job, commands, deadline.session_timeout(session_cap))
    if timed_out or code != 0:
        raise ProbeError(classify_failure(err, timed_out))
    return out


def validate_status_output(output: str) -> str:
    rows = list(_table_rows(output))
    # Never call a partially parsed table clean. A single unknown/truncated
    # interface row can be the failing port even if other rows parsed normally.
    parsed=[row[0] for row in rows]
    candidates=[];in_table=False;unparsed_error=False
    for raw in output.splitlines():
        line=_strip_prompt(raw.rstrip("\r"));fields=line.split()
        if _header_columns(line):in_table=True;continue
        if in_table and fields and INTERFACE.fullmatch(fields[0]) and any(c.isdigit() for c in fields[0]):candidates.append(fields[0])
        if in_table and fields and fields[0] not in parsed and re.search(r"\b(?:err-disabled|errdisable|errdisabled)\b",line,re.I):unparsed_error=True
    if (not has_status_table(output) or cli_errors(output) or not rows or "--More--" in output
            or unparsed_error or set(candidates)!=set(parsed) or len(candidates)!=len(parsed) or len(parsed)!=len(set(parsed))):
        raise ProbeError("status_unreadable")
    return output


def status_table(job, deadline: Deadline) -> str:
    return validate_status_output(session_output(job,STATUS_COMMANDS,deadline))


# --------------------------------------------------------------------------- #
# Operations                                                                  #
# --------------------------------------------------------------------------- #
def status(job):
    deadline = Deadline(HELPER_DEADLINE["status"])
    # Fixed commands only.  Raw output is parsed then discarded.
    return safe_status_ports(status_table(job, deadline),job)


SENSITIVE_LABEL = re.compile(r'\b(?:password|secret|community|key(?:-string)?|token|authorization|api[_-]?key|access[_-]?token)\b\s*(?:[:=]\s*|\s+)\S+|BEGIN[^\n]*PRIVATE KEY|(?:radius|tacacs)[^\n]*\bkey\s+\S+',re.I)

def sensitive_label(text,username,password):
    folded=text.casefold()
    return (any(secret and (secret.casefold() in folded or
                (len(folded)>=8 and secret.casefold().startswith(folded)))
                for secret in (username,password)) or bool(SENSITIVE_LABEL.search(text)) or
            bool(re.search(r'[\x00-\x1f\x7f\u202a-\u202e\u2066-\u2069]',text)))

def safe_status_ports(output,job):
    ports={}
    for interface,name,status in _table_rows(output):
        if status.lower() not in {'err-disabled','errdisable','errdisabled'}:continue
        # Inspect the ORIGINAL field before bounding it. Otherwise a long secret
        # can become a visible prefix which no longer matches its full value.
        label=name.strip()
        ports.setdefault(interface,'' if sensitive_label(label,job['username'],job['password']) else _clean_description(label))
    return {'ok':True,'ports':[{'interface':i,'description':ports[i]} for i in sorted(ports)]}


DESCRIPTION_HEADER = re.compile(r"^\s*Interface\s+Status\s+Protocol\s+Description\s*$",re.I)
DESCRIPTION_ROW = re.compile(r"^(\s*([A-Za-z][A-Za-z0-9/.-]{0,63})\s+(?:(?:admin(?:istratively)?\s+)?(?:up|down)|deleted|reset|unknown)\s+(?:up|down|unknown)(?:\s+|$))(.*)$",re.I)
DESCRIPTION_PROMPT = re.compile(r"^[^\s#>]{1,64}[#>]\s*(?=Interface\b)",re.I)

def descriptions_table(output,username,password):
    """Only the fixed read-only command's table, never banner/prompt/CLI.
    Preserve table spacing/newlines. Sensitive description payloads are redacted.
    Called both in the child and the API before crossing the browser boundary.
    """
    if not isinstance(output,str) or len(output)>100000 or cli_errors(output) or '--More--' in output or re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u202a-\u202e\u2066-\u2069]',output):raise ProbeError('descriptions_unreadable')
    lines=[];seen=set();started=False;redacted=False
    for raw in output.splitlines():
        line=DESCRIPTION_PROMPT.sub('',raw,count=1)
        if DESCRIPTION_HEADER.fullmatch(line):
            if started:raise ProbeError('descriptions_unreadable')
            started=True;lines.append(line);continue
        if not started:continue
        if re.fullmatch(r'(?:[^\s#>]{1,64}[#>]\s*(?:exit)?|exit)\s*',line,re.I):break
        if not line.strip():lines.append(line);continue
        match=DESCRIPTION_ROW.fullmatch(line)
        if not match or not any(c.isdigit() for c in match[2]) or match[2].lower() in seen or len(seen)>=2048:raise ProbeError('descriptions_unreadable')
        seen.add(match[2].lower());description=match[3]
        sensitive=sensitive_label(description,username,password)
        if sensitive:line=match[1]+'[REDACTED]';redacted=True
        lines.append(line)
    if not started or not seen:raise ProbeError('descriptions_unreadable')
    while lines and not lines[-1].strip():lines.pop()
    return '\n'.join(lines)+'\n',redacted

def descriptions(job):
    output=session_output(job,DESCRIPTION_COMMANDS,Deadline(HELPER_DEADLINE['descriptions']))
    table,redacted=descriptions_table(output,job['username'],job['password'])
    return {'ok':True,'output':table,'redacted':redacted}


def inspect_device(job):
    """Both fixed reads in ONE SSH authentication/ASKPASS lifecycle.
    Split at the actual description header; never auto-reconnect on failure.
    If no boundary is available, fail closed rather than guess a clean table.
    """
    job['_timings']={}
    output=session_output(job,INSPECT_COMMANDS,Deadline(HELPER_DEADLINE['inspect']),INSPECT_SESSION_TIMEOUT)
    lines=output.splitlines();boundary=next((i for i,line in enumerate(lines) if DESCRIPTION_HEADER.fullmatch(DESCRIPTION_PROMPT.sub('',line,count=1))),None)
    if boundary is None:raise ProbeError('descriptions_unreadable')
    status_output='\n'.join(lines[:boundary])+'\n'
    result=safe_status_ports(validate_status_output(status_output),job)
    try:
        table,redacted=descriptions_table('\n'.join(lines[boundary:])+'\n',job['username'],job['password'])
        result['descriptions']={'ok':True,'output':table,'redacted':redacted}
    except ProbeError:result['descriptions']={'ok':False,'error':'descriptions_unreadable'}
    result['timings']=job['_timings']
    return result


def recovery_commands(interface: str):
    # This is the only allowed configuration sequence.  Do not enable, save,
    # or execute any caller-provided command.
    assert INTERFACE.fullmatch(interface)
    return ("terminal length 0", "configure terminal", "interface " + interface, "shutdown", "no shutdown", "end", "exit")


def recover(job):
    deadline=Deadline(HELPER_DEADLINE['recover'])
    workdir=runtime_directory();askpass=None
    try:
        askpass=prepare_askpass(workdir)
        return _recover({**job,'_askpass':(askpass,workdir)},deadline)
    finally:_cleanup_runtime(workdir,askpass)


def _recover(job,deadline):
    interface = job["interface"]
    before=status_table(job, deadline)
    if interface not in {row[0] for row in _table_rows(before)}:raise ProbeError("status_unreadable")
    if interface not in errdisabled_ports(before):
        return {"ok": True, "recovery": "not_errdisabled"}
    try:
        config_output = session_output(job, recovery_commands(interface), deadline)
        if cli_errors(config_output):
            # e.g. insufficient privilege: do not claim recovery succeeded. Never save.
            raise ProbeError("connection_failed")
        after_table=status_table(job, deadline)
        if interface not in {row[0] for row in _table_rows(after_table)}:raise ProbeError("status_unreadable")
        after = errdisabled_ports(after_table)
        return {"ok": True, "recovery": "still_errdisabled" if interface in after else "recovered"}
    except Exception:
        # After config may have started, neither delivery nor rollback is
        # knowable. Never retry/enable an administratively disabled port here.
        raise ProbeError('recovery_uncertain') from None



def diagnose(job):
    # Two deliberate read phases, one request-owned ASKPASS; never retry auth.
    try:
        from . import equipment_diagnostics as diagnostic
    except ImportError:
        import equipment_diagnostics as diagnostic
    deadline=Deadline(HELPER_DEADLINE['diagnose']);workdir=runtime_directory();askpass=None
    try:
        askpass=prepare_askpass(workdir);shared={**job,'_askpass':(askpass,workdir)}
        version=session_output(shared,('terminal length 0','show version','exit'),deadline)
        try:hardware=diagnostic.profile(version)
        except ValueError:raise ProbeError('unsupported_platform') from None
        output=session_output(shared,('terminal length 0',*diagnostic.READS,'exit'),deadline,50)
        try:
            report=diagnostic.assess(hardware,diagnostic.client(job['clientIp'],job['clientMac']),output)
            diagnostic.validate_report(report)
            encoded=json.dumps(report).casefold()
            if any(secret.casefold() in encoded for secret in (job['username'],job['password'])):raise ValueError('sensitive result')
            return {'ok':True,'report':report}
        except (ValueError,TypeError):raise ProbeError('diagnosis_unreadable') from None
    finally:_cleanup_runtime(workdir,askpass)


def execute(value):
    """Run one already-decoded, bounded job and return only its safe result."""
    if isinstance(value,dict) and value.get('operation') in ('group-plan','group-apply'):
        try:
            if __package__:from . import equipment_group as group
            else:import equipment_group as group
            base={'operation','host','username','password','interfaces','mode','staticIp'}
            if set(value)!=(base|({'planHash'} if value['operation']=='group-apply' else set())):raise ValueError('schema')
            group.interfaces(value['interfaces'])
            if not isinstance(value['mode'],str) or value['mode'] not in ('recover','replace') or type(value['staticIp']) is not bool or (value['mode']=='recover' and value['staticIp']):raise ValueError('mode')
            if value['operation']=='group-apply' and (not isinstance(value['planHash'],str) or not group.r.HASH.fullmatch(value['planHash'])):raise ValueError('hash')
            if not isinstance(value['host'],str):raise ValueError('host')
            address=ipaddress.IPv4Address(value['host'])
            if not any(address in n for n in ALLOWED_IPV4_NETWORKS) or not isinstance(value['username'],str) or not USERNAME.fullmatch(value['username']):raise ValueError('host/user')
            password=value['password']
            if not isinstance(password,str) or not 1<=len(password)<=512 or not all(0x20<=ord(c)<=0x7e for c in password):raise ValueError('password')
        except (ValueError,TypeError,KeyError):return {'ok':False,'error':'invalid_request'}
        try:return group.run(value,apply=value['operation']=='group-apply')
        except ProbeError as exc:return {'ok':False,'error':exc.code}
        except Exception:return {'ok':False,'error':'group_preflight'}
    if isinstance(value,dict) and value.get('operation') in ('replacement-plan','replacement-apply'):
        try:
            if __package__:from . import equipment_replacement as replacement
            else:import equipment_replacement as replacement
            base={'operation','host','username','password','interface','staticIp'}
            if set(value)!=(base|({'planHash'} if value['operation']=='replacement-apply' else set())):raise ValueError('schema')
            replacement.interface(value['interface'])
            if type(value['staticIp']) is not bool:raise ValueError('static')
            if value['operation']=='replacement-apply' and (not isinstance(value['planHash'],str) or not replacement.HASH.fullmatch(value['planHash'])):raise ValueError('hash')
            if not isinstance(value['host'],str):raise ValueError('host')
            address=ipaddress.IPv4Address(value['host'])
            if not any(address in n for n in ALLOWED_IPV4_NETWORKS) or not isinstance(value['username'],str) or not USERNAME.fullmatch(value['username']):raise ValueError('host/user')
            password=value['password']
            if not isinstance(password,str) or not 1<=len(password)<=512 or not all(0x20<=ord(c)<=0x7e for c in password):raise ValueError('password')
        except (ValueError,TypeError,KeyError):return {'ok':False,'error':'invalid_request'}
        try:return replacement.run(value,apply=value['operation']=='replacement-apply')
        except ProbeError as exc:return {'ok':False,'error':exc.code}
        except Exception:return {'ok':False,'error':'replacement_preflight'}
    if not isinstance(value, dict) or set(value) not in ({"operation", "host", "username", "password"}, {"operation", "host", "username", "password", "interface"}, {"operation", "host", "username", "password", "clientIp", "clientMac"}):
        return {"ok": False, "error": "invalid_request"}
    if not isinstance(value.get("operation"), str) or value["operation"] not in {"status", "inspect", "descriptions", "recover", "diagnose"} or not all(isinstance(value.get(key), str) for key in ("host", "username", "password")):
        return {"ok": False, "error": "invalid_request"}
    try:
        address = ipaddress.ip_address(value["host"])
    except ValueError:
        return {"ok": False, "error": "invalid_request"}
    if not isinstance(address, ipaddress.IPv4Address) or not any(address in network for network in ALLOWED_IPV4_NETWORKS):
        return {"ok": False, "error": "invalid_request"}
    if not USERNAME.fullmatch(value["username"]):
        return {"ok": False, "error": "invalid_request"}
    password = value["password"]
    if not 1 <= len(password) <= 512 or not all(0x20 <= ord(char) <= 0x7E for char in password):
        return {"ok": False, "error": "invalid_request"}
    if value["operation"] == "recover" and (not isinstance(value.get("interface"), str) or not INTERFACE.fullmatch(value["interface"])):
        return {"ok": False, "error": "invalid_request"}
    if value["operation"] != "recover" and "interface" in value:
        return {"ok": False, "error": "invalid_request"}
    if value['operation']=='diagnose':
        try:
            if __package__:from .equipment_diagnostics import client
            else:from equipment_diagnostics import client
            target=client(value.get('clientIp'),value.get('clientMac'))
        except (ValueError,TypeError):return {'ok':False,'error':'invalid_request'}
    elif 'clientIp' in value or 'clientMac' in value:return {'ok':False,'error':'invalid_request'}
    job = {"host": str(address), "username": value["username"], "password": password}
    if value["operation"] == "recover":
        job["interface"] = value["interface"]
    if value['operation']=='diagnose':job.update(clientIp=target['ip'],clientMac=target['mac'])
    try:
        return {"diagnose":diagnose,"status":status,"inspect":inspect_device,"descriptions":descriptions,"recover":recover}[value["operation"]](job)
    except ProbeError as exc:
        return {"ok": False, "error": exc.code}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "connection_timeout"}
    except Exception:  # Map every library/OS detail to one stable code.
        return {"ok": False, "error": "connection_failed"}


_PROCESS_JOB = None

def protect_process_tree():
    """Fail closed on Windows if a kill-on-close Job cannot supervise us.

    The sole non-inheritable Job handle lives until PROCESS EXIT, not a Python
    finally (which would kill us before responding). Kernel close-on-exit also
    covers an externally killed helper, compiler and detached ssh descendants.
    """
    global _PROCESS_JOB
    if os.name != 'nt' or _PROCESS_JOB is not None:return
    import ctypes
    from ctypes import wintypes as w
    class Basic(ctypes.Structure):
        _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),
                  ('flags',ctypes.c_uint32),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),
                  ('active',ctypes.c_uint32),('affinity',ctypes.c_size_t),
                  ('priority',ctypes.c_uint32),('scheduling',ctypes.c_uint32)]
    class IO(ctypes.Structure):
        _fields_=[('v'+str(i),ctypes.c_uint64) for i in range(6)]
    class Extended(ctypes.Structure):
        _fields_=[('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),
                  ('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR];kernel.CreateJobObjectW.restype=w.HANDLE
    kernel.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD];kernel.SetInformationJobObject.restype=w.BOOL
    kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE];kernel.AssignProcessToJobObject.restype=w.BOOL
    kernel.GetCurrentProcess.argtypes=[];kernel.GetCurrentProcess.restype=w.HANDLE
    kernel.CloseHandle.argtypes=[w.HANDLE];kernel.CloseHandle.restype=w.BOOL
    handle=kernel.CreateJobObjectW(None,None)
    if not handle:raise ProbeError('connection_failed')
    limits=Extended();limits.basic.flags=0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel.SetInformationJobObject(handle,9,ctypes.byref(limits),ctypes.sizeof(limits)) or not kernel.AssignProcessToJobObject(handle,kernel.GetCurrentProcess()):
        kernel.CloseHandle(handle)
        raise ProbeError('connection_failed')
    _PROCESS_JOB=handle

def main():
    try:
        value = json.loads(sys.stdin.buffer.read(4096).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        respond({"ok": False, "error": "invalid_request"})
        return
    try:protect_process_tree()
    except Exception:
        respond({'ok':False,'error':'connection_failed'});return
    respond(execute(value))


if __name__ == "__main__":
    main()
