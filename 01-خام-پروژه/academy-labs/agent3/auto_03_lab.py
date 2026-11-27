"""Local Python Mock for auto_03 (Netmiko Context Manager, TextFSM Fallback & Nornir Pilot).

No real SSH connection, Netmiko session, Nornir inventory target, or Cisco IOS device is run.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


class MockNetmikoConnection:
    """Simulated ConnectHandler demonstrating guaranteed disconnect via context manager."""

    def __init__(self, host: str) -> None:
        self.host = host
        self.connected = False
        self.closed = False
        self.sent_configs: list[str] = []

    def __enter__(self) -> "MockNetmikoConnection":
        self.connected = True
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.connected = False
        self.closed = True
        return False  # Do not swallow exceptions

    def send_command(self, cmd: str, use_textfsm: bool = False) -> object:
        raw = f"{self.host}: GigabitEthernet0/0 is up, line protocol is up"
        if use_textfsm and cmd == "show ip interface brief":
            return [{"intf": "GigabitEthernet0/0", "status": "up", "proto": "up"}]
        # Mirror real Netmiko fallback: missing template returns raw str!
        return raw

    def send_config_set(self, commands: list[str], dry_run: bool = True) -> dict[str, object]:
        if dry_run:
            return {"host": self.host, "applied": False, "planned_commands": list(commands)}
        self.sent_configs.extend(commands)
        return {"host": self.host, "applied": True, "commands_count": len(commands)}


def run_nornir_style_pilot(
    inventory: list[dict[str, str]],
    role_filter: str,
    commands: list[str],
    dry_run: bool = True,
    max_workers: int = 4,
) -> list[dict[str, object]]:
    """Filter inventory to a pilot group first and execute with bounded concurrency."""
    targets = [dev for dev in inventory if dev.get("role") == role_filter]

    def task(dev: dict[str, str]) -> dict[str, object]:
        with MockNetmikoConnection(dev["host"]) as conn:
            res = conn.send_config_set(commands, dry_run=dry_run)
        return {**res, "session_closed": conn.closed}

    with ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(targets)))) as pool:
        return list(pool.map(task, targets))


def main() -> None:
    print("Local Python Mock only — no real SSH, Netmiko, Nornir, or IOS-XE router is contacted.")
    with MockNetmikoConnection("192.0.2.11") as conn:
        parsed = conn.send_command("show ip interface brief", use_textfsm=True)
        fallback = conn.send_command("show custom vendor telemetry", use_textfsm=True)
    print("TextFSM matched type:", type(parsed).__name__, parsed)
    print("TextFSM missing-template fallback type:", type(fallback).__name__, fallback)
    print("Session closed safely after with-block:", conn.closed)

    inv = [
        {"host": "192.0.2.11", "role": "pilot"},
        {"host": "192.0.2.12", "role": "production"},
        {"host": "192.0.2.13", "role": "production"},
    ]
    print("Pilot dry-run:", run_nornir_style_pilot(inv, "pilot", ["ntp server 192.0.2.123"], dry_run=True))


if __name__ == "__main__":
    main()
