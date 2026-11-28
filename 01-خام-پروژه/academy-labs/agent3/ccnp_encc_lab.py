"""Local Python Mock for ccnp_encc (Cloud Connectivity: Overlapping CIDR Audit & BGP Prefix Limit Guard).

Educational local model only — no live AWS Transit Gateway, AWS Direct Connect,
Azure Virtual WAN, ExpressRoute, or IPsec tunnel is contacted.
Models:
1. Multi-VPC / On-Premises CIDR overlap detector (detecting overlapping subnets that require
   summarization, re-IPing, or NAT at the cloud edge!).
2. Cloud BGP prefix-limit guard (illustrative check against provider BGP route limits such as
   100 routes on AWS Direct Connect / VGW BGP sessions, reminding engineers to summarize).
"""
from __future__ import annotations

import ipaddress


def audit_cloud_cidr_overlaps(allocations: list[dict[str, str]]) -> dict[str, object]:
    """Detect IPv4 CIDR overlaps across on-prem sites and cloud VPC/VNets."""
    if not isinstance(allocations, list) or len(allocations) < 2:
        raise ValueError("allocations must be a list of at least 2 {'name', 'cidr'} dicts")
    parsed: list[tuple[str, ipaddress.IPv4Network]] = []
    for item in allocations:
        if not isinstance(item, dict):
            raise ValueError("each allocation must be a dict")
        name = str(item.get("name", "")).strip()
        if not name:
            raise ValueError("allocation name must be non-empty")
        net = ipaddress.IPv4Network(str(item["cidr"]), strict=True)
        parsed.append((name, net))

    overlaps: list[dict[str, str]] = []
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            n1, net1 = parsed[i]
            n2, net2 = parsed[j]
            if net1.overlaps(net2):
                overlaps.append({"a": f"{n1} ({net1})", "b": f"{n2} ({net2})"})

    return {
        "model_checks_ok": len(overlaps) == 0,
        "overlap_count": len(overlaps),
        "overlaps": overlaps,
        "remediation_hint": "Use non-overlapping IPAM blocks or explicit NAT/translation gateway for overlapping VPCs." if overlaps else "No CIDR overlaps detected in supplied list.",
    }


def check_cloud_bgp_prefix_limit(advertised_prefixes: int, provider_limit: int = 100) -> dict[str, object]:
    """Check whether advertised BGP prefix count stays safely below a cloud gateway limit."""
    if isinstance(advertised_prefixes, bool) or not isinstance(advertised_prefixes, int) or advertised_prefixes < 0:
        raise ValueError("advertised_prefixes must be a non-negative int")
    if isinstance(provider_limit, bool) or not isinstance(provider_limit, int) or provider_limit <= 0:
        raise ValueError("provider_limit must be a positive int")
    exceeds = advertised_prefixes > provider_limit
    return {
        "advertised_prefixes": advertised_prefixes,
        "provider_limit": provider_limit,
        "bgp_session_reset_risk": exceeds,
        "action": "SUMMARIZE_PREFIXES_BEFORE_ADVERTISING" if exceeds else "WITHIN_MODEL_LIMIT",
        "model_scope_note": "Illustrative prefix-limit check only; verify current AWS/Azure quota docs for exact service tier limits.",
    }


def main() -> None:
    print("Local Python Mock only — no live AWS/Azure cloud gateway or BGP session is contacted.")
    audit = audit_cloud_cidr_overlaps([
        {"name": "OnPrem-HQ", "cidr": "10.10.0.0/16"},
        {"name": "AWS-Prod-VPC", "cidr": "10.20.0.0/16"},
        {"name": "Acquired-Azure-VNet", "cidr": "10.10.50.0/24"},
    ])
    assert audit["model_checks_ok"] is False and audit["overlap_count"] == 1
    lim = check_cloud_bgp_prefix_limit(135, provider_limit=100)
    assert lim["bgp_session_reset_risk"] is True
    print("Cloud CIDR overlap audit:", audit)
    print("Cloud BGP prefix limit check:", lim)


if __name__ == "__main__":
    main()
