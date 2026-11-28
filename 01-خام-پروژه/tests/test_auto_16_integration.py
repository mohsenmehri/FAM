"""Tests a toy state machine; no real CI runner, scan, deploy or rollback."""
import html
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/auto_16_lab.py'
spec=importlib.util.spec_from_file_location('a16',source);lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
class PipelineModelTests(unittest.TestCase):
    def test_gate_order_and_simulated_recovery(self):
        good={'raw_yaml':'vlan: 10','vlan_id':10}
        self.assertEqual(lab.run_pipeline(good)['status'],'blocked_at_approval')
        self.assertFalse(lab.run_pipeline(good)['deploy_simulated'])
        leak=lab.run_pipeline({'raw_yaml':'password: leaked','vlan_id':10},approved=True)
        self.assertEqual(leak['status'],'blocked_at_security_scan');self.assertFalse(leak['deploy_simulated'])
        bad=lab.run_pipeline(good,post_verify_ok=False,approved=True)
        self.assertEqual(bad['status'],'rollback_simulated');self.assertTrue(bad['rollback_simulated'])
        for v in (True,0,4095,None):
            with self.subTest(vlan=v):self.assertEqual(lab.run_pipeline({'vlan_id':v},approved=True)['status'],'blocked_at_test')
        with self.assertRaises(ValueError):lab.run_pipeline(good,approved=1)
    def test_embedded_and_boundaries(self):
        d=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_16.json').read_text())
        self.assertIn(source.read_text(),html.unescape(d['stages']['lab']['html']))
        self.assertIn('روی تجهیز اجرا نشده',d['evidence'])
        self.assertIn('YAML را parse و با VLAN تطبیق نمی',html.unescape(d['stages']['lab']['html']))
