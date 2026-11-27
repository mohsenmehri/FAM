#!/usr/bin/env python3
"""
Local Mock Lab — ccde_20 (CCDE HLD/LLD Completeness Auditor & 400-007 Exam Trap Detector)
Audits an HLD document for all mandatory CCDE architecture sections (Business Drivers, Constraints,
Assumptions, Trade-Off Matrix, Failure Domains, Security, Migration & Rollback) and flags classic 400-007 traps.
No real exam portal or enterprise document management system is connected.
"""

import json


REQUIRED_HLD_SECTIONS = [
    "executive_summary_and_business_drivers",
    "requirements_constraints_and_assumptions_register",
    "high_level_topology_and_failure_domains",
    "technology_selection_and_tradeoff_matrix",
    "security_and_compliance_architecture",
    "capacity_scalability_and_ha_math",
    "migration_coexistence_and_rollback_strategy",
]


def audit_hld_completeness(present_sections: list[str], includes_raw_cli_configs: bool) -> dict:
    missing = [s for s in REQUIRED_HLD_SECTIONS if s not in present_sections]
    warnings = []
    if includes_raw_cli_configs:
        warnings.append("HLD_SCOPE_TRAP: Raw CLI configs and per-port IP tables belong in LLD, NOT HLD!")
    return {
        "hld_ready_for_architecture_board": (len(missing) == 0 and not warnings),
        "missing_hld_sections": missing,
        "scope_warnings": warnings,
    }


def detect_exam_400_007_traps(answer_choice: dict) -> list[str]:
    traps = []
    if answer_choice["ignores_budget_or_ops_skill_constraint"]:
        traps.append("TRAP_1: Ignored a hidden Constraint in stakeholder emails (budget / small Ops team)!")
    if answer_choice["chooses_most_complex_tech_without_driver"]:
        traps.append("TRAP_2: Over-Engineering — picked complex tech (e.g. ACI/RSVP-TE) with no business driver!")
    if answer_choice["skips_migration_coexistence"]:
        traps.append("TRAP_3: Designed a pretty Greenfield picture but ignored Brownfield zero-downtime migration!")
    return traps


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_HLD_DEFENSE_AND_EXAM_AUDITOR",
        "hld_audit_complete_draft": audit_hld_completeness(REQUIRED_HLD_SECTIONS, includes_raw_cli_configs=False),
        "hld_audit_flawed_draft": audit_hld_completeness(REQUIRED_HLD_SECTIONS[:4], includes_raw_cli_configs=True),
        "exam_400_007_trap_checks": {
            "over_engineered_answer": detect_exam_400_007_traps({
                "ignores_budget_or_ops_skill_constraint": True,
                "chooses_most_complex_tech_without_driver": True,
                "skips_migration_coexistence": True,
            }),
            "ccde_master_answer": detect_exam_400_007_traps({
                "ignores_budget_or_ops_skill_constraint": False,
                "chooses_most_complex_tech_without_driver": False,
                "skips_migration_coexistence": False,
            }),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
