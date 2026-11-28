"""Checks a local configuration model, not a switch or live network."""
import html
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/ccna_02_vlan_lab.py'
spec=importlib.util.spec_from_file_location('vlan_lab',source)
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class VlanIntegrationTests(unittest.TestCase):
    def test_missing_native_and_voice(self):
        r=lab.audit_trunk_pair([10],[10],[10,50,999],[10,50,999],999,999,[10,50])
        self.assertFalse(r['model_checks_ok'])
        self.assertIn('SW1_NATIVE_MISSING: native VLAN 999 missing from SW1 database',r['issues'])
        self.assertIn('VLAN_50_MISSING_ON_SW2_DB',r['issues'])
        self.assertNotIn('effective_forwarding_vlans',r)

    def test_tag_and_dtp_and_validation(self):
        args=([10,999],[10,999],[10,999],[10,999],999,999,[10])
        self.assertFalse(lab.audit_trunk_pair(*args,sw1_tag_native=True)['model_checks_ok'])
        self.assertEqual(lab.evaluate_dtp_link('dynamic_auto','dynamic_auto')['operational_state'],'access_no_trunk')
        self.assertEqual(lab.evaluate_dtp_link('trunk','trunk',True,True)['operational_state'],'trunk')
        for invalid in ([], {}, None, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):lab.evaluate_dtp_link(invalid,'trunk')
        with self.assertRaises(ValueError):lab.audit_trunk_pair(*args,sw1_tag_native=1)

    def test_embedded_lab_and_original_fourth_question(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/ccna_02_vlan.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertIn('show vlan brief',bp['interactiveQuiz'][3]['title'])
        self.assertIn('show interfaces trunk',bp['interactiveQuiz'][3]['options'][bp['interactiveQuiz'][3]['correctIndex']])
        self.assertIn('روی تجهیز اجرا نشده',bp['evidence'])
