#!/usr/bin/env python3
"""
Local Mock Lab — ccde_09 (CCDE Resiliency Architecture: 5-Layer Risk Audit & Fast Convergence vs Dampening)
Audits a network design across all 5 CCDE resiliency layers (Physical/L1, L2/L3, Control Plane,
Management/Controller, Human Ops) and simulates IP Event Dampening vs Fast Convergence under link flapping.
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
        findings.append("HUMAN_OPS_RISK: Unreviewed manual CLI changes are top cause of outages.")
    return {"design_name": design["name"], "layers_passing": 5 - len(findings), "risks": findings}


def simulate_flap_dampening(flaps_in_60s: int, suppress_threshold: int = 4) -> dict:
    if flaps_in_60s >= suppress_threshold:
        return {
            "flaps_in_60s": flaps_in_60s,
            "action": "DAMPEN_SUPPRESS_INTERFACE",
            "reason": "Prevents endless SPF/BGP churn across core; stability beats chasing a broken flapping optic!",
        }
    return {
        "flaps_in_60s": flaps_in_60s,
        "action": "FAST_CONVERGE_SUBSECOND_BFD_FRR",
        "reason": "Clean single fault -> trigger sub-second BFD + LFA/TI-LFA recovery immediately.",
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_RESILIENCY_MODELER",
        "five_layer_audits": [
            audit_five_resiliency_layers({
                "name": "Legacy_Single_Duct_Campus",
                "diverse_fiber_ducts": False,
                "loop_free_l3_ecmp": False,
                "graceful_control_plane_limits": False,
                "out_of_band_mgmt_and_ha_controller": True,
                "automated_validated_changes": False,
            }),
            audit_five_resiliency_layers({
                "name": "CCDE_Hardened_Architecture",
                "diverse_fiber_ducts": True,
                "loop_free_l3_ecmp": True,
                "graceful_control_plane_limits": True,
                "out_of_band_mgmt_and_ha_controller": True,
                "automated_validated_changes": True,
            }),
        ],
        "convergence_vs_stability": {
            "single_clean_fiber_cut": simulate_flap_dampening(1),
            "failing_sfp_flapping_12x": simulate_flap_dampening(12),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
