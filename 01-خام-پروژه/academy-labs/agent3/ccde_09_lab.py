#!/usr/bin/env python3
"""
Local Mock Lab — ccde_09 (CCDE Resiliency Architecture: 5-Layer Risk Audit & Fast Convergence vs Dampening)
Audits a network design across all 5 CCDE resiliency layers (Physical/L1, L2/L3, Control Plane,
Management/Controller, Human Ops) and simulates IP Event Dampening vs Fast Convergence with strict
boundary checks (rejecting negative flap counts and distinguishing 0 flaps steady-state from single fault).
No real production routers or physical fiber plants are connected.
"""

import json


def audit_five_resiliency_layers(design: dict) -> dict:
    findings = []
    if not design["diverse_fiber_ducts"]:
        findings.append("L1_PHYSICAL_SHARED_FATE: Dual circuits share same conduit/entry duct.")
    if not design["loop_free_l3_ecmp"]:
        findings.append("L2_L3_RISK: Flat STP domain creates wide broadcast/loop blast radius.")
    if not design["graceful_control_plane_limits"]:
        findings.append("CONTROL_PLANE_RISK: Missing BGP max-prefix, CoPP, or route summarization.")
    if not design["out_of_band_mgmt_and_ha_controller"]:
        findings.append("MGMT_RISK: In-band-only management or single controller SPOF.")
    if not design["automated_validated_changes"]:
        findings.append("HUMAN_OPS_RISK: Unreviewed manual CLI changes are a leading cause of outages.")
    return {"design_name": design["name"], "layers_passing": 5 - len(findings), "risks": findings}


def simulate_flap_dampening(flaps_in_60s: int, suppress_threshold: int = 4) -> dict:
    if isinstance(flaps_in_60s, bool) or not isinstance(flaps_in_60s, int) or flaps_in_60s < 0:
        raise ValueError(f"flaps_in_60s must be a non-negative integer, got {flaps_in_60s!r}")
    if isinstance(suppress_threshold, bool) or not isinstance(suppress_threshold, int) or suppress_threshold < 1:
        raise ValueError(f"suppress_threshold must be an integer >= 1, got {suppress_threshold!r}")
    if flaps_in_60s == 0:
        return {
            "flaps_in_60s": 0,
            "action": "NO_FAULT_STEADY_STATE",
            "reason": "Zero link flaps observed in window; interface remains stable in forwarding state.",
        }
    if flaps_in_60s >= suppress_threshold:
        return {
            "flaps_in_60s": flaps_in_60s,
            "action": "DAMPEN_SUPPRESS_INTERFACE",
            "reason": "Prevents repeated SPF/BGP churn across core; stability beats chasing a broken flapping optic.",
        }
    return {
        "flaps_in_60s": flaps_in_60s,
        "action": "FAST_CONVERGE_SUBSECOND_BFD_FRR",
        "reason": "Isolated fault below dampening threshold -> trigger sub-second BFD + LFA/TI-LFA recovery.",
    }


def main() -> None:
    bad_design = audit_five_resiliency_layers({
        "name": "Legacy_Single_Duct_Campus",
        "diverse_fiber_ducts": False,
        "loop_free_l3_ecmp": False,
        "graceful_control_plane_limits": False,
        "out_of_band_mgmt_and_ha_controller": True,
        "automated_validated_changes": False,
    })
    good_design = audit_five_resiliency_layers({
        "name": "CCDE_Hardened_Architecture",
        "diverse_fiber_ducts": True,
        "loop_free_l3_ecmp": True,
        "graceful_control_plane_limits": True,
        "out_of_band_mgmt_and_ha_controller": True,
        "automated_validated_changes": True,
    })
    steady = simulate_flap_dampening(0)
    single_cut = simulate_flap_dampening(1)
    flapping = simulate_flap_dampening(12)

    assert bad_design["layers_passing"] == 1 and good_design["layers_passing"] == 5
    assert steady["action"] == "NO_FAULT_STEADY_STATE"
    assert single_cut["action"] == "FAST_CONVERGE_SUBSECOND_BFD_FRR"
    assert flapping["action"] == "DAMPEN_SUPPRESS_INTERFACE"

    report = {
        "mode": "LOCAL_MOCK_CCDE_RESILIENCY_MODELER",
        "five_layer_audits": [bad_design, good_design],
        "convergence_vs_stability": {
            "steady_state_zero_flaps": steady,
            "single_clean_fiber_cut": single_cut,
            "failing_sfp_flapping_12x": flapping,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
