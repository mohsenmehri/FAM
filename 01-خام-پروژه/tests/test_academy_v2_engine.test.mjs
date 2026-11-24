/* FAM Academy v2 pure-engine and JavaScript syntax contract tests.
 * Run with: node --test tests/test_academy_v2_engine.test.mjs
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const here = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(here, '..');
const assets = join(packageRoot, 'server', 'www', 'academy-assets');
const enginePath = join(assets, 'academy-engine.js');
const appPath = join(assets, 'academy-v2.js');
const engine = require(enginePath);

test('engine exports a pure educational contract', () => {
  assert.equal(engine.OUTPUT_LABEL, 'Sample / Simulated — Internal Simulator');
  assert.deepEqual(engine.ENGINE_FUNCTIONS, ['arpResolve', 'vlanForward', 'ospfAdjacency']);
  for (const name of [...engine.ENGINE_FUNCTIONS, 'evaluateQuiz', 'createLabState', 'runLabCommand', 'sameSubnet', 'ipToInt', 'maskInt', 'macFor', 'normalizeInterface']) {
    assert.equal(typeof engine[name], 'function', name);
  }
  const source = readFileSync(enginePath, 'utf8');
  assert.equal(/\bdocument\b/.test(source), false, 'engine must not depend on DOM');
  assert.equal(/\bfetch\(/.test(source), false, 'engine must not perform network calls');
  assert.equal(/[\u3400-\u9fff]/.test(source), false, 'engine must not contain CJK artifacts');
});

test('JavaScript sources pass node --check', () => {
  for (const file of [enginePath, appPath]) {
    assert.doesNotThrow(() => execFileSync(process.execPath, ['--check', file], { stdio: 'pipe' }), file);
  }
  const appSource = readFileSync(appPath, 'utf8');
  assert.equal(/[\u3400-\u9fff]/.test(appSource), false, 'SPA must not contain CJK artifacts');
  assert.match(appSource, /\/api\/academy\/v2\/catalog/);
  assert.match(appSource, /famAcademyV2\.progress\.v1/);
  assert.match(appSource, /app-shell/);
  assert.match(appSource, /academy-section-head/);
  assert.match(appSource, /fam\.academy\.theme/);
});

test('ARP logic distinguishes local delivery, remote gateway, cache and invalid input', () => {
  const local = engine.arpResolve({ sourceIp: '192.0.2.10', targetIp: '192.0.2.20', mask: 24, gatewayIp: '192.0.2.1', cacheHit: false });
  assert.equal(local.ok, true);
  assert.equal(local.decision, 'Local delivery');
  assert.ok(local.table.some((row) => row.protocol === 'ARP' && row.to === 'Broadcast'));

  const remote = engine.arpResolve({ sourceIp: '192.0.2.10', targetIp: '203.0.113.10', mask: 24, gatewayIp: '192.0.2.1', cacheHit: false });
  assert.equal(remote.decision, 'Remote delivery via gateway');
  assert.equal(remote.params.arpTargetIp, undefined); // the target is encoded in the decision/summary, not a raw field
  assert.match(remote.summary, /Gateway/);
  assert.ok(remote.table.some((row) => row.message.includes('192.0.2.1')));

  const cached = engine.arpResolve({ sourceIp: '192.0.2.10', targetIp: '192.0.2.20', mask: 24, cacheHit: true });
  assert.equal(cached.table.some((row) => row.to === 'Broadcast'), false);
  assert.ok(cached.warnings.some((w) => w.includes('Cache Hit')));

  const invalid = engine.arpResolve({ sourceIp: '999.0.2.10', targetIp: '192.0.2.20', mask: 24 });
  assert.equal(invalid.ok, false);
  assert.match(invalid.error, /octet|IPv4/);
});

test('VLAN/Trunk logic reacts to allowed list, native mismatch and inter-VLAN routing need', () => {
  const delivered = engine.vlanForward({ sourceVlan: 10, destinationVlan: 10, trunkAllowed: '10,20,99', nativeVlan: 99, remoteNativeVlan: 99, tagNative: false });
  assert.equal(delivered.decision, 'Delivered');
  assert.match(delivered.summary, /Tagged/);

  const notAllowed = engine.vlanForward({ sourceVlan: 30, destinationVlan: 30, trunkAllowed: '10,20,99', nativeVlan: 99, remoteNativeVlan: 99 });
  assert.equal(notAllowed.decision, 'Dropped / needs routing');
  assert.match(notAllowed.summary, /Allowed VLAN List/);

  const nativeMismatch = engine.vlanForward({ sourceVlan: 99, destinationVlan: 99, trunkAllowed: '10,20,99', nativeVlan: 99, remoteNativeVlan: 20, tagNative: false });
  assert.equal(nativeMismatch.decision, 'Dropped / needs routing');
  assert.ok(nativeMismatch.warnings.some((w) => w.includes('Native VLAN Mismatch')));

  const differentVlans = engine.vlanForward({ sourceVlan: 10, destinationVlan: 20, trunkAllowed: '10,20,99', nativeVlan: 99, remoteNativeVlan: 99 });
  assert.equal(differentVlans.decision, 'Dropped / needs routing');
  assert.ok(differentVlans.warnings.some((w) => w.includes('Routing') && w.includes('SVI')));
});

test('OSPF adjacency stops at correct state for mismatches and DROther', () => {
  const base = { areaId: '0', remoteAreaId: '0', hello: 10, remoteHello: 10, dead: 40, remoteDead: 40, auth: 'none', remoteAuth: 'none', mtu: 1500, remoteMtu: 1500, networkType: 'broadcast', priority: 1 };
  const full = engine.ospfAdjacency(base);
  assert.equal(full.finalState, 'Full');
  assert.equal(full.steps.length, 7);

  const timerMismatch = engine.ospfAdjacency({ ...base, remoteHello: 20 });
  assert.equal(timerMismatch.finalState, 'Init');
  assert.match(timerMismatch.summary, /Hello Interval/);

  const mtuMismatch = engine.ospfAdjacency({ ...base, remoteMtu: 1400 });
  assert.equal(mtuMismatch.finalState, 'ExStart');
  assert.match(mtuMismatch.summary, /MTU/);

  const drother = engine.ospfAdjacency({ ...base, priority: 0 });
  assert.equal(drother.finalState, '2-Way');
  assert.ok(drother.warnings.some((w) => w.includes('Priority=0')));
});

test('quiz evaluation is deterministic and explains every answer', () => {
  const lesson = {
    id: 'fixture',
    quiz: [
      { id: 'q1', prompt: 'One?', options: ['A', 'B'], answerIndex: 1, explanation: 'B is correct.' },
      { id: 'q2', prompt: 'Two?', options: ['A', 'B', 'C'], answerIndex: 0, explanation: 'A is correct.' },
    ],
  };
  const perfect = engine.evaluateQuiz(lesson, [1, 0]);
  assert.equal(perfect.score, 100);
  assert.equal(perfect.correct, 2);
  assert.equal(perfect.details.length, 2);
  assert.ok(perfect.details.every((d) => d.correct && d.explanation && d.options.length));

  const partial = engine.evaluateQuiz(lesson, [1, null]);
  assert.equal(partial.score, 50);
  assert.equal(partial.correct, 1);
  assert.equal(partial.details[1].correct, false);

  const outOfRange = engine.evaluateQuiz(lesson, [99, 0]);
  assert.equal(outOfRange.score, 50);
});

test('lab simulator tracks IOS-like configuration state without real-device access', () => {
  const state = engine.createLabState({ id: 'lab-vlan-trunk' });
  assert.equal(state.realDeviceConnection, false);
  assert.equal(state.mode, 'user');
  assert.equal(engine.normalizeInterface('gi0/1'), 'GigabitEthernet0/1');

  const commands = [
    'enable', 'configure terminal', 'vlan 10', 'name Users', 'exit',
    'interface gi0/1', 'switchport mode access', 'switchport access vlan 10', 'no shutdown', 'end',
    'show vlan brief', 'show interfaces status',
  ];
  let output = [];
  for (const cmd of commands) {
    const result = engine.runLabCommand(state, cmd);
    assert.equal(result.label, engine.OUTPUT_LABEL);
    assert.equal(result.state, state);
    output = output.concat(result.output);
  }
  assert.equal(state.mode, 'privileged');
  assert.equal(state.vlans[10].name, 'Users');
  assert.ok(state.vlans[10].ports.includes('GigabitEthernet0/1'));
  assert.equal(state.interfaces['GigabitEthernet0/1'].mode, 'access');
  assert.equal(state.interfaces['GigabitEthernet0/1'].vlan, 10);
  assert.equal(state.interfaces['GigabitEthernet0/1'].shutdown, false);
  assert.ok(output.some((line) => line.includes('Users')));
  assert.ok(output.some((line) => line.includes('GigabitEthernet0/1')));

  const unknown = engine.runLabCommand(state, 'reload in 5');
  assert.equal(unknown.matched, false);
  assert.ok(unknown.output.some((line) => line.includes('Invalid input') || line.includes('unsupported')));
  assert.equal(state.realDeviceConnection, false);
});

test('OSPF lab simulator produces expected show-command branches', () => {
  const state = engine.createLabState({ id: 'lab-ospf-single-area' });
  for (const cmd of ['enable', 'configure terminal', 'router ospf 1', 'network 192.0.2.0 0.0.0.3 area 0', 'end']) {
    engine.runLabCommand(state, cmd);
  }
  const neighbor = engine.runLabCommand(state, 'show ip ospf neighbor');
  assert.ok(neighbor.output.some((line) => line.includes('FULL/DR')));
  const route = engine.runLabCommand(state, 'show ip route ospf');
  assert.ok(route.output.some((line) => line.trim().startsWith('O ')));
  assert.equal(state.realDeviceConnection, false);
});
