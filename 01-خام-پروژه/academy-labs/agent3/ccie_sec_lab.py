#!/usr/bin/env python3
"""
Local Mock Lab — ccie_sec (CCIE Security v6.1: NTP/PKI/pxGrid Pre-Flight Audit & FTD Packet-Tracer Pipeline)
Simulates (1) Pre-flight NTP clock-skew and DNS/PKI verification across ISE, FMC, FTD, and AD,
and (2) Multi-phase Cisco Secure Firewall (FTD) packet-tracer evaluation (Route -> NAT -> ACP/SGT -> IPS/Decrypt).
No real Cisco ISE, FMC/FTD, ASA, or Active Directory server is connected.
"""

import json


def audit_ntp_dns_preflight(nodes: list[dict], max_skew_sec: int = 30) -> dict:
    failures = []
    for n in nodes:
        if abs(n["clock_skew_sec"]) > max_skew_sec:
            failures.append(f"{n['name']}: skew {n['clock_skew_sec']}s breaks Kerberos/PKI/pxGrid/SAML")
        if not n["dns_forward_reverse_ok"]:
            failures.append(f"{n['name']}: DNS A/PTR mismatch breaks ISE AD join & EST/SCEP certs")
    return {"preflight_passed": len(failures) == 0, "failures": failures}


def ftd_packet_tracer(flow: dict, sgt_table: dict[str, int]) -> dict:
    phases = []
    # Phase 1: Route lookup
    if not flow.get("route_exists", True):
        return {"flow": flow, "result": "DROP", "drop_phase": "ROUTE-LOOKUP"}
    phases.append({"phase": "ROUTE-LOOKUP", "action": "ALLOW", "egress_zone": flow["dst_zone"]})

    # Phase 2: NAT
    nat_ip = flow.get("nat_translated_src", flow["src_ip"])
    phases.append({"phase": "NAT", "action": "ALLOW", "translated_src": nat_ip})

    # Phase 3: Access Control Policy (ACP) + pxGrid SGT
    src_sgt = sgt_table.get(flow["src_ip"], 0)
    if src_sgt == 99:
        phases.append({"phase": "ACCESS-POLICY-SGT", "action": "DROP", "reason": "SGT 99 (Quarantine via ISE pxGrid ANC)"})
        return {"flow": flow, "src_sgt": src_sgt, "result": "DROP", "phases": phases}
    phases.append({"phase": "ACCESS-POLICY-SGT", "action": "ALLOW", "src_sgt": src_sgt})

    # Phase 4: Snort IPS Inspection
    if flow.get("contains_exploit_sig"):
        phases.append({"phase": "SNORT-IPS", "action": "DROP", "reason": "Snort Inline Drop (CVE signature matched)"})
        return {"flow": flow, "src_sgt": src_sgt, "result": "DROP", "phases": phases}
    phases.append({"phase": "SNORT-IPS", "action": "ALLOW"})
    return {"flow": flow, "src_sgt": src_sgt, "result": "ALLOW", "phases": phases}


def main() -> None:
    nodes_bad = [
        {"name": "ISE-PAN-01", "clock_skew_sec": 0, "dns_forward_reverse_ok": True},
        {"name": "FTD-EDGE-01", "clock_skew_sec": 420, "dns_forward_reverse_ok": False},
    ]
    nodes_good = [
        {"name": "ISE-PAN-01", "clock_skew_sec": 1, "dns_forward_reverse_ok": True},
        {"name": "FTD-EDGE-01", "clock_skew_sec": -2, "dns_forward_reverse_ok": True},
    ]
    sgt_map = {"10.10.20.15": 10, "10.10.20.99": 99}

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_ISE_FMC_OR_FTD_HARDWARE",
        "preflight_before_fix": audit_ntp_dns_preflight(nodes_bad),
        "preflight_after_fix": audit_ntp_dns_preflight(nodes_good),
        "packet_tracer_runs": {
            "clean_employee_https": ftd_packet_tracer(
                {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "contains_exploit_sig": False},
                sgt_map,
            ),
            "quarantined_endpoint_sgt99": ftd_packet_tracer(
                {"src_ip": "10.10.20.99", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "contains_exploit_sig": False},
                sgt_map,
            ),
            "employee_with_exploit_payload": ftd_packet_tracer(
                {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "contains_exploit_sig": True},
                sgt_map,
            ),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
