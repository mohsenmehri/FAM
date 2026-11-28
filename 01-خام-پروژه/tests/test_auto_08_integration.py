"""Regression checks for the local teaching model; no real NETCONF device."""
import html
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/auto_08_lab.py'
spec=importlib.util.spec_from_file_location('auto08',source)
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class NetconfIntegrationTests(unittest.TestCase):
    def test_multibyte_chunk_and_invalid_frames(self):
        msg='<rpc><!-- ]]>]]> --><description>سلام</description></rpc>'
        ET.fromstring(msg)
        for size in (1,2,7,50):
            with self.subTest(size=size):
                self.assertEqual(lab.parse_netconf_1_1_chunked(lab.frame_netconf_1_1_chunked(msg,size)),msg)
        for data in (b'\n##\n',b'\n#01\na\n##\n',b'\n#1\na',b'\n#1\na\n##\nextra',b'\n#4294967296\na\n##\n',b'\n#1\n\xff\n##\n'):
            with self.subTest(data=data),self.assertRaises(ValueError):lab.parse_netconf_1_1_chunked(data)

    def test_mock_requires_owner_and_guards_pending_backup(self):
        ds=lab.NetconfDatastoreMock()
        for call in (lambda: ds.edit_candidate(None,['deny']),lambda: ds.commit_confirmed(None),lambda: ds.confirm_commit(None)):
            with self.assertRaises(RuntimeError):call()
        ds.lock('s1');ds.edit_candidate('s1',['deny any']);ds.commit_confirmed('s1')
        with self.assertRaises(RuntimeError):ds.commit_confirmed('s1')
        with self.assertRaises(RuntimeError):ds.confirm_commit('other')
        ds.confirm_timeout_expired();self.assertEqual(ds.running['acl_mgmt'],['permit 10.0.0.0/24'])

    def test_embedded_and_scope(self):
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_08.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertIn('روی تجهیز اجرا نشده',bp['evidence'])
        self.assertIn('قابلیت',bp['interactiveQuiz'][10]['title'])
