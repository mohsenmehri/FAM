#!/usr/bin/env python3
"""
Local Mock Lab — ccde_08 (CCDE Network Segmentation: Macro VRF vs Micro SGT & Over-Segmentation Guard)
Models Macro-Segmentation (VRF-Lite / MPLS VPN) vs Micro-Segmentation (SGT / EPG Policy Matrix),
and warns when excessive VRF/Zone proliferation triggers the CCDE Over-Segmentation operational trap.
No real Cisco ISE, SD-Access fabric, or enterprise firewalls are connected.
"""

import json


def evaluate_segmentation_plan(vrfs: int, sgts: int, ops_engineers: int) -> dict:
    # Rule of thumb: keep Macro VRFs compact (3-6); handle fine-grained isolation with Micro SGT/EPG
    warnings = []
    if vrfs > 8:
        warnings.append(f"OVER-SEGMENTATION TRAP: {vrfs} Macro VRFs create massive route-leaking/firewall complexity for {ops_engineers} engineers!")
    if sgts == 0:
        warnings.append("Missing Micro-Segmentation (SGT/EPG): lateral movement inside a VRF remains unrestricted.")
    verdict = "BALANCED_MACRO_PLUS_MICRO" if not warnings else "NEEDS_REDESIGN"
    return {"macro_vrfs": vrfs, "micro_sgt_groups": sgts, "ops_team_size": ops_engineers, "verdict": verdict, "warnings": warnings}


def check_sgt_matrix(src_sgt: str, dst_sgt: str, policy: dict[tuple[str, str], str]) -> dict:
    action = policy.get((src_sgt, dst_sgt), "DENY_DEFAULT")
    return {"src_sgt": src_sgt, "dst_sgt": dst_sgt, "action": action}


def main() -> None:
    sgt_policy = {
        ("Employees", "Shared_Services"): "PERMIT_DNS_AD_HTTPS",
        ("IoT_Cameras", "NVR_Servers"): "PERMIT_RTSP_ONLY",
        ("PCI_POS", "Payment_Gateway"): "PERMIT_TLS_1_3_ONLY",
    }
    report = {
        "mode": "LOCAL_MOCK_CCDE_SEGMENTATION_MODELER",
        "architecture_audits": {
            "over_segmented_45_vrfs": evaluate_segmentation_plan(vrfs=45, sgts=0, ops_engineers=4),
            "recommended_4_macro_vrfs_plus_sgts": evaluate_segmentation_plan(vrfs=4, sgts=12, ops_engineers=4),
        },
        "micro_segmentation_decisions": [
            check_sgt_matrix("Employees", "Shared_Services", sgt_policy),
            check_sgt_matrix("IoT_Cameras", "PCI_POS", sgt_policy),
            check_sgt_matrix("PCI_POS", "Payment_Gateway", sgt_policy),
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
