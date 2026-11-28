"""Real local Git exercise; no remote, device or operating-system sandbox."""
import html
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('auto04', ROOT / 'academy-labs/agent3/auto_04_lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class GitLabTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('git', path=os.defpath), 'Git executable is required')
    def test_real_git_and_inherited_configuration_isolation(self):
        with tempfile.TemporaryDirectory() as outside:
            root=Path(outside); hooks=root/'hooks'; hooks.mkdir(); marker=root/'hook-ran'
            hook=hooks/'post-commit'; hook.write_text(f'#!/bin/sh\ntouch "{marker}"\n'); hook.chmod(0o755)
            (root/'.gitconfig').write_text(f'[core]\n hooksPath = {hooks}\n')
            hostile={'HOME':str(root),'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'core.hooksPath',
                     'GIT_CONFIG_VALUE_0':str(hooks),'GIT_DIR':str(root/'not-a-repository')}
            with patch.dict(os.environ, hostile): result=lab.simulate_safe_git_workflow()
            self.assertFalse(marker.exists())
            self.assertTrue(result['env_ignored_by_gitignore'])
            self.assertEqual(result['commit_count_after_revert'],3)
            self.assertTrue(result['history_preserved_with_revert'])
            self.assertEqual(result['restored_ntp_cfg'],'ntp server 192.0.2.123')

    def test_source_and_catalog_match(self):
        blueprint=json.loads((ROOT/'server/www/academy-assets/v5/blueprints/auto_04.json').read_text())
        self.assertIn((ROOT/'academy-labs/agent3/auto_04_lab.py').read_text(),html.unescape(blueprint['stages']['lab']['html']))
        self.assertIn('بازبینی مستقل انسانی انجام نشده',blueprint['reviewStatus'])
        self.assertIn('Git محلی',blueprint['evidence'])
        catalog=json.loads((ROOT/'server/www/academy-assets/curriculum-catalog.json').read_text())
        self.assertEqual(sum(l['id']=='auto_04' for p in catalog['paths'] for c in p['courses'] for l in c['lessons']),1)
