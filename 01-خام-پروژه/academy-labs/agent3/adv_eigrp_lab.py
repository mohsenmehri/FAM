"""Local Python Mock for adv_eigrp (EIGRP Classic/Wide Metrics, DUAL Feasibility & Variance).

Educational local model only — no live Cisco IOS/IOS-XE EIGRP router or real RTP/DUAL
state machine is contacted.
Models:
1. Classic EIGRP Metric (default K1=1, K3=1, K2=K4=K5=0) vs Wide Metric (64-bit scaling for >10Gbps).
2. DUAL Feasibility Condition (`RD < FD`), Successor, Feasible Successor selection,
   and Unequal-Cost Load Balancing (`variance`) candidate filtering.
"""
from __future__ import annotations

CLASSIC_BW_REF_KBPS = 10_000_000
WIDE_SCALE = 65_536
WIDE_BW_REF_KBPS = 10_000_000  # 10^7 * 65536 / bw_kbps per RFC 7868 Wide Metric Throughput


def _require_pos_int(val: object, name: str, max_val: int = 10**12) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (1 <= val <= max_val):
        raise ValueError(f"{name} must be an int in 1..{max_val}, got {val!r}")
    return val


def _require_non_neg_int(val: object, name: str, max_val: int = 10**15) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (0 <= val <= max_val):
        raise ValueError(f"{name} must be an int in 0..{max_val}, got {val!r}")
    return val


def compute_classic_metric(min_bandwidth_kbps: int, total_delay_tens_of_us: int) -> int:
    """Compute Classic EIGRP Metric with default K-values (K1=1, K3=1, K2=K4=K5=0)."""
    bw = _require_pos_int(min_bandwidth_kbps, "min_bandwidth_kbps")
    delay = _require_non_neg_int(total_delay_tens_of_us, "total_delay_tens_of_us")
    bw_term = CLASSIC_BW_REF_KBPS // bw
    return (bw_term + delay) * 256


def compute_wide_metric(min_bandwidth_kbps: int, total_delay_picoseconds: int, rib_scale: int = 128) -> dict[str, int]:
    """Compute RFC 7868 EIGRP Wide Metric (default K1=1, K3=1) and RIB-scaled value."""
    bw = _require_pos_int(min_bandwidth_kbps, "min_bandwidth_kbps")
    delay_ps = _require_non_neg_int(total_delay_picoseconds, "total_delay_picoseconds")
    scale = _require_pos_int(rib_scale, "rib_scale", max_val=255)
    # RFC 7868: Throughput = (10^7 * 65536) // bw_kbps; Latency = (delay_ps * 65536) // 1_000_000
    throughput = (WIDE_BW_REF_KBPS * WIDE_SCALE) // bw
    latency = (delay_ps * WIDE_SCALE) // 1_000_000
    composite_64 = throughput + latency
    return {
        "wide_composite_64bit": composite_64,
        "rib_scaled_metric": composite_64 // scale,
    }


def evaluate_dual_and_variance(
    paths: list[dict[str, object]],
    variance: int = 1,
) -> dict[str, object]:
    """Select Successor, Feasible Successors (strict RD < FD), and Variance-eligible paths."""
    var = _require_pos_int(variance, "variance", max_val=128)
    if not isinstance(paths, list) or not paths:
        raise ValueError("paths must be a non-empty list")

    norm: list[dict[str, object]] = []
    for p in paths:
        if not isinstance(p, dict):
            raise ValueError("each path must be a dict")
        nh = p.get("next_hop")
        if not isinstance(nh, str) or not nh.strip():
            raise ValueError("next_hop must be a non-empty str")
        rd = _require_non_neg_int(p["rd"], "rd")
        local_cost = _require_pos_int(p["local_cost"], "local_cost")
        computed_dist = rd + local_cost
        norm.append({"next_hop": nh.strip(), "rd": rd, "local_cost": local_cost, "computed_distance": computed_dist})

    fd = min(p["computed_distance"] for p in norm)
    successors = [p for p in norm if p["computed_distance"] == fd]
    feasible_successors = [p for p in norm if p["computed_distance"] > fd and p["rd"] < fd]
    non_feasible = [p for p in norm if p["computed_distance"] > fd and p["rd"] >= fd]
    variance_limit = fd * var
    uclb_paths = successors + [p for p in feasible_successors if p["computed_distance"] <= variance_limit]

    return {
        "feasible_distance_fd": fd,
        "variance": var,
        "variance_ceiling": variance_limit,
        "successors": successors,
        "feasible_successors": feasible_successors,
        "non_feasible_rejected": non_feasible,
        "uclb_eligible_paths": uclb_paths,
        "model_scope_note": "RFC 7868 DUAL Feasibility Condition (RD < FD) educational model only; no live EIGRP router contacted.",
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco IOS/IOS-XE EIGRP router is contacted.")
    # Classic metric cannot distinguish 10G vs 40G (10_000_000 // bw truncates to 1 vs 0!)
    c_10g = compute_classic_metric(10_000_000, 1)
    c_40g = compute_classic_metric(40_000_000, 1)
    w_10g = compute_wide_metric(10_000_000, 10_000_000)
    w_40g = compute_wide_metric(40_000_000, 10_000_000)
    assert w_40g["wide_composite_64bit"] < w_10g["wide_composite_64bit"]
    print("Classic 10G vs 40G:", {"10G": c_10g, "40G": c_40g})
    print("Wide 10G vs 40G:", {"10G": w_10g, "40G": w_40g})

    dual = evaluate_dual_and_variance(
        [
            {"next_hop": "10.0.12.2", "rd": 1000, "local_cost": 500},   # CD=1500 (Successor, FD=1500)
            {"next_hop": "10.0.13.3", "rd": 1400, "local_cost": 1200},  # CD=2600, RD=1400 < 1500 (FS!)
            {"next_hop": "10.0.14.4", "rd": 1500, "local_cost": 300},   # CD=1800, RD=1500 == FD (NOT FS!)
        ],
        variance=2,
    )
    assert len(dual["successors"]) == 1
    assert [p["next_hop"] for p in dual["feasible_successors"]] == ["10.0.13.3"]
    assert [p["next_hop"] for p in dual["non_feasible_rejected"]] == ["10.0.14.4"]
    assert len(dual["uclb_eligible_paths"]) == 2
    print("DUAL & Variance=2 evaluation:", dual)


if __name__ == "__main__":
    main()
