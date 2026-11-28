"""Local Python Mock for adv_mcast (IPv4 Multicast 32-to-1 MAC Mapping & PIM RPF Check).

Educational local model only — no live multicast router, IGMP snooping ASIC, or PIM-SM
Rendezvous Point is contacted.
Models:
1. RFC 1112 IPv4 Multicast (`224.0.0.0/4`) 23-bit mapping to `01:00:5e:xx:xx:xx` and
   exact 32-to-1 L2 MAC collision detection across different IPv4 multicast groups.
2. PIM Reverse Path Forwarding (RPF) check against a unicast FIB table (longest prefix match).
"""
from __future__ import annotations

import ipaddress


def ipv4_multicast_to_mac(group_ip: str) -> dict[str, object]:
    """Map an IPv4 multicast address (224.0.0.0/4) to its RFC 1112 Ethernet MAC address."""
    if not isinstance(group_ip, str) or not group_ip.strip():
        raise ValueError("group_ip must be a non-empty IPv4 multicast address string")
    ip = ipaddress.IPv4Address(group_ip.strip())
    if not ip.is_multicast:
        raise ValueError(f"{ip} is not in IPv4 multicast range 224.0.0.0/4")
    octets = ip.packed
    low23_b1 = octets[1] & 0x7F  # drop top bit of second octet (5 bits lost overall -> 2^5 = 32 overlap)
    mac = f"01:00:5e:{low23_b1:02x}:{octets[2]:02x}:{octets[3]:02x}"
    return {
        "group_ip": str(ip),
        "multicast_mac": mac,
        "link_local_224_0_0_x": ip in ipaddress.IPv4Network("224.0.0.0/24"),
        "overlap_factor": 32,
    }


def evaluate_pim_rpf(
    source_ip: str,
    incoming_interface: str,
    unicast_fib: list[dict[str, str]],
) -> dict[str, object]:
    """Check whether a multicast packet from source_ip arrived on the unicast RPF interface."""
    src = ipaddress.IPv4Address(source_ip.strip())
    if not isinstance(incoming_interface, str) or not incoming_interface.strip():
        raise ValueError("incoming_interface must be a non-empty str")
    if not isinstance(unicast_fib, list):
        raise ValueError("unicast_fib must be a list of {'prefix', 'interface'} dicts")

    best_len = -1
    rpf_iface: str | None = None
    for entry in unicast_fib:
        net = ipaddress.IPv4Network(str(entry["prefix"]), strict=True)
        if src in net and net.prefixlen > best_len:
            best_len = net.prefixlen
            rpf_iface = str(entry["interface"]).strip()

    if rpf_iface is None:
        return {"rpf_passed": False, "expected_rpf_interface": None, "reason": "NO_UNICAST_ROUTE_TO_SOURCE"}
    passed = incoming_interface.strip() == rpf_iface
    return {
        "source_ip": str(src),
        "incoming_interface": incoming_interface.strip(),
        "expected_rpf_interface": rpf_iface,
        "rpf_passed": passed,
        "reason": "RPF_INTERFACE_MATCHED" if passed else "RPF_FAILURE_PACKET_DROPPED",
    }


def main() -> None:
    print("Local Python Mock only — no live PIM-SM router or IGMP snooping switch is contacted.")
    m1 = ipv4_multicast_to_mac("224.1.1.1")
    m2 = ipv4_multicast_to_mac("239.129.1.1")
    assert m1["multicast_mac"] == m2["multicast_mac"] == "01:00:5e:01:01:01"
    print("32-to-1 MAC overlap proven:", {"224.1.1.1": m1["multicast_mac"], "239.129.1.1": m2["multicast_mac"]})

    fib = [
        {"prefix": "0.0.0.0/0", "interface": "GigabitEthernet0/1"},
        {"prefix": "10.50.0.0/16", "interface": "GigabitEthernet0/0"},
    ]
    ok = evaluate_pim_rpf("10.50.1.10", "GigabitEthernet0/0", fib)
    fail = evaluate_pim_rpf("10.50.1.10", "GigabitEthernet0/1", fib)
    assert ok["rpf_passed"] is True and fail["rpf_passed"] is False
    print("PIM RPF checks:", {"ok": ok["rpf_passed"], "fail": fail["reason"]})


if __name__ == "__main__":
    main()
