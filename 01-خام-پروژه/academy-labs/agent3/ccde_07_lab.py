#!/usr/bin/env python3
"""
Local Mock Lab — ccde_07 (CCDE Cloud Connectivity: Direct Connect vs VPN, Colo Hub & Hybrid Cloud Trap Auditor)
Evaluates Direct Connect/ExpressRoute vs IPsec VPN vs Colocation Cloud Exchange Hub,
calculates annual cloud egress cost impact, and checks for RFC 1918 CIDR overlaps across VPCs/On-Prem.
No real AWS/Azure/GCP accounts or Equinix Colocation exchanges are connected.
"""

import ipaddress
import json
import math


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_non_neg_finite(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a non-negative finite number (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval) or fval < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {val!r}")
    return fval


def select_cloud_interconnect(bandwidth_gbps: float, needs_deterministic_latency: bool, multi_cloud: bool) -> dict:
    bw = _require_non_neg_finite(bandwidth_gbps, "bandwidth_gbps")
    if bw <= 0:
        raise ValueError(f"bandwidth_gbps must be > 0, got {bw!r}")
    det_lat = _require_bool(needs_deterministic_latency, "needs_deterministic_latency")
    mcloud = _require_bool(multi_cloud, "multi_cloud")
    if mcloud and bw >= 5.0:
        return {
            "recommended": "Colocation Cloud Exchange Hub (e.g. Equinix Fabric) -> Private Virtual Cross-Connects to AWS/Azure/GCP",
            "reason": "Single high-speed aggregation hub avoids hairpinned cloud-to-cloud traffic and lowers Direct Connect egress fees",
        }
    if det_lat or bw > 1.25:
        return {
            "recommended": "Redundant Dedicated Direct Connect / ExpressRoute (Dual Diversely Routed Locations) + IPsec Backup",
            "reason": "Bypasses public internet jitter, exceeds classic 1.25Gbps single-tunnel IPsec throughput (without ECMP/higher SKUs), and typically lowers cloud egress rates (provider/region/tier-dependent)",
        }
    return {
        "recommended": "Redundant Site-to-Site IPsec VPN (BGP ECMP) over Dual ISP",
        "reason": "Fastest deployment and lowest OpEx for small workloads without strict latency SLA",
    }


def detect_cidr_overlaps(allocations: dict[str, str]) -> list[dict]:
    if not isinstance(allocations, dict):
        raise ValueError(f"allocations must be a dict of site -> CIDR, got {type(allocations).__name__}")
    items = []
    for name, cidr in allocations.items():
        if not isinstance(name, str) or not isinstance(cidr, str):
            raise ValueError(f"allocation keys and CIDRs must be strings, got {name!r}: {cidr!r}")
        items.append((name, ipaddress.ip_network(cidr, strict=True)))
    overlaps = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][1].overlaps(items[j][1]):
                overlaps.append({"site_a": items[i][0], "cidr_a": str(items[i][1]), "site_b": items[j][0], "cidr_b": str(items[j][1])})
    return overlaps


def cloud_egress_annual_cost(monthly_tb: float, internet_per_gb: float = 0.09, direct_connect_per_gb: float = 0.02) -> dict:
    tb = _require_non_neg_finite(monthly_tb, "monthly_tb")
    inet_rate = _require_non_neg_finite(internet_per_gb, "internet_per_gb")
    dx_rate = _require_non_neg_finite(direct_connect_per_gb, "direct_connect_per_gb")
    inet_exact = tb * 1024.0 * inet_rate * 12.0
    dx_exact = tb * 1024.0 * dx_rate * 12.0
    if not (math.isfinite(inet_exact) and math.isfinite(dx_exact)):
        raise ValueError("egress cost calculation overflowed IEEE-754 finite float range")
    return {
        "monthly_egress_tb": tb,
        "internet_egress_annual_usd": round(inet_exact, 2),
        "direct_connect_egress_annual_usd": round(dx_exact, 2),
        "annual_egress_savings_usd": round(inet_exact - dx_exact, 2),
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_CLOUD_MODELER",
        "interconnect_choices": {
            "multi_cloud_enterprise_10g": select_cloud_interconnect(10.0, True, True),
            "single_cloud_low_latency_2g": select_cloud_interconnect(2.0, True, False),
            "dev_test_small_300m": select_cloud_interconnect(0.3, False, False),
        },
        "cloud_egress_trap_50tb_month": cloud_egress_annual_cost(50.0),
        "cidr_overlap_audit": detect_cidr_overlaps({
            "OnPrem_DC": "10.0.0.0/16",
            "AWS_Prod_VPC": "10.10.0.0/16",
            "Acquired_Azure_VNet": "10.0.128.0/17",
        }),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
