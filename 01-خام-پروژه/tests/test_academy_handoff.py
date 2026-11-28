"""Check handoff coverage and ownership; this is not a semantic lesson review."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AcademyHandoffTests(unittest.TestCase):
    def test_every_historical_id_has_one_row_and_current_owner(self):
        inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text())
        ids = [item['legacyId'] for item in inventory['lessons']]
        self.assertEqual(len(ids), 114)
        self.assertEqual(len(set(ids)), 114)
        text = (ROOT / 'academy-labs/reviews/AGENT-HANDOFF-fa.md').read_text()
        rows = re.findall(r'^\| `([^`]+)` \| ([^|]+) \| `([0-9a-f]{40})` \| ([^|]+) \| ([^|]+) \|$', text, re.M)
        self.assertEqual(len(rows), 114)
        self.assertEqual({r[0] for r in rows}, set(ids))
        self.assertEqual(len({r[0] for r in rows}), 114)
        third = [row for row in rows if row[1].strip() == 'ایجنت سوم']
        mine = [row for row in rows if row[1].strip() == 'یکپارچه‌ساز']
        self.assertEqual((len(mine), len(third)), (33, 81))
        for lesson, owner, sha, status, action in rows:
            expected_third = (lesson.startswith(('spec_', 'ccie_', 'ccde_')) or (lesson.startswith('auto_') and lesson != 'auto_12') or (lesson.startswith('ccna_') and lesson not in {'ccna_01', 'ccna_02'}) or lesson in {'adv_01', 'adv_02', 'adv_03', 'adv_04', 'adv_bfd'})
            self.assertEqual(owner.strip() == 'ایجنت سوم', expected_third, lesson)
            self.assertTrue(status.strip(), lesson)
            self.assertTrue(action.strip(), lesson)
