#!/usr/bin/env python3
"""
Local Mock Lab — spec_dc_stor (Data Center Storage Networking: FC SAN, VSAN, Zoning, NPIV & FCoE DCB)
Simulates Fibre Channel Single-Initiator Zoning (using explicit role registry rather than hardcoded WWPN
OUI prefixes), VSAN isolation, NPIV virtual WWPN login, and FCoE lossless Ethernet (DCB: PFC + ETS + Jumbo MTU).
No real Cisco MDS SAN switch or storage array is connected.
"""

import json


def evaluate_fc_access(
    initiator: dict,
    target: dict,
    zones: list[dict],
    known_initiator_wwpns: set[str] | None = None,
) -> dict:
    if initiator["vsan"] != target["vsan"]:
        return {
            "allowed": False,
            "reason": f"VSAN mismatch ({initiator['vsan']} != {target['vsan']}) — hard L2 fabric isolation",
        }
    initiator_registry = set(known_initiator_wwpns) if known_initiator_wwpns is not None else {initiator["wwpn"]}
    initiator_registry.add(initiator["wwpn"])

    for zone in zones:
        if zone["vsan"] != initiator["vsan"]:
            continue
        members = set(zone["members"])
        if initiator["wwpn"] in members and target["wwpn"] in members:
            init_count = sum(1 for m in members if m in initiator_registry)
            best_practice = init_count == 1
            return {
                "allowed": True,
                "zone": zone["name"],
                "initiators_in_zone": init_count,
                "single_initiator_best_practice": best_practice,
                "warning": None if best_practice else f"{init_count} initiators share one zone (RSCN blast risk)",
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
    esxi01_fabric_a = {"name": "ESXi-01-HBA0", "vsan": 100, "wwpn": "20:00:00:11:aa:01:00:01"}
    esxi02_qlogic = {"name": "ESXi-02-QLogic-HBA0", "vsan": 100, "wwpn": "21:00:00:24:ff:02:00:01"}
    esxi01_fabric_b = {"name": "ESXi-01-HBA1", "vsan": 200, "wwpn": "20:00:00:11:aa:01:00:02"}
    vm_sql_npiv = {"name": "VM-SQL-vHBA (NPIV)", "vsan": 100, "wwpn": "20:00:00:11:ff:99:00:01"}
    storage_a = {"name": "Storage-Array-PortA", "vsan": 100, "wwpn": "50:00:09:70:00:01:00:01"}

    known_initiators = {
        esxi01_fabric_a["wwpn"],
        esxi02_qlogic["wwpn"],
        esxi01_fabric_b["wwpn"],
        vm_sql_npiv["wwpn"],
    }

    zones = [
        {
            "name": "Z_ESXI01_VMAX_P1",
            "vsan": 100,
            "members": [esxi01_fabric_a["wwpn"], storage_a["wwpn"]],
        },
        {
            "name": "Z_VM_SQL_NPIV_VMAX_P1",
            "vsan": 100,
            "members": [vm_sql_npiv["wwpn"], storage_a["wwpn"]],
        },
    ]
    bad_multi_init_zones = [
        {
            "name": "Z_LEGACY_ALL_ESXI_VMAX",
            "vsan": 100,
            "members": [esxi01_fabric_a["wwpn"], esxi02_qlogic["wwpn"], storage_a["wwpn"]],
        }
    ]

    ok_single = evaluate_fc_access(esxi01_fabric_a, storage_a, zones, known_initiators)
    blocked_vsan = evaluate_fc_access(esxi01_fabric_b, storage_a, zones, known_initiators)
    ok_npiv = evaluate_fc_access(vm_sql_npiv, storage_a, zones, known_initiators)
    bad_multi_init = evaluate_fc_access(esxi02_qlogic, storage_a, bad_multi_init_zones, known_initiators)
    dcb_bad = check_fcoe_dcb_readiness({"name": "Eth1/1-Bad", "pfc_cos3_enabled": False, "ets_enabled": True, "mtu": 1500})
    dcb_good = check_fcoe_dcb_readiness({"name": "Eth1/2-Good", "pfc_cos3_enabled": True, "ets_enabled": True, "mtu": 9216})

    assert ok_single["allowed"] is True and ok_single["single_initiator_best_practice"] is True
    assert blocked_vsan["allowed"] is False
    assert ok_npiv["allowed"] is True and ok_npiv["single_initiator_best_practice"] is True
    assert bad_multi_init["allowed"] is True and bad_multi_init["single_initiator_best_practice"] is False
    assert dcb_bad["lossless_ready"] is False and dcb_good["lossless_ready"] is True

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_MDS_OR_SAN_HARDWARE",
        "fc_zoning_checks": {
            "fabric_a_single_initiator": ok_single,
            "cross_vsan_blocked": blocked_vsan,
            "npiv_vm_direct_lun": ok_npiv,
            "multi_initiator_antipattern_flagged": bad_multi_init,
        },
        "fcoe_dcb_checks": [dcb_bad, dcb_good],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
