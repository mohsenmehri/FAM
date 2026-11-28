"""Local Python 3 stdlib mock lab for ccna_05 (ACL First-Match, Port Security, DHCP Snooping & DAI).

Boundary: Pure in-memory simulation using Python stdlib only (ipaddress).
No real Cisco switch/router, live traffic, or packet capture is executed.
"""
from __future__ import annotations

import ipaddress


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _wildcard_matches(ip_str: str, rule_ip: str, wildcard: str) -> bool:
    ip_int = int(ipaddress.IPv4Address(ip_str))
    rule_int = int(ipaddress.IPv4Address(rule_ip))
    wc_int = int(ipaddress.IPv4Address(wildcard))
    return (ip_int & ~wc_int) == (rule_int & ~wc_int)


def evaluate_extended_acl(
    rules: list[dict[str, object]],
    packet: dict[str, object],
) -> dict[str, object]:
    """Evaluate Cisco Extended ACL top-down (First-Match + Implicit Deny Any)."""
    src_ip = str(packet["src_ip"])
    dst_ip = str(packet["dst_ip"])
    proto = str(packet["proto"]).lower()
    dst_port = packet.get("dst_port")
    ipaddress.IPv4Address(src_ip)
    ipaddress.IPv4Address(dst_ip)
    if dst_port is not None and (type(dst_port) is not int or not (1 <= dst_port <= 65535)):
        raise ValueError("packet dst_port must be an integer in 1..65535 or None")

    for idx, rule in enumerate(rules, start=1):
        action = str(rule["action"]).lower()
        if action not in ("permit", "deny"):
            raise ValueError(f"Rule {idx} action must be 'permit' or 'deny'")
        r_proto = str(rule["proto"]).lower()
        if r_proto not in ("ip", "tcp", "udp", "icmp"):
            raise ValueError(f"Rule {idx} unsupported protocol: {r_proto}")
        if r_proto != "ip" and r_proto != proto:
            continue
        if not _wildcard_matches(src_ip, str(rule["src_ip"]), str(rule["src_wc"])):
            continue
        if not _wildcard_matches(dst_ip, str(rule["dst_ip"]), str(rule["dst_wc"])):
            continue
        if rule.get("dst_port") is not None and rule.get("dst_port") != dst_port:
            continue
        return {"decision": action, "matched_rule_index": idx, "implicit_deny": False}

    return {"decision": "deny", "matched_rule_index": None, "implicit_deny": True}


def evaluate_port_security(
    port_mode: str,
    max_macs: int,
    learned_macs: set[str],
    incoming_mac: str,
    violation_mode: str = "shutdown",
) -> dict[str, object]:
    """Simulate Cisco Switch Port Security violation modes (shutdown/restrict/protect)."""
    if port_mode not in ("static_access", "trunk", "dynamic_auto", "dynamic_desirable"):
        raise ValueError(f"Invalid port_mode: {port_mode}")
    if port_mode.startswith("dynamic_"):
        raise ValueError("Port Security cannot be enabled on dynamic DTP ports; set static access or trunk")
    if type(max_macs) is not int or max_macs < 1:
        raise ValueError("max_macs must be an integer >= 1")
    if violation_mode not in ("shutdown", "restrict", "protect"):
        raise ValueError("violation_mode must be 'shutdown', 'restrict', or 'protect'")

    if incoming_mac in learned_macs or len(learned_macs) < max_macs:
        return {
            "allowed": True,
            "port_state": "up",
            "syslog_sent": False,
            "counter_incremented": False,
        }

    if violation_mode == "shutdown":
        return {
            "allowed": False,
            "port_state": "err-disabled",
            "syslog_sent": True,
            "counter_incremented": True,
        }
    if violation_mode == "restrict":
        return {
            "allowed": False,
            "port_state": "up",
            "syslog_sent": True,
            "counter_incremented": True,
        }
    # protect: silent drop only
    return {
        "allowed": False,
        "port_state": "up",
        "syslog_sent": False,
        "counter_incremented": False,
    }


def evaluate_dai_packet(
    port_trusted: bool,
    sender_ip: str,
    sender_mac: str,
    snooping_binding_db: dict[str, str],
    static_arp_acl: dict[str, str],
) -> dict[str, object]:
    """Simulate Dynamic ARP Inspection (DAI) relying on DHCP Snooping Binding DB or ARP ACL."""
    _require_bool(port_trusted, "port_trusted")
    ipaddress.IPv4Address(sender_ip)
    if not isinstance(sender_mac, str) or not sender_mac.strip():
        raise ValueError("sender_mac must be a non-empty string")

    if port_trusted:
        return {"action": "forward", "reason": "TRUSTED_UPLINK_PORT_BYPASSES_DAI_CHECK"}
    if static_arp_acl.get(sender_ip) == sender_mac:
        return {"action": "forward", "reason": "MATCHED_STATIC_ARP_ACL"}
    if snooping_binding_db.get(sender_ip) == sender_mac:
        return {"action": "forward", "reason": "MATCHED_DHCP_SNOOPING_BINDING_DB"}
    return {"action": "drop", "reason": "ARP_SPOOF_OR_MISSING_BINDING_ON_UNTRUSTED_PORT"}


def main() -> None:
    acl = [
        {"action": "deny", "proto": "tcp", "src_ip": "10.10.20.0", "src_wc": "0.0.0.255",
         "dst_ip": "10.10.50.10", "dst_wc": "0.0.0.0", "dst_port": 22},
        {"action": "permit", "proto": "ip", "src_ip": "0.0.0.0", "src_wc": "255.255.255.255",
         "dst_ip": "0.0.0.0", "dst_wc": "255.255.255.255", "dst_port": None},
    ]
    r_deny = evaluate_extended_acl(acl, {"src_ip": "10.10.20.5", "dst_ip": "10.10.50.10", "proto": "tcp", "dst_port": 22})
    r_allow = evaluate_extended_acl(acl, {"src_ip": "10.10.20.5", "dst_ip": "10.10.50.10", "proto": "tcp", "dst_port": 443})
    r_implicit = evaluate_extended_acl(acl[:1], {"src_ip": "10.10.20.5", "dst_ip": "10.10.50.10", "proto": "tcp", "dst_port": 443})
    assert r_deny["decision"] == "deny" and r_deny["implicit_deny"] is False
    assert r_allow["decision"] == "permit"
    assert r_implicit["decision"] == "deny" and r_implicit["implicit_deny"] is True

    ps_restrict = evaluate_port_security("static_access", 1, {"aa:aa:aa:00:00:01"}, "bb:bb:bb:00:00:02", "restrict")
    ps_protect = evaluate_port_security("static_access", 1, {"aa:aa:aa:00:00:01"}, "bb:bb:bb:00:00:02", "protect")
    assert ps_restrict["port_state"] == "up" and ps_restrict["syslog_sent"] is True
    assert ps_protect["port_state"] == "up" and ps_protect["syslog_sent"] is False

    dai_ok = evaluate_dai_packet(False, "10.10.10.25", "aa:aa:aa:00:00:01", {"10.10.10.25": "aa:aa:aa:00:00:01"}, {})
    dai_drop = evaluate_dai_packet(False, "10.10.10.25", "de:ad:be:ef:00:01", {"10.10.10.25": "aa:aa:aa:00:00:01"}, {})
    dai_static = evaluate_dai_packet(False, "10.10.10.5", "11:22:33:44:55:66", {}, {"10.10.10.5": "11:22:33:44:55:66"})
    assert dai_ok["action"] == "forward" and dai_drop["action"] == "drop" and dai_static["action"] == "forward"

    print("Extended ACL:", r_deny, r_allow, r_implicit)
    print("Port Security (restrict vs protect):", ps_restrict, ps_protect)
    print("DAI checks (valid / spoof / static ARP ACL):", dai_ok, dai_drop, dai_static)


if __name__ == "__main__":
    main()
