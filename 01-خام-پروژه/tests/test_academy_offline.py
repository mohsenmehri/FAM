"""Offline build parity. Structural equality is not a content review."""
import importlib.util
import json
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parent
spec = importlib.util.spec_from_file_location('build_academy_offline', PACKAGE / 'tools/build_academy_offline.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class OfflineBuildTests(unittest.TestCase):
    def test_committed_offline_is_generated_from_current_online_assets(self):
        self.assertEqual((REPO / 'FAM-Academy-Offline.html').read_text(encoding='utf-8'), build.build())

    def test_all_catalog_blueprints_are_embedded_and_counted(self):
        text = build.build()
        catalog = json.loads((PACKAGE / 'server/www/academy-assets/curriculum-catalog.json').read_text(encoding='utf-8'))
        lessons = [l for p in catalog['paths'] for c in p['courses'] for l in c['lessons']]
        self.assertEqual(len(lessons), 127)
        self.assertIn(f'هر {len(lessons)} درس فعال', text)
        self.assertIn('پوشش کامل ۱۱۴ شناسه تاریخی', text)
        self.assertIn('شبیه‌ساز آموزشی CLI', text)
        self.assertIn('FamAcademySimulator', text)
        for lesson in lessons:
            with self.subTest(lesson=lesson['id']):
                self.assertIn(lesson['blueprint'], text)
        self.assertNotIn('<script src="/academy-assets/', text)
        self.assertNotIn('<link rel="stylesheet" href="/academy-assets/', text)

    def test_embedded_json_matches_each_online_source_independently(self):
        text = (REPO / 'FAM-Academy-Offline.html').read_text(encoding='utf-8')
        marker = '  const resources = '
        self.assertEqual(text.count(marker), 1)
        embedded, _ = json.JSONDecoder().raw_decode(text.split(marker, 1)[1])
        assets = PACKAGE / 'server/www/academy-assets'
        catalog = json.loads((assets / 'curriculum-catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(embedded['/academy-assets/curriculum-catalog.json'], catalog)
        lessons = [l for p in catalog['paths'] for c in p['courses'] for l in c['lessons']]
        self.assertEqual(len(embedded), len(lessons) + 1)
        for lesson in lessons:
            ref = lesson['blueprint']
            with self.subTest(lesson=lesson['id']):
                self.assertEqual(embedded[ref], json.loads((assets / ref.removeprefix('/academy-assets/')).read_text(encoding='utf-8')))


if __name__ == '__main__':
    unittest.main()
