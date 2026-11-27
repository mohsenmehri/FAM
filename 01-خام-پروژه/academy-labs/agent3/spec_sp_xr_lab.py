#!/usr/bin/env python3
"""
Local Mock Lab — spec_sp_xr (Service Provider Cisco IOS-XR: Two-Stage Commit, Commit Confirmed & RPL)
Simulates IOS-XR candidate vs running datastore, automatic rollback on unconfirmed commit,
and Route Policy Language (RPL) filtering with eBGP default-deny safety.
No real Cisco IOS-XR router (ASR 9000 / NCS 5500) is connected.
"""

import copy
import json


class MockIOSXRRouter:
    def __init__(self) -> None:
        self.running = {"hostname": "PE-TEHRAN-01", "ebgp_neighbor_policy_in": None, "ebgp_neighbor_policy_out": None}
        self.candidate = copy.deepcopy(self.running)
        self.commit_history: list[dict] = [{"commit_id": 1000000001, "state": copy.deepcopy(self.running)}]

    def stage_config(self, updates: dict) -> dict:
        self.candidate.update(updates)
        diff = {k: (self.running.get(k), v) for k, v in self.candidate.items() if self.running.get(k) != v}
        return {"staged_diff": diff, "running_unchanged": self.running}

    def commit(self, confirmed_seconds: int | None = None, confirmed_by_operator: bool = True) -> dict:
        prev = copy.deepcopy(self.running)
        self.running = copy.deepcopy(self.candidate)
        if confirmed_seconds and not confirmed_by_operator:
            # Simulate operator lockout -> automatic rollback after timer expiry
            self.running = prev
            self.candidate = copy.deepcopy(prev)
            return {
                "status": "AUTO_ROLLED_BACK",
                "reason": f"No 'commit' confirmation received within {confirmed_seconds}s — lockout prevented!",
                "active_running": self.running,
            }
        commit_id = self.commit_history[-1]["commit_id"] + 1
        self.commit_history.append({"commit_id": commit_id, "state": copy.deepcopy(self.running)})
        return {"status": "COMMITTED", "commit_id": commit_id, "active_running": self.running}


def eval_rpl_policy(policy_name: str | None, prefix: str, prefix_len: int, local_pref: int = 100) -> dict:
    # IOS-XR eBGP default safety (RFC 8212): without an attached RPL policy, all prefixes are denied!
    if policy_name is None:
        return {"prefix": f"{prefix}/{prefix_len}", "action": "DROP", "reason": "IOS-XR eBGP default-deny (no RPL policy attached)"}
    if policy_name == "RPL_CUST_IN":
        if prefix.startswith("198.51.100.") and 21 <= prefix_len <= 24:
            return {"prefix": f"{prefix}/{prefix_len}", "action": "PASS", "set_local_pref": 200, "policy": policy_name}
        return {"prefix": f"{prefix}/{prefix_len}", "action": "DROP", "reason": "Did not match customer prefix-set (implicit drop)"}
    return {"prefix": f"{prefix}/{prefix_len}", "action": "DROP", "reason": "Unknown policy"}


def main() -> None:
    xr = MockIOSXRRouter()
    staged = xr.stage_config({"ebgp_neighbor_policy_in": "RPL_CUST_IN", "ebgp_neighbor_policy_out": "RPL_CUST_OUT"})
    # Scenario 1: simulated lockout on a risky ACL/BGP change using commit confirmed 60
    lockout_test = xr.commit(confirmed_seconds=60, confirmed_by_operator=False)
    # Scenario 2: re-stage and properly confirm
    xr.stage_config({"ebgp_neighbor_policy_in": "RPL_CUST_IN", "ebgp_neighbor_policy_out": "RPL_CUST_OUT"})
    good_commit = xr.commit(confirmed_seconds=60, confirmed_by_operator=True)

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_IOS_XR_HARDWARE",
        "two_stage_diff_before_commit": staged["staged_diff"],
        "commit_confirmed_lockout_recovery": lockout_test,
        "confirmed_commit_result": good_commit,
        "rpl_evaluation": {
            "before_policy_attached_ebgp": eval_rpl_policy(None, "198.51.100.0", 24),
            "valid_customer_prefix": eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "198.51.100.0", 24),
            "bogus_hijack_prefix": eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "8.8.8.0", 24),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
