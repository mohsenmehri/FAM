#!/usr/bin/env python3
"""
FAM Academy Lab — auto_17: Containers, Docker Networking & Hardening Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of read-only Image vs
ephemeral Container layer vs persistent Volume, Docker network drivers
(bridge/host/macvlan), and Dockerfile security linter. No Docker daemon run.
"""

from __future__ import annotations

import copy
import json

NETWORK_DRIVERS = {
    "bridge": {"own_ip": True, "own_lan_mac": False, "uses_nat_port_map": True, "host_net_isolation": True},
    "host": {"own_ip": False, "own_lan_mac": False, "uses_nat_port_map": False, "host_net_isolation": False},
    "macvlan": {"own_ip": True, "own_lan_mac": True, "uses_nat_port_map": False, "host_net_isolation": True},
}


def audit_dockerfile(lines: list[str]) -> list[str]:
    findings = []
    joined = "\n".join(lines)
    if ":latest" in joined:
        findings.append("Avoid unpinned :latest base image tag")
    if not any(line.strip().startswith("USER ") and "root" not in line.lower() for line in lines):
        findings.append("Missing non-root USER instruction")
    if any("ENV " in line and ("PASSWORD=" in line.upper() or "SECRET=" in line.upper()) for line in lines):
        findings.append("Hardcoded secret in ENV instruction")
    return findings


def main() -> None:
    image_fs = {"/app/collector.py": "v1.0"}  # read-only template
    named_volume = {"/var/lib/tsdb": ["metric_day1"]}  # persistent host-managed storage

    # Container 1 starts from image, writes to ephemeral layer AND named volume
    c1_layer = copy.deepcopy(image_fs)
    c1_layer["/tmp/ephemeral.log"] = "temp"
    named_volume["/var/lib/tsdb"].append("metric_day2")

    # Container 1 is removed; Container 2 recreated from same image + same volume
    del c1_layer
    c2_layer = copy.deepcopy(image_fs)
    ephemeral_lost = "/tmp/ephemeral.log" not in c2_layer
    volume_persisted = "metric_day2" in named_volume["/var/lib/tsdb"]
    assert ephemeral_lost and volume_persisted

    insecure_df = ["FROM python:latest", "ENV API_PASSWORD=admin123", "COPY . /app"]
    secure_df = ["FROM python:3.11-slim", "RUN useradd -m appuser", "USER appuser", "COPY . /app"]
    assert len(audit_dockerfile(insecure_df)) == 3
    assert audit_dockerfile(secure_df) == []
    assert NETWORK_DRIVERS["macvlan"]["own_lan_mac"] is True

    print("=== auto_17 Docker Image/Volume, Networking & Security Local Mock ===")
    print(json.dumps({
        "ephemeral_layer_cleared_on_recreate": ephemeral_lost,
        "named_volume_persisted": volume_persisted,
        "macvlan_properties": NETWORK_DRIVERS["macvlan"],
        "insecure_dockerfile_findings": audit_dockerfile(insecure_df),
        "secure_dockerfile_findings": audit_dockerfile(secure_df),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
