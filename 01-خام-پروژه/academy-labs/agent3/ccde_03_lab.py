#!/usr/bin/env python3
"""
Local Mock Lab — ccde_03 (CCDE Service Provider Architecture: Transit vs IXP Peering Economics & SR/MPLS Choice)
Models Service Provider internet economics (Tier-1 Transit vs IXP Settlement-Free Peering + CDN Cache),
verifies BGP-Free Core P-router scaling, and recommends LDP vs SR-MPLS/EVPN based on hardware & 5G SLA.
No real carrier core routers or IXP fabrics are connected.
"""

import json
import math


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_non_neg_finite(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a non-negative finite number (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval) or fval < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {val!r}")
    return fval


def model_sp_peering_economics(total_gbps: float, transit_usd_per_mbps: float, ixp_port_usd_month: float, offload_ratio: float) -> dict:
    gbps = _require_non_neg_finite(total_gbps, "total_gbps")
    transit = _require_non_neg_finite(transit_usd_per_mbps, "transit_usd_per_mbps")
    ixp = _require_non_neg_finite(ixp_port_usd_month, "ixp_port_usd_month")
    ratio = _require_non_neg_finite(offload_ratio, "offload_ratio")
    if ratio > 1.0:
        raise ValueError(f"offload_ratio must be in [0.0, 1.0], got {ratio!r}")
    all_transit_exact = gbps * 1000.0 * transit
    offloaded_exact = gbps * ratio
    remaining_exact = gbps - offloaded_exact
    hybrid_exact = remaining_exact * 1000.0 * transit + ixp
    savings_exact = all_transit_exact - hybrid_exact
    if not all(math.isfinite(v) for v in (all_transit_exact, hybrid_exact, savings_exact)):
        raise ValueError("peering economics calculation overflowed IEEE-754 finite float range")
    return {
        "total_peak_gbps": gbps,
        "all_transit_monthly_usd": round(all_transit_exact, 2),
        "ixp_and_cdn_offload_gbps": round(offloaded_exact, 2),
        "hybrid_monthly_usd": round(hybrid_exact, 2),
        "monthly_opex_savings_usd": round(savings_exact, 2),
        "roi_positive": savings_exact > 0,
    }


def select_sp_transport(legacy_ldp_only: bool, needs_5g_slicing_and_tilfa: bool) -> dict:
    legacy = _require_bool(legacy_ldp_only, "legacy_ldp_only")
    needs_5g = _require_bool(needs_5g_slicing_and_tilfa, "needs_5g_slicing_and_tilfa")
    if needs_5g and not legacy:
        return {
            "recommended": "SR-MPLS (or SRv6) + Flex-Algo + TI-LFA + EVPN",
            "reason": "Eliminates LDP/RSVP state in Core, enables TI-LFA loop-free protection on 2-connected topologies within hardware MSD (<50ms target with fast detection) and latency-based Flex-Algo slices",
        }
    if needs_5g and legacy:
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
