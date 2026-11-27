#!/usr/bin/env python3
"""
Local Mock Lab — ccde_15 (CCDE Business Requirements Analysis: Req vs Constraint, RPO/RTO Cost & Compliance)
Classifies stakeholder statements into Business Goal / Technical Requirement / Constraint / Assumption,
and computes financial downtime loss vs DR investment ROI from RPO/RTO targets.
No real financial ERP or production disaster recovery sites are connected.
"""

import json


def classify_statement(statement: str, category: str, impact: str) -> dict:
    return {"statement": statement, "ccde_category": category, "architectural_impact": impact}


def rto_financial_justification(downtime_loss_usd_per_hr: float, expected_incidents_per_yr: float, old_rto_hr: float, new_rto_hr: float, dr_annual_cost_usd: float) -> dict:
    old_annual_risk = downtime_loss_usd_per_hr * old_rto_hr * expected_incidents_per_yr
    new_annual_risk = downtime_loss_usd_per_hr * new_rto_hr * expected_incidents_per_yr
    annual_risk_avoided = round(old_annual_risk - new_annual_risk, 2)
    net_benefit = round(annual_risk_avoided - dr_annual_cost_usd, 2)
    return {
        "annual_risk_before_usd": round(old_annual_risk, 2),
        "annual_risk_after_usd": round(new_annual_risk, 2),
        "annual_risk_avoided_usd": annual_risk_avoided,
        "dr_investment_annual_usd": dr_annual_cost_usd,
        "net_annual_business_value_usd": net_benefit,
        "cfo_approved_roi": net_benefit > 0,
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
