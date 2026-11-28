"""Simplified routing thought experiment; never reads or changes system routes."""
from ipaddress import IPv4Address, IPv4Network


def choose(candidates, destination):
    """Candidate: (prefix, admin_distance, metric, name).

    Illustrative policy: minimum AD then metric for each identical prefix;
    longest match among selected prefixes. Does not model protocol-specific
    comparability, equal-cost multipath, reachability, or real IOS behavior.
    """
    selected = {}
    for prefix, distance, metric, name in candidates:
        net = IPv4Network(prefix, strict=True)
        if distance < 0 or metric < 0:
            raise ValueError('distance and metric must be nonnegative')
        candidate = (distance, metric, name)
        if net not in selected or candidate < selected[net]:
            selected[net] = candidate
    address = IPv4Address(destination)
    matching = [net for net in selected if address in net]
    if not matching:
        return None
    network = max(matching, key=lambda net: net.prefixlen)
    return str(network), selected[network][2]


if __name__ == '__main__':
    routes = [('192.0.2.0/24', 1, 0, 'static'),
              ('192.0.2.128/25', 110, 50, 'ospf'),
              ('192.0.2.128/25', 120, 1, 'other')]
    print('Toy route selection for 192.0.2.150:', choose(routes, '192.0.2.150'))
    print('No real routing table or device accessed')
