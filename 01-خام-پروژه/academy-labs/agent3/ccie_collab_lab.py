#!/usr/bin/env python3
"""
Local Mock Lab — ccie_collab (CCIE Collaboration v3.1: CUCM CSS/Partition, Region/Location CAC & SIP 30s ACK Debug)
Simulates (1) CUCM Calling Search Space (CSS) -> Partition authorization + Region codec & Location CAC check
(explicit Cisco CUCM CAC table: G.711/G.722 = 80 kbps, G.729 = 24 kbps), and (2) CUBE SIP call-flow diagnosis
for 404 Not Found, One-Way Audio (RFC 1918 10/8, 172.16/12, 192.168/16 + RFC 6598 100.64/10 + link-local/loopback
SDP leaks via ipaddress), and 30-second ACK drop. No real Cisco CUCM, Expressway, or CUBE hardware is connected.
"""

import ipaddress
import json

CUCM_LOCATION_CAC_KBPS = {
    "G.711": 80,
    "G.722": 80,
    "G.729": 24,
}

NON_PUBLIC_SDP_NETS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
)


def evaluate_cucm_call(css_partitions: list[str], target_partition: str, inter_region_codec: str, location_avail_kbps: int) -> dict:
    if inter_region_codec not in CUCM_LOCATION_CAC_KBPS:
        raise ValueError(f"Unsupported codec '{inter_region_codec}'; expected one of {sorted(CUCM_LOCATION_CAC_KBPS)}")
    if target_partition not in css_partitions:
        return {"admitted": False, "sip_code": "404 Not Found", "reason": f"CSS lacks access to Partition '{target_partition}'"}
    needed_kbps = CUCM_LOCATION_CAC_KBPS[inter_region_codec]
    if location_avail_kbps < needed_kbps:
        return {
            "admitted": False,
            "sip_code": "488 / Location CAC Reject",
            "reason": f"Need {needed_kbps} kbps for {inter_region_codec}, only {location_avail_kbps} kbps available",
        }
    return {"admitted": True, "sip_code": "200 OK", "codec": inter_region_codec, "bandwidth_reserved_kbps": needed_kbps}


def diagnose_sip_trace(events: list[str], sdp_ip: str) -> dict:
    addr = ipaddress.ip_address(sdp_ip)
    if "ACK" not in events and "200 OK" in events:
        return {
            "symptom": "Call drops cleanly after ~30 seconds (SIP Timer B/H)",
            "root_cause": "Missing ACK for 200 OK — check Contact header NAT/Route or firewall blocking return SIP signaling",
        }
    if any(addr in net for net in NON_PUBLIC_SDP_NETS):
        return {
            "symptom": "Call connects but One-Way / No-Way Audio",
            "root_cause": f"Non-public IP {sdp_ip} leaked in SDP c=IN IP4 toward ITSP — fix CUBE bind/SIP Profile NAT",
        }
    return {"symptom": "Healthy Two-Way Audio", "root_cause": None}


def main() -> None:
    css_denied = evaluate_cucm_call(["PT_INTERNAL", "PT_LOCAL"], "PT_INTL", "G.711", 512)
    cac_denied = evaluate_cucm_call(["PT_INTERNAL", "PT_WAN"], "PT_WAN", "G.711", 40)
    cac_ok = evaluate_cucm_call(["PT_INTERNAL", "PT_WAN"], "PT_WAN", "G.729", 40)

    ack_drop = diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK"], "203.0.113.5")
    sdp_10 = diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK", "ACK"], "10.10.50.12")
    sdp_172 = diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK", "ACK"], "172.16.50.12")
    sdp_ok = diagnose_sip_trace(["INVITE", "180 Ringing", "200 OK", "ACK"], "203.0.113.5")

    assert css_denied["admitted"] is False and cac_denied["admitted"] is False and cac_ok["admitted"] is True
    assert "30 seconds" in ack_drop["symptom"]
    assert "One-Way" in sdp_10["symptom"] and "One-Way" in sdp_172["symptom"]
    assert sdp_ok["root_cause"] is None

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_CUCM_OR_CUBE_HARDWARE",
        "cucm_call_admission": {
            "css_missing_intl_partition": css_denied,
            "wan_cac_exhausted_g711": cac_denied,
            "wan_admitted_with_g729": cac_ok,
        },
        "sip_trace_diagnostics": {
            "thirty_second_drop": ack_drop,
            "one_way_audio_private_sdp_10": sdp_10,
            "one_way_audio_private_sdp_172_16": sdp_172,
            "healthy_call": sdp_ok,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
