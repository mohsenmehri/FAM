"""Partial candidate regressions only; not acceptance or production validation."""
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/'academy-labs/candidates/agent3'
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'_lab.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
jwt=load('auto_07');netconf=load('auto_08')

class CandidateRegression(unittest.TestCase):
    def test_jwt_malformed_signature_and_duplicate_payload(self):
        token=jwt.build_hs256_jwt({'exp':1893456000},b'test');header,payload,_=token.split('.')
        for sig in ('☃','!!!!','=', ''):
            with self.subTest(sig=sig):
                self.assertFalse(jwt.verify_hs256_jwt(header+'.'+payload+'.'+sig,b'test')['valid'])
        self.assertTrue(jwt.verify_hs256_jwt(token,b'test')['valid'])
        dup=jwt.b64url_encode(b'{"exp":1893456000,"exp":1893456001}')
        self.assertFalse(jwt.verify_hs256_jwt(header+'.'+dup+'.'+token.split('.')[2],b'test')['valid'])

    def test_utf8_split_octets_and_bad_framing(self):
        message='<rpc>سلام</rpc>'
        for size in (1,2,3,8,100):
            with self.subTest(size=size):
                self.assertEqual(netconf.parse_netconf_1_1_chunked(netconf.frame_netconf_1_1_chunked(message,size)),message)
        for data in (b'\n##\n', b'\n#01\na\n##\n',b'\n#1\na', b'\n#1\na\n##\nextra',
                     b'\n#4294967296\na\n##\n',b'\n#1\n\xff\n##\n'):
            with self.subTest(data=data), self.assertRaises(ValueError):netconf.parse_netconf_1_1_chunked(data)

class UpdatedJwtCandidateTests(unittest.TestCase):
    def test_new_candidate_recursion_and_configured_not_performed(self):
        updated=load('auto_07_993')
        token=updated.build_hs256_jwt_demo({'exp':1893456000},b'secret')
        header,_,sig=token.split('.')
        nested=b'{"x":'+b'['*1100+b'0'+b']'*1100+b'}'
        result=updated.evaluate_hs256_jwt_demo(header+'.'+updated.b64url_encode(nested)+'.'+sig,b'secret')
        self.assertFalse(result['demo_checks_passed'])
        self.assertEqual(result['reason'],'malformed_jwt_encoding_or_json')
        self.assertIn('checks_configured',result)
        self.assertNotIn('checks_performed',result)
        self.assertFalse(updated.evaluate_hs256_jwt_demo(header+'.e30.☃',b'secret')['demo_checks_passed'])
