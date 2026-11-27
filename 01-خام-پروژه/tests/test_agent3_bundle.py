import html
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bundle', ROOT / 'tools/inspect_agent3_bundle.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Agent3BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.inventory = {'lessons': [{'legacyId':'auto_01','owner':'agent-3'}]}
        self.bp = self.root / 'server/www/academy-assets/v5/blueprints/auto_01.json'
        self.lab = self.root / 'academy-labs/agent3/auto_01_lab.py'
        self.review = self.root / 'academy-labs/reviews/auto_01-review-fa.md'
        for p in (self.bp,self.lab,self.review): p.parent.mkdir(parents=True, exist_ok=True)
        self.code = 'import subprocess\nprint("NOT EXECUTED")\n'
        self.lab.write_text(self.code)
        self.review.write_text('self review')
        self.data = {'schema':'fam-app-blueprint-v1', 'lessonId':'auto_01', 'objectiveId':'auto_01',
                     'stages': {'lab': {'html':html.escape(self.code)}}}
        self.bp.write_text(json.dumps(self.data))

    def test_static_inspection_and_source_mismatch(self):
        result = m.inspect(self.root, self.inventory)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['records']['auto_01']['flaggedImports'], ['subprocess'])
        self.lab.write_text(self.code + 'changed = True\n')
        self.assertIn('embedded lab', m.inspect(self.root, self.inventory)['errors'][0]['error'])

    def test_missing_final_newline_is_reported(self):
        self.data['stages']['lab']['html'] = html.escape(self.code[:-1])
        self.bp.write_text(json.dumps(self.data))
        result = m.inspect(self.root, self.inventory)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['records']['auto_01']['embeddedLabMatch'], 'missing-final-newline')
        self.data['stages']['lab']['html'] = html.escape(self.code[:-2])
        self.bp.write_text(json.dumps(self.data))
        self.assertTrue(m.inspect(self.root, self.inventory)['errors'])

    def test_missing_and_wrong_id_and_escape(self):
        self.review.unlink()
        self.assertEqual(len(m.inspect(self.root, self.inventory)['errors']), 1)
        self.review.write_text('review')
        self.data['objectiveId'] = 'other'; self.bp.write_text(json.dumps(self.data))
        self.assertIn('mismatch', m.inspect(self.root, self.inventory)['errors'][0]['error'])
        self.bp.unlink()
        outside = self.root.parent / (self.root.name + '-outside.json')
        outside.write_text('{}'); self.addCleanup(outside.unlink)
        self.bp.symlink_to(outside)
        self.assertIn('outside', m.inspect(self.root, self.inventory)['errors'][0]['error'])
