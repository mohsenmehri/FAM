#!/usr/bin/env python3
"""
FAM Academy Lab — spec_dc_nx: Cisco NX-OS vPC Type-1 Consistency,
Peer-Link/Keepalive Split-Brain Protection & Orphan Port Trap Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of NX-OS vPC consistency
validation and peer-link failure behavior. No live Cisco Nexus switch connected.
"""

from __future__ import annotations

import json


def check_vpc_type1(peer1: dict, peer2: dict) -> dict:
    mismatches = []
    for key in ("mtu", "stp_mode", "native_vlan"):
        if peer1[key] != peer2[key]:
            mismatches.append(f"{key}: primary={peer1[key]} vs secondary={peer2[key]}")
    return {
        "type1_consistent": len(mismatches) == 0,
        "mismatches": mismatches,
        "secondary_vpc_ports_state": "UP" if not mismatches else "SUSPENDED",
    }


def simulate_peer_link_failure(keepalive_alive: bool, orphan_port_suspend: bool) -> dict:
    if keepalive_alive:
        return {
            "primary_state": "ACTIVE (forwards traffic)",
            "secondary_vpc_member_ports": "SUSPENDED (prevents split-brain)",
            "secondary_orphan_port": "SUSPENDED (fails over cleanly)" if orphan_port_suspend else "REMAINS_UP_BLACKHOLE_RISK",
        }
    return {
        "primary_state": "DOWN_OR_UNREACHABLE",
        "secondary_vpc_member_ports": "TAKES_OVER_AS_PRIMARY",
        "secondary_orphan_port": "UP_AND_FORWARDING",
    }


def main() -> None:
    mtu_mismatch = check_vpc_type1(
        {"mtu": 9216, "stp_mode": "rapid-pvst", "native_vlan": 1},
        {"mtu": 1500, "stp_mode": "rapid-pvst", "native_vlan": 1},
    )
    assert mtu_mismatch["type1_consistent"] is False
    assert mtu_mismatch["secondary_vpc_ports_state"] == "SUSPENDED"

    orphan_trap = simulate_peer_link_failure(keepalive_alive=True, orphan_port_suspend=False)
    orphan_fixed = simulate_peer_link_failure(keepalive_alive=True, orphan_port_suspend=True)
    assert orphan_trap["secondary_orphan_port"] == "REMAINS_UP_BLACKHOLE_RISK"
    assert "SUSPENDED" in orphan_fixed["secondary_orphan_port"]

    print("=== spec_dc_nx NX-OS vPC Consistency & Orphan Port Local Mock ===")
    print(json.dumps({
        "type1_mtu_check": mtu_mismatch,
        "peer_link_down_without_orphan_suspend": orphan_trap,
        "peer_link_down_with_orphan_suspend": orphan_fixed,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
