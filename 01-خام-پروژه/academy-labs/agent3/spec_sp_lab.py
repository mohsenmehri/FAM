"""Local Python Mock for spec_sp (MPLS L3VPN Label Stack, PHP, RD/RT & MTU).

No real Cisco IOS-XE/IOS-XR router, LDP session, or MP-BGP VPNv4 peering is run.
Models standard 20-bit MPLS labels (0..1048575), Penultimate Hop Popping (Implicit Null = 3),
Explicit Null (0), and non-PHP swap behavior at PE2.
"""
from __future__ import annotations

from dataclasses import dataclass

IMPLICIT_NULL = 3
EXPLICIT_NULL_IPV4 = 0
MAX_MPLS_LABEL = (1 << 20) - 1  # 1,048,575 (20-bit MPLS label field)


def _require_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int):
        raise ValueError(f"{name} must be an int (not bool), got {val!r} ({type(val).__name__})")
    return val


def _require_mpls_label(val: object, name: str, allow_special: bool = False) -> int:
    lbl = _require_int(val, name)
    if not (0 <= lbl <= MAX_MPLS_LABEL):
        raise ValueError(f"{name} out of 20-bit MPLS label range 0..{MAX_MPLS_LABEL}: {lbl}")
    if not allow_special and lbl < 16:
        raise ValueError(f"{name} must be a non-reserved MPLS label (>=16), got {lbl}")
    return lbl


@dataclass(frozen=True)
class Vpnv4Route:
    rd: str
    prefix: str
    export_rts: tuple[str, ...]
    vpn_label: int
    egress_pe_loopback: str

    def __post_init__(self) -> None:
        _require_mpls_label(self.vpn_label, "vpn_label", allow_special=False)


def import_routes_into_vrf(
    vrf_name: str,
    import_rts: set[str],
    bgp_vpnv4_table: list[Vpnv4Route],
) -> list[dict[str, object]]:
    """Simulate MP-BGP VPNv4 RT import matching (RD guarantees uniqueness, RT controls import)."""
    if not isinstance(vrf_name, str) or not vrf_name.strip():
        raise ValueError("vrf_name must be a non-empty str")
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
    """Trace Push -> Swap/PHP Pop -> Egress PE Pop across PE1 -> P1 -> PE2."""
    _require_mpls_label(transport_label_pe1_to_p1, "transport_label_pe1_to_p1", allow_special=False)
    _require_mpls_label(p1_outgoing_label, "p1_outgoing_label", allow_special=True)
    _require_mpls_label(vpn_label, "vpn_label", allow_special=False)
    payload = _require_int(ip_payload_bytes, "ip_payload_bytes")
    mtu = _require_int(core_mpls_mtu, "core_mpls_mtu")
    if payload <= 0 or mtu <= 0:
        raise ValueError("ip_payload_bytes and core_mpls_mtu must be positive integers")

    stack = [transport_label_pe1_to_p1, vpn_label]  # index 0 = top (outer) label
    mpls_header_bytes = len(stack) * 4
    total_l3_frame = payload + mpls_header_bytes
    mtu_ok = total_l3_frame <= mtu
    trace = [f"PE1 (Push): stack={list(stack)} (size={total_l3_frame}B vs MPLS MTU {mtu}B)"]

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
        trace.append(f"P1 (Swap outer transport label to {p1_outgoing_label} — no PHP): stack={list(stack)}")

    # Egress PE2 processing: if an outer label remains (Explicit Null or non-PHP transport label), pop it first
    if len(stack) == 2:
        outer_popped = stack.pop(0)
        trace.append(f"PE2 (Pop outer label {outer_popped} — double lookup without PHP): stack={list(stack)}")

    final_vpn_label = stack.pop(0)
    trace.append(f"PE2 (Pop VPN Label {final_vpn_label} -> VRF lookup -> CE): stack={list(stack)}")
    return {"delivered": True, "final_vpn_label": final_vpn_label, "trace": trace}


def main() -> None:
    print("Local Python Mock only — no real PE/P router, LDP, or MP-BGP session is executed.")
    vpnv4_table = [
        Vpnv4Route("65100:101", "10.50.1.0/24", ("65100:101",), 18001, "198.51.100.2"),
        Vpnv4Route("65100:202", "10.50.1.0/24", ("65100:202",), 18002, "198.51.100.2"),
    ]
    imported = import_routes_into_vrf("CUST_A", {"65100:101"}, vpnv4_table)
    php_res = simulate_mpls_l3vpn_forwarding(24, IMPLICIT_NULL, 18001, 1500, 1508)
    swap_res = simulate_mpls_l3vpn_forwarding(24, 30, 18001, 1500, 1508)
    mtu_fail = simulate_mpls_l3vpn_forwarding(24, IMPLICIT_NULL, 18001, 1500, 1500)
    assert len(imported) == 1 and imported[0]["vpn_label"] == 18001
    assert php_res["delivered"] is True and php_res["final_vpn_label"] == 18001
    assert swap_res["delivered"] is True and swap_res["final_vpn_label"] == 18001
    assert mtu_fail["delivered"] is False
    print("VRF CUST_A imports:", imported)
    print("PHP forwarding:", php_res)
    print("Non-PHP swap forwarding:", swap_res)
    print("MTU failure:", mtu_fail)


if __name__ == "__main__":
    main()
