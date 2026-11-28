#!/usr/bin/env python3
"""
FAM Academy Lab — auto_11: Ansible Playbook, Inventory & Idempotency Mock.
Execution boundary: Pure Python 3 stdlib mock simulating Ansible inventory
group matching, ios_config parents hierarchy, --check diff mode (with strict
bool validation), handlers, and idempotency across two consecutive playbook runs
against isolated per-run state. No real Ansible/SSH run.
"""

from __future__ import annotations

import copy
import json

INVENTORY = {
    "core_routers": ["R1-CORE", "R2-CORE"],
    "access_switches": ["SW1-ACC"],
}

DEFAULT_DEVICE_STATE: dict[str, dict[str, list[str]]] = {
    "R1-CORE": {"interface Loopback0": ["description OLD", "ip address 10.255.0.1 255.255.255.255"]},
    "R2-CORE": {"interface Loopback0": ["description MANAGEMENT_LO0", "ip address 10.255.0.2 255.255.255.255"]},
    "SW1-ACC": {},
}

# Backwards-compatible default state table (callers should prefer passing an isolated copy via device_state=)
DEVICE_STATE: dict[str, dict[str, list[str]]] = copy.deepcopy(DEFAULT_DEVICE_STATE)


def build_initial_device_state() -> dict[str, dict[str, list[str]]]:
    """Return a fresh deep copy of initial mock device state so test runs stay isolated."""
    return copy.deepcopy(DEFAULT_DEVICE_STATE)


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def resolve_hosts(pattern: str) -> list[str]:
    if not isinstance(pattern, str) or not pattern.strip():
        raise ValueError(f"hosts pattern must be a non-empty str, got {pattern!r}")
    if pattern == "all":
        return sorted({h for hs in INVENTORY.values() for h in hs})
    if pattern in INVENTORY:
        return list(INVENTORY[pattern])
    all_hosts = {h for hs in INVENTORY.values() for h in hs}
    return [pattern] if pattern in all_hosts else []


def run_ios_config_task(
    hosts_pattern: str,
    parents: list[str],
    lines: list[str],
    check_mode: bool = False,
    device_state: dict[str, dict[str, list[str]]] | None = None,
) -> dict:
    is_check = _require_bool(check_mode, "check_mode")
    if (
        not isinstance(parents, list)
        or not isinstance(lines, list)
        or not all(isinstance(p, str) and p.strip() for p in parents)
        or not all(isinstance(line, str) and line.strip() for line in lines)
    ):
        raise ValueError("parents and lines must be lists of non-empty str")
    state = DEVICE_STATE if device_state is None else device_state
    if not isinstance(state, dict):
        raise ValueError("device_state must be a dict")
    parent_key = " > ".join(parents)
    results = {}
    handler_notified = []
    for host in resolve_hosts(hosts_pattern):
        current = state[host].get(parent_key, [])
        missing = [line for line in lines if line not in current]
        changed = bool(missing)
        if changed and not is_check:
            state[host][parent_key] = current + missing
        if changed:
            handler_notified.append(host)
        results[host] = {"changed": changed, "planned_additions": missing, "check_mode": is_check}
    return {
        "results": results,
        "save_config_handler_triggered_for": handler_notified,
        "handler_actually_executed": (not is_check) and bool(handler_notified),
    }


def main() -> None:
    state = build_initial_device_state()
    parents = ["interface Loopback0"]
    desired_lines = ["description MANAGEMENT_LO0"]

    dry_run = run_ios_config_task("core_routers", parents, desired_lines, check_mode=True, device_state=state)
    assert dry_run["results"]["R1-CORE"]["changed"] is True
    assert dry_run["results"]["R2-CORE"]["changed"] is False
    assert dry_run["handler_actually_executed"] is False
    # Dry-run must NOT mutate device state
    assert "description MANAGEMENT_LO0" not in state["R1-CORE"]["interface Loopback0"]

    run1 = run_ios_config_task("core_routers", parents, desired_lines, check_mode=False, device_state=state)
    assert run1["save_config_handler_triggered_for"] == ["R1-CORE"]
    assert run1["handler_actually_executed"] is True

    # Second run proves idempotency: zero changes, handler NOT re-triggered
    run2 = run_ios_config_task("core_routers", parents, desired_lines, check_mode=False, device_state=state)
    assert run2["results"]["R1-CORE"]["changed"] is False
    assert run2["results"]["R2-CORE"]["changed"] is False
    assert run2["save_config_handler_triggered_for"] == []
    assert run2["handler_actually_executed"] is False

    print("=== auto_11 Ansible Idempotency & Parents Local Mock ===")
    print(json.dumps({"check_mode": dry_run, "first_run": run1, "second_run_idempotent": run2}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
