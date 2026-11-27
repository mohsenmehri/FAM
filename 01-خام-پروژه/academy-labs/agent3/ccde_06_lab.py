#!/usr/bin/env python3
"""
Local Mock Lab — ccde_06 (CCDE WAN Architecture: MPLS vs Hybrid SD-WAN TCO & AAR Path Selector)
Compares 3-year WAN TCO of Dual-MPLS vs Hybrid SD-WAN (MPLS + DIA Broadband),
and simulates Application-Aware Routing (AAR) SLA steering for Voice/ERP vs Bulk/SaaS traffic.
No real SD-WAN controllers, MPLS circuits, or branch WAN routers are connected.
"""

import json
import math


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


def compare_wan_tco(branches: int, mpls_usd_mo: float, dia_usd_mo: float, sdwan_lic_usd_mo: float) -> dict:
    if isinstance(branches, bool) or not isinstance(branches, int) or branches <= 0:
        raise ValueError(f"branches must be a positive int (not bool), got {branches!r}")
    mpls = _require_non_neg_finite(mpls_usd_mo, "mpls_usd_mo")
    dia = _require_non_neg_finite(dia_usd_mo, "dia_usd_mo")
    lic = _require_non_neg_finite(sdwan_lic_usd_mo, "sdwan_lic_usd_mo")
    try:
        dual_mpls_3yr = branches * (2.0 * mpls) * 36.0
        hybrid_sdwan_3yr = branches * (mpls + dia + lic) * 36.0
        dual_internet_sdwan_3yr = branches * (2.0 * dia + lic) * 36.0
    except OverflowError as exc:
        raise ValueError("WAN TCO calculation overflowed IEEE-754 finite float range") from exc
    if not all(math.isfinite(v) for v in (dual_mpls_3yr, hybrid_sdwan_3yr, dual_internet_sdwan_3yr)):
        raise ValueError("WAN TCO calculation produced non-finite value")
    return {
        "branches": branches,
        "dual_mpls_3yr_usd": dual_mpls_3yr,
        "hybrid_mpls_plus_dia_sdwan_3yr_usd": hybrid_sdwan_3yr,
        "dual_internet_sdwan_3yr_usd": dual_internet_sdwan_3yr,
        "hybrid_savings_vs_dual_mpls_usd": dual_mpls_3yr - hybrid_sdwan_3yr,
    }


def aar_select_path(app: str, sla: dict, transports: list[dict]) -> dict:
    if not isinstance(app, str) or not app.strip():
        raise ValueError(f"app must be a non-empty str, got {app!r}")
    if not isinstance(sla, dict):
        raise ValueError("sla must be a dict")
    if not isinstance(transports, list) or not transports:
        raise ValueError("transports must be a non-empty list of dicts")
    max_rtt = _require_non_neg_finite(sla.get("max_rtt"), "sla['max_rtt']")
    max_jitter = _require_non_neg_finite(sla.get("max_jitter"), "sla['max_jitter']")
    max_loss = _require_non_neg_finite(sla.get("max_loss"), "sla['max_loss']")
    if max_loss > 100.0:
        raise ValueError(f"sla['max_loss'] must be in [0, 100], got {max_loss!r}")
    clean = []
    for t in transports:
        if not isinstance(t, dict) or not isinstance(t.get("name"), str) or not t["name"].strip():
            raise ValueError(f"invalid transport entry: {t!r}")
        rtt = _require_non_neg_finite(t.get("rtt_ms"), f"{t['name']}.rtt_ms")
        jit = _require_non_neg_finite(t.get("jitter_ms"), f"{t['name']}.jitter_ms")
        loss = _require_non_neg_finite(t.get("loss_pct"), f"{t['name']}.loss_pct")
        if loss > 100.0:
            raise ValueError(f"{t['name']}.loss_pct must be in [0, 100], got {loss!r}")
        rank = _require_non_neg_finite(t.get("cost_rank", 1), f"{t['name']}.cost_rank")
        clean.append({"name": t["name"], "rtt_ms": rtt, "jitter_ms": jit, "loss_pct": loss, "cost_rank": rank})
    passing = [
        t for t in clean
        if t["rtt_ms"] <= max_rtt and t["jitter_ms"] <= max_jitter and t["loss_pct"] <= max_loss
    ]
    if passing:
        best = sorted(passing, key=lambda t: (t["rtt_ms"], t["cost_rank"]))[0]
        return {"app": app, "selected_transport": best["name"], "sla_met": True}
    fallback = sorted(clean, key=lambda t: t["loss_pct"])[0]
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
