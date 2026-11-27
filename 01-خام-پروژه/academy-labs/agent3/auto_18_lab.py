#!/usr/bin/env python3
"""
FAM Academy Lab — auto_18: Automated Network Testing (pyATS/Genie Dq &
Batfish-style Pre-Deployment Graph Verification) Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of Genie operational diff,
Dq-style nested state filtering, and Batfish-style static routing-loop /
blackhole verification before production push. No live pyATS/Batfish runtime.
"""

from __future__ import annotations

import json


def dq_filter_down_bgp_peers(bgp_parsed: dict) -> list[str]:
    if not isinstance(bgp_parsed, dict):
        raise ValueError(f"bgp_parsed must be a dict, got {type(bgp_parsed).__name__}")
    down = []
    for vrf_data in bgp_parsed.get("vrf", {}).values():
        for peer_ip, info in vrf_data.get("neighbor", {}).items():
            if info.get("session_state") != "Established":
                down.append(peer_ip)
    return sorted(down)


def batfish_style_trace(rib: dict[str, dict[str, str]], start_router: str, dst_prefix: str) -> dict:
    if not isinstance(rib, dict):
        raise ValueError("rib must be a dict mapping router -> {prefix: next_hop}")
    if not isinstance(start_router, str) or not start_router.strip():
        raise ValueError("start_router must be a non-empty str")
    if not isinstance(dst_prefix, str) or not dst_prefix.strip():
        raise ValueError("dst_prefix must be a non-empty str")
    visited: list[str] = []
    cur = start_router
    while True:
        if cur in visited:
            return {"outcome": "ROUTING_LOOP", "path": visited + [cur]}
        visited.append(cur)
        next_hop = rib.get(cur, {}).get(dst_prefix)
        if next_hop is None:
            return {"outcome": "BLACKHOLE", "path": visited}
        if next_hop == "LOCAL_DELIVER":
            return {"outcome": "DELIVERED", "path": visited}
        cur = next_hop


def main() -> None:
    pre_bgp = {"vrf": {"default": {"neighbor": {
        "10.0.0.2": {"session_state": "Established", "prefixes": 120},
        "10.0.0.3": {"session_state": "Established", "prefixes": 85},
    }}}}
    post_bgp = {"vrf": {"default": {"neighbor": {
        "10.0.0.2": {"session_state": "Established", "prefixes": 120},
        "10.0.0.3": {"session_state": "Active", "prefixes": 0},
    }}}}
    pre_down = dq_filter_down_bgp_peers(pre_bgp)
    post_down = dq_filter_down_bgp_peers(post_bgp)
    assert pre_down == [] and post_down == ["10.0.0.3"]

    candidate_rib = {
        "R1": {"10.50.0.0/24": "R2", "10.99.0.0/24": "R3", "10.10.0.0/24": "R2"},
        "R2": {"10.50.0.0/24": "R1", "10.10.0.0/24": "LOCAL_DELIVER"},  # Loop on 10.50.0.0/24!
        "R3": {},  # Blackhole on 10.99.0.0/24!
    }
    loop_res = batfish_style_trace(candidate_rib, "R1", "10.50.0.0/24")
    bh_res = batfish_style_trace(candidate_rib, "R1", "10.99.0.0/24")
    ok_res = batfish_style_trace(candidate_rib, "R1", "10.10.0.0/24")
    assert loop_res["outcome"] == "ROUTING_LOOP"
    assert bh_res["outcome"] == "BLACKHOLE"
    assert ok_res["outcome"] == "DELIVERED"

    print("=== auto_18 pyATS/Genie Dq & Batfish-Style Pre-Check Local Mock ===")
    print(json.dumps({
        "genie_dq_post_change_down_bgp_peers": post_down,
        "batfish_style_loop_check": loop_res,
        "batfish_style_blackhole_check": bh_res,
        "batfish_style_healthy_check": ok_res,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
