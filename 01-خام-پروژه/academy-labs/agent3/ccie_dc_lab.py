#!/usr/bin/env python3
"""
Local Mock Lab — ccie_dc (CCIE Data Center v3.1: 5-Link ACI Debug Chain, NX-OS VXLAN EVPN & MDS SAN Check)
Simulates the 5-step Cisco ACI EPG-to-EPG troubleshooting chain, NX-OS BGP EVPN / NVE VTEP
control/data plane verification, and MDS Fibre Channel FLOGI + active zoneset health check.
No real Cisco APIC, Nexus 9000, UCS, or MDS 9000 hardware is connected.
"""

import ipaddress
import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def _require_dict_bool(d: dict, key: str) -> bool:
    if key not in d:
        raise ValueError(f"Missing required boolean key '{key}'")
    return _require_bool(d[key], key)


def verify_aci_5_link_chain(fabric: dict) -> dict:
    if not isinstance(fabric, dict):
        raise ValueError(f"fabric must be a dict, got {type(fabric).__name__}")
    aaep = _require_dict_bool(fabric, "aaep_bound_to_domain")
    vlan_ok = _require_dict_bool(fabric, "vlan_in_domain_pool")
    bd_uc = _require_dict_bool(fabric, "bd_unicast_routing")
    bd_sub = _require_dict_bool(fabric, "bd_has_subnet")
    bd_vrf = _require_dict_bool(fabric, "bd_vrf_attached")
    contract_ok = _require_dict_bool(fabric, "contract_applied_both_sides")
    checks = [
        ("1_aaep_domain_binding", aaep, "Bind AAEP to Physical/VMM Domain"),
        ("2_vlan_pool_encap_match", vlan_ok, "Add static encap VLAN to Domain VLAN Pool"),
        ("3_bd_unicast_and_subnet", bd_uc and bd_sub, "Enable Unicast Routing and define Subnet on BD"),
        ("4_bd_linked_to_vrf", bd_vrf, "Attach Bridge Domain to target VRF"),
        ("5_contract_direction_scope", contract_ok, "Apply Contract as Provider/Consumer with matching Scope"),
    ]
    failed = [{"step": name, "fix": fix} for name, ok, fix in checks if not ok]
    return {"epg_ping_ok": len(failed) == 0, "failed_links": failed}


def verify_nxos_evpn_vxlan(bgp_evpn_up: bool, nve_peers: list[str], mac_in_l2route: bool, vni: int) -> dict:
    evpn_up = _require_bool(bgp_evpn_up, "bgp_evpn_up")
    mac_ok = _require_bool(mac_in_l2route, "mac_in_l2route")
    if isinstance(vni, bool) or not isinstance(vni, int) or not (1 <= vni <= 16_777_215):
        raise ValueError(f"vni must be a 24-bit VXLAN VNI int in [1, 16777215] (RFC 7348), got {vni!r}")
    if not isinstance(nve_peers, list):
        raise ValueError(f"nve_peers must be a list of IP strings, got {type(nve_peers).__name__}")
    validated_peers = []
    for p in nve_peers:
        if not isinstance(p, str):
            raise ValueError(f"nve_peer must be an IP string, got {p!r}")
        validated_peers.append(str(ipaddress.ip_address(p)))
    ok = evpn_up and len(validated_peers) > 0 and mac_ok
    return {
        "vni": vni,
        "bgp_l2vpn_evpn": "Established" if evpn_up else "Idle",
        "nve1_peers": validated_peers,
        "l2route_mac_learned": mac_ok,
        "east_west_forwarding_ready": ok,
    }


def main() -> None:
    broken_aci = {
        "aaep_bound_to_domain": True,
        "vlan_in_domain_pool": False,
        "bd_unicast_routing": True,
        "bd_has_subnet": True,
        "bd_vrf_attached": True,
        "contract_applied_both_sides": False,
    }
    fixed_aci = {k: True for k in broken_aci}
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_APIC_NEXUS_OR_MDS_HARDWARE",
        "aci_5_link_debug_before": verify_aci_5_link_chain(broken_aci),
        "aci_5_link_debug_after": verify_aci_5_link_chain(fixed_aci),
        "nxos_vxlan_evpn_check": verify_nxos_evpn_vxlan(
            bgp_evpn_up=True,
            nve_peers=["10.255.0.11", "10.255.0.12"],
            mac_in_l2route=True,
            vni=10010,
        ),
        "mds_san_flogi_zoneset": {
            "vsan": 100,
            "flogi_entries": 2,
            "zoneset_activated": True,
            "status": "READY",
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
