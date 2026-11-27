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


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_dict_bool(d: dict, key: str) -> bool:
    if key not in d:
        raise ValueError(f"Missing required boolean key '{key}'")
    return _require_bool(d[key], key)


def audit_hld_completeness(present_sections: list[str], includes_raw_cli_configs: bool) -> dict:
    if not isinstance(present_sections, list) or not all(isinstance(s, str) for s in present_sections):
        raise ValueError("present_sections must be a list of section name strings")
    has_raw_cli = _require_bool(includes_raw_cli_configs, "includes_raw_cli_configs")
    present_set = set(present_sections)
    missing = [s for s in REQUIRED_HLD_SECTIONS if s not in present_set]
    warnings = []
    if has_raw_cli:
        warnings.append("HLD_SCOPE_TRAP: Raw CLI configs and per-port IP tables belong in LLD, NOT HLD!")
    return {
        "hld_ready_for_architecture_board": (len(missing) == 0 and not warnings),
        "missing_hld_sections": missing,
        "scope_warnings": warnings,
    }


def detect_exam_400_007_traps(answer_choice: dict) -> list[str]:
    if not isinstance(answer_choice, dict):
        raise ValueError(f"answer_choice must be a dict, got {type(answer_choice).__name__}")
    ignores_constraint = _require_dict_bool(answer_choice, "ignores_budget_or_ops_skill_constraint")
    over_engineers = _require_dict_bool(answer_choice, "chooses_most_complex_tech_without_driver")
    skips_migration = _require_dict_bool(answer_choice, "skips_migration_coexistence")
    traps = []
    if ignores_constraint:
        traps.append("TRAP_1: Ignored a hidden Constraint in stakeholder emails (budget / small Ops team)!")
    if over_engineers:
        traps.append("TRAP_2: Over-Engineering — picked complex tech (e.g. ACI/RSVP-TE) with no business driver!")
    if skips_migration:
        traps.append("TRAP_3: Designed a pretty Greenfield picture but ignored Brownfield coexistence, minimal-downtime migration & rollback!")
    return traps


def main() -> None:
    complete_audit = audit_hld_completeness(REQUIRED_HLD_SECTIONS, includes_raw_cli_configs=False)
    flawed_audit = audit_hld_completeness(REQUIRED_HLD_SECTIONS[:4], includes_raw_cli_configs=True)
    bad_traps = detect_exam_400_007_traps({
        "ignores_budget_or_ops_skill_constraint": True,
        "chooses_most_complex_tech_without_driver": True,
        "skips_migration_coexistence": True,
    })
    good_traps = detect_exam_400_007_traps({
        "ignores_budget_or_ops_skill_constraint": False,
        "chooses_most_complex_tech_without_driver": False,
        "skips_migration_coexistence": False,
    })

    assert complete_audit["hld_ready_for_architecture_board"] is True
    assert flawed_audit["hld_ready_for_architecture_board"] is False and len(flawed_audit["missing_hld_sections"]) == 3
    assert len(bad_traps) == 3 and good_traps == []

    report = {
        "mode": "LOCAL_MOCK_CCDE_HLD_DEFENSE_AND_EXAM_AUDITOR",
        "hld_audit_complete_draft": complete_audit,
        "hld_audit_flawed_draft": flawed_audit,
        "exam_400_007_trap_checks": {
            "over_engineered_answer": bad_traps,
            "ccde_master_answer": good_traps,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
