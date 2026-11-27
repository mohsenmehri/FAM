#!/usr/bin/env python3
"""
FAM Academy Lab — auto_10: YANG (RFC 7950) Local Data-Model Validator.
Execution boundary: Pure Python 3 stdlib educational validator checking
YANG leaf types, string length/pattern, uint16 range, list key uniqueness,
config false immutability, and choice mandatory=false/true semantics.
Does NOT replace a full YANG 1.1 compiler such as pyang or libyang.
"""

from __future__ import annotations

import json
import re


def validate_vlan_payload(payload: dict) -> list[str]:
    """Validate an instance against a simplified YANG module contract."""
    errors: list[str] = []
    seen_keys: set[int] = set()
    vlans = payload.get("vlans", [])
    if not isinstance(vlans, list):
        return ["vlans must be a YANG list"]

    for idx, item in enumerate(vlans):
        # leaf vlan-id { type uint16 { range "1..4094"; } } (list key)
        vid = item.get("vlan-id")
        if not isinstance(vid, int) or isinstance(vid, bool) or not (1 <= vid <= 4094):
            errors.append(f"vlans[{idx}].vlan-id={vid!r} violates uint16 range 1..4094")
        elif vid in seen_keys:
            errors.append(f"vlans[{idx}].vlan-id={vid} violates YANG list key uniqueness")
        else:
            seen_keys.add(vid)

        # leaf name { type string { length "1..32"; pattern "[A-Za-z0-9_-]+"; } }
        name = item.get("name", "")
        if not isinstance(name, str) or not (1 <= len(name) <= 32):
            errors.append(f"vlans[{idx}].name violates YANG length 1..32")
        elif not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            errors.append(f"vlans[{idx}].name={name!r} violates YANG pattern")

        # leaf oper-packet-count { config false; } -> must not be edited in config payload
        if "oper-packet-count" in item:
            errors.append(f"vlans[{idx}].oper-packet-count is config false (read-only state)")

        # choice addressing { mandatory false; case static-ip; case dhcp; }
        has_static = "static-ip" in item
        has_dhcp = "dhcp" in item
        if has_static and has_dhcp:
            errors.append(f"vlans[{idx}] violates YANG choice mutual exclusion (both static-ip and dhcp set)")
        # Note: neither set is valid because choice default is mandatory=false!

    return errors


def main() -> None:
    valid_payload = {
        "vlans": [
            {"vlan-id": 10, "name": "USERS_CORP", "static-ip": "10.10.10.1/24"},
            {"vlan-id": 20, "name": "VOICE_L2_ONLY"},  # 0 choice cases allowed when mandatory=false
        ]
    }
    invalid_payload = {
        "vlans": [
            {"vlan-id": 5000, "name": "BAD NAME!", "oper-packet-count": 99, "static-ip": "10.0.0.1/24", "dhcp": True},
            {"vlan-id": 10, "name": "DUP_A"},
            {"vlan-id": 10, "name": "DUP_B"},
        ]
    }

    valid_errs = validate_vlan_payload(valid_payload)
    invalid_errs = validate_vlan_payload(invalid_payload)
    assert valid_errs == [], f"Expected valid payload, got {valid_errs}"
    assert len(invalid_errs) == 5, f"Expected 5 YANG violations, got {invalid_errs}"

    print("=== auto_10 YANG RFC 7950 Local Validator Lab ===")
    print(json.dumps({
        "valid_payload_errors": valid_errs,
        "invalid_payload_error_count": len(invalid_errs),
        "invalid_payload_errors": invalid_errs,
        "boundary_note": "Educational Python validator only; full RFC 7950 checks require pyang/libyang.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
