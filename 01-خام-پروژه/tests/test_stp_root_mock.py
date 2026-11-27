import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/stp_root_mock.py'
spec = importlib.util.spec_from_file_location('stp_root_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RootIDTests(unittest.TestCase):
    def test_priority_then_mac(self):
        bridges = [(32778, '02:00:00:00:00:02'), (32778, '02:00:00:00:00:01'),
                   (24586, '02:00:00:00:00:03')]
        self.assertEqual(m.elect_root(bridges), (24586, '02:00:00:00:00:03'))
        self.assertEqual(m.elect_root(bridges[:2]), (32778, '02:00:00:00:00:01'))
        with self.assertRaises(ValueError): m.elect_root([])
        with self.assertRaises(ValueError): m.elect_root([(65536, '02:00:00:00:00:01')])
        with self.assertRaises(ValueError): m.elect_root([(1, 'not-a-mac')])
