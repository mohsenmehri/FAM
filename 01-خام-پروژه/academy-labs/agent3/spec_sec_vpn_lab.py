#!/usr/bin/env python3
"""
FAM Academy Lab — spec_sec_vpn: IKEv2 NAT-T, VTI vs Crypto Map & IPsec SA
Counter Diagnostics Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of NAT-D hash mismatch
triggering UDP 4500 encapsulation, VTI dynamic routing readiness, and asymmetric
encaps/decaps troubleshooting. No live IPsec routers or real crypto sockets.
"""

from __future__ import annotations

import hashlib
import json


def nat_detection_hash(spi_i: str, spi_r: str, ip: str, port: int) -> str:
    return hashlib.sha1(f"{spi_i}:{spi_r}:{ip}:{port}".encode("utf-8")).hexdigest()[:16]


def negotiate_transport(local_ip: str, seen_ip: str, local_port: int, seen_port: int) -> dict:
    h_sent = nat_detection_hash("AAA1", "BBB2", local_ip, local_port)
    h_seen = nat_detection_hash("AAA1", "BBB2", seen_ip, seen_port)
    nat_detected = h_sent != h_seen
    return {
        "nat_detected": nat_detected,
        "ike_auth_and_esp_port": "UDP 4500 (NAT-T)" if nat_detected else "UDP 500 + IP Protocol 50 (ESP)",
    }


def diagnose_ipsec_counters(pkts_encaps: int, pkts_decaps: int) -> str:
    if pkts_encaps == 0 and pkts_decaps == 0:
        return "NO_INTERESTING_TRAFFIC_OR_ROUTE_NOT_POINTING_TO_VTI"
    if pkts_encaps > 0 and pkts_decaps == 0:
        return "ONE_WAY_RETURN_BLOCKED_CHECK_ESP_OR_UDP4500_AND_RETURN_ROUTE"
    return "BIDIRECTIONAL_TUNNEL_HEALTHY"


def main() -> None:
    direct = negotiate_transport("198.51.100.10", "198.51.100.10", 500, 500)
    behind_nat = negotiate_transport("10.0.0.10", "198.51.100.10", 500, 41234)
    assert direct["nat_detected"] is False
    assert behind_nat["nat_detected"] is True and "4500" in behind_nat["ike_auth_and_esp_port"]

    diag = diagnose_ipsec_counters(pkts_encaps=420, pkts_decaps=0)
    assert diag == "ONE_WAY_RETURN_BLOCKED_CHECK_ESP_OR_UDP4500_AND_RETURN_ROUTE"

    print("=== spec_sec_vpn IKEv2 NAT-T & Counter Diagnostics Mock ===")
    print(json.dumps({
        "direct_public_peers": direct,
        "peer_behind_nat_pat": behind_nat,
        "counter_diagnosis_enc420_dec0": diag,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
