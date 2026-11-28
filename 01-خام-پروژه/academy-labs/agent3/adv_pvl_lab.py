"""Local Python Mock for adv_pvl (Private VLAN L2 Forwarding Matrix & VLAN Pruning Audit).

Educational local model only — no live Cisco Catalyst switch, hardware ASIC,
VTP daemon, or L3 SVI ACL is contacted or tested.
Models:
1. Private VLAN (PVLAN) Layer 2 forwarding matrix (RFC 5517 concepts):
   - Promiscuous <-> Primary / Isolated / Community (allowed at L2)
   - Community <-> Same Community & Promiscuous (blocked from other Community / Isolated at L2)
   - Isolated <-> Promiscuous ONLY (blocked from other Isolated & Community at L2)
   - Explicitly notes that L2 PVLAN isolation does NOT replace L3 gateway ACLs/firewalls
     or proxy-ARP policy!
2. Manual trunk pruning audit checking that required VLANs (and Voice/Primary/Secondary VLANs)
   are present in both VLAN databases and trunk allowed lists.
"""
from __future__ import annotations

VALID_PVLAN_PORT_TYPES = frozenset({"promiscuous", "isolated", "community"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r}")
    return val


def _require_vlan(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (1 <= val <= 4094):
        raise ValueError(f"{name} must be an int VLAN ID in 1..4094, got {val!r}")
    return val


def _require_vlan_set(vals: object, name: str) -> set[int]:
    if not isinstance(vals, (list, set, tuple)):
        raise ValueError(f"{name} must be a sequence or set of VLAN IDs")
    return {_require_vlan(v, f"{name}[]") for v in vals}


def evaluate_pvlan_l2_forwarding(
    src_port_type: str,
    src_secondary_vlan: int | None,
    dst_port_type: str,
    dst_secondary_vlan: int | None,
    primary_vlan: int,
    l3_proxy_arp_enabled: bool = False,
) -> dict[str, object]:
    """Evaluate Layer 2 PVLAN frame forwarding rules within a single Primary VLAN."""
    p_vlan = _require_vlan(primary_vlan, "primary_vlan")
    proxy_arp = _require_bool(l3_proxy_arp_enabled, "l3_proxy_arp_enabled")
    if not isinstance(src_port_type, str) or src_port_type not in VALID_PVLAN_PORT_TYPES:
        raise ValueError(f"src_port_type must be in {sorted(VALID_PVLAN_PORT_TYPES)}")
    if not isinstance(dst_port_type, str) or dst_port_type not in VALID_PVLAN_PORT_TYPES:
        raise ValueError(f"dst_port_type must be in {sorted(VALID_PVLAN_PORT_TYPES)}")

    s_sec = None if src_port_type == "promiscuous" else _require_vlan(src_secondary_vlan, "src_secondary_vlan")
    d_sec = None if dst_port_type == "promiscuous" else _require_vlan(dst_secondary_vlan, "dst_secondary_vlan")
    if s_sec == p_vlan or d_sec == p_vlan:
        raise ValueError("Secondary VLAN ID must differ from Primary VLAN ID")

    if src_port_type == "promiscuous" or dst_port_type == "promiscuous":
        l2_allowed = True
        reason = "PROMISCUOUS_ENDPOINT_PERMITTED_L2"
    elif src_port_type == "isolated" or dst_port_type == "isolated":
        l2_allowed = False
        reason = "ISOLATED_PORT_L2_BLOCKED_TO_NON_PROMISCUOUS"
    elif src_port_type == "community" and dst_port_type == "community":
        if s_sec == d_sec:
            l2_allowed = True
            reason = "SAME_COMMUNITY_VLAN_PERMITTED_L2"
        else:
            l2_allowed = False
            reason = "DIFFERENT_COMMUNITY_VLANS_BLOCKED_L2"
    else:
        l2_allowed = False
        reason = "BLOCKED_BY_DEFAULT"

    warnings: list[str] = []
    if not l2_allowed and proxy_arp:
        warnings.append(
            "L3_GATEWAY_BYPASS_RISK: Proxy ARP or unguarded L3 SVI routing on the gateway "
            "can still route traffic between isolated/different-community hosts unless blocked by ACL/firewall."
        )

    return {
        "primary_vlan": p_vlan,
        "l2_model_allowed": l2_allowed,
        "reason": reason,
        "warnings": warnings,
        "model_scope_note": "RFC 5517 L2 PVLAN logic model only; platform VTP/ASIC/ACL support must be verified separately.",
    }


def audit_trunk_pruning(
    trunk_allowed_vlans: list[int],
    active_edge_vlans: list[int],
    voice_vlan: int | None = None,
) -> dict[str, object]:
    """Audit manual trunk pruning: find missing required VLANs and unnecessary unpruned VLANs."""
    allowed = _require_vlan_set(trunk_allowed_vlans, "trunk_allowed_vlans")
    needed = _require_vlan_set(active_edge_vlans, "active_edge_vlans")
    if voice_vlan is not None:
        needed.add(_require_vlan(voice_vlan, "voice_vlan"))
    missing = sorted(needed - allowed)
    excess = sorted(allowed - needed)
    return {
        "model_checks_ok": len(missing) == 0,
        "missing_required_vlans": missing,
        "excess_prunable_vlans": excess,
        "recommended_allowed_vlans": sorted(needed),
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco Catalyst switch or VTP daemon is contacted.")
    iso_to_iso = evaluate_pvlan_l2_forwarding("isolated", 101, "isolated", 101, primary_vlan=100, l3_proxy_arp_enabled=True)
    iso_to_prom = evaluate_pvlan_l2_forwarding("isolated", 101, "promiscuous", None, primary_vlan=100)
    comm_same = evaluate_pvlan_l2_forwarding("community", 102, "community", 102, primary_vlan=100)
    comm_diff = evaluate_pvlan_l2_forwarding("community", 102, "community", 103, primary_vlan=100)
    assert iso_to_iso["l2_model_allowed"] is False and len(iso_to_iso["warnings"]) == 1
    assert iso_to_prom["l2_model_allowed"] is True
    assert comm_same["l2_model_allowed"] is True
    assert comm_diff["l2_model_allowed"] is False
    prune = audit_trunk_pruning([10, 20, 30, 40, 999], [10, 20, 999], voice_vlan=50)
    assert prune["model_checks_ok"] is False and prune["missing_required_vlans"] == [50]
    print("PVLAN Isolated<->Isolated (with proxy-ARP warning):", iso_to_iso)
    print("PVLAN Community<->Same Community:", comm_same)
    print("Manual trunk pruning audit:", prune)


if __name__ == "__main__":
    main()
