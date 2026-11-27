"""Local Python Mock for spec_wl (RF dBm/SNR Physics, Wi-Fi 6/6E/7 & Catalyst 9800 Tags).

No real Cisco Catalyst 9800 WLC, Access Point, CAPWAP tunnel, or 802.11 radio is run.
Strict typing rejects non-bool Catalyst 9800 flags, non-finite RF values, and negative cable loss.
"""
from __future__ import annotations

import math


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    return float(val)


def dbm_to_mw(dbm: float) -> float:
    val = _require_finite_num(dbm, "dbm")
    return 10 ** (val / 10.0)


def mw_to_dbm(mw: float) -> float:
    val = _require_finite_num(mw, "mw")
    if val <= 0:
        raise ValueError("Power in mW must be positive.")
    return 10.0 * math.log10(val)


def compute_rf_link(
    tx_power_dbm: float,
    cable_loss_db: float,
    antenna_gain_dbi: float,
    rssi_dbm: float,
    noise_floor_20mhz_dbm: float,
    channel_width_mhz: int = 20,
) -> dict[str, object]:
    """Calculate EIRP, channel-width-adjusted noise floor, and SNR."""
    tx = _require_finite_num(tx_power_dbm, "tx_power_dbm")
    loss = _require_finite_num(cable_loss_db, "cable_loss_db")
    if loss < 0:
        raise ValueError(f"cable_loss_db must be non-negative, got {loss}")
    gain = _require_finite_num(antenna_gain_dbi, "antenna_gain_dbi")
    rssi = _require_finite_num(rssi_dbm, "rssi_dbm")
    nf = _require_finite_num(noise_floor_20mhz_dbm, "noise_floor_20mhz_dbm")
    if isinstance(channel_width_mhz, bool) or channel_width_mhz not in (20, 40, 80, 160, 320):
        raise ValueError(f"Unsupported 802.11 channel width: {channel_width_mhz!r}")

    eirp_dbm = round(tx - loss + gain, 2)
    doublings = int(math.log2(channel_width_mhz // 20))
    noise_penalty_db = 3.0 * doublings
    effective_noise = round(nf + noise_penalty_db, 2)
    snr_db = round(rssi - effective_noise, 2)
    voice_ready = snr_db >= 25.0 and rssi >= -67.0
    return {
        "eirp_dbm": eirp_dbm,
        "eirp_mw": round(dbm_to_mw(eirp_dbm), 2),
        "channel_width_mhz": channel_width_mhz,
        "noise_penalty_db": noise_penalty_db,
        "effective_noise_dbm": effective_noise,
        "snr_db": snr_db,
        "enterprise_voice_ready": voice_ready,
    }


def check_6ghz_security(security_mode: str, pmf: str) -> dict[str, object]:
    """Verify Wi-Fi 6E/7 6 GHz mandatory security (WPA3 or OWE + mandatory PMF 802.11w)."""
    if not isinstance(security_mode, str) or not isinstance(pmf, str):
        raise ValueError("security_mode and pmf must be str")
    allowed_modes = {"wpa3-enterprise", "wpa3-personal-sae", "owe"}
    valid = security_mode.strip().lower() in allowed_modes and pmf.strip().lower() == "mandatory"
    return {
        "band": "6 GHz",
        "security_mode": security_mode,
        "pmf": pmf,
        "compliant": valid,
        "note": "Compliant with 6 GHz rules." if valid else "6 GHz forbids WPA2/Open and requires mandatory PMF.",
    }


def resolve_c9800_ap_behavior(
    wlan_no_shut: bool,
    policy_profile_no_shut: bool,
    central_switching: bool,
    site_tag_local_site: bool,
    flex_profile_assigned: bool,
) -> dict[str, object]:
    """Model Cisco Catalyst 9800 Policy Tag + Site Tag switching decision."""
    w_up = _require_bool(wlan_no_shut, "wlan_no_shut")
    p_up = _require_bool(policy_profile_no_shut, "policy_profile_no_shut")
    central = _require_bool(central_switching, "central_switching")
    local_site = _require_bool(site_tag_local_site, "site_tag_local_site")
    flex_ok = _require_bool(flex_profile_assigned, "flex_profile_assigned")

    if not (w_up and p_up):
        return {
            "ssid_broadcasting": False,
            "mode": "disabled",
            "reason": "Both WLAN and Policy Profile must have 'no shutdown' in Catalyst 9800.",
        }
    if local_site:
        return {
            "ssid_broadcasting": True,
            "mode": "central_switching_local_ap",
            "capwap_data_tunnel_udp_5247": True,
        }
    if not flex_ok:
        return {
            "ssid_broadcasting": False,
            "mode": "misconfigured_flex",
            "reason": "Non-local Site Tag requires a Flex Profile.",
        }
    return {
        "ssid_broadcasting": True,
        "mode": "flexconnect_local_switching" if not central else "flexconnect_central_switching",
        "capwap_data_tunnel_udp_5247": central,
    }


def main() -> None:
    print("Local Python Mock only — no real Catalyst 9800 WLC or RF hardware is invoked.")
    rf20 = compute_rf_link(14.0, 1.0, 4.0, -64.0, -90.0, 20)
    rf80 = compute_rf_link(14.0, 1.0, 4.0, -64.0, -90.0, 80)
    assert rf20["snr_db"] == 26.0 and rf20["enterprise_voice_ready"] is True
    assert rf80["snr_db"] == 20.0 and rf80["enterprise_voice_ready"] is False
    assert check_6ghz_security("wpa2-psk", "optional")["compliant"] is False
    assert check_6ghz_security("wpa3-enterprise", "mandatory")["compliant"] is True
    flex = resolve_c9800_ap_behavior(True, True, False, False, True)
    assert flex["ssid_broadcasting"] is True and flex["capwap_data_tunnel_udp_5247"] is False
    print("20 MHz RF:", rf20)
    print("80 MHz RF (noise penalty):", rf80)
    print("6 GHz WPA2 invalid:", check_6ghz_security("wpa2-psk", "optional"))
    print("6 GHz WPA3 valid:", check_6ghz_security("wpa3-enterprise", "mandatory"))
    print("C9800 FlexConnect Local:", flex)


if __name__ == "__main__":
    main()
