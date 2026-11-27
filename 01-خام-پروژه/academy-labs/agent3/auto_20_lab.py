#!/usr/bin/env python3
"""
FAM Academy Lab — auto_20: AIOps Anomaly Detection, Parent-Child Correlation Heuristic &
Simulated Closed-Loop Remediation Gate with Human-in-the-Loop (500-Branch Capstone Mock).

Execution & modeling boundaries:
- Pure Python 3 stdlib local simulation of 500 branches grouped under 4 regional hubs.
- Strict input validation: z_score rejects non-finite numbers (NaN/Infinity), huge float-overflow
  ints (e.g. 10**500), booleans (True/False), and empty or zero-variance baselines with ValueError.
- remediation_decision enforces an explicit action allowlist (rejecting empty, None, or arbitrary
  actions like 'destroy_everything') and strict Python bool for human_approved. Output explicitly
  marks simulated_only=True so policy-gate output is never mistaken for live network modification.
- correlate_root_cause models a topology-parent alert-suppression heuristic ONLY; co-occurring
  branch alarms do NOT prove actual hub root cause without independent underlay/control-plane checks.
No live WAN controllers, ML cluster, or production routers are connected.
"""

from __future__ import annotations

import json
import math

LOW_RISK_ALLOWED_ACTIONS = frozenset({
    "shift_single_branch_sdwan_path",
    "adjust_qos_queue",
    "quarantine_single_port",
})

HIGH_RISK_ALLOWED_ACTIONS = frozenset({
    "failover_regional_hub",
    "rewrite_bgp_policy",
})

ALLOWED_REMEDIATION_ACTIONS = LOW_RISK_ALLOWED_ACTIONS | HIGH_RISK_ALLOWED_ACTIONS


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r} ({type(val).__name__})")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval):
        raise ValueError(f"{name} must be a finite number (no NaN/Infinity), got {val!r}")
    return fval


def z_score(value: float, baseline: list[float]) -> float:
    if not isinstance(baseline, (list, tuple)) or len(baseline) < 2:
        raise ValueError("baseline must be a list/tuple with at least 2 finite numeric observations")
    val = _require_finite_num(value, "value")
    clean_base = [_require_finite_num(x, f"baseline[{i}]") for i, x in enumerate(baseline)]
    mean = sum(clean_base) / len(clean_base)
    variance = sum((x - mean) ** 2 for x in clean_base) / len(clean_base)
    if not math.isfinite(variance):
        raise ValueError("baseline variance overflowed IEEE-754 finite float range")
    if variance == 0.0:
        if val == mean:
            return 0.0
        raise ValueError("baseline has zero variance; Z-score is undefined for a constant baseline")
    return (val - mean) / math.sqrt(variance)


def correlate_root_cause(hub_down: set[str], branch_alerts: list[dict]) -> dict:
    """Suppress downstream branch alerts when their mapped parent hub has a reported outage (heuristic only)."""
    if not isinstance(hub_down, (set, frozenset)) or not isinstance(branch_alerts, list):
        raise ValueError("hub_down must be a set of hub names and branch_alerts must be a list of dicts")
    suppressed = 0
    independent = []
    for alert in branch_alerts:
        if alert["hub"] in hub_down:
            suppressed += 1
        else:
            independent.append(alert["branch_id"])
    return {
        "suspected_parent_hub_incidents": sorted(hub_down),
        "suppressed_child_branch_alerts": suppressed,
        "independent_branch_alerts": independent,
        "causal_caveat": (
            "Topology correlation heuristic ONLY: co-occurring branch alarms mapped to a hub do NOT prove "
            "actual root cause without independent underlay, routing, and carrier verification."
        ),
    }


def remediation_decision(action: str, impacted_branches: int, confidence: float, human_approved: bool) -> dict:
    if not isinstance(action, str) or action not in ALLOWED_REMEDIATION_ACTIONS:
        raise ValueError(
            f"action {action!r} is not in ALLOWED_REMEDIATION_ACTIONS: {sorted(ALLOWED_REMEDIATION_ACTIONS)}"
        )
    if isinstance(impacted_branches, bool) or not isinstance(impacted_branches, int) or impacted_branches < 0:
        raise ValueError(f"impacted_branches must be a non-negative integer, got {impacted_branches!r}")
    conf = _require_finite_num(confidence, "confidence")
    if not (0.0 <= conf <= 1.0):
        raise ValueError(f"confidence must be in [0.0, 1.0], got {conf!r}")
    approved = _require_bool(human_approved, "human_approved")

    high_risk = impacted_branches > 5 or action in HIGH_RISK_ALLOWED_ACTIONS
    if high_risk and not approved:
        return {
            "simulation_only": True,
            "simulated_execution_allowed": False,
            "mode": "AWAITING_HUMAN_APPROVAL",
            "action": action,
            "reason": "High blast radius or high-risk action requires Human-in-the-Loop approval",
        }
    if conf < 0.85:
        return {
            "simulation_only": True,
            "simulated_execution_allowed": False,
            "mode": "ESCALATED_TO_NOC",
            "action": action,
            "reason": "Confidence below simulated auto-remediation threshold (0.85)",
        }
    return {
        "simulation_only": True,
        "simulated_execution_allowed": True,
        "mode": "SIMULATED_GATE_APPROVED_NO_LIVE_CHANGE",
        "action": action,
        "note": "Local policy-gate simulation only; no live router or controller configuration is changed.",
    }


def main() -> None:
    baseline_rtt_ms = [22.0, 23.5, 21.8, 22.4, 23.1, 22.7, 21.9, 22.6]
    spike_z = z_score(68.0, baseline_rtt_ms)
    assert spike_z > 3.0, "Latency spike must exceed 3-sigma anomaly threshold"

    # 500 branches = 4 regional hubs x 125 branches; HUB-WEST fails + 1 independent branch in HUB-EAST
    branch_alerts = [{"branch_id": f"BR-W-{i:03d}", "hub": "HUB-WEST"} for i in range(1, 126)]
    branch_alerts.append({"branch_id": "BR-E-042", "hub": "HUB-EAST"})
    rca = correlate_root_cause({"HUB-WEST"}, branch_alerts)
    assert rca["suppressed_child_branch_alerts"] == 125
    assert rca["independent_branch_alerts"] == ["BR-E-042"]

    blocked = remediation_decision("failover_regional_hub", impacted_branches=125, confidence=0.96, human_approved=False)
    approved = remediation_decision("failover_regional_hub", impacted_branches=125, confidence=0.96, human_approved=True)
    safe_auto = remediation_decision("shift_single_branch_sdwan_path", impacted_branches=1, confidence=0.95, human_approved=False)
    assert blocked["simulated_execution_allowed"] is False
    assert approved["simulated_execution_allowed"] is True and approved["simulation_only"] is True
    assert safe_auto["simulated_execution_allowed"] is True and safe_auto["simulation_only"] is True

    print("=== auto_20 AIOps & 500-Branch Capstone Local Mock ===")
    print(json.dumps({
        "anomaly_z_score": round(spike_z, 2),
        "root_cause_correlation_heuristic": rca,
        "high_blast_radius_without_approval": blocked,
        "high_blast_radius_with_approval": approved,
        "low_blast_radius_auto_remediation": safe_auto,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
