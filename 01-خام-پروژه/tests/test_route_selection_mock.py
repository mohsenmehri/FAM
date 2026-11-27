import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/route_selection_mock.py'
spec = importlib.util.spec_from_file_location('route_selection_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RouteSelectionTests(unittest.TestCase):
    def test_same_prefix_selection_then_longest_match(self):
        routes = [('192.0.2.0/24', 1, 0, 'static'),
                  ('192.0.2.128/25', 110, 50, 'ospf'),
                  ('192.0.2.128/25', 120, 1, 'other')]
        self.assertEqual(m.choose(routes, '192.0.2.150'), ('192.0.2.128/25', 'ospf'))
        self.assertEqual(m.choose(routes, '192.0.2.10'), ('192.0.2.0/24', 'static'))
        self.assertIsNone(m.choose(routes, '198.51.100.1'))
        self.assertEqual(m.choose([('192.0.2.0/24', 110, 20, 'a'), ('192.0.2.0/24', 110, 10, 'b')],
                                  '192.0.2.1'), ('192.0.2.0/24', 'b'))
        with self.assertRaises(ValueError):
            m.choose([('192.0.2.0/24', -1, 0, 'x')], '192.0.2.1')
