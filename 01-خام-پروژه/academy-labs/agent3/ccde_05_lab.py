#!/usr/bin/env python3
"""
Local Mock Lab — ccde_05 (CCDE Data Center Architecture: Speed-of-Light DCI RTT, Product-Conditioned Sync vs Async & L3 DCI)
Calculates ideal fiber speed-of-light RTT (~0.01 ms/km) and realistic routed-fiber RTT (with path stretch),
evaluates Synchronous vs Asynchronous replication against product-specific RTT limits (e.g., VMware vSAN <=5ms
vs NetApp MetroCluster / VMware vMSC / Dell Metro Node <=10ms), and models L3-only DCI with GSLB.
No real DWDM optical equipment, storage arrays, or data center fabrics are connected.
"""

import json

PRODUCT_SYNC_LIMITS_MS = {
    "vmware_vsan_stretched": 5.0,
    "netapp_metrocluster_or_vmsc": 10.0,
}


def evaluate_dci_distance(city_pair: str, straight_km: float, route_stretch: float = 1.35) -> dict:
    # Ideal silica fiber (~200,000 km/s) => ~0.01 ms/km RTT; real terrestrial routes add stretch + DWDM delay
    theoretical_rtt_ms = round(straight_km * 0.01, 2)
    routed_rtt_ms = round(theoretical_rtt_ms * route_stretch, 2)
    product_feasibility = {
        name: (routed_rtt_ms <= limit_ms)
        for name, limit_ms in PRODUCT_SYNC_LIMITS_MS.items()
    }
    any_sync_feasible = any(product_feasibility.values())
    return {
        "pair": city_pair,
        "straight_distance_km": straight_km,
        "theoretical_min_rtt_ms": theoretical_rtt_ms,
        "estimated_routed_rtt_ms": routed_rtt_ms,
        "sync_feasible_by_product": product_feasibility,
        "recommended_replication": (
            "Synchronous Replication feasible (subject to product RTT limit & app write-latency SLA)"
            if any_sync_feasible
            else "Asynchronous Replication required — routed fiber RTT exceeds standard 5-10 ms product sync limits"
        ),
    }


def evaluate_dci_l2_stretch(app_hardcodes_ip_on_failover: bool, budget_for_evpn_multisite: bool) -> dict:
    if not app_hardcodes_ip_on_failover:
        return {
            "dci_model": "L3-Only DCI + DNS GSLB / Anycast BGP",
            "l2_stretched": False,
            "reason": "Preferred CCDE choice: zero shared L2 broadcast/STP fate between data centers",
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
    # At 450 km (~6.08 ms routed): fails vSAN 5ms limit, still under 10ms MetroCluster limit (with write penalty!)
    isfahan = report["fiber_physics_dci_checks"][1]
    assert isfahan["sync_feasible_by_product"]["vmware_vsan_stretched"] is False
    assert isfahan["sync_feasible_by_product"]["netapp_metrocluster_or_vmsc"] is True
    # At 5,000 km (~67.5 ms routed): fails BOTH 5ms and 10ms product limits!
    dubai = report["fiber_physics_dci_checks"][2]
    assert all(v is False for v in dubai["sync_feasible_by_product"].values())
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
