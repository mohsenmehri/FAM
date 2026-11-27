#!/usr/bin/env python3
"""
Local Mock Lab — ccde_07 (CCDE Cloud Connectivity: Direct Connect vs VPN, Colo Hub & Hybrid Cloud Trap Auditor)
Evaluates Direct Connect/ExpressRoute vs IPsec VPN vs Colocation Cloud Exchange Hub,
calculates annual cloud egress cost impact, and checks for RFC 1918 CIDR overlaps across VPCs/On-Prem.
No real AWS/Azure/GCP accounts or Equinix Colocation exchanges are connected.
"""

import ipaddress
import json


def select_cloud_interconnect(bandwidth_gbps: float, needs_deterministic_latency: bool, multi_cloud: bool) -> dict:
    if multi_cloud and bandwidth_gbps >= 5.0:
        return {
            "recommended": "Colocation Cloud Exchange Hub (e.g. Equinix Fabric) -> Private Virtual Cross-Connects to AWS/Azure/GCP",
            "reason": "Single high-speed aggregation hub avoids hairpinned cloud-to-cloud traffic and lowers Direct Connect egress fees",
        }
    if needs_deterministic_latency or bandwidth_gbps > 1.25:
        return {
            "recommended": "Redundant Dedicated Direct Connect / ExpressRoute (Dual Diversely Routed Locations) + IPsec Backup",
            "reason": "Bypasses public internet jitter, exceeds classic 1.25Gbps single-tunnel IPsec throughput (without ECMP/higher SKUs), and typically lowers cloud egress rates (provider/region/tier-dependent)",
        }
    return {
        "recommended": "Redundant Site-to-Site IPsec VPN (BGP ECMP) over Dual ISP",
        "reason": "Fastest deployment and lowest OpEx for small workloads without strict latency SLA",
    }


def detect_cidr_overlaps(allocations: dict[str, str]) -> list[dict]:
    items = [(name, ipaddress.ip_network(cidr)) for name, cidr in allocations.items()]
    overlaps = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][1].overlaps(items[j][1]):
                overlaps.append({"site_a": items[i][0], "cidr_a": str(items[i][1]), "site_b": items[j][0], "cidr_b": str(items[j][1])})
    return overlaps


def cloud_egress_annual_cost(monthly_tb: float, internet_per_gb: float = 0.09, direct_connect_per_gb: float = 0.02) -> dict:
    inet_yr = round(monthly_tb * 1024 * internet_per_gb * 12, 2)
    dx_yr = round(monthly_tb * 1024 * direct_connect_per_gb * 12, 2)
    return {"monthly_egress_tb": monthly_tb, "internet_egress_annual_usd": inet_yr, "direct_connect_egress_annual_usd": dx_yr, "annual_egress_savings_usd": round(inet_yr - dx_yr, 2)}


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
