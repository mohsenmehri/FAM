#!/usr/bin/env python3
"""
Local Mock Lab — ccde_11 (CCDE Capacity Planning: 5-Year Compound Growth, Failover Headroom & 5 Hidden Dimensions)
Computes 5-year compound traffic growth C_5 = C_0 * (1 + r)^5 with configurable N/2N failover headroom
(default 50% cap), and audits 5 hidden CCDE capacity dimensions (Gbps, PPS small-packet rate,
TCAM/FIB, NGFW TLS inspection, Power kW).
Strict validation rejects zero/negative capacities, invalid utilization caps, bools, and NaN/Inf.
No real production telemetry or hardware chassis is connected.
"""

import json
import math


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    return fval


def forecast_5yr_capacity(
    current_gbps: float,
    annual_growth_rate: float,
    failover_utilization_cap: float = 0.50,
) -> dict:
    cur = _require_finite_num(current_gbps, "current_gbps")
    rate = _require_finite_num(annual_growth_rate, "annual_growth_rate")
    cap = _require_finite_num(failover_utilization_cap, "failover_utilization_cap")
    if cur <= 0:
        raise ValueError(f"current_gbps must be positive, got {cur}")
    if rate < -1.0:
        raise ValueError(f"annual_growth_rate cannot be < -1.0, got {rate}")
    if not (0.0 < cap <= 1.0):
        raise ValueError(f"failover_utilization_cap must be in (0.0, 1.0], got {cap}")

    year5_peak = round(cur * ((1.0 + rate) ** 5), 2)
    required_link_capacity = round(year5_peak / cap, 2)
    return {
        "year0_peak_gbps": cur,
        "annual_growth_pct": round(rate * 100, 1),
        "failover_utilization_cap_pct": round(cap * 100, 1),
        "year5_peak_gbps": year5_peak,
        "required_capacity_with_failover_cap_gbps": required_link_capacity,
    }


def audit_five_dimensions(demand: dict, hardware_spec: dict) -> dict:
    if not isinstance(demand, dict) or not isinstance(hardware_spec, dict) or not demand:
        raise ValueError("demand and hardware_spec must be non-empty dicts")
    bottlenecks = []
    for dim, raw_req in demand.items():
        if dim not in hardware_spec:
            raise ValueError(f"Missing hardware_spec capacity for dimension '{dim}'")
        req = _require_finite_num(raw_req, f"demand.{dim}")
        cap = _require_finite_num(hardware_spec[dim], f"hardware_spec.{dim}")
        if req < 0 or cap <= 0:
            raise ValueError(f"Invalid capacity/demand for '{dim}': demand={req}, capacity={cap}")
        util_pct = round((req / cap) * 100.0, 1)
        if util_pct > 70.0:
            bottlenecks.append({"dimension": dim, "demand": req, "capacity": cap, "utilization_pct": util_pct})
    return {"passed_all_5_dimensions": len(bottlenecks) == 0, "bottlenecks": bottlenecks}


def main() -> None:
    forecast = forecast_5yr_capacity(current_gbps=12.0, annual_growth_rate=0.35)
    audit = audit_five_dimensions(
        demand={"throughput_gbps": 8.0, "small_packet_mpps": 4.5, "fib_routes_k": 850, "tls_inspection_gbps": 6.5, "rack_power_kw": 14.0},
        hardware_spec={"throughput_gbps": 40.0, "small_packet_mpps": 5.0, "fib_routes_k": 1000, "tls_inspection_gbps": 7.0, "rack_power_kw": 20.0},
    )
    assert forecast["year5_peak_gbps"] == 53.81
    assert forecast["required_capacity_with_failover_cap_gbps"] == 107.62
    assert audit["passed_all_5_dimensions"] is False and len(audit["bottlenecks"]) == 3

    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPACITY_PLANNER",
        "five_year_wan_core_forecast": forecast,
        "five_dimension_ngfw_audit": audit,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
