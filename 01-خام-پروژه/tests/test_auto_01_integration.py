"""Tests only the limited sample parser and temporary file, not live hosts."""
import html
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'academy-labs/agent3/auto_01_lab.py'
spec=importlib.util.spec_from_file_location('auto01',source)
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class LinuxSampleTests(unittest.TestCase):
    def test_sample_and_untrusted_user(self):
        self.assertEqual(lab.parse_failed_ssh_counts(lab.SAMPLE_AUTH_LOG), [('198.51.100.10',3),('203.0.113.77',1)])
        forged='sshd: Failed password for invalid user user from 192.0.2.2 port 100 ssh2 from 203.0.113.5 port 501 ssh2'
        self.assertEqual(lab.parse_failed_ssh_counts(forged), [('203.0.113.5',1)])
        for value in (None, 1, 'Failed password for x from 999.1.1.1 port 1 ssh2', 'Failed password malformed'):
            with self.subTest(value=value), self.assertRaises(ValueError):lab.parse_failed_ssh_counts(value)
        self.assertEqual(lab.parse_failed_ssh_counts('sshd: Accepted publickey for x'),[])

    def test_temp_mode_and_embedded_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=lab.verify_ssh_key_permissions(Path(tmp));self.assertEqual(result['octal_mode'],'0o600')
        bp=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_01.json').read_text())
        self.assertIn(source.read_text(),html.unescape(bp['stages']['lab']['html']))
        self.assertEqual(len(bp['interactiveQuiz']),12)
        self.assertIn('بازبینی مستقل انسانی انجام نشده',bp['reviewStatus'])
