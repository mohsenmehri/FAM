"""Local Python Mock for ccnp_enc_arch (CEF FIB/Adjacency Lookup, TCAM Utilization & SD-Access Roles).

Educational local model only — no live Cisco Catalyst 9000 ASIC, CEF engine, TCAM bank,
or Cisco SD-Access fabric is contacted.
Models:
1. Illustrative CEF Data-Plane table separation (FIB prefix -> Adjacency L2 rewrite header).
2. Illustrative TCAM entry utilization budget warning (ACL/QoS/L3 routes).
3. SD-Access fabric node role mapping (Control Plane Node, Edge Node, Border Node).
"""
from __future__ import annotations

import ipaddress


def _require_non_neg_int(val: object, name: str, max_val: int = 10_000_000) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (0 <= val <= max_val):
        raise ValueError(f"{name} must be an int in 0..{max_val}, got {val!r}")
    return val


def cef_fib_adjacency_lookup(
    destination_ip: str,
    fib_table: list[dict[str, str]],
    adjacency_table: dict[str, dict[str, str]],
) -> dict[str, object]:
    """Model two-table CEF lookup: Longest Prefix Match in FIB -> L2 rewrite in Adjacency Table."""
    dst = ipaddress.IPv4Address(destination_ip.strip())
    best_len = -1
    best_entry: dict[str, str] | None = None
    for row in fib_table:
        net = ipaddress.IPv4Network(str(row["prefix"]), strict=True)
        if dst in net and net.prefixlen > best_len:
            best_len = net.prefixlen
            best_entry = row
    if best_entry is None:
        return {"cef_hit": False, "reason": "NO_FIB_MATCH_PUNT_OR_DROP"}
    nh = str(best_entry["next_hop"])
    adj = adjacency_table.get(nh)
    if not adj:
        return {"cef_hit": False, "fib_prefix": best_entry["prefix"], "reason": "GLEAN_ADJACENCY_ARP_REQUIRED"}
    return {
        "cef_hit": True,
        "fib_prefix": best_entry["prefix"],
        "next_hop": nh,
        "l2_rewrite_dst_mac": adj["dst_mac"],
        "egress_interface": adj["egress_interface"],
        "model_scope_note": "Illustrative CEF FIB/Adjacency data-structure model only; no hardware ASIC tested.",
    }


def evaluate_tcam_utilization(used_entries: int, max_entries: int) -> dict[str, object]:
    """Evaluate illustrative TCAM occupancy percentage and exhaustion risk."""
    used = _require_non_neg_int(used_entries, "used_entries")
    cap = _require_non_neg_int(max_entries, "max_entries")
    if cap == 0:
        raise ValueError("max_entries must be > 0")
    pct = round((used / cap) * 100.0, 2)
    status = "EXHAUSTED_CPU_PUNT_OR_DROP_RISK" if used >= cap else ("WARNING_HIGH_OCCUPANCY" if pct >= 80.0 else "NORMAL")
    return {"used_entries": used, "max_entries": cap, "utilization_pct": pct, "status": status}


def main() -> None:
    print("Local Python Mock only — no live Catalyst ASIC, TCAM, or SD-Access fabric is contacted.")
    fib = [
        {"prefix": "0.0.0.0/0", "next_hop": "10.0.0.1"},
        {"prefix": "10.40.0.0/16", "next_hop": "10.0.0.2"},
    ]
    adj = {"10.0.0.2": {"dst_mac": "00:50:56:aa:bb:02", "egress_interface": "TenGigabitEthernet1/0/1"}}
    hit = cef_fib_adjacency_lookup("10.40.12.5", fib, adj)
    glean = cef_fib_adjacency_lookup("198.51.100.10", fib, adj)
    assert hit["cef_hit"] is True and glean["reason"] == "GLEAN_ADJACENCY_ARP_REQUIRED"
    tcam = evaluate_tcam_utilization(3600, 4096)
    assert tcam["status"] == "WARNING_HIGH_OCCUPANCY"
    print("CEF hit:", hit)
    print("TCAM occupancy:", tcam)


if __name__ == "__main__":
    main()
