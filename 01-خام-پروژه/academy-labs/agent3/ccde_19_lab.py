#!/usr/bin/env python3
"""
Local Mock Lab — ccde_19 (CCDE Capstone Case Study 2: Aria-Telecom Service Provider & 5G Modernization)
Validates the end-to-end HLD for Aria-Telecom (2,000 Metro/Access + 50 Core routers, legacy LDP brownfield
upgrading to Seamless SR-MPLS, EVPN, 5G URLLC/eMBB Flex-Algo slicing, TI-LFA on 2-connected rings within
hardware MSD, and IXP/CDN offload), comparing a rejected flat/forklift anti-pattern against the approved HLD.
No real telecom core or 5G RAN infrastructure is connected.
"""

import json


def validate_aria_telecom_hld(design: dict) -> dict:
    checks = [
        {
            "pillar": "2,000-Router IGP Scale (Unified / Seamless SR-MPLS)",
            "pass": design["max_routers_per_igp_domain"] <= 300 and design["inter_domain_stitching"] == "bgp_lu_unified_sr",
            "note": "Splits 2,000 metro rings into <=300-node IS-IS domains stitched end-to-end via BGP-LU / SR-MPLS",
        },
        {
            "pillar": "5G Network Slicing (URLLC Low-Delay vs eMBB High-BW)",
            "pass": design["flex_algo_slices"] >= 2 and design["tilfa_enabled"] and design["rings_two_connected_within_msd"],
            "note": "Flex-Algo 128 (Min-Delay/TWAMP) + Flex-Algo 129 (IGP/BW) + TI-LFA (<50ms target on 2-connected rings within MSD)",
        },
        {
            "pillar": "Unified L2/L3 Service Layer (EVPN + L3VPN over BGP-Free Core)",
            "pass": design["service_plane"] == "evpn_plus_l3vpn_bgp_free_core",
            "note": "Replaces legacy VPLS/Pseudowire sprawl with unified BGP EVPN + L3VPN; P-routers stay BGP-Free",
        },
        {
            "pillar": "Zero-Downtime Brownfield Migration (LDP -> SR-MPLS)",
            "pass": design["migration_mechanism"] == "phased_srms_coexistence",
            "note": "SR Mapping Server (RFC 8661) enables ring-by-ring migration without forklift outage for 5M subscribers",
        },
        {
            "pillar": "Carrier Security & Peering Economics (MANRS + IXP/CDN)",
            "pass": design["rpki_and_flowspec"] and design["ixp_cdn_offload_pct"] >= 60,
            "note": "RPKI ROV + FlowSpec/Scrubbing + >=60% IXP/CDN offload protects core & improves transit margin",
        },
    ]
    return {
        "case_study": "Aria-Telecom (2,000 Metro + 50 Core Routers | 5G Modernization)",
        "all_pillars_validated": all(c["pass"] for c in checks),
        "pillars": checks,
    }


def main() -> None:
    rejected_flat_forklift = {
        "max_routers_per_igp_domain": 2050,
        "inter_domain_stitching": "single_flat_igp",
        "flex_algo_slices": 1,
        "tilfa_enabled": True,
        "rings_two_connected_within_msd": False,
        "service_plane": "legacy_vpls_plus_bgp_in_core",
        "migration_mechanism": "overnight_forklift_cutover",
        "rpki_and_flowspec": False,
        "ixp_cdn_offload_pct": 15,
    }
    approved_aria_hld = {
        "max_routers_per_igp_domain": 200,
        "inter_domain_stitching": "bgp_lu_unified_sr",
        "flex_algo_slices": 2,
        "tilfa_enabled": True,
        "rings_two_connected_within_msd": True,
        "service_plane": "evpn_plus_l3vpn_bgp_free_core",
        "migration_mechanism": "phased_srms_coexistence",
        "rpki_and_flowspec": True,
        "ixp_cdn_offload_pct": 65,
    }
    report = {
        "mode": "LOCAL_MOCK_CCDE_CAPSTONE_ARIA_TELECOM",
        "rejected_flat_forklift_proposal": validate_aria_telecom_hld(rejected_flat_forklift),
        "approved_hld_validation": validate_aria_telecom_hld(approved_aria_hld),
    }
    assert report["rejected_flat_forklift_proposal"]["all_pillars_validated"] is False
    assert report["approved_hld_validation"]["all_pillars_validated"] is True
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
