"""Tests of intake candidates; not a complete content review or a production network test."""
import html
import importlib.util
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / 'academy-labs/candidates/agent3'


def load(name):
    spec = importlib.util.spec_from_file_location(name, CANDIDATES / f'{name}_lab.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class IntakeCandidateTests(unittest.TestCase):
    def test_candidate_scripts_match_embedded_and_not_student_catalogued(self):
        catalog = json.loads((ROOT / 'server/www/academy-assets/curriculum-catalog.json').read_text())
        ids = {lesson['id'] for track in catalog['paths'] for course in track['courses'] for lesson in course['lessons']}
        for name in ('ccde_18', 'auto_20'):
            with self.subTest(name=name):
                bp = json.loads((CANDIDATES / f'{name}.json').read_text())
                self.assertEqual(bp['lessonId'], name)
                self.assertIn((CANDIDATES / f'{name}_lab.py').read_text(), html.unescape(bp['stages']['lab']['html']))
                self.assertIn('در انتظار بازبینی', bp['reviewStatus'])
                if name == 'auto_20': self.assertIn(name, ids)
                else: self.assertNotIn(name, ids)

    def test_ccde_unknown_profile_type_fails_cleanly(self):
        lab = load('ccde_18')
        for profile in ([], {}, None, True, 'unknown'):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                lab.validate_pars_global_hld({}, profile)

    def test_auto20_zero_variance_and_large_finite_values(self):
        lab = load('auto_20')
        for baseline, value in (([1, 1], 1), ([1, 1], 2), ([0, 0], 0),
                                ([1, float('nan')], 2), ([True, 1], 2),
                                ([0, 1], float('inf'))):
            with self.subTest(baseline=baseline, value=value), self.assertRaises(ValueError):
                lab.z_score(value, baseline)
        self.assertAlmostEqual(lab.z_score(1e200, [1e200, 0]), 1.0)
        self.assertAlmostEqual(lab.z_score(1e308, [-1e308, 1e308]), 1.0)
        with self.assertRaises(ValueError): lab.z_score(1e308, [1e-308, 2e-308])
        self.assertGreater(lab.z_score(68, [22,23.5,21.8,22.4,23.1,22.7,21.9,22.6]), 3)
        for action in ('destroy_everything', '', None):
            with self.subTest(action=action), self.assertRaises(ValueError):
                lab.remediation_decision(action, 0, .95, False)
        for approved in ('False', 0, None):
            with self.subTest(approved=approved), self.assertRaises(ValueError):
                lab.remediation_decision('failover_regional_hub', 125, .96, approved)
        result=lab.remediation_decision('failover_regional_hub',125,.96,False)
        self.assertTrue(result['simulation_only']); self.assertFalse(result['simulated_execution_allowed'])

    def test_ccde18_jitter_and_unrounded_strict_rtt_boundaries(self):
        lab = load('ccde_18')
        design={'dc_distance_km':100, 'assumed_equipment_and_detour_overhead_ms':1,
                'storage_replication':'synchronous', 'target_rpo_minutes':0,
                'dci_l2_stretched':False, 'gslb_enabled':True,
                'wan_model':'hybrid_sdwan_regional_hubs_plus_sase',
                'cloud_hub':'dual_colo_cloud_exchange_direct_connect', 'macro_vrfs':3,
                'micro_sgt_enabled':True, 'eu_residency_policy_enforced':True,
                'eu_personal_data_transferred_outside_eea':False,
                'chapter_v_transfer_safeguard':None, 'encryption_in_transit_assumed':True}
        select='netapp_ontap_select_metrocluster_sds'
        def check(changes, profile=select):
            return lab.validate_pars_global_hld({**design, **changes}, profile)['domain_validations'][0]
        unknown=check({}); self.assertIsNone(unknown['modeled_jitter_ok']); self.assertFalse(unknown['pass'])
        self.assertIn('jitter assumption missing', unknown['note'])
        self.assertTrue(check({'assumed_jitter_ms':5})['pass'])
        self.assertFalse(check({'assumed_jitter_ms':5.001})['pass'])
        self.assertTrue(check({'storage_replication':'asynchronous','target_rpo_minutes':15})['pass'])
        for value in (-1, True, '0', float('nan'), float('inf'), 10**500):
            with self.subTest(jitter=value), self.assertRaises(ValueError): check({'assumed_jitter_ms':value})
        profile='netapp_vmsc_snapmirror_active_sync'
        self.assertTrue(check({'dc_distance_km':100,'assumed_equipment_and_detour_overhead_ms':8.599},profile)['pass'])
        self.assertFalse(check({'dc_distance_km':100,'assumed_equipment_and_detour_overhead_ms':8.6},profile)['pass'])
        self.assertFalse(check({'dc_distance_km':100,'assumed_equipment_and_detour_overhead_ms':8.601},profile)['pass'])
        for key in ('dci_l2_stretched','gslb_enabled','micro_sgt_enabled','eu_residency_policy_enforced','eu_personal_data_transferred_outside_eea','encryption_in_transit_assumed'):
            for value in ('False', 0, 1, None, [], {}):
                with self.subTest(key=key, value=value), self.assertRaises(ValueError): check({key:value})
            missing=design.copy(); del missing[key]
            with self.subTest(missing=key), self.assertRaises(ValueError): lab.validate_pars_global_hld(missing,select)
        self.assertFalse(check({'storage_replication':'invalid'})['pass'])
        self.assertIn('3 Macro VRFs',lab.validate_pars_global_hld({**design,'assumed_jitter_ms':5},select)['domain_validations'][-1]['note'])

    def test_ccna_vlan_reference_candidate_consistency(self):
        source = ROOT / 'academy-labs/candidates/agent1/ccna_02_vlan.json'
        lesson = json.loads(source.read_text())
        self.assertEqual(lesson['id'], 'ccna_02_vlan')
        self.assertEqual(len(lesson['quiz']), 4)
        self.assertIn('show vlan brief', lesson['quiz'][3]['q'])
        self.assertEqual(lesson['quiz'][3]['ans'], 1)
        self.assertIn('10,20,50,999', lesson['iosCommands'][1]['out'])
        self.assertIn('10,20,50,999', lesson['lab']['steps'][3])
        self.assertIn('نمونه ثابت', lesson['lab']['steps'][0])
        self.assertEqual(lesson['lab']['labType'], 'Reference')
        self.assertIn('در انتظار', lesson['candidateStatus'])
        catalog = json.loads((ROOT / 'server/www/academy-assets/curriculum-catalog.json').read_text())
        record = next(l for t in catalog['paths'] for c in t['courses'] for l in c['lessons'] if l['id'] == 'ccna_02_vlan')
        # The historical candidate remains a reference; the catalog uses the reviewed blueprint instead.
        self.assertEqual(record['blueprint'], '/academy-assets/v5/blueprints/ccna_02_vlan.json')
        self.assertNotIn('candidates/', record['blueprint'])
