import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/vlan_trunk_mock.py'
spec = importlib.util.spec_from_file_location('vlan_trunk_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class VLANTrunkTests(unittest.TestCase):
    def test_ingress_classification(self):
        self.assertEqual(m.classify({10, 20}, 10, None), 10)
        self.assertEqual(m.classify({10, 20}, 10, 20), 20)
        self.assertIsNone(m.classify({10, 20}, 10, 30))
        self.assertIsNone(m.classify({20}, 10, None))
        with self.assertRaises(ValueError):
            m.classify({10}, 10, 0)

    def test_egress_decisions(self):
        self.assertEqual(m.forward(20, 'trunk', 10, {10, 20}), 'tag:20')
        self.assertEqual(m.forward(10, 'trunk', 10, {10, 20}), 'untagged')
        self.assertEqual(m.forward(30, 'trunk', 10, {10, 20}), 'drop')
        self.assertEqual(m.forward(20, 'access', 20), 'untagged')
        self.assertEqual(m.forward(10, 'access', 20), 'drop')
