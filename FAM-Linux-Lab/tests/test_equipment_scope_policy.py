"""C1 authorization regression tests. Only temporary SQLite and mock executors.

Run: PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
Run from FAM-Linux-Lab with the server's Flask dependency installed.
"""
import json
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
import app as server
import equipment_inventory as eq

EMPTY = {k: [] for k in eq.FIELDS}
FULL = {k: ['*'] for k in eq.FIELDS}
LIMITED = {'types': ['type-switch'], 'models': ['model-2960'],
           'regions': ['region-1'], 'siteKinds': ['kind-building'], 'sites': ['building-0']}
SCAN = ['equipment-operations', 'equipment-scan']
ORIGIN = {'Origin': 'https://audit.invalid'}
DEVICE = {'username': 'fixture-user', 'password': 'fixture-password'}


class EquipmentPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fam-c1-')
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / 'fixture.sqlite3')
        self.calls = []
        self.addCleanup(patch.stopall)
        patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')).start()
        patch.object(socket.socket, 'connect_ex', side_effect=AssertionError('network forbidden')).start()
        patch.object(subprocess, 'Popen', side_effect=AssertionError('subprocess forbidden')).start()
        self.config = {'TESTING': True, 'DB_PATH': self.db, 'PUBLIC_ORIGIN': ORIGIN['Origin'],
                       'COOKIE_SECURE': False, 'EQUIPMENT_OPS_ENABLED': True,
                       'EQUIPMENT_EXECUTOR': self.executor}
        self.app = server.create_app(self.config)
        self.salt, self.digest = server.credentials('fixture-password')
        with sqlite3.connect(self.db) as db:
            payload = json.loads(db.execute('SELECT payload FROM equipment_state').fetchone()[0])
            def node(ident, host, region, typ='type-switch', model='model-2960'):
                return {'id': ident, 'name': ident, 'host': host, 'typeId': typ, 'modelId': model,
                        'regionId': region, 'siteKindId': 'kind-building', 'siteId': 'building-0'}
            payload['inventory']['nodes'] = [node('inside', '10.0.0.10', 'region-1'),
                                              node('outside', '10.0.0.12', 'region-2'),
                                              node('router', '10.0.0.13', 'region-1', 'type-router', 'model-1841')]
            db.execute('UPDATE equipment_state SET payload=?', (json.dumps(payload),))

    def executor(self, job):
        self.calls.append(job['operation'])
        if job['operation'] in ('status', 'inspect'):
            return {'ok': True, 'ports': [{'interface': 'Fa0/1', 'description': ''}]}
        if job['operation'] == 'recover':
            return {'ok': True, 'recovery': 'recovered'}
        return {'ok': False, 'error': 'fixture_only'}

    def add_user(self, name, permissions, scope, role=4, categories='[]'):
        with sqlite3.connect(self.db) as db:
            db.execute('INSERT INTO users(id,username,name,role,enabled,regions,sheets,categories,permissions,revision,salt,hash,equipment_scope) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                       (name + '-fixture-id', name, name, role, 1, '[]', '[]',
                        categories, None if permissions is None else json.dumps(permissions),
                        'fixture-revision', self.salt, self.digest,
                        scope if isinstance(scope, str) or scope is None else json.dumps(scope)))

    def login(self, name, password='fixture-password'):
        client = self.app.test_client()
        result = client.post('/api/login', headers=ORIGIN, json={'username': name, 'password': password})
        self.assertEqual(result.status_code, 200, result.get_json())
        return client, {**ORIGIN, 'X-FAM-CSRF': result.json['csrf']}, result.json['user']

    def check(self, client, headers, host):
        return client.post('/api/equipment/check', headers=headers, json={**DEVICE, 'host': host})

    def stored(self, name):
        with sqlite3.connect(self.db) as db:
            return db.execute('SELECT permissions,equipment_scope,revision FROM users WHERE username=?', (name,)).fetchone()

    def test_policy_null_empty_and_explicit(self):
        for role in (1, 2, 3, 4):
            for perms in (None, [], ['manage-users'], ['equipment-operations'], SCAN):
                with self.subTest(role=role, permissions=perms):
                    u = {'role': role}
                    if perms is not None: u['permissions'] = perms
                    permissions, scope = eq.policy(u, None)
                    self.assertEqual(scope, EMPTY)
                    self.assertEqual(permissions, set(perms or []))
                    self.assertFalse(eq.permitted({**u, 'equipmentScope': scope}))
        self.assertEqual(eq.policy({'permissions': SCAN}, LIMITED), (set(SCAN), LIMITED))
        for invalid in ({}, [], False, '', {'types': []}, {**EMPTY, 'types': None}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError): eq.policy({}, invalid)

    def test_each_scope_dimension_is_required_and_combined_with_and(self):
        node = {'typeId': 'type-switch', 'modelId': 'model-2960', 'regionId': 'region-1',
                'siteKindId': 'kind-building', 'siteId': 'building-0'}
        self.assertTrue(eq.node_allowed({'equipmentScope': LIMITED}, node))
        for key, field in eq.FIELDS.items():
            altered = dict(node)
            altered[field] = 'different'
            with self.subTest(dimension=key):
                self.assertFalse(eq.node_allowed({'equipmentScope': LIMITED}, altered))
                partial = dict(LIMITED, **{key: []})
                self.assertFalse(eq.permitted({'permissions': SCAN, 'equipmentScope': partial}))

    def test_sql_and_json_null_deny_even_with_all_explicit_permissions(self):
        for name, raw in [('sqlnull', None), ('jsonnull', 'null')]:
            self.add_user(name, list(eq.OPS), raw)
            c, h, u = self.login(name)
            self.assertEqual(u['equipmentScope'], EMPTY)
            self.assertEqual(c.get('/api/equipment/state').status_code, 403)
            self.assertEqual(self.check(c, h, '10.0.0.10').status_code, 403)
            self.assertEqual(self.check(c, h, '10.0.0.11').status_code, 403)
        self.assertEqual(self.calls, [])

    def test_limited_empty_wildcard_without_permissions_and_router(self):
        cases = [('limited', SCAN, LIMITED, [200, 403, 403, 403]),
                 ('empty', SCAN, EMPTY, [403, 403, 403, 403]),
                 ('noperm', [], FULL, [403, 403, 403, 403]),
                 ('wildcard', SCAN, FULL, [200, 200, 200, 403])]
        for name, perms, scope, expected in cases:
            self.add_user(name, perms, scope)
            c, h, _ = self.login(name)
            actual = [self.check(c, h, host).status_code for host in
                      ('10.0.0.10', '10.0.0.12', '10.0.0.11', '10.0.0.13')]
            self.assertEqual(actual, expected, name)
        self.assertEqual(self.calls, ['status'] * 4)

    def test_manager_without_equipment_can_manage_users_but_not_equipment(self):
        self.add_user('manager', ['manage-users'], FULL)
        c, h, u = self.login('manager')
        self.assertEqual(u['permissions'], ['manage-users'])
        users = c.get('/api/users')
        self.assertEqual(users.status_code, 200)
        self.assertEqual(c.post('/api/users', headers=h, json=users.json).status_code, 200)
        self.assertEqual(c.get('/api/equipment/state').status_code, 403)
        self.assertEqual(self.check(c, h, '10.0.0.11').status_code, 403)
        self.assertEqual(self.calls, [])

    def test_get_post_never_materializes_permissions_or_scope(self):
        self.add_user('nullcustom', ['equipment-operations'], None)
        self.add_user('jsoncustom', ['manage-users'], 'null')
        self.add_user('legacytwo', None, None, role=2, categories=None)
        self.add_user('explicit', SCAN, LIMITED)
        before = {n: self.stored(n) for n in ('nullcustom', 'jsoncustom', 'legacytwo', 'explicit')}
        c, h, _ = self.login('admin', '1109')
        result = c.get('/api/users')
        users = {u['username']: u for u in result.json['users']}
        self.assertEqual(users['nullcustom']['permissions'], ['equipment-operations'])
        self.assertEqual(users['jsoncustom']['permissions'], ['manage-users'])
        self.assertNotIn('permissions', users['legacytwo'])
        self.assertEqual(c.post('/api/users', headers=h, json=result.json).status_code, 200)
        for name, original in before.items(): self.assertEqual(self.stored(name), original, name)

    def test_repair_requires_explicit_permission_and_ticket(self):
        self.add_user('scanonly', SCAN, LIMITED)
        c, h, _ = self.login('scanonly')
        check = self.check(c, h, '10.0.0.10')
        ticket = check.json['recoveryTickets']['Fa0/1']
        response = c.post('/api/equipment/recover', headers=h, json={**DEVICE, 'host': '10.0.0.10', 'interface': 'Fa0/1', 'ticket': ticket})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.calls, ['status'])
        self.add_user('repairer', SCAN + ['equipment-repair'], LIMITED)
        c, h, _ = self.login('repairer')
        ticket = self.check(c, h, '10.0.0.10').json['recoveryTickets']['Fa0/1']
        body = {**DEVICE, 'host': '10.0.0.10', 'interface': 'Fa0/1', 'ticket': ticket}
        self.assertEqual(c.post('/api/equipment/recover', headers=h, json=body).status_code, 200)
        self.assertEqual(c.post('/api/equipment/recover', headers=h, json=body).status_code, 409)
        self.assertEqual(self.calls, ['status', 'status', 'recover'])

    def test_all_equipment_routes_deny_null_before_executor(self):
        self.add_user('nullall', list(eq.OPS), None)
        c, h, _ = self.login('nullall')
        for route in ('check', 'inspect', 'descriptions', 'diagnose', 'recover',
                      'replacement/plan', 'replacement/apply', 'group/plan', 'group/apply'):
            with self.subTest(route=route):
                self.assertEqual(c.post('/api/equipment/' + route, headers=h, json={}).status_code, 403)
        self.assertEqual(c.get('/api/equipment/state').status_code, 403)
        self.assertEqual(self.calls, [])

    def test_target_scope_rechecked_across_operation_routes(self):
        self.add_user('operator', SCAN + ['equipment-repair'], LIMITED)
        c, h, _ = self.login('operator')
        simple = dict(DEVICE)
        diagnosis = {**simple, 'clientIp': '10.0.0.20', 'clientMac': ''}
        replacement = {**simple, 'interface': 'Fa0/1', 'staticIp': False}
        group = {**simple, 'interfaces': ['Fa0/1'], 'mode': 'recover', 'staticIp': False}
        approval = {'ticket': 'x' * 50, 'planHash': 'a' * 64}
        routes = [('check', simple), ('inspect', simple), ('descriptions', simple),
                  ('diagnose', diagnosis), ('recover', {**simple, 'interface': 'Fa0/1', 'ticket': 'x' * 50}),
                  ('replacement/plan', replacement), ('replacement/apply', {**replacement, **approval}),
                  ('group/plan', group), ('group/apply', {**group, **approval})]
        for route, body in routes:
            with self.subTest(route=route):
                before = list(self.calls)
                response = c.post('/api/equipment/' + route, headers=h,
                                  json={**body, 'host': '10.0.0.12'})
                self.assertEqual(response.status_code, 403, response.get_json())
                self.assertEqual(self.calls, before)
        for route, body in routes[:4]:
            with self.subTest(allowed_route=route):
                before = len(self.calls)
                response = c.post('/api/equipment/' + route, headers=h,
                                  json={**body, 'host': '10.0.0.10'})
                # Mock success for check/inspect, deliberately incomplete output for the others.
                self.assertIn(response.status_code, (200, 502))
                self.assertEqual(len(self.calls), before + 1)
        for route, body in (routes[5], routes[7]):
            before = len(self.calls)
            self.assertEqual(c.post('/api/equipment/' + route, headers=h,
                                    json={**body, 'host': '10.0.0.10'}).status_code, 502)
            self.assertEqual(len(self.calls), before + 1)
        for route, body in (routes[6], routes[8]):
            before = len(self.calls)
            self.assertEqual(c.post('/api/equipment/' + route, headers=h,
                                    json={**body, 'host': '10.0.0.10'}).status_code, 409)
            self.assertEqual(len(self.calls), before)

    def test_explicit_scope_and_permissions_can_be_assigned_by_manager(self):
        self.add_user('needscope', SCAN, None)
        self.add_user('manageronly', ['manage-users'], None)
        c, h, _ = self.login('manageronly')
        result = c.get('/api/users')
        self.assertEqual(result.status_code, 200)
        payload = result.json
        user = next(u for u in payload['users'] if u['username'] == 'needscope')
        user['equipmentScope'] = LIMITED
        self.assertEqual(c.post('/api/users', headers=h, json=payload).status_code, 200)
        self.assertEqual(json.loads(self.stored('needscope')[0]), SCAN)
        self.assertEqual(json.loads(self.stored('needscope')[1]), LIMITED)
        target, heads, _ = self.login('needscope')
        self.assertEqual(self.check(target, heads, '10.0.0.10').status_code, 200)
        self.assertEqual(self.check(target, heads, '10.0.0.12').status_code, 403)
        self.assertIsNone(self.stored('manageronly')[1])

    def test_inventory_view_filters_and_missing_scope_cannot_change_cards(self):
        self.add_user('viewer', SCAN, LIMITED)
        c, h, _ = self.login('viewer')
        response = c.get('/api/equipment/state')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([n['host'] for n in response.json['inventory']['nodes']], ['10.0.0.10'])
        self.add_user('noarea', list(eq.OPS), None)
        c, h, _ = self.login('noarea')
        body = {'revision': 0, 'requestId': '00000000-0000-0000-0000-000000000001',
                'kind': 'cards', 'value': {'version': 1, 'cards': []}}
        self.assertEqual(c.post('/api/equipment/state', headers=h, json=body).status_code, 403)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT revision FROM equipment_state').fetchone()[0], 0)

    def test_legacy_roles_have_no_implicit_equipment_permissions(self):
        for role in (1, 2, 3, 4):
            self.add_user('legacy' + str(role), None, FULL, role=role, categories=None)
            c, h, user = self.login('legacy' + str(role))
            self.assertNotIn('permissions', user)
            self.assertEqual(c.get('/api/equipment/state').status_code, 403)
            self.assertEqual(self.check(c, h, '10.0.0.11').status_code, 403)
        self.assertEqual(self.calls, [])

    def test_fresh_bootstrap_is_explicit_and_survives_restart(self):
        permissions, raw_scope, revision = self.stored('admin')
        self.assertEqual(set(json.loads(permissions)), server.PERMISSIONS)
        self.assertEqual(json.loads(raw_scope), FULL)
        c, h, _ = self.login('admin', '1109')
        self.assertEqual(c.get('/api/users').status_code, 200)
        self.assertEqual(self.check(c, h, '10.0.0.11').status_code, 200)
        server.create_app(self.config)
        self.assertEqual(self.stored('admin'), (permissions, raw_scope, revision))

    def test_legacy_schema_migration_null_fails_closed_no_account_rewrite(self):
        self.add_user('oldmanager', None, None, role=1, categories=None)
        before = self.stored('oldmanager')
        with sqlite3.connect(self.db) as db: db.execute('ALTER TABLE users DROP COLUMN equipment_scope')
        migrated = server.create_app(self.config)
        self.assertEqual(self.stored('oldmanager'), before)
        c = migrated.test_client()
        result = c.post('/api/login', headers=ORIGIN, json={'username': 'oldmanager', 'password': 'fixture-password'})
        self.assertEqual(result.status_code, 200)
        h = {**ORIGIN, 'X-FAM-CSRF': result.json['csrf']}
        self.assertEqual(c.get('/api/users').status_code, 200)
        self.assertEqual(c.get('/api/equipment/state').status_code, 403)
        self.assertEqual(self.check(c, h, '10.0.0.11').status_code, 403)

    def test_partial_account_and_invalid_scope_fail_closed(self):
        self.add_user('partial', None, FULL, role=1, categories='[]')
        self.add_user('invalid', SCAN, '{}')
        for name in ('partial', 'invalid'):
            c = self.app.test_client()
            self.assertEqual(c.post('/api/login', headers=ORIGIN, json={'username': name, 'password': 'fixture-password'}).status_code, 500)
        self.assertEqual(self.calls, [])

    def test_disabled_account_and_revision_changes_revoke_session(self):
        for name, update in [('disabled', 'enabled=0'), ('revised', "revision='changed'")]:
            self.add_user(name, SCAN, LIMITED)
            c, h, _ = self.login(name)
            with sqlite3.connect(self.db) as db:
                db.execute('UPDATE users SET ' + update + ' WHERE username=?', (name,))
            self.assertEqual(self.check(c, h, '10.0.0.10').status_code, 401)
        self.assertEqual(self.calls, [])

    def test_invalid_accounts_are_isolated_and_not_rewritten(self):
        self.add_user('broken_scope', SCAN, '{}')
        self.add_user('broken_fields', None, FULL, role=1, categories='[]')
        self.add_user('broken_json', SCAN, None)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE users SET permissions='{' WHERE username='broken_json'")
            before = db.execute("SELECT * FROM users WHERE username LIKE 'broken_%' ORDER BY username").fetchall()
        server.create_app(self.config)
        c, h, _ = self.login('admin', '1109')
        response = c.get('/api/users')
        self.assertEqual(response.status_code, 200)
        payload = response.json
        damaged = [u for u in payload['users'] if u.get('accountInvalid')]
        self.assertEqual({u['username'] for u in damaged}, {'broken_scope', 'broken_fields', 'broken_json'})
        for u in damaged:
            self.assertNotIn('permissions', u)
            badclient = self.app.test_client()
            self.assertEqual(badclient.post('/api/login', headers=ORIGIN, json={'username': u['username'], 'password': 'fixture-password'}).status_code, 500)
        payload['users'].append({'id': 'created-fixture-001', 'username': 'created', 'name': 'created',
                                 'enabled': True, 'regions': [], 'sheets': [], 'categories': [],
                                 'permissions': SCAN, 'equipmentScope': LIMITED, 'password': 'fixture-password'})
        saved = c.post('/api/users', headers=h, json=payload)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        created, heads, _ = self.login('created')
        self.assertEqual(self.check(created, heads, '10.0.0.10').status_code, 200)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(before, db.execute("SELECT * FROM users WHERE username LIKE 'broken_%' ORDER BY username").fetchall())
        payload = c.get('/api/users').json
        payload['users'] = [u for u in payload['users'] if u.get('username') != 'broken_scope']
        self.assertEqual(c.post('/api/users', headers=h, json=payload).status_code, 400)
        payload = c.get('/api/users').json
        target = next(u for u in payload['users'] if u.get('username') == 'broken_scope')
        target.pop('accountInvalid')
        self.assertEqual(c.post('/api/users', headers=h, json=payload).status_code, 400)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(before, db.execute("SELECT * FROM users WHERE username LIKE 'broken_%' ORDER BY username").fetchall())

    def test_unsaveable_accounts_are_isolated_without_rewriting(self):
        for name in ('badrole', 'badcategory', 'badregions', 'badname'):
            self.add_user(name, SCAN, LIMITED)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE users SET role=99,categories=NULL,permissions=NULL WHERE username='badrole'")
            db.execute("UPDATE users SET categories=? WHERE username='badcategory'", (json.dumps(['not valid!']),))
            db.execute("UPDATE users SET regions=? WHERE username='badregions'", (json.dumps(['x' * 101]),))
            db.execute("UPDATE users SET name='' WHERE username='badname'")
            before = db.execute("SELECT * FROM users WHERE username LIKE 'bad%' ORDER BY username").fetchall()
        c, h, _ = self.login('admin', '1109')
        payload = c.get('/api/users').json
        self.assertEqual({u['username'] for u in payload['users'] if u.get('accountInvalid')},
                         {'badrole', 'badcategory', 'badregions', 'badname'})
        admin = next(u for u in payload['users'] if u['username'] == 'admin')
        admin['name'] = 'Healthy manager'
        result = c.post('/api/users', headers=h, json=payload)
        self.assertEqual(result.status_code, 200, result.get_json())
        with sqlite3.connect(self.db) as db:
            self.assertEqual(before, db.execute("SELECT * FROM users WHERE username LIKE 'bad%' ORDER BY username").fetchall())
            self.assertEqual(db.execute("SELECT name FROM users WHERE username='admin'").fetchone()[0], 'Healthy manager')
        for name in ('badrole', 'badcategory', 'badregions', 'badname'):
            bad = self.app.test_client().post('/api/login', headers=ORIGIN, json={'username': name, 'password': 'fixture-password'})
            self.assertEqual(bad.status_code, 500, name)
        self.assertEqual(self.calls, [])

    def test_manager_can_create_edit_and_delete_a_user_without_equipment_access(self):
        self.add_user('manageronly', ['manage-users'], None)
        c, h, _ = self.login('manageronly')
        payload = c.get('/api/users').json
        payload['users'].append({'id':'new-user-fixture-id', 'username':'newuser', 'name':'newuser',
                                 'enabled':True, 'regions':[], 'sheets':[], 'categories':[],
                                 'permissions':SCAN, 'equipmentScope':LIMITED, 'password':'fixture-password'})
        result = c.post('/api/users', headers=h, json=payload)
        self.assertEqual(result.status_code, 200, result.get_json())
        payload = result.json
        newuser = next(u for u in payload['users'] if u.get('username') == 'newuser')
        newuser['name'] = 'new display name'
        result = c.post('/api/users', headers=h, json=payload)
        self.assertEqual(result.status_code, 200, result.get_json())
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT name FROM users WHERE username='newuser'").fetchone()[0], 'new display name')
        payload = result.json
        payload['users'] = [u for u in payload['users'] if u.get('username') != 'newuser']
        self.assertEqual(c.post('/api/users', headers=h, json=payload).status_code, 200)
        with sqlite3.connect(self.db) as db:
            self.assertIsNone(db.execute("SELECT id FROM users WHERE username='newuser'").fetchone())
        self.assertEqual(c.get('/api/equipment/state').status_code, 403)
        self.assertEqual(self.calls, [])

    def test_manager_catalog_supports_scope_edit_without_device_access(self):
        self.add_user('manageronly', ['manage-users'], None)
        self.add_user('targetuser', SCAN, LIMITED)
        c, h, _ = self.login('manageronly')
        result = c.get('/api/users')
        self.assertEqual(result.status_code, 200)
        catalog = result.json['equipmentCatalog']
        self.assertEqual(set(catalog), set(eq.FIELDS))
        self.assertIn('region-2', [x['id'] for x in catalog['regions']])
        serialized = json.dumps(catalog)
        self.assertNotIn('10.0.0.', serialized)
        self.assertNotIn('nodes', catalog)
        self.assertEqual(c.get('/api/equipment/state').status_code, 403)
        self.assertEqual(self.check(c, h, '10.0.0.10').status_code, 403)
        payload = result.json
        user = next(u for u in payload['users'] if u.get('username') == 'targetuser')
        user['equipmentScope']['regions'] = ['region-2']
        saved = c.post('/api/users', headers=h, json=payload)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        target, th, _ = self.login('targetuser')
        self.assertEqual(self.check(target, th, '10.0.0.10').status_code, 403)
        self.assertEqual(self.check(target, th, '10.0.0.12').status_code, 200)
        self.assertEqual(self.calls, ['status'])
        self.assertEqual(target.get('/api/users').status_code, 403)

    def test_unknown_and_duplicate_existing_permissions_preserved(self):
        original = ['equipment-operations', 'future-permission', 'equipment-scan', 'equipment-scan']
        self.add_user('future', original, LIMITED)
        before = self.stored('future')
        c, h, _ = self.login('admin', '1109')
        payload = c.get('/api/users').json
        user = next(u for u in payload['users'] if u.get('username') == 'future')
        self.assertEqual(user['permissions'], original)
        user['permissions'] = list(dict.fromkeys(user['permissions']))
        saved = c.post('/api/users', headers=h, json=payload)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        self.assertEqual(self.stored('future'), before)
        payload = c.get('/api/users').json
        user = next(u for u in payload['users'] if u.get('username') == 'future')
        user['permissions'].append('invented-permission')
        self.assertEqual(c.post('/api/users', headers=h, json=payload).status_code, 400)
        self.assertEqual(self.stored('future'), before)

    def test_invalid_scope_cannot_be_saved_or_grant_access(self):
        self.add_user('targetuser', SCAN, LIMITED)
        c, h, _ = self.login('admin', '1109')
        before = self.stored('targetuser')
        for invalid in (None, {}, [], False, {'types': ['*']}):
            with self.subTest(scope=invalid):
                payload = c.get('/api/users').json
                user = next(u for u in payload['users'] if u.get('username') == 'targetuser')
                user['equipmentScope'] = invalid
                self.assertEqual(c.post('/api/users', headers=h, json=payload).status_code, 400)
                self.assertEqual(self.stored('targetuser'), before)

    def test_csrf_origin_and_scope_change_are_rechecked(self):
        self.add_user('scoped', SCAN, LIMITED)
        c, h, _ = self.login('scoped')
        self.assertEqual(self.check(c, ORIGIN, '10.0.0.10').status_code, 403)
        self.assertEqual(self.check(c, {**h, 'Origin': 'https://bad.invalid'}, '10.0.0.10').status_code, 403)
        with sqlite3.connect(self.db) as db: db.execute("UPDATE users SET equipment_scope=? WHERE username='scoped'", (json.dumps(EMPTY),))
        self.assertEqual(self.check(c, h, '10.0.0.10').status_code, 403)
        self.assertEqual(self.calls, [])


if __name__ == '__main__': unittest.main()
