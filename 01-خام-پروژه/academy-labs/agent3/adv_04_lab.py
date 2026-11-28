"""Local Python 3 stdlib mock lab for adv_04 (Control/Data Plane CEF, MTU/MSS PMTUD & Asymmetric Routing).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Cisco router, GRE/IPsec tunnel, stateful firewall, or ICMP probe is executed.
"""
from __future__ import annotations


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def compute_tunnel_mtu_mss(
    underlay_mtu: int,
    encapsulation: str,
    ipv4_tcp_header_bytes: int = 40,
) -> dict[str, object]:
    """Calculate exact tunnel IP MTU, TCP MSS, and IOS vs Linux/Windows DF ping payload sizes."""
    if type(underlay_mtu) is not int or not (576 <= underlay_mtu <= 9216):
        raise ValueError("underlay_mtu must be an integer in 576..9216")
    if type(ipv4_tcp_header_bytes) is not int or ipv4_tcp_header_bytes < 40:
        raise ValueError("ipv4_tcp_header_bytes must be >= 40")

    overheads = {
        "none_ethernet": 0,
        "gre_ipv4": 24,            # 20B outer IPv4 + 4B GRE
        "gre_over_ipsec_safe": 100,  # Conservative operational budget (typical 50-76+B -> MTU 1400 / MSS 1360)
    }
    if encapsulation not in overheads:
        raise ValueError(f"Unsupported encapsulation: {encapsulation}")

    ip_mtu = underlay_mtu - overheads[encapsulation]
    tcp_mss = ip_mtu - ipv4_tcp_header_bytes
    icmp_payload_linux_win = ip_mtu - 28  # 20B IPv4 + 8B ICMP
    return {
        "encapsulation": encapsulation,
        "underlay_mtu": underlay_mtu,
        "ip_mtu": ip_mtu,
        "ip_tcp_adjust_mss": tcp_mss,
        "ios_ping_df_total_size": ip_mtu,
        "linux_win_ping_df_payload": icmp_payload_linux_win,
    }


def simulate_pmtud_packet(
    packet_size_bytes: int,
    path_mtu_bytes: int,
    df_bit: bool,
    icmp_frag_needed_allowed: bool,
) -> dict[str, object]:
    """Simulate why small pings succeed while large HTTPS packets hit a PMTUD Blackhole."""
    if type(packet_size_bytes) is not int or packet_size_bytes <= 0:
        raise ValueError("packet_size_bytes must be a positive integer")
    if type(path_mtu_bytes) is not int or path_mtu_bytes < 576:
        raise ValueError("path_mtu_bytes must be an integer >= 576")
    _require_bool(df_bit, "df_bit")
    _require_bool(icmp_frag_needed_allowed, "icmp_frag_needed_allowed")

    if packet_size_bytes <= path_mtu_bytes:
        return {"outcome": "DELIVERED", "reason": "PACKET_FITS_PATH_MTU"}
    if not df_bit:
        return {"outcome": "FRAGMENTED_AND_DELIVERED", "reason": "DF_ZERO_ALLOWED_ROUTER_FRAGMENTATION"}
    if icmp_frag_needed_allowed:
        return {"outcome": "PMTUD_CONVERGED", "reason": "ICMP_TYPE3_CODE4_LOWERED_SENDER_MSS"}
    return {"outcome": "PMTUD_BLACKHOLE_HANG", "reason": "DF_1_DROPPED_AND_ICMP_TYPE3_CODE4_BLOCKED"}


def evaluate_asymmetric_flow(
    outbound_fw: str,
    return_fw: str,
    fw_state_synced: bool,
    urpf_strict_on_return: bool = False,
) -> dict[str, object]:
    """Simulate TCP flow across symmetric vs asymmetric Stateful Firewalls and uRPF Strict Mode."""
    if not isinstance(outbound_fw, str) or not outbound_fw.strip():
        raise ValueError("outbound_fw must be a non-empty string")
    if not isinstance(return_fw, str) or not return_fw.strip():
        raise ValueError("return_fw must be a non-empty string")
    _require_bool(fw_state_synced, "fw_state_synced")
    _require_bool(urpf_strict_on_return, "urpf_strict_on_return")

    asymmetric = outbound_fw != return_fw
    if not asymmetric:
        return {"tcp_established": True, "asymmetric": False, "reason": "SYMMETRIC_PATH_OK"}
    if urpf_strict_on_return:
        return {"tcp_established": False, "asymmetric": True, "reason": "DROPPED_BY_URPF_STRICT_MODE_ON_ASYMMETRIC_PATH"}
    if not fw_state_synced:
        return {"tcp_established": False, "asymmetric": True, "reason": "STATEFUL_FW_B_DROPPED_SYN_ACK_NO_SESSION_STATE"}
    return {"tcp_established": True, "asymmetric": True, "reason": "ALLOWED_BY_CLUSTERED_STATE_SYNC"}


def main() -> None:
    gre = compute_tunnel_mtu_mss(1500, "gre_ipv4")
    gre_ipsec = compute_tunnel_mtu_mss(1500, "gre_over_ipsec_safe")
    assert gre["ip_mtu"] == 1476 and gre["ip_tcp_adjust_mss"] == 1436
    assert gre_ipsec["ip_mtu"] == 1400 and gre_ipsec["ip_tcp_adjust_mss"] == 1360

    small_ping = simulate_pmtud_packet(100, 1476, True, False)
    https_hang = simulate_pmtud_packet(1500, 1476, True, False)
    https_fixed = simulate_pmtud_packet(1476, 1476, True, False)
    assert small_ping["outcome"] == "DELIVERED"
    assert https_hang["outcome"] == "PMTUD_BLACKHOLE_HANG"
    assert https_fixed["outcome"] == "DELIVERED"

    asym_drop = evaluate_asymmetric_flow("FW-A", "FW-B", fw_state_synced=False)
    urpf_drop = evaluate_asymmetric_flow("FW-A", "FW-B", fw_state_synced=True, urpf_strict_on_return=True)
    assert asym_drop["tcp_established"] is False and urpf_drop["tcp_established"] is False

    print("GRE MTU/MSS:", gre)
    print("GRE+IPsec Safe MTU/MSS:", gre_ipsec)
    print("PMTUD (Small Ping vs HTTPS Blackhole):", small_ping, https_hang)
    print("Asymmetric Stateful FW / uRPF Strict:", asym_drop, urpf_drop)


if __name__ == "__main__":
    main()
