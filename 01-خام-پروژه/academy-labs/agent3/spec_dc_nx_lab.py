#!/usr/bin/env python3
"""
FAM Academy Lab — spec_dc_nx: Cisco NX-OS vPC Type-1 Consistency,
Peer-Link/Keepalive Split-Brain Protection & Orphan Port Trap Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of NX-OS vPC consistency
validation and peer-link failure behavior. No live Cisco Nexus switch connected.
"""

from __future__ import annotations

import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def check_vpc_type1(peer1: dict, peer2: dict) -> dict:
    for pname, peer in (("peer1", peer1), ("peer2", peer2)):
        if not isinstance(peer, dict):
            raise ValueError(f"{pname} must be a dict")
        for key in ("mtu", "stp_mode", "native_vlan"):
            if key not in peer:
                raise ValueError(f"{pname} missing required key '{key}'")
        if isinstance(peer["mtu"], bool) or not isinstance(peer["mtu"], int) or peer["mtu"] <= 0:
            raise ValueError(f"{pname}.mtu must be a positive int (not bool), got {peer['mtu']!r}")
        if isinstance(peer["native_vlan"], bool) or not isinstance(peer["native_vlan"], int) or not (1 <= peer["native_vlan"] <= 4094):
            raise ValueError(f"{pname}.native_vlan must be an int in [1, 4094] (not bool), got {peer['native_vlan']!r}")
        if not isinstance(peer["stp_mode"], str) or not peer["stp_mode"].strip():
            raise ValueError(f"{pname}.stp_mode must be a non-empty str, got {peer['stp_mode']!r}")
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
    ka = _require_bool(keepalive_alive, "keepalive_alive")
    orphan = _require_bool(orphan_port_suspend, "orphan_port_suspend")
    if ka:
        return {
            "primary_state": "ACTIVE (forwards traffic)",
            "secondary_vpc_member_ports": "SUSPENDED (prevents split-brain)",
            "secondary_orphan_port": "SUSPENDED (fails over cleanly)" if orphan else "REMAINS_UP_BLACKHOLE_RISK",
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
