#!/usr/bin/env python3
"""
Local Mock Lab — spec_sp_xr (Service Provider Cisco IOS-XR: Two-Stage Commit, Commit Confirmed & RPL)
Simulates IOS-XR candidate vs running datastore, automatic rollback on unconfirmed commit,
and Route Policy Language (RPL) strict CIDR prefix-set filtering with RFC 8212 eBGP default-deny safety.
No real Cisco IOS-XR router (ASR 9000 / NCS 5500) is connected.
"""

import copy
import ipaddress
import json

CUSTOMER_AGGREGATE = ipaddress.ip_network("198.51.100.0/24")


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
    try:
        net = ipaddress.ip_network(f"{prefix}/{prefix_len}", strict=True)
    except ValueError as exc:
        return {"prefix": f"{prefix}/{prefix_len}", "action": "DROP", "reason": f"Invalid CIDR prefix: {exc}"}

    if policy_name == "RPL_CUST_IN":
        # Models IOS-XR prefix-set: 198.51.100.0/24 le 26 (strict RFC 4632 CIDR subnet check)
        if net.version == 4 and net.subnet_of(CUSTOMER_AGGREGATE) and 24 <= net.prefixlen <= 26:
            return {"prefix": str(net), "action": "PASS", "set_local_pref": 200, "policy": policy_name}
        return {"prefix": str(net), "action": "DROP", "reason": "Did not match customer prefix-set 198.51.100.0/24 le 26 (implicit drop)"}
    return {"prefix": str(net), "action": "DROP", "reason": "Unknown policy"}


def main() -> None:
    xr = MockIOSXRRouter()
    staged = xr.stage_config({"ebgp_neighbor_policy_in": "RPL_CUST_IN", "ebgp_neighbor_policy_out": "RPL_CUST_OUT"})
    lockout_test = xr.commit(confirmed_seconds=60, confirmed_by_operator=False)
    assert lockout_test["status"] == "AUTO_ROLLED_BACK"
    assert xr.running["ebgp_neighbor_policy_in"] is None

    xr.stage_config({"ebgp_neighbor_policy_in": "RPL_CUST_IN", "ebgp_neighbor_policy_out": "RPL_CUST_OUT"})
    good_commit = xr.commit(confirmed_seconds=60, confirmed_by_operator=True)
    assert good_commit["status"] == "COMMITTED"

    r_no_pol = eval_rpl_policy(None, "198.51.100.0", 24)
    r_valid_24 = eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "198.51.100.0", 24)
    r_valid_25 = eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "198.51.100.128", 25)
    r_bad_hostbits = eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "198.51.100.0", 21)
    r_too_specific = eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "198.51.100.0", 28)
    r_hijack = eval_rpl_policy(xr.running["ebgp_neighbor_policy_in"], "8.8.8.0", 24)

    assert r_no_pol["action"] == "DROP"
    assert r_valid_24["action"] == "PASS" and r_valid_25["action"] == "PASS"
    assert r_bad_hostbits["action"] == "DROP" and "Invalid CIDR" in r_bad_hostbits["reason"]
    assert r_too_specific["action"] == "DROP" and r_hijack["action"] == "DROP"

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_IOS_XR_HARDWARE",
        "two_stage_diff_before_commit": staged["staged_diff"],
        "commit_confirmed_lockout_recovery": lockout_test,
        "confirmed_commit_result": good_commit,
        "rpl_evaluation": {
            "before_policy_attached_ebgp": r_no_pol,
            "valid_customer_24": r_valid_24,
            "valid_customer_25": r_valid_25,
            "invalid_non_cidr_21_rejected": r_bad_hostbits,
            "too_specific_28_rejected": r_too_specific,
            "bogus_hijack_prefix": r_hijack,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
