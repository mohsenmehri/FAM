"""Local Python Mock for adv_bgp (BGP Path Selection, iBGP Split Horizon & Route Reflector Rules).

Educational local model only — no live BGP TCP/179 router or production Internet DFZ
is contacted.
Models:
1. Cisco-style BGP Best-Path Selection subset:
   Next-hop reachable -> Highest Weight (Cisco-local) -> Highest LOCAL_PREF ->
   Shortest AS_PATH -> Lowest Origin (IGP < EGP < Incomplete) -> Lowest MED (same neighbor AS) ->
   eBGP over iBGP -> Lowest Router-ID.
2. RFC 4456 Route Reflector reflection matrix (Client vs Non-Client vs eBGP).
"""
from __future__ import annotations

import ipaddress

ORIGIN_RANK = {"igp": 0, "egp": 1, "incomplete": 2}
PEER_TYPES = frozenset({"ebgp", "rr_client", "rr_non_client"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r}")
    return val


def _require_non_neg_int(val: object, name: str, max_val: int = 2**32 - 1) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (0 <= val <= max_val):
        raise ValueError(f"{name} must be an int in 0..{max_val}, got {val!r}")
    return val


def select_best_bgp_path(candidates: list[dict[str, object]]) -> dict[str, object]:
    """Select best BGP path using Cisco-style tie-breakers (ignoring unreachable next-hops)."""
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidates must be a non-empty list")

    eligible: list[dict[str, object]] = []
    skipped: list[str] = []
    for c in candidates:
        if not isinstance(c, dict):
            raise ValueError("each candidate must be a dict")
        reachable = _require_bool(c.get("next_hop_reachable", True), "next_hop_reachable")
        rid = str(ipaddress.IPv4Address(str(c["router_id"])))
        if not reachable:
            skipped.append(rid)
            continue
        weight = _require_non_neg_int(c.get("weight", 0), "weight", 65535)
        lp = _require_non_neg_int(c.get("local_pref", 100), "local_pref")
        as_path = c.get("as_path", [])
        if not isinstance(as_path, list) or not all(not isinstance(a, bool) and isinstance(a, int) and 1 <= a <= 2**32 - 1 for a in as_path):
            raise ValueError("as_path must be a list of valid ASN ints")
        origin = str(c.get("origin", "igp")).lower()
        if origin not in ORIGIN_RANK:
            raise ValueError(f"origin must be in {sorted(ORIGIN_RANK)}")
        med = _require_non_neg_int(c.get("med", 0), "med")
        is_ebgp = _require_bool(c.get("is_ebgp", True), "is_ebgp")
        eligible.append({
            "router_id": rid,
            "weight": weight,
            "local_pref": lp,
            "as_path": as_path,
            "origin": origin,
            "med": med,
            "is_ebgp": is_ebgp,
        })

    if not eligible:
        return {"best_path": None, "skipped_unreachable_rids": skipped, "reason": "NO_REACHABLE_NEXT_HOP"}

    # Note: MED is only comparable across paths from the same neighbor AS unless always-compare-med is enabled.
    first_ases = {p["as_path"][0] if p["as_path"] else 0 for p in eligible}
    compare_med = len(first_ases) == 1

    def sort_key(p: dict[str, object]) -> tuple:
        return (
            -int(p["weight"]),
            -int(p["local_pref"]),
            len(p["as_path"]),
            ORIGIN_RANK[str(p["origin"])],
            int(p["med"]) if compare_med else 0,
            0 if p["is_ebgp"] else 1,
            int(ipaddress.IPv4Address(str(p["router_id"]))),
        )

    ranked = sorted(eligible, key=sort_key)
    return {
        "best_path": ranked[0],
        "med_compared_same_neighbor_as": compare_med,
        "skipped_unreachable_rids": skipped,
        "model_scope_note": "Educational BGP path-selection subset only (ignores IGP-cost-to-NH/multipath/cluster-list); no live BGP speaker contacted.",
    }


def evaluate_rr_reflection(learned_from: str, target_peer: str) -> dict[str, object]:
    """Evaluate RFC 4456 Route Reflector advertisement rules."""
    if learned_from not in PEER_TYPES or target_peer not in PEER_TYPES:
        raise ValueError(f"peer types must be in {sorted(PEER_TYPES)}")
    # RFC 4456: non-client -> non-client is NOT reflected!
    allowed = not (learned_from == "rr_non_client" and target_peer == "rr_non_client")
    return {
        "learned_from": learned_from,
        "target_peer": target_peer,
        "reflect_route": allowed,
        "reason": "BLOCKED_NON_CLIENT_TO_NON_CLIENT_SPLIT_HORIZON" if not allowed else "PERMITTED_BY_RFC4456",
    }


def main() -> None:
    print("Local Python Mock only — no live BGP TCP/179 session is contacted.")
    res = select_best_bgp_path([
        {"router_id": "1.1.1.1", "weight": 0, "local_pref": 200, "as_path": [65001, 65002], "origin": "igp", "med": 50, "is_ebgp": True, "next_hop_reachable": False},
        {"router_id": "2.2.2.2", "weight": 0, "local_pref": 150, "as_path": [65001, 65002, 65003], "origin": "igp", "med": 100, "is_ebgp": False, "next_hop_reachable": True},
        {"router_id": "3.3.3.3", "weight": 0, "local_pref": 100, "as_path": [65009], "origin": "igp", "med": 10, "is_ebgp": True, "next_hop_reachable": True},
    ])
    assert res["best_path"]["router_id"] == "2.2.2.2"  # 1.1.1.1 unreachable, 2.2.2.2 wins on LOCAL_PREF 150 > 100
    assert evaluate_rr_reflection("rr_non_client", "rr_non_client")["reflect_route"] is False
    assert evaluate_rr_reflection("rr_client", "rr_non_client")["reflect_route"] is True
    print("BGP best path:", res)
    print("RR non-client->non-client:", evaluate_rr_reflection("rr_non_client", "rr_non_client"))


if __name__ == "__main__":
    main()
