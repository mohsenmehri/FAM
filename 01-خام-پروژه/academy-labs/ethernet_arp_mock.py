"""A routing/ARP thought experiment; does not access a real network."""
from ipaddress import IPv4Address, IPv4Interface


def arp_target(local, destination, gateway):
    iface = IPv4Interface(local)
    dst, gw = IPv4Address(destination), IPv4Address(gateway)
    if gw not in iface.network:
        raise ValueError('gateway must be on the local subnet')
    return dst if dst in iface.network else gw


if __name__ == '__main__':
    local, gateway = '192.0.2.10/24', '192.0.2.1'
    print('Python Mock: no ARP request sent')
    for target in ('192.0.2.20', '198.51.100.80'):
        print(f'destination {target} -> ARP target {arp_target(local, target, gateway)}')
