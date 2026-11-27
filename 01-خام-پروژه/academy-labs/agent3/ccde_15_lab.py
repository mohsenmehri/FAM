#!/usr/bin/env python3
"""
Local Mock Lab — ccde_15 (CCDE Business Requirements Analysis: Req vs Constraint, RPO/RTO Cost & Compliance)
Classifies stakeholder statements into Business Goal / Technical Requirement / Constraint / Assumption,
and computes financial downtime loss vs DR investment ROI from RPO/RTO targets.
No real financial ERP or production disaster recovery sites are connected.
"""

import json
import math


def _require_non_neg_finite(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a non-negative finite number (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval) or fval < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {val!r}")
    return fval


def classify_statement(statement: str, category: str, impact: str) -> dict:
    for nm, val in (("statement", statement), ("category", category), ("impact", impact)):
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{nm} must be a non-empty str, got {val!r}")
    return {"statement": statement, "ccde_category": category, "architectural_impact": impact}


def rto_financial_justification(downtime_loss_usd_per_hr: float, expected_incidents_per_yr: float, old_rto_hr: float, new_rto_hr: float, dr_annual_cost_usd: float) -> dict:
    loss_hr = _require_non_neg_finite(downtime_loss_usd_per_hr, "downtime_loss_usd_per_hr")
    inc_yr = _require_non_neg_finite(expected_incidents_per_yr, "expected_incidents_per_yr")
    old_rto = _require_non_neg_finite(old_rto_hr, "old_rto_hr")
    new_rto = _require_non_neg_finite(new_rto_hr, "new_rto_hr")
    dr_cost = _require_non_neg_finite(dr_annual_cost_usd, "dr_annual_cost_usd")
    try:
        old_annual_risk = loss_hr * old_rto * inc_yr
        new_annual_risk = loss_hr * new_rto * inc_yr
        annual_risk_avoided_exact = old_annual_risk - new_annual_risk
        net_benefit_exact = annual_risk_avoided_exact - dr_cost
    except OverflowError as exc:
        raise ValueError("RTO financial calculation overflowed IEEE-754 finite float range") from exc
    if not all(math.isfinite(v) for v in (old_annual_risk, new_annual_risk, annual_risk_avoided_exact, net_benefit_exact)):
        raise ValueError("RTO financial calculation produced non-finite value")
    return {
        "annual_risk_before_usd": round(old_annual_risk, 2),
        "annual_risk_after_usd": round(new_annual_risk, 2),
        "annual_risk_avoided_usd": round(annual_risk_avoided_exact, 2),
        "dr_investment_annual_usd": dr_cost,
        "net_annual_business_value_usd": round(net_benefit_exact, 2),
        "cfo_approved_roi": net_benefit_exact > 0,
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_BUSINESS_ANALYSIS_MODELER",
        "requirement_taxonomy": [
            classify_statement("Expand into 30 new retail stores within 6 months", "Business Goal", "Drives fast-provisioning SD-WAN + 5G DIA"),
            classify_statement("Voice jitter <= 15ms and failover < 1s", "Technical Requirement", "Drives AAR SLA policy + BFD + QoS"),
            classify_statement("Max CapEx $800k, Ops team of 3, PCI-DSS mandatory", "Constraint", "Eliminates over-engineered multi-vendor stack; requires isolated VRF_PCI"),
            classify_statement("Existing fiber conduits at HQ are physically diverse", "Assumption (MUST VERIFY!)", "Unverified assumption could hide L1 Shared Fate!"),
        ],
        "rto_cfo_roi_model": rto_financial_justification(
            downtime_loss_usd_per_hr=120000.0,
            expected_incidents_per_yr=2.0,
            old_rto_hr=4.0,
            new_rto_hr=0.25,
            dr_annual_cost_usd=250000.0,
        ),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
