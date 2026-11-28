"""Local Python 3 stdlib mock lab for adv_01 (MST 802.1s, STP Guards, BPDU Filter Trap, UDLD & SVL).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Cisco Catalyst switch, live STP domain, or fiber link is executed.
"""
from __future__ import annotations


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_non_empty_str(val: object, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return val.strip()


def evaluate_mst_region_match(
    sw1: dict[str, object],
    sw2: dict[str, object],
) -> dict[str, object]:
    """Check whether two switches belong to the same IEEE 802.1s MST Region."""
    mismatches = []
    for key in ("region_name", "revision", "vlan_to_instance"):
        if key not in sw1 or key not in sw2:
            raise ValueError(f"Missing required MST parameter: {key}")
    _require_non_empty_str(sw1["region_name"], "sw1.region_name")
    _require_non_empty_str(sw2["region_name"], "sw2.region_name")
    for side, rev in (("sw1", sw1["revision"]), ("sw2", sw2["revision"])):
        if type(rev) is not int or not (0 <= rev <= 65535):
            raise ValueError(f"{side}.revision must be an int in 0..65535")
    if sw1["region_name"] != sw2["region_name"]:
        mismatches.append("REGION_NAME_MISMATCH")
    if sw1["revision"] != sw2["revision"]:
        mismatches.append("REVISION_NUMBER_MISMATCH")
    if sw1["vlan_to_instance"] != sw2["vlan_to_instance"]:
        mismatches.append("VLAN_TO_INSTANCE_MAP_MISMATCH")
    return {
        "same_mst_region": len(mismatches) == 0,
        "mismatches": mismatches,
        "fallback_behavior": "Separate regions interoperate only via CIST (Instance 0)" if mismatches else "Full multi-instance MST region",
    }


def evaluate_stp_port_protection(
    port_role: str,
    event: str,
    bpdu_guard: bool = False,
    root_guard: bool = False,
    loop_guard: bool = False,
    interface_bpdu_filter: bool = False,
) -> dict[str, object]:
    """Simulate STP Guard and interface-level BPDU Filter outcomes."""
    for name, val in (
        ("bpdu_guard", bpdu_guard),
        ("root_guard", root_guard),
        ("loop_guard", loop_guard),
        ("interface_bpdu_filter", interface_bpdu_filter),
    ):
        _require_bool(val, name)
    if root_guard and loop_guard:
        raise ValueError("root_guard and loop_guard are mutually exclusive on the same port")
    if port_role not in ("access_portfast", "distribution_downlink", "non_designated_uplink"):
        raise ValueError(f"Unsupported port_role: {port_role}")
    if event not in ("bpdu_received", "superior_bpdu_received", "bpdus_stopped_rx_dead"):
        raise ValueError(f"Unsupported event: {event}")

    if interface_bpdu_filter and event in ("bpdu_received", "superior_bpdu_received"):
        return {
            "port_state": "forwarding_unsafe",
            "l2_loop_risk": True,
            "reason": "INTERFACE_BPDU_FILTER_DROPS_BPDUS_AND_DISABLES_STP",
        }
    if event == "bpdu_received" and bpdu_guard:
        return {"port_state": "err-disabled", "l2_loop_risk": False, "reason": "BPDU_GUARD_SHUTDOWN"}
    if event == "superior_bpdu_received" and root_guard:
        return {"port_state": "root-inconsistent", "l2_loop_risk": False, "reason": "ROOT_GUARD_BLOCKED_SUPERIOR_BPDU"}
    if event == "bpdus_stopped_rx_dead" and loop_guard:
        return {"port_state": "loop-inconsistent", "l2_loop_risk": False, "reason": "LOOP_GUARD_PREVENTED_UNIDIRECTIONAL_LOOP"}
    return {"port_state": "forwarding_or_reconverged", "l2_loop_risk": event == "bpdus_stopped_rx_dead", "reason": "NO_MATCHING_GUARD_ACTIVE"}


def evaluate_udld_fiber_fault(mode: str, rx_fiber_cut: bool, missed_echoes: int) -> dict[str, object]:
    """Simulate Cisco UDLD Normal vs Aggressive behavior on an RX-cut unidirectional fiber."""
    if mode not in ("disabled", "normal", "aggressive"):
        raise ValueError("mode must be 'disabled', 'normal', or 'aggressive'")
    _require_bool(rx_fiber_cut, "rx_fiber_cut")
    if type(missed_echoes) is not int or missed_echoes < 0:
        raise ValueError("missed_echoes must be a non-negative integer")
    if not rx_fiber_cut:
        return {"mode": mode, "port_state": "up", "action": "HEALTHY_BIDIRECTIONAL_LINK"}
    if mode == "aggressive" and missed_echoes >= 8:
        return {"mode": mode, "port_state": "err-disabled", "action": "UDLD_AGGRESSIVE_LOCKED_PORT_AFTER_8_PROBES"}
    if mode == "normal":
        return {"mode": mode, "port_state": "undetermined_up_risk", "action": "UDLD_NORMAL_LOGS_ONLY_ON_UNKNOWN_LINK_LOSS"}
    return {"mode": mode, "port_state": "up_l2_loop_risk", "action": "UNIDIRECTIONAL_FAULT_UNDETECTED"}


def main() -> None:
    sw1 = {"region_name": "CORP_MST", "revision": 2, "vlan_to_instance": {1: [10, 20], 2: [30, 40]}}
    sw2_ok = {"region_name": "CORP_MST", "revision": 2, "vlan_to_instance": {1: [10, 20], 2: [30, 40]}}
    sw2_bad = {"region_name": "CORP_MST", "revision": 3, "vlan_to_instance": {1: [10, 20], 2: [30, 40]}}
    assert evaluate_mst_region_match(sw1, sw2_ok)["same_mst_region"] is True
    assert evaluate_mst_region_match(sw1, sw2_bad)["same_mst_region"] is False

    filt_trap = evaluate_stp_port_protection("access_portfast", "bpdu_received", interface_bpdu_filter=True)
    guard_ok = evaluate_stp_port_protection("access_portfast", "bpdu_received", bpdu_guard=True)
    root_ok = evaluate_stp_port_protection("distribution_downlink", "superior_bpdu_received", root_guard=True)
    loop_ok = evaluate_stp_port_protection("non_designated_uplink", "bpdus_stopped_rx_dead", loop_guard=True)
    assert filt_trap["l2_loop_risk"] is True
    assert guard_ok["port_state"] == "err-disabled"
    assert root_ok["port_state"] == "root-inconsistent"
    assert loop_ok["port_state"] == "loop-inconsistent"

    udld_agg = evaluate_udld_fiber_fault("aggressive", True, 8)
    assert udld_agg["port_state"] == "err-disabled"

    print("MST Match vs Mismatch:", evaluate_mst_region_match(sw1, sw2_ok), evaluate_mst_region_match(sw1, sw2_bad))
    print("Interface BPDU Filter Trap:", filt_trap)
    print("Guards (BPDU/Root/Loop):", guard_ok, root_ok, loop_ok)
    print("UDLD Aggressive:", udld_agg)


if __name__ == "__main__":
    main()
