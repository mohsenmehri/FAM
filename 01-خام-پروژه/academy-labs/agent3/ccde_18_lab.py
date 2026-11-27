#!/usr/bin/env python3
"""
Local Mock Lab — ccde_18 (CCDE Capstone Case Study 1: Pars-Global Multi-Site Enterprise Architecture)
Validates the end-to-end HLD for Pars-Global (3 continents, Frankfurt & Dubai DCs ~5,000 km great-circle
apart, 100 branches, Multi-Cloud AWS/Azure, PCI-DSS & Pars-Global corporate EU data-residency policy)
using product-conditioned synchronous replication RTT ceilings (e.g., VMware vSAN <=5ms, NetApp
MetroCluster/vMSC <=10ms), separated L2 blast-radius policy checks, and dynamic pass/fail diagnostics.
No real international circuits, storage arrays, or enterprise sites are connected.
"""

import json

PRODUCT_SYNC_RTT_LIMITS_MS = {
    "vmware_vsan_stretched": 5.0,
    "vmware_vmsc_netapp_metrocluster": 10.0,
}

VALID_TRANSFER_BASES = (
    "eu_eea_residency_policy",
    "chapter_v_adequacy_or_scc_tia",
)


def estimate_fiber_rtt_ms(great_circle_km: float, route_stretch_factor: float = 1.4) -> dict:
    # Ideal straight-line silica fiber (~200,000 km/s => ~0.01 ms/km propagation-only RTT);
    # real submarine/terrestrial cable routes add route stretch + DWDM/switching/routing delay.
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
        design["storage_replication"] == "asynchronous"
        if not sync_feasible_for_profile
        else design["storage_replication"] in ("synchronous", "asynchronous")
    )
    l2_stretch_policy_ok = design["dci_l2_stretched"] is False
    dci_pass = replication_ok and l2_stretch_policy_ok

    dci_reasons = []
    if sync_feasible_for_profile:
        dci_reasons.append(
            f"Estimated routed RTT (~{rtt_info['estimated_routed_fiber_rtt_ms']} ms; propagation-only min "
            f"{rtt_info['theoretical_fiber_min_rtt_ms']} ms) is within {sync_product_profile} ceiling ({max_sync_ms} ms); "
            f"selected mode '{design['storage_replication']}' is supported for this profile."
        )
    elif replication_ok:
        dci_reasons.append(
            f"Estimated routed RTT (~{rtt_info['estimated_routed_fiber_rtt_ms']} ms; propagation-only min "
            f"{rtt_info['theoretical_fiber_min_rtt_ms']} ms) exceeds {sync_product_profile} ceiling ({max_sync_ms} ms); "
            "asynchronous replication + GSLB appropriately selected."
        )
    else:
        dci_reasons.append(
            f"REJECTED: estimated routed RTT (~{rtt_info['estimated_routed_fiber_rtt_ms']} ms) exceeds "
            f"{sync_product_profile} sync ceiling ({max_sync_ms} ms); switch to asynchronous replication."
        )

    if l2_stretch_policy_ok:
        dci_reasons.append("L3-only DCI architectural blast-radius policy satisfied.")
    else:
        dci_reasons.append("REJECTED (policy): stretched L2 DCI violates Pars-Global failure-domain isolation policy.")

    checks.append({
        "domain": f"DCI & Storage Profile ({design['dc_distance_km']} km great-circle)",
        "product_sync_profile": sync_product_profile,
        "product_max_sync_rtt_ms": max_sync_ms,
        **rtt_info,
        "sync_feasible_for_profile": sync_feasible_for_profile,
        "replication_ok": replication_ok,
        "l2_stretch_policy_ok": l2_stretch_policy_ok,
        "pass": dci_pass,
        "note": " ".join(dci_reasons),
    })

    wan_ok = design["wan_model"] == "hybrid_sdwan_regional_hubs_plus_sase"
    checks.append({
        "domain": "Global WAN (100 Branches across 3 Continents)",
        "pass": wan_ok,
        "note": (
            "Regional SD-WAN hubs + local DIA/SASE breakout reduces intercontinental tromboning."
            if wan_ok
            else f"REJECTED: WAN model '{design['wan_model']}' risks intercontinental backhaul tromboning."
        ),
    })

    cloud_ok = design["cloud_hub"] == "dual_colo_cloud_exchange_direct_connect"
    checks.append({
        "domain": "Multi-Cloud Connectivity (AWS Frankfurt + Azure UAE)",
        "pass": cloud_ok,
        "note": (
            "Dual Colo Exchanges can lower Egress (provider/tier-dependent) and cut Colo-to-Cloud RTT."
            if cloud_ok
            else f"REJECTED: cloud connectivity model '{design['cloud_hub']}' lacks dual-colo direct-connect resilience."
        ),
    })

    transfer_basis = design.get("cross_border_transfer_basis", "")
    eu_policy_ok = bool(design.get("eu_residency_policy_enforced"))
    transfer_basis_ok = transfer_basis in VALID_TRANSFER_BASES
    encryption_ok = bool(design.get("encryption_in_transit"))
    seg_ok = (3 <= design["macro_vrfs"] <= 6) and bool(design["micro_sgt_enabled"])
    compliance_controls_ok = seg_ok and eu_policy_ok and transfer_basis_ok and encryption_ok
    checks.append({
        "domain": "Segmentation, Encryption & Corporate EU Residency Policy (PCI-DSS + GDPR Chapter V)",
        "macro_vrfs_ok": 3 <= design["macro_vrfs"] <= 6,
        "micro_sgt_enabled": bool(design["micro_sgt_enabled"]),
        "eu_residency_policy_enforced": eu_policy_ok,
        "cross_border_transfer_basis": transfer_basis,
        "encryption_in_transit": encryption_ok,
        "pass": compliance_controls_ok,
        "note": (
            "4 Macro VRFs + Micro SGT (QSA-validated PCI scope reduction) + IPsec/TLS/MACsec + Pars-Global "
            "corporate EU residency policy (chosen to minimize GDPR Chapter V transfer-safeguard overhead)."
            if compliance_controls_ok
            else "REJECTED: verify 3-6 Macro VRFs, Micro SGT, encryption in transit, corporate EU residency policy, and documented GDPR Chapter V transfer basis."
        ),
        "compliance_scope_note": (
            "Network residency and encryption are technical controls only; GDPR Chapter V (Arts. 44-49) allows "
            "transfers with adequacy decisions or SCCs/TIA, and full GDPR/PCI compliance requires DPO/legal "
            "governance, Art. 32 organizational controls, DPA/SCC contracts, and independent QSA assessment."
        ),
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
        "eu_residency_policy_enforced": True,
        "cross_border_transfer_basis": "eu_eea_residency_policy",
        "encryption_in_transit": True,
    }
    approved_pars_global_hld = {
        **rejected_initial_proposal,
        "storage_replication": "asynchronous",
        "dci_l2_stretched": False,
    }
    metro_sync_feasible_example = {
        **approved_pars_global_hld,
        "dc_distance_km": 150,
        "storage_replication": "synchronous",
    }
    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPSTONE_PARS_GLOBAL",
        "rejected_sync_l2_proposal": validate_pars_global_hld(rejected_initial_proposal, "vmware_vsan_stretched"),
        "approved_hld_validation": validate_pars_global_hld(approved_pars_global_hld, "vmware_vmsc_netapp_metrocluster"),
        "metro_sync_feasible_example": validate_pars_global_hld(metro_sync_feasible_example, "vmware_vsan_stretched"),
    }
    assert report["rejected_sync_l2_proposal"]["all_architectural_checks_passed"] is False
    assert report["approved_hld_validation"]["all_architectural_checks_passed"] is True
    assert report["metro_sync_feasible_example"]["all_architectural_checks_passed"] is True
    assert report["metro_sync_feasible_example"]["domain_validations"][0]["sync_feasible_for_profile"] is True
    assert "exceeds" not in report["metro_sync_feasible_example"]["domain_validations"][0]["note"]
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
