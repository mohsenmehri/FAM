"""Local simulation tests; no controller or real network is modified."""
import html
import importlib.util
import json
import statistics
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'academy-labs/agent3/auto_20_lab.py'
spec = importlib.util.spec_from_file_location('auto20_integrated', source)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class AIOpsMockTests(unittest.TestCase):
    def test_z_score_and_numeric_edges(self):
        for baseline, value in (([1, 1], 1), ([1, 1], 2), ([0, 0], 0),
                                ([1, float('nan')], 2), ([True, 1], 2), ([0, 1], float('inf'))):
            with self.subTest(baseline=baseline, value=value), self.assertRaises(ValueError): lab.z_score(value, baseline)
        for v, b in ((1e200,[1e200,0]), (1e308,[-1e308,1e308])):
            self.assertAlmostEqual(lab.z_score(v,b),1)
        with self.assertRaises(ValueError): lab.z_score(1e308,[1e-308,2e-308])
        baseline=[22,23.5,21.8,22.4,23.1,22.7,21.9,22.6]
        self.assertAlmostEqual(lab.z_score(68,baseline),(68-statistics.mean(baseline))/statistics.pstdev(baseline),places=10)

    def test_gate_and_topology_do_not_claim_real_execution(self):
        for bad in ('False',None,0,1):
            with self.subTest(approval=bad), self.assertRaises(ValueError): lab.remediation_decision('failover_regional_hub',125,.96,bad)
        for bad in ('destroy_everything','',None):
            with self.subTest(action=bad), self.assertRaises(ValueError): lab.remediation_decision(bad,0,.95,False)
        self.assertFalse(lab.remediation_decision('failover_regional_hub',125,.96,False)['simulated_execution_allowed'])
        result=lab.remediation_decision('failover_regional_hub',125,.96,True)
        self.assertTrue(result['simulation_only']); self.assertTrue(result['simulated_execution_allowed'])
        self.assertFalse(lab.remediation_decision('shift_single_branch_sdwan_path',1,.849,False)['simulated_execution_allowed'])
        self.assertTrue(lab.remediation_decision('shift_single_branch_sdwan_path',1,.85,False)['simulated_execution_allowed'])
        result=lab.correlate_root_cause({'west'},[{'hub':'west','branch_id':'1'},{'hub':'east','branch_id':'2'}])
        self.assertEqual(result['suppressed_child_branch_alerts'],1); self.assertEqual(result['independent_branch_alerts'],['2'])
        self.assertIn('do NOT prove',result['causal_caveat'])

    def test_embedded_code_matches_and_review_is_visible(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_20.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertIn('بازبینی مستقل انسانی انجام نشده',bp['reviewStatus'])
        self.assertIn('سناریوی تجهیز مرجع',bp['evidence'])
        self.assertEqual(len(bp['interactiveQuiz']),12)
