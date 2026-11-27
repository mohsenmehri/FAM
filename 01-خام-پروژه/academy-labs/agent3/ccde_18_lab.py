#!/usr/bin/env python3
"""
Local Mock Lab — ccde_18 (CCDE Capstone Case Study 1: Pars-Global Multi-Site Enterprise Architecture)
Validates the complete end-to-end HLD architecture for Pars-Global (3 continents, Frankfurt & Dubai DCs
5,000 km apart, 100 branches, Multi-Cloud AWS/Azure, PCI-DSS compliance) across physics, WAN, DCI & segmentation.
No real international circuits or enterprise sites are connected.
"""

import json


def validate_pars_global_hld(design: dict) -> dict:
    checks = []
    # 1. Frankfurt <-> Dubai = 5,000 km -> ~50ms fiber RTT -> Async replication mandatory!
    rtt_ms = design["dc_distance_km"] * 0.01
    checks.append({
        "domain": "DCI & Storage Physics (Frankfurt <-> Dubai 5,000km)",
        "measured_min_rtt_ms": rtt_ms,
        "pass": (design["storage_replication"] == "asynchronous") and (design["dci_l2_stretched"] is False),
        "note": "50ms RTT forbids Sync RPO=0; L3-Only DCI + GSLB eliminates cross-continental L2 broadcast fate!",
    })
    # 2. WAN Architecture for 100 global branches
    checks.append({
        "domain": "Global WAN (100 Branches across 3 Continents)",
        "pass": design["wan_model"] == "hybrid_sdwan_regional_hubs_plus_sase",
        "note": "Regional SD-WAN hubs + Local DIA/SASE breakout eliminates intercontinental tromboning & cuts MPLS OpEx",
    })
    # 3. Multi-Cloud Connectivity (AWS Frankfurt + Azure UAE)
    checks.append({
        "domain": "Multi-Cloud Connectivity",
        "pass": design["cloud_hub"] == "dual_colo_cloud_exchange_direct_connect",
        "note": "Carrier-neutral Colo Exchanges in Frankfurt & Dubai give low-latency private DX/ER + low Egress",
    })
    # 4. Segmentation & Compliance (PCI-DSS + GDPR)
    checks.append({
        "domain": "End-to-End Segmentation & Compliance",
        "pass": (3 <= design["macro_vrfs"] <= 6) and design["micro_sgt_enabled"] and design["gdpr_eu_data_local"],
        "note": "Compact 4 Macro VRFs (Corp/PCI/IoT/Guest) + Micro SGT + EU data stays in Frankfurt for GDPR!",
    })
    return {
        "case_study": "Pars-Global Enterprise (3 Continents | 2 DCs | 100 Branches)",
        "all_architectural_checks_passed": all(c["pass"] for c in checks),
        "domain_validations": checks,
    }


def main() -> None:
    pars_global_hld = {
        "dc_distance_km": 5000,
        "storage_replication": "asynchronous",
        "dci_l2_stretched": False,
        "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
        "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
        "macro_vrfs": 4,
        "micro_sgt_enabled": True,
        "gdpr_eu_data_local": True,
    }
    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPSTONE_PARS_GLOBAL",
        "validation_result": validate_pars_global_hld(pars_global_hld),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
