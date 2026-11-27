#!/usr/bin/env python3
"""
Local Mock Lab — ccde_17 (CCDE Technology Trade-Offs & 5-Year TCO: CapEx vs OpEx & Architecture Duels)
Computes 5-Year Total Cost of Ownership (CapEx + 5yr OpEx + Ops Training/FTE) across competing
architectures with strict non-negative finite cost validation (preventing negative costs and zero-division).
All figures are illustrative scenario inputs, NOT real vendor quotes.
No real vendor price lists or production fabrics are connected.
"""

import json
import math


def _require_non_negative_cost(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {val!r}")
    return float(val)


def compute_5yr_tco(
    option: str,
    capex_yr0: float,
    annual_lic_support: float,
    annual_ops_fte_cost: float,
    annual_circuit_opex: float,
) -> dict:
    capex = _require_non_negative_cost(capex_yr0, "capex_yr0")
    lic = _require_non_negative_cost(annual_lic_support, "annual_lic_support")
    fte = _require_non_negative_cost(annual_ops_fte_cost, "annual_ops_fte_cost")
    circ = _require_non_negative_cost(annual_circuit_opex, "annual_circuit_opex")

    opex_5yr = round((lic + fte + circ) * 5.0, 2)
    tco_5yr = round(capex + opex_5yr, 2)
    if tco_5yr <= 0:
        raise ValueError(f"Total 5-year TCO for '{option}' must be > 0 to compute cost breakdown")
    return {
        "option": option,
        "capex_yr0_usd": capex,
        "opex_5yr_usd": opex_5yr,
        "total_5yr_tco_usd": tco_5yr,
        "opex_share_pct": round((opex_5yr / tco_5yr) * 100.0, 1),
    }


def main() -> None:
    dc_duel = [
        compute_5yr_tco("Open_VXLAN_EVPN_MultiVendor_Automated", capex_yr0=900000, annual_lic_support=110000, annual_ops_fte_cost=260000, annual_circuit_opex=0),
        compute_5yr_tco("Turnkey_ACI_SingleVendor_PolicyFabric", capex_yr0=1150000, annual_lic_support=170000, annual_ops_fte_cost=190000, annual_circuit_opex=0),
    ]
    wan_duel = [
        compute_5yr_tco("Legacy_Dual_MPLS_LowCapEx_HighOpEx", capex_yr0=200000, annual_lic_support=40000, annual_ops_fte_cost=180000, annual_circuit_opex=900000),
        compute_5yr_tco("Hybrid_SDWAN_HigherCapEx_LowOpEx", capex_yr0=450000, annual_lic_support=90000, annual_ops_fte_cost=150000, annual_circuit_opex=480000),
    ]
    dc_sorted = sorted(dc_duel, key=lambda x: x["total_5yr_tco_usd"])
    wan_sorted = sorted(wan_duel, key=lambda x: x["total_5yr_tco_usd"])
    assert wan_sorted[0]["option"] == "Hybrid_SDWAN_HigherCapEx_LowOpEx"
    assert wan_sorted[0]["total_5yr_tco_usd"] == 4050000.0
    assert wan_sorted[1]["total_5yr_tco_usd"] == 5800000.0

    report = {
        "mode": "LOCAL_MOCK_CCDE_TRADEOFF_TCO_MODELER",
        "dc_fabric_5yr_tco_duel": dc_sorted,
        "wan_5yr_tco_duel": wan_sorted,
        "key_insight": "Illustrative scenario numbers only — OpEx often dominates 5-year TCO compared to Day-1 CapEx; verify with live vendor/carrier quotes.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
