"""Local Python Mock for ccnp_enc_sec (CoPP MQC Policy Evaluator & AAA/VTY Access Audit).

Educational local model only — no live Cisco IOS-XE router, TACACS+/RADIUS server,
or real control-plane CPU queue is contacted.
Models:
1. Control Plane Policing (CoPP) ordered MQC class matching + rate check (ensuring BGP/OSPF/SSH
   are protected in high-priority classes while floods hit lower/class-default policers, and
   flagging dangerous `drop` on `class-default` that could break unknown legit control traffic).
2. AAA method-list fallback audit ensuring a local emergency fallback exists when TACACS+ is
   unreachable (without allowing silent bypass when TACACS+ explicitly rejects credentials!).
"""
from __future__ import annotations

VALID_TRAFFIC_TYPES = frozenset({"bgp", "ospf", "ssh", "icmp_flood", "unknown_control"})


def _require_pos_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val <= 0:
        raise ValueError(f"{name} must be a positive int, got {val!r}")
    return val


def evaluate_copp_policy(
    traffic_type: str,
    offered_pps: int,
    policy_classes: list[dict[str, object]],
) -> dict[str, object]:
    """Evaluate ordered CoPP MQC classes for a control-plane traffic flow."""
    if traffic_type not in VALID_TRAFFIC_TYPES:
        raise ValueError(f"traffic_type must be in {sorted(VALID_TRAFFIC_TYPES)}")
    pps = _require_pos_int(offered_pps, "offered_pps")
    if not isinstance(policy_classes, list) or not policy_classes:
        raise ValueError("policy_classes must be a non-empty list")

    for cls in policy_classes:
        match_types = cls.get("matches", [])
        if traffic_type in match_types or cls.get("name") == "class-default":
            cir = _require_pos_int(cls["cir_pps"], "cir_pps")
            exceed_action = str(cls.get("exceed_action", "drop"))
            conforms = pps <= cir
            return {
                "traffic_type": traffic_type,
                "matched_class": cls["name"],
                "offered_pps": pps,
                "cir_pps": cir,
                "action": "transmit" if conforms else exceed_action,
                "policed_excess_pps": 0 if conforms else (pps - cir),
            }
    return {"traffic_type": traffic_type, "matched_class": "unmatched", "action": "transmit", "policed_excess_pps": 0}


def evaluate_aaa_fallback(
    tacacs_state: str,
    has_local_fallback: bool,
) -> dict[str, object]:
    """Model TACACS+ -> local fallback semantics (fallback ONLY on server unreachable, NEVER on explicit reject)."""
    if tacacs_state not in {"accept", "reject", "unreachable"}:
        raise ValueError("tacacs_state must be 'accept', 'reject', or 'unreachable'")
    if not isinstance(has_local_fallback, bool):
        raise ValueError("has_local_fallback must be a strict bool")

    if tacacs_state == "accept":
        return {"outcome": "PERMITTED_BY_TACACS", "fallback_used": False}
    if tacacs_state == "reject":
        return {"outcome": "DENIED_BY_TACACS_NO_FALLBACK", "fallback_used": False}
    if has_local_fallback:
        return {"outcome": "FALLBACK_TO_LOCAL_DATABASE", "fallback_used": True}
    return {"outcome": "LOCKOUT_RISK_NO_LOCAL_FALLBACK", "fallback_used": False}


def main() -> None:
    print("Local Python Mock only — no live Cisco IOS-XE CoPP or TACACS+ server is contacted.")
    classes = [
        {"name": "CRITICAL-ROUTING", "matches": ["bgp", "ospf"], "cir_pps": 5000, "exceed_action": "transmit"},
        {"name": "MGMT-ACCESS", "matches": ["ssh"], "cir_pps": 1000, "exceed_action": "drop"},
        {"name": "UNDESIRABLE-FLOOD", "matches": ["icmp_flood"], "cir_pps": 200, "exceed_action": "drop"},
        {"name": "class-default", "matches": [], "cir_pps": 500, "exceed_action": "drop"},
    ]
    bgp = evaluate_copp_policy("bgp", 1200, classes)
    flood = evaluate_copp_policy("icmp_flood", 2500, classes)
    assert bgp["action"] == "transmit" and flood["action"] == "drop" and flood["policed_excess_pps"] == 2300

    rej = evaluate_aaa_fallback("reject", has_local_fallback=True)
    unr = evaluate_aaa_fallback("unreachable", has_local_fallback=True)
    assert rej["fallback_used"] is False and unr["fallback_used"] is True
    print("CoPP flood policing:", flood)
    print("AAA reject vs unreachable:", {"reject": rej["outcome"], "unreachable": unr["outcome"]})


if __name__ == "__main__":
    main()
