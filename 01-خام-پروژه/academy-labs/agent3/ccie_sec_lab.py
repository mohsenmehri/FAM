#!/usr/bin/env python3
"""
Local Mock Lab — ccie_sec (CCIE Security v6.1: NTP/PKI/pxGrid Pre-Flight Audit & FTD Packet-Tracer Pipeline)
Simulates (1) Pre-flight NTP clock-skew (distinguishing operational NTP warning >30s from RFC 4120 / AD
Kerberos default MaxClockSkew >300s failure) and strict-boolean DNS A/PTR checks across ISE/FMC/FTD/AD, and
(2) Multi-phase Cisco Secure Firewall (FTD) packet-tracer evaluation (Route -> NAT -> ACP/SGT -> TLS Decrypt -> Snort IPS)
with strict Python bool validation on all security control flags.
No real Cisco ISE, FMC/FTD, ASA, or Active Directory server is connected.
"""

import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def audit_ntp_dns_preflight(
    nodes: list[dict],
    ops_warning_skew_sec: int = 30,
    kerberos_max_skew_sec: int = 300,
) -> dict:
    failures = []
    warnings = []
    for n in nodes:
        skew_raw = n["clock_skew_sec"]
        if isinstance(skew_raw, bool) or not isinstance(skew_raw, (int, float)):
            raise ValueError(f"{n['name']}: clock_skew_sec must be numeric, got {skew_raw!r}")
        skew = abs(skew_raw)
        dns_ok = _require_bool(n.get("dns_forward_reverse_ok"), f"{n['name']}.dns_forward_reverse_ok")
        if skew > kerberos_max_skew_sec:
            failures.append(
                f"{n['name']}: skew {skew_raw}s exceeds RFC 4120 / AD Kerberos default 300s (5-min) tolerance (KRB_AP_ERR_SKEW)"
            )
        elif skew > ops_warning_skew_sec:
            warnings.append(
                f"{n['name']}: skew {skew_raw}s exceeds {ops_warning_skew_sec}s operational NTP target (within 300s Kerberos default, fix NTP)"
            )
        if not dns_ok:
            failures.append(f"{n['name']}: DNS A/PTR mismatch breaks ISE AD join & EST/SCEP certs")
    return {"preflight_passed": len(failures) == 0, "failures": failures, "warnings": warnings}


def ftd_packet_tracer(flow: dict, sgt_table: dict[str, int]) -> dict:
    route_exists = _require_bool(flow.get("route_exists", True), "flow['route_exists']")
    tls_decrypted = _require_bool(flow.get("tls_decrypted", True), "flow['tls_decrypted']")
    has_exploit = _require_bool(flow.get("contains_exploit_sig", False), "flow['contains_exploit_sig']")

    phases = []
    # Phase 1: Route lookup
    if not route_exists:
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

    # Phase 4: TLS Decryption visibility gate for encrypted HTTPS (443)
    encrypted_tls = flow.get("dst_port") == 443
    if encrypted_tls and not tls_decrypted:
        phases.append({
            "phase": "TLS-DECRYPT",
            "action": "DO-NOT-DECRYPT",
            "note": "Encrypted payload opaque to Snort IPS; only metadata (IP/SNI/cert) visible",
        })
        phases.append({"phase": "SNORT-IPS", "action": "BLIND_BYPASS"})
        return {"flow": flow, "src_sgt": src_sgt, "result": "ALLOW_UNINSPECTED_TLS", "phases": phases}
    if encrypted_tls:
        phases.append({"phase": "TLS-DECRYPT", "action": "DECRYPT-RESIGN"})

    # Phase 5: Snort IPS Inspection
    if has_exploit:
        phases.append({"phase": "SNORT-IPS", "action": "DROP", "reason": "Snort Inline Drop (CVE signature matched)"})
        return {"flow": flow, "src_sgt": src_sgt, "result": "DROP", "phases": phases}
    phases.append({"phase": "SNORT-IPS", "action": "ALLOW"})
    return {"flow": flow, "src_sgt": src_sgt, "result": "ALLOW", "phases": phases}


def main() -> None:
    nodes_bad = [
        {"name": "ISE-PAN-01", "clock_skew_sec": 0, "dns_forward_reverse_ok": True},
        {"name": "FTD-EDGE-01", "clock_skew_sec": 420, "dns_forward_reverse_ok": False},
    ]
    nodes_warn_only = [
        {"name": "ISE-PAN-01", "clock_skew_sec": 45, "dns_forward_reverse_ok": True},
    ]
    nodes_good = [
        {"name": "ISE-PAN-01", "clock_skew_sec": 1, "dns_forward_reverse_ok": True},
        {"name": "FTD-EDGE-01", "clock_skew_sec": -2, "dns_forward_reverse_ok": True},
    ]
    sgt_map = {"10.10.20.15": 10, "10.10.20.99": 99}

    pf_bad = audit_ntp_dns_preflight(nodes_bad)
    pf_warn = audit_ntp_dns_preflight(nodes_warn_only)
    pf_good = audit_ntp_dns_preflight(nodes_good)
    assert pf_bad["preflight_passed"] is False and len(pf_bad["failures"]) == 2
    assert pf_warn["preflight_passed"] is True and len(pf_warn["warnings"]) == 1
    assert pf_good["preflight_passed"] is True and pf_good["warnings"] == []

    clean_https = ftd_packet_tracer(
        {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "tls_decrypted": True, "contains_exploit_sig": False},
        sgt_map,
    )
    quarantined = ftd_packet_tracer(
        {"src_ip": "10.10.20.99", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "tls_decrypted": True, "contains_exploit_sig": False},
        sgt_map,
    )
    exploit_decrypted = ftd_packet_tracer(
        {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "tls_decrypted": True, "contains_exploit_sig": True},
        sgt_map,
    )
    exploit_blind_tls = ftd_packet_tracer(
        {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC_APP", "tls_decrypted": False, "contains_exploit_sig": True},
        sgt_map,
    )
    assert clean_https["result"] == "ALLOW"
    assert quarantined["result"] == "DROP"
    assert exploit_decrypted["result"] == "DROP"
    assert exploit_blind_tls["result"] == "ALLOW_UNINSPECTED_TLS"

    report = {
        "mode": "LOCAL_MOCK_NO_REAL_ISE_FMC_OR_FTD_HARDWARE",
        "preflight_before_fix": pf_bad,
        "preflight_ops_warning_within_kerberos_300s": pf_warn,
        "preflight_after_fix": pf_good,
        "packet_tracer_runs": {
            "clean_employee_https": clean_https,
            "quarantined_endpoint_sgt99": quarantined,
            "employee_with_exploit_payload_decrypted": exploit_decrypted,
            "employee_with_exploit_payload_blind_without_tls_decrypt": exploit_blind_tls,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
