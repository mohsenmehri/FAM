#!/usr/bin/env python3
"""
FAM Academy Lab — auto_16: Network CI/CD Pipeline & Security Gate Local Mock.
Execution boundary: Toy Python 3 stdlib simulation; raw_yaml is not parsed or checked against vlan_id,
regexes do not establish secret safety, and approval/verify/rollback are model inputs or outputs.
Pure Python 3 stdlib simulation of a simplified network CI/CD
pipeline (lint -> strict schema test rejecting bool/out-of-range VLAN -> secret scan ->
canary deploy -> post-verify + auto-rollback). No live GitHub Actions/GitLab Runner or network gear connected.
"""

from __future__ import annotations

import json
import re

SECRET_PATTERNS = [
    re.compile(r"password\s*[:=]\s*['\"]?[^'\"\s]+", re.IGNORECASE),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def run_pipeline(change_cfg: dict, post_verify_ok: bool = True, approved: bool = False) -> dict:
    if not isinstance(change_cfg, dict):
        raise ValueError(f"change_cfg must be a dict, got {type(change_cfg).__name__}")
    verify_ok = _require_bool(post_verify_ok, "post_verify_ok")
    approved = _require_bool(approved, "approved")
    raw_text = change_cfg.get("raw_yaml", "")
    if not isinstance(raw_text, str):
        raise ValueError(f"change_cfg['raw_yaml'] must be str, got {raw_text!r}")
    stages: list[dict] = []
    # Stage 1: Lint (no tabs in raw YAML text)
    lint_ok = "\t" not in raw_text
    stages.append({"stage": "lint", "passed": lint_ok})
    if not lint_ok:
        return {"status": "blocked_at_lint", "deploy_simulated": False, "stages": stages}

    # Stage 2: Schema / policy test (IEEE 802.1Q valid VLAN range 1..4094; explicitly reject Python bool!)
    vlan_id = change_cfg.get("vlan_id", -1)
    test_ok = isinstance(vlan_id, int) and not isinstance(vlan_id, bool) and 1 <= vlan_id <= 4094
    stages.append({"stage": "test", "passed": test_ok})
    if not test_ok:
        return {"status": "blocked_at_test", "deploy_simulated": False, "stages": stages}

    # Stage 3: Security scan (detect hardcoded credentials)
    secret_hit = any(p.search(raw_text) for p in SECRET_PATTERNS)
    sec_ok = not secret_hit
    stages.append({"stage": "security_scan", "passed": sec_ok})
    if not sec_ok:
        return {"status": "blocked_at_security_scan", "deploy_simulated": False, "stages": stages}

    # Approval is a model input, not evidence of human authorization.
    stages.append({"stage": "approval", "passed": approved})
    if not approved:
        return {"status": "blocked_at_approval", "deploy_simulated": False, "stages": stages}

    # Stage 4: simulated Canary deploy
    stages.append({"stage": "canary_deploy", "passed": True})

    # Stage 5: Post-deploy verification (triggers rollback if failed)
    stages.append({"stage": "verify", "passed": verify_ok})
    if not verify_ok:
        return {"status": "rollback_simulated", "deploy_simulated": True, "rollback_simulated": True, "stages": stages}
    return {"status": "succeeded", "deploy_simulated": True, "rollback_simulated": False, "stages": stages}


def main() -> None:
    tab_lint_pr = run_pipeline({"raw_yaml": "vlan:\t30\n", "vlan_id": 30})
    assert tab_lint_pr["status"] == "blocked_at_lint" and tab_lint_pr["deploy_simulated"] is False

    bool_vlan_pr = run_pipeline({"raw_yaml": "vlan: true\n", "vlan_id": True})
    assert bool_vlan_pr["status"] == "blocked_at_test" and bool_vlan_pr["deploy_simulated"] is False

    out_of_range_pr = run_pipeline({"raw_yaml": "vlan: 5000\n", "vlan_id": 5000})
    assert out_of_range_pr["status"] == "blocked_at_test" and out_of_range_pr["deploy_simulated"] is False

    leaked_secret_pr = run_pipeline({"raw_yaml": "vlan: 30\npassword: SuperSecret123\n", "vlan_id": 30})
    assert leaked_secret_pr["status"] == "blocked_at_security_scan"
    assert leaked_secret_pr["deploy_simulated"] is False

    failed_verify_pr = run_pipeline({"raw_yaml": "vlan: 30\nname: DMZ\n", "vlan_id": 30}, post_verify_ok=False, approved=True)
    assert failed_verify_pr["status"] == "rollback_simulated"
    assert failed_verify_pr["rollback_simulated"] is True

    clean_pr = run_pipeline({"raw_yaml": "vlan: 30\nname: DMZ\n", "vlan_id": 30}, post_verify_ok=True, approved=True)
    assert clean_pr["status"] == "succeeded"

    print("=== auto_16 Network CI/CD Pipeline Local Mock ===")
    print(json.dumps({
        "tab_lint_pr": tab_lint_pr,
        "bool_vlan_rejected_pr": bool_vlan_pr,
        "secret_leak_pr": leaked_secret_pr,
        "failed_post_verify_pr": failed_verify_pr,
        "clean_pr": clean_pr,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
