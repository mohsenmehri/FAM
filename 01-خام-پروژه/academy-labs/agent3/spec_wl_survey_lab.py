#!/usr/bin/env python3
"""
Local Mock Lab — spec_wl_survey (Wireless RF Site Survey: Attenuation, RSSI/SNR, 2.4/5 GHz Channel Plan)
Simulates predictive RF link budget for Voice-over-Wi-Fi (-65 dBm / SNR >= 25 dB target),
wall attenuation impact, and 2.4 GHz / 5 GHz co-channel (CCI) & adjacent-channel (ACI) conflict checks.
No real Ekahau Pro hardware, spectrum analyzer, or Cisco Catalyst AP is connected.
"""

import json
import math


WALL_ATTENUATION_DB = {
    "drywall": 3.0,
    "glass_office": 4.0,
    "brick_wall": 8.0,
    "concrete_core": 12.0,
    "elevator_shaft": 20.0,
}

NON_OVERLAPPING_24 = {1, 6, 11}


def fspl_db(distance_m: float, freq_mhz: float) -> float:
    return 20 * math.log10(max(distance_m, 1.0)) + 20 * math.log10(freq_mhz) - 27.55


def evaluate_rf_cell(ap_tx_dbm: float, ap_gain_dbi: float, distance_m: float, freq_mhz: float, walls: list[str], noise_floor_dbm: float = -95.0) -> dict:
    wall_loss = sum(WALL_ATTENUATION_DB[w] for w in walls)
    path_loss = fspl_db(distance_m, freq_mhz) + wall_loss
    rssi = round(ap_tx_dbm + ap_gain_dbi - path_loss, 2)
    snr = round(rssi - noise_floor_dbm, 2)
    return {
        "freq_mhz": freq_mhz,
        "distance_m": distance_m,
        "walls": walls,
        "wall_loss_db": wall_loss,
        "estimated_rssi_dbm": rssi,
        "snr_db": snr,
        "voice_grade_pass": rssi >= -65.0 and snr >= 25.0,
        "data_grade_pass": rssi >= -70.0 and snr >= 20.0,
    }


def audit_24ghz_plan(ap_channels: dict[str, int]) -> dict:
    aci_warnings = [ap for ap, ch in ap_channels.items() if ch not in NON_OVERLAPPING_24]
    channel_counts: dict[int, list[str]] = {}
    for ap, ch in ap_channels.items():
        channel_counts.setdefault(ch, []).append(ap)
    cci_pairs = {str(ch): aps for ch, aps in channel_counts.items() if len(aps) > 1}
    return {
        "channels": ap_channels,
        "aci_overlapping_channel_aps": aci_warnings,
        "cci_shared_channels": cci_pairs,
        "plan_valid": len(aci_warnings) == 0,
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_EKAHAU_OR_AP_HARDWARE",
        "rf_link_budgets": {
            "open_office_5ghz_12m_drywall": evaluate_rf_cell(14.0, 4.0, 12.0, 5180.0, ["drywall"]),
            "behind_concrete_5ghz_14m": evaluate_rf_cell(14.0, 4.0, 14.0, 5180.0, ["concrete_core", "brick_wall"]),
        },
        "channel_24ghz_audit": {
            "bad_plan_with_ch3_ch8": audit_24ghz_plan({"AP-01": 1, "AP-02": 3, "AP-03": 8}),
            "clean_1_6_11_plan": audit_24ghz_plan({"AP-01": 1, "AP-02": 6, "AP-03": 11}),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
