#!/usr/bin/env python3
"""
Local Mock Lab — ccde_01 (CCDE Network Architecture Fundamentals: SLA Math, Blast Radius & Trade-Off Matrix)
Translates executive business SLAs into annual downtime budgets, calculates Failure Domain blast radius,
and runs a validated weighted CCDE Trade-Off Analysis across competing design options.
No real enterprise infrastructure or live network hardware is connected.
"""

import json


def sla_downtime_budget(sla_percent: float) -> dict:
    if not (0.0 < sla_percent <= 100.0):
        raise ValueError(f"SLA percent must be in (0, 100], got {sla_percent}")
    minutes_per_year = 365.25 * 24 * 60
    allowed_down_min = round(minutes_per_year * (1.0 - sla_percent / 100.0), 2)
    return {
        "sla_percent": sla_percent,
        "max_downtime_minutes_per_year": allowed_down_min,
        "implication": (
            "Requires <1s failover + 2N/Dual-Homing + minimal-downtime/ISSU-capable upgrade procedures"
            if allowed_down_min < 60
            else "N+1 with standard convergence and planned maintenance windows acceptable"
        ),
    }


def blast_radius(total_users: int, failure_domains: int) -> dict:
    if total_users <= 0 or failure_domains <= 0:
        raise ValueError("total_users and failure_domains must be positive integers")
    affected = round(total_users / failure_domains)
    pct = round((affected / total_users) * 100.0, 2)
    return {
        "total_users": total_users,
        "failure_domains": failure_domains,
        "max_users_impacted_per_fault": affected,
        "blast_radius_pct": pct,
    }


def weighted_tradeoff(weights: dict[str, float], options: dict[str, dict[str, int]]) -> list[dict]:
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError(f"Trade-off weights must sum to 1.0 (got {weight_sum})")
    scored = []
    for name, scores in options.items():
        total = round(sum(scores[k] * w for k, w in weights.items()), 2)
        scored.append({"option": name, "weighted_score": total, "breakdown": scores})
    return sorted(scored, key=lambda x: -x["weighted_score"])


def main() -> None:
    weights = {"resiliency": 0.35, "simplicity": 0.25, "scalability": 0.20, "cost_efficiency": 0.20}
    options = {
        "Flat_L2_SpanningTree": {"resiliency": 3, "simplicity": 7, "scalability": 2, "cost_efficiency": 9},
        "Modular_L3_Routed_Access": {"resiliency": 9, "simplicity": 8, "scalability": 9, "cost_efficiency": 7},
        "Full_SD_Access_Overlay": {"resiliency": 9, "simplicity": 5, "scalability": 10, "cost_efficiency": 5},
    }
    slas = [sla_downtime_budget(99.9), sla_downtime_budget(99.99), sla_downtime_budget(99.999)]
    flat = blast_radius(4000, 1)
    modular = blast_radius(4000, 8)
    ranked = weighted_tradeoff(weights, options)

    assert slas[1]["max_downtime_minutes_per_year"] == 52.6
    assert slas[2]["max_downtime_minutes_per_year"] == 5.26
    assert flat["blast_radius_pct"] == 100.0 and modular["blast_radius_pct"] == 12.5
    assert ranked[0]["option"] == "Modular_L3_Routed_Access"

    report = {
        "mode": "LOCAL_MOCK_CCDE_DESIGN_MODELER",
        "sla_translations": slas,
        "failure_domain_comparison": {
            "single_flat_domain": flat,
            "eight_modular_blocks": modular,
        },
        "weighted_tradeoff_ranking": ranked,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
