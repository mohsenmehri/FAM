#!/usr/bin/env python3
"""
Local Mock Lab — ccde_16 (CCDE Migration Strategy: Phased vs Forklift, Coexistence Loop Guard & MoP Rollback Gate)
Evaluates Migration Risk (Forklift vs Parallel Phased), validates loop-free mutual redistribution tags
during Ships-in-the-Night coexistence, and runs a 4-pillar MoP Pre/Post-Check & Rollback decision gate.
No real production routers or maintenance windows are connected.
"""

import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_non_neg_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val < 0:
        raise ValueError(f"{name} must be a non-negative int (not bool), got {val!r}")
    return val


def select_migration_strategy(max_downtime_min: int, dual_budget_available: bool) -> dict:
    dt = _require_non_neg_int(max_downtime_min, "max_downtime_min")
    dual_budget = _require_bool(dual_budget_available, "dual_budget_available")
    if dt <= 15 and dual_budget:
        return {
            "strategy": "Parallel Phased Migration (Build Side-by-Side + Graceful Cutover)",
            "risk": "LOW",
            "reason": "Build & validate new fabric in parallel, migrate 1 pilot site/VLAN first, keep instant rollback path",
        }
    if dt >= 240:
        return {
            "strategy": "Controlled Weekend Forklift (Only When Maintenance Window & Rollback Are Guaranteed)",
            "risk": "MEDIUM-HIGH",
            "reason": "Lower CapEx, but requires full staged config, verified backups, and strict Go/No-Go timer",
        }
    return {
        "strategy": "In-Place Staged Overlay / Coexistence (e.g. SRMS LDP-to-SR or Ships-in-the-Night IGP)",
        "risk": "MEDIUM",
        "reason": "Avoids forklift outage without duplicating 100% of hardware",
    }


def evaluate_mop_gate(pre_checks_passed: bool, post_checks: dict[str, bool], elapsed_min: int, go_nogo_deadline_min: int) -> dict:
    pre_ok = _require_bool(pre_checks_passed, "pre_checks_passed")
    if not isinstance(post_checks, dict) or not post_checks:
        raise ValueError("post_checks must be a non-empty dict of check_name -> strict bool")
    elapsed = _require_non_neg_int(elapsed_min, "elapsed_min")
    deadline = _require_non_neg_int(go_nogo_deadline_min, "go_nogo_deadline_min")
    if deadline <= 0:
        raise ValueError(f"go_nogo_deadline_min must be > 0, got {deadline!r}")
    failed_posts = []
    for k, v in post_checks.items():
        if not isinstance(k, str) or not k.strip():
            raise ValueError(f"post_checks key must be a non-empty str, got {k!r}")
        if not _require_bool(v, f"post_checks['{k}']"):
            failed_posts.append(k)
    if not pre_ok:
        return {"decision": "ABORT_BEFORE_CHANGE", "reason": "Pre-checks failed — never touch production on a broken baseline!"}
    if failed_posts and elapsed >= deadline:
        return {"decision": "EXECUTE_ROLLBACK_IMMEDIATELY", "failed_checks": failed_posts, "reason": "Go/No-Go deadline reached with unresolved post-check failures!"}
    if not failed_posts:
        return {"decision": "CUTOVER_SUCCESS_COMMIT", "failed_checks": [], "reason": "All post-checks match baseline; sign off maintenance window."}
    return {"decision": "TROUBLESHOOT_WITHIN_WINDOW", "failed_checks": failed_posts, "remaining_min": deadline - elapsed}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_MIGRATION_MODELER",
        "strategy_choices": {
            "24x7_bank_zero_outage": select_migration_strategy(max_downtime_min=5, dual_budget_available=True),
            "carrier_ldp_to_sr_brownfield": select_migration_strategy(max_downtime_min=10, dual_budget_available=False),
            "small_office_weekend_window": select_migration_strategy(max_downtime_min=360, dual_budget_available=False),
        },
        "coexistence_loop_prevention": {
            "tactic_1": "Ships-in-the-Night (run new IGP at higher AD first, test, then lower AD smoothly)",
            "tactic_2": "Mutual Redistribution Route-Tagging (deny re-entry of tagged prefixes at dual ABRs)",
        },
        "mop_gate_simulations": {
            "clean_cutover": evaluate_mop_gate(True, {"bgp_peers_up": True, "app_synthetic_ok": True, "zero_packet_loss": True}, 45, 90),
            "trigger_rollback_at_deadline": evaluate_mop_gate(True, {"bgp_peers_up": True, "app_synthetic_ok": False, "zero_packet_loss": False}, 92, 90),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
