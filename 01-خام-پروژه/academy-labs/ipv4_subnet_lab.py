"""Local Python ipaddress calculations; no network equipment is contacted."""
from ipaddress import IPv4Interface


def describe(cidr):
    net = IPv4Interface(cidr).network
    # ipaddress.hosts() includes both addresses on /31 and the single /32.
    # These are library semantics, not a blanket deployment recommendation.
    first = net.network_address if net.prefixlen >= 31 else net.network_address + 1
    last = net.broadcast_address if net.prefixlen >= 31 else net.broadcast_address - 1
    count = net.num_addresses if net.prefixlen >= 31 else net.num_addresses - 2
    return {'network': str(net.network_address), 'broadcast_field': str(net.broadcast_address),
            'mask': str(net.netmask), 'address_count': net.num_addresses,
            'python_host_first': str(first), 'python_host_last': str(last), 'python_host_count': count}


if __name__ == '__main__':
    info = describe('192.0.2.191/26')
    print('Python calculation only; no interfaces configured')
    for key in ('network', 'broadcast_field', 'mask', 'address_count',
                'python_host_first', 'python_host_last', 'python_host_count'):
        print(f'{key}: {info[key]}')
