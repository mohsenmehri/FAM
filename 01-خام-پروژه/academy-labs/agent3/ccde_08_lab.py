#!/usr/bin/env python3
"""
Local Mock Lab — ccde_08 (CCDE Network Segmentation: Macro VRF vs Micro SGT & Over-Segmentation Guard)
Models Macro-Segmentation (VRF-Lite / MPLS VPN) vs Micro-Segmentation (SGT / EPG Policy Matrix),
and warns when excessive VRF/Zone proliferation triggers the CCDE Over-Segmentation operational trap.
Strict validation rejects non-positive VRF/engineer counts, negative SGT counts, bools, and empty SGT names.
No real Cisco ISE, SD-Access fabric, or enterprise firewalls are connected.
"""

import json


def _require_int(val: object, name: str, min_val: int) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val < min_val:
        raise ValueError(f"{name} must be an int >= {min_val} (not bool), got {val!r}")
    return val


def evaluate_segmentation_plan(vrfs: int, sgts: int, ops_engineers: int) -> dict:
    vrf_n = _require_int(vrfs, "vrfs", 1)
    sgt_n = _require_int(sgts, "sgts", 0)
    ops_n = _require_int(ops_engineers, "ops_engineers", 1)

    # Rule of thumb: keep Macro VRFs compact (3-6); handle fine-grained isolation with Micro SGT/EPG
    warnings = []
    if vrf_n > 8:
        warnings.append(
            f"OVER-SEGMENTATION TRAP: {vrf_n} Macro VRFs create massive route-leaking/firewall complexity for {ops_n} engineers!"
        )
    if sgt_n == 0:
        warnings.append("Missing Micro-Segmentation (SGT/EPG): lateral movement inside a VRF remains unrestricted.")
    verdict = "BALANCED_MACRO_PLUS_MICRO" if not warnings else "NEEDS_REDESIGN"
    return {
        "macro_vrfs": vrf_n,
        "micro_sgt_groups": sgt_n,
        "ops_team_size": ops_n,
        "verdict": verdict,
        "warnings": warnings,
    }


def check_sgt_matrix(src_sgt: str, dst_sgt: str, policy: dict[tuple[str, str], str]) -> dict:
    if not isinstance(src_sgt, str) or not src_sgt.strip():
        raise ValueError(f"src_sgt must be a non-empty str, got {src_sgt!r}")
    if not isinstance(dst_sgt, str) or not dst_sgt.strip():
        raise ValueError(f"dst_sgt must be a non-empty str, got {dst_sgt!r}")
    if not isinstance(policy, dict):
        raise ValueError("policy must be a dict mapping (src_sgt, dst_sgt) -> action")
    action = policy.get((src_sgt, dst_sgt), "DENY_DEFAULT")
    return {"src_sgt": src_sgt, "dst_sgt": dst_sgt, "action": action}


def main() -> None:
    sgt_policy = {
        ("Employees", "Shared_Services"): "PERMIT_DNS_AD_HTTPS",
        ("IoT_Cameras", "NVR_Servers"): "PERMIT_RTSP_ONLY",
        ("PCI_POS", "Payment_Gateway"): "PERMIT_TLS_1_3_ONLY",
    }
    bad_plan = evaluate_segmentation_plan(vrfs=45, sgts=0, ops_engineers=4)
    good_plan = evaluate_segmentation_plan(vrfs=4, sgts=12, ops_engineers=4)
    assert bad_plan["verdict"] == "NEEDS_REDESIGN" and len(bad_plan["warnings"]) == 2
    assert good_plan["verdict"] == "BALANCED_MACRO_PLUS_MICRO" and good_plan["warnings"] == []
    denied = check_sgt_matrix("IoT_Cameras", "PCI_POS", sgt_policy)
    assert denied["action"] == "DENY_DEFAULT"

    report = {
        "mode": "LOCAL_MOCK_CCDE_SEGMENTATION_MODELER",
        "architecture_audits": {
            "over_segmented_45_vrfs": bad_plan,
            "recommended_4_macro_vrfs_plus_sgts": good_plan,
        },
        "micro_segmentation_decisions": [
            check_sgt_matrix("Employees", "Shared_Services", sgt_policy),
            denied,
            check_sgt_matrix("PCI_POS", "Payment_Gateway", sgt_policy),
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
