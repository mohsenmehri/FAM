"""Real ephemeral loopback HTTP lab, not a network controller test."""
import html
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/auto_06_lab.py'
spec=importlib.util.spec_from_file_location('auto06',source)
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class HttpLabTests(unittest.TestCase):
    def test_loopback_crud_and_error_boundaries(self):
        result=lab.run_local_rest_lab()
        self.assertEqual(result,{'bad_post_status':400,'post_status':201,'wrong_path_status':404,
            'bad_type_status':400,'invalid_patch_status':400,'wrong_delete_status':404,
            'duplicate_post_status':409,'patch_status':200,'put_idempotent_same_result':True,
            'delete_status':204,'get_after_delete_status':404})

    def test_embedded_and_scope(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_06.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertEqual(len(bp['interactiveQuiz']),12)
        self.assertIn('روی تجهیز اجرا نشده',bp['evidence'])
        self.assertIn('deadline کل',bp['interactiveQuiz'][5]['explanationHtml'])
