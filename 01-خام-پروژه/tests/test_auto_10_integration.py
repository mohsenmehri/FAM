"""Educational validator, not a YANG compiler or a real network test."""
import html
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'academy-labs/agent3/auto_10_lab.py'
spec = importlib.util.spec_from_file_location('auto10', source)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class YangMockTests(unittest.TestCase):
    def test_representative_examples_and_fail_closed_fields(self):
        self.assertEqual(lab.validate_vlan_payload({'vlans':[{'vlan-id':10,'name':'FINANCE','static-ip':'192.0.2.1/24'}, {'vlan-id':20,'name':'VOICE','dhcp':False}, {'vlan-id':4094,'name':'X'}]}), [])
        invalid = [None, [], {'vlans':'wrong'}, {'vlans':[None]},
                   {'vlans':[{'vlan-id':True,'name':'X'}]},
                   {'vlans':[{'vlan-id':0,'name':'X'}]},
                   {'vlans':[{'vlan-id':4095,'name':'X'}]},
                   {'vlans':[{'vlan-id':1,'name':'bad name'}]},
                   {'vlans':[{'vlan-id':1,'name':'X','static-ip':'999.1.1.1/24'}]},
                   {'vlans':[{'vlan-id':1,'name':'X','static-ip':'192.0.2.1'}]},
                   {'vlans':[{'vlan-id':1,'name':'X','static-ip':None}]},
                   {'vlans':[{'vlan-id':1,'name':'X','dhcp':'False'}]},
                   {'vlans':[{'vlan-id':1,'name':'X','static-ip':'192.0.2.1/24','dhcp':False}]},
                   {'vlans':[{'vlan-id':1,'name':'X','oper-packet-count':0}]},
                   {'vlans':[{'vlan-id':1,'name':'X'}, {'vlan-id':1,'name':'Y'}]},
                   {'vlans':[{'vlan-id':1,'name':'X','surprise':1}]}, {'vlans':[],'surprise':1}]
        for value in invalid:
            with self.subTest(payload=value): self.assertTrue(lab.validate_vlan_payload(value))

    def test_embedded_matches_executed_model(self):
        bp = json.loads((ROOT / 'server/www/academy-assets/v5/blueprints/auto_10.json').read_text())
        self.assertIn(source.read_text(), html.unescape(bp['stages']['lab']['html']))
        self.assertIn('بازبینی مستقل انسانی انجام نشده', bp['reviewStatus'])
        self.assertIn('سناریوی تجهیز مرجع', bp['evidence'])
        self.assertEqual(len(bp['interactiveQuiz']), 12)
