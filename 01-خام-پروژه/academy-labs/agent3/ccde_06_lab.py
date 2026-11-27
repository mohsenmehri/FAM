#!/usr/bin/env python3
"""
Local Mock Lab — ccde_06 (CCDE WAN Architecture: MPLS vs Hybrid SD-WAN TCO & AAR Path Selector)
Compares 3-year WAN TCO of Dual-MPLS vs Hybrid SD-WAN (MPLS + DIA Broadband),
and simulates Application-Aware Routing (AAR) SLA steering for Voice/ERP vs Bulk/SaaS traffic.
No real SD-WAN controllers, MPLS circuits, or branch WAN routers are connected.
"""

import json


def compare_wan_tco(branches: int, mpls_usd_mo: float, dia_usd_mo: float, sdwan_lic_usd_mo: float) -> dict:
    dual_mpls_3yr = branches * (2 * mpls_usd_mo) * 36
    hybrid_sdwan_3yr = branches * (mpls_usd_mo + dia_usd_mo + sdwan_lic_usd_mo) * 36
    dual_internet_sdwan_3yr = branches * (2 * dia_usd_mo + sdwan_lic_usd_mo) * 36
    return {
        "branches": branches,
        "dual_mpls_3yr_usd": dual_mpls_3yr,
        "hybrid_mpls_plus_dia_sdwan_3yr_usd": hybrid_sdwan_3yr,
        "dual_internet_sdwan_3yr_usd": dual_internet_sdwan_3yr,
        "hybrid_savings_vs_dual_mpls_usd": dual_mpls_3yr - hybrid_sdwan_3yr,
    }


def aar_select_path(app: str, sla: dict, transports: list[dict]) -> dict:
    passing = [
        t for t in transports
        if t["rtt_ms"] <= sla["max_rtt"] and t["jitter_ms"] <= sla["max_jitter"] and t["loss_pct"] <= sla["max_loss"]
    ]
    if passing:
        best = sorted(passing, key=lambda t: (t["rtt_ms"], t["cost_rank"]))[0]
        return {"app": app, "selected_transport": best["name"], "sla_met": True}
    fallback = sorted(transports, key=lambda t: t["loss_pct"])[0]
    return {"app": app, "selected_transport": fallback["name"], "sla_met": False, "note": "Fallback to lowest-loss transport"}


def main() -> None:
    transports = [
        {"name": "MPLS_Primary", "rtt_ms": 28, "jitter_ms": 3, "loss_pct": 0.05, "cost_rank": 2},
        {"name": "DIA_Internet", "rtt_ms": 42, "jitter_ms": 9, "loss_pct": 0.3, "cost_rank": 1},
        {"name": "LTE_5G_Backup", "rtt_ms": 95, "jitter_ms": 25, "loss_pct": 1.8, "cost_rank": 3},
    ]
    report = {
        "mode": "LOCAL_MOCK_CCDE_WAN_MODELER",
        "three_year_tco_100_branches": compare_wan_tco(branches=100, mpls_usd_mo=1800, dia_usd_mo=350, sdwan_lic_usd_mo=150),
        "aar_path_decisions": [
            aar_select_path("VoIP_ContactCenter", {"max_rtt": 100, "max_jitter": 15, "max_loss": 0.5}, transports),
            aar_select_path("M365_SaaS_LocalBreakout", {"max_rtt": 150, "max_jitter": 30, "max_loss": 1.0}, [transports[1], transports[2]]),
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
