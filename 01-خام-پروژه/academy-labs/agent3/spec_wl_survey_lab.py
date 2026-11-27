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


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval):
        raise ValueError(f"{name} must be a finite number, got {val!r}")
    return fval


def fspl_db(distance_m: float, freq_mhz: float) -> float:
    dist = _require_finite_num(distance_m, "distance_m")
    freq = _require_finite_num(freq_mhz, "freq_mhz")
    if dist <= 0:
        raise ValueError(f"distance_m must be > 0, got {dist!r}")
    if freq <= 0:
        raise ValueError(f"freq_mhz must be > 0, got {freq!r}")
    return 20.0 * math.log10(max(dist, 1.0)) + 20.0 * math.log10(freq) - 27.55


def evaluate_rf_cell(ap_tx_dbm: float, ap_gain_dbi: float, distance_m: float, freq_mhz: float, walls: list[str], noise_floor_dbm: float = -95.0) -> dict:
    # Conservative predictive assumption: 0 dBi isotropic client Rx antenna gain (Ekahau baseline convention)
    tx = _require_finite_num(ap_tx_dbm, "ap_tx_dbm")
    gain = _require_finite_num(ap_gain_dbi, "ap_gain_dbi")
    nf = _require_finite_num(noise_floor_dbm, "noise_floor_dbm")
    if not isinstance(walls, list):
        raise ValueError(f"walls must be a list of wall types, got {type(walls).__name__}")
    for w in walls:
        if not isinstance(w, str) or w not in WALL_ATTENUATION_DB:
            raise ValueError(f"Unknown wall type {w!r}; expected one of {sorted(WALL_ATTENUATION_DB)}")
    wall_loss = sum(WALL_ATTENUATION_DB[w] for w in walls)
    path_loss = fspl_db(distance_m, freq_mhz) + wall_loss
    rssi_exact = tx + gain - path_loss
    snr_exact = rssi_exact - nf
    return {
        "freq_mhz": float(freq_mhz),
        "distance_m": float(distance_m),
        "walls": walls,
        "wall_loss_db": wall_loss,
        "estimated_rssi_dbm": round(rssi_exact, 2),
        "snr_db": round(snr_exact, 2),
        "voice_grade_pass": rssi_exact >= -65.0 and snr_exact >= 25.0,
        "data_grade_pass": rssi_exact >= -70.0 and snr_exact >= 20.0,
    }


def audit_24ghz_plan(ap_channels: dict[str, int]) -> dict:
    if not isinstance(ap_channels, dict):
        raise ValueError(f"ap_channels must be a dict, got {type(ap_channels).__name__}")
    for ap, ch in ap_channels.items():
        if not isinstance(ap, str) or not ap.strip():
            raise ValueError(f"AP name must be a non-empty str, got {ap!r}")
        if isinstance(ch, bool) or not isinstance(ch, int) or not (1 <= ch <= 14):
            raise ValueError(f"2.4 GHz channel for {ap} must be an int in [1, 14] (not bool), got {ch!r}")
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
