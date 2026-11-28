"""Local Python Mock for ccnp_ensld (Enterprise Design: Oversubscription, Failure Domain & IPv6 Nibble Plan).

Educational local model only — no live enterprise campus/DC switch or IPAM system is contacted.
Models:
1. Access-to-Distribution / Leaf-to-Spine Oversubscription ratio calculation.
2. IPv6 Nibble-boundary hierarchical site subnet planner (`/48` per site -> `/52` functional block -> `/64` VLAN).
"""
from __future__ import annotations

import ipaddress


def _require_pos_int(val: object, name: str, max_val: int = 10**9) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (1 <= val <= max_val):
        raise ValueError(f"{name} must be an int in 1..{max_val}, got {val!r}")
    return val


def compute_oversubscription_ratio(
    downlink_ports: int,
    downlink_gbps: int,
    uplink_ports: int,
    uplink_gbps: int,
) -> dict[str, object]:
    """Compute oversubscription ratio (downlink aggregate / uplink aggregate)."""
    dp = _require_pos_int(downlink_ports, "downlink_ports", 10_000)
    dg = _require_pos_int(downlink_gbps, "downlink_gbps", 800)
    up = _require_pos_int(uplink_ports, "uplink_ports", 10_000)
    ug = _require_pos_int(uplink_gbps, "uplink_gbps", 800)
    down_total = dp * dg
    up_total = up * ug
    ratio = round(down_total / up_total, 2)
    return {
        "downlink_total_gbps": down_total,
        "uplink_total_gbps": up_total,
        "oversubscription_ratio": f"{ratio}:1",
        "ratio_numeric": ratio,
        "non_blocking": ratio <= 1.0,
        "design_note": "Illustrative capacity math only; acceptable oversubscription (e.g., 20:1 campus access vs 3:1 DC leaf-spine) depends on workload burst profile.",
    }


def allocate_ipv6_site_prefix(
    org_prefix: str,
    site_index: int,
    vlan_id: int,
) -> dict[str, str]:
    """Allocate a nibble-aligned IPv6 /48 site block and /64 VLAN prefix from an org /32 (or /36.. /44)."""
    base = ipaddress.IPv6Network(org_prefix, strict=True)
    if base.prefixlen > 44:
        raise ValueError("org_prefix must be /44 or shorter to carve /48 site blocks")
    s_idx = _require_pos_int(site_index, "site_index", 255)
    vid = _require_pos_int(vlan_id, "vlan_id", 4094)
    # Build deterministic /48 site prefix and /64 subnet using hex VLAN ID (nibble-aligned!)
    site_addr = int(base.network_address) + (s_idx << 80)
    site_net = ipaddress.IPv6Network((site_addr, 48))
    if not site_net.subnet_of(base):
        raise ValueError("site_index exceeds org_prefix capacity")
    vlan_net = ipaddress.IPv6Network((int(site_net.network_address) + (vid << 64), 64))
    return {
        "org_prefix": str(base),
        "site_slash48": str(site_net),
        "vlan_slash64": str(vlan_net),
    }


def main() -> None:
    print("Local Python Mock only — no live switch or IPAM database is contacted.")
    campus = compute_oversubscription_ratio(48, 1, 2, 10)  # 48G / 20G = 2.4:1
    dc_leaf = compute_oversubscription_ratio(48, 25, 4, 100)  # 1200G / 400G = 3.0:1
    assert campus["ratio_numeric"] == 2.4 and dc_leaf["ratio_numeric"] == 3.0
    v6 = allocate_ipv6_site_prefix("2001:db8::/32", site_index=1, vlan_id=10)
    assert v6["site_slash48"] == "2001:db8:1::/48" and v6["vlan_slash64"] == "2001:db8:1:a::/64"
    print("Campus & DC oversubscription:", {"campus": campus["oversubscription_ratio"], "dc": dc_leaf["oversubscription_ratio"]})
    print("IPv6 nibble plan:", v6)


if __name__ == "__main__":
    main()
