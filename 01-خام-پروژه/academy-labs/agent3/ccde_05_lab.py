#!/usr/bin/env python3
"""
Local Mock Lab — ccde_05 (CCDE Data Center Architecture: Speed-of-Light DCI RTT, Sync vs Async & Active/Active)
Calculates fiber speed-of-light RTT (~1 ms per 100 km round-trip), determines Synchronous vs Asynchronous
storage replication feasibility, and evaluates Active/Active DCI vs L3-only DCI with GSLB.
No real DWDM optical equipment or data center fabrics are connected.
"""

import json


def evaluate_dci_distance(city_pair: str, fiber_km: float) -> dict:
    # Light in single-mode fiber travels ~200,000 km/s => 5 us/km one-way => 10 us/km RTT (1 ms per 100 km)
    rtt_ms = round(fiber_km * 0.01, 2)
    sync_replication_ok = rtt_ms <= 5.0
    return {
        "pair": city_pair,
        "fiber_distance_km": fiber_km,
        "physics_min_rtt_ms": rtt_ms,
        "synchronous_storage_rpo0_feasible": sync_replication_ok,
        "recommended_replication": "Synchronous Replication (RPO = 0 possible)" if sync_replication_ok else "Asynchronous Replication (RPO > 0) — fiber physics exceeds 5ms sync write limit",
    }


def evaluate_dci_l2_stretch(app_hardcodes_ip_on_failover: bool, budget_for_evpn_multisite: bool) -> dict:
    if not app_hardcodes_ip_on_failover:
        return {
            "dci_model": "L3-Only DCI + DNS GSLB / Anycast BGP",
            "l2_stretched": False,
            "reason": "Gold-standard CCDE choice: zero shared L2 broadcast/STP fate between data centers",
        }
    if budget_for_evpn_multisite:
        return {
            "dci_model": "Contained Overlay DCI (EVPN Multi-Site / ACI Multi-Site) with BUM Storm Control + Host-Route Injection",
            "l2_stretched": True,
            "reason": "Isolates broadcast/control plane faults while meeting legacy IP-persistence requirement",
        }
    return {
        "dci_model": "Refactor Application / DNS Failover (Reject Raw L2 Trunk Stretch!)",
        "l2_stretched": False,
        "reason": "Raw L2 VLAN stretch across cities risks dual-DC meltdown from a single STP/BUM storm",
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_DC_DCI_MODELER",
        "fiber_physics_dci_checks": [
            evaluate_dci_distance("Tehran_DC1 <-> Karaj_DC2", 65.0),
            evaluate_dci_distance("Tehran_DC1 <-> Isfahan_DC2", 450.0),
            evaluate_dci_distance("Frankfurt_DC1 <-> Dubai_DC2", 5000.0),
        ],
        "l2_stretch_design_decisions": {
            "modern_stateless_web_app": evaluate_dci_l2_stretch(False, True),
            "legacy_erp_fixed_ip": evaluate_dci_l2_stretch(True, True),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
