#!/usr/bin/env python3
"""
Local Mock Lab — ccde_03 (CCDE Service Provider Architecture: Transit vs IXP Peering Economics & SR/MPLS Choice)
Models Service Provider internet economics (Tier-1 Transit vs IXP Settlement-Free Peering + CDN Cache),
verifies BGP-Free Core P-router scaling, and recommends LDP vs SR-MPLS/EVPN based on hardware & 5G SLA.
No real carrier core routers or IXP fabrics are connected.
"""

import json


def model_sp_peering_economics(total_gbps: float, transit_usd_per_mbps: float, ixp_port_usd_month: float, offload_ratio: float) -> dict:
    all_transit_cost = round(total_gbps * 1000 * transit_usd_per_mbps, 2)
    offloaded_gbps = round(total_gbps * offload_ratio, 2)
    remaining_transit_gbps = round(total_gbps - offloaded_gbps, 2)
    hybrid_cost = round(remaining_transit_gbps * 1000 * transit_usd_per_mbps + ixp_port_usd_month, 2)
    monthly_savings = round(all_transit_cost - hybrid_cost, 2)
    return {
        "total_peak_gbps": total_gbps,
        "all_transit_monthly_usd": all_transit_cost,
        "ixp_and_cdn_offload_gbps": offloaded_gbps,
        "hybrid_monthly_usd": hybrid_cost,
        "monthly_opex_savings_usd": monthly_savings,
        "roi_positive": monthly_savings > 0,
    }


def select_sp_transport(legacy_ldp_only: bool, needs_5g_slicing_and_tilfa: bool) -> dict:
    if needs_5g_slicing_and_tilfa and not legacy_ldp_only:
        return {
            "recommended": "SR-MPLS (or SRv6) + Flex-Algo + TI-LFA + EVPN",
            "reason": "Eliminates LDP/RSVP state in Core, gives 100% <50ms TI-LFA and latency-based Flex-Algo slices",
        }
    if needs_5g_slicing_and_tilfa and legacy_ldp_only:
        return {
            "recommended": "Phased SR-MPLS migration using SRMS (Mapping Server) alongside LDP",
            "reason": "Allows gradual brownfield upgrade without forklift outage",
        }
    return {
        "recommended": "Classic MPLS LDP + LFA/rLFA (BGP-Free Core)",
        "reason": "Simplest stable fit for basic L3VPN on legacy hardware without TE slicing needs",
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_SP_MODELER",
        "transit_vs_ixp_economics": model_sp_peering_economics(
            total_gbps=400.0,
            transit_usd_per_mbps=0.65,
            ixp_port_usd_month=18000.0,
            offload_ratio=0.65,
        ),
        "transport_architecture_choices": {
            "greenfield_5g_carrier": select_sp_transport(False, True),
            "brownfield_upgrade_to_5g": select_sp_transport(True, True),
            "legacy_l3vpn_only": select_sp_transport(True, False),
        },
        "bgp_free_core_p_router_rib_routes": {"igp_loopbacks_only": 1200, "full_internet_plus_vpn_avoided": 1_800_000},
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
