"""Optional local-only Chromium test; skipped unless browser paths are configured.

Requires FAM_BROWSER_EXECUTABLE and FAM_PLAYWRIGHT_MODULE (playwright-core),
plus node and Flask. No service or database outside the temporary fixture is used.
"""
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
import app as server
import equipment_ops
from werkzeug.serving import make_server


@unittest.skipUnless(os.environ.get('FAM_BROWSER_EXECUTABLE') and os.environ.get('FAM_PLAYWRIGHT_MODULE'),
                     'set FAM_BROWSER_EXECUTABLE and FAM_PLAYWRIGHT_MODULE for the browser test')
class EquipmentScopeBrowserTests(unittest.TestCase):
    def test_manager_can_edit_scope_without_equipment_access(self):
        with tempfile.TemporaryDirectory(prefix='fam-browser-fixture-') as tmp:
            dbpath = str(Path(tmp) / 'fixture.sqlite3')
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            origin = 'http://127.0.0.1:' + str(port)
            def forbidden(job): raise AssertionError('fixture executor must not run')
            app = server.create_app({'TESTING': True, 'DB_PATH': dbpath, 'PUBLIC_ORIGIN': origin,
                'COOKIE_SECURE': False, 'EQUIPMENT_OPS_ENABLED': True, 'EQUIPMENT_EXECUTOR': forbidden})
            salt, digest = server.credentials('fixture-password')
            limited = {'types':['type-switch'], 'models':['model-2960'], 'regions':['region-1'],
                       'siteKinds':['kind-building'], 'sites':['building-0']}
            with sqlite3.connect(dbpath) as db:
                for name, permissions, scope in (
                    ('manager', ['manage-users'], None),
                    ('target', ['equipment-operations','equipment-scan','future-permission'], json.dumps(limited)),
                    ('broken', ['equipment-operations'], '{}')):
                    db.execute('INSERT INTO users(id,username,name,role,enabled,regions,sheets,categories,permissions,revision,salt,hash,equipment_scope) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (name+'-fixture-id',name,name,4,1,'[]','[]','[]',json.dumps(permissions),'fixture-revision',salt,digest,scope))
            with sqlite3.connect(dbpath) as db:
                db.execute('INSERT INTO users(id,username,name,role,enabled,regions,sheets,categories,permissions,revision,salt,hash,equipment_scope) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           ('legacy-fixture-id','legacy','legacy',2,1,'[]','[]',None,None,'fixture-revision',salt,digest,None))
            client = app.test_client()
            login = client.post('/api/login', headers={'Origin': origin},
                                json={'username':'manager', 'password':'fixture-password'})
            self.assertEqual(login.status_code, 200)
            environment = {**os.environ, 'FAM_FIXTURE_ORIGIN':origin,
                           'FAM_FIXTURE_COOKIE':client.get_cookie('fam_session').value}
            with patch.object(equipment_ops, '_execute', side_effect=AssertionError('executor forbidden')) as execute:
                http = make_server('127.0.0.1', port, app)
                thread = threading.Thread(target=http.serve_forever, daemon=True)
                thread.start()
                try:
                    subprocess.run(['node', str(Path(__file__).with_name('equipment_scope_browser.js'))],
                                   env=environment, timeout=90, check=True)
                finally:
                    http.shutdown()
                    thread.join()
                    http.server_close()
                execute.assert_not_called()
            with sqlite3.connect(dbpath) as db:
                permissions, scope = db.execute("SELECT permissions,equipment_scope FROM users WHERE username='target'").fetchone()
                self.assertEqual(json.loads(permissions), ['equipment-operations','equipment-scan','future-permission'])
                self.assertEqual(json.loads(scope)['regions'], ['region-2'])
                self.assertTrue(all('*' not in v for v in json.loads(scope).values()))
                self.assertEqual(db.execute("SELECT equipment_scope FROM users WHERE username='broken'").fetchone()[0], '{}')
                self.assertIsNone(db.execute("SELECT equipment_scope FROM users WHERE username='manager'").fetchone()[0])
                legacy_permissions, legacy_scope = db.execute("SELECT permissions,equipment_scope FROM users WHERE username='legacy'").fetchone()
                self.assertTrue(all(not p.startswith('equipment-') for p in json.loads(legacy_permissions)))
                self.assertIsNone(legacy_scope)
