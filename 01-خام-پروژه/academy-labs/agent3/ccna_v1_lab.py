"""Local Python Mock for ccna_v1 (Virtualization, Containers, vSwitch Tagging & Cloud Models).

No real ESXi/KVM hypervisor, Docker host, or cloud VPC is executed.
Models:
1. EST vs VST vs VGT VLAN tagging compatibility between a host vSwitch and a physical switch port.
2. VM (guest kernel) vs Container (shared host kernel) architectural boundary.
3. Cloud Shared Responsibility Matrix (On-Premises, IaaS, PaaS, SaaS).
"""
from __future__ import annotations

VALID_TAGGING_MODES = frozenset({"EST", "VST", "VGT"})
VALID_PORT_MODES = frozenset({"access", "trunk"})
VALID_CLOUD_MODELS = frozenset({"on_premises", "iaas", "paas", "saas"})


def _require_vlan(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (1 <= val <= 4094):
        raise ValueError(f"{name} must be an int in 1..4094 (not bool), got {val!r}")
    return val


def _require_vlan_list(vals: object, name: str) -> set[int]:
    if not isinstance(vals, (list, set, tuple)) or len(vals) == 0:
        raise ValueError(f"{name} must be a non-empty list/set/tuple of VLAN IDs")
    return {_require_vlan(v, f"{name} element") for v in vals}


def audit_vswitch_uplink(
    tagging_mode: str,
    vm_vlans: list[int],
    switch_port_mode: str,
    switch_vlans: list[int],
) -> dict[str, object]:
    """Check selected configuration assumptions only; not a connectivity test."""
    if not isinstance(tagging_mode, str) or tagging_mode not in VALID_TAGGING_MODES:
        raise ValueError(f"tagging_mode must be one of {sorted(VALID_TAGGING_MODES)}, got {tagging_mode!r}")
    if not isinstance(switch_port_mode, str) or switch_port_mode not in VALID_PORT_MODES:
        raise ValueError(f"switch_port_mode must be one of {sorted(VALID_PORT_MODES)}, got {switch_port_mode!r}")
    req_vlans = _require_vlan_list(vm_vlans, "vm_vlans")
    phys_vlans = _require_vlan_list(switch_vlans, "switch_vlans")

    issues: list[str] = []
    if tagging_mode == "EST":
        if switch_port_mode != "access":
            issues.append("EST_REQUIRES_ACCESS_PORT: External Switch Tagging expects untagged frames on an access port")
        if len(phys_vlans) != 1:
            issues.append("ACCESS_REQUIRES_ONE_VLAN: this model expects exactly one access VLAN")
        if len(req_vlans) > 1:
            issues.append("EST_SINGLE_VLAN_ONLY: an access uplink carries only one VLAN per physical NIC")
    else:
        # VST (vSwitch tags) and VGT (guest VM tags) require 802.1Q trunk on the physical switch port
        if switch_port_mode != "trunk":
            issues.append(f"{tagging_mode}_REQUIRES_TRUNK_PORT: physical switch port must be 802.1Q trunk")

    missing = sorted(req_vlans - phys_vlans)
    if missing:
        issues.append(f"MISSING_VLANS_ON_PHYSICAL_SWITCH: {missing}")

    return {
        "tagging_mode": tagging_mode,
        "switch_port_mode": switch_port_mode,
        "model_checks_ok": len(issues) == 0,
        "issues": issues,
    }


def classify_cloud_responsibility(model: str) -> dict[str, str]:
    """Return one illustrative matrix, not a provider-specific contract."""
    if not isinstance(model, str) or model not in VALID_CLOUD_MODELS:
        raise ValueError(f"model must be one of {sorted(VALID_CLOUD_MODELS)}, got {model!r}")
    matrix = {
        "on_premises": {
            "physical_hardware": "customer",
            "hypervisor": "customer",
            "guest_os_and_vpc": "customer",
            "application_and_data": "customer",
            "wan_and_user_access_network": "customer",
        },
        "iaas": {
            "physical_hardware": "provider",
            "hypervisor": "provider",
            "guest_os_and_vpc": "customer",
            "application_and_data": "customer",
            "wan_and_user_access_network": "customer",
        },
        "paas": {
            "physical_hardware": "provider",
            "hypervisor": "provider",
            "guest_os_and_vpc": "provider_managed",
            "application_and_data": "customer",
            "wan_and_user_access_network": "customer",
        },
        "saas": {
            "physical_hardware": "provider",
            "hypervisor": "provider",
            "guest_os_and_vpc": "provider",
            "application_and_data": "shared_customer_owns_data_and_iam",
            "wan_and_user_access_network": "customer",
        },
    }
    return matrix[model]


def main() -> None:
    print("Local Python Mock only — no real hypervisor, container engine, or cloud VPC is contacted.")
    broken = audit_vswitch_uplink("VST", [10, 30], "access", [10])
    assert broken["model_checks_ok"] is False
    print("Broken VST on access port:", broken)

    fixed = audit_vswitch_uplink("VST", [10, 30], "trunk", [10, 20, 30])
    assert fixed["model_checks_ok"] is True
    print("Fixed VST on 802.1Q trunk:", fixed)

    iaas = classify_cloud_responsibility("iaas")
    saas = classify_cloud_responsibility("saas")
    assert iaas["guest_os_and_vpc"] == "customer" and iaas["physical_hardware"] == "provider"
    assert saas["wan_and_user_access_network"] == "customer"
    print("IaaS boundaries:", iaas)
    print("SaaS boundaries:", saas)


if __name__ == "__main__":
    main()
