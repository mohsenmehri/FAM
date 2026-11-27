"""Local Python Mock for spec_sec (Cisco Secure Firewall TLS/IPS & ISE 802.1X Policy).

Enforces strict Python bool typing on security flags (authenticated, decrypt_enabled, cert_pinned,
snort_signature_match) so truthy strings like "False" cannot bypass 802.1X or TLS controls.
No real Cisco FTD, FMC, Cisco ISE, RADIUS packet, or switch port is executed.
"""
from __future__ import annotations

from dataclasses import dataclass

TLS_BYPASS_CATEGORIES = frozenset({"banking", "healthcare", "government_privacy", "pinned_client"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


@dataclass(frozen=True)
class TlsFlow:
    sni: str
    category: str
    cert_pinned: bool
    snort_signature_match: bool


def evaluate_ftd_tls_and_ips(flow: TlsFlow, decrypt_enabled: bool) -> dict[str, object]:
    """Simulate FTD Outbound Decrypt-Resign policy + Snort 3 inspection visibility."""
    decrypt_flag = _require_bool(decrypt_enabled, "decrypt_enabled")
    cert_pinned = _require_bool(flow.cert_pinned, "flow.cert_pinned")
    sig_match = _require_bool(flow.snort_signature_match, "flow.snort_signature_match")
    if not decrypt_flag:
        return {
            "action": "do_not_decrypt",
            "payload_visible": False,
            "verdict": "allow_blind_to_payload",
            "note": "Without TLS decryption, Snort only sees metadata (IP/SNI/cert), not encrypted payload.",
        }
    if cert_pinned or flow.category in TLS_BYPASS_CATEGORIES:
        reason = "certificate pinning breaks MITM resign" if cert_pinned else f"compliance bypass ({flow.category})"
        return {
            "action": "do_not_decrypt",
            "payload_visible": False,
            "verdict": "allow_metadata_only",
            "note": f"Bypassed TLS decryption: {reason}.",
        }
    verdict = "block_snort_ips" if sig_match else "allow_inspected"
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
    if host_mode not in {"single-host", "multi-domain", "multi-auth", "multi-host"}:
        raise ValueError(f"Unsupported 802.1X host_mode: {host_mode!r}")
    if port_mode not in {"monitor", "low_impact", "closed"}:
        raise ValueError(f"Unsupported 802.1X port_mode: {port_mode!r}")
    authorized: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    voice_count = 0
    data_count = 0

    for sess in sessions:
        domain = str(sess["domain"]).upper()
        auth_ok = _require_bool(sess.get("authenticated"), "sess['authenticated']")
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
    r_no_dec = evaluate_ftd_tls_and_ips(c2_flow, decrypt_enabled=False)
    r_dec = evaluate_ftd_tls_and_ips(c2_flow, decrypt_enabled=True)
    r_bank = evaluate_ftd_tls_and_ips(bank_flow, decrypt_enabled=True)
    assert r_no_dec["verdict"] == "allow_blind_to_payload"
    assert r_dec["verdict"] == "block_snort_ips"
    assert r_bank["action"] == "do_not_decrypt"

    port_sessions = [
        {"mac": "0200.0000.0010", "domain": "VOICE", "authenticated": True, "sgt": 12},
        {"mac": "0200.0000.0020", "domain": "DATA", "authenticated": True, "sgt": 15},
        {"mac": "0200.0000.0030", "domain": "DATA", "authenticated": True, "sgt": 15},
    ]
    md_res = evaluate_8021x_port("multi-domain", "closed", port_sessions)
    assert len(md_res["authorized"]) == 2 and len(md_res["rejected"]) == 1
    print("C2 without decrypt:", r_no_dec)
    print("C2 with decrypt:", r_dec)
    print("Banking compliance bypass:", r_bank)
    print("Multi-domain port result:", md_res)


if __name__ == "__main__":
    main()
