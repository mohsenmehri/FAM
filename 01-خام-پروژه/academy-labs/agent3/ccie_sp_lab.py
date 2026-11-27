#!/usr/bin/env python3
"""
Local Mock Lab — ccie_sp (CCIE Service Provider v5.1: Bottom-Up MPLS/SR L3VPN & Inter-AS Option B Debugger)
Simulates bottom-up Service Provider lab troubleshooting:
Layer 1: PE Loopback /32 IGP reachability, Layer 2: SR-MPLS Prefix-SID collision check,
Layer 3: MP-BGP VPNv4 Route-Target Import/Export matching + IOS-XR eBGP RPL policy check.
No real Cisco IOS-XR / IOS-XE router or carrier core is connected.
"""

import json


def debug_mpls_l3vpn_bottom_up(pe1: dict, pe2: dict) -> dict:
    steps = []
    # 1. Underlay /32 Loopback reachability
    if not (pe1["igp_lo0_reachable"] and pe2["igp_lo0_reachable"]):
        return {"healthy": False, "failed_layer": "IGP_UNDERLAY", "fix": "Verify IS-IS/OSPF /32 Loopback advertisement"}
    steps.append("1_IGP_LOOPBACK_32_OK")

    # 2. SR-MPLS Prefix-SID uniqueness
    if pe1["prefix_sid_index"] == pe2["prefix_sid_index"]:
        return {
            "healthy": False,
            "failed_layer": "SR_MPLS_LABEL_PLANE",
            "fix": f"Prefix-SID Collision! Both PE1 and PE2 use index {pe1['prefix_sid_index']}",
        }
    steps.append("2_SR_MPLS_PREFIX_SID_UNIQUE_OK")

    # 3. MP-BGP VPNv4 Route-Target match
    rt_overlap = set(pe1["rt_export"]) & set(pe2["rt_import"])
    if not rt_overlap:
        return {
            "healthy": False,
            "failed_layer": "MP_BGP_VPNV4_RT_MISMATCH",
            "fix": f"PE1 exports {pe1['rt_export']} but PE2 imports {pe2['rt_import']} — no overlap!",
        }
    steps.append(f"3_VPNV4_RT_MATCH_OK ({sorted(rt_overlap)})")

    # 4. IOS-XR PE-CE eBGP RPL Policy attached (RFC 8212)
    if not (pe1["xr_ebgp_rpl_attached"] and pe2["xr_ebgp_rpl_attached"]):
        return {
            "healthy": False,
            "failed_layer": "IOS_XR_EBGP_RPL_MISSING",
            "fix": "Attach inbound & outbound RPL route-policy to IOS-XR PE-CE eBGP neighbor!",
        }
    steps.append("4_IOS_XR_PE_CE_RPL_OK")
    return {"healthy": True, "verified_layers": steps}


def main() -> None:
    broken_pe1 = {"igp_lo0_reachable": True, "prefix_sid_index": 1, "rt_export": ["65000:100"], "xr_ebgp_rpl_attached": True}
    broken_pe2 = {"igp_lo0_reachable": True, "prefix_sid_index": 2, "rt_import": ["65000:200"], "xr_ebgp_rpl_attached": False}
    fixed_pe2 = {"igp_lo0_reachable": True, "prefix_sid_index": 2, "rt_import": ["65000:100"], "xr_ebgp_rpl_attached": True}

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_IOS_XR_OR_MPLS_CORE",
        "before_fix_diagnosis": debug_mpls_l3vpn_bottom_up(broken_pe1, broken_pe2),
        "after_fix_verification": debug_mpls_l3vpn_bottom_up(broken_pe1, fixed_pe2),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
