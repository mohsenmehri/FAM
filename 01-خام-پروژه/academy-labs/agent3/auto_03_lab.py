"""Local Python Mock for auto_03 (Netmiko Context Manager, TextFSM Fallback & Nornir Pilot).

No real SSH connection, Netmiko session, Nornir inventory target, or Cisco IOS device is run.
Strict validation rejects non-bool use_textfsm/dry_run flags and non-positive/bool max_workers.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


class MockNetmikoConnection:
    """Simulated ConnectHandler demonstrating disconnect via context manager."""

    def __init__(self, host: str) -> None:
        if not isinstance(host, str) or not host.strip():
            raise ValueError(f"host must be a non-empty str, got {host!r}")
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
        if not isinstance(cmd, str) or not cmd.strip():
            raise ValueError("cmd must be a non-empty str")
        want_textfsm = _require_bool(use_textfsm, "use_textfsm")
        raw = f"{self.host}: GigabitEthernet0/0 is up, line protocol is up"
        if want_textfsm and cmd == "show ip interface brief":
            return [{"intf": "GigabitEthernet0/0", "status": "up", "proto": "up"}]
        # Mirror real Netmiko fallback: missing template returns raw str!
        return raw

    def send_config_set(self, commands: list[str], dry_run: bool = True) -> dict[str, object]:
        is_dry_run = _require_bool(dry_run, "dry_run")
        if not isinstance(commands, list) or not all(isinstance(c, str) and c.strip() for c in commands):
            raise ValueError("commands must be a list of nonempty strings")
        if is_dry_run:
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
    is_dry_run = _require_bool(dry_run, "dry_run")
    if isinstance(max_workers, bool) or not isinstance(max_workers, int) or max_workers <= 0:
        raise ValueError(f"max_workers must be a positive int (not bool), got {max_workers!r}")
    targets = [dev for dev in inventory if dev.get("role") == role_filter]

    def task(dev: dict[str, str]) -> dict[str, object]:
        with MockNetmikoConnection(dev["host"]) as conn:
            res = conn.send_config_set(commands, dry_run=is_dry_run)
        return {**res, "session_closed": conn.closed}

    with ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(targets)))) as pool:
        return list(pool.map(task, targets))


def main() -> None:
    print("Local Python Mock only — no real SSH, Netmiko, Nornir, or IOS-XE router is contacted.")
    with MockNetmikoConnection("192.0.2.11") as conn:
        parsed = conn.send_command("show ip interface brief", use_textfsm=True)
        fallback = conn.send_command("show custom vendor telemetry", use_textfsm=True)
    assert isinstance(parsed, list) and isinstance(fallback, str) and conn.closed is True
    print("TextFSM matched type:", type(parsed).__name__, parsed)
    print("TextFSM missing-template fallback type:", type(fallback).__name__, fallback)
    print("Session closed safely after with-block:", conn.closed)

    inv = [
        {"host": "192.0.2.11", "role": "pilot"},
        {"host": "192.0.2.12", "role": "production"},
        {"host": "192.0.2.13", "role": "production"},
    ]
    pilot_res = run_nornir_style_pilot(inv, "pilot", ["ntp server 192.0.2.123"], dry_run=True)
    assert len(pilot_res) == 1 and pilot_res[0]["applied"] is False and pilot_res[0]["session_closed"] is True
    print("Pilot dry-run:", pilot_res)


if __name__ == "__main__":
    main()
