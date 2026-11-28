"""Illustrative DHCP and PAT models, no socket, packet, or device access."""
from ipaddress import IPv4Address


def dhcp_exchange(offer, accepted):
    """One successful initial allocation only; timeouts and renewal not modeled."""
    offered = IPv4Address(offer)
    if offered != IPv4Address(accepted):
        raise ValueError('requested address must match the offer in this toy exchange')
    return [('DISCOVER', None), ('OFFER', str(offered)),
            ('REQUEST', str(offered)), ('ACK', str(offered))]


def pat_translate(flows, public_ip):
    """Illustrative unique-port allocations; no expiry, collision or filtering model."""
    outside = str(IPv4Address(public_ip))
    result = {}
    for address, port, protocol in flows:
        address = str(IPv4Address(address))
        if not isinstance(port, int) or not 1 <= port <= 65535 or protocol not in ('TCP', 'UDP'):
            raise ValueError('invalid transport flow')
        key = (address, port, protocol)
        if key not in result:
            allocated = 40000 + len(result)
            if allocated > 65535:
                raise ValueError('toy port pool exhausted')
            result[key] = (outside, allocated, protocol)
    return result


if __name__ == '__main__':
    print('DHCP toy exchange:', dhcp_exchange('192.0.2.10', '192.0.2.10'))
    flows = [('10.0.0.10', 50000, 'TCP'), ('10.0.0.11', 50000, 'TCP')]
    print('Illustrative PAT allocations:', pat_translate(flows, '198.51.100.10'))
