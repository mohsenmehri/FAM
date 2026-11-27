#!/usr/bin/env python3
"""
Local Mock Lab — ccie_01 (CCIE Enterprise Infrastructure v1.1: Dual-Module Gate, Route-Tag Loop Prevention & SD-Access Fusion)
Simulates (1) CCIE 8-hour Lab dual-pass scoring gate (Design 3h + DOO 5h),
(2) Mutual OSPF<->EIGRP redistribution loop prevention using route-tags,
and (3) SD-Access Border to Fusion Router VRF-Lite peering health check.
No real Cisco CML, Catalyst Center, SD-WAN vManage, or IOS-XE router is connected.
"""

import ipaddress
import json
import math


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_pct(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a finite percentage in [0, 100], got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval) or not (0.0 <= fval <= 100.0):
        raise ValueError(f"{name} must be in [0, 100], got {val!r}")
    return fval


def evaluate_ccie_exam_gate(design_pct: float, doo_pct: float, min_mod: float = 65.0, min_total: float = 75.0) -> dict:
    # Illustrative model thresholds (Cisco does NOT publish exact numeric CCIE pass cutoffs;
    # only the dual-gate rule — passing both modules AND the overall score — is official).
    d_pct = _require_pct(design_pct, "design_pct")
    o_pct = _require_pct(doo_pct, "doo_pct")
    m_cut = _require_pct(min_mod, "min_mod")
    t_cut = _require_pct(min_total, "min_total")
    weighted_exact = d_pct * 0.375 + o_pct * 0.625
    weighted = round(weighted_exact, 2)
    passed = d_pct >= m_cut and o_pct >= m_cut and weighted_exact >= t_cut
    reasons = []
    if d_pct < m_cut:
        reasons.append(f"Design score {d_pct}% below illustrative module cutoff {m_cut}%")
    if o_pct < m_cut:
        reasons.append(f"DOO score {o_pct}% below illustrative module cutoff {m_cut}%")
    if weighted_exact < t_cut:
        reasons.append(f"Aggregate {weighted}% below illustrative overall cutoff {t_cut}%")
    return {
        "design_pct": d_pct,
        "doo_pct": o_pct,
        "weighted_total": weighted,
        "passed": passed,
        "reasons": reasons,
        "threshold_note": "Illustrative thresholds only; Cisco does not publicly disclose numeric CCIE cutoffs.",
    }


def simulate_redistribution(prefix: str, origin_proto: str, tag: int | None, filter_enabled: bool) -> dict:
    # Classic two-point mutual OSPF <-> EIGRP redistribution scenario
    if not isinstance(prefix, str):
        raise ValueError(f"prefix must be a CIDR string, got {prefix!r}")
    net = str(ipaddress.ip_network(prefix, strict=True))
    if not isinstance(origin_proto, str) or not origin_proto.strip():
        raise ValueError(f"origin_proto must be a non-empty str, got {origin_proto!r}")
    if tag is not None and (isinstance(tag, bool) or not isinstance(tag, int) or tag < 0):
        raise ValueError(f"tag must be None or a non-negative int (not bool), got {tag!r}")
    filt = _require_bool(filter_enabled, "filter_enabled")
    if not filt:
        return {
            "prefix": net,
            "origin": origin_proto,
            "loop_detected": True,
            "cause": "Without route-tag filtering, EIGRP external (AD 170) vs OSPF (AD 110) re-injects prefix back at R2 -> suboptimal path / routing loop!",
        }
    if origin_proto == "EIGRP" and tag == 90:
        return {
            "prefix": net,
            "origin": origin_proto,
            "tag_applied": 90,
            "re_injection_at_r2": "DENIED_BY_ROUTE_MAP_TAG_90",
            "loop_detected": False,
        }
    return {"prefix": net, "origin": origin_proto, "loop_detected": False, "tag_applied": tag}


def check_sda_fusion_vrf(vrf: str, border_bgp_up: bool, fusion_route_leaked: bool, sgt_mapped: bool) -> dict:
    if not isinstance(vrf, str) or not vrf.strip():
        raise ValueError(f"vrf must be a non-empty str, got {vrf!r}")
    bgp_up = _require_bool(border_bgp_up, "border_bgp_up")
    leaked = _require_bool(fusion_route_leaked, "fusion_route_leaked")
    sgt_ok = _require_bool(sgt_mapped, "sgt_mapped")
    ok = bgp_up and leaked and sgt_ok
    return {
        "vrf": vrf,
        "border_to_fusion_ebgp": "UP" if bgp_up else "DOWN",
        "shared_services_leaked": leaked,
        "ise_sgt_policy_ok": sgt_ok,
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
