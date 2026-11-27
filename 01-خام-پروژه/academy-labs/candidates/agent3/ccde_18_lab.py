#!/usr/bin/env python3
"""
Local Mock Lab — ccde_18 (CCDE Capstone Case Study 1: Pars-Global Multi-Site Enterprise Architecture)
Validates HLD design assumptions for Pars-Global (3 continents, Frankfurt & Dubai DCs ~5,000 km great-circle
apart, 100 branches, Multi-Cloud AWS/Azure, PCI-DSS & Pars-Global corporate EU data-residency policy).

Key modeling boundaries:
- Strict input typing: all boolean inputs MUST be strict Python bool (True/False) — strings like "False"/"True"/"",
  integers 0/1, None, lists, and dicts are explicitly rejected with ValueError. Huge integers (e.g. 10**500) that
  overflow IEEE-754 float are caught and rejected with ValueError (never OverflowError).
- Named product sync RTT profiles (not generalized across different storage products):
  * vmware_vsan_stretched: <= 5.0 ms RTT (VMware vSAN Stretched Cluster data-site guideline, version dependent)
  * netapp_vmsc_snapmirror_active_sync: < 10.0 ms RTT strictly (NetApp vMSC with SnapMirror active sync)
  * netapp_ontap_select_metrocluster_sds: <= 5.0 ms RTT (+ <= 5.0 ms jitter requirement; ONTAP Select MetroCluster SDS)
- Latency figures separate ideal straight-line silica fiber propagation (~0.01 ms/km => ~50 ms at 5,000 km),
  illustrative routed-fiber propagation (default 1.4x => ~70 ms), and optional illustrative equipment/path
  overhead (+35 ms default => ~105 ms inside the ~95-130 ms assumed total RTT range) — all explicitly marked as
  model assumptions, NOT live circuit measurements.
- RPO checking in this local model verifies ONLY high-level mode/target compatibility (e.g., async cannot meet RPO=0);
  it does NOT prove real achieved RPO (which depends on WAN bandwidth, write change rate, replication queue depth,
  snapshot cadence, and live DR failover drills).
- Boolean compliance inputs are unverified HLD assumptions, NOT legal opinions, DPO sign-off, or PCI-DSS QSA evidence.
No real international circuits, storage arrays, or enterprise sites are connected.
"""

import json
import math

PRODUCT_SYNC_PROFILES = {
    "vmware_vsan_stretched": {
        "max_rtt_ms": 5.0,
        "strict_lt": False,
        "comparator_text": "<= 5.0 ms",
        "source_note": "VMware vSAN Stretched Cluster data-site RTT ceiling (<= 5 ms; verify exact vSAN release).",
    },
    "netapp_vmsc_snapmirror_active_sync": {
        "max_rtt_ms": 10.0,
        "strict_lt": True,
        "comparator_text": "< 10.0 ms",
        "source_note": (
            "NetApp vMSC with SnapMirror active sync requires strictly < 10 ms RTT "
            "(https://docs.netapp.com/us-en/netapp-solutions-virtualization/vmware/vmw-vmsc-with-smas.html)."
        ),
    },
    "netapp_ontap_select_metrocluster_sds": {
        "max_rtt_ms": 5.0,
        "max_jitter_ms": 5.0,
        "strict_lt": False,
        "comparator_text": "<= 5.0 ms RTT and <= 5.0 ms jitter",
        "source_note": (
            "NetApp ONTAP Select MetroCluster SDS requires <= 5 ms RTT and <= 5 ms jitter "
            "(https://docs.netapp.com/us-en/ontap-select/concept_ha_config.html)."
        ),
    },
}

VALID_REPLICATION_MODES = ("synchronous", "asynchronous")

VALID_CHAPTER_V_SAFEGUARDS = (
    "adequacy_decision",
    "sccs_plus_tia_supplementary_measures",
    "binding_corporate_rules",
)


def _require_bool(design: dict, key: str) -> bool:
    if key not in design:
        raise ValueError(f"Missing required boolean input '{key}'")
    val = design[key]
    if not isinstance(val, bool):
        raise ValueError(
            f"{key} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})"
        )
    return val


def _require_str(design: dict, key: str) -> str:
    if key not in design:
        raise ValueError(f"Missing required string input '{key}'")
    val = design[key]
    if not isinstance(val, str):
        raise ValueError(f"{key} must be a str, got {val!r} ({type(val).__name__})")
    return val


def _to_finite_float(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number (not bool), got {value!r}")
    try:
        fval = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {value!r}") from exc
    if not math.isfinite(fval):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return fval


def _require_positive_finite(value: object, name: str) -> float:
    fval = _to_finite_float(value, name)
    if fval <= 0:
        raise ValueError(f"{name} must be a positive finite number, got {value!r}")
    return fval


def _require_non_negative_finite(value: object, name: str) -> float:
    fval = _to_finite_float(value, name)
    if fval < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {value!r}")
    return fval


def estimate_fiber_rtt_ms(
    great_circle_km: float,
    route_stretch_factor: float = 1.4,
    assumed_equipment_and_detour_overhead_ms: float = 35.0,
) -> dict:
    dist_km = _require_positive_finite(great_circle_km, "great_circle_km")
    stretch = _require_positive_finite(route_stretch_factor, "route_stretch_factor")
    if stretch < 1.0:
        raise ValueError(f"route_stretch_factor must be >= 1.0, got {stretch}")
    overhead = _require_non_negative_finite(
        assumed_equipment_and_detour_overhead_ms,
        "assumed_equipment_and_detour_overhead_ms",
    )

    # Ideal straight-line silica fiber (~200,000 km/s => ~0.01 ms/km propagation-only RTT)
    propagation_min = round(dist_km * 0.01, 2)
    raw_propagation = dist_km * 0.01
    raw_routed = raw_propagation * stretch
    raw_total_rtt = raw_routed + overhead
    if not math.isfinite(raw_total_rtt):
        raise ValueError("computed RTT exceeds finite float range")
    routed_propagation = round(raw_routed, 2)
    assumed_total_rtt = round(raw_total_rtt, 2)
    return {
        "assumed_total_end_to_end_rtt_unrounded_ms": raw_total_rtt,
        "great_circle_km": dist_km,
        "route_stretch_factor_assumed": stretch,
        "propagation_only_min_rtt_ms": propagation_min,
        "routed_propagation_only_rtt_ms": routed_propagation,
        "assumed_equipment_and_detour_overhead_ms": overhead,
        "assumed_total_end_to_end_rtt_ms": assumed_total_rtt,
        "latency_assumption_note": (
            "Illustrative model estimate only (not measured carrier RTT); real RTT depends on actual "
            "submarine/terrestrial cable path, DWDM optics, and intermediate routing hops."
        ),
    }


def validate_pars_global_hld(design: dict, sync_product_profile: str = "netapp_vmsc_snapmirror_active_sync") -> dict:
    if not isinstance(design, dict):
        raise ValueError(f"design must be a dict, got {type(design).__name__}")
    if sync_product_profile not in PRODUCT_SYNC_PROFILES:
        raise ValueError(
            f"Unknown sync_product_profile {sync_product_profile!r}; "
            f"expected one of {sorted(PRODUCT_SYNC_PROFILES)}"
        )

    if "dc_distance_km" not in design:
        raise ValueError("Missing required numeric input 'dc_distance_km'")
    dist_km = _require_positive_finite(design["dc_distance_km"], "dc_distance_km")
    overhead_ms = _require_non_negative_finite(
        design.get("assumed_equipment_and_detour_overhead_ms", 35.0 if dist_km >= 1000 else 1.0),
        "assumed_equipment_and_detour_overhead_ms",
    )
    target_rpo_min = _require_non_negative_finite(design.get("target_rpo_minutes", 15.0), "target_rpo_minutes")

    if "macro_vrfs" not in design:
        raise ValueError("Missing required integer input 'macro_vrfs'")
    macro_vrfs = design["macro_vrfs"]
    if isinstance(macro_vrfs, bool) or not isinstance(macro_vrfs, int) or macro_vrfs < 0:
        raise ValueError(f"macro_vrfs must be a non-negative integer, got {macro_vrfs!r}")

    # Strict boolean validation for EVERY boolean input in the HLD model
    dci_l2_stretched = _require_bool(design, "dci_l2_stretched")
    gslb_enabled = _require_bool(design, "gslb_enabled")
    micro_sgt_enabled = _require_bool(design, "micro_sgt_enabled")
    eu_policy_enforced = _require_bool(design, "eu_residency_policy_enforced")
    transferred_outside_eea = _require_bool(design, "eu_personal_data_transferred_outside_eea")
    encryption_assumed = _require_bool(design, "encryption_in_transit_assumed")

    rep_mode = _require_str(design, "storage_replication")
    wan_model = _require_str(design, "wan_model")
    cloud_hub = _require_str(design, "cloud_hub")
    safeguard = design.get("chapter_v_transfer_safeguard")
    if safeguard is not None and not isinstance(safeguard, str):
        raise ValueError(
            f"chapter_v_transfer_safeguard must be None or str, got {safeguard!r} ({type(safeguard).__name__})"
        )

    checks = []
    rtt_info = estimate_fiber_rtt_ms(dist_km, assumed_equipment_and_detour_overhead_ms=overhead_ms)
    profile = PRODUCT_SYNC_PROFILES[sync_product_profile]
    max_sync_ms = profile["max_rtt_ms"]
    # Compare the unrounded estimate: display rounding must not change a
    # strict boundary such as the SnapMirror active sync < 10 ms RTT limit.
    assumed_rtt = rtt_info["assumed_total_end_to_end_rtt_unrounded_ms"]
    rtt_ok = assumed_rtt < max_sync_ms if profile["strict_lt"] else assumed_rtt <= max_sync_ms
    jitter_limit = profile.get("max_jitter_ms")
    jitter = design.get("assumed_jitter_ms")
    if jitter is not None:
        jitter = _require_non_negative_finite(jitter, "assumed_jitter_ms")
    jitter_ok = None if jitter_limit is not None and jitter is None else (
        jitter <= jitter_limit if jitter_limit is not None else None
    )
    # The Select profile cannot pass its model check without a jitter assumption.
    # No profile check is proof of full product compatibility or measurement.
    sync_feasible_for_profile = rtt_ok and (jitter_limit is None or jitter_ok is True)

    rep_mode_valid = rep_mode in VALID_REPLICATION_MODES
    if not rep_mode_valid:
        replication_ok = False
    elif not sync_feasible_for_profile:
        replication_ok = rep_mode == "asynchronous"
    else:
        replication_ok = True

    # High-level mode/target RPO consistency ONLY (does NOT prove real achieved RPO!)
    rpo_mode_compatible = rep_mode_valid and (target_rpo_min > 0 or rep_mode == "synchronous")
    l2_stretch_policy_ok = not dci_l2_stretched
    gslb_ok = gslb_enabled
    dci_pass = rep_mode_valid and replication_ok and rpo_mode_compatible and l2_stretch_policy_ok and gslb_ok

    dci_reasons = []
    if not rep_mode_valid:
        dci_reasons.append(
            f"REJECTED: unsupported storage_replication mode {rep_mode!r}; "
            f"expected one of {VALID_REPLICATION_MODES}."
        )
    else:
        jitter_text = (
            "no jitter limit modeled for this profile" if jitter_limit is None else
            "required jitter assumption missing" if jitter is None else
            f"assumed jitter {jitter:g} ms, limit <= {jitter_limit:g} ms"
        )
        dci_reasons.append(
            f"Assumed RTT {assumed_rtt:g} ms, modeled limit {profile['comparator_text']}; {jitter_text}. "
            "These are unverified assumptions, not proof of product support or observed performance."
        )
        if not sync_feasible_for_profile and rep_mode == "synchronous":
            dci_reasons.append("REJECTED: modeled sync RTT/jitter requirements not satisfied or unknown.")
        elif not sync_feasible_for_profile:
            dci_reasons.append("Asynchronous mode selected; the modeled sync requirements need not pass.")

    if rep_mode_valid:
        if rpo_mode_compatible:
            dci_reasons.append(
                f"Target RPO ({target_rpo_min} min) is mode-compatible with '{rep_mode}' replication "
                "(model check only; actual achieved RPO requires WAN throughput, churn-rate, and DR drill validation)."
            )
        else:
            dci_reasons.append(
                f"REJECTED (RPO): target RPO={target_rpo_min} min cannot be met by asynchronous replication."
            )

    if l2_stretch_policy_ok:
        dci_reasons.append("L3-only DCI architectural blast-radius policy satisfied.")
    else:
        dci_reasons.append("REJECTED (policy): stretched L2 DCI violates Pars-Global failure-domain isolation policy.")

    if gslb_ok:
        dci_reasons.append("GSLB site-steering input enabled for L3-only multi-DC failover.")
    else:
        dci_reasons.append("REJECTED (GSLB): gslb_enabled is False; L3-only Active/Active DCI requires GSLB/application steering.")

    checks.append({
        "domain": f"DCI, Storage Profile, RPO & GSLB ({dist_km:g} km great-circle)",
        "product_sync_profile": sync_product_profile,
        "product_sync_limit": profile["comparator_text"],
        "product_sync_source_note": profile["source_note"],
        "product_max_sync_rtt_ms": max_sync_ms,
        **rtt_info,
        "storage_replication": rep_mode,
        "storage_replication_valid": rep_mode_valid,
        "modeled_rtt_ok": rtt_ok,
        "assumed_jitter_ms": jitter,
        "modeled_jitter_ok": jitter_ok,
        "sync_feasible_for_profile": sync_feasible_for_profile,
        "sync_feasibility_scope": "Only modeled RTT and, where specified, jitter assumptions are checked; other product requirements are not validated.",
        "replication_ok": replication_ok,
        "target_rpo_minutes": target_rpo_min,
        "rpo_ok": rpo_mode_compatible,
        "rpo_scope_note": (
            "Model checks high-level replication-mode vs target-RPO consistency only; it does NOT prove "
            "real achieved RPO (which depends on WAN bandwidth, write change rate, replication queue depth, "
            "snapshot schedule, and live DR failover testing)."
        ),
        "l2_stretch_policy_ok": l2_stretch_policy_ok,
        "gslb_enabled": gslb_enabled,
        "gslb_ok": gslb_ok,
        "pass": dci_pass,
        "note": " ".join(dci_reasons),
    })

    wan_ok = wan_model == "hybrid_sdwan_regional_hubs_plus_sase"
    checks.append({
        "domain": "Global WAN (100 Branches across 3 Continents)",
        "pass": wan_ok,
        "note": (
            "Regional SD-WAN hubs + local DIA/SASE breakout aims to reduce intercontinental tromboning (subject to real ISP/SASE PoP measurements)."
            if wan_ok
            else f"REJECTED: WAN model '{wan_model}' risks intercontinental backhaul tromboning."
        ),
    })

    cloud_ok = cloud_hub == "dual_colo_cloud_exchange_direct_connect"
    checks.append({
        "domain": "Multi-Cloud Connectivity (AWS Frankfurt + Azure UAE)",
        "pass": cloud_ok,
        "note": (
            "Dual Colo Exchanges are designed to reduce Egress unit cost and Colo-to-Cloud RTT (subject to actual carrier/cloud pricing and route measurement)."
            if cloud_ok
            else f"REJECTED: cloud connectivity model '{cloud_hub}' lacks dual-colo direct-connect resilience."
        ),
    })

    seg_ok = (3 <= macro_vrfs <= 6) and micro_sgt_enabled
    residency_consistency_ok = not (eu_policy_enforced and transferred_outside_eea)
    if transferred_outside_eea:
        chapter_v_ok = safeguard in VALID_CHAPTER_V_SAFEGUARDS
    else:
        chapter_v_ok = safeguard is None or safeguard in VALID_CHAPTER_V_SAFEGUARDS

    compliance_assumptions_ok = (
        seg_ok
        and residency_consistency_ok
        and chapter_v_ok
        and encryption_assumed
        and (eu_policy_enforced or (transferred_outside_eea and chapter_v_ok))
    )

    comp_reasons = []
    if not seg_ok:
        comp_reasons.append("REJECTED: requires 3-6 Macro VRFs and Micro SGT enabled.")
    if not residency_consistency_ok:
        comp_reasons.append(
            "REJECTED (policy contradiction): eu_residency_policy_enforced=True conflicts with eu_personal_data_transferred_outside_eea=True."
        )
    if transferred_outside_eea and not chapter_v_ok:
        comp_reasons.append(
            f"REJECTED (GDPR Ch.V): cross-border transfer outside EEA requires valid safeguard in {VALID_CHAPTER_V_SAFEGUARDS}, got {safeguard!r}."
        )
    if not transferred_outside_eea and not eu_policy_enforced:
        comp_reasons.append("REJECTED: specify either corporate EU residency enforcement or documented cross-border transfer governance.")
    if not encryption_assumed:
        comp_reasons.append("REJECTED: encryption_in_transit_assumed is False (needed for PCI-DSS Req 4 / Art. 32 risk mitigation).")
    if not comp_reasons:
        if not transferred_outside_eea:
            comp_reasons.append(
                f"HLD technical assumptions consistent: {macro_vrfs} Macro VRFs + Micro SGT + encryption in transit + "
                "corporate EU residency policy enforced (no EU personal data transferred outside EEA; Chapter V safeguard not triggered)."
            )
        else:
            comp_reasons.append(
                f"HLD technical assumptions consistent: {macro_vrfs} Macro VRFs + Micro SGT + encryption in transit + "
                f"documented GDPR Chapter V transfer safeguard '{safeguard}'."
            )

    checks.append({
        "domain": "Segmentation, Encryption & EU Data-Governance Assumptions (PCI-DSS + GDPR Chapter V)",
        "macro_vrfs": macro_vrfs,
        "macro_vrfs_ok": 3 <= macro_vrfs <= 6,
        "micro_sgt_enabled": micro_sgt_enabled,
        "eu_residency_policy_enforced": eu_policy_enforced,
        "eu_personal_data_transferred_outside_eea": transferred_outside_eea,
        "chapter_v_transfer_safeguard": safeguard,
        "residency_consistency_ok": residency_consistency_ok,
        "chapter_v_ok": chapter_v_ok,
        "encryption_in_transit_assumed": encryption_assumed,
        "pass": compliance_assumptions_ok,
        "note": " ".join(comp_reasons),
        "assumption_disclaimer": (
            "Boolean inputs represent unverified HLD design assumptions ONLY — not legal opinions, DPO sign-off, "
            "or PCI-DSS QSA audit evidence. Network residency and encryption alone do not guarantee full GDPR/PCI compliance."
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
        "target_rpo_minutes": 0,
        "dci_l2_stretched": True,
        "gslb_enabled": False,
        "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
        "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
        "macro_vrfs": 4,
        "micro_sgt_enabled": True,
        "eu_residency_policy_enforced": True,
        "eu_personal_data_transferred_outside_eea": False,
        "chapter_v_transfer_safeguard": None,
        "encryption_in_transit_assumed": True,
    }
    approved_pars_global_hld = {
        **rejected_initial_proposal,
        "storage_replication": "asynchronous",
        "target_rpo_minutes": 15,
        "dci_l2_stretched": False,
        "gslb_enabled": True,
    }
    metro_sync_feasible_example = {
        **approved_pars_global_hld,
        "dc_distance_km": 150,
        "assumed_equipment_and_detour_overhead_ms": 1.0,
        "storage_replication": "synchronous",
        "target_rpo_minutes": 0,
    }
    invalid_mode_example = {
        **metro_sync_feasible_example,
        "storage_replication": "not-a-real-mode",
    }

    res_rejected = validate_pars_global_hld(rejected_initial_proposal, "vmware_vsan_stretched")
    res_approved = validate_pars_global_hld(approved_pars_global_hld, "netapp_vmsc_snapmirror_active_sync")
    res_metro = validate_pars_global_hld(metro_sync_feasible_example, "vmware_vsan_stretched")
    res_bad_mode = validate_pars_global_hld(invalid_mode_example, "vmware_vsan_stretched")

    assert res_rejected["all_architectural_checks_passed"] is False
    assert res_approved["all_architectural_checks_passed"] is True
    assert res_metro["all_architectural_checks_passed"] is True
    assert res_metro["domain_validations"][0]["sync_feasible_for_profile"] is True
    assert "violates" not in res_metro["domain_validations"][0]["note"]
    assert res_bad_mode["all_architectural_checks_passed"] is False
    assert "unsupported storage_replication mode" in res_bad_mode["domain_validations"][0]["note"]
    assert "is supported" not in res_bad_mode["domain_validations"][0]["note"]

    # Negative check: non-bool string "False" and huge int 10**500 MUST raise ValueError
    for bad_input in (
        {**approved_pars_global_hld, "gslb_enabled": "False"},
        {**approved_pars_global_hld, "dc_distance_km": 10**500},
    ):
        try:
            validate_pars_global_hld(bad_input)
            raise AssertionError(f"Expected ValueError for {bad_input!r}")
        except ValueError:
            pass

    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPSTONE_PARS_GLOBAL",
        "rejected_sync_l2_proposal": res_rejected,
        "approved_hld_validation": res_approved,
        "metro_sync_feasible_example": res_metro,
        "invalid_mode_rejected_example": res_bad_mode,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
