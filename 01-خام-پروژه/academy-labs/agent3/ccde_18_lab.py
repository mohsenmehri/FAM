#!/usr/bin/env python3
"""
Local Mock Lab — ccde_18 (CCDE Capstone Case Study 1: Pars-Global Multi-Site Enterprise Architecture)
Validates the end-to-end HLD for Pars-Global (3 continents, Frankfurt & Dubai DCs ~5,000 km great-circle
apart, 100 branches, Multi-Cloud AWS/Azure, PCI-DSS & GDPR) using product-conditioned synchronous
replication RTT limits (e.g., VMware vSAN <=5ms, NetApp MetroCluster/vMSC <=10ms) and both theoretical
fiber lower-bound (~0.01 ms/km) and realistic routed-fiber stretch (~1.4x).
No real international circuits, storage arrays, or enterprise sites are connected.
"""

import json

PRODUCT_SYNC_RTT_LIMITS_MS = {
    "vmware_vsan_stretched": 5.0,
    "vmware_vmsc_netapp_metrocluster": 10.0,
}


def estimate_fiber_rtt_ms(great_circle_km: float, route_stretch_factor: float = 1.4) -> dict:
    # Ideal straight-line silica fiber (~200,000 km/s => ~0.01 ms/km RTT); real routes add stretch + equipment delay
    theoretical_min = round(great_circle_km * 0.01, 2)
    estimated_routed = round(theoretical_min * route_stretch_factor, 2)
    return {
        "great_circle_km": great_circle_km,
        "theoretical_fiber_min_rtt_ms": theoretical_min,
        "estimated_routed_fiber_rtt_ms": estimated_routed,
    }


def validate_pars_global_hld(design: dict, sync_product_profile: str = "vmware_vmsc_netapp_metrocluster") -> dict:
    checks = []
    rtt_info = estimate_fiber_rtt_ms(design["dc_distance_km"])
    max_sync_ms = PRODUCT_SYNC_RTT_LIMITS_MS[sync_product_profile]
    sync_feasible_for_profile = rtt_info["estimated_routed_fiber_rtt_ms"] <= max_sync_ms
    replication_ok = (
        (design["storage_replication"] == "asynchronous")
        if not sync_feasible_for_profile
        else design["storage_replication"] in ("synchronous", "asynchronous")
    )
    checks.append({
        "domain": "DCI & Storage Physics (Frankfurt <-> Dubai ~5,000 km)",
        "product_sync_profile": sync_product_profile,
        "product_max_sync_rtt_ms": max_sync_ms,
        **rtt_info,
        "sync_feasible_for_profile": sync_feasible_for_profile,
        "pass": replication_ok and (design["dci_l2_stretched"] is False),
        "note": (
            f"Theoretical min {rtt_info['theoretical_fiber_min_rtt_ms']} ms / routed ~{rtt_info['estimated_routed_fiber_rtt_ms']} ms RTT "
            f"exceeds {sync_product_profile} ceiling ({max_sync_ms} ms) -> Async + L3-Only DCI + GSLB required."
        ),
    })
    checks.append({
        "domain": "Global WAN (100 Branches across 3 Continents)",
        "pass": design["wan_model"] == "hybrid_sdwan_regional_hubs_plus_sase",
        "note": "Regional SD-WAN hubs + Local DIA/SASE breakout eliminates intercontinental tromboning",
    })
    checks.append({
        "domain": "Multi-Cloud Connectivity (AWS Frankfurt + Azure UAE)",
        "pass": design["cloud_hub"] == "dual_colo_cloud_exchange_direct_connect",
        "note": "Dual Colo Exchanges lower Egress (provider/tier-dependent) and cut Colo-to-Cloud RTT",
    })
    checks.append({
        "domain": "End-to-End Segmentation & Compliance (PCI-DSS + GDPR)",
        "pass": (3 <= design["macro_vrfs"] <= 6) and design["micro_sgt_enabled"] and design["gdpr_eu_data_local"],
        "note": "4 Macro VRFs (Corp/PCI/IoT/Guest) + Micro SGT (QSA-validated scope reduction) + EU GDPR pinning",
    })
    return {
        "case_study": "Pars-Global Enterprise (3 Continents | 2 DCs | 100 Branches)",
        "all_architectural_checks_passed": all(c["pass"] for c in checks),
        "domain_validations": checks,
    }


def main() -> None:
    rejected_initial_proposal = {
        "dc_distance_km": 5000,
        "storage_replication": "synchronous",
        "dci_l2_stretched": True,
        "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
        "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
        "macro_vrfs": 4,
        "micro_sgt_enabled": True,
        "gdpr_eu_data_local": True,
    }
    approved_pars_global_hld = {
        **rejected_initial_proposal,
        "storage_replication": "asynchronous",
        "dci_l2_stretched": False,
    }
    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPSTONE_PARS_GLOBAL",
        "rejected_sync_l2_proposal": validate_pars_global_hld(rejected_initial_proposal, "vmware_vsan_stretched"),
        "approved_hld_validation": validate_pars_global_hld(approved_pars_global_hld, "vmware_vmsc_netapp_metrocluster"),
    }
    assert report["rejected_sync_l2_proposal"]["all_architectural_checks_passed"] is False
    assert report["approved_hld_validation"]["all_architectural_checks_passed"] is True
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
