#!/usr/bin/env python3
"""
Local Mock Lab — ccde_11 (CCDE Capacity Planning: 5-Year Compound Growth, Failover Headroom & 5 Hidden Dimensions)
Computes 5-year compound traffic growth C_5 = C_0 * (1 + r)^5 with 50% N/2N failover headroom,
and audits the 5 hidden CCDE capacity dimensions (Gbps, PPS small-packet rate, TCAM/FIB, NGFW TLS CPS, Power kW).
No real production telemetry or hardware chassis is connected.
"""

import json


def forecast_5yr_capacity(current_gbps: float, annual_growth_rate: float, failover_utilization_cap: float = 0.50) -> dict:
    year5_peak = round(current_gbps * ((1.0 + annual_growth_rate) ** 5), 2)
    required_link_capacity = round(year5_peak / failover_utilization_cap, 2)
    return {
        "year0_peak_gbps": current_gbps,
        "annual_growth_pct": round(annual_growth_rate * 100, 1),
        "year5_peak_gbps": year5_peak,
        "required_capacity_with_50pct_failover_cap_gbps": required_link_capacity,
    }


def audit_five_dimensions(demand: dict, hardware_spec: dict) -> dict:
    bottlenecks = []
    for dim, req in demand.items():
        cap = hardware_spec[dim]
        util_pct = round((req / cap) * 100.0, 1)
        if util_pct > 70.0:
            bottlenecks.append({"dimension": dim, "demand": req, "capacity": cap, "utilization_pct": util_pct})
    return {"passed_all_5_dimensions": len(bottlenecks) == 0, "bottlenecks": bottlenecks}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPACITY_PLANNER",
        "five_year_wan_core_forecast": forecast_5yr_capacity(current_gbps=12.0, annual_growth_rate=0.35),
        "five_dimension_ngfw_audit": audit_five_dimensions(
            demand={"throughput_gbps": 8.0, "small_packet_mpps": 4.5, "fib_routes_k": 850, "tls_inspection_gbps": 6.5, "rack_power_kw": 14.0},
            hardware_spec={"throughput_gbps": 40.0, "small_packet_mpps": 5.0, "fib_routes_k": 1000, "tls_inspection_gbps": 7.0, "rack_power_kw": 20.0},
        ),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
