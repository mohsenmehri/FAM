#!/usr/bin/env python3
"""
Local Mock Lab — ccie_dc (CCIE Data Center v3.1: 5-Link ACI Debug Chain, NX-OS VXLAN EVPN & MDS SAN Check)
Simulates the 5-step Cisco ACI EPG-to-EPG troubleshooting chain, NX-OS BGP EVPN / NVE VTEP
control/data plane verification, and MDS Fibre Channel FLOGI + active zoneset health check.
No real Cisco APIC, Nexus 9000, UCS, or MDS 9000 hardware is connected.
"""

import json


def verify_aci_5_link_chain(fabric: dict) -> dict:
    checks = [
        ("1_aaep_domain_binding", fabric["aaep_bound_to_domain"], "Bind AAEP to Physical/VMM Domain"),
        ("2_vlan_pool_encap_match", fabric["vlan_in_domain_pool"], "Add static encap VLAN to Domain VLAN Pool"),
        ("3_bd_unicast_and_subnet", fabric["bd_unicast_routing"] and fabric["bd_has_subnet"], "Enable Unicast Routing and define Subnet on BD"),
        ("4_bd_linked_to_vrf", fabric["bd_vrf_attached"], "Attach Bridge Domain to target VRF"),
        ("5_contract_direction_scope", fabric["contract_applied_both_sides"], "Apply Contract as Provider/Consumer with matching Scope"),
    ]
    failed = [{"step": name, "fix": fix} for name, ok, fix in checks if not ok]
    return {"epg_ping_ok": len(failed) == 0, "failed_links": failed}


def verify_nxos_evpn_vxlan(bgp_evpn_up: bool, nve_peers: list[str], mac_in_l2route: bool, vni: int) -> dict:
    ok = bgp_evpn_up and len(nve_peers) > 0 and mac_in_l2route
    return {
        "vni": vni,
        "bgp_l2vpn_evpn": "Established" if bgp_evpn_up else "Idle",
        "nve1_peers": nve_peers,
        "l2route_mac_learned": mac_in_l2route,
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
