#!/usr/bin/env python3
"""
FAM Academy Lab — auto_16: Network CI/CD Pipeline & Security Gate Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of a 5-stage network CI/CD
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


def run_pipeline(change_cfg: dict, post_verify_ok: bool = True) -> dict:
    stages: list[dict] = []
    # Stage 1: Lint (no tabs in raw YAML text)
    raw_text = change_cfg.get("raw_yaml", "")
    lint_ok = "\t" not in raw_text
    stages.append({"stage": "lint", "passed": lint_ok})
    if not lint_ok:
        return {"status": "blocked_at_lint", "deploy_executed": False, "stages": stages}

    # Stage 2: Schema / policy test (IEEE 802.1Q valid VLAN range 1..4094; explicitly reject Python bool!)
    vlan_id = change_cfg.get("vlan_id", -1)
    test_ok = isinstance(vlan_id, int) and not isinstance(vlan_id, bool) and 1 <= vlan_id <= 4094
    stages.append({"stage": "test", "passed": test_ok})
    if not test_ok:
        return {"status": "blocked_at_test", "deploy_executed": False, "stages": stages}

    # Stage 3: Security scan (detect hardcoded credentials)
    secret_hit = any(p.search(raw_text) for p in SECRET_PATTERNS)
    sec_ok = not secret_hit
    stages.append({"stage": "security_scan", "passed": sec_ok})
    if not sec_ok:
        return {"status": "blocked_at_security_scan", "deploy_executed": False, "stages": stages}

    # Stage 4: Canary deploy
    stages.append({"stage": "canary_deploy", "passed": True})

    # Stage 5: Post-deploy verification (triggers rollback if failed)
    stages.append({"stage": "verify", "passed": post_verify_ok})
    if not post_verify_ok:
        return {"status": "rolled_back", "deploy_executed": True, "rollback_executed": True, "stages": stages}
    return {"status": "succeeded", "deploy_executed": True, "rollback_executed": False, "stages": stages}


def main() -> None:
    tab_lint_pr = run_pipeline({"raw_yaml": "vlan:\t30\n", "vlan_id": 30})
    assert tab_lint_pr["status"] == "blocked_at_lint" and tab_lint_pr["deploy_executed"] is False

    bool_vlan_pr = run_pipeline({"raw_yaml": "vlan: true\n", "vlan_id": True})
    assert bool_vlan_pr["status"] == "blocked_at_test" and bool_vlan_pr["deploy_executed"] is False

    out_of_range_pr = run_pipeline({"raw_yaml": "vlan: 5000\n", "vlan_id": 5000})
    assert out_of_range_pr["status"] == "blocked_at_test" and out_of_range_pr["deploy_executed"] is False

    leaked_secret_pr = run_pipeline({"raw_yaml": "vlan: 30\npassword: SuperSecret123\n", "vlan_id": 30})
    assert leaked_secret_pr["status"] == "blocked_at_security_scan"
    assert leaked_secret_pr["deploy_executed"] is False

    failed_verify_pr = run_pipeline({"raw_yaml": "vlan: 30\nname: DMZ\n", "vlan_id": 30}, post_verify_ok=False)
    assert failed_verify_pr["status"] == "rolled_back"
    assert failed_verify_pr["rollback_executed"] is True

    clean_pr = run_pipeline({"raw_yaml": "vlan: 30\nname: DMZ\n", "vlan_id": 30}, post_verify_ok=True)
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
