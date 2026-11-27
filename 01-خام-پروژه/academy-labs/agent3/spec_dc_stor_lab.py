#!/usr/bin/env python3
"""
Local Mock Lab — spec_dc_stor (Data Center Storage Networking: FC SAN, VSAN, Zoning, NPIV & FCoE DCB)
Simulates Fibre Channel Single-Initiator Zoning, VSAN isolation, NPIV virtual WWPN login,
and FCoE lossless Ethernet (DCB: PFC + ETS + Jumbo MTU) readiness checks.
No real Cisco MDS SAN switch or storage array is connected.
"""

import json


def evaluate_fc_access(initiator: dict, target: dict, zones: list[dict]) -> dict:
    if initiator["vsan"] != target["vsan"]:
        return {
            "allowed": False,
            "reason": f"VSAN mismatch ({initiator['vsan']} != {target['vsan']}) — hard L2 fabric isolation",
        }
    for zone in zones:
        if zone["vsan"] != initiator["vsan"]:
            continue
        members = set(zone["members"])
        if initiator["wwpn"] in members and target["wwpn"] in members:
            init_count = sum(1 for m in members if m.startswith("20:00:00:11"))
            best_practice = init_count == 1
            return {
                "allowed": True,
                "zone": zone["name"],
                "single_initiator_best_practice": best_practice,
                "warning": None if best_practice else "Multiple initiators share one zone (RSCN blast risk)",
            }
    return {"allowed": False, "reason": "No active zoneset entry pairs this initiator and target WWPN"}


def check_fcoe_dcb_readiness(link: dict) -> dict:
    issues = []
    if not link.get("pfc_cos3_enabled"):
        issues.append("PFC (802.1Qbb) missing on CoS 3 — frames will drop under congestion")
    if not link.get("ets_enabled"):
        issues.append("ETS (802.1Qaz) missing — storage bandwidth not guaranteed")
    if link.get("mtu", 1500) < 2240:
        issues.append(f"MTU {link.get('mtu')} too small for 2112B FC payload + FCoE headers (need >=2240 / 9216)")
    return {"link": link["name"], "lossless_ready": len(issues) == 0, "issues": issues}


def main() -> None:
    zones = [
        {
            "name": "Z_ESXI01_VMAX_P1",
            "vsan": 100,
            "members": ["20:00:00:11:aa:01:00:01", "50:00:09:70:00:01:00:01"],
        },
        {
            "name": "Z_VM_SQL_NPIV_VMAX_P1",
            "vsan": 100,
            "members": ["20:00:00:11:ff:99:00:01", "50:00:09:70:00:01:00:01"],
        },
    ]
    esxi01_fabric_a = {"name": "ESXi-01-HBA0", "vsan": 100, "wwpn": "20:00:00:11:aa:01:00:01"}
    esxi01_fabric_b = {"name": "ESXi-01-HBA1", "vsan": 200, "wwpn": "20:00:00:11:aa:01:00:02"}
    vm_sql_npiv = {"name": "VM-SQL-vHBA (NPIV)", "vsan": 100, "wwpn": "20:00:00:11:ff:99:00:01"}
    storage_a = {"name": "Storage-Array-PortA", "vsan": 100, "wwpn": "50:00:09:70:00:01:00:01"}

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_MDS_OR_SAN_HARDWARE",
        "fc_zoning_checks": {
            "fabric_a_single_initiator": evaluate_fc_access(esxi01_fabric_a, storage_a, zones),
            "cross_vsan_blocked": evaluate_fc_access(esxi01_fabric_b, storage_a, zones),
            "npiv_vm_direct_lun": evaluate_fc_access(vm_sql_npiv, storage_a, zones),
        },
        "fcoe_dcb_checks": [
            check_fcoe_dcb_readiness({"name": "Eth1/1-Bad", "pfc_cos3_enabled": False, "ets_enabled": True, "mtu": 1500}),
            check_fcoe_dcb_readiness({"name": "Eth1/2-Good", "pfc_cos3_enabled": True, "ets_enabled": True, "mtu": 9216}),
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
