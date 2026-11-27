"""Local Python Mock for spec_sec (Cisco Secure Firewall TLS/IPS & ISE 802.1X Policy).

No real Cisco FTD, FMC, Cisco ISE, RADIUS packet, or switch port is executed.
"""
from __future__ import annotations

from dataclasses import dataclass

TLS_BYPASS_CATEGORIES = frozenset({"banking", "healthcare", "government_privacy", "pinned_client"})


@dataclass(frozen=True)
class TlsFlow:
    sni: str
    category: str
    cert_pinned: bool
    snort_signature_match: bool


def evaluate_ftd_tls_and_ips(flow: TlsFlow, decrypt_enabled: bool) -> dict[str, object]:
    """Simulate FTD Outbound Decrypt-Resign policy + Snort 3 inspection visibility."""
    if not decrypt_enabled:
        return {
            "action": "do_not_decrypt",
            "payload_visible": False,
            "verdict": "allow_blind_to_payload",
            "note": "Without TLS decryption, Snort only sees metadata (IP/SNI/cert), not encrypted payload.",
        }
    if flow.cert_pinned or flow.category in TLS_BYPASS_CATEGORIES:
        reason = "certificate pinning breaks MITM resign" if flow.cert_pinned else f"compliance bypass ({flow.category})"
        return {
            "action": "do_not_decrypt",
            "payload_visible": False,
            "verdict": "allow_metadata_only",
            "note": f"Bypassed TLS decryption: {reason}.",
        }
    verdict = "block_snort_ips" if flow.snort_signature_match else "allow_inspected"
    return {
        "action": "decrypt_resign",
        "payload_visible": True,
        "verdict": verdict,
        "note": "Decrypt-Resign exposed payload to Snort 3 inspection.",
    }


def evaluate_8021x_port(
    host_mode: str,
    port_mode: str,
    sessions: list[dict[str, object]],
) -> dict[str, object]:
    """Simulate Cisco switch 802.1X host-mode and authorization policy."""
    authorized: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    voice_count = 0
    data_count = 0

    for sess in sessions:
        domain = str(sess["domain"]).upper()
        auth_ok = bool(sess["authenticated"])
        if not auth_ok:
            if port_mode == "monitor":
                authorized.append({**sess, "enforcement": "monitor_open_logged"})
            elif port_mode == "low_impact":
                authorized.append({**sess, "enforcement": "pre_auth_acl_dhcp_dns_only"})
            else:
                rejected.append({**sess, "reason": "closed_mode_eapol_only"})
            continue

        if host_mode == "single-host" and len(authorized) >= 1:
            rejected.append({**sess, "reason": "single-host allows only 1 authenticated MAC"})
            continue
        if host_mode == "multi-domain":
            if domain == "VOICE" and voice_count >= 1:
                rejected.append({**sess, "reason": "multi-domain allows max 1 VOICE MAC"})
                continue
            if domain == "DATA" and data_count >= 1:
                rejected.append({**sess, "reason": "multi-domain allows max 1 DATA MAC"})
                continue
            if domain == "VOICE":
                voice_count += 1
            else:
                data_count += 1

        authorized.append({**sess, "enforcement": f"authorized_sgt_{sess.get('sgt', 'none')}"})

    return {
        "host_mode": host_mode,
        "port_mode": port_mode,
        "authorized": authorized,
        "rejected": rejected,
    }


def main() -> None:
    print("Local Python Mock only — no real FTD, FMC, Cisco ISE, or switch is contacted.")
    c2_flow = TlsFlow("cdn-update.example", "uncategorized", False, True)
    bank_flow = TlsFlow("bank.example", "banking", False, False)
    print("C2 without decrypt:", evaluate_ftd_tls_and_ips(c2_flow, decrypt_enabled=False))
    print("C2 with decrypt:", evaluate_ftd_tls_and_ips(c2_flow, decrypt_enabled=True))
    print("Banking compliance bypass:", evaluate_ftd_tls_and_ips(bank_flow, decrypt_enabled=True))

    port_sessions = [
        {"mac": "0200.0000.0010", "domain": "VOICE", "authenticated": True, "sgt": 12},
        {"mac": "0200.0000.0020", "domain": "DATA", "authenticated": True, "sgt": 15},
        {"mac": "0200.0000.0030", "domain": "DATA", "authenticated": True, "sgt": 15},
    ]
    print("Multi-domain port result:", evaluate_8021x_port("multi-domain", "closed", port_sessions))


if __name__ == "__main__":
    main()
