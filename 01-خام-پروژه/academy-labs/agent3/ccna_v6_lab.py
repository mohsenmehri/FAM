"""Local Python Mock for ccna_v6 (IPv4/IPv6 Routing, Longest Prefix Match, AD/Metric & Link-Local).

No real Cisco IOS/IOS-XE router is contacted.
Models:
1. Strict Dual-Stack Longest Prefix Match (LPM) before Cisco-default AD and Metric tie-breaking.
2. IPv6 global `ipv6 unicast-routing` gate.
3. IPv6 Link-Local (`fe80::/10`) static next-hop exit-interface requirement.
4. OSPFv3 32-bit Router-ID requirement on IPv6-only routers.
"""
from __future__ import annotations

import ipaddress


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_non_neg_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val < 0:
        raise ValueError(f"{name} must be a non-negative int (not bool), got {val!r}")
    return val


def lookup_best_route(
    destination: str,
    rib: list[dict[str, object]],
    ipv6_unicast_routing: bool = True,
) -> dict[str, object]:
    """Perform strict LPM -> AD -> Metric selection on a Dual-Stack RIB."""
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("destination must be a non-empty IP address string")
    v6_enabled = _require_bool(ipv6_unicast_routing, "ipv6_unicast_routing")
    dest_ip = ipaddress.ip_address(destination.strip())

    if dest_ip.version == 6 and not v6_enabled:
        return {
            "destination": str(dest_ip),
            "forwarded": False,
            "reason": "IPV6_UNICAST_ROUTING_DISABLED",
            "selected_routes": [],
        }

    if not isinstance(rib, list):
        raise ValueError("rib must be a list of route dicts")

    matches: list[tuple[int, int, int, dict[str, object]]] = []
    for entry in rib:
        if not isinstance(entry, dict):
            raise ValueError("each RIB entry must be a dict")
        net = ipaddress.ip_network(str(entry["prefix"]), strict=True)
        ad = _require_non_neg_int(entry["ad"], "ad")
        if ad > 255:
            raise ValueError(f"ad must be in 0..255, got {ad}")
        metric = _require_non_neg_int(entry["metric"], "metric")
        if net.version == dest_ip.version and dest_ip in net:
            # Longest prefix wins FIRST; then lowest AD (vendor-specific default); then lowest metric
            matches.append((-net.prefixlen, ad, metric, {**entry, "prefix": str(net)}))

    if not matches:
        return {
            "destination": str(dest_ip),
            "forwarded": False,
            "reason": "NO_MATCHING_ROUTE",
            "selected_routes": [],
        }

    matches.sort(key=lambda t: (t[0], t[1], t[2]))
    best_key = (matches[0][0], matches[0][1], matches[0][2])
    winners = [m[3] for m in matches if (m[0], m[1], m[2]) == best_key]
    return {
        "destination": str(dest_ip),
        "forwarded": True,
        "ecmp_count": len(winners),
        "selected_routes": winners,
    }


def validate_ipv6_static_next_hop(
    prefix: str,
    next_hop: str,
    exit_interface: str | None = None,
) -> dict[str, object]:
    """Validate IPv6 static route syntax, enforcing exit_interface for Link-Local next-hops."""
    net = ipaddress.IPv6Network(prefix, strict=True)
    nh = ipaddress.IPv6Address(next_hop)
    is_ll = nh in ipaddress.IPv6Network("fe80::/10")
    has_iface = isinstance(exit_interface, str) and bool(exit_interface.strip())
    if is_ll and not has_iface:
        return {
            "valid": False,
            "prefix": str(net),
            "next_hop": str(nh),
            "reason": "LINK_LOCAL_NEXT_HOP_REQUIRES_EXIT_INTERFACE",
        }
    return {
        "valid": True,
        "prefix": str(net),
        "next_hop": str(nh),
        "exit_interface": exit_interface.strip() if has_iface else None,
    }


def validate_ospfv3_router_id(
    has_ipv4_interface: bool,
    explicit_router_id: str | None = None,
) -> dict[str, object]:
    """Model OSPFv3 32-bit Router-ID requirement on IPv6-only routers."""
    has_v4 = _require_bool(has_ipv4_interface, "has_ipv4_interface")
    if explicit_router_id is not None:
        if not isinstance(explicit_router_id, str):
            raise ValueError("explicit_router_id must be a dotted IPv4-format string or None")
        rid = ipaddress.IPv4Address(explicit_router_id.strip())
        if str(rid) == "0.0.0.0":
            raise ValueError("OSPFv3 router-id cannot be 0.0.0.0")
        return {"can_start": True, "router_id": str(rid), "source": "explicit"}
    if has_v4:
        return {"can_start": True, "router_id": "auto_from_ipv4", "source": "ipv4_interface"}
    return {
        "can_start": False,
        "router_id": None,
        "reason": "MISSING_32BIT_ROUTER_ID_ON_IPV6_ONLY_ROUTER",
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco router is contacted.")
    rib = [
        {"prefix": "2001:db8:1::/48", "protocol": "static", "ad": 1, "metric": 0, "next_hop": "fe80::1"},
        {"prefix": "2001:db8:1:2::/64", "protocol": "ospfv3", "ad": 110, "metric": 10, "next_hop": "fe80::2"},
        {"prefix": "10.20.0.0/16", "protocol": "static", "ad": 1, "metric": 0, "next_hop": "192.0.2.1"},
        {"prefix": "10.20.30.0/24", "protocol": "ospf", "ad": 110, "metric": 20, "next_hop": "192.0.2.2"},
    ]
    # LPM beats AD in both IPv6 and IPv4
    res_v6 = lookup_best_route("2001:db8:1:2::9", rib, ipv6_unicast_routing=True)
    assert res_v6["forwarded"] is True and res_v6["selected_routes"][0]["protocol"] == "ospfv3"
    res_v6_off = lookup_best_route("2001:db8:1:2::9", rib, ipv6_unicast_routing=False)
    assert res_v6_off["forwarded"] is False and res_v6_off["reason"] == "IPV6_UNICAST_ROUTING_DISABLED"
    print("IPv6 LPM winner:", res_v6)
    print("IPv6 unicast-routing off:", res_v6_off)

    # Link-Local static check
    bad_ll = validate_ipv6_static_next_hop("2001:db8:99::/64", "fe80::2", None)
    good_ll = validate_ipv6_static_next_hop("2001:db8:99::/64", "fe80::2", "GigabitEthernet0/0")
    assert bad_ll["valid"] is False and good_ll["valid"] is True
    print("Link-Local check:", {"without_iface": bad_ll["valid"], "with_iface": good_ll["valid"]})

    # OSPFv3 Router-ID on IPv6-only router
    assert validate_ospfv3_router_id(False, None)["can_start"] is False
    assert validate_ospfv3_router_id(False, "3.3.3.3")["can_start"] is True
    print("OSPFv3 Router-ID check passed.")


if __name__ == "__main__":
    main()
