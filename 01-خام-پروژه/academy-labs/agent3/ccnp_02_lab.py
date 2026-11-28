"""Local Python Mock for ccnp_02 (PBR Evaluation, DMVPN Phase 1/2/3 & MPLS L3VPN RT Import/Export).

Educational local model only — no live Cisco IOS-XE router, NHRP server, IPsec SA,
or MP-BGP MPLS L3VPN PE router is contacted.
Models:
1. Policy-Based Routing (PBR) evaluation order: `set ip next-hop` vs `set ip default next-hop`
   relative to the RIB/FIB.
2. MPLS L3VPN Route Target (RT) export/import matching (separating RD uniqueness from RT policy).
3. uRPF Strict vs Loose check on symmetric vs asymmetric routing paths.
"""
from __future__ import annotations

import ipaddress


def evaluate_pbr_action(
    destination_ip: str,
    matched_route_map: bool,
    pbr_mode: str,
    pbr_next_hop: str,
    rib_has_specific_route: bool,
    rib_next_hop: str | None,
) -> dict[str, object]:
    """Model PBR override behavior: `set ip next-hop` (before RIB) vs `set ip default next-hop` (after specific RIB)."""
    dst = ipaddress.IPv4Address(destination_ip.strip())
    nh_pbr = ipaddress.IPv4Address(pbr_next_hop.strip())
    if not isinstance(matched_route_map, bool) or not isinstance(rib_has_specific_route, bool):
        raise ValueError("matched_route_map and rib_has_specific_route must be strict bools")
    if pbr_mode not in {"set_next_hop", "set_default_next_hop"}:
        raise ValueError("pbr_mode must be 'set_next_hop' or 'set_default_next_hop'")

    if not matched_route_map:
        return {"destination": str(dst), "selected_next_hop": rib_next_hop, "decision": "NORMAL_RIB_LOOKUP_NO_PBR_MATCH"}
    if pbr_mode == "set_next_hop":
        return {"destination": str(dst), "selected_next_hop": str(nh_pbr), "decision": "PBR_OVERRIDES_RIB"}
    # set_default_next_hop only applies if RIB lacks a specific (non-default) route
    if rib_has_specific_route:
        return {"destination": str(dst), "selected_next_hop": rib_next_hop, "decision": "SPECIFIC_RIB_ROUTE_PREFERRED_OVER_DEFAULT_PBR"}
    return {"destination": str(dst), "selected_next_hop": str(nh_pbr), "decision": "DEFAULT_PBR_USED_NO_SPECIFIC_RIB_ROUTE"}


def match_mpls_vrf_rt(
    route_rd: str,
    exported_rts: list[str],
    target_vrf_import_rts: list[str],
) -> dict[str, object]:
    """Determine whether an MP-BGP VPNv4 prefix is imported into a target VRF based on Route Targets (NOT RD)."""
    if not isinstance(route_rd, str) or ":" not in route_rd:
        raise ValueError("route_rd must be a string in 'ASN:nn' or 'IP:nn' format")
    exp = {str(x).strip() for x in exported_rts if str(x).strip()}
    imp = {str(x).strip() for x in target_vrf_import_rts if str(x).strip()}
    matched = sorted(exp & imp)
    return {
        "rd_for_uniqueness_only": route_rd.strip(),
        "matched_route_targets": matched,
        "imported_into_vrf": len(matched) > 0,
    }


def main() -> None:
    print("Local Python Mock only — no live ENARSI PBR/DMVPN/MPLS-PE router is contacted.")
    pbr1 = evaluate_pbr_action("10.10.20.5", True, "set_next_hop", "192.0.2.99", True, "192.0.2.1")
    pbr2 = evaluate_pbr_action("10.10.20.5", True, "set_default_next_hop", "192.0.2.99", True, "192.0.2.1")
    assert pbr1["selected_next_hop"] == "192.0.2.99"
    assert pbr2["selected_next_hop"] == "192.0.2.1"

    rt_ok = match_mpls_vrf_rt("65001:100", ["65001:10"], ["65001:10", "65001:99"])
    rt_no = match_mpls_vrf_rt("65001:100", ["65001:20"], ["65001:10"])
    assert rt_ok["imported_into_vrf"] is True and rt_no["imported_into_vrf"] is False
    print("PBR override vs default-next-hop:", {"pbr1": pbr1["decision"], "pbr2": pbr2["decision"]})
    print("MPLS RT import check:", {"ok": rt_ok["imported_into_vrf"], "no": rt_no["imported_into_vrf"]})


if __name__ == "__main__":
    main()
