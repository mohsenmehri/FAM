"""Address formatting and TCP handshake arithmetic, not packets or a TCP stack."""
from ipaddress import IPv6Address


def ipv6_forms(value):
    addr = IPv6Address(value)
    return addr.exploded, addr.compressed


def handshake(client_isn, server_isn):
    if not all(isinstance(v, int) and 0 <= v < 2**32 for v in (client_isn, server_isn)):
        raise ValueError('sequence numbers must be unsigned 32-bit integers')
    # Model SYN and SYN+ACK with no data; SYN consumes one sequence number.
    return {'syn_seq': client_isn, 'syn_ack_seq': server_isn,
            'syn_ack_ack': (client_isn + 1) % 2**32,
            'final_ack_seq': (client_isn + 1) % 2**32,
            'final_ack_ack': (server_isn + 1) % 2**32}


if __name__ == '__main__':
    print('IPv6 expanded, compressed:', ipv6_forms('2001:db8:0:0:0:0:0:1'))
    print('No-data handshake:', handshake(100, 500))
