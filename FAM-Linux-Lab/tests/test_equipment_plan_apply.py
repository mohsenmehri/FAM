"""Isolated plan/apply API tests: temporary SQLite, mocked executor, no SSH."""
import copy
import json
import sqlite3
import unittest
from unittest.mock import patch

import test_equipment_scope_policy as fixture
import equipment_ops
import equipment_probe as probe
import equipment_replacement as replacement
import equipment_group as group


class PlanApplyTests(unittest.TestCase):
    setUp = fixture.EquipmentPolicyTests.setUp
    add_user = fixture.EquipmentPolicyTests.add_user
    login = fixture.EquipmentPolicyTests.login

    def executor(self, job):
        self.calls.append(job['operation'])
        return copy.deepcopy(self.outputs.get(job['operation'], {'ok': False, 'error': 'fixture_only'}))

    def prepare(self, scope=fixture.LIMITED, perms=None):
        self.outputs = {}
        self.add_user('operator', perms if perms is not None else fixture.SCAN + ['equipment-repair'], scope)
        return self.login('operator')[:2]

    def scenario(self, kind='replacement', mode='recover', static=False, host='10.0.0.10'):
        base = {**fixture.DEVICE, 'host': host}
        old, new, fingerprint = '0011.2233.4455', '00aa.bbcc.ddee', 'a' * 64
        ip = '10.0.0.55' if static else ''
        if kind == 'replacement':
            body = {**base, 'interface': 'Fa0/1', 'staticIp': static}
            plan = {'interface': 'Fa0/1', 'staticIp': static, 'ip': ip, 'oldMac': old,
                    'planHash': fingerprint, 'vlan': 100, 'acl': 'Inspection' if static else ''}
            success = {'ok': True, 'replacement': 'replaced', 'interface': 'Fa0/1',
                       'staticIp': static, 'ip': ip, 'oldMac': old, 'newMac': new, 'protectionRestored': True}
        else:
            ports = ['Fa0/1', 'Fa0/2']
            body = {**base, 'interfaces': ports, 'mode': mode, 'staticIp': static}
            items = [{'interface': port, 'ip': ('10.0.0.' + str(55+i)) if static else '',
                      'oldMac': '0011.2233.44' + str(55+i), 'expectedMac': ''}
                     for i, port in enumerate(ports)]
            plan = {'mode': mode, 'interfaces': ports, 'staticIp': static, 'items': items,
                    'removals': [], 'planHash': fingerprint, 'relocationPolicy': 'idle-access-vlan100'}
            rows = [{**item, 'newMac': ('00aa.bbcc.dd' + str(55+i)) if mode == 'replace' else '',
                     'state': 'replaced' if mode == 'replace' else 'recovered'} for i, item in enumerate(items)]
            success = {'ok': True, 'mode': mode, 'interfaces': ports, 'rows': rows,
                       'protectionRestored': True, 'removed': []}
        self.outputs[kind + '-plan'] = {'ok': True, 'plan': plan}
        self.outputs[kind + '-apply'] = success
        return body, plan, success

    def post(self, client, headers, kind, stage, body):
        return client.post('/api/equipment/' + kind + '/' + stage, headers=headers, json=body)

    def approval(self, client, headers, kind, body):
        response = self.post(client, headers, kind, 'plan', body)
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.json['plan'], self.outputs[kind + '-plan']['plan'])
        return {**body, 'ticket': response.json['ticket'], 'planHash': response.json['plan']['planHash']}

    def test_success_and_one_time_ticket_all_modes(self):
        c, h = self.prepare()
        for kind, mode, static in (('replacement', '', False), ('replacement', '', True),
                                   ('group', 'recover', False), ('group', 'replace', False),
                                   ('group', 'replace', True)):
            with self.subTest(kind=kind, mode=mode, static=static):
                body, _, success = self.scenario(kind, mode, static)
                apply = self.approval(c, h, kind, body)
                before = len(self.calls)
                result = self.post(c, h, kind, 'apply', apply)
                self.assertEqual(result.status_code, 200, result.get_json())
                self.assertEqual(result.json['host'], body['host'])
                for key, value in success.items():
                    if key != 'ok': self.assertEqual(result.json[key], value)
                replay = self.post(c, h, kind, 'apply', apply)
                self.assertEqual(replay.status_code, 409)
                self.assertEqual(replay.json['code'], 'ticket_consumed')
                self.assertEqual(self.calls[before:], [kind + '-apply'])

    def test_authorization_and_scope_denied_before_executor(self):
        self.outputs = {}
        for name, perms, scope in (('noscan', ['equipment-operations','equipment-repair'], fixture.LIMITED),
                                   ('norepair', fixture.SCAN, fixture.LIMITED),
                                   ('empty', fixture.SCAN + ['equipment-repair'], fixture.EMPTY),
                                   ('nullscope', fixture.SCAN + ['equipment-repair'], None)):
            self.add_user(name, perms, scope)
            c, h, _ = self.login(name)
            for kind in ('replacement', 'group'):
                body, _, _ = self.scenario(kind)
                for stage in ('plan', 'apply'):
                    data = body if stage == 'plan' else {**body, 'planHash': 'a'*64, 'ticket': 'x'*60}
                    with self.subTest(user=name, kind=kind, stage=stage):
                        self.assertEqual(self.post(c,h,kind,stage,data).status_code, 403)
        self.add_user('limited', fixture.SCAN + ['equipment-repair'], fixture.LIMITED)
        c, h, _ = self.login('limited')
        for host in ('10.0.0.12', '10.0.0.11', '10.0.0.13'):
            for kind in ('replacement','group'):
                body, _, _ = self.scenario(kind, host=host)
                for stage in ('plan','apply'):
                    data = body if stage == 'plan' else {**body, 'planHash':'a'*64, 'ticket':'x'*60}
                    with self.subTest(host=host, kind=kind, stage=stage):
                        self.assertEqual(self.post(c,h,kind,stage,data).status_code, 403)
        self.assertEqual(self.calls, [])

    def test_unknown_destination_requires_explicit_full_wildcard(self):
        c, h = self.prepare(fixture.FULL)
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind, host='10.0.0.11')
            apply = self.approval(c, h, kind, body)
            self.assertEqual(self.post(c,h,kind,'apply',apply).status_code, 200)
        self.assertEqual(self.calls, ['replacement-plan','replacement-apply','group-plan','group-apply'])

    def test_scope_changed_after_plan_denies_apply(self):
        c, h = self.prepare()
        approvals = []
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind)
            approvals.append((kind, self.approval(c,h,kind,body)))
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE users SET equipment_scope=? WHERE username='operator'", (json.dumps(fixture.EMPTY),))
        for kind, apply in approvals:
            self.assertEqual(self.post(c,h,kind,'apply',apply).status_code, 403)
        self.assertEqual(self.calls, ['replacement-plan','group-plan'])

    def test_permissions_revoked_after_plan_deny_apply(self):
        c,h = self.prepare()
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind)
            for remaining in (['equipment-operations','equipment-repair'], fixture.SCAN):
                with self.subTest(kind=kind, remaining=remaining):
                    with sqlite3.connect(self.db) as db:
                        db.execute("UPDATE users SET permissions=? WHERE username='operator'", (json.dumps(fixture.SCAN + ['equipment-repair']),))
                    approval = self.approval(c,h,kind,body)
                    before = len(self.calls)
                    with sqlite3.connect(self.db) as db:
                        db.execute("UPDATE users SET permissions=? WHERE username='operator'", (json.dumps(remaining),))
                    self.assertEqual(self.post(c,h,kind,'apply',approval).status_code,403)
                    self.assertEqual(len(self.calls),before)
            with sqlite3.connect(self.db) as db:
                db.execute("UPDATE users SET permissions=? WHERE username='operator'", (json.dumps(fixture.SCAN + ['equipment-repair']),))

    def test_ticket_is_bound_to_host_even_with_full_scope(self):
        c,h = self.prepare(fixture.FULL)
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind)
            approval = self.approval(c,h,kind,body)
            before = len(self.calls)
            self.assertEqual(self.post(c,h,kind,'apply',{**approval,'host':'10.0.0.11'}).status_code,409)
            self.assertEqual(len(self.calls),before)
            self.assertEqual(self.post(c,h,kind,'apply',approval).status_code,200)

    def test_group_recover_reports_still_errdisabled_without_relabeling(self):
        c,h = self.prepare()
        body, _, success = self.scenario('group', 'recover', False)
        approval = self.approval(c,h,'group',body)
        success['rows'][1]['state'] = 'still_errdisabled'
        self.outputs['group-apply'] = success
        response = self.post(c,h,'group','apply',approval)
        self.assertEqual(response.status_code,200)
        self.assertEqual([row['state'] for row in response.json['rows']],['recovered','still_errdisabled'])

    def test_input_validation_rejects_before_executor(self):
        c, h = self.prepare()
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind)
            invalid = [{**body, 'host':'8.8.8.8'}, {**body, 'username':'-bad'},
                       {**body, 'staticIp':'false'}, {**body, 'command':'show version'}]
            invalid += ([{**body,'interface':'Fa0/25'}, {**body,'interface':'Fa0/1;reload'}]
                        if kind == 'replacement' else
                        [{**body,'interfaces':['Fa0/1','Fa0/1']}, {**body,'mode':'recover','staticIp':True}])
            for item in invalid:
                with self.subTest(kind=kind, item=item):
                    self.assertEqual(self.post(c,h,kind,'plan',item).status_code,400)
            for addition in ({'ticket':'x'*60,'planHash':'not-a-hash'}, {'ticket':'bad','planHash':'a'*64}):
                self.assertEqual(self.post(c,h,kind,'apply',{**body,**addition}).status_code,400)
        self.assertEqual(self.calls, [])

    def test_ticket_binding_expiry_and_forgery(self):
        c, h = self.prepare()
        self.add_user('other', fixture.SCAN + ['equipment-repair'], fixture.LIMITED)
        other, other_h, _ = self.login('other')
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind)
            approval = self.approval(c,h,kind,body)
            before = len(self.calls)
            changes = [{'planHash':'b'*64}, {'username':'another-user'}, {'ticket':'x'*60}]
            changes += ([{'interface':'Fa0/2'}, {'staticIp':True}] if kind == 'replacement'
                        else [{'interfaces':['Fa0/1']}, {'mode':'replace'}])
            for change in changes:
                self.assertEqual(self.post(c,h,kind,'apply',{**approval,**change}).status_code,409)
            self.assertEqual(self.post(other,other_h,kind,'apply',approval).status_code,409)
            with patch.object(equipment_ops.time, 'time', return_value=equipment_ops.time.time()+301):
                self.assertEqual(self.post(c,h,kind,'apply',approval).status_code,409)
            self.assertEqual(len(self.calls), before)
            self.assertEqual(self.post(c,h,kind,'apply',approval).status_code,200)

    def test_preflight_rejects_bad_results_and_executor_error(self):
        c,h = self.prepare()
        for kind in ('replacement','group'):
            body, plan, _ = self.scenario(kind)
            for result in ({'ok':False,'error':'connection_failed'}, None, {'ok':True,'plan':{}},
                           {'ok':True,'plan':{**plan, 'planHash':'invalid'}},
                           {'ok':True,'plan':{**plan, 'staticIp':True}}):
                self.outputs[kind+'-plan'] = result
                response = self.post(c,h,kind,'plan',body)
                self.assertEqual(response.status_code,502, (kind,result,response.get_json()))
                self.assertNotIn('ticket',response.get_json())
            self.outputs[kind+'-plan'] = {'ok':False,'error':'equipment_busy'}
            self.assertEqual(self.post(c,h,kind,'plan',body).status_code,429)

    def test_uncertain_changed_busy_and_malformed_apply_never_report_success(self):
        c,h = self.prepare()
        for kind in ('replacement','group'):
            for outcome, expected, code in [({'ok':False,'error':'connection_failed'},502,kind+'_uncertain'),
                                             (None,502,kind+'_uncertain'),
                                             ({'ok':False,'error':kind+'_changed'},502,kind+'_changed'),
                                             ({'ok':False,'error':'equipment_busy'},429,'equipment_busy'),
                                             ({'ok':True},502,kind+'_uncertain')]:
                with self.subTest(kind=kind,outcome=outcome):
                    body, _, _ = self.scenario(kind)
                    apply = self.approval(c,h,kind,body)
                    self.outputs[kind+'-apply'] = outcome
                    response = self.post(c,h,kind,'apply',apply)
                    self.assertEqual(response.status_code,expected,response.get_json())
                    self.assertEqual(response.json['code'],code)
                    self.assertTrue(response.json['requiresRecheck'])
                    self.assertEqual(self.post(c,h,kind,'apply',apply).status_code,409)

    def test_guard_busy_blocks_executor_and_preserves_ticket(self):
        c,h = self.prepare()
        for kind in ('replacement','group'):
            body, _, _ = self.scenario(kind)
            approval = self.approval(c,h,kind,body)
            before = len(self.calls)
            with self.app.extensions['equipment_guard'].admit(body['host']):
                self.assertEqual(self.post(c,h,kind,'apply',approval).status_code,429)
            self.assertEqual(len(self.calls),before)
            self.assertEqual(self.post(c,h,kind,'apply',approval).status_code,200)

    def test_malformed_group_apply_output_is_uncertain(self):
        c,h = self.prepare()
        for case in ('wrong_port', 'wrong_mode', 'duplicate_mac', 'invalid_removal', 'not_protected'):
            with self.subTest(case=case):
                body, _, success = self.scenario('group', 'replace', False)
                approval = self.approval(c,h,'group',body)
                if case == 'wrong_port': success['rows'][0]['interface'] = 'Fa0/3'
                if case == 'wrong_mode': success['mode'] = 'recover'
                if case == 'duplicate_mac': success['rows'][1]['newMac'] = success['rows'][0]['newMac']
                if case == 'invalid_removal': success['removed'] = [{'interface':'Fa0/3','mac':'00aa.bbcc.dd99','kind':'securedynamic','vlan':100,'reason':'old_port_conflict'}]
                if case == 'not_protected': success['protectionRestored'] = False
                self.outputs['group-apply'] = success
                result = self.post(c,h,'group','apply',approval)
                self.assertEqual(result.status_code,502)
                self.assertEqual(result.json['code'],'group_uncertain')
                self.assertTrue(result.json['requiresRecheck'])

    def test_replacement_empty_old_mac_is_allowed(self):
        c,h = self.prepare()
        body, plan, success = self.scenario('replacement')
        plan['oldMac'] = ''
        success['oldMac'] = ''
        approval = self.approval(c,h,'replacement',body)
        result = self.post(c,h,'replacement','apply',approval)
        self.assertEqual(result.status_code,200,result.get_json())
        self.assertEqual(result.json['oldMac'],'')

    def test_helper_stale_preflight_stops_before_write_without_ssh(self):
        # Test helper branching with synthetic snapshots and transport patched out.
        seen = []
        def fake_session(job, commands, *args, **kwargs):
            seen.append(commands)
            if any(command == 'configure terminal' for command in commands):
                raise AssertionError('write must not execute')
            return 'synthetic read-only output'
        common = [patch.object(probe,'runtime_directory',return_value='fixture-only'),
                  patch.object(probe,'prepare_askpass',return_value='fixture-only'),
                  patch.object(probe,'_cleanup_runtime'),
                  patch.object(probe,'session_output',side_effect=fake_session),
                  patch.object(replacement.d,'profile',return_value=None)]
        from contextlib import ExitStack
        with ExitStack() as stack:
            for item in common: stack.enter_context(item)
            stack.enter_context(patch.object(replacement,'snapshot',return_value={'fixture':True}))
            plan = {'interface':'Fa0/1','staticIp':False,'ip':'','oldMac':'0011.2233.4455',
                    'planHash':'a'*64,'vlan':100,'acl':''}
            stack.enter_context(patch.object(replacement,'plan_from',return_value=plan))
            job = {'interface':'Fa0/1','staticIp':False,'planHash':'b'*64}
            with self.assertRaises(probe.ProbeError) as error:
                replacement.run(job,apply=True)
            self.assertEqual(error.exception.code,'replacement_changed')
        self.assertEqual(len(seen),2)
        seen.clear()
        snapshot = {'items':{'Fa0/1':{}}, 'secure':[], 'bindings':[], 'acl':[], 'states':{'Fa0/1':'err-disabled'}}
        item = {'interface':'Fa0/1','ip':'','oldMac':'','expectedMac':''}
        with ExitStack() as stack:
            for item_patch in (patch.object(probe,'runtime_directory',return_value='fixture-only'),
                               patch.object(probe,'prepare_askpass',return_value='fixture-only'),
                               patch.object(probe,'_cleanup_runtime'),
                               patch.object(probe,'session_output',side_effect=fake_session),
                               patch.object(group.d,'profile',return_value=None),
                               patch.object(group,'snapshot',return_value=snapshot),
                               patch.object(group,'cleanup_rows',return_value=([item],[]))):
                stack.enter_context(item_patch)
            job = {'interfaces':['Fa0/1'],'mode':'recover','staticIp':False,'planHash':'b'*64}
            with self.assertRaises(probe.ProbeError) as error:
                group.run(job,apply=True)
            self.assertEqual(error.exception.code,'group_changed')
        self.assertEqual(len(seen),2)

    def test_replacement_bad_mac_in_plan_is_not_success(self):
        c,h = self.prepare()
        for bad in (None, [], 0):
            with self.subTest(oldMac=bad):
                body, _, _ = self.scenario('replacement')
                self.outputs['replacement-plan']['plan']['oldMac'] = bad
                result = self.post(c,h,'replacement','plan',body)
                self.assertEqual(result.status_code,502)
                self.assertNotIn('ticket',result.get_json())

    def test_replacement_bad_mac_in_result_is_not_success(self):
        c,h = self.prepare()
        for bad in (None, [], 0, '0011.2233.4455'):
            with self.subTest(bad=bad):
                body, _, success = self.scenario('replacement')
                approval = self.approval(c,h,'replacement',body)
                if bad == '0011.2233.4455': success['newMac'] = bad
                else: success['oldMac'] = bad
                self.outputs['replacement-apply'] = success
                result = self.post(c,h,'replacement','apply',approval)
                self.assertEqual(result.status_code,502)
                self.assertEqual(result.json['code'],'replacement_uncertain')
                self.assertTrue(result.json['requiresRecheck'])


if __name__ == '__main__': unittest.main()
