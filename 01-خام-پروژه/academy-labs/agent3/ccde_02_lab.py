#!/usr/bin/env python3
"""
Local Mock Lab — ccde_02 (CCDE Enterprise Architecture: Campus Access Selector, Branch Profiles & Summarization)
Models CCDE Enterprise Composite design choices across Campus Access architectures (L2, L3 Routed, SD-Access),
right-sized Branch Profiles (Small/Medium/Large), and contiguous block CIDR summarization boundaries
with strict boolean/numeric/subnet input validation.
No real enterprise switches, routers, or Catalyst Center controllers are connected.
"""

import ipaddress
import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_pos_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val <= 0:
        raise ValueError(f"{name} must be a positive integer, got {val!r}")
    return val


def recommend_campus_access(needs_l2_mobility: bool, needs_sgt_microseg: bool, max_convergence_ms: int) -> dict:
    l2_mob = _require_bool(needs_l2_mobility, "needs_l2_mobility")
    sgt_seg = _require_bool(needs_sgt_microseg, "needs_sgt_microseg")
    conv_ms = _require_pos_int(max_convergence_ms, "max_convergence_ms")
    if l2_mob and sgt_seg:
        return {"architecture": "SD-Access Overlay (LISP/VXLAN + ISE)", "reason": "Delivers L2 mobility without STP + dynamic SGT segmentation"}
    if not l2_mob and conv_ms <= 200:
        return {"architecture": "L3 Routed Access (L3 to Access Switch)", "reason": "Eliminates STP completely, ECMP uplinks, sub-second IGP/BFD convergence"}
    return {"architecture": "Traditional L2 Access with L3 Distribution (SVL/HSRP)", "reason": "Simple and budget-friendly when VLAN mobility is limited to one block"}


def classify_branch_profile(users: int, revenue_critical: bool) -> dict:
    user_cnt = _require_pos_int(users, "users")
    rev_crit = _require_bool(revenue_critical, "revenue_critical")
    if user_cnt <= 25 and not rev_crit:
        return {"profile": "Small Branch", "wan": "Single Broadband + 4G/5G LTE backup", "routers": 1, "local_voice": "Cloud/Central"}
    if user_cnt <= 150:
        return {"profile": "Medium Branch", "wan": "Dual ISP (DIA + Broadband) with SD-WAN", "routers": 2, "local_voice": "SRST Recommended"}
    return {"profile": "Large Regional Hub", "wan": "MPLS + DIA Hybrid SD-WAN (Dual Carrier)", "routers": 2, "local_voice": "HA CUBE/SRST Mandatory"}


def verify_block_summarization(subnets: list[str]) -> dict:
    if not subnets:
        raise ValueError("subnets must be a non-empty list of CIDR prefixes")
    nets = [ipaddress.ip_network(s, strict=True) for s in subnets]
    versions = {n.version for n in nets}
    if len(versions) != 1:
        raise ValueError("All subnets in a single summarization block must share the same IP version")
    collapsed = [str(n) for n in ipaddress.collapse_addresses(nets)]
    return {"input_subnets": subnets, "summarized_blocks": collapsed, "clean_single_summary": len(collapsed) == 1}


def main() -> None:
    hosp = recommend_campus_access(True, True, 500)
    trade = recommend_campus_access(False, False, 150)
    office = recommend_campus_access(False, False, 2000)
    b_small = classify_branch_profile(12, False)
    b_med = classify_branch_profile(90, True)
    b_large = classify_branch_profile(450, True)
    sum_ok = verify_block_summarization(["10.10.0.0/24", "10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"])
    sum_bad = verify_block_summarization(["10.10.0.0/24", "10.10.5.0/24", "10.10.9.0/24"])

    assert "SD-Access" in hosp["architecture"] and "L3 Routed" in trade["architecture"]
    assert b_small["profile"] == "Small Branch" and b_med["profile"] == "Medium Branch" and b_large["profile"] == "Large Regional Hub"
    assert sum_ok["clean_single_summary"] is True and sum_ok["summarized_blocks"] == ["10.10.0.0/22"]
    assert sum_bad["clean_single_summary"] is False

    report = {
        "mode": "LOCAL_MOCK_CCDE_ENTERPRISE_MODELER",
        "campus_decisions": {
            "hospital_zero_trust_mobility": hosp,
            "trading_floor_fast_convergence": trade,
            "simple_office_low_budget": office,
        },
        "branch_profiles": {
            "sales_kiosk_12_users": b_small,
            "regional_branch_90_users": b_med,
            "hq_regional_hub_450_users": b_large,
        },
        "campus_block_summarization": {
            "contiguous_building_a": sum_ok,
            "discontiguous_bad_plan": sum_bad,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
