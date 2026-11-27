#!/usr/bin/env python3
"""
Local Mock Lab — ccde_13 (CCDE Traffic Engineering: 4 TE Levels, SR-TE Flex-Algo & Post-Failure Capacity Trap)
Models the 4 CCDE Traffic Engineering levels (IGP/ECMP, BGP Communities, RSVP-TE, SR-TE/Flex-Algo)
and simulates the classic Post-Failure Capacity Instability Trap with strict validation on link names,
surviving backup availability, and non-negative flow/capacity parameters.
No real carrier routers or PCE controllers are connected.
"""

import json


def simulate_post_failure_te(links: dict[str, dict], primary_flow_gbps: float, backup_existing_gbps: float, failed_link: str) -> dict:
    if failed_link not in links:
        raise ValueError(f"failed_link '{failed_link}' not found in links {sorted(links)}")
    if primary_flow_gbps < 0 or backup_existing_gbps < 0:
        raise ValueError("Traffic flow values must be non-negative")
    surviving = {k: v for k, v in links.items() if k != failed_link}
    if not surviving:
        raise ValueError("No surviving backup link available after failure (single-point-of-failure outage)")
    backup_name, backup = next(iter(surviving.items()))
    if backup["capacity_gbps"] <= 0:
        raise ValueError(f"Backup link '{backup_name}' capacity_gbps must be > 0")
    post_fail_load = round(backup_existing_gbps + primary_flow_gbps, 2)
    congested = post_fail_load > backup["capacity_gbps"]
    return {
        "failed_link": failed_link,
        "rerouted_onto": backup_name,
        "backup_capacity_gbps": backup["capacity_gbps"],
        "post_failure_total_load_gbps": post_fail_load,
        "post_failure_congestion_meltdown": congested,
        "remediation": (
            "Pre-reserve TE headroom or split critical vs best-effort classes (QoS + Flex-Algo)"
            if congested
            else "Clean failover within backup link capacity"
        ),
    }


def select_te_level(needs_explicit_latency_slice: bool, large_scale_stateless: bool, multi_homed_internet: bool) -> dict:
    if needs_explicit_latency_slice and large_scale_stateless:
        return {"level": "Level 4: SR-TE + Flex-Algo + PCE", "reason": "Explicit low-latency/disjoint paths with zero midpoint per-flow state"}
    if multi_homed_internet:
        return {"level": "Level 2: BGP Attributes & Communities (Local-Pref / MED / Prepend)", "reason": "Clean egress/ingress steering at internet ASBR edges"}
    return {"level": "Level 1: IGP Metric Tuning + ECMP", "reason": "Simplest stable TE — never over-engineer TE when IGP ECMP suffices!"}


def main() -> None:
    links = {
        "Link_A_LowLatency_100G": {"capacity_gbps": 100.0, "delay_ms": 8},
        "Link_B_HighBW_100G": {"capacity_gbps": 100.0, "delay_ms": 22},
    }
    overloaded = simulate_post_failure_te(links, primary_flow_gbps=70.0, backup_existing_gbps=60.0, failed_link="Link_A_LowLatency_100G")
    headroomed = simulate_post_failure_te(links, primary_flow_gbps=45.0, backup_existing_gbps=40.0, failed_link="Link_A_LowLatency_100G")
    assert overloaded["post_failure_congestion_meltdown"] is True
    assert headroomed["post_failure_congestion_meltdown"] is False

    report = {
        "mode": "LOCAL_MOCK_CCDE_TRAFFIC_ENGINEERING_MODELER",
        "te_level_recommendations": {
            "5g_ultra_low_latency_carrier": select_te_level(True, True, False),
            "enterprise_dual_isp_edge": select_te_level(False, False, True),
            "balanced_campus_core": select_te_level(False, False, False),
        },
        "post_failure_trap_check": {
            "overloaded_backup_trap": overloaded,
            "properly_headroomed_backup": headroomed,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
