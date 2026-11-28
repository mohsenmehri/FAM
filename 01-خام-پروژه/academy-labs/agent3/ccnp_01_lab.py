"""Local Python Mock for ccnp_01 (GRE/IPsec MTU & Recursive-Routing Guard, LISP/VXLAN & SPAN/ERSPAN).

Educational local model only — no live Cisco IOS-XE router, IPsec crypto engine,
LISP Map-Server, VXLAN VTEP, or ERSPAN collector is contacted.
Models:
1. GRE over IPsec effective payload MTU / TCP MSS budgeting (illustrative IPv4 + GRE + ESP overhead).
2. GRE Tunnel Recursive-Routing detector (checking whether the tunnel destination prefix is
   learned via the tunnel interface itself!).
3. SPAN vs RSPAN vs ERSPAN transport scope classifier.
"""
from __future__ import annotations

import ipaddress


def _require_int_range(val: object, name: str, lo: int, hi: int) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (lo <= val <= hi):
        raise ValueError(f"{name} must be an int in {lo}..{hi}, got {val!r}")
    return val


def compute_gre_ipsec_mtu(
    underlay_mtu: int = 1500,
    gre_overhead: int = 24,
    ipsec_esp_overhead: int = 56,
) -> dict[str, object]:
    """Compute illustrative tunnel IP MTU and recommended TCP MSS for GRE over IPsec."""
    u = _require_int_range(underlay_mtu, "underlay_mtu", 576, 9216)
    g = _require_int_range(gre_overhead, "gre_overhead", 24, 64)
    e = _require_int_range(ipsec_esp_overhead, "ipsec_esp_overhead", 0, 128)
    tunnel_mtu = u - g - e
    if tunnel_mtu < 576:
        raise ValueError("resulting tunnel_mtu < 576 bytes")
    tcp_mss = tunnel_mtu - 40  # IPv4 (20) + TCP (20) without options
    return {
        "underlay_mtu": u,
        "gre_overhead_bytes": g,
        "ipsec_overhead_bytes": e,
        "illustrative_tunnel_ip_mtu": tunnel_mtu,
        "illustrative_tcp_mss": tcp_mss,
        "model_scope_note": "Illustrative overhead budget only; exact ESP padding/IV/NAT-T/crypto-suite overhead depends on configured transform-set and tunnel mode.",
    }


def detect_gre_recursive_routing(
    tunnel_destination_ip: str,
    best_route_exit_interface: str,
    tunnel_interface_name: str,
) -> dict[str, object]:
    """Detect whether the GRE tunnel destination resolves out the tunnel interface itself."""
    dst = ipaddress.IPv4Address(tunnel_destination_ip.strip())
    if not isinstance(best_route_exit_interface, str) or not best_route_exit_interface.strip():
        raise ValueError("best_route_exit_interface must be a non-empty str")
    if not isinstance(tunnel_interface_name, str) or not tunnel_interface_name.strip():
        raise ValueError("tunnel_interface_name must be a non-empty str")
    recursive = best_route_exit_interface.strip().lower() == tunnel_interface_name.strip().lower()
    return {
        "tunnel_destination": str(dst),
        "best_route_exit": best_route_exit_interface.strip(),
        "recursive_routing_fault": recursive,
        "reason": "TUNNEL_DEST_LEARNED_OVER_TUNNEL_FLAP" if recursive else "UNDERLAY_EXIT_HEALTHY",
    }


def main() -> None:
    print("Local Python Mock only — no live IOS-XE GRE/IPsec/LISP/VXLAN device is contacted.")
    budget = compute_gre_ipsec_mtu(1500, 24, 56)
    assert budget["illustrative_tunnel_ip_mtu"] == 1420 and budget["illustrative_tcp_mss"] == 1380
    bad = detect_gre_recursive_routing("198.51.100.2", "Tunnel0", "Tunnel0")
    good = detect_gre_recursive_routing("198.51.100.2", "GigabitEthernet0/0", "Tunnel0")
    assert bad["recursive_routing_fault"] is True and good["recursive_routing_fault"] is False
    print("GRE/IPsec budget:", budget)
    print("Recursive routing guard:", {"bad": bad["reason"], "good": good["reason"]})


if __name__ == "__main__":
    main()
