#!/usr/bin/env python3
"""
FAM Academy Lab — auto_15: Infrastructure as Code (IaC), Terraform State Drift
& NetBox Source-of-Truth Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of declarative plan/apply,
state file tracking, refresh-only drift detection, and dual-stack (IPv4 + IPv6)
IPAM overlap checks. No real Terraform binary, cloud provider, or NetBox server executed.
"""

from __future__ import annotations

import copy
import ipaddress
import json


class MiniDeclarativeIaC:
    def __init__(self) -> None:
        self.state: dict[str, dict] = {}
        self.live: dict[str, dict] = {}

    def plan(self, desired: dict[str, dict]) -> dict[str, list[str]]:
        to_create = [k for k in desired if k not in self.state]
        to_update = [k for k in desired if k in self.state and self.state[k] != desired[k]]
        to_destroy = [k for k in self.state if k not in desired]
        return {"create": to_create, "update": to_update, "destroy": to_destroy}

    def apply(self, desired: dict[str, dict]) -> dict[str, list[str]]:
        p = self.plan(desired)
        self.live = copy.deepcopy(desired)
        self.state = copy.deepcopy(desired)
        return p

    def plan_refresh_only(self) -> dict[str, dict]:
        """Inspect drift between state and live WITHOUT modifying live or state."""
        drifts = {}
        for k in set(self.state) | set(self.live):
            if self.state.get(k) != self.live.get(k):
                drifts[k] = {"state": self.state.get(k), "observed_live": self.live.get(k)}
        return drifts


def validate_sot_prefixes(prefixes: list[str]) -> list[str]:
    nets = [ipaddress.ip_network(p, strict=True) for p in prefixes]
    overlaps = []
    for i in range(len(nets)):
        for j in range(i + 1, len(nets)):
            if nets[i].version == nets[j].version and nets[i].overlaps(nets[j]):
                overlaps.append(f"{nets[i]} overlaps {nets[j]}")
    return overlaps


def main() -> None:
    iac = MiniDeclarativeIaC()
    desired = {
        "vlan_10": {"id": 10, "name": "CORP_DATA", "cidr": "10.10.10.0/24"},
        "vlan_20": {"id": 20, "name": "VOICE", "cidr": "10.10.20.0/24"},
    }
    first_apply = iac.apply(desired)
    assert first_apply == {"create": ["vlan_10", "vlan_20"], "update": [], "destroy": []}

    # Simulate manual out-of-band edit directly on live switch (Drift!)
    iac.live["vlan_20"]["name"] = "VOICE_MANUAL_EDIT"
    drift_report = iac.plan_refresh_only()
    assert "vlan_20" in drift_report
    # plan -refresh-only must NOT mutate state or live!
    assert iac.state["vlan_20"]["name"] == "VOICE"

    # NetBox/Nautobot SoT dual-stack (IPv4 + IPv6) prefix overlap detection
    overlaps = validate_sot_prefixes(["10.10.10.0/24", "10.10.10.128/25", "10.10.20.0/24", "2001:db8:1::/48"])
    assert len(overlaps) == 1

    print("=== auto_15 IaC State Drift & SoT Local Mock ===")
    print(json.dumps({
        "initial_apply": first_apply,
        "refresh_only_drift_detected": drift_report,
        "state_unchanged_after_plan_refresh_only": iac.state["vlan_20"]["name"] == "VOICE",
        "sot_prefix_overlaps": overlaps,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
