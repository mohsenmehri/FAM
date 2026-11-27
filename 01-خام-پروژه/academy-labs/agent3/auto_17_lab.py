#!/usr/bin/env python3
"""
FAM Academy Lab — auto_17: Containers, Docker Networking & Hardening Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of read-only Image vs
ephemeral Container layer vs persistent Volume, Docker network drivers
(bridge/host/macvlan), and Dockerfile security linter (enforcing final non-root
USER, rejecting UID 0 / root escalation, unpinned :latest, and hardcoded ENV secrets).
No Docker daemon run.
"""

from __future__ import annotations

import copy
import json

NETWORK_DRIVERS = {
    "bridge": {"own_ip": True, "own_lan_mac": False, "uses_nat_port_map": True, "host_net_isolation": True},
    "host": {"own_ip": False, "own_lan_mac": False, "uses_nat_port_map": False, "host_net_isolation": False},
    "macvlan": {"own_ip": True, "own_lan_mac": True, "uses_nat_port_map": False, "host_net_isolation": True},
}

SECRET_ENV_MARKERS = ("PASSWORD=", "SECRET=", "TOKEN=", "API_KEY=")


def _is_root_user_spec(user_spec: str) -> bool:
    primary = user_spec.strip().split(":")[0].strip().lower()
    return primary in ("", "root", "0")


def audit_dockerfile(lines: list[str]) -> list[str]:
    findings = []
    joined = "\n".join(lines)
    if ":latest" in joined:
        findings.append("Avoid unpinned :latest base image tag")

    user_instructions = [line.strip()[5:].strip() for line in lines if line.strip().upper().startswith("USER ")]
    if not user_instructions or _is_root_user_spec(user_instructions[-1]):
        findings.append("Final effective USER must be non-root (neither root nor UID 0)")

    if any(
        line.strip().upper().startswith("ENV ") and any(marker in line.upper() for marker in SECRET_ENV_MARKERS)
        for line in lines
    ):
        findings.append("Hardcoded secret in ENV instruction")
    return findings


def main() -> None:
    image_fs = {"/app/collector.py": "v1.0"}  # read-only template
    named_volume = {"/var/lib/tsdb": ["metric_day1"]}  # persistent host-managed mount

    # Container 1 writes ephemeral file + persistent volume record
    container1_rw = copy.deepcopy(image_fs)
    container1_rw["/tmp/ephemeral.log"] = "lost_when_removed"
    named_volume["/var/lib/tsdb"].append("metric_day2")

    # Recreating container starts fresh from read-only image, while volume survives
    container2_rw = copy.deepcopy(image_fs)
    ephemeral_lost = "/tmp/ephemeral.log" not in container2_rw
    volume_persisted = "metric_day2" in named_volume["/var/lib/tsdb"]
    assert ephemeral_lost and volume_persisted

    insecure_df = ["FROM python:latest", "ENV API_PASSWORD=admin123", "COPY . /app"]
    uid0_escalation_df = ["FROM python:3.11-slim", "USER appuser", "USER 0", "COPY . /app"]
    secure_df = ["FROM python:3.11-slim", "RUN useradd -m appuser", "USER appuser", "COPY . /app"]
    assert len(audit_dockerfile(insecure_df)) == 3
    assert len(audit_dockerfile(uid0_escalation_df)) == 1
    assert audit_dockerfile(secure_df) == []
    assert NETWORK_DRIVERS["macvlan"]["own_lan_mac"] is True

    print("=== auto_17 Docker Image/Volume, Networking & Security Local Mock ===")
    print(json.dumps({
        "ephemeral_layer_cleared_on_recreate": ephemeral_lost,
        "named_volume_persisted": volume_persisted,
        "macvlan_properties": NETWORK_DRIVERS["macvlan"],
        "insecure_dockerfile_findings": audit_dockerfile(insecure_df),
        "uid0_escalation_findings": audit_dockerfile(uid0_escalation_df),
        "secure_dockerfile_findings": audit_dockerfile(secure_df),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
