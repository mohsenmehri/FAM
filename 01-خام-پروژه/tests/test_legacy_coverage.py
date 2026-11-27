"""Partition and catalog integrity, not content or migration validation."""
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'server/www/academy-assets'


class LegacyCoverageTests(unittest.TestCase):
    def test_partition_is_disjoint_complete_and_assigned(self):
        inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text())
        rows = inventory['lessons']
        ids = [x['legacyId'] for x in rows]
        self.assertEqual(inventory['lessonCount'], 114)
        self.assertEqual(len(ids), 114)
        self.assertEqual(len(set(ids)), 114)
        self.assertEqual(Counter(x['owner'] for x in rows), {'integrator':15, 'agent-1':35, 'agent-3':64})
        self.assertEqual({x['legacyId'] for x in rows if x['owner'] == 'integrator'},
                         {f's{i:02}' for i in range(1, 13)} | {'ccna_01','ccna_02','auto_12'})
        for row in rows:
            i, owner = row['legacyId'], row['owner']
            if owner == 'agent-1': self.assertTrue(i.startswith(('ccna_', 'adv_', 'ccnp_')))
            if owner == 'agent-3': self.assertTrue(i.startswith(('spec_', 'ccie_', 'ccde_', 'auto_')) and i != 'auto_12')

    def test_current_integrator_lessons_are_unique_and_aliases_do_not_claim_migration(self):
        data = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text())
        catalog = json.loads((ASSETS / 'curriculum-catalog.json').read_text())
        lessons = [x for p in catalog['paths'] for c in p['courses'] for x in c['lessons']]
        catalog_ids = [x['id'] for x in lessons]
        self.assertEqual(len(catalog_ids), len(set(catalog_ids)))
        records = {x['id']: x for x in lessons}
        for row in data['lessons']:
            if row['owner'] != 'integrator': continue
            legacy = row['legacyId']
            catalog_id = data['catalogAliases'].get(legacy, legacy)
            self.assertIn(catalog_id, records)
            self.assertFalse(legacy in records and legacy != catalog_id)
            path = records[catalog_id]['blueprint'].removeprefix('/academy-assets/')
            blueprint = json.loads((ASSETS / path).read_text())
            self.assertEqual(blueprint['lessonId'], catalog_id)
            self.assertEqual(blueprint['objectiveId'], legacy)
        # Aliases only link content identity; no progress migration is asserted.
        self.assertEqual(data['catalogAliases'], {'s01':'academy-stage-zero-osi-fa', 'auto_12':'academy-automation-terraform'})

class HistoricalVerificationTests(unittest.TestCase):
    def test_mismatched_hash_ids_and_titles_are_rejected(self):
        import hashlib
        import importlib.util
        import copy
        spec = importlib.util.spec_from_file_location('verify', ROOT / 'tools/verify_legacy_inventory.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text())
        synthetic = {'lessons': {row['legacyId']: {'title': row['title']} for row in inventory['lessons']}}
        raw = json.dumps(synthetic).encode()
        inv = copy.deepcopy(inventory)
        inv['sourceSha256'] = hashlib.sha256(raw).hexdigest()
        self.assertEqual(module.verify(raw, inv), 114)
        with self.assertRaises(ValueError): module.verify(raw + b' ', inv)
        bad = copy.deepcopy(inv); bad['lessons'][0]['title'] = 'wrong'
        with self.assertRaises(ValueError): module.verify(raw, bad)
        bad = copy.deepcopy(inv); bad['lessons'][0]['legacyId'] = bad['lessons'][1]['legacyId']
        with self.assertRaises(ValueError): module.verify(raw, bad)
