"""Local crypto demo only, never a production JWT/TLS implementation."""
import html
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/auto_07_lab.py'
spec=importlib.util.spec_from_file_location('auto07',source);lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class JwtDemoTests(unittest.TestCase):
    def test_valid_claims_and_actual_execution_report(self):
        token=lab.build_hs256_jwt_demo({'exp':1893456000,'nbf':1764201500,'iss':'issuer','aud':['api']},b'key')
        ok=lab.evaluate_hs256_jwt_demo(token,b'key',expected_iss='issuer',expected_aud='api')
        self.assertTrue(ok['demo_checks_passed']);self.assertTrue(ok['not_production_jwt_verifier'])
        bad=lab.evaluate_hs256_jwt_demo(token.rsplit('.',1)[0]+'.☃',b'key')
        self.assertFalse(bad['demo_checks_passed']);self.assertIn('signature_base64url',bad['checks_executed'])
        self.assertNotIn('hmac_sha256_bytes_constant_time',bad['checks_executed'])
        self.assertIn('hmac_sha256_bytes_constant_time',bad['checks_configured'])
        self.assertFalse(lab.evaluate_hs256_jwt_demo(token,b'key',expected_aud='other')['demo_checks_passed'])

    def test_malformed_nested_duplicate_and_float_overflow(self):
        token=lab.build_hs256_jwt_demo({'exp':1893456000},b'key');head,_,sig=token.split('.')
        for raw in (b'{"x":'+b'['*1100+b'0'+b']'*1100+b'}',b'{"exp":1,"exp":2}',b'{"exp":1893456000,"x":1e999}'):
            with self.subTest(raw=raw[:40]):
                res=lab.evaluate_hs256_jwt_demo(head+'.'+lab.b64url_encode(raw)+'.'+sig,b'key')
                self.assertFalse(res['demo_checks_passed']);self.assertEqual(res['reason'],'malformed_jwt_encoding_or_json')
        self.assertFalse(lab.verify_san_match('a.b.netops.example',['*.netops.example']))

    def test_embedded_and_early_data_qualification(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_07.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertIn('روی تجهیز اجرا نشده',bp['evidence'])
        self.assertIn('چند stream',bp['interactiveQuiz'][1]['options'][bp['interactiveQuiz'][1]['correctIndex']])
