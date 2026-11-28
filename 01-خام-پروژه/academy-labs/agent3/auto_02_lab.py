"""Local Python Lab for auto_02 (Parsing CLI text, Sets/Dicts, with open & safe exceptions).

Runs locally in Python 3 using synthetic CLI text; no real Cisco router is contacted.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

SAMPLE_SHOW_IP_INT_BR = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.0.2.1       YES manual up                    up
GigabitEthernet0/1     198.51.100.1    YES manual administratively down down
Loopback0              203.0.113.10    YES manual up                    up
""".strip()


def parse_interfaces(raw_output: str) -> list[dict[str, str]]:
    """Parse the stated simplified table, failing closed on malformed input.

    This is not a general IOS parser; validate platform output separately.
    """
    lines = [line for line in raw_output.splitlines() if line.strip()]
    if not lines or lines[0].split() != ["Interface", "IP-Address", "OK?", "Method", "Status", "Protocol"]:
        raise ValueError("missing or unsupported table header")
    results: list[dict[str, str]] = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) < 6:
            raise ValueError(f"malformed interface row: {line!r}")
        interface, ip_addr, ok_flag, method = parts[0], parts[1], parts[2], parts[3]
        protocol = parts[-1]
        status = " ".join(parts[4:-1])
        results.append({
            "interface": interface,
            "ip": ip_addr,
            "ok": ok_flag,
            "method": method,
            "status": status,
            "protocol": protocol,
        })
    return results


def diff_vlans(desired_vlans: set[int], observed_vlans: set[int]) -> dict[str, list[int]]:
    """Use Python sets to identify missing and unexpected VLANs cleanly."""
    return {
        "to_add": sorted(desired_vlans - observed_vlans),
        "unexpected_extra": sorted(observed_vlans - desired_vlans),
        "compliant": sorted(desired_vlans & observed_vlans),
    }


def safe_parse_vlan_id(raw_value: str) -> int:
    """Validate VLAN ID using specific exceptions (never bare except)."""
    try:
        vid = int(raw_value.strip())
    except ValueError as exc:
        raise ValueError(f"VLAN ID must be an integer, got {raw_value!r}") from exc
    if not (1 <= vid <= 4094):
        raise ValueError(f"VLAN ID out of 802.1Q range (1..4094): {vid}")
    return vid


def main() -> None:
    print("Local Python lab only — synthetic CLI text; no real router or switch is contacted.")
    parsed = parse_interfaces(SAMPLE_SHOW_IP_INT_BR)
    up_ifaces = [row["interface"] for row in parsed if row["status"] == "up" and row["protocol"] == "up"]
    print("Parsed interfaces:", len(parsed), "| up/up:", up_ifaces)
    print("VLAN diff:", diff_vlans({10, 20, 30}, {10, 99}))
    with tempfile.TemporaryDirectory() as tmp:
        out_file = Path(tmp) / "interfaces.json"
        with open(out_file, "w", encoding="utf-8") as fh:
            json.dump(parsed, fh, indent=2)
        print("Saved JSON to temporary file via 'with open':", out_file.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
