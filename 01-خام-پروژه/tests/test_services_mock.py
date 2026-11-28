import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/services_mock.py'
spec = importlib.util.spec_from_file_location('services_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ServicesMockTests(unittest.TestCase):
    def test_initial_dhcp_exchange(self):
        self.assertEqual([event[0] for event in m.dhcp_exchange('192.0.2.10', '192.0.2.10')],
                         ['DISCOVER', 'OFFER', 'REQUEST', 'ACK'])
        with self.assertRaises(ValueError):
            m.dhcp_exchange('192.0.2.10', '192.0.2.11')

    def test_distinct_pat_mappings_and_validation(self):
        a = ('10.0.0.10', 50000, 'TCP')
        b = ('10.0.0.11', 50000, 'TCP')
        result = m.pat_translate([a, a, b], '198.51.100.10')
        self.assertEqual(result[a], ('198.51.100.10', 40000, 'TCP'))
        self.assertEqual(result[b], ('198.51.100.10', 40001, 'TCP'))
        with self.assertRaises(ValueError):
            m.pat_translate([('10.0.0.1', 0, 'TCP')], '198.51.100.10')
        with self.assertRaises(ValueError):
            m.pat_translate([('10.0.0.1', 80, 'ICMP')], '198.51.100.10')
