"""Parse a fixed illustrative JSON response; no API or device connection.

Not a RESTCONF or YANG validator and not intended for untrusted input.
"""
import json


def parse_interfaces(status, body):
    if status != 200:
        raise ValueError('mock expected a successful 200 response')
    doc = json.loads(body)
    rows = doc['ietf-interfaces:interfaces']['interface']
    if not isinstance(rows, list):
        raise ValueError('interface must be a list')
    result = []
    for row in rows:
        name, enabled = row['name'], row['enabled']
        if not isinstance(name, str) or not isinstance(enabled, bool):
            raise ValueError('invalid field type')
        result.append((name, enabled))
    return result


if __name__ == '__main__':
    example = '{"ietf-interfaces:interfaces":{"interface":[{"name":"Ethernet1","enabled":true},{"name":"Ethernet2","enabled":false}]}}'
    print('Mock JSON only:', parse_interfaces(200, example))
    print('No HTTP request or device access')
