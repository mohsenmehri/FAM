import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/vxlan_mtu_mock.py'
spec = importlib.util.spec_from_file_location('vxlan_mtu_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class VXLANSizeTests(unittest.TestCase):
    def test_ip_mtu_scenarios(self):
        self.assertEqual(m.fits(1500, 1550), (1550, True))
        self.assertEqual(m.fits(1500, 1549), (1550, False))
        self.assertEqual(m.fits(1500, 1550, outer_ip_version=6), (1570, False))
        self.assertEqual(m.fits(1500, 1554, inner_vlan_tags=1), (1554, True))
        self.assertEqual(m.outer_ip_size(1500, inner_vlan_tags=2), 1558)
        with self.assertRaises(ValueError): m.outer_ip_size(0)
        with self.assertRaises(ValueError): m.outer_ip_size(1500, outer_ip_version=5)
        with self.assertRaises(ValueError): m.fits(1500, 0)

    def test_strict_types_and_boundaries(self):
        for bad in (True, False, 1.0, '1500', None, -1, 0):
            with self.subTest(field='inner', value=bad), self.assertRaises(ValueError): m.outer_ip_size(bad)
            with self.subTest(field='mtu', value=bad), self.assertRaises(ValueError): m.fits(1500, bad)
        for bad in (True, False, 1.0, -1, 3, None, '1'):
            with self.subTest(field='tags', value=bad), self.assertRaises(ValueError): m.outer_ip_size(1500, inner_vlan_tags=bad)
        for bad in (True, 4.0, 6.0, '4', None, 5):
            with self.subTest(field='version', value=bad), self.assertRaises(ValueError): m.outer_ip_size(1500, outer_ip_version=bad)
        self.assertEqual(m.fits(1500, 1578, inner_vlan_tags=2, outer_ip_version=6),(1578,True))
        self.assertEqual(m.fits(1500, 1577, inner_vlan_tags=2, outer_ip_version=6),(1578,False))
