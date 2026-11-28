"""Local Python Mock for ccna_02_vlan (802.1Q VLAN, Access/Voice, Trunk, Native VLAN & DTP).

No real Cisco Catalyst switch or live CLI session is run.
Explicitly models the reconciliation of the ccna_02_vlan scenario discrepancies:
- Native VLAN 999 MUST be in allowed VLANs on BOTH trunk ends when carrying native traffic.
- Voice VLAN 50 MUST exist in the VLAN database and be allowed on trunks if spanning switches.
- switchport mode access forces permanent nontrunk, while switchport nonegotiate stops DTP frames.
- Native VLAN is untagged by default, unless explicit native-VLAN tagging is configured.
"""
from __future__ import annotations

VALID_VLAN_RANGE = range(1, 4095)
VALID_PORT_MODES = frozenset({"access", "trunk", "dynamic_auto", "dynamic_desirable"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_vlan_id(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val not in VALID_VLAN_RANGE:
        raise ValueError(f"{name} must be an int in 1..4094 (not bool), got {val!r}")
    return val


def _require_vlan_set(vals: object, name: str) -> set[int]:
    if not isinstance(vals, (list, set, tuple)):
        raise ValueError(f"{name} must be a list/set/tuple of VLAN IDs")
    return {_require_vlan_id(v, f"{name} element") for v in vals}


def evaluate_dtp_link(
    sw1_mode: str,
    sw2_mode: str,
    sw1_nonegotiate: bool = False,
    sw2_nonegotiate: bool = False,
) -> dict[str, object]:
    """Model Catalyst DTP negotiation and explicitly distinguish mode vs nonegotiate."""
    if sw1_mode not in VALID_PORT_MODES or sw2_mode not in VALID_PORT_MODES:
        raise ValueError(f"modes must be in {sorted(VALID_PORT_MODES)}")
    n1 = _require_bool(sw1_nonegotiate, "sw1_nonegotiate")
    n2 = _require_bool(sw2_nonegotiate, "sw2_nonegotiate")

    if (sw1_mode.startswith("dynamic") and n1) or (sw2_mode.startswith("dynamic") and n2):
        raise ValueError("switchport nonegotiate requires a static mode (access or trunk), not dynamic")

    # DTP frame transmission stops only with explicit nonegotiate (platform-dependent on static access)
    dtp_frames_sent = (not n1) or (not n2)

    if sw1_mode == "access" and sw2_mode == "access":
        state = "access"
    elif (sw1_mode == "access" and sw2_mode == "trunk") or (sw1_mode == "trunk" and sw2_mode == "access"):
        state = "mismatch_broken"
    elif sw1_mode == "trunk" and sw2_mode == "trunk":
        state = "trunk"
    elif "trunk" in (sw1_mode, sw2_mode):
        other_noneg = n1 if sw1_mode == "trunk" else n2
        state = "mismatch_broken" if other_noneg else "trunk"
    elif "access" in (sw1_mode, sw2_mode):
        state = "access"
    elif "dynamic_desirable" in (sw1_mode, sw2_mode):
        state = "trunk"
    else:
        # dynamic_auto <-> dynamic_auto never forms a trunk!
        state = "access_no_trunk"

    return {
        "sw1_mode": sw1_mode,
        "sw2_mode": sw2_mode,
        "sw1_nonegotiate": n1,
        "sw2_nonegotiate": n2,
        "operational_state": state,
        "dtp_frames_may_still_be_sent": dtp_frames_sent,
    }


def audit_trunk_pair(
    sw1_vlans: list[int],
    sw2_vlans: list[int],
    sw1_allowed: list[int],
    sw2_allowed: list[int],
    sw1_native: int,
    sw2_native: int,
    required_vlans: list[int],
    sw1_tag_native: bool = False,
    sw2_tag_native: bool = False,
    require_native_in_allowed: bool = True,
) -> dict[str, object]:
    """Audit end-to-end 802.1Q trunk consistency across SW1 and SW2."""
    db1 = _require_vlan_set(sw1_vlans, "sw1_vlans")
    db2 = _require_vlan_set(sw2_vlans, "sw2_vlans")
    all1 = _require_vlan_set(sw1_allowed, "sw1_allowed")
    all2 = _require_vlan_set(sw2_allowed, "sw2_allowed")
    req = _require_vlan_set(required_vlans, "required_vlans")
    nat1 = _require_vlan_id(sw1_native, "sw1_native")
    nat2 = _require_vlan_id(sw2_native, "sw2_native")
    tag1 = _require_bool(sw1_tag_native, "sw1_tag_native")
    tag2 = _require_bool(sw2_tag_native, "sw2_tag_native")
    req_nat_allowed = _require_bool(require_native_in_allowed, "require_native_in_allowed")

    issues: list[str] = []
    if nat1 != nat2:
        issues.append(f"NATIVE_VLAN_MISMATCH: SW1={nat1} vs SW2={nat2}")
    if tag1 != tag2:
        issues.append(f"NATIVE_TAGGING_MISMATCH: SW1 tag_native={tag1} vs SW2 tag_native={tag2}")
    if req_nat_allowed:
        if nat1 not in all1:
            issues.append(f"SW1_NATIVE_PRUNED: native VLAN {nat1} missing from SW1 allowed list {sorted(all1)}")
        if nat2 not in all2:
            issues.append(f"SW2_NATIVE_PRUNED: native VLAN {nat2} missing from SW2 allowed list {sorted(all2)}")

    for vid in sorted(req):
        if vid not in db1:
            issues.append(f"VLAN_{vid}_MISSING_ON_SW1_DB")
        if vid not in db2:
            issues.append(f"VLAN_{vid}_MISSING_ON_SW2_DB")
        if vid not in all1:
            issues.append(f"VLAN_{vid}_NOT_ALLOWED_ON_SW1_TRUNK")
        if vid not in all2:
            issues.append(f"VLAN_{vid}_NOT_ALLOWED_ON_SW2_TRUNK")

    native_frame_format = "tagged_8021q" if (tag1 and tag2) else ("untagged_default" if (not tag1 and not tag2) else "mismatched")
    return {
        "end_to_end_ok": len(issues) == 0,
        "native_vlan_sw1": nat1,
        "native_vlan_sw2": nat2,
        "native_frame_format": native_frame_format,
        "effective_forwarding_vlans": sorted(db1 & db2 & all1 & all2),
        "issues": issues,
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco Catalyst switch is contacted.")
    # 1. Legacy discrepancy: Native=999 pruned from allowed [10, 20] & Voice VLAN 50 missing!
    broken_legacy = audit_trunk_pair(
        sw1_vlans=[1, 10, 20, 999],
        sw2_vlans=[1, 10, 20, 999],
        sw1_allowed=[10, 20],
        sw2_allowed=[10, 20],
        sw1_native=999,
        sw2_native=999,
        required_vlans=[10, 20, 50],
    )
    assert broken_legacy["end_to_end_ok"] is False
    assert any("SW1_NATIVE_PRUNED" in i for i in broken_legacy["issues"])
    assert any("VLAN_50_MISSING" in i for i in broken_legacy["issues"])
    print("Legacy broken scenario caught:", broken_legacy["issues"])

    # 2. Reconciled consistent scenario: VLANs 10, 20, 50 (Voice), 999 (Native) created & allowed on BOTH switches
    reconciled = audit_trunk_pair(
        sw1_vlans=[1, 10, 20, 50, 999],
        sw2_vlans=[1, 10, 20, 50, 999],
        sw1_allowed=[10, 20, 50, 999],
        sw2_allowed=[10, 20, 50, 999],
        sw1_native=999,
        sw2_native=999,
        required_vlans=[10, 20, 50],
    )
    assert reconciled["end_to_end_ok"] is True
    assert reconciled["native_frame_format"] == "untagged_default"
    print("Reconciled SW1<->SW2 trunk:", reconciled)

    # 3. DTP nuance: static trunk + nonegotiate stops DTP; dynamic_auto <-> dynamic_auto stays access!
    dtp_safe = evaluate_dtp_link("trunk", "trunk", sw1_nonegotiate=True, sw2_nonegotiate=True)
    dtp_auto = evaluate_dtp_link("dynamic_auto", "dynamic_auto")
    assert dtp_safe["operational_state"] == "trunk" and dtp_safe["dtp_frames_may_still_be_sent"] is False
    assert dtp_auto["operational_state"] == "access_no_trunk"
    print("DTP safe trunk:", dtp_safe)
    print("DTP auto/auto trap:", dtp_auto)


if __name__ == "__main__":
    main()
