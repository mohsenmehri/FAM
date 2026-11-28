"""Local Python 3 stdlib mock lab for ccna_qos_ssh (DiffServ QoS, VoIP SLA, SSHv2 & SCP/FTP/TFTP).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Cisco device, packet queue, SSH daemon, or file transfer occurs.
"""
from __future__ import annotations

import math


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_finite_nonneg(val: object, name: str) -> float:
    if type(val) is bool or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a real number")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} overflowed float range") from exc
    if not math.isfinite(fval) or fval < 0:
        raise ValueError(f"{name} must be finite and >= 0")
    return fval


def evaluate_voip_qos_sla(
    one_way_delay_ms: float,
    jitter_ms: float,
    packet_loss_pct: float,
) -> dict[str, object]:
    """Evaluate VoIP path against Cisco Enterprise QoS SRND / ITU-T G.114 target thresholds."""
    delay = _require_finite_nonneg(one_way_delay_ms, "one_way_delay_ms")
    jitter = _require_finite_nonneg(jitter_ms, "jitter_ms")
    loss = _require_finite_nonneg(packet_loss_pct, "packet_loss_pct")
    if loss > 100.0:
        raise ValueError("packet_loss_pct cannot exceed 100")

    breaches = []
    if delay > 150.0:
        breaches.append(f"ONE_WAY_DELAY_EXCEEDS_150MS ({delay}ms)")
    if jitter > 30.0:
        breaches.append(f"JITTER_EXCEEDS_30MS ({jitter}ms)")
    if loss > 1.0:
        breaches.append(f"PACKET_LOSS_EXCEEDS_1PCT ({loss}%)")
    return {"voip_sla_met": len(breaches) == 0, "breaches": breaches}


def classify_dscp_marking(traffic_class: str) -> dict[str, object]:
    """Return standard DiffServ DSCP (L3) and 802.1p CoS (L2) markings."""
    table = {
        "voice": {"dscp_name": "EF", "dscp_decimal": 46, "cos_8021p": 5, "queue": "LLQ (Strict Priority + Policer)"},
        "call_signaling": {"dscp_name": "CS3", "dscp_decimal": 24, "cos_8021p": 3, "queue": "CBWFQ Guaranteed"},
        "interactive_video": {"dscp_name": "AF41", "dscp_decimal": 34, "cos_8021p": 4, "queue": "CBWFQ / Priority Video"},
        "best_effort": {"dscp_name": "BE/DF", "dscp_decimal": 0, "cos_8021p": 0, "queue": "Class-Default"},
    }
    if traffic_class not in table:
        raise ValueError(f"Unknown traffic_class: {traffic_class}")
    return {"traffic_class": traffic_class, **table[traffic_class]}


def audit_ssh_prerequisites(
    hostname: str,
    domain_name: str,
    rsa_modulus_bits: int,
    ssh_version: int,
    vty_transport_input: list[str],
    local_or_aaa_auth: bool,
) -> dict[str, object]:
    """Verify Cisco IOS SSHv2 prerequisites and detect insecure Telnet exposure."""
    if not isinstance(hostname, str) or not hostname.strip():
        raise ValueError("hostname must be a non-empty string")
    if not isinstance(domain_name, str):
        raise ValueError("domain_name must be a string")
    if type(rsa_modulus_bits) is not int or rsa_modulus_bits < 0:
        raise ValueError("rsa_modulus_bits must be a non-negative integer")
    if type(ssh_version) is not int or ssh_version not in (1, 2):
        raise ValueError("ssh_version must be 1 or 2")
    _require_bool(local_or_aaa_auth, "local_or_aaa_auth")

    issues = []
    if hostname.strip() in ("Router", "Switch"):
        issues.append("DEFAULT_HOSTNAME_BLOCKS_RSA_KEYGEN")
    if not domain_name.strip():
        issues.append("MISSING_IP_DOMAIN_NAME")
    if rsa_modulus_bits < 768:
        issues.append("RSA_KEY_TOO_SMALL_FOR_SSHV2_MIN_768_REC_2048")
    elif rsa_modulus_bits < 2048:
        issues.append("RSA_KEY_BELOW_MODERN_2048_BIT_RECOMMENDATION")
    if ssh_version != 2:
        issues.append("SSH_VERSION_1_INSECURE")
    if "telnet" in [t.lower() for t in vty_transport_input] or "all" in [t.lower() for t in vty_transport_input]:
        issues.append("CLEARTEXT_TELNET_ALLOWED_ON_VTY")
    if "ssh" not in [t.lower() for t in vty_transport_input]:
        issues.append("SSH_NOT_ENABLED_ON_VTY")
    if not local_or_aaa_auth:
        issues.append("MISSING_LOCAL_OR_AAA_LOGIN_AUTH")

    return {"ssh_ready_and_hardened": len(issues) == 0, "issues": issues}


def audit_file_transfer_protocol(protocol: str) -> dict[str, object]:
    """Compare TFTP, FTP, and SCP/SFTP security properties."""
    p = protocol.upper() if isinstance(protocol, str) else ""
    profiles = {
        "TFTP": {"port": "UDP/69", "authenticated": False, "encrypted": False, "recommended": False},
        "FTP": {"port": "TCP/21 (control) + TCP/20 or passive", "authenticated": True, "encrypted": False, "recommended": False},
        "SCP": {"port": "TCP/22 (over SSH)", "authenticated": True, "encrypted": True, "recommended": True},
        "SFTP": {"port": "TCP/22 (over SSH)", "authenticated": True, "encrypted": True, "recommended": True},
    }
    if p not in profiles:
        raise ValueError(f"Unsupported file transfer protocol: {protocol}")
    return {"protocol": p, **profiles[p]}


def main() -> None:
    sla_ok = evaluate_voip_qos_sla(85.0, 12.0, 0.2)
    sla_bad = evaluate_voip_qos_sla(190.0, 45.0, 2.5)
    assert sla_ok["voip_sla_met"] is True
    assert sla_bad["voip_sla_met"] is False and len(sla_bad["breaches"]) == 3

    ef = classify_dscp_marking("voice")
    assert ef["dscp_decimal"] == 46 and ef["cos_8021p"] == 5

    ssh_fail = audit_ssh_prerequisites("Router", "", 0, 2, ["telnet"], False)
    ssh_ok = audit_ssh_prerequisites("R1-EDGE", "corp.example", 2048, 2, ["ssh"], True)
    assert ssh_fail["ssh_ready_and_hardened"] is False
    assert ssh_ok["ssh_ready_and_hardened"] is True
    assert audit_file_transfer_protocol("SCP")["recommended"] is True
    assert audit_file_transfer_protocol("FTP")["encrypted"] is False

    print("VoIP QoS SLA (OK vs Breach):", sla_ok, sla_bad)
    print("Voice Marking:", ef)
    print("SSH Audit (Fail vs Hardened):", ssh_fail, ssh_ok)
    print("File Transfer (FTP vs SCP):", audit_file_transfer_protocol("FTP"), audit_file_transfer_protocol("SCP"))


if __name__ == "__main__":
    main()
