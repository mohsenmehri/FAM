#!/usr/bin/env python3
"""
Local Mock Lab — ccie_01 (CCIE Enterprise Infrastructure v1.1: Dual-Module Gate, Route-Tag Loop Prevention & SD-Access Fusion)
Simulates (1) CCIE 8-hour Lab dual-pass scoring gate (Design 3h + DOO 5h),
(2) Mutual OSPF<->EIGRP redistribution loop prevention using route-tags,
and (3) SD-Access Border to Fusion Router VRF-Lite peering health check.
No real Cisco CML, Catalyst Center, SD-WAN vManage, or IOS-XE router is connected.
"""

import json


def evaluate_ccie_exam_gate(design_pct: float, doo_pct: float, min_mod: float = 65.0, min_total: float = 75.0) -> dict:
    # Illustrative model thresholds (Cisco does NOT publish exact numeric CCIE pass cutoffs;
    # only the dual-gate rule — passing both modules AND the overall score — is official).
    weighted = round(design_pct * 0.375 + doo_pct * 0.625, 2)
    passed = design_pct >= min_mod and doo_pct >= min_mod and weighted >= min_total
    reasons = []
    if design_pct < min_mod:
        reasons.append(f"Design score {design_pct}% below illustrative module cutoff {min_mod}%")
    if doo_pct < min_mod:
        reasons.append(f"DOO score {doo_pct}% below illustrative module cutoff {min_mod}%")
    if weighted < min_total:
        reasons.append(f"Aggregate {weighted}% below illustrative overall cutoff {min_total}%")
    return {
        "design_pct": design_pct,
        "doo_pct": doo_pct,
        "weighted_total": weighted,
        "passed": passed,
        "reasons": reasons,
        "threshold_note": "Illustrative thresholds only; Cisco does not publicly disclose numeric CCIE cutoffs.",
    }


def simulate_redistribution(prefix: str, origin_proto: str, tag: int | None, filter_enabled: bool) -> dict:
    # Classic two-point mutual OSPF <-> EIGRP redistribution scenario
    if not filter_enabled:
        return {
            "prefix": prefix,
            "origin": origin_proto,
            "loop_detected": True,
            "cause": "Without route-tag filtering, EIGRP external (AD 170) vs OSPF (AD 110) re-injects prefix back at R2 -> suboptimal path / routing loop!",
        }
    if origin_proto == "EIGRP" and tag == 90:
        return {
            "prefix": prefix,
            "origin": origin_proto,
            "tag_applied": 90,
            "re_injection_at_r2": "DENIED_BY_ROUTE_MAP_TAG_90",
            "loop_detected": False,
        }
    return {"prefix": prefix, "origin": origin_proto, "loop_detected": False, "tag_applied": tag}


def check_sda_fusion_vrf(vrf: str, border_bgp_up: bool, fusion_route_leaked: bool, sgt_mapped: bool) -> dict:
    ok = border_bgp_up and fusion_route_leaked and sgt_mapped
    return {
        "vrf": vrf,
        "border_to_fusion_ebgp": "UP" if border_bgp_up else "DOWN",
        "shared_services_leaked": fusion_route_leaked,
        "ise_sgt_policy_ok": sgt_mapped,
        "ready": ok,
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_CML_OR_CCIE_POD",
        "exam_gate_simulations": {
            "high_cli_but_failed_design": evaluate_ccie_exam_gate(55.0, 92.0),
            "balanced_pass": evaluate_ccie_exam_gate(80.0, 84.0),
        },
        "mutual_redistribution_check": {
            "without_route_tags": simulate_redistribution("10.50.0.0/24", "EIGRP", None, filter_enabled=False),
            "with_route_tag_90": simulate_redistribution("10.50.0.0/24", "EIGRP", 90, filter_enabled=True),
        },
        "sda_fusion_verification": check_sda_fusion_vrf("CORP_VN", border_bgp_up=True, fusion_route_leaked=True, sgt_mapped=True),
    }
    assert report["exam_gate_simulations"]["high_cli_but_failed_design"]["passed"] is False
    assert report["exam_gate_simulations"]["balanced_pass"]["passed"] is True
    assert report["mutual_redistribution_check"]["without_route_tags"]["loop_detected"] is True
    assert report["mutual_redistribution_check"]["with_route_tag_90"]["loop_detected"] is False
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
