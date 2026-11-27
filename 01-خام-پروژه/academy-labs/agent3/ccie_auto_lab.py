#!/usr/bin/env python3
"""
Local Mock Lab — ccie_auto (CCIE Automation / DevNet Expert: NSO FASTMAP Idempotency, Paginated API & pyATS Gate)
Simulates (1) Cisco NSO FASTMAP service lifecycle (dry-run native diff, idempotent re-apply,
and per-service atomic deletion without affecting unrelated services), (2) REST API pagination collector,
and (3) Post-deployment pyATS-style operational assertion gate.
Strict validation rejects non-bool dry_run values and empty service/VRF identifiers.
No real Cisco NSO, GitLab CI, Catalyst Center, or IOS-XE/XR device is connected.
"""

import copy
import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_non_empty_str(val: object, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty str, got {val!r}")
    return val


class MockNSOEngine:
    def __init__(self) -> None:
        self.device_cdb: dict[str, dict] = {"PE1": {"vrfs": {}}, "PE2": {"vrfs": {}}}
        self.services: dict[str, dict] = {}

    def apply_l3vpn_service(self, svc_name: str, vrf: str, rd: str, dry_run: bool = False) -> dict:
        _require_non_empty_str(svc_name, "svc_name")
        _require_non_empty_str(vrf, "vrf")
        _require_non_empty_str(rd, "rd")
        is_dry_run = _require_bool(dry_run, "dry_run")

        desired = copy.deepcopy(self.device_cdb)
        for dev in ("PE1", "PE2"):
            desired[dev]["vrfs"][vrf] = {"rd": rd, "owner_service": svc_name}
        diff = [
            f"{dev}: + vrf {vrf} rd {rd}"
            for dev in ("PE1", "PE2")
            if self.device_cdb[dev]["vrfs"].get(vrf) != desired[dev]["vrfs"][vrf]
        ]
        if is_dry_run:
            return {"mode": "commit dry-run outformat native", "native_diff": diff, "changed": len(diff) > 0}
        self.device_cdb = desired
        self.services[svc_name] = {"vrf": vrf, "rd": rd}
        return {"mode": "commit", "native_diff": diff, "changed": len(diff) > 0}

    def delete_l3vpn_service(self, svc_name: str) -> dict:
        _require_non_empty_str(svc_name, "svc_name")
        svc = self.services.pop(svc_name, None)
        if not svc:
            return {"deleted": False, "residual_vrfs": self.device_cdb}
        vrf = svc["vrf"]
        for dev in ("PE1", "PE2"):
            if self.device_cdb[dev]["vrfs"].get(vrf, {}).get("owner_service") == svc_name:
                self.device_cdb[dev]["vrfs"].pop(vrf, None)
        service_vrf_removed = all(vrf not in d["vrfs"] for d in self.device_cdb.values())
        return {"deleted": True, "fastmap_clean": service_vrf_removed, "device_cdb": self.device_cdb}


def fetch_all_paginated(pages: list[list[str]]) -> list[str]:
    if not isinstance(pages, list):
        raise ValueError("pages must be a list of lists")
    collected = []
    for page in pages:
        if not isinstance(page, list):
            raise ValueError(f"each page must be a list, got {type(page).__name__}")
        collected.extend(page)
    return collected


def main() -> None:
    nso = MockNSOEngine()
    dry = nso.apply_l3vpn_service("CUST-ACME", "VRF_ACME", "65000:101", dry_run=True)
    assert dry["changed"] is True and "VRF_ACME" not in nso.device_cdb["PE1"]["vrfs"]
    first_apply = nso.apply_l3vpn_service("CUST-ACME", "VRF_ACME", "65000:101", dry_run=False)
    assert first_apply["changed"] is True
    second_apply = nso.apply_l3vpn_service("CUST-ACME", "VRF_ACME", "65000:101", dry_run=False)
    assert second_apply["changed"] is False and second_apply["native_diff"] == []
    post_check_ok = all("VRF_ACME" in nso.device_cdb[d]["vrfs"] for d in ("PE1", "PE2"))
    assert post_check_ok is True
    cleanup = nso.delete_l3vpn_service("CUST-ACME")
    assert cleanup["deleted"] is True and cleanup["fastmap_clean"] is True

    devices = fetch_all_paginated([["PE1", "PE2"], ["P1", "P2"], ["LEAF1"]])
    assert len(devices) == 5
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
