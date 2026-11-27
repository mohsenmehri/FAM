"""Single-VLAN learning model, not an IOS switch or network simulator."""
BROADCAST = 'ff:ff:ff:ff:ff:ff'


def learn_and_forward(table, ports, ingress, src, dst):
    """Mutates the toy table. Assumes active ports, unicast source and one VLAN."""
    if ingress not in ports:
        raise ValueError('unknown ingress port')
    table[src] = ingress
    if dst == BROADCAST or dst not in table:
        return sorted(port for port in ports if port != ingress)
    output = table[dst]
    if output not in ports:
        raise ValueError('table contains an unknown port')
    return [] if output == ingress else [output]


if __name__ == '__main__':
    ports, table = ['p1', 'p2', 'p3'], {}
    print('Python Mock: single VLAN; no frames sent')
    print('unknown B:', learn_and_forward(table, ports, 'p1', 'A', 'B'))
    print('B replies:', learn_and_forward(table, ports, 'p2', 'B', 'A'))
    print('A to known B:', learn_and_forward(table, ports, 'p1', 'A', 'B'))
