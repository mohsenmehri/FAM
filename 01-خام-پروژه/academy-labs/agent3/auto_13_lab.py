#!/usr/bin/env python3
"""
FAM Academy Lab — auto_13: Cisco NSO (CDB, NED, FASTMAP & Atomic Rollback) Mock.
Execution boundary: Pure Python 3 stdlib simulation of NSO multi-vendor service
mapping (L3VPN servicepoint -> IOS-XE & Junos NEDs), two-phase atomic commit
with rollback on southbound failure, and check-sync drift detection. No live NSO.
"""

from __future__ import annotations

import copy
import json


def _require_non_empty_str(val: object, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty str, got {val!r}")
    return val


class NsoOrchestratorMock:
    def __init__(self) -> None:
        self.cdb_devices = {"PE1-IOSXE": [], "PE2-JUNOS": []}
        self.live_devices = copy.deepcopy(self.cdb_devices)

    def render_ned_commands(self, vrf_name: str, rd: str) -> dict[str, list[str]]:
        _require_non_empty_str(vrf_name, "vrf_name")
        _require_non_empty_str(rd, "rd")
        return {
            "PE1-IOSXE": [f"vrf definition {vrf_name}", f" rd {rd}", " address-family ipv4"],
            "PE2-JUNOS": [f"set routing-instances {vrf_name} instance-type vrf", f"set routing-instances {vrf_name} route-distinguisher {rd}"],
        }

    def commit_service(self, vrf_name: str, rd: str, fail_on_device: str | None = None) -> dict:
        rendered = self.render_ned_commands(vrf_name, rd)
        if fail_on_device is not None and fail_on_device not in rendered:
            raise ValueError(f"Unknown fail_on_device {fail_on_device!r}; expected one of {sorted(rendered)}")
        cdb_backup = copy.deepcopy(self.cdb_devices)
        live_backup = copy.deepcopy(self.live_devices)
        try:
            for dev, cmds in rendered.items():
                if dev == fail_on_device:
                    raise RuntimeError(f"Southbound NED error on {dev}: RPC rejected")
                self.live_devices[dev].extend(cmds)
                self.cdb_devices[dev].extend(cmds)
            return {"status": "committed", "rollback_triggered": False, "rendered": rendered}
        except RuntimeError as exc:
            # Atomic rollback restores BOTH PE1 and PE2 to pre-transaction snapshot
            self.cdb_devices = cdb_backup
            self.live_devices = live_backup
            return {"status": "aborted", "error": str(exc), "rollback_triggered": True}

    def check_sync(self, device: str) -> str:
        if device not in self.cdb_devices:
            raise ValueError(f"Unknown NSO device: {device!r}")
        return "in-sync" if self.cdb_devices[device] == self.live_devices[device] else "out-of-sync"


def main() -> None:
    nso = NsoOrchestratorMock()
    # 1. Failed transaction on PE2 must roll back PE1 too!
    failed_tx = nso.commit_service("CUST_A", "65000:100", fail_on_device="PE2-JUNOS")
    assert failed_tx["rollback_triggered"] is True
    assert nso.live_devices["PE1-IOSXE"] == [], "PE1 must be rolled back atomically"

    # 2. Successful multi-vendor service provisioning
    ok_tx = nso.commit_service("CUST_A", "65000:100")
    assert ok_tx["status"] == "committed"
    assert nso.check_sync("PE1-IOSXE") == "in-sync"

    # 3. Simulate manual out-of-band CLI edit causing drift
    nso.live_devices["PE1-IOSXE"].append("description MANUAL_HOTFIX_BY_ADMIN")
    drift_status = nso.check_sync("PE1-IOSXE")
    assert drift_status == "out-of-sync"

    print("=== auto_13 Cisco NSO FASTMAP & Atomic Rollback Mock ===")
    print(json.dumps({
        "failed_tx_atomic_rollback": failed_tx,
        "successful_tx_status": ok_tx["status"],
        "drift_check_after_manual_cli": drift_status,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
