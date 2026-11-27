#!/usr/bin/env python3
"""
FAM Academy Lab — auto_19: Model-Driven Streaming Telemetry (gNMI/MDT),
Compact Binary Encoding vs JSON & Alert Hysteresis Local Mock.
Execution boundary: Pure Python 3 stdlib educational model comparing SNMP
polling vs MDT on-change/sample push, compact binary struct vs JSON payload
sizes, and hysteresis-based alerting (enforcing clear_thresh < high_thresh).
No live gNMI router, InfluxDB, or Grafana.
"""

from __future__ import annotations

import json
import math
import struct


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    return float(val)


def _require_non_neg_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val < 0:
        raise ValueError(f"{name} must be a non-negative int (not bool), got {val!r}")
    return val


def encode_compact_metric(ts: int, if_id: int, in_octets: int, cpu_pct: float) -> bytes:
    """Compact fixed binary struct (illustrative of binary efficiency vs verbose JSON)."""
    t = _require_non_neg_int(ts, "ts")
    i = _require_non_neg_int(if_id, "if_id")
    o = _require_non_neg_int(in_octets, "in_octets")
    c = _require_finite_num(cpu_pct, "cpu_pct")
    if not (0.0 <= c <= 100.0):
        raise ValueError(f"cpu_pct must be within 0..100, got {c}")
    return struct.pack("!IHQf", t, i, o, c)


def evaluate_alert_hysteresis(cpu_samples: list[float], high_thresh: float = 85.0, clear_thresh: float = 70.0) -> list[dict]:
    hi = _require_finite_num(high_thresh, "high_thresh")
    lo = _require_finite_num(clear_thresh, "clear_thresh")
    if lo >= hi:
        raise ValueError(f"clear_thresh ({lo}) must be strictly less than high_thresh ({hi})")
    firing = False
    transitions = []
    for idx, raw_val in enumerate(cpu_samples):
        val = _require_finite_num(raw_val, f"cpu_samples[{idx}]")
        if not firing and val >= hi:
            firing = True
            transitions.append({"sample": idx, "cpu": val, "event": "ALERT_FIRING"})
        elif firing and val <= lo:
            firing = False
            transitions.append({"sample": idx, "cpu": val, "event": "ALERT_RESOLVED"})
    return transitions


def main() -> None:
    sample_record = {
        "timestamp": 1764201600,
        "interface_id": 101,
        "in_octets": 987654321012,
        "cpu_utilization_percent": 87.5,
    }
    json_bytes = json.dumps(sample_record).encode("utf-8")
    bin_bytes = encode_compact_metric(1764201600, 101, 987654321012, 87.5)
    assert len(bin_bytes) < len(json_bytes)

    # Flapping CPU near 85% would spam naive threshold alerts; hysteresis fires once!
    cpu_series = [60, 86, 83, 87, 82, 86, 68, 65]
    events = evaluate_alert_hysteresis(cpu_series, high_thresh=85.0, clear_thresh=70.0)
    assert len(events) == 2 and events[0]["event"] == "ALERT_FIRING" and events[1]["event"] == "ALERT_RESOLVED"

    # On-change telemetry detects 3-second link flap that 300s SNMP polling typically misses!
    snmp_poll_interval_s = 300
    flap_duration_s = 3
    missed_by_snmp_poll = flap_duration_s < snmp_poll_interval_s

    print("=== auto_19 Streaming Telemetry & Alert Hysteresis Local Mock ===")
    print(json.dumps({
        "json_payload_bytes": len(json_bytes),
        "compact_binary_bytes": len(bin_bytes),
        "size_reduction_percent": round((1 - len(bin_bytes) / len(json_bytes)) * 100, 1),
        "short_flap_shorter_than_5min_snmp_poll": missed_by_snmp_poll,
        "hysteresis_alert_transitions": events,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
