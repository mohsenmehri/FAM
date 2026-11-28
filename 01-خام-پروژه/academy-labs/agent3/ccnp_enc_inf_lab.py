"""Local Python Mock for ccnp_enc_inf (OSPF Network-Type Adjacency Audit & Wireless L2/L3 Roaming Model).

Educational local model only — no live Cisco IOS-XE OSPF router, Catalyst 9800 WLC,
or CAPWAP AP is contacted.
Models:
1. OSPF network-type mismatch detector (e.g., point-to-point vs broadcast: Hello/Dead timers
   match on 10s/40s, adjacency reaches FULL, yet LSA Type-1 vs Type-2 mismatch breaks SPF/RIB!).
2. Wireless L2 (Intra-Controller / Same-VLAN) vs L3 (Anchor / Foreign Tunnel) Roaming state model.
"""
from __future__ import annotations

OSPF_NET_TYPES = {
    "point-to-point": {"hello": 10, "dead": 40, "elects_dr": False},
    "broadcast": {"hello": 10, "dead": 40, "elects_dr": True},
    "non-broadcast": {"hello": 30, "dead": 120, "elects_dr": True},
    "point-to-multipoint": {"hello": 30, "dead": 120, "elects_dr": False},
}


def audit_ospf_network_type_pair(r1_type: str, r2_type: str) -> dict[str, object]:
    """Audit two ends of an OSPF link for timer compatibility AND DR/LSA SPF consistency."""
    if r1_type not in OSPF_NET_TYPES or r2_type not in OSPF_NET_TYPES:
        raise ValueError(f"network types must be in {sorted(OSPF_NET_TYPES)}")
    t1, t2 = OSPF_NET_TYPES[r1_type], OSPF_NET_TYPES[r2_type]
    timers_match = (t1["hello"] == t2["hello"]) and (t1["dead"] == t2["dead"])
    dr_match = t1["elects_dr"] == t2["elects_dr"]
    if not timers_match:
        return {
            "neighbor_forms_full": False,
            "spf_routes_healthy": False,
            "reason": "HELLO_DEAD_TIMER_MISMATCH_NO_ADJACENCY",
        }
    if not dr_match:
        return {
            "neighbor_forms_full": True,
            "spf_routes_healthy": False,
            "reason": "SILENT_TRAP_FULL_ADJACENCY_BUT_DR_NON_DR_LSA_MISMATCH_NO_SPF_ROUTES",
        }
    return {
        "neighbor_forms_full": True,
        "spf_routes_healthy": True,
        "dr_election_overhead_avoided": (r1_type == "point-to-point"),
        "reason": "OSPF_NETWORK_TYPES_COMPATIBLE",
    }


def classify_wireless_roam(
    old_vlan: int,
    new_vlan: int,
    same_wlc: bool,
    same_mobility_group: bool,
) -> dict[str, object]:
    """Classify client roaming as L2 vs L3 (Foreign/Anchor tunnel) in a WLC architecture."""
    if isinstance(old_vlan, bool) or isinstance(new_vlan, bool) or not isinstance(old_vlan, int) or not isinstance(new_vlan, int):
        raise ValueError("VLAN IDs must be ints")
    if not (1 <= old_vlan <= 4094) or not (1 <= new_vlan <= 4094):
        raise ValueError("VLAN IDs must be in 1..4094")
    if not isinstance(same_wlc, bool) or not isinstance(same_mobility_group, bool):
        raise ValueError("same_wlc and same_mobility_group must be strict bools")
    if not same_wlc and not same_mobility_group:
        return {"roam_type": "FULL_REAUTH_NEW_SESSION", "client_ip_preserved": False, "anchor_tunnel_used": False}
    if old_vlan == new_vlan:
        return {
            "roam_type": "L2_INTRA_CONTROLLER" if same_wlc else "L2_INTER_CONTROLLER",
            "client_ip_preserved": True,
            "anchor_tunnel_used": False,
        }
    return {
        "roam_type": "L3_ROAM_ANCHOR_FOREIGN_TUNNEL",
        "client_ip_preserved": True,
        "anchor_tunnel_used": True,
    }


def main() -> None:
    print("Local Python Mock only — no live IOS-XE OSPF router or Catalyst 9800 WLC is contacted.")
    trap = audit_ospf_network_type_pair("point-to-point", "broadcast")
    clean = audit_ospf_network_type_pair("point-to-point", "point-to-point")
    assert trap["neighbor_forms_full"] is True and trap["spf_routes_healthy"] is False
    assert clean["spf_routes_healthy"] is True and clean["dr_election_overhead_avoided"] is True

    l2 = classify_wireless_roam(10, 10, same_wlc=True, same_mobility_group=True)
    l3 = classify_wireless_roam(10, 20, same_wlc=False, same_mobility_group=True)
    assert l2["anchor_tunnel_used"] is False and l3["anchor_tunnel_used"] is True
    print("OSPF P2P-vs-Broadcast silent trap:", trap)
    print("Wireless L3 roam:", l3)


if __name__ == "__main__":
    main()
