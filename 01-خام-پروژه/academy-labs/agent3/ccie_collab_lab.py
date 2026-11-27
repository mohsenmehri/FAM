#!/usr/bin/env python3
"""
Local Mock Lab — ccie_collab (CCIE Collaboration v3.1: CUCM CSS/Partition, Region/Location CAC & SIP 30s ACK Debug)
Simulates (1) CUCM Calling Search Space (CSS) -> Partition authorization + Region codec & Location CAC check,
and (2) CUBE SIP call-flow diagnosis for 404 Not Found, One-Way Audio (SDP private IP), and 30-second ACK drop.
No real Cisco CUCM, Expressway, or CUBE hardware is connected.
"""

import json


def evaluate_cucm_call(css_partitions: list[str], target_partition: str, inter_region_codec: str, location_avail_kbps: int) -> dict:
    if target_partition not in css_partitions:
        return {"admitted": False, "sip_code": "404 Not Found", "reason": f"CSS lacks access to Partition '{target_partition}'"}
    needed_kbps = 80 if inter_region_codec == "G.711" else 24
    if location_avail_kbps < needed_kbps:
        return {
            "admitted": False,
            "sip_code": "488 / Location CAC Reject",
            "reason": f"Need {needed_kbps} kbps for {inter_region_codec}, only {location_avail_kbps} kbps available",
        }
    return {"admitted": True, "sip_code": "200 OK", "codec": inter_region_codec, "bandwidth_reserved_kbps": needed_kbps}


def diagnose_sip_trace(events: list[str], sdp_ip: str) -> dict:
    if "ACK" not in events and "200 OK" in events:
        return {
            "symptom": "Call drops cleanly after ~30 seconds (SIP Timer B/H)",
            "root_cause": "Missing ACK for 200 OK — check Contact header NAT/Route or firewall blocking return SIP signaling",
        }
    if sdp_ip.startswith("10.") or sdp_ip.startswith("192.168."):
        return {
            "symptom": "Call connects but One-Way / No-Way Audio",
            "root_cause": f"Private IP {sdp_ip} leaked in SDP c=IN IP4 toward ITSP — fix CUBE bind/SIP Profile NAT",
        }
    return {"symptom": "Healthy Two-Way Audio", "root_cause": None}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_CUCM_OR_CUBE_HARDWARE",
        "cucm_call_admission": {
            "css_missing_intl_partition": evaluate_cucm_call(["PT_INTERNAL", "PT_LOCAL"], "PT_INTL", "G.711", 512),
            "wan_cac_exhausted_g711": evaluate_cucm_call(["PT_INTERNAL", "PT_WAN"], "PT_WAN", "G.711", 40),
            "wan_admitted_with_g729": evaluate_cucm_call(["PT_INTERNAL", "PT_WAN"], "PT_WAN", "G.729", 40),
        },
        "sip_trace_diagnostics": {
            "thirty_second_drop": diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK"], "203.0.113.5"),
            "one_way_audio_private_sdp": diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK", "ACK"], "10.10.50.12"),
            "healthy_call": diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK", "ACK"], "203.0.113.5"),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
