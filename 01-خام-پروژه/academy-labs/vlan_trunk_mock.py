"""Single-port 802.1Q classification exercise; no frames or device access."""


def classify(allowed, native, tagged_vlan):
    """Assume native VLAN maps untagged traffic; return VLAN or None if denied.

    Deliberately excludes priority tags (VID 0), double tags and vendor options.
    """
    allowed = set(allowed)
    if not all(isinstance(v, int) and 1 <= v <= 4094 for v in allowed | {native}):
        raise ValueError('VLAN IDs must be in 1..4094')
    if tagged_vlan is not None and (not isinstance(tagged_vlan, int) or not 1 <= tagged_vlan <= 4094):
        raise ValueError('tagged VLAN must be in 1..4094')
    vlan = native if tagged_vlan is None else tagged_vlan
    return vlan if vlan in allowed else None


def forward(ingress_vlan, egress_kind, egress_vlan, allowed=()):
    """Simplified egress: native traffic untagged; access permits one VLAN."""
    if egress_kind == 'access':
        return 'untagged' if ingress_vlan == egress_vlan else 'drop'
    if egress_kind == 'trunk':
        if ingress_vlan not in allowed:
            return 'drop'
        return 'untagged' if ingress_vlan == egress_vlan else f'tag:{ingress_vlan}'
    raise ValueError('unknown egress kind')


if __name__ == '__main__':
    allowed, native = {10, 20}, 10
    for tag in (None, 20, 30):
        vlan = classify(allowed, native, tag)
        print('ingress tag:', tag, 'classified VLAN:', vlan)
    print('VLAN 20 out trunk:', forward(20, 'trunk', native, allowed))
    print('No switch or Ethernet frame accessed')
