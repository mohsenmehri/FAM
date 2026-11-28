"""Local Python 3 stdlib mock lab for ccna_dhcp (DHCP Server, Relay giaddr, APIPA & DNS).

Boundary: Pure in-memory simulation using Python stdlib only (ipaddress).
No real Cisco router, DHCP server, DNS server, or network sockets are used.
"""
from __future__ import annotations

import ipaddress


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_non_empty_str(val: object, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return val.strip()


def allocate_dhcp_lease(
    subnet_cidr: str,
    excluded_ranges: list[tuple[str, str]],
    active_leases: set[str],
    client_mac: str,
) -> dict[str, object]:
    """Simulate Cisco IOS DHCP pool allocation respecting excluded-address ranges."""
    _require_non_empty_str(subnet_cidr, "subnet_cidr")
    _require_non_empty_str(client_mac, "client_mac")
    net = ipaddress.IPv4Network(subnet_cidr, strict=True)
    if net.prefixlen >= 31:
        raise ValueError("DHCP pool requires a subnet with usable host addresses (prefix <= /30)")

    excluded: set[ipaddress.IPv4Address] = set()
    for start_s, end_s in excluded_ranges:
        s_ip = ipaddress.IPv4Address(start_s)
        e_ip = ipaddress.IPv4Address(end_s)
        if int(s_ip) > int(e_ip):
            raise ValueError(f"Excluded range start {start_s} > end {end_s}")
        if s_ip not in net or e_ip not in net:
            raise ValueError(f"Excluded range {start_s}-{end_s} outside subnet {subnet_cidr}")
        for raw in range(int(s_ip), int(e_ip) + 1):
            excluded.add(ipaddress.IPv4Address(raw))

    used = {ipaddress.IPv4Address(ip) for ip in active_leases}
    for host in net.hosts():
        if host not in excluded and host not in used:
            return {
                "allocated": True,
                "client_mac": client_mac,
                "assigned_ip": str(host),
                "subnet_mask": str(net.netmask),
                "excluded_count": len(excluded),
            }
    return {
        "allocated": False,
        "client_mac": client_mac,
        "assigned_ip": None,
        "reason": "POOL_EXHAUSTED_CLIENT_FALLS_BACK_TO_APIPA_169_254_0_0_16",
    }


def simulate_dhcp_relay(
    client_vlan: int,
    gateway_ip: str,
    helper_address: str | None,
    server_scopes: dict[str, str],
    server_reachable: bool = True,
) -> dict[str, object]:
    """Simulate DHCP Discover crossing a router with/without ip helper-address (giaddr)."""
    if type(client_vlan) is not int or not (1 <= client_vlan <= 4094):
        raise ValueError("client_vlan must be an integer in 1..4094")
    gw = ipaddress.IPv4Address(gateway_ip)
    _require_bool(server_reachable, "server_reachable")

    if helper_address is None:
        return {
            "dora_success": False,
            "client_vlan": client_vlan,
            "giaddr": None,
            "result": "DROPPED_AT_ROUTER_NO_HELPER_ADDRESS",
            "client_fallback": "APIPA 169.254.0.0/16 (RFC 3927)",
        }

    srv = ipaddress.IPv4Address(helper_address)
    if not server_reachable:
        return {
            "dora_success": False,
            "client_vlan": client_vlan,
            "giaddr": str(gw),
            "helper_target": str(srv),
            "result": "DHCP_SERVER_UNREACHABLE",
            "client_fallback": "APIPA 169.254.0.0/16 (RFC 3927)",
        }

    matched_scope = None
    for scope_name, scope_cidr in server_scopes.items():
        net = ipaddress.IPv4Network(scope_cidr, strict=True)
        if gw in net:
            matched_scope = scope_name
            break

    if matched_scope is None:
        return {
            "dora_success": False,
            "client_vlan": client_vlan,
            "giaddr": str(gw),
            "helper_target": str(srv),
            "result": "NO_MATCHING_SCOPE_FOR_GIADDR",
            "client_fallback": "APIPA 169.254.0.0/16 (RFC 3927)",
        }

    return {
        "dora_success": True,
        "client_vlan": client_vlan,
        "giaddr": str(gw),
        "helper_target": str(srv),
        "udp_ports": {"client": 68, "server": 67},
        "selected_scope": matched_scope,
        "result": "RELAYED_UNICAST_AND_SCOPE_MATCHED",
    }


def classify_dns_record(record_type: str, transport_size_bytes: int, is_zone_transfer: bool = False) -> dict[str, object]:
    """Validate common DNS record types and UDP/TCP 53 transport selection."""
    rtype = _require_non_empty_str(record_type, "record_type").upper()
    if type(transport_size_bytes) is not int or transport_size_bytes <= 0:
        raise ValueError("transport_size_bytes must be a positive integer")
    _require_bool(is_zone_transfer, "is_zone_transfer")

    meanings = {
        "A": "IPv4 host address mapping",
        "AAAA": "IPv6 host address mapping",
        "CNAME": "Canonical name alias",
        "PTR": "Reverse IP-to-hostname pointer",
        "MX": "Mail exchanger record",
        "NS": "Authoritative name server record",
    }
    if rtype not in meanings:
        raise ValueError(f"Unsupported record_type: {rtype}")

    protocol = "TCP/53" if (is_zone_transfer or transport_size_bytes > 512) else "UDP/53"
    return {
        "record_type": rtype,
        "purpose": meanings[rtype],
        "recommended_transport": protocol,
    }


def main() -> None:
    lease = allocate_dhcp_lease(
        "10.10.10.0/24",
        [("10.10.10.1", "10.10.10.20")],
        {"10.10.10.21"},
        "aa:bb:cc:00:00:01",
    )
    assert lease["allocated"] is True and lease["assigned_ip"] == "10.10.10.22"

    scopes = {"VLAN10_USERS": "10.10.10.0/24", "VLAN20_SALES": "10.10.20.0/24"}
    ok_relay = simulate_dhcp_relay(10, "10.10.10.1", "10.99.0.10", scopes)
    no_helper = simulate_dhcp_relay(30, "10.10.30.1", None, scopes)
    no_scope = simulate_dhcp_relay(30, "10.10.30.1", "10.99.0.10", scopes)
    assert ok_relay["dora_success"] is True and ok_relay["selected_scope"] == "VLAN10_USERS"
    assert no_helper["dora_success"] is False and "NO_HELPER" in str(no_helper["result"])
    assert no_scope["dora_success"] is False and no_scope["result"] == "NO_MATCHING_SCOPE_FOR_GIADDR"

    dns_udp = classify_dns_record("AAAA", 128)
    dns_tcp = classify_dns_record("NS", 200, is_zone_transfer=True)
    assert dns_udp["recommended_transport"] == "UDP/53"
    assert dns_tcp["recommended_transport"] == "TCP/53"

    print("DHCP Lease (respecting excluded 1..20):", lease)
    print("DHCP Relay OK (giaddr=10.10.10.1):", ok_relay)
    print("DHCP Relay Missing Helper (APIPA fallback):", no_helper)
    print("DHCP Relay Missing Scope:", no_scope)
    print("DNS Transport Checks:", dns_udp, dns_tcp)


if __name__ == "__main__":
    main()
