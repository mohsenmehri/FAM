#!/usr/bin/env python3
"""
FAM Academy Lab — spec_dc_aci: Cisco ACI Policy Model (Tenant->VRF->BD->EPG->
Contract), Headless APIC Operation & Multi-Site vs Multi-Pod Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of ACI VRF Enforced
whitelist policy evaluation and APIC control/data plane separation. No live APIC.
"""

from __future__ import annotations

import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def evaluate_aci_traffic(
    src_epg: str,
    dst_epg: str,
    port: int,
    vrf_enforced: bool,
    contracts: list[dict],
) -> dict:
    if not isinstance(src_epg, str) or not src_epg.strip() or not isinstance(dst_epg, str) or not dst_epg.strip():
        raise ValueError("src_epg and dst_epg must be non-empty strings")
    if isinstance(port, bool) or not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError(f"port must be an int in [1, 65535] (not bool), got {port!r}")
    enforced = _require_bool(vrf_enforced, "vrf_enforced")
    if not isinstance(contracts, list):
        raise ValueError("contracts must be a list of dicts")
    if src_epg == dst_epg:
        return {"action": "PERMIT", "reason": "Intra-EPG traffic permitted by default"}
    if not enforced:
        return {"action": "PERMIT", "reason": "VRF in Unenforced mode (no contract required)"}
    for c in contracts:
        if c["consumer"] == src_epg and c["provider"] == dst_epg and port in c["tcp_ports"]:
            return {"action": "PERMIT", "reason": f"Matched Contract {c['name']} on TCP/{port}"}
    return {"action": "DROP", "reason": "VRF Enforced default whitelist: no matching Contract"}


def apic_offline_impact(all_apics_down: bool) -> dict:
    down = _require_bool(all_apics_down, "all_apics_down")
    if down:
        return {
            "existing_hardware_forwarding": "CONTINUES (Headless Operation on Leaf/Spine)",
            "new_policy_changes": "BLOCKED until APIC quorum restored",
        }
    return {"existing_hardware_forwarding": "NORMAL", "new_policy_changes": "ALLOWED"}


def main() -> None:
    contracts = [{"name": "WEB_TO_APP", "consumer": "EPG-WEB", "provider": "EPG-APP", "tcp_ports": [8443]}]
    # Same BD/Subnet, different EPGs in Enforced VRF -> DROP without matching contract!
    drop_db = evaluate_aci_traffic("EPG-WEB", "EPG-DB", 5432, vrf_enforced=True, contracts=contracts)
    permit_app = evaluate_aci_traffic("EPG-WEB", "EPG-APP", 8443, vrf_enforced=True, contracts=contracts)
    headless = apic_offline_impact(all_apics_down=True)

    assert drop_db["action"] == "DROP"
    assert permit_app["action"] == "PERMIT"
    assert "Headless" in headless["existing_hardware_forwarding"]

    print("=== spec_dc_aci ACI EPG/Contract & Headless Operation Mock ===")
    print(json.dumps({
        "web_to_db_no_contract": drop_db,
        "web_to_app_with_contract": permit_app,
        "all_3_apics_offline": headless,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
