#!/usr/bin/env python3
"""
FAM Academy Lab — auto_20: AIOps Anomaly Detection, Root-Cause Correlation &
Closed-Loop Remediation with Human-in-the-Loop Gate (500-Branch Capstone Mock).
Execution boundary: Pure Python 3 stdlib simulation of 500 branches grouped
under 4 regional hubs, Z-score anomaly detection (with empty/constant baseline guards),
parent-child alert suppression (125->1 root cause), and strict-boolean blast-radius
approval gating (preventing truthy-string bypasses such as human_approved="False").
No live WAN controllers, ML cluster, or production routers connected.
"""

from __future__ import annotations

import json
import math


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def z_score(value: float, baseline: list[float]) -> float:
    if len(baseline) < 2:
        raise ValueError("baseline must contain at least 2 numeric observations")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"value must be a finite number, got {value!r}")
    mean = sum(baseline) / len(baseline)
    variance = sum((x - mean) ** 2 for x in baseline) / len(baseline)
    if variance == 0:
        if value == mean:
            return 0.0
        raise ValueError("baseline has zero variance; Z-score is undefined for a constant baseline")
    return (value - mean) / math.sqrt(variance)


def correlate_root_cause(hub_down: set[str], branch_alerts: list[dict]) -> dict:
    """Suppress downstream branch alerts when their parent regional hub uplink is down."""
    suppressed = 0
    independent = []
    for alert in branch_alerts:
        if alert["hub"] in hub_down:
            suppressed += 1
        else:
            independent.append(alert["branch_id"])
    return {
        "root_cause_incidents": sorted(hub_down),
        "suppressed_child_branch_alerts": suppressed,
        "independent_branch_alerts": independent,
    }


def remediation_decision(action: str, impacted_branches: int, confidence: float, human_approved: bool) -> dict:
    if isinstance(impacted_branches, bool) or not isinstance(impacted_branches, int) or impacted_branches < 0:
        raise ValueError(f"impacted_branches must be a non-negative integer, got {impacted_branches!r}")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        raise ValueError(f"confidence must be in [0.0, 1.0], got {confidence!r}")
    approved = _require_bool(human_approved, "human_approved")

    high_risk = impacted_branches > 5 or action in {"failover_regional_hub", "rewrite_bgp_policy"}
    if high_risk and not approved:
        return {"executed": False, "mode": "AWAITING_HUMAN_APPROVAL", "reason": "High blast radius requires Human-in-the-Loop"}
    if confidence < 0.85:
        return {"executed": False, "mode": "ESCALATED_TO_NOC", "reason": "Confidence below auto-remediation threshold"}
    return {"executed": True, "mode": "AUTO_OR_APPROVED_EXECUTED", "action": action}


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
    assert blocked["executed"] is False and approved["executed"] is True and safe_auto["executed"] is True

    print("=== auto_20 AIOps & 500-Branch Capstone Local Mock ===")
    print(json.dumps({
        "anomaly_z_score": round(spike_z, 2),
        "root_cause_correlation": rca,
        "high_blast_radius_without_approval": blocked,
        "high_blast_radius_with_approval": approved,
        "low_blast_radius_auto_remediation": safe_auto,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
