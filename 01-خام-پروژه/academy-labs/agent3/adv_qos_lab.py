"""Local Python Mock for adv_qos (DSCP/PHB Decoder, Token Bucket Policing/Shaping & WRED).

Educational local model only — no live Cisco IOS-XE QoS hardware scheduler or ASIC queue
is contacted.
Models:
1. RFC 2474/2597/3246 DSCP binary/decimal/PHB mapping (CS, AFxy, EF).
2. Single-rate Token Bucket calculation (`Bc = CIR * Tc`) for Policing (drop/re-mark)
   vs Shaping (buffer/delay).
3. WRED linear drop probability between min-threshold and max-threshold.
"""
from __future__ import annotations

import math

NAMED_PHB = {
    "BE": 0,
    "CS1": 8, "AF11": 10, "AF12": 12, "AF13": 14,
    "CS2": 16, "AF21": 18, "AF22": 20, "AF23": 22,
    "CS3": 24, "AF31": 26, "AF32": 28, "AF33": 30,
    "CS4": 32, "AF41": 34, "AF42": 36, "AF43": 38,
    "CS5": 40, "EF": 46, "CS6": 48, "CS7": 56,
}


def _require_int_range(val: object, name: str, lo: int, hi: int) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (lo <= val <= hi):
        raise ValueError(f"{name} must be an int in {lo}..{hi}, got {val!r}")
    return val


def _require_pos_float(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(float(val)) or float(val) <= 0:
        raise ValueError(f"{name} must be a positive finite number, got {val!r}")
    return float(val)


def decode_dscp(dscp_value: int) -> dict[str, object]:
    """Decode a 6-bit DSCP value (0..63) to binary, ToS byte (shifted <<2), and standard PHB name."""
    v = _require_int_range(dscp_value, "dscp_value", 0, 63)
    reverse_map = {val: name for name, val in NAMED_PHB.items()}
    phb = reverse_map.get(v, "NON_STANDARD_OR_LOCAL_USE")
    return {
        "dscp_decimal": v,
        "dscp_6bit_binary": f"{v:06b}",
        "tos_byte_zero_ecn": v << 2,
        "phb_name": phb,
    }


def compute_token_bucket(cir_bps: int, tc_ms: float) -> dict[str, object]:
    """Compute committed burst Bc (bits & bytes) from CIR (bps) and Tc (milliseconds)."""
    cir = _require_int_range(cir_bps, "cir_bps", 8_000, 100_000_000_000)
    tc = _require_pos_float(tc_ms, "tc_ms")
    if tc > 1000.0:
        raise ValueError("tc_ms must be <= 1000 ms")
    bc_bits = cir * (tc / 1000.0)
    return {
        "cir_bps": cir,
        "tc_ms": tc,
        "bc_bits": round(bc_bits, 2),
        "bc_bytes": round(bc_bits / 8.0, 2),
        "voice_friendly_tc": tc <= 10.0,
    }


def compute_wred_drop_probability(
    avg_queue_depth: int,
    min_threshold: int,
    max_threshold: int,
    mark_prob_denominator: int,
) -> dict[str, object]:
    """Compute illustrative WRED drop probability (between 0.0 and 1.0)."""
    q = _require_int_range(avg_queue_depth, "avg_queue_depth", 0, 1_000_000)
    mn = _require_int_range(min_threshold, "min_threshold", 1, 1_000_000)
    mx = _require_int_range(max_threshold, "max_threshold", mn + 1, 2_000_000)
    mpd = _require_int_range(mark_prob_denominator, "mark_prob_denominator", 1, 65535)

    if q < mn:
        prob = 0.0
        zone = "BELOW_MIN_THRESHOLD_NO_WRED_DROP"
    elif q >= mx:
        prob = 1.0
        zone = "AT_OR_ABOVE_MAX_THRESHOLD_FULL_DROP"
    else:
        max_p = 1.0 / mpd
        prob = max_p * ((q - mn) / (mx - mn))
        zone = "LINEAR_RANDOM_EARLY_DROP_ZONE"
    return {"avg_queue_depth": q, "drop_probability": round(prob, 6), "zone": zone}


def main() -> None:
    print("Local Python Mock only — no live Cisco IOS-XE QoS queue or hardware scheduler is contacted.")
    ef = decode_dscp(46)
    af31 = decode_dscp(26)
    assert ef["phb_name"] == "EF" and ef["tos_byte_zero_ecn"] == 184
    assert af31["phb_name"] == "AF31"
    tb = compute_token_bucket(cir_bps=10_000_000, tc_ms=10.0)
    assert tb["bc_bits"] == 100_000.0 and tb["voice_friendly_tc"] is True
    wred_mid = compute_wred_drop_probability(avg_queue_depth=30, min_threshold=20, max_threshold=40, mark_prob_denominator=10)
    assert wred_mid["drop_probability"] == 0.05
    print("DSCP EF:", ef, "| Token Bucket:", tb, "| WRED mid:", wred_mid)


if __name__ == "__main__":
    main()
