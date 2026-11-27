"""Local Python Mock for spec_wl (RF dBm/SNR Physics, Wi-Fi 6/6E/7 & Catalyst 9800 Tags).

No real Cisco Catalyst 9800 WLC, Access Point, CAPWAP tunnel, or 802.11 radio is run.
"""
from __future__ import annotations

import math


def dbm_to_mw(dbm: float) -> float:
    return 10 ** (dbm / 10.0)


def mw_to_dbm(mw: float) -> float:
    if mw <= 0:
        raise ValueError("Power in mW must be positive.")
    return 10.0 * math.log10(mw)


def compute_rf_link(
    tx_power_dbm: float,
    cable_loss_db: float,
    antenna_gain_dbi: float,
    rssi_dbm: float,
    noise_floor_20mhz_dbm: float,
    channel_width_mhz: int = 20,
) -> dict[str, object]:
    """Calculate EIRP, channel-width-adjusted noise floor, and SNR."""
    if channel_width_mhz not in (20, 40, 80, 160, 320):
        raise ValueError(f"Unsupported 802.11 channel width: {channel_width_mhz}")
    eirp_dbm = round(tx_power_dbm - cable_loss_db + antenna_gain_dbi, 2)
    doublings = int(math.log2(channel_width_mhz // 20))
    noise_penalty_db = 3.0 * doublings
    effective_noise = round(noise_floor_20mhz_dbm + noise_penalty_db, 2)
    snr_db = round(rssi_dbm - effective_noise, 2)
    voice_ready = snr_db >= 25.0 and rssi_dbm >= -67.0
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
    allowed_modes = {"wpa3-enterprise", "wpa3-personal-sae", "owe"}
    valid = security_mode.lower() in allowed_modes and pmf.lower() == "mandatory"
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
    if not (wlan_no_shut and policy_profile_no_shut):
        return {
            "ssid_broadcasting": False,
            "mode": "disabled",
            "reason": "Both WLAN and Policy Profile must have 'no shutdown' in Catalyst 9800.",
        }
    if site_tag_local_site:
        return {
            "ssid_broadcasting": True,
            "mode": "central_switching_local_ap",
            "capwap_data_tunnel_udp_5247": True,
        }
    if not flex_profile_assigned:
        return {
            "ssid_broadcasting": False,
            "mode": "misconfigured_flex",
            "reason": "Non-local Site Tag requires a Flex Profile.",
        }
    return {
        "ssid_broadcasting": True,
        "mode": "flexconnect_local_switching" if not central_switching else "flexconnect_central_switching",
        "capwap_data_tunnel_udp_5247": central_switching,
    }


def main() -> None:
    print("Local Python Mock only — no real Catalyst 9800 WLC or RF hardware is invoked.")
    print("20 MHz RF:", compute_rf_link(14.0, 1.0, 4.0, -64.0, -90.0, 20))
    print("80 MHz RF (noise penalty):", compute_rf_link(14.0, 1.0, 4.0, -64.0, -90.0, 80))
    print("6 GHz WPA2 invalid:", check_6ghz_security("wpa2-psk", "optional"))
    print("6 GHz WPA3 valid:", check_6ghz_security("wpa3-enterprise", "mandatory"))
    print("C9800 FlexConnect Local:", resolve_c9800_ap_behavior(True, True, False, False, True))


if __name__ == "__main__":
    main()
