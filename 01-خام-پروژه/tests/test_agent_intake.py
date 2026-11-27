import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('intake', ROOT / 'tools/inspect_agent_blueprints.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text())
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def file(self, name, lesson, **changes):
        bp = {'schema':'fam-app-blueprint-v1','lessonId':lesson,
              'sections':[{'html':'untrusted'}], 'interactiveQuiz':[{'title':'untrusted'}]}
        bp.update(changes)
        path = Path(self.tmp.name) / name
        path.write_text(json.dumps(bp))
        return path

    def test_read_only_owner_and_duplicate_checks(self):
        good = self.file('good.json', 'ccna_03')
        result = m.inspect([good], 'agent-1', self.inventory)
        self.assertEqual(list(result['acceptedForInspection']), ['ccna_03'])
        self.assertEqual(result['errors'], [])
        self.assertIn('not integrated', result['warning'])
        self.assertEqual(len(result['notYetProvided']), 34)
        self.assertTrue(m.inspect([good, good], 'agent-1', self.inventory)['errors'])
        self.assertTrue(m.inspect([good], 'agent-3', self.inventory)['errors'])
        self.assertTrue(m.inspect([self.file('other.json', 's01')], 'agent-1', self.inventory)['errors'])
        self.assertTrue(m.inspect([self.file('broken.json', 'ccna_03', sections=[])], 'agent-1', self.inventory)['errors'])
        self.assertTrue(m.inspect([], 'agent-1', self.inventory)['errors'])

    def test_malformed_and_unexpected_schema(self):
        p = Path(self.tmp.name) / 'bad.json'; p.write_text('{')
        self.assertTrue(m.inspect([p], 'agent-3', self.inventory)['errors'])
        self.assertTrue(m.inspect([self.file('schema.json','spec_ent',schema='unsupported')], 'agent-3', self.inventory)['errors'])
