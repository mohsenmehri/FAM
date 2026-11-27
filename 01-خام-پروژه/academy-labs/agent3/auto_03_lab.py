"""Local Python Mock for auto_03 (Netmiko Context Manager, TextFSM Fallback, save_config & Nornir Pilot).

No real SSH connection, Netmiko session, Nornir inventory target, or network OS device is run.
Models four real-world safety boundaries:
1. Context manager (__enter__/__exit__) closes sessions even on exceptions.
2. TextFSM missing-template fallback returns raw str instead of list[dict].
3. Netmiko send_config_set has NO native dry_run; Nornir dry_run safety depends on an explicit
   task.is_dry_run() guard or a dry-run-capable plugin (e.g., nornir_napalm napalm_configure).
4. save_config() is platform-dependent (IOS/IOS-XE/NX-OS vs commit-based IOS-XR/JunOS).
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

SAVE_CONFIG_PLATFORMS = frozenset({"cisco_ios", "cisco_xe", "cisco_nxos", "arista_eos"})
COMMIT_BASED_PLATFORMS = frozenset({"cisco_xr", "juniper_junos"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _host_role(dev: dict[str, object]) -> str | None:
    """Resolve Nornir SimpleInventory data.role (or legacy top-level role)."""
    if not isinstance(dev, dict):
        raise ValueError(f"inventory entry must be a dict, got {type(dev).__name__}")
    data = dev.get("data")
    if isinstance(data, dict) and "role" in data:
        role = data["role"]
        return role if isinstance(role, str) else None
    role = dev.get("role")
    return role if isinstance(role, str) else None


class MockNetmikoConnection:
    """Simulated ConnectHandler demonstrating disconnect via context manager and platform save_config."""

    def __init__(self, host: str, platform: str = "cisco_ios") -> None:
        if not isinstance(host, str) or not host.strip():
            raise ValueError(f"host must be a non-empty str, got {host!r}")
        if not isinstance(platform, str) or platform not in (SAVE_CONFIG_PLATFORMS | COMMIT_BASED_PLATFORMS):
            raise ValueError(f"unsupported mock platform {platform!r}")
        self.host = host
        self.platform = platform
        self.connected = False
        self.closed = False
        self.sent_configs: list[str] = []
        self.dirty_running_config = False
        self.saved_to_startup = False

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

    def send_config_set(self, commands: list[str]) -> dict[str, object]:
        """Mirror real Netmiko send_config_set: applies directly to running-config (no native dry_run)."""
        if not isinstance(commands, list) or not all(isinstance(c, str) and c.strip() for c in commands):
            raise ValueError("commands must be a list of non-empty strings")
        self.sent_configs.extend(commands)
        if commands:
            self.dirty_running_config = True
            self.saved_to_startup = False
        return {"host": self.host, "applied": True, "commands_count": len(commands)}

    def save_config(self) -> dict[str, object]:
        """Platform-dependent save_config(): works on running/startup OSes, not commit-based OSes."""
        if self.platform in COMMIT_BASED_PLATFORMS:
            raise NotImplementedError(
                f"save_config() is not used on commit-based platform {self.platform!r}; use commit() instead."
            )
        self.dirty_running_config = False
        self.saved_to_startup = True
        return {"host": self.host, "platform": self.platform, "saved": True}


def run_nornir_style_pilot(
    inventory: list[dict[str, object]],
    role_filter: str,
    commands: list[str],
    dry_run: bool = True,
    max_workers: int = 4,
    task_honors_dry_run: bool = True,
) -> list[dict[str, object]]:
    """Filter inventory by SimpleInventory data.role and enforce explicit task-level dry_run gating."""
    is_dry_run = _require_bool(dry_run, "dry_run")
    honors_dry_run = _require_bool(task_honors_dry_run, "task_honors_dry_run")
    if isinstance(max_workers, bool) or not isinstance(max_workers, int) or max_workers <= 0:
        raise ValueError(f"max_workers must be a positive int (not bool), got {max_workers!r}")
    if not isinstance(role_filter, str) or not role_filter.strip():
        raise ValueError("role_filter must be a non-empty str")
    if not isinstance(commands, list) or not all(isinstance(c, str) and c.strip() for c in commands):
        raise ValueError("commands must be a list of non-empty strings")

    targets = [dev for dev in inventory if _host_role(dev) == role_filter]

    def task(dev: dict[str, object]) -> dict[str, object]:
        host = dev.get("host")
        platform = str(dev.get("platform", "cisco_ios"))
        if is_dry_run and not honors_dry_run:
            raise RuntimeError(
                "dry_run=True requested, but task/plugin does not implement task.is_dry_run() "
                "(e.g., raw nornir_netmiko netmiko_send_config); wrap explicitly or use nornir_napalm."
            )
        with MockNetmikoConnection(str(host), platform=platform) as conn:
            if is_dry_run:
                res: dict[str, object] = {
                    "host": conn.host,
                    "applied": False,
                    "dry_run_honored": True,
                    "planned_commands": list(commands),
                }
            else:
                res = {**conn.send_config_set(commands), "dry_run_honored": False}
        return {**res, "session_closed": conn.closed}

    with ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(targets)))) as pool:
        return list(pool.map(task, targets))


def main() -> None:
    print("Local Python Mock only — no real SSH, Netmiko, Nornir, or IOS-XE router is contacted.")
    with MockNetmikoConnection("192.0.2.11", platform="cisco_ios") as conn:
        parsed = conn.send_command("show ip interface brief", use_textfsm=True)
        fallback = conn.send_command("show custom vendor telemetry", use_textfsm=True)
    assert isinstance(parsed, list) and isinstance(fallback, str) and conn.closed is True
    print("TextFSM matched type:", type(parsed).__name__, parsed)
    print("TextFSM missing-template fallback type:", type(fallback).__name__, fallback)
    print("Session closed safely after with-block:", conn.closed)

    # Nornir SimpleInventory-style data.role schema
    inv = [
        {"host": "192.0.2.11", "platform": "cisco_ios", "groups": ["campus_iosxe"], "data": {"role": "pilot"}},
        {"host": "192.0.2.12", "platform": "cisco_ios", "groups": ["campus_iosxe"], "data": {"role": "production"}},
        {"host": "192.0.2.13", "platform": "cisco_xr", "groups": ["core_iosxr"], "data": {"role": "production"}},
    ]
    pilot_res = run_nornir_style_pilot(inv, "pilot", ["ntp server 192.0.2.123"], dry_run=True)
    assert len(pilot_res) == 1 and pilot_res[0]["applied"] is False and pilot_res[0]["session_closed"] is True
    print("Pilot dry-run (explicit task.is_dry_run() guard):", pilot_res)

    # Demonstrate platform-dependent save_config() boundary (IOS-XE vs commit-based IOS-XR)
    with MockNetmikoConnection("192.0.2.13", platform="cisco_xr") as xr_conn:
        try:
            xr_conn.save_config()
            raise AssertionError("Expected NotImplementedError for cisco_xr save_config()")
        except NotImplementedError as exc:
            print("Platform save_config() guard:", exc)


if __name__ == "__main__":
    main()
