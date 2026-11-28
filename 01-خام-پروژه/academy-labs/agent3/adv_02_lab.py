"""Local Python 3 stdlib mock lab for adv_02 (Multi-Area OSPF, LSA Types 1-7, Stub/NSSA & E1/E2).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Cisco router or live OSPF LSDB is executed.
"""
from __future__ import annotations

import math


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_nonneg_int(val: object, name: str) -> int:
    if type(val) is not int or val < 0:
        raise ValueError(f"{name} must be an integer >= 0")
    return val


def evaluate_ospf_area_policy(
    area_id: int,
    area_type: str,
    nssa_default_info_originate: bool = False,
) -> dict[str, object]:
    """Return exact LSA filtering and automatic default-route injection behavior for OSPF area types."""
    if type(area_id) is not int or area_id < 0:
        raise ValueError("area_id must be a non-negative integer")
    _require_bool(nssa_default_info_originate, "nssa_default_info_originate")
    if area_type not in ("backbone", "standard", "stub", "totally_stubby", "nssa", "totally_nssa"):
        raise ValueError(f"Unsupported area_type: {area_type}")
    if area_id == 0 and area_type != "backbone":
        raise ValueError("Area 0 (Backbone) cannot be configured as Stub or NSSA")
    if area_id != 0 and area_type == "backbone":
        raise ValueError("Only Area 0 can have area_type='backbone'")

    rules = {
        "backbone": {"allowed_lsas": [1, 2, 3, 4, 5], "blocked_lsas": [], "local_asbr_allowed": True, "auto_default_route": False},
        "standard": {"allowed_lsas": [1, 2, 3, 4, 5], "blocked_lsas": [], "local_asbr_allowed": True, "auto_default_route": False},
        "stub": {"allowed_lsas": [1, 2, 3], "blocked_lsas": [4, 5], "local_asbr_allowed": False, "auto_default_route": True},
        "totally_stubby": {"allowed_lsas": [1, 2], "blocked_lsas": [3, 4, 5], "local_asbr_allowed": False, "auto_default_route": True},
        "nssa": {"allowed_lsas": [1, 2, 3, 7], "blocked_lsas": [4, 5], "local_asbr_allowed": True, "auto_default_route": nssa_default_info_originate},
        "totally_nssa": {"allowed_lsas": [1, 2, 7], "blocked_lsas": [3, 4, 5], "local_asbr_allowed": True, "auto_default_route": True},
    }
    return {"area_id": area_id, "area_type": area_type, **rules[area_type]}


def select_ospf_path(candidates: list[dict[str, object]]) -> dict[str, object]:
    """Select best OSPF path following strict RFC 2328 preference: O > O IA > E1/N1 > E2/N2."""
    if not candidates:
        raise ValueError("candidates must be non-empty")
    rank = {"O": 1, "O IA": 2, "O E1": 3, "O N1": 3, "O E2": 4, "O N2": 4}

    def sort_key(item: dict[str, object]) -> tuple[int, int, int]:
        code = str(item["code"])
        if code not in rank:
            raise ValueError(f"Unsupported OSPF route code: {code}")
        internal = _require_nonneg_int(item["internal_cost"], "internal_cost")
        external = _require_nonneg_int(item.get("external_seed", 0), "external_seed")
        if code in ("O", "O IA"):
            return (rank[code], internal, 0)
        if code in ("O E1", "O N1"):
            return (rank[code], internal + external, 0)
        # O E2 / O N2 compare seed metric first, then internal forward cost to ASBR
        return (rank[code], external, internal)

    best = min(candidates, key=sort_key)
    eff_metric = (
        int(best["internal_cost"]) + int(best.get("external_seed", 0))
        if best["code"] in ("O E1", "O N1")
        else (int(best.get("external_seed", 0)) if best["code"] in ("O E2", "O N2") else int(best["internal_cost"]))
    )
    return {"winner": best["name"], "code": best["code"], "effective_metric": eff_metric}


def summarization_location(summary_scope: str) -> dict[str, str]:
    """Identify the exact router role and IOS command for OSPF summarization."""
    if summary_scope == "inter_area_type3":
        return {"role": "ABR", "command": "area <area-id> range <network> <mask>", "loop_guard": "Auto Null0 route on ABR"}
    if summary_scope == "external_type5_or_7":
        return {"role": "ASBR (or translating ABR for Type 7->5)", "command": "summary-address <network> <mask>", "loop_guard": "Auto Null0 route on ASBR"}
    raise ValueError("summary_scope must be 'inter_area_type3' or 'external_type5_or_7'")


def main() -> None:
    tot_nssa = evaluate_ospf_area_policy(10, "totally_nssa")
    std_nssa = evaluate_ospf_area_policy(10, "nssa", nssa_default_info_originate=False)
    assert tot_nssa["local_asbr_allowed"] is True and tot_nssa["auto_default_route"] is True and 3 in tot_nssa["blocked_lsas"]
    assert std_nssa["auto_default_route"] is False

    # Intra-area (O) ALWAYS beats Inter-area (O IA) even with higher cost!
    intra_vs_inter = select_ospf_path([
        {"name": "Via_Backbone", "code": "O IA", "internal_cost": 10},
        {"name": "Direct_IntraArea", "code": "O", "internal_cost": 500},
    ])
    assert intra_vs_inter["winner"] == "Direct_IntraArea"

    # E1 always beats E2 regardless of metric!
    e1_vs_e2 = select_ospf_path([
        {"name": "Path_E2", "code": "O E2", "internal_cost": 1, "external_seed": 20},
        {"name": "Path_E1", "code": "O E1", "internal_cost": 50, "external_seed": 20},
    ])
    assert e1_vs_e2["winner"] == "Path_E1" and e1_vs_e2["effective_metric"] == 70

    print("Totally NSSA vs Standard NSSA:", tot_nssa, std_nssa)
    print("Intra vs Inter-Area (O beats O IA):", intra_vs_inter)
    print("E1 vs E2 (E1 beats E2):", e1_vs_e2)
    print("Inter-Area Summarization:", summarization_location("inter_area_type3"))
    assert math.isfinite(float(e1_vs_e2["effective_metric"]))


if __name__ == "__main__":
    main()
