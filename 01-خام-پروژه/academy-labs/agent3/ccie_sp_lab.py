#!/usr/bin/env python3
"""
Local Mock Lab — ccie_sp (CCIE Service Provider v5.1: Bottom-Up MPLS/SR L3VPN & Inter-AS Option B Debugger)
Simulates bottom-up Service Provider lab troubleshooting:
Layer 1: PE Loopback /32 IGP reachability, Layer 2: SR-MPLS Prefix-SID collision check,
Layer 3: MP-BGP VPNv4 Route-Target Import/Export matching + IOS-XR eBGP RPL policy check.
Strict validation rejects non-bool flags (e.g. "False", 0, 1, None) and invalid Prefix-SID indices.
No real Cisco IOS-XR / IOS-XE router or carrier core is connected.
"""

import json


def _require_bool(mapping: dict, key: str, who: str) -> bool:
    if key not in mapping:
        raise ValueError(f"{who} missing required boolean key '{key}'")
    val = mapping[key]
    if not isinstance(val, bool):
        raise ValueError(f"{who}.{key} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_prefix_sid(mapping: dict, who: str) -> int:
    if "prefix_sid_index" not in mapping:
        raise ValueError(f"{who} missing required 'prefix_sid_index'")
    val = mapping["prefix_sid_index"]
    if isinstance(val, bool) or not isinstance(val, int) or val < 0:
        raise ValueError(f"{who}.prefix_sid_index must be a non-negative int (not bool), got {val!r}")
    return val


def debug_mpls_l3vpn_bottom_up(pe1: dict, pe2: dict) -> dict:
    pe1_igp = _require_bool(pe1, "igp_lo0_reachable", "pe1")
    pe2_igp = _require_bool(pe2, "igp_lo0_reachable", "pe2")
    pe1_sid = _require_prefix_sid(pe1, "pe1")
    pe2_sid = _require_prefix_sid(pe2, "pe2")
    pe1_rpl = _require_bool(pe1, "xr_ebgp_rpl_attached", "pe1")
    pe2_rpl = _require_bool(pe2, "xr_ebgp_rpl_attached", "pe2")

    steps = []
    # 1. Underlay /32 Loopback reachability
    if not (pe1_igp and pe2_igp):
        return {"healthy": False, "failed_layer": "IGP_UNDERLAY", "fix": "Verify IS-IS/OSPF /32 Loopback advertisement"}
    steps.append("1_IGP_LOOPBACK_32_OK")

    # 2. SR-MPLS Prefix-SID uniqueness
    if pe1_sid == pe2_sid:
        return {
            "healthy": False,
            "failed_layer": "SR_MPLS_LABEL_PLANE",
            "fix": f"Prefix-SID Collision! Both PE1 and PE2 use index {pe1_sid}",
        }
    steps.append("2_SR_MPLS_PREFIX_SID_UNIQUE_OK")

    # 3. MP-BGP VPNv4 Route-Target match
    rt_export = pe1.get("rt_export")
    rt_import = pe2.get("rt_import")
    if not isinstance(rt_export, (list, set, tuple)) or not isinstance(rt_import, (list, set, tuple)):
        raise ValueError("pe1.rt_export and pe2.rt_import must be iterables of RT strings")
    rt_overlap = set(rt_export) & set(rt_import)
    if not rt_overlap:
        return {
            "healthy": False,
            "failed_layer": "MP_BGP_VPNV4_RT_MISMATCH",
            "fix": f"PE1 exports {list(rt_export)} but PE2 imports {list(rt_import)} — no overlap!",
        }
    steps.append(f"3_VPNV4_RT_MATCH_OK ({sorted(rt_overlap)})")

    # 4. IOS-XR PE-CE eBGP RPL Policy attached (RFC 8212)
    if not (pe1_rpl and pe2_rpl):
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

    before = debug_mpls_l3vpn_bottom_up(broken_pe1, broken_pe2)
    after = debug_mpls_l3vpn_bottom_up(broken_pe1, fixed_pe2)
    assert before["healthy"] is False and before["failed_layer"] == "MP_BGP_VPNV4_RT_MISMATCH"
    assert after["healthy"] is True and len(after["verified_layers"]) == 4

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_IOS_XR_OR_MPLS_CORE",
        "before_fix_diagnosis": before,
        "after_fix_verification": after,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
