"""Local Python Mock for spec_sp (MPLS L3VPN Label Stack, PHP, RD/RT & MTU).

No real Cisco IOS-XE/IOS-XR router, LDP session, or MP-BGP VPNv4 peering is run.
"""
from __future__ import annotations

from dataclasses import dataclass

IMPLICIT_NULL = 3
EXPLICIT_NULL_IPV4 = 0


@dataclass(frozen=True)
class Vpnv4Route:
    rd: str
    prefix: str
    export_rts: tuple[str, ...]
    vpn_label: int
    egress_pe_loopback: str


def import_routes_into_vrf(
    vrf_name: str,
    import_rts: set[str],
    bgp_vpnv4_table: list[Vpnv4Route],
) -> list[dict[str, object]]:
    """Simulate MP-BGP VPNv4 RT import matching (RD guarantees uniqueness, RT controls import)."""
    imported = []
    for route in bgp_vpnv4_table:
        matched_rts = sorted(import_rts & set(route.export_rts))
        if matched_rts:
            imported.append({
                "vrf": vrf_name,
                "rd": route.rd,
                "prefix": route.prefix,
                "matched_rts": matched_rts,
                "vpn_label": route.vpn_label,
                "next_hop_pe": route.egress_pe_loopback,
            })
    return imported


def simulate_mpls_l3vpn_forwarding(
    transport_label_pe1_to_p1: int,
    p1_outgoing_label: int,
    vpn_label: int,
    ip_payload_bytes: int = 1500,
    core_mpls_mtu: int = 1508,
) -> dict[str, object]:
    """Trace Push -> Swap/PHP Pop -> Pop across PE1 -> P1 -> PE2."""
    stack = [transport_label_pe1_to_p1, vpn_label]  # index 0 = top (outer) label
    mpls_header_bytes = len(stack) * 4
    total_l3_frame = ip_payload_bytes + mpls_header_bytes
    mtu_ok = total_l3_frame <= core_mpls_mtu
    trace = [f"PE1 (Push): stack={list(stack)} (size={total_l3_frame}B vs MPLS MTU {core_mpls_mtu}B)"]

    if not mtu_ok:
        return {"delivered": False, "reason": "MPLS MTU exceeded on core link", "trace": trace}

    if p1_outgoing_label == IMPLICIT_NULL:
        stack.pop(0)
        trace.append(f"P1 (PHP Pop on Implicit Null Label 3): stack={list(stack)}")
    elif p1_outgoing_label == EXPLICIT_NULL_IPV4:
        stack[0] = EXPLICIT_NULL_IPV4
        trace.append(f"P1 (Swap to Explicit Null Label 0 — preserves TC/QoS): stack={list(stack)}")
    else:
        stack[0] = p1_outgoing_label
        trace.append(f"P1 (Swap to {p1_outgoing_label}): stack={list(stack)}")

    if stack and stack[0] == EXPLICIT_NULL_IPV4:
        stack.pop(0)
    final_vpn_label = stack.pop(0)
    trace.append(f"PE2 (Pop VPN Label {final_vpn_label} -> VRF lookup -> CE): stack={list(stack)}")
    return {"delivered": True, "final_vpn_label": final_vpn_label, "trace": trace}


def main() -> None:
    print("Local Python Mock only — no real PE/P router, LDP, or MP-BGP session is executed.")
    vpnv4_table = [
        Vpnv4Route("65100:101", "10.50.1.0/24", ("65100:101",), 18001, "198.51.100.2"),
        Vpnv4Route("65100:202", "10.50.1.0/24", ("65100:202",), 18002, "198.51.100.2"),
    ]
    print("VRF CUST_A imports:", import_routes_into_vrf("CUST_A", {"65100:101"}, vpnv4_table))
    print("PHP forwarding:", simulate_mpls_l3vpn_forwarding(24, IMPLICIT_NULL, 18001, 1500, 1508))
    print("MTU failure:", simulate_mpls_l3vpn_forwarding(24, IMPLICIT_NULL, 18001, 1500, 1500))


if __name__ == "__main__":
    main()
