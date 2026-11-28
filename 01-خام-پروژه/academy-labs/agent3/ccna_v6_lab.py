"""Local Python Mock for ccna_v6 (IPv4/IPv6 Control-Plane RIB vs Data-Plane FIB LPM & Link-Local).

Educational local model only — no live Cisco IOS/IOS-XE router, CEF/FIB hardware,
or real packet forwarding is tested.
Models TWO distinct stages:
1. Control Plane RIB installation per exact prefix:
   - Each routing protocol selects its own best path(s) by its own Metric.
   - Competing protocols for the exact same prefix are compared by Administrative Distance (AD).
   - Metrics from different protocols are NEVER compared directly (incomparable scales).
2. Data Plane FIB lookup:
   - Among installed FIB prefixes, Longest Prefix Match (LPM) selects the most specific match
     (assuming Policy-Based Routing / PBR does not override destination lookup).
3. IPv6 global `ipv6 unicast-routing` gate, Link-Local static next-hop exit-interface check,
   and IOS/IOS-XE OSPFv3 32-bit Router-ID requirement on IPv6-only routers.
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


def build_fib_from_candidates(candidates: list[dict[str, object]]) -> dict[str, object]:
    """Stage 1 (Control Plane): install best candidate(s) per exact prefix into FIB.

    Metrics are compared ONLY within the same protocol. If two different protocols
    propose the exact same prefix with the exact same AD, this model flags an
    implementation-dependent tie rather than comparing incomparable metrics.
    """
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list of route dicts")

    by_prefix: dict[tuple[int, str], list[dict[str, object]]] = {}
    for entry in candidates:
        if not isinstance(entry, dict):
            raise ValueError("each candidate entry must be a dict")
        net = ipaddress.ip_network(str(entry["prefix"]), strict=True)
        ad = _require_non_neg_int(entry["ad"], "ad")
        if ad > 255:
            raise ValueError(f"ad must be in 0..255, got {ad}")
        metric = _require_non_neg_int(entry["metric"], "metric")
        proto = entry.get("protocol")
        if not isinstance(proto, str) or not proto.strip():
            raise ValueError("protocol must be a non-empty str")
        norm = {**entry, "prefix": str(net), "protocol": proto.strip().lower(), "ad": ad, "metric": metric}
        by_prefix.setdefault((net.version, str(net)), []).append(norm)

    installed: list[dict[str, object]] = []
    ambiguous_ties: list[dict[str, object]] = []

    for (_ver, prefix_str), entries in by_prefix.items():
        best_ad = min(e["ad"] for e in entries)
        ad_winners = [e for e in entries if e["ad"] == best_ad]
        protos = sorted({e["protocol"] for e in ad_winners})
        if len(protos) > 1:
            ambiguous_ties.append(
                {
                    "prefix": prefix_str,
                    "ad": best_ad,
                    "protocols": protos,
                    "reason": "CROSS_PROTOCOL_EQUAL_AD_METRICS_INCOMPARABLE",
                }
            )
            continue
        best_metric = min(e["metric"] for e in ad_winners)
        installed.extend(e for e in ad_winners if e["metric"] == best_metric)

    return {
        "installed_fib_routes": installed,
        "ambiguous_cross_protocol_ties": ambiguous_ties,
    }


def lookup_best_route(
    destination: str,
    rib_candidates: list[dict[str, object]],
    ipv6_unicast_routing: bool = True,
) -> dict[str, object]:
    """Run Stage 1 (RIB->FIB per exact prefix) then Stage 2 (FIB Longest Prefix Match)."""
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("destination must be a non-empty IP address string")
    v6_enabled = _require_bool(ipv6_unicast_routing, "ipv6_unicast_routing")
    dest_ip = ipaddress.ip_address(destination.strip())

    if dest_ip.version == 6 and not v6_enabled:
        return {
            "destination": str(dest_ip),
            "route_matched": False,
            "reason": "IPV6_UNICAST_ROUTING_DISABLED",
            "selected_routes": [],
            "ambiguous_cross_protocol_ties": [],
            "model_scope_note": "Local RIB/FIB model only; does not prove live CEF/packet forwarding or PBR.",
        }

    fib_result = build_fib_from_candidates(rib_candidates)
    installed = fib_result["installed_fib_routes"]
    ambiguous = fib_result["ambiguous_cross_protocol_ties"]

    matches: list[tuple[int, dict[str, object]]] = []
    for entry in installed:
        net = ipaddress.ip_network(str(entry["prefix"]), strict=True)
        if net.version == dest_ip.version and dest_ip in net:
            matches.append((net.prefixlen, entry))

    if not matches:
        return {
            "destination": str(dest_ip),
            "route_matched": False,
            "reason": "NO_MATCHING_FIB_ROUTE",
            "selected_routes": [],
            "ambiguous_cross_protocol_ties": ambiguous,
            "model_scope_note": "Local RIB/FIB model only; does not prove live CEF/packet forwarding or PBR.",
        }

    max_len = max(m[0] for m in matches)
    winners = [m[1] for m in matches if m[0] == max_len]
    return {
        "destination": str(dest_ip),
        "route_matched": True,
        "matched_prefix_len": max_len,
        "ecmp_candidate_count": len(winners),
        "selected_routes": winners,
        "ambiguous_cross_protocol_ties": ambiguous,
        "model_scope_note": "Local RIB/FIB model only; does not prove live CEF/packet forwarding, ACLs, or PBR.",
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
    """Model IOS/IOS-XE OSPFv3 32-bit Router-ID requirement on IPv6-only routers."""
    has_v4 = _require_bool(has_ipv4_interface, "has_ipv4_interface")
    if explicit_router_id is not None:
        if not isinstance(explicit_router_id, str):
            raise ValueError("explicit_router_id must be a dotted IPv4-format string or None")
        rid = ipaddress.IPv4Address(explicit_router_id.strip())
        if str(rid) == "0.0.0.0":
            raise ValueError("OSPFv3 router-id cannot be 0.0.0.0")
        return {"can_start_in_ios_model": True, "router_id": str(rid), "source": "explicit"}
    if has_v4:
        return {"can_start_in_ios_model": True, "router_id": "auto_from_ipv4", "source": "ipv4_interface"}
    return {
        "can_start_in_ios_model": False,
        "router_id": None,
        "reason": "MISSING_32BIT_ROUTER_ID_ON_IPV6_ONLY_ROUTER",
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco router or real packet forwarding is tested.")
    rib = [
        {"prefix": "2001:db8:1::/48", "protocol": "static", "ad": 1, "metric": 0, "next_hop": "fe80::1"},
        {"prefix": "2001:db8:1:2::/64", "protocol": "ospfv3", "ad": 110, "metric": 10, "next_hop": "fe80::2"},
        {"prefix": "10.20.0.0/16", "protocol": "static", "ad": 1, "metric": 0, "next_hop": "192.0.2.1"},
        {"prefix": "10.20.30.0/24", "protocol": "ospf", "ad": 110, "metric": 20, "next_hop": "192.0.2.2"},
    ]
    res_v6 = lookup_best_route("2001:db8:1:2::9", rib, ipv6_unicast_routing=True)
    assert res_v6["route_matched"] is True and res_v6["selected_routes"][0]["protocol"] == "ospfv3"
    res_v6_off = lookup_best_route("2001:db8:1:2::9", rib, ipv6_unicast_routing=False)
    assert res_v6_off["route_matched"] is False and res_v6_off["reason"] == "IPV6_UNICAST_ROUTING_DISABLED"

    # Cross-protocol equal-AD tie must NOT compare incomparable metrics
    tie_res = build_fib_from_candidates([
        {"prefix": "10.99.0.0/24", "protocol": "ospf", "ad": 110, "metric": 10},
        {"prefix": "10.99.0.0/24", "protocol": "eigrp", "ad": 110, "metric": 2816},
    ])
    assert len(tie_res["ambiguous_cross_protocol_ties"]) == 1
    assert tie_res["installed_fib_routes"] == []
    print("IPv6 FIB LPM winner:", res_v6)
    print("Cross-protocol equal-AD tie safely flagged:", tie_res["ambiguous_cross_protocol_ties"])

    bad_ll = validate_ipv6_static_next_hop("2001:db8:99::/64", "fe80::2", None)
    good_ll = validate_ipv6_static_next_hop("2001:db8:99::/64", "fe80::2", "GigabitEthernet0/0")
    assert bad_ll["valid"] is False and good_ll["valid"] is True
    assert validate_ospfv3_router_id(False, None)["can_start_in_ios_model"] is False
    assert validate_ospfv3_router_id(False, "3.3.3.3")["can_start_in_ios_model"] is True
    print("Link-Local & OSPFv3 Router-ID model checks passed.")


if __name__ == "__main__":
    main()
