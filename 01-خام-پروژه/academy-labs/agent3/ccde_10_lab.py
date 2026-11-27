#!/usr/bin/env python3
"""
Local Mock Lab — ccde_10 (CCDE High Availability: Series vs Parallel Availability Math & N+1 vs 2N)
Calculates exact end-to-end availability for series vs parallel component chains,
converts availability into annual downtime minutes, and evaluates N vs N+1 vs 2N & Multi-Box vs In-Box HA.
No real chassis routers, power feeds, or live clusters are connected.
"""

import json
import math


def _require_prob(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a finite probability in [0.0, 1.0] (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval) or not (0.0 <= fval <= 1.0):
        raise ValueError(f"{name} must be in [0.0, 1.0], got {val!r}")
    return fval


def series_availability(components: list[float]) -> float:
    if not isinstance(components, (list, tuple)) or not components:
        raise ValueError("components must be a non-empty list/tuple of probabilities in [0.0, 1.0]")
    a = 1.0
    for i, c in enumerate(components):
        a *= _require_prob(c, f"components[{i}]")
    return a


def parallel_availability(components: list[float]) -> float:
    if not isinstance(components, (list, tuple)) or not components:
        raise ValueError("components must be a non-empty list/tuple of probabilities in [0.0, 1.0]")
    unavail = 1.0
    for i, c in enumerate(components):
        unavail *= (1.0 - _require_prob(c, f"components[{i}]"))
    return 1.0 - unavail


def summarize_availability(label: str, avail: float) -> dict:
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"label must be a non-empty str, got {label!r}")
    p = _require_prob(avail, "avail")
    downtime_min_yr = round(365.25 * 24 * 60 * (1.0 - p), 2)
    return {"topology": label, "availability_pct": round(p * 100.0, 5), "expected_downtime_min_per_year": downtime_min_yr}


def main() -> None:
    # Single path: Switch (99.9%) -> Firewall (99.9%) -> WAN Router (99.9%)
    single_chain = series_availability([0.999, 0.999, 0.999])
    # Dual independent parallel paths (2N multi-box): each path is a 3-device chain
    dual_parallel_2n = parallel_availability([single_chain, single_chain])
    # Dual per-layer mesh (parallel at every tier, then series across tiers)
    mesh_per_tier = series_availability([
        parallel_availability([0.999, 0.999]),
        parallel_availability([0.999, 0.999]),
        parallel_availability([0.999, 0.999]),
    ])
    report = {
        "mode": "LOCAL_MOCK_CCDE_HA_MATH_MODELER",
        "availability_models": [
            summarize_availability("Single_Path_Series_3x99.9%", single_chain),
            summarize_availability("Dual_Independent_Chains_2N", dual_parallel_2n),
            summarize_availability("Redundant_Per_Tier_Full_Mesh", mesh_per_tier),
        ],
        "redundancy_patterns": {
            "N": "Zero spare — any single fault causes outage",
            "N+1": "One shared spare (e.g., 3 routers carrying load of 2) — survives 1 fault cost-effectively",
            "2N": "Full active mirror — survives full half-loss or simultaneous maintenance + fault",
        },
        "in_box_vs_multi_box": "In-Box SSO/NSF/ISSU cannot survive chassis/power/OS-wide bug -> Multi-Box HA is mandatory for >=99.99%",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
