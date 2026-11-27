"""Python local exercise against synthetic data; no equipment is contacted."""
import html
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('auto02',ROOT/'academy-labs/agent3/auto_02_lab.py')
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class PythonLabTests(unittest.TestCase):
    def test_synthetic_table_and_fail_closed(self):
        rows=lab.parse_interfaces(lab.SAMPLE_SHOW_IP_INT_BR)
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[1]['status'],'administratively down')
        self.assertEqual(rows[1]['protocol'],'down')
        for text in ('', 'Gi0/1 192.0.2.1 YES manual up up',
                     'Interface IP-Address OK? Method Status Protocol\nGi0/1 broken'):
            with self.subTest(text=text), self.assertRaises(ValueError):lab.parse_interfaces(text)
        self.assertEqual(lab.parse_interfaces('Interface IP-Address OK? Method Status Protocol\n'),[])

    def test_vlan_and_embedded_source(self):
        self.assertEqual(lab.diff_vlans({10,20,30},{10,99}), {'to_add':[20,30],'unexpected_extra':[99],'compliant':[10]})
        for value in ('0','4095','bad'):
            with self.subTest(value=value),self.assertRaises(ValueError):lab.safe_parse_vlan_id(value)
        self.assertEqual(lab.safe_parse_vlan_id('4094'),4094)
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_02.json').read_text())
        self.assertIn((ROOT/'academy-labs/agent3/auto_02_lab.py').read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertIn('بازبینی مستقل انسانی انجام نشده',bp['reviewStatus'])
