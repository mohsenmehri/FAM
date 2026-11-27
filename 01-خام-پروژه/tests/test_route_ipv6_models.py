"""Tests for local models; no equipment or packet capture is involved."""
import importlib.util
import unittest
from pathlib import Path

LABS = Path(__file__).resolve().parents[1] / 'academy-labs'


def load(name):
    spec = importlib.util.spec_from_file_location(name, LABS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RouteIPv6ModelsTests(unittest.TestCase):
    def test_route_summary_exact_and_holes(self):
        m = load('route_summary_mock')
        self.assertEqual(m.cover(['192.0.2.0/26', '192.0.2.64/26']), ('192.0.2.0/25', True))
        self.assertEqual(m.cover(['192.0.2.0/26', '192.0.2.128/26']), ('192.0.2.0/24', False))
        self.assertEqual(m.cover(['192.0.2.0/24', '192.0.2.0/26']), ('192.0.2.0/24', True))
        with self.assertRaises(ValueError):
            m.cover([])
        with self.assertRaises(ValueError):
            m.cover(['192.0.2.1/26'])
        self.assertEqual(m.longest_match(['192.0.2.0/24', '192.0.2.128/25'], '192.0.2.150'), '192.0.2.128/25')
        self.assertIsNone(m.longest_match(['192.0.2.0/24'], '198.51.100.1'))

    def test_ipv6_and_handshake_wrap(self):
        m = load('ipv6_tcp_mock')
        self.assertEqual(m.ipv6_forms('2001:db8:0:0:0:0:0:1'),
                         ('2001:0db8:0000:0000:0000:0000:0000:0001', '2001:db8::1'))
        self.assertEqual(m.handshake(100, 500), {'syn_seq':100,'syn_ack_seq':500,'syn_ack_ack':101,'final_ack_seq':101,'final_ack_ack':501})
        self.assertEqual(m.handshake(2**32 - 1, 2**32 - 1)['final_ack_ack'], 0)
        with self.assertRaises(ValueError):
            m.handshake(-1, 1)
        with self.assertRaises(ValueError):
            m.ipv6_forms('2001::db8::1')
