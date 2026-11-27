import html
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/auto_03_lab.py'
spec=importlib.util.spec_from_file_location('auto03',source)
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class MockNornirTests(unittest.TestCase):
    def test_context_fallback_and_pilot(self):
        conn=lab.MockNetmikoConnection('192.0.2.1')
        with self.assertRaises(RuntimeError):
            with conn:
                self.assertIsInstance(conn.send_command('show ip interface brief',True),list)
                self.assertIsInstance(conn.send_command('unknown',True),str)
                raise RuntimeError('example')
        self.assertTrue(conn.closed);self.assertFalse(conn.connected)
        inv=[{'host':'a','role':'pilot'},{'host':'b','role':'prod'}]
        result=lab.run_nornir_style_pilot(inv,'pilot',['show'],True,2)
        self.assertEqual(len(result),1);self.assertFalse(result[0]['applied']);self.assertTrue(result[0]['session_closed'])
        self.assertEqual(lab.run_nornir_style_pilot(inv,'none',['show']),[])
        # Applied means in-memory mock only, not an SSH or production change.
        self.assertTrue(lab.run_nornir_style_pilot(inv,'pilot',['show'],False,2)[0]['applied'])
        for bad in ('false', 0, 1, None):
            with self.subTest(flag=bad),self.assertRaises(ValueError):lab.run_nornir_style_pilot(inv,'pilot',['show'],bad)
        for bad in (0,True,1.5):
            with self.subTest(workers=bad),self.assertRaises(ValueError):lab.run_nornir_style_pilot(inv,'pilot',['show'],True,bad)
        with self.assertRaises(ValueError):lab.run_nornir_style_pilot(inv,'pilot','config',True)

    def test_embedded(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_03.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertEqual(len(bp['interactiveQuiz']),12)
        self.assertIn('جلوی اجرای task دلخواه',bp['sections'][9]['html'])
