#!/usr/bin/env python3
"""
Local Mock Lab — ccde_02 (CCDE Enterprise Architecture: Campus Access Selector, Branch Profiles & Summarization)
Models CCDE Enterprise Composite design choices across Campus Access architectures (L2, L3 Routed, SD-Access),
right-sized Branch Profiles (Small/Medium/Large), and contiguous block CIDR summarization boundaries.
No real enterprise switches, routers, or Catalyst Center controllers are connected.
"""

import ipaddress
import json


def recommend_campus_access(needs_l2_mobility: bool, needs_sgt_microseg: bool, max_convergence_ms: int) -> dict:
    if needs_l2_mobility and needs_sgt_microseg:
        return {"architecture": "SD-Access Overlay (LISP/VXLAN + ISE)", "reason": "Delivers L2 mobility without STP + dynamic SGT segmentation"}
    if not needs_l2_mobility and max_convergence_ms <= 200:
        return {"architecture": "L3 Routed Access (L3 to Access Switch)", "reason": "Eliminates STP completely, ECMP uplinks, sub-second IGP/BFD convergence"}
    return {"architecture": "Traditional L2 Access with L3 Distribution (SVL/HSRP)", "reason": "Simple and budget-friendly when VLAN mobility is limited to one block"}


def classify_branch_profile(users: int, revenue_critical: bool) -> dict:
    if users <= 25 and not revenue_critical:
        return {"profile": "Small Branch", "wan": "Single Broadband + 4G/5G LTE backup", "routers": 1, "local_voice": "Cloud/Central"}
    if users <= 150:
        return {"profile": "Medium Branch", "wan": "Dual ISP (DIA + Broadband) with SD-WAN", "routers": 2, "local_voice": "SRST Recommended"}
    return {"profile": "Large Regional Hub", "wan": "MPLS + DIA Hybrid SD-WAN (Dual Carrier)", "routers": 2, "local_voice": "HA CUBE/SRST Mandatory"}


def verify_block_summarization(subnets: list[str]) -> dict:
    nets = [ipaddress.ip_network(s) for s in subnets]
    collapsed = [str(n) for n in ipaddress.collapse_addresses(nets)]
    return {"input_subnets": subnets, "summarized_blocks": collapsed, "clean_single_summary": len(collapsed) == 1}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_ENTERPRISE_MODELER",
        "campus_decisions": {
            "hospital_zero_trust_mobility": recommend_campus_access(True, True, 500),
            "trading_floor_fast_convergence": recommend_campus_access(False, False, 150),
            "simple_office_low_budget": recommend_campus_access(False, False, 2000),
        },
        "branch_profiles": {
            "sales_kiosk_12_users": classify_branch_profile(12, False),
            "regional_branch_90_users": classify_branch_profile(90, True),
            "hq_regional_hub_450_users": classify_branch_profile(450, True),
        },
        "campus_block_summarization": {
            "contiguous_building_a": verify_block_summarization(["10.10.0.0/24", "10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]),
            "discontiguous_bad_plan": verify_block_summarization(["10.10.0.0/24", "10.10.5.0/24", "10.10.9.0/24"]),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
