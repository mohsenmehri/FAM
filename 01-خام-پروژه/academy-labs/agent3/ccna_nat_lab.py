"""Local Python 3 stdlib mock lab for ccna_nat (Static NAT, Dynamic NAT, PAT & Order of Operations).

Boundary: Pure in-memory simulation using Python stdlib only (ipaddress).
No real Cisco router, NAT table, or live traffic is executed.
"""
from __future__ import annotations

import ipaddress


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_port(val: object, name: str) -> int:
    if type(val) is not int or not (1 <= val <= 65535):
        raise ValueError(f"{name} must be an integer port in 1..65535")
    return val


def is_rfc1918_private(ip_str: str) -> bool:
    """Explicitly check RFC 1918 private IPv4 ranges (10/8, 172.16/12, 192.168/16)."""
    addr = ipaddress.IPv4Address(ip_str)
    rfc1918 = (
        ipaddress.IPv4Network("10.0.0.0/8"),
        ipaddress.IPv4Network("172.16.0.0/12"),
        ipaddress.IPv4Network("192.168.0.0/16"),
    )
    return any(addr in net for net in rfc1918)


def simulate_outbound_nat(
    src_ip: str,
    src_port: int,
    dst_ip: str,
    dst_port: int,
    nat_mode: str,
    inside_if_marked: bool,
    outside_if_marked: bool,
    has_route_to_dst: bool,
    pool_ips: list[str],
    existing_bindings: dict[str, str],
) -> dict[str, object]:
    """Simulate Cisco IOS Inside->Outside order of operations: Routing FIRST, then NAT."""
    ipaddress.IPv4Address(src_ip)
    ipaddress.IPv4Address(dst_ip)
    _require_port(src_port, "src_port")
    _require_port(dst_port, "dst_port")
    _require_bool(inside_if_marked, "inside_if_marked")
    _require_bool(outside_if_marked, "outside_if_marked")
    _require_bool(has_route_to_dst, "has_route_to_dst")

    if nat_mode not in ("static", "dynamic", "pat"):
        raise ValueError("nat_mode must be one of 'static', 'dynamic', 'pat'")
    if not pool_ips:
        raise ValueError("pool_ips must contain at least one IPv4 address")
    for p in pool_ips:
        ipaddress.IPv4Address(p)

    # Cisco IOS Inside -> Outside: Routing lookup happens BEFORE NAT!
    if not has_route_to_dst:
        return {
            "translated": False,
            "order_of_ops": "ROUTING_BEFORE_NAT",
            "reason": "DROPPED_NO_ROUTE_TO_DESTINATION_EMPTY_NAT_TABLE",
        }
    if not (inside_if_marked and outside_if_marked):
        return {
            "translated": False,
            "order_of_ops": "ROUTING_BEFORE_NAT",
            "reason": "FORWARDED_UNTRANSLATED_MISSING_NAT_INSIDE_OR_OUTSIDE",
        }

    if nat_mode == "static":
        inside_global = pool_ips[0]
        return {
            "translated": True,
            "mode": "static",
            "inside_local": f"{src_ip}:{src_port}",
            "inside_global": f"{inside_global}:{src_port}",
            "outside_local": f"{dst_ip}:{dst_port}",
            "outside_global": f"{dst_ip}:{dst_port}",
        }

    if nat_mode == "dynamic":
        if src_ip in existing_bindings:
            inside_global = existing_bindings[src_ip]
        else:
            used_globals = set(existing_bindings.values())
            free = [ip for ip in pool_ips if ip not in used_globals]
            if not free:
                return {
                    "translated": False,
                    "mode": "dynamic",
                    "reason": "DYNAMIC_NAT_POOL_EXHAUSTED_NO_OVERLOAD",
                }
            inside_global = free[0]
        return {
            "translated": True,
            "mode": "dynamic",
            "inside_local": f"{src_ip}:{src_port}",
            "inside_global": f"{inside_global}:{src_port}",
            "outside_local": f"{dst_ip}:{dst_port}",
            "outside_global": f"{dst_ip}:{dst_port}",
        }

    # PAT (NAT Overload): multiplex multiple Inside Local hosts onto a single Inside Global IP via unique L4 port
    pat_ip = pool_ips[0]
    used_ports = {int(v.split(":")[1]) for v in existing_bindings.values() if ":" in v}
    mapped_port = src_port
    while mapped_port in used_ports:
        mapped_port = 1024 if mapped_port >= 65535 else mapped_port + 1
    return {
        "translated": True,
        "mode": "pat_overload",
        "inside_local": f"{src_ip}:{src_port}",
        "inside_global": f"{pat_ip}:{mapped_port}",
        "outside_local": f"{dst_ip}:{dst_port}",
        "outside_global": f"{dst_ip}:{dst_port}",
    }


def simulate_inbound_return_nat(
    packet_dst_global: str,
    nat_table: dict[str, str],
    has_internal_route: bool,
) -> dict[str, object]:
    """Simulate Cisco IOS Outside->Inside order of operations: NAT FIRST, then Routing."""
    _require_bool(has_internal_route, "has_internal_route")
    if packet_dst_global not in nat_table:
        return {
            "delivered": False,
            "order_of_ops": "NAT_BEFORE_ROUTING",
            "reason": "NO_MATCHING_NAT_TRANSLATION_ENTRY",
        }
    inside_local = nat_table[packet_dst_global]
    if not has_internal_route:
        return {
            "delivered": False,
            "order_of_ops": "NAT_BEFORE_ROUTING",
            "translated_to": inside_local,
            "reason": "NO_INTERNAL_ROUTE_AFTER_UNTRANSLATION",
        }
    return {
        "delivered": True,
        "order_of_ops": "NAT_BEFORE_ROUTING",
        "inside_global_hit": packet_dst_global,
        "translated_to_inside_local": inside_local,
    }


def main() -> None:
    assert is_rfc1918_private("192.168.10.25") is True
    assert is_rfc1918_private("203.0.113.10") is False

    # Missing default route -> Routing runs BEFORE NAT -> dropped with empty NAT table
    no_route = simulate_outbound_nat(
        "192.168.10.11", 51200, "198.51.100.80", 443, "pat", True, True, False, ["203.0.113.10"], {}
    )
    assert no_route["translated"] is False and "NO_ROUTE" in str(no_route["reason"])

    # Dynamic NAT pool exhaustion (1 public IP, 2nd host fails)
    dyn_exhausted = simulate_outbound_nat(
        "192.168.10.12", 51200, "198.51.100.80", 443, "dynamic", True, True, True,
        ["203.0.113.10"], {"192.168.10.11": "203.0.113.10"},
    )
    assert dyn_exhausted["translated"] is False and "EXHAUSTED" in str(dyn_exhausted["reason"])

    # PAT Overload shares single public IP with distinct translated source port
    pat_ok = simulate_outbound_nat(
        "192.168.10.12", 51200, "198.51.100.80", 443, "pat", True, True, True,
        ["203.0.113.10"], {"192.168.10.11:51200": "203.0.113.10:51200"},
    )
    assert pat_ok["translated"] is True and pat_ok["inside_global"] == "203.0.113.10:51201"

    # Inbound return: NAT lookup BEFORE internal routing
    ret_ok = simulate_inbound_return_nat(
        "203.0.113.10:51201", {"203.0.113.10:51201": "192.168.10.12:51200"}, True
    )
    assert ret_ok["delivered"] is True

    print("Outbound No Route (Routing before NAT):", no_route)
    print("Dynamic NAT Exhausted:", dyn_exhausted)
    print("PAT Overload Multiplexed:", pat_ok)
    print("Inbound Return (NAT before Routing):", ret_ok)


if __name__ == "__main__":
    main()
