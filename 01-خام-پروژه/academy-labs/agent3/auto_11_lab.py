#!/usr/bin/env python3
"""
FAM Academy Lab — auto_11: Ansible Playbook, Inventory & Idempotency Mock.
Execution boundary: Pure Python 3 stdlib mock simulating Ansible inventory
group matching, ios_config parents hierarchy, --check diff mode, handlers,
and idempotency across two consecutive playbook runs. No real Ansible/SSH run.
"""

from __future__ import annotations

import json

INVENTORY = {
    "core_routers": ["R1-CORE", "R2-CORE"],
    "access_switches": ["SW1-ACC"],
}

DEVICE_STATE: dict[str, dict[str, list[str]]] = {
    "R1-CORE": {"interface Loopback0": ["description OLD", "ip address 10.255.0.1 255.255.255.255"]},
    "R2-CORE": {"interface Loopback0": ["description MANAGEMENT_LO0", "ip address 10.255.0.2 255.255.255.255"]},
    "SW1-ACC": {},
}


def resolve_hosts(pattern: str) -> list[str]:
    if pattern == "all":
        return sorted({h for hs in INVENTORY.values() for h in hs})
    if pattern in INVENTORY:
        return list(INVENTORY[pattern])
    all_hosts = {h for hs in INVENTORY.values() for h in hs}
    return [pattern] if pattern in all_hosts else []


def run_ios_config_task(hosts_pattern: str, parents: list[str], lines: list[str], check_mode: bool = False) -> dict:
    parent_key = " > ".join(parents)
    results = {}
    handler_notified = []
    for host in resolve_hosts(hosts_pattern):
        current = DEVICE_STATE[host].get(parent_key, [])
        missing = [line for line in lines if line not in current]
        changed = bool(missing)
        if changed and not check_mode:
            DEVICE_STATE[host][parent_key] = current + missing
        if changed:
            handler_notified.append(host)
        results[host] = {"changed": changed, "planned_additions": missing, "check_mode": check_mode}
    return {"results": results, "save_config_handler_triggered_for": handler_notified}


def main() -> None:
    parents = ["interface Loopback0"]
    desired_lines = ["description MANAGEMENT_LO0"]

    dry_run = run_ios_config_task("core_routers", parents, desired_lines, check_mode=True)
    assert dry_run["results"]["R1-CORE"]["changed"] is True
    assert dry_run["results"]["R2-CORE"]["changed"] is False
    # Dry-run must NOT mutate device state
    assert "description MANAGEMENT_LO0" not in DEVICE_STATE["R1-CORE"]["interface Loopback0"]

    run1 = run_ios_config_task("core_routers", parents, desired_lines, check_mode=False)
    assert run1["save_config_handler_triggered_for"] == ["R1-CORE"]

    # Second run proves idempotency: zero changes, handler NOT re-triggered
    run2 = run_ios_config_task("core_routers", parents, desired_lines, check_mode=False)
    assert run2["results"]["R1-CORE"]["changed"] is False
    assert run2["results"]["R2-CORE"]["changed"] is False
    assert run2["save_config_handler_triggered_for"] == []

    print("=== auto_11 Ansible Idempotency & Parents Local Mock ===")
    print(json.dumps({"check_mode": dry_run, "first_run": run1, "second_run_idempotent": run2}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
