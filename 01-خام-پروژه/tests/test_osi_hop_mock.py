"""Tests for a Python model, not real IOS or network packet execution."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / 'academy-labs' / 'osi_hop_mock.py'
spec = importlib.util.spec_from_file_location('osi_hop_mock', PATH)
mock = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mock
spec.loader.exec_module(mock)


class OsiHopMockTests(unittest.TestCase):
    def test_hop_changes_ttl_and_link_addresses_not_ip(self):
        packet = mock.Packet('192.0.2.10', '198.51.100.80', 64)
        result = mock.forward(packet, 'in', 'out', 'next')
        self.assertEqual((result['packet'].src_ip, result['packet'].dst_ip), (packet.src_ip, packet.dst_ip))
        self.assertEqual((packet.ttl, result['packet'].ttl), (64, 63))
        self.assertEqual((result['incoming_frame_dst'], result['outgoing_frame_src'], result['outgoing_frame_dst']), ('in', 'out', 'next'))

    def test_ttl_expiry_and_missing_next_hop_fail(self):
        with self.assertRaises(ValueError):
            mock.forward(mock.Packet('a', 'b', 1), 'in', 'out', 'next')
        with self.assertRaises(ValueError):
            mock.forward(mock.Packet('a', 'b', 64), 'in', 'out', '')

    def test_example_runs(self):
        result = subprocess.run([sys.executable, str(PATH)], capture_output=True, text=True, check=True, timeout=5)
        self.assertIn('Mock only; no network traffic', result.stdout)
        self.assertIn('198.51.100.80 TTL 63', result.stdout)


if __name__ == '__main__':
    unittest.main()
