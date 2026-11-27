#!/usr/bin/env python3
"""
FAM Academy Lab — spec_ent_campus: StackWise Virtual (SVL), MEC & DAD Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of Catalyst 9400/9500/9600 SVL
prerequisite checks (including supported platform family validation), MEC STP
loop-free forwarding, and Dual-Active Detection preventing Split-Brain.
No live Catalyst hardware connected.
"""

from __future__ import annotations

import json

SUPPORTED_SVL_FAMILIES = ("C9400", "C9500", "C9600")


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def is_svl_supported_model(model: str) -> bool:
    if not isinstance(model, str) or not model.strip():
        raise ValueError(f"model must be a non-empty str, got {model!r}")
    upper = model.strip().upper()
    return any(upper.startswith(prefix) for prefix in SUPPORTED_SVL_FAMILIES)


def validate_svl_pair(sw1: dict, sw2: dict) -> list[str]:
    for sname, sw in (("sw1", sw1), ("sw2", sw2)):
        if not isinstance(sw, dict):
            raise ValueError(f"{sname} must be a dict")
        for key in ("model", "ios_xe", "license"):
            val = sw.get(key)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"{sname}['{key}'] must be a non-empty str, got {val!r}")
    errs = []
    if not is_svl_supported_model(sw1["model"]) or not is_svl_supported_model(sw2["model"]):
        errs.append(
            f"SVL is only supported on Catalyst 9400/9500/9600 families (got {sw1['model']} & {sw2['model']}; C9200/C9300 use hardware StackWise)"
        )
    if sw1["model"] != sw2["model"]:
        errs.append("SVL requires identical switch models")
    if sw1["ios_xe"] != sw2["ios_xe"]:
        errs.append("SVL requires matching IOS-XE versions")
    if sw1["license"] != "network-advantage" or sw2["license"] != "network-advantage":
        errs.append("SVL requires Network Advantage license on both peers")
    return errs


def simulate_svl_failure(svl_up: bool, dad_up: bool) -> dict:
    svl = _require_bool(svl_up, "svl_up")
    dad = _require_bool(dad_up, "dad_up")
    if svl:
        return {"sw1_role": "ACTIVE", "sw2_role": "STANDBY", "split_brain": False, "mec_active_uplinks": 2}
    if not svl and not dad:
        # Both assume Active with identical virtual MAC/IP -> Split-Brain!
        return {"sw1_role": "ACTIVE", "sw2_role": "ACTIVE", "split_brain": True, "mec_active_uplinks": 2}
    # SVL down, DAD alive -> Former Active enters Recovery (shuts non-DAD ports), Standby takes over cleanly!
    return {"sw1_role": "RECOVERY_MODE", "sw2_role": "ACTIVE", "split_brain": False, "mec_active_uplinks": 1}


def main() -> None:
    good_errs = validate_svl_pair(
        {"model": "C9500-48Y4C", "ios_xe": "17.9.4a", "license": "network-advantage"},
        {"model": "C9500-48Y4C", "ios_xe": "17.9.4a", "license": "network-advantage"},
    )
    bad_mixed_errs = validate_svl_pair(
        {"model": "C9200-48P", "ios_xe": "17.9.4a", "license": "network-essentials"},
        {"model": "C9500-48Y4C", "ios_xe": "17.12.1", "license": "network-advantage"},
    )
    # Negative test: identical C9200 pair with matching IOS-XE and Advantage license STILL cannot run SVL!
    unsupported_same_model_errs = validate_svl_pair(
        {"model": "C9200-48P", "ios_xe": "17.9.4a", "license": "network-advantage"},
        {"model": "C9200-48P", "ios_xe": "17.9.4a", "license": "network-advantage"},
    )
    assert good_errs == []
    assert len(bad_mixed_errs) == 4
    assert len(unsupported_same_model_errs) == 1 and "C9200/C9300" in unsupported_same_model_errs[0]

    normal = simulate_svl_failure(svl_up=True, dad_up=True)
    split_brain = simulate_svl_failure(svl_up=False, dad_up=False)
    dad_protected = simulate_svl_failure(svl_up=False, dad_up=True)
    assert normal["mec_active_uplinks"] == 2
    assert split_brain["split_brain"] is True
    assert dad_protected["split_brain"] is False and dad_protected["sw1_role"] == "RECOVERY_MODE"

    print("=== spec_ent_campus SVL & DAD Local Mock ===")
    print(json.dumps({
        "valid_pair_errors": good_errs,
        "invalid_mixed_pair_errors": bad_mixed_errs,
        "unsupported_identical_c9200_pair_errors": unsupported_same_model_errs,
        "normal_operation": normal,
        "svl_cut_without_dad": split_brain,
        "svl_cut_with_dad_protected": dad_protected,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
