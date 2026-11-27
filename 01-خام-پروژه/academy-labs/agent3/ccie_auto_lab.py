#!/usr/bin/env python3
"""
Local Mock Lab — ccie_auto (CCIE Automation / DevNet Expert: NSO FASTMAP Idempotency, Paginated API & pyATS Gate)
Simulates (1) Cisco NSO FASTMAP service lifecycle (dry-run native diff, idempotent re-apply,
and atomic rollback with zero residual config), (2) REST API pagination collector,
and (3) Post-deployment pyATS-style operational assertion gate.
No real Cisco NSO, GitLab CI, Catalyst Center, or IOS-XE/XR device is connected.
"""

import copy
import json


class MockNSOEngine:
    def __init__(self) -> None:
        self.device_cdb: dict[str, dict] = {"PE1": {"vrfs": {}}, "PE2": {"vrfs": {}}}
        self.services: dict[str, dict] = {}

    def apply_l3vpn_service(self, svc_name: str, vrf: str, rd: str, dry_run: bool = False) -> dict:
        desired = copy.deepcopy(self.device_cdb)
        for dev in ("PE1", "PE2"):
            desired[dev]["vrfs"][vrf] = {"rd": rd, "owner_service": svc_name}
        diff = [
            f"{dev}: + vrf {vrf} rd {rd}"
            for dev in ("PE1", "PE2")
            if self.device_cdb[dev]["vrfs"].get(vrf) != desired[dev]["vrfs"][vrf]
        ]
        if dry_run:
            return {"mode": "commit dry-run outformat native", "native_diff": diff, "changed": len(diff) > 0}
        self.device_cdb = desired
        self.services[svc_name] = {"vrf": vrf, "rd": rd}
        return {"mode": "commit", "native_diff": diff, "changed": len(diff) > 0}

    def delete_l3vpn_service(self, svc_name: str) -> dict:
        svc = self.services.pop(svc_name, None)
        if not svc:
            return {"deleted": False, "residual_vrfs": self.device_cdb}
        vrf = svc["vrf"]
        for dev in ("PE1", "PE2"):
            self.device_cdb[dev]["vrfs"].pop(vrf, None)
        return {"deleted": True, "fastmap_clean": all(len(d["vrfs"]) == 0 for d in self.device_cdb.values()), "device_cdb": self.device_cdb}


def fetch_all_paginated(pages: list[list[str]]) -> list[str]:
    collected = []
    for page in pages:
        collected.extend(page)
    return collected


def main() -> None:
    nso = MockNSOEngine()
    dry = nso.apply_l3vpn_service("CUST-ACME", "VRF_ACME", "65000:101", dry_run=True)
    first_apply = nso.apply_l3vpn_service("CUST-ACME", "VRF_ACME", "65000:101", dry_run=False)
    second_apply = nso.apply_l3vpn_service("CUST-ACME", "VRF_ACME", "65000:101", dry_run=False)
    post_check_ok = all("VRF_ACME" in nso.device_cdb[d]["vrfs"] for d in ("PE1", "PE2"))
    cleanup = nso.delete_l3vpn_service("CUST-ACME")

    devices = fetch_all_paginated([["PE1", "PE2"], ["P1", "P2"], ["LEAF1"]])
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_NSO_OR_LIVE_ROUTERS",
        "nso_fastmap_lifecycle": {
            "1_dry_run_preview": dry,
            "2_first_commit": first_apply,
            "3_second_commit_idempotent": second_apply,
            "4_pyats_post_check_passed": post_check_ok,
            "5_delete_fastmap_zero_residue": cleanup,
        },
        "paginated_inventory_total": len(devices),
        "paginated_inventory_items": devices,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
