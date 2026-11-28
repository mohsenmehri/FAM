"""Local Python 3 stdlib mock lab for adv_03 (VRF-Lite Isolation, IP SLA + Track & NetFlow vs SNMP).

Boundary: Pure in-memory simulation using Python stdlib only (ipaddress).
No real Cisco router, VRF table, ICMP/UDP probe, or NetFlow collector is executed.
"""
from __future__ import annotations

import ipaddress


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_non_empty_str(val: object, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return val.strip()


def apply_vrf_forwarding(
    interface_name: str,
    existing_ip: str | None,
    target_vrf: str,
    vrf_tables: dict[str, list[str]],
    reconfigure_ip: str | None = None,
) -> dict[str, object]:
    """Simulate Cisco IOS behavior: applying 'vrf forwarding' removes existing IP until re-entered."""
    _require_non_empty_str(interface_name, "interface_name")
    vrf = _require_non_empty_str(target_vrf, "target_vrf")
    if existing_ip is not None:
        ipaddress.IPv4Interface(existing_ip)
    if reconfigure_ip is not None:
        ipaddress.IPv4Interface(reconfigure_ip)

    ip_removed = existing_ip is not None
    final_ip = reconfigure_ip
    overlap_allowed = False
    if final_ip is not None:
        new_net = str(ipaddress.IPv4Interface(final_ip).network)
        overlap_allowed = any(
            new_net in nets for other_vrf, nets in vrf_tables.items() if other_vrf != vrf
        )
        vrf_tables.setdefault(vrf, []).append(new_net)

    return {
        "interface": interface_name,
        "vrf": vrf,
        "previous_ip_stripped_by_ios": ip_removed,
        "active_ip": final_ip,
        "overlapping_subnet_isolated_across_vrfs": overlap_allowed,
    }


def evaluate_ip_sla_failover(
    wan_port_up: bool,
    sla_probe_success: bool,
    track_attached: bool,
    probe_type: str = "icmp-echo",
    responder_configured: bool = False,
) -> dict[str, object]:
    """Simulate indirect WAN failure detection behind an ISP modem using IP SLA + Object Tracking."""
    _require_bool(wan_port_up, "wan_port_up")
    _require_bool(sla_probe_success, "sla_probe_success")
    _require_bool(track_attached, "track_attached")
    _require_bool(responder_configured, "responder_configured")
    if probe_type not in ("icmp-echo", "tcp-connect", "dns", "udp-jitter"):
        raise ValueError(f"Unsupported probe_type: {probe_type}")
    if probe_type == "udp-jitter" and not responder_configured:
        return {
            "active_path": "INVALID_PROBE_CONFIG",
            "blackhole_avoided": False,
            "reason": "UDP_JITTER_REQUIRES_REMOTE_IP_SLA_RESPONDER",
        }

    if not wan_port_up:
        return {"active_path": "BACKUP_WAN", "blackhole_avoided": True, "reason": "DIRECT_L1_LINK_DOWN"}
    if wan_port_up and not sla_probe_success:
        if track_attached:
            return {"active_path": "BACKUP_WAN", "blackhole_avoided": True, "reason": "IP_SLA_TRACK_DETECTED_INDIRECT_OUTAGE"}
        return {"active_path": "PRIMARY_BLACKHOLE", "blackhole_avoided": False, "reason": "ETH_UP_UP_WITHOUT_IP_SLA_BLACKHOLES_TRAFFIC"}
    return {"active_path": "PRIMARY_WAN", "blackhole_avoided": True, "reason": "PRIMARY_HEALTHY"}


def aggregate_netflow_records(packets: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate raw packet metadata into 5-tuple NetFlow records (identifying top talkers vs SNMP)."""
    if not isinstance(packets, list) or not packets:
        raise ValueError("packets must be a non-empty list")
    flows: dict[tuple[str, str, int, int, str], dict[str, object]] = {}
    for pkt in packets:
        src = str(ipaddress.IPv4Address(str(pkt["src_ip"])))
        dst = str(ipaddress.IPv4Address(str(pkt["dst_ip"])))
        sport = pkt["src_port"]
        dport = pkt["dst_port"]
        bcount = pkt["bytes"]
        if type(sport) is not int or not (1 <= sport <= 65535):
            raise ValueError("src_port must be int 1..65535")
        if type(dport) is not int or not (1 <= dport <= 65535):
            raise ValueError("dst_port must be int 1..65535")
        if type(bcount) is not int or bcount <= 0:
            raise ValueError("bytes must be positive int")
        proto = _require_non_empty_str(pkt["proto"], "proto").upper()
        key = (src, dst, sport, dport, proto)
        if key not in flows:
            flows[key] = {"src_ip": src, "dst_ip": dst, "src_port": sport, "dst_port": dport, "proto": proto, "packets": 0, "bytes": 0}
        flows[key]["packets"] = int(flows[key]["packets"]) + 1
        flows[key]["bytes"] = int(flows[key]["bytes"]) + bcount
    return sorted(flows.values(), key=lambda r: int(r["bytes"]), reverse=True)


def main() -> None:
    vrfs: dict[str, list[str]] = {"FINANCE": ["192.168.10.0/24"]}
    # Applying vrf forwarding strips IP if not re-entered
    stripped = apply_vrf_forwarding("Gi0/0.20", "192.168.10.1/24", "GUEST", vrfs, reconfigure_ip=None)
    assert stripped["previous_ip_stripped_by_ios"] is True and stripped["active_ip"] is None
    # Re-entering overlapping 192.168.10.1/24 in GUEST VRF succeeds with full L3 isolation
    re_ok = apply_vrf_forwarding("Gi0/0.20", None, "GUEST", vrfs, reconfigure_ip="192.168.10.1/24")
    assert re_ok["overlapping_subnet_isolated_across_vrfs"] is True

    # Indirect ISP failure: Ethernet stays up/up!
    bh = evaluate_ip_sla_failover(True, False, track_attached=False)
    ok_fo = evaluate_ip_sla_failover(True, False, track_attached=True)
    assert bh["blackhole_avoided"] is False and ok_fo["active_path"] == "BACKUP_WAN"

    top_flows = aggregate_netflow_records([
        {"src_ip": "10.10.10.50", "dst_ip": "198.51.100.90", "src_port": 51000, "dst_port": 443, "proto": "TCP", "bytes": 1500},
        {"src_ip": "10.10.10.50", "dst_ip": "198.51.100.90", "src_port": 51000, "dst_port": 443, "proto": "TCP", "bytes": 1500},
        {"src_ip": "10.10.10.22", "dst_ip": "198.51.100.53", "src_port": 52001, "dst_port": 53, "proto": "UDP", "bytes": 96},
    ])
    assert top_flows[0]["src_ip"] == "10.10.10.50" and top_flows[0]["bytes"] == 3000

    print("VRF IP Strip Trap:", stripped)
    print("VRF Overlap Isolation OK:", re_ok)
    print("IP SLA Failover (No Track vs Tracked):", bh, ok_fo)
    print("NetFlow Top Talker:", top_flows[0])


if __name__ == "__main__":
    main()
