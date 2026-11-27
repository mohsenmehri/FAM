"""Local Python Mock for spec_cyber (SIEM Correlation, C2 Beaconing, DNS Entropy & NIST 800-61r3).

No real SIEM appliance, EDR sensor, packet capture interface, or live attack is executed.
Strict validation rejects non-positive threshold, negative windows/CV, bool timestamps,
and empty/non-string DNS names.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math
import statistics


def _require_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int):
        raise ValueError(f"{name} must be an int (not bool), got {val!r} ({type(val).__name__})")
    return val


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    return float(val)


def detect_ssh_bruteforce(
    events: list[dict[str, object]],
    threshold: int = 5,
    window_sec: int = 60,
) -> list[dict[str, object]]:
    """Correlate failed SSH authentication events per source IP within a sliding window."""
    thresh = _require_int(threshold, "threshold")
    win = _require_int(window_sec, "window_sec")
    if thresh <= 0:
        raise ValueError(f"threshold must be positive, got {thresh}")
    if win < 0:
        raise ValueError(f"window_sec must be non-negative, got {win}")

    by_ip: dict[str, list[int]] = defaultdict(list)
    for ev in events:
        if ev.get("service") == "ssh" and ev.get("outcome") == "failure":
            ts = _require_int(ev.get("ts"), "event.ts")
            src_ip = ev.get("src_ip")
            if not isinstance(src_ip, str) or not src_ip.strip():
                raise ValueError(f"event.src_ip must be a non-empty str, got {src_ip!r}")
            by_ip[src_ip].append(ts)

    alerts = []
    for ip, times in sorted(by_ip.items()):
        times.sort()
        left = 0
        for right, ts in enumerate(times):
            while ts - times[left] > win:
                left += 1
            count = right - left + 1
            if count >= thresh:
                alerts.append({
                    "rule": "SSH_BRUTE_FORCE",
                    "src_ip": ip,
                    "failures_in_window": count,
                    "window_sec": win,
                    "mitre_attack": "T1110.001",
                })
                break
    return alerts


def detect_c2_beaconing(timestamps: list[float], max_cv: float = 0.25) -> dict[str, object]:
    """Detect periodic C2 beaconing using inter-arrival coefficient of variation (CV = std / mean)."""
    cv_limit = _require_finite_num(max_cv, "max_cv")
    if cv_limit < 0:
        raise ValueError(f"max_cv must be non-negative, got {cv_limit}")
    clean_ts = [_require_finite_num(t, "timestamp") for t in timestamps]
    if len(clean_ts) < 4:
        return {"beaconing_suspected": False, "reason": "need at least 4 observations"}
    ordered = sorted(clean_ts)
    deltas = [ordered[i + 1] - ordered[i] for i in range(len(ordered) - 1)]
    mean_d = statistics.mean(deltas)
    stdev_d = statistics.pstdev(deltas)
    cv = stdev_d / mean_d if mean_d > 0 else float("inf")
    return {
        "mean_interval_sec": round(mean_d, 2),
        "stdev_sec": round(stdev_d, 2),
        "cv": round(cv, 4) if math.isfinite(cv) else float("inf"),
        "beaconing_suspected": cv <= cv_limit and mean_d > 0,
        "mitre_attack": "T1071.001",
    }


def shannon_entropy(text: str) -> float:
    if not isinstance(text, str):
        raise ValueError(f"text must be str, got {text!r}")
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    val = -sum((c / n) * math.log2(c / n) for c in counts.values())
    return 0.0 if val == 0 else val


def score_dns_tunneling(fqdn: str) -> dict[str, object]:
    """Flag unusually long, high-entropy leftmost DNS labels indicative of tunneling/exfiltration."""
    if not isinstance(fqdn, str) or not fqdn.strip().strip("."):
        raise ValueError(f"fqdn must be a non-empty domain string, got {fqdn!r}")
    labels = fqdn.strip().strip(".").split(".")
    leftmost = labels[0]
    ent = round(shannon_entropy(leftmost), 3)
    suspicious = len(leftmost) >= 32 and ent >= 3.6
    return {
        "fqdn": fqdn,
        "label_len": len(leftmost),
        "entropy": ent,
        "tunneling_suspected": suspicious,
        "mitre_attack": "T1048.003" if suspicious else None,
    }


NIST_800_61_R3_CSF2_FUNCTIONS = (
    "Govern",
    "Identify",
    "Protect",
    "Detect",
    "Respond",
    "Recover",
)
NIST_800_61_R2_HISTORICAL_PHASES = (
    "Preparation",
    "Detection and Analysis",
    "Containment, Eradication, and Recovery",
    "Post-Incident Activity",
)


def main() -> None:
    print("Local Python Mock only — synthetic log data; no live SIEM or production host is touched.")
    sample_events = [
        {"ts": 100 + i * 5, "src_ip": "198.51.100.44", "service": "ssh", "outcome": "failure"}
        for i in range(6)
    ]
    alerts = detect_ssh_bruteforce(sample_events)
    beacon = detect_c2_beaconing([0, 60, 123, 181, 244, 302])
    normal_dns = score_dns_tunneling("www.example.com")
    tunnel_dns = score_dns_tunneling("a9f4c8e1b70d3e2a55f19c8b4e6d7a2f10c3.exfil.example")
    assert len(alerts) == 1 and alerts[0]["mitre_attack"] == "T1110.001"
    assert beacon["beaconing_suspected"] is True
    assert normal_dns["tunneling_suspected"] is False
    assert tunnel_dns["tunneling_suspected"] is True
    print("SIEM SSH alerts:", alerts)
    print("Beaconing check:", beacon)
    print("DNS normal:", normal_dns)
    print("DNS tunneling candidate:", tunnel_dns)
    print("NIST SP 800-61r3 (2025) CSF 2.0 Functions:", NIST_800_61_R3_CSF2_FUNCTIONS)
    print("NIST SP 800-61r2 (Historical) 4 Phases:", NIST_800_61_R2_HISTORICAL_PHASES)


if __name__ == "__main__":
    main()
