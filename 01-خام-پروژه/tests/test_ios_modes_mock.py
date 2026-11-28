import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/ios_modes_mock.py'
spec = importlib.util.spec_from_file_location('ios_modes_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class IOSModesMockTests(unittest.TestCase):
    def test_mode_transitions_and_unsupported(self):
        mode = 'user'
        for cmd, target in [('enable', 'privileged'), ('configure terminal', 'global-config'),
                            ('interface gigabitethernet 0/1', 'interface-config'),
                            ('exit', 'global-config'), ('end', 'privileged'), ('disable', 'user')]:
            mode = m.step(mode, cmd)
            self.assertEqual(mode, target)
        with self.assertRaises(ValueError):
            m.step('user', 'configure terminal')
        with self.assertRaises(ValueError):
            m.step('privileged', 'write erase')
