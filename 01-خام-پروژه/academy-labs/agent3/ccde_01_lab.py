#!/usr/bin/env python3
"""
Local Mock Lab — ccde_01 (CCDE Network Architecture Fundamentals: SLA Math, Blast Radius & Trade-Off Matrix)
Translates executive business SLAs into annual downtime budgets, calculates Failure Domain blast radius,
and runs a weighted CCDE Trade-Off Analysis across competing design options.
No real enterprise infrastructure or live network hardware is connected.
"""

import json


def sla_downtime_budget(sla_percent: float) -> dict:
    minutes_per_year = 365.25 * 24 * 60
    allowed_down_min = round(minutes_per_year * (1.0 - sla_percent / 100.0), 2)
    return {
        "sla_percent": sla_percent,
        "max_downtime_minutes_per_year": allowed_down_min,
        "implication": "Requires <1s failover + 2N/Dual-Homing + Hitless upgrades" if allowed_down_min < 60 else "N+1 with standard convergence acceptable",
    }


def blast_radius(total_users: int, failure_domains: int) -> dict:
    affected = round(total_users / failure_domains)
    pct = round((affected / total_users) * 100.0, 2)
    return {"total_users": total_users, "failure_domains": failure_domains, "max_users_impacted_per_fault": affected, "blast_radius_pct": pct}


def weighted_tradeoff(weights: dict[str, float], options: dict[str, dict[str, int]]) -> list[dict]:
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
    report = {
        "mode": "LOCAL_MOCK_CCDE_DESIGN_MODELER",
        "sla_translations": [sla_downtime_budget(99.9), sla_downtime_budget(99.99), sla_downtime_budget(99.999)],
        "failure_domain_comparison": {
            "single_flat_domain": blast_radius(4000, 1),
            "eight_modular_blocks": blast_radius(4000, 8),
        },
        "weighted_tradeoff_ranking": weighted_tradeoff(weights, options),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
