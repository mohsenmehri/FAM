"""Local Python Mock for spec_cyber (SIEM Correlation, C2 Beaconing, DNS Entropy & NIST 800-61r3).

No real SIEM appliance, EDR sensor, packet capture interface, or live attack is executed.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math
import statistics


def detect_ssh_bruteforce(
    events: list[dict[str, object]],
    threshold: int = 5,
    window_sec: int = 60,
) -> list[dict[str, object]]:
    """Correlate failed SSH authentication events per source IP within a sliding window."""
    by_ip: dict[str, list[int]] = defaultdict(list)
    for ev in events:
        if ev.get("service") == "ssh" and ev.get("outcome") == "failure":
            by_ip[str(ev["src_ip"])].append(int(ev["ts"]))

    alerts = []
    for ip, times in sorted(by_ip.items()):
        times.sort()
        left = 0
        for right, ts in enumerate(times):
            while ts - times[left] > window_sec:
                left += 1
            count = right - left + 1
            if count >= threshold:
                alerts.append({
                    "rule": "SSH_BRUTE_FORCE",
                    "src_ip": ip,
                    "failures_in_window": count,
                    "window_sec": window_sec,
                    "mitre_attack": "T1110.001",
                })
                break
    return alerts


def detect_c2_beaconing(timestamps: list[float], max_cv: float = 0.25) -> dict[str, object]:
    """Detect periodic C2 beaconing using inter-arrival coefficient of variation (CV = std / mean)."""
    if len(timestamps) < 4:
        return {"beaconing_suspected": False, "reason": "need at least 4 observations"}
    ordered = sorted(timestamps)
    deltas = [ordered[i + 1] - ordered[i] for i in range(len(ordered) - 1)]
    mean_d = statistics.mean(deltas)
    stdev_d = statistics.pstdev(deltas)
    cv = stdev_d / mean_d if mean_d > 0 else float("inf")
    return {
        "mean_interval_sec": round(mean_d, 2),
        "stdev_sec": round(stdev_d, 2),
        "cv": round(cv, 4),
        "beaconing_suspected": cv <= max_cv and mean_d > 0,
        "mitre_attack": "T1071.001",
    }


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    val = -sum((c / n) * math.log2(c / n) for c in counts.values())
    return 0.0 if val == 0 else val


def score_dns_tunneling(fqdn: str) -> dict[str, object]:
    """Flag unusually long, high-entropy leftmost DNS labels indicative of tunneling/exfiltration."""
    labels = fqdn.strip(".").split(".")
    leftmost = labels[0] if labels else ""
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
    print("SIEM SSH alerts:", detect_ssh_bruteforce(sample_events))
    print("Beaconing check:", detect_c2_beaconing([0, 60, 123, 181, 244, 302]))
    print("DNS normal:", score_dns_tunneling("www.example.com"))
    print("DNS tunneling candidate:", score_dns_tunneling("a9f4c8e1b70d3e2a55f19c8b4e6d7a2f10c3.exfil.example"))
    print("NIST SP 800-61r3 (2025) CSF 2.0 Functions:", NIST_800_61_R3_CSF2_FUNCTIONS)
    print("NIST SP 800-61r2 (Historical) 4 Phases:", NIST_800_61_R2_HISTORICAL_PHASES)


if __name__ == "__main__":
    main()
