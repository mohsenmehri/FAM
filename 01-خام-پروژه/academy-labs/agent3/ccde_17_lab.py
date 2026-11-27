#!/usr/bin/env python3
"""
Local Mock Lab — ccde_17 (CCDE Technology Trade-Offs & 5-Year TCO: CapEx vs OpEx & Architecture Duels)
Computes 5-Year Total Cost of Ownership (CapEx + 5yr OpEx + Ops Training/FTE) across competing
architectures (e.g. VXLAN EVPN Multi-Vendor vs Cisco ACI, In-House vs Managed) and evaluates protocol trade-offs.
No real vendor price lists or production fabrics are connected.
"""

import json


def compute_5yr_tco(option: str, capex_yr0: float, annual_lic_support: float, annual_ops_fte_cost: float, annual_circuit_opex: float) -> dict:
    opex_5yr = (annual_lic_support + annual_ops_fte_cost + annual_circuit_opex) * 5
    tco_5yr = round(capex_yr0 + opex_5yr, 2)
    return {
        "option": option,
        "capex_yr0_usd": capex_yr0,
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
    report = {
        "mode": "LOCAL_MOCK_CCDE_TRADEOFF_TCO_MODELER",
        "dc_fabric_5yr_tco_duel": sorted(dc_duel, key=lambda x: x["total_5yr_tco_usd"]),
        "wan_5yr_tco_duel": sorted(wan_duel, key=lambda x: x["total_5yr_tco_usd"]),
        "key_insight": "OpEx typically accounts for 70-85% of 5-year TCO — cheapest Day-1 CapEx often loses badly over 5 years!",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
