#!/usr/bin/env python3
"""
FAM Academy Lab — spec_ent_campus: StackWise Virtual (SVL), MEC & DAD Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of Catalyst 9500/9600 SVL
prerequisite checks, MEC STP loop-free forwarding, and Dual-Active Detection
preventing Split-Brain. No live Catalyst hardware connected.
"""

from __future__ import annotations

import json


def validate_svl_pair(sw1: dict, sw2: dict) -> list[str]:
    errs = []
    if sw1["model"] != sw2["model"]:
        errs.append("SVL requires identical switch models")
    if sw1["ios_xe"] != sw2["ios_xe"]:
        errs.append("SVL requires matching IOS-XE versions")
    if sw1["license"] != "network-advantage" or sw2["license"] != "network-advantage":
        errs.append("SVL requires Network Advantage license on both peers")
    return errs


def simulate_svl_failure(svl_up: bool, dad_up: bool) -> dict:
    if svl_up:
        return {"sw1_role": "ACTIVE", "sw2_role": "STANDBY", "split_brain": False, "mec_active_uplinks": 2}
    if not svl_up and not dad_up:
        # Both assume Active with identical virtual MAC/IP -> Split-Brain!
        return {"sw1_role": "ACTIVE", "sw2_role": "ACTIVE", "split_brain": True, "mec_active_uplinks": 2}
    # SVL down, DAD alive -> Former Active enters Recovery (shuts non-DAD ports), Standby takes over cleanly!
    return {"sw1_role": "RECOVERY_MODE", "sw2_role": "ACTIVE", "split_brain": False, "mec_active_uplinks": 1}


def main() -> None:
    good_errs = validate_svl_pair(
        {"model": "C9500-48Y4C", "ios_xe": "17.9.4a", "license": "network-advantage"},
        {"model": "C9500-48Y4C", "ios_xe": "17.9.4a", "license": "network-advantage"},
    )
    bad_errs = validate_svl_pair(
        {"model": "C9200-48P", "ios_xe": "17.9.4a", "license": "network-essentials"},
        {"model": "C9500-48Y4C", "ios_xe": "17.12.1", "license": "network-advantage"},
    )
    assert good_errs == [] and len(bad_errs) == 3

    normal = simulate_svl_failure(svl_up=True, dad_up=True)
    split_brain = simulate_svl_failure(svl_up=False, dad_up=False)
    dad_protected = simulate_svl_failure(svl_up=False, dad_up=True)
    assert normal["mec_active_uplinks"] == 2
    assert split_brain["split_brain"] is True
    assert dad_protected["split_brain"] is False and dad_protected["sw1_role"] == "RECOVERY_MODE"

    print("=== spec_ent_campus SVL & DAD Local Mock ===")
    print(json.dumps({
        "valid_pair_errors": good_errs,
        "invalid_pair_errors": bad_errs,
        "normal_operation": normal,
        "svl_cut_without_dad": split_brain,
        "svl_cut_with_dad_protected": dad_protected,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
