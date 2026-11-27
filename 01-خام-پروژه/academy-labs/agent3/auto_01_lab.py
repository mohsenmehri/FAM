"""Local Linux & Log-Processing Lab for auto_01 (runs locally in a temporary directory).

No production Linux server, root privilege, or real Cisco/network device is modified.
"""
from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
import stat
import tempfile

SAMPLE_AUTH_LOG = """Nov 27 02:10:01 bastion sshd[101]: Failed password for invalid user admin from 198.51.100.10 port 51234 ssh2
Nov 27 02:10:03 bastion sshd[102]: Failed password for invalid user admin from 198.51.100.10 port 51235 ssh2
Nov 27 02:10:05 bastion sshd[103]: Accepted publickey for netops from 192.0.2.15 port 52001 ssh2
Nov 27 02:10:07 bastion sshd[104]: Failed password for root from 203.0.113.77 port 49111 ssh2
Nov 27 02:10:09 bastion sshd[105]: Failed password for invalid user test from 198.51.100.10 port 51239 ssh2
"""


def parse_failed_ssh_counts(log_text: str) -> list[tuple[str, int]]:
    """Python equivalent of: grep 'Failed password' | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr."""
    ips = []
    for line in log_text.splitlines():
        if "Failed password" in line:
            tokens = line.split()
            if "from" in tokens:
                idx = tokens.index("from")
                if idx + 1 < len(tokens):
                    ips.append(tokens[idx + 1])
    return sorted(Counter(ips).items(), key=lambda item: (-item[1], item[0]))


def verify_ssh_key_permissions(temp_dir: Path) -> dict[str, object]:
    """Create a dummy key file in temp_dir and verify octal 0600 (owner rw only)."""
    key_path = temp_dir / "id_ed25519_dummy"
    key_path.write_text("DUMMY-KEY-NOT-REAL\n", encoding="utf-8")
    os.chmod(key_path, 0o600)
    mode = stat.S_IMODE(key_path.stat().st_mode)
    return {
        "file": key_path.name,
        "octal_mode": oct(mode),
        "safe_for_openssh": mode == 0o600,
    }


def main() -> None:
    print("Local temporary-directory Linux lab only — no production server or router is modified.")
    counts = parse_failed_ssh_counts(SAMPLE_AUTH_LOG)
    print("Top failed SSH source IPs:", counts)
    with tempfile.TemporaryDirectory() as tmp:
        print("SSH key permission check:", verify_ssh_key_permissions(Path(tmp)))


if __name__ == "__main__":
    main()
