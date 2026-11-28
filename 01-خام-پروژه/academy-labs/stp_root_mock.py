"""Root bridge-ID comparison only, not an STP, RSTP, or LACP implementation."""
import re


def elect_root(bridges):
    """Compare complete 16-bit priority field then 48-bit MAC for one STP instance."""
    valid = []
    for priority, mac in bridges:
        if type(priority) is not int or not 0 <= priority <= 65535:
            raise ValueError('priority field must fit 16 bits')
        if not isinstance(mac, str) or not re.fullmatch(r'[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}', mac):
            raise ValueError('MAC must be six colon-separated hexadecimal octets')
        valid.append((priority, int(mac.replace(':', ''), 16), mac.lower()))
    if not valid:
        raise ValueError('at least one bridge is required')
    priority, _, mac = min(valid)
    return priority, mac


if __name__ == '__main__':
    bridges = [(32778, '02:00:00:00:00:02'), (32778, '02:00:00:00:00:01'),
               (24586, '02:00:00:00:00:03')]
    print('Lowest bridge ID:', elect_root(bridges))
    print('Mock only: no BPDU or network traffic')
