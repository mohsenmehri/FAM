"""VXLAN size arithmetic only; no network, BGP, tunnels or packets."""

def outer_ip_size(inner_ip_size, *, inner_vlan_tags=0, outer_ip_version=4):
    """Inner IPv4/IPv6 packet in Ethernet frame, excluding inner FCS.

    Returns outer IP packet bytes, including outer IP/UDP/VXLAN headers,
    excluding outer Ethernet header, VLAN tags, FCS, and physical overhead.
    No IP options, IPv6 extensions, security encapsulation or fragmentation.
    """
    if not isinstance(inner_ip_size, int) or inner_ip_size <= 0:
        raise ValueError('inner IP size must be a positive integer')
    if inner_vlan_tags not in (0, 1, 2) or outer_ip_version not in (4, 6):
        raise ValueError('unsupported VLAN tag count or outer IP version')
    outer_ip = 20 if outer_ip_version == 4 else 40
    return inner_ip_size + 14 + 4 * inner_vlan_tags + 8 + 8 + outer_ip


def fits(inner_ip_size, underlay_ip_mtu, **kwargs):
    if not isinstance(underlay_ip_mtu, int) or underlay_ip_mtu <= 0:
        raise ValueError('underlay IP MTU must be positive')
    size = outer_ip_size(inner_ip_size, **kwargs)
    return size, size <= underlay_ip_mtu


if __name__ == '__main__':
    for version in (4, 6):
        size, ok = fits(1500, 1550, outer_ip_version=version)
        print(f'Outer IPv{version}: {size} IP bytes; fits 1550 IP MTU: {ok}')
    print('Arithmetic only; no encapsulation or network traffic')
