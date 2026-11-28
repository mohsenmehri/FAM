"""Local Python 3 stdlib mock lab for adv_bfd (BFD RFC 5880 Negotiation & Flexible NetFlow v9/IPFIX).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Cisco router, BFD ASIC offload, or NetFlow collector is executed.
"""
from __future__ import annotations


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_pos_int(val: object, name: str) -> int:
    if type(val) is not int or val <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return val


def negotiate_bfd_detection(
    r1_tx_ms: int,
    r1_min_rx_ms: int,
    r1_mult: int,
    r2_tx_ms: int,
    r2_min_rx_ms: int,
    r2_mult: int,
    multihop: bool = False,
) -> dict[str, object]:
    """Compute RFC 5880 BFD negotiated detection times (effective interval = max(local_rx, peer_tx))."""
    for name, val in (
        ("r1_tx_ms", r1_tx_ms),
        ("r1_min_rx_ms", r1_min_rx_ms),
        ("r1_mult", r1_mult),
        ("r2_tx_ms", r2_tx_ms),
        ("r2_min_rx_ms", r2_min_rx_ms),
        ("r2_mult", r2_mult),
    ):
        _require_pos_int(val, name)
    _require_bool(multihop, "multihop")

    # R1 detects R2 failure based on R1's multiplier * max(R1_min_rx, R2_desired_tx)
    r1_effective_rx_ms = max(r1_min_rx_ms, r2_tx_ms)
    r1_detect_ms = r1_mult * r1_effective_rx_ms
    r2_effective_rx_ms = max(r2_min_rx_ms, r1_tx_ms)
    r2_detect_ms = r2_mult * r2_effective_rx_ms

    return {
        "udp_control_port": 4784 if multihop else 3784,
        "udp_echo_port": None if multihop else 3785,
        "r1_detects_r2_down_ms": r1_detect_ms,
        "r2_detects_r1_down_ms": r2_detect_ms,
        "sub_second_both_sides": r1_detect_ms < 1000 and r2_detect_ms < 1000,
    }


def simulate_fnf_active_timeout(
    flow_duration_sec: int,
    active_timeout_sec: int,
    total_mb: int,
) -> dict[str, object]:
    """Demonstrate why Flexible NetFlow 'cache timeout active 60' prevents delayed spike reporting."""
    _require_pos_int(flow_duration_sec, "flow_duration_sec")
    _require_pos_int(active_timeout_sec, "active_timeout_sec")
    _require_pos_int(total_mb, "total_mb")

    export_events = (flow_duration_sec + active_timeout_sec - 1) // active_timeout_sec
    mb_per_export = round(total_mb / export_events, 2)
    return {
        "flow_duration_sec": flow_duration_sec,
        "active_timeout_sec": active_timeout_sec,
        "export_buckets": export_events,
        "avg_mb_per_export": mb_per_export,
        "avoids_single_end_of_flow_spike": export_events > 1,
    }


def validate_fnf_architecture(
    has_flow_record: bool,
    has_flow_exporter: bool,
    has_flow_monitor: bool,
    exporter_uses_loopback: bool,
    protocol: str = "ipfix",
) -> dict[str, object]:
    """Audit the 3 mandatory Flexible NetFlow components and Loopback source best practice."""
    for name, val in (
        ("has_flow_record", has_flow_record),
        ("has_flow_exporter", has_flow_exporter),
        ("has_flow_monitor", has_flow_monitor),
        ("exporter_uses_loopback", exporter_uses_loopback),
    ):
        _require_bool(val, name)
    if protocol not in ("netflow-v9", "ipfix"):
        raise ValueError("protocol must be 'netflow-v9' or 'ipfix'")

    issues = []
    if not has_flow_record:
        issues.append("MISSING_FLOW_RECORD")
    if not has_flow_exporter:
        issues.append("MISSING_FLOW_EXPORTER")
    if not has_flow_monitor:
        issues.append("MISSING_FLOW_MONITOR")
    if not exporter_uses_loopback:
        issues.append("EXPORTER_SOURCE_NOT_LOOPBACK_FLAP_RISK")

    return {
        "fnf_valid": len(issues) == 0,
        "protocol": protocol,
        "standard_udp_port": 4739 if protocol == "ipfix" else 2055,
        "issues": issues,
    }


def main() -> None:
    sym = negotiate_bfd_detection(50, 50, 3, 50, 50, 3)
    asym = negotiate_bfd_detection(50, 50, 3, 200, 200, 3)
    mhop = negotiate_bfd_detection(100, 100, 3, 100, 100, 3, multihop=True)
    assert sym["r1_detects_r2_down_ms"] == 150 and sym["udp_control_port"] == 3784
    assert asym["r1_detects_r2_down_ms"] == 600  # Negotiated slower interval!
    assert mhop["udp_control_port"] == 4784 and mhop["udp_echo_port"] is None

    fnf_60 = simulate_fnf_active_timeout(1500, 60, 1500)
    fnf_default = simulate_fnf_active_timeout(1500, 1800, 1500)
    assert fnf_60["export_buckets"] == 25 and fnf_60["avoids_single_end_of_flow_spike"] is True
    assert fnf_default["export_buckets"] == 1

    audit_ok = validate_fnf_architecture(True, True, True, True, "ipfix")
    assert audit_ok["fnf_valid"] is True and audit_ok["standard_udp_port"] == 4739

    print("BFD Symmetric 50msx3:", sym)
    print("BFD Asymmetric 50ms vs 200ms:", asym)
    print("BFD Multihop:", mhop)
    print("FNF Active Timeout (60s vs 1800s):", fnf_60, fnf_default)
    print("FNF Audit:", audit_ok)


if __name__ == "__main__":
    main()
