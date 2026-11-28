"""IPv4 route summarization calculations only; does not configure a router."""
from ipaddress import IPv4Address, IPv4Network, collapse_addresses


def cover(routes):
    networks = [IPv4Network(route, strict=True) for route in routes]
    if not networks:
        raise ValueError('at least one route is required')
    first = min(int(n.network_address) for n in networks)
    last = max(int(n.broadcast_address) for n in networks)
    prefix = 32 - (first ^ last).bit_length()
    summary = IPv4Network((first, prefix), strict=False)
    exact = list(collapse_addresses(networks)) == [summary]
    return str(summary), exact


def longest_match(routes, destination):
    address = IPv4Address(destination)
    matches = [IPv4Network(route) for route in routes if address in IPv4Network(route)]
    return str(max(matches, key=lambda n: n.prefixlen)) if matches else None


if __name__ == '__main__':
    for routes in (['192.0.2.0/26', '192.0.2.64/26'],
                   ['192.0.2.0/26', '192.0.2.128/26']):
        print(f'{routes} -> summary, exact = {cover(routes)}')
    print('more specific wins:', longest_match(['192.0.2.0/24', '192.0.2.128/25'], '192.0.2.150'))
