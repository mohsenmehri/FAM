"""Local Python 3 stdlib mock lab for ccna_wl (2.4GHz Channels, Local vs FlexConnect, CAPWAP & WPA3).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Access Point, Cisco WLC, RF spectrum, or CAPWAP tunnel is executed.
"""
from __future__ import annotations


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def check_24ghz_channel_overlap(ch_a: int, ch_b: int) -> dict[str, object]:
    """Check whether two 2.4GHz 20MHz Wi-Fi channels (1..11) overlap."""
    for name, ch in (("ch_a", ch_a), ("ch_b", ch_b)):
        if type(ch) is not int or not (1 <= ch <= 11):
            raise ValueError(f"{name} must be an integer channel in 1..11")
    separation = abs(ch_a - ch_b)
    if ch_a == ch_b:
        relation = "CO_CHANNEL_CONTENTION"
        overlapping = True
    elif separation < 5:
        relation = "ADJACENT_CHANNEL_INTERFERENCE"
        overlapping = True
    else:
        relation = "NON_OVERLAPPING"
        overlapping = False
    return {
        "channels": (ch_a, ch_b),
        "separation": separation,
        "overlapping": overlapping,
        "relation": relation,
    }


def audit_ap_wlc_switchports(
    ap_mode: str,
    ap_switchport_mode: str,
    wlc_switchport_mode: str,
) -> dict[str, object]:
    """Audit switchport Access/Trunk alignment for Local Mode vs FlexConnect AP architectures.

    Note: Corrects the inverted legacy quiz answer (in Local Mode, AP port = access, WLC port = trunk!).
    """
    if ap_mode not in ("local", "flexconnect_local_switching"):
        raise ValueError("ap_mode must be 'local' or 'flexconnect_local_switching'")
    for name, mode in (("ap_switchport_mode", ap_switchport_mode), ("wlc_switchport_mode", wlc_switchport_mode)):
        if mode not in ("access", "trunk"):
            raise ValueError(f"{name} must be 'access' or 'trunk'")

    expected_ap = "access" if ap_mode == "local" else "trunk"
    expected_wlc = "trunk"
    issues = []
    if ap_switchport_mode != expected_ap:
        issues.append(f"AP_PORT_MISMATCH: {ap_mode} expects '{expected_ap}', got '{ap_switchport_mode}'")
    if wlc_switchport_mode != expected_wlc:
        issues.append(f"WLC_PORT_MISMATCH: WLC carrying multiple WLAN VLANs expects 'trunk', got '{wlc_switchport_mode}'")

    return {
        "ap_mode": ap_mode,
        "capwap_ports": {"control": "UDP/5246 (DTLS encrypted by default)", "data": "UDP/5247 (unencrypted by default unless DTLS Data enabled)"},
        "architecture_valid": len(issues) == 0,
        "issues": issues,
    }


def audit_wlan_security(standard: str, pmf_enabled: bool = True) -> dict[str, object]:
    """Evaluate Wi-Fi security protocol resistance to offline dictionary attacks."""
    _require_bool(pmf_enabled, "pmf_enabled")
    profiles = {
        "WEP": {"deprecated": True, "offline_dict_resistant": False, "recommended": False},
        "WPA-TKIP": {"deprecated": True, "offline_dict_resistant": False, "recommended": False},
        "WPA2-Personal": {"deprecated": False, "offline_dict_resistant": False, "recommended": False},
        "WPA3-Personal": {"deprecated": False, "offline_dict_resistant": True, "recommended": pmf_enabled},
        "WPA3-Enterprise": {"deprecated": False, "offline_dict_resistant": True, "recommended": pmf_enabled},
    }
    if standard not in profiles:
        raise ValueError(f"Unsupported WLAN security standard: {standard}")
    res = dict(profiles[standard])
    if standard.startswith("WPA3") and not pmf_enabled:
        res["warning"] = "WPA3 mandates Protected Management Frames (PMF / 802.11w)"
    return {"standard": standard, "pmf_enabled": pmf_enabled, **res}


def main() -> None:
    ov_bad = check_24ghz_channel_overlap(1, 3)
    ov_ok = check_24ghz_channel_overlap(1, 6)
    assert ov_bad["relation"] == "ADJACENT_CHANNEL_INTERFERENCE"
    assert ov_ok["overlapping"] is False

    # Local Mode: AP = Access, WLC = Trunk (correcting inverted legacy quiz option!)
    local_ok = audit_ap_wlc_switchports("local", "access", "trunk")
    local_inverted = audit_ap_wlc_switchports("local", "trunk", "access")
    flex_ok = audit_ap_wlc_switchports("flexconnect_local_switching", "trunk", "trunk")
    assert local_ok["architecture_valid"] is True
    assert local_inverted["architecture_valid"] is False and len(local_inverted["issues"]) == 2
    assert flex_ok["architecture_valid"] is True

    wpa2 = audit_wlan_security("WPA2-Personal", True)
    wpa3 = audit_wlan_security("WPA3-Personal", True)
    assert wpa2["offline_dict_resistant"] is False and wpa3["offline_dict_resistant"] is True

    print("2.4GHz Overlap (1 vs 3, 1 vs 6):", ov_bad, ov_ok)
    print("WLC Local Mode OK:", local_ok)
    print("WLC Local Mode Inverted (Legacy Bug Catch):", local_inverted)
    print("FlexConnect Local Switching:", flex_ok)
    print("WLAN Security (WPA2 vs WPA3):", wpa2, wpa3)


if __name__ == "__main__":
    main()
