"""Local assumptions model only; no hypervisor or cloud is contacted."""
import html
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/ccna_v1_lab.py'
spec=importlib.util.spec_from_file_location('v1',source);lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
class VirtualizationIntegrationTests(unittest.TestCase):
    def test_configuration_model_not_connectivity(self):
        self.assertTrue(lab.audit_vswitch_uplink('VST',[10,30],'trunk',[10,30])['model_checks_ok'])
        self.assertFalse(lab.audit_vswitch_uplink('VST',[10,30],'access',[10])['model_checks_ok'])
        self.assertFalse(lab.audit_vswitch_uplink('EST',[10],'access',[10,20])['model_checks_ok'])
        self.assertNotIn('reachable',lab.audit_vswitch_uplink('EST',[10],'access',[10]))
        for bad in ([],{},None,True):
            with self.subTest(bad=bad),self.assertRaises(ValueError):lab.audit_vswitch_uplink(bad,[10],'access',[10])
        with self.assertRaises(ValueError):lab.audit_vswitch_uplink('VST',[True],'trunk',[10])
    def test_embedded_review_and_contract(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/ccna_v1.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertIn('روی تجهیز اجرا نشده',bp['evidence'])
        self.assertEqual(bp['interactiveQuiz'][4]['options'][bp['interactiveQuiz'][4]['correctIndex']],'IaaS')
