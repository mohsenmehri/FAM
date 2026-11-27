"""Tiny mode-transition exercise; not IOS, no configuration or network access."""
TRANSITIONS = {
    ('user', 'enable'): 'privileged',
    ('privileged', 'disable'): 'user',
    ('privileged', 'configure terminal'): 'global-config',
    ('global-config', 'interface gigabitethernet 0/1'): 'interface-config',
    ('global-config', 'end'): 'privileged',
    ('global-config', 'exit'): 'privileged',
    ('interface-config', 'exit'): 'global-config',
    ('interface-config', 'end'): 'privileged',
}


def step(mode, command):
    key = (mode, command.strip().lower())
    if key not in TRANSITIONS:
        raise ValueError('unsupported in this toy model')
    return TRANSITIONS[key]


if __name__ == '__main__':
    mode = 'user'
    for command in ('enable', 'configure terminal', 'interface gigabitethernet 0/1', 'exit', 'end'):
        new_mode = step(mode, command)
        print(f'{mode} -- {command} --> {new_mode}')
        mode = new_mode
    print('Mock only: no IOS configuration or device access')
