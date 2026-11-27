#!/usr/bin/env python3
"""
Local Mock Lab — ccde_19 (CCDE Capstone Case Study 2: Aria-Telecom Service Provider & 5G Modernization)
Validates the end-to-end HLD for Aria-Telecom (2,000 Metro/Access + 50 Core routers, legacy LDP brownfield
upgrading to Seamless SR-MPLS, EVPN, 5G URLLC/eMBB Flex-Algo slicing, TI-LFA on 2-connected rings within
hardware MSD, and IXP/CDN offload), comparing a rejected flat/forklift anti-pattern against the approved HLD
with dynamic pass/fail diagnostic notes on every pillar.
No real telecom core or 5G RAN infrastructure is connected.
"""

import json


def validate_aria_telecom_hld(design: dict) -> dict:
    igp_ok = design["max_routers_per_igp_domain"] <= 300 and design["inter_domain_stitching"] == "bgp_lu_unified_sr"
    slice_ok = design["flex_algo_slices"] >= 2 and design["tilfa_enabled"] and design["rings_two_connected_within_msd"]
    service_ok = design["service_plane"] == "evpn_plus_l3vpn_bgp_free_core"
    migration_ok = design["migration_mechanism"] == "phased_srms_coexistence"
    sec_peering_ok = design["rpki_and_flowspec"] and design["ixp_cdn_offload_pct"] >= 60

    checks = [
        {
            "pillar": "2,000-Router IGP Scale (Unified / Seamless SR-MPLS)",
            "pass": igp_ok,
            "note": (
                "Splits 2,000 metro rings into <=300-node IS-IS domains stitched end-to-end via BGP-LU / SR-MPLS."
                if igp_ok
                else f"REJECTED: {design['max_routers_per_igp_domain']}-node domain with '{design['inter_domain_stitching']}' risks LSDB/SPF instability."
            ),
        },
        {
            "pillar": "5G Network Slicing (URLLC Low-Delay vs eMBB High-BW)",
            "pass": slice_ok,
            "note": (
                "Flex-Algo 128 (Min-Delay/TWAMP) + Flex-Algo 129 (IGP/BW) + TI-LFA (<50ms target on 2-connected rings within MSD)."
                if slice_ok
                else "REJECTED: requires >=2 Flex-Algo slices, TI-LFA enabled, and 2-connected rings within hardware MSD."
            ),
        },
        {
            "pillar": "Unified L2/L3 Service Layer (EVPN + L3VPN over BGP-Free Core)",
            "pass": service_ok,
            "note": (
                "Replaces legacy VPLS/Pseudowire sprawl with unified BGP EVPN + L3VPN; P-routers stay BGP-Free."
                if service_ok
                else f"REJECTED: service plane '{design['service_plane']}' retains legacy VPLS/core-BGP complexity."
            ),
        },
        {
            "pillar": "Minimal-Downtime Phased Brownfield Migration (LDP -> SR-MPLS)",
            "pass": migration_ok,
            "note": (
                "SR Mapping Server (RFC 8661) enables phased ring-by-ring coexistence and rollback windows (subject to lab validation and maintenance controls)."
                if migration_ok
                else f"REJECTED: '{design['migration_mechanism']}' risks large-scale subscriber outage; use phased SRMS coexistence."
            ),
        },
        {
            "pillar": "Carrier Security & Peering Economics (MANRS + IXP/CDN)",
            "pass": sec_peering_ok,
            "note": (
                f"RPKI ROV + FlowSpec/Scrubbing + {design['ixp_cdn_offload_pct']}% IXP/CDN offload target protects core and reduces transit dependency."
                if sec_peering_ok
                else f"REJECTED: requires RPKI/FlowSpec enabled and >=60% IXP/CDN offload target (got {design['ixp_cdn_offload_pct']}%)."
            ),
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
    assert all(p["note"].startswith("REJECTED:") for p in report["rejected_flat_forklift_proposal"]["pillars"])
    assert report["approved_hld_validation"]["all_pillars_validated"] is True
    assert all(not p["note"].startswith("REJECTED:") for p in report["approved_hld_validation"]["pillars"])
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
