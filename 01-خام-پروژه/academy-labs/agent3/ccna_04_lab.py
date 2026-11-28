"""Local Python Mock for ccna_04 (HSRP, NTP Stratum, Syslog Severity & SNMPv3 Security).

No real Cisco router, NTP server, Syslog collector, or SNMP manager is contacted.
Models:
1. HSRP v1 vs v2 compatibility, Active/Standby election, preempt behavior & Dual-Active detection.
2. NTP Stratum validation (RFC 5905: 1..15 synchronized, 16 unsynchronized).
3. Syslog inclusive severity filter (0=Emergency .. 7=Debug).
4. SNMP security posture audit (SNMPv3 authPriv vs cleartext SNMPv2c).
"""
from __future__ import annotations

import ipaddress

SYSLOG_LEVELS = {
    0: "emergencies",
    1: "alerts",
    2: "critical",
    3: "errors",
    4: "warnings",
    5: "notifications",
    6: "informational",
    7: "debugging",
}


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_int_range(val: object, name: str, lo: int, hi: int) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (lo <= val <= hi):
        raise ValueError(f"{name} must be an int in {lo}..{hi} (not bool), got {val!r}")
    return val


def evaluate_hsrp_pair(
    r1: dict[str, object],
    r2: dict[str, object],
    hello_reachable: bool = True,
    current_active: str | None = None,
) -> dict[str, object]:
    """Model HSRP election including version mismatch, split-brain Dual-Active, and preempt."""
    reachable = _require_bool(hello_reachable, "hello_reachable")
    if current_active not in (None, "R1", "R2"):
        raise ValueError("current_active must be None, 'R1', or 'R2'")

    for lbl, r in (("R1", r1), ("R2", r2)):
        ver = _require_int_range(r["version"], f"{lbl}.version", 1, 2)
        max_grp = 255 if ver == 1 else 4095
        _require_int_range(r["group"], f"{lbl}.group", 0, max_grp)
        _require_int_range(r["priority"], f"{lbl}.priority", 0, 255)
        _require_bool(r["preempt"], f"{lbl}.preempt")
        ipaddress.IPv4Address(str(r["ip"]))

    if not reachable or r1["version"] != r2["version"] or r1["group"] != r2["group"]:
        return {
            "healthy": False,
            "state": "DUAL_ACTIVE_SPLIT_BRAIN",
            "active_routers": ["R1", "R2"],
            "multicast_group_r1": "224.0.0.2" if r1["version"] == 1 else "224.0.0.102",
            "multicast_group_r2": "224.0.0.2" if r2["version"] == 1 else "224.0.0.102",
        }

    k1 = (int(r1["priority"]), int(ipaddress.IPv4Address(str(r1["ip"]))))
    k2 = (int(r2["priority"]), int(ipaddress.IPv4Address(str(r2["ip"]))))
    if k1 == k2:
        raise ValueError("R1 and R2 cannot share identical IP addresses")
    preferred = "R1" if k1 > k2 else "R2"

    if current_active is None:
        winner = preferred
    elif current_active == preferred:
        winner = preferred
    else:
        # Returning higher-priority router takes over ONLY if preempt is enabled!
        pref_router = r1 if preferred == "R1" else r2
        winner = preferred if pref_router["preempt"] else current_active

    return {
        "healthy": True,
        "state": "ACTIVE_STANDBY",
        "active": winner,
        "standby": "R2" if winner == "R1" else "R1",
        "multicast_group": "224.0.0.2" if r1["version"] == 1 else "224.0.0.102",
    }


def evaluate_ntp_stratum(upstream_stratum: int) -> dict[str, object]:
    """Compute local NTP stratum (upstream + 1); stratum 16 is unsynchronized per RFC 5905."""
    up = _require_int_range(upstream_stratum, "upstream_stratum", 0, 16)
    local = min(16, up + 1)
    return {
        "upstream_stratum": up,
        "local_stratum": local,
        "synchronized": local <= 15,
    }


def filter_syslog_events(events: list[tuple[int, str]], trap_level: int) -> list[dict[str, object]]:
    """Filter syslog events: Cisco `logging trap <level>` sends severities 0..level inclusive."""
    lvl = _require_int_range(trap_level, "trap_level", 0, 7)
    if not isinstance(events, list):
        raise ValueError("events must be a list of (severity, message) tuples")
    out: list[dict[str, object]] = []
    for sev, msg in events:
        s = _require_int_range(sev, "event severity", 0, 7)
        if not isinstance(msg, str) or not msg.strip():
            raise ValueError("event message must be a non-empty str")
        if s <= lvl:
            out.append({"severity": s, "name": SYSLOG_LEVELS[s], "message": msg})
    return out


def audit_snmp_config(version: str, security_level: str = "") -> dict[str, object]:
    """Audit SNMP version and security level."""
    if version not in ("v1", "v2c", "v3"):
        raise ValueError("version must be 'v1', 'v2c', or 'v3'")
    if version in ("v1", "v2c"):
        return {"secure": False, "cleartext_credentials": True, "note": "Community string and payload sent in cleartext"}
    if security_level not in ("noAuthNoPriv", "authNoPriv", "authPriv"):
        raise ValueError("SNMPv3 security_level must be 'noAuthNoPriv', 'authNoPriv', or 'authPriv'")
    return {
        "secure": security_level == "authPriv",
        "authenticated": security_level in ("authNoPriv", "authPriv"),
        "encrypted": security_level == "authPriv",
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco router, NTP, Syslog, or SNMP server is contacted.")
    r1 = {"version": 2, "group": 10, "priority": 150, "preempt": False, "ip": "10.0.10.2"}
    r2 = {"version": 2, "group": 10, "priority": 100, "preempt": False, "ip": "10.0.10.3"}

    # Without preempt, R1 returning after failover stays Standby while R2 remains Active
    no_preempt = evaluate_hsrp_pair(r1, r2, hello_reachable=True, current_active="R2")
    with_preempt = evaluate_hsrp_pair({**r1, "preempt": True}, r2, hello_reachable=True, current_active="R2")
    split = evaluate_hsrp_pair({**r1, "version": 1}, r2, hello_reachable=True)
    assert no_preempt["active"] == "R2" and with_preempt["active"] == "R1"
    assert split["state"] == "DUAL_ACTIVE_SPLIT_BRAIN"
    print("HSRP no-preempt:", no_preempt["active"], "| with-preempt:", with_preempt["active"], "| v1/v2 mismatch:", split["state"])

    # NTP stratum 15 -> local 16 unsynchronized
    assert evaluate_ntp_stratum(2)["synchronized"] is True
    assert evaluate_ntp_stratum(15)["synchronized"] is False

    # Syslog trap warnings (4) includes 0..4, excludes 5..7
    ev = [(2, "PSU fail"), (4, "High CPU"), (5, "Link up"), (7, "Debug packet")]
    sent = filter_syslog_events(ev, 4)
    assert [e["severity"] for e in sent] == [2, 4]
    assert audit_snmp_config("v2c")["secure"] is False
    assert audit_snmp_config("v3", "authPriv")["secure"] is True
    print("NTP/Syslog/SNMPv3 checks passed:", len(sent), "events sent for trap 4.")


if __name__ == "__main__":
    main()
