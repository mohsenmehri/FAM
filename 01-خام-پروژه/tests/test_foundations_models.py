"""Local Python models and calculations only; not real devices."""
import importlib.util
import html
import json
import subprocess
import sys
import unittest
from pathlib import Path

LABS = Path(__file__).resolve().parents[1] / 'academy-labs'

def load(name):
    spec = importlib.util.spec_from_file_location(name, LABS / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FoundationModelsTests(unittest.TestCase):
    def test_arp_target_on_and_off_link(self):
        m = load('ethernet_arp_mock')
        self.assertEqual(str(m.arp_target('192.0.2.10/24', '192.0.2.20', '192.0.2.1')), '192.0.2.20')
        self.assertEqual(str(m.arp_target('192.0.2.10/24', '198.51.100.80', '192.0.2.1')), '192.0.2.1')
        with self.assertRaises(ValueError):
            m.arp_target('192.0.2.10/24', '198.51.100.80', '192.0.3.1')

    def test_learning_forwarding_flooding_and_filter(self):
        m = load('switch_learning_mock')
        table, ports = {}, ['p1', 'p2', 'p3']
        self.assertEqual(m.learn_and_forward(table, ports, 'p1', 'A', 'B'), ['p2', 'p3'])
        self.assertEqual(m.learn_and_forward(table, ports, 'p2', 'B', 'A'), ['p1'])
        self.assertEqual(m.learn_and_forward(table, ports, 'p1', 'A', 'B'), ['p2'])
        self.assertEqual(m.learn_and_forward(table, ports, 'p1', 'C', 'A'), [])
        self.assertEqual(m.learn_and_forward(table, ports, 'p2', 'B', m.BROADCAST), ['p1', 'p3'])
        with self.assertRaises(ValueError):
            m.learn_and_forward(table, ports, 'missing', 'A', 'B')

    def test_subnet_boundaries_and_31(self):
        m = load('ipv4_subnet_lab')
        result = m.describe('192.0.2.191/26')
        self.assertEqual((result['network'], result['broadcast_field'], result['mask']),
                         ('192.0.2.128', '192.0.2.191', '255.255.255.192'))
        self.assertEqual((result['python_host_first'], result['python_host_last'], result['python_host_count']),
                         ('192.0.2.129', '192.0.2.190', 62))
        self.assertEqual(m.describe('192.0.2.0/31')['python_host_count'], 2)
        self.assertEqual(m.describe('0.0.0.0/0')['address_count'], 2**32)

    def test_blueprints_embed_model_and_pending_status(self):
        assets = LABS.parent / "server/www/academy-assets/v5/blueprints"
        for lesson, name in (("s02", "ethernet_arp_mock"), ("s03", "switch_learning_mock"), ("s04", "ipv4_subnet_lab")):
            with self.subTest(lesson=lesson):
                bp = json.loads((assets / f"{lesson}.json").read_text())
                self.assertIn("Pending", bp["reviewStatus"])
                self.assertIn((LABS / f"{name}.py").read_text(), html.unescape(bp["stages"]["lab"]["html"]))

    def test_examples_run_locally(self):
        for name in ('ethernet_arp_mock', 'switch_learning_mock', 'ipv4_subnet_lab'):
            with self.subTest(name=name):
                r = subprocess.run([sys.executable, str(LABS / f'{name}.py')], text=True, capture_output=True, check=True, timeout=5)
                self.assertTrue(r.stdout)


if __name__ == '__main__':
    unittest.main()
