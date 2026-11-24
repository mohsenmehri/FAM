import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const simEngine = require('../server/www/academy-assets/academy-sim-engine.js');

test('arpResolve handles same-subnet ARP broadcast vs off-subnet gateway resolution', () => {
  const sameNet = simEngine.arpResolve({
    sourceIp: '192.168.10.5',
    mask: 24,
    targetIp: '192.168.10.20',
    gatewayIp: '192.168.10.1',
    cacheHit: false,
    vlanId: 10
  });
  assert.equal(sameNet.ok, true);
  assert.match(sameNet.decision, /Local Delivery/);
  assert.equal(sameNet.steps.length, 5);

  const cachedSameNet = simEngine.arpResolve({
    sourceIp: '192.168.10.5',
    mask: 24,
    targetIp: '192.168.10.20',
    gatewayIp: '192.168.10.1',
    cacheHit: true
  });
  assert.equal(cachedSameNet.ok, true);
  assert.equal(cachedSameNet.steps.length, 4);

  const offNet = simEngine.arpResolve({
    sourceIp: '192.168.10.5',
    mask: 24,
    targetIp: '10.20.30.40',
    gatewayIp: '192.168.10.1',
    cacheHit: false
  });
  assert.equal(offNet.ok, true);
  assert.match(offNet.decision, /Gateway/);

  const badIp = simEngine.arpResolve({ sourceIp: '999.1.1.1', mask: 24, targetIp: '192.168.10.2', gatewayIp: '192.168.10.1' });
  assert.equal(badIp.ok, false);
});

test('vlanForward distinguishes same-VLAN L2 forwarding, cross-VLAN drop, and trunk allowed-VLAN rules', () => {
  const crossVlanBlocked = simEngine.vlanForward({
    sourceVlan: 10,
    destinationVlan: 20,
    trunkAllowed: '10,20',
    nativeVlan: 99,
    remoteNativeVlan: 99,
    tagNative: false
  });
  assert.equal(crossVlanBlocked.ok, true);
  assert.match(crossVlanBlocked.decision, /لایه ۳/);

  const trunkAllowed = simEngine.vlanForward({
    sourceVlan: 10,
    destinationVlan: 10,
    trunkAllowed: '10,20',
    nativeVlan: 99,
    remoteNativeVlan: 99,
    tagNative: false
  });
  assert.equal(trunkAllowed.ok, true);
  assert.match(trunkAllowed.decision, /تحویل موفق/);

  const trunkDenied = simEngine.vlanForward({
    sourceVlan: 30,
    destinationVlan: 30,
    trunkAllowed: '10,20',
    nativeVlan: 99,
    remoteNativeVlan: 99,
    tagNative: false
  });
  assert.equal(trunkDenied.ok, true);
  assert.match(trunkDenied.decision, /حذف/);
  assert.match(trunkDenied.summary, /Allowed VLAN/);
});

test('ospfAdjacency verifies timers, area, auth, and MTU for Full vs ExStart vs Init vs 2-Way', () => {
  const full = simEngine.ospfAdjacency({
    areaId: '0',
    remoteAreaId: '0',
    hello: 10,
    dead: 40,
    remoteHello: 10,
    remoteDead: 40,
    mtu: 1500,
    remoteMtu: 1500,
    auth: 'none',
    remoteAuth: 'none'
  });
  assert.equal(full.ok, true);
  assert.equal(full.finalState, 'Full');

  const mtuMismatch = simEngine.ospfAdjacency({
    areaId: '0',
    remoteAreaId: '0',
    hello: 10,
    dead: 40,
    remoteHello: 10,
    remoteDead: 40,
    mtu: 1500,
    remoteMtu: 1400,
    auth: 'none',
    remoteAuth: 'none'
  });
  assert.equal(mtuMismatch.ok, true);
  assert.equal(mtuMismatch.finalState, 'ExStart');

  const timerMismatch = simEngine.ospfAdjacency({
    areaId: '0',
    remoteAreaId: '0',
    hello: 10,
    dead: 40,
    remoteHello: 30,
    remoteDead: 120,
    mtu: 1500,
    remoteMtu: 1500,
    auth: 'none',
    remoteAuth: 'none'
  });
  assert.equal(timerMismatch.ok, true);
  assert.equal(timerMismatch.finalState, 'Init');
});

test('IOS CLI lab engine enforces modes, avoids duplicate VLAN ports, tracks shutdown, and uses dynamic OSPF areas', () => {
  const state = simEngine.createLabState(simEngine.LAB_PRESETS[0]);

  // User mode rejects privileged/global config commands
  const badConf = simEngine.runLabCommand(state, 'configure terminal');
  assert.equal(badConf.matched, false);
  assert.equal(state.mode, 'user');

  simEngine.runLabCommand(state, 'enable');
  assert.equal(state.mode, 'privileged');

  simEngine.runLabCommand(state, 'configure terminal');
  assert.equal(state.mode, 'config');

  simEngine.runLabCommand(state, 'vlan 10');
  assert.equal(state.mode, 'vlan');
  simEngine.runLabCommand(state, 'name Users');
  simEngine.runLabCommand(state, 'exit');
  assert.equal(state.mode, 'config');

  simEngine.runLabCommand(state, 'interface Gi0/1');
  assert.equal(state.mode, 'interface');
  simEngine.runLabCommand(state, 'switchport mode access');
  simEngine.runLabCommand(state, 'switchport access vlan 10');
  // Re-running must not duplicate GigabitEthernet0/1 in VLAN 10
  simEngine.runLabCommand(state, 'switchport access vlan 10');
  assert.deepEqual(state.vlans['10'].ports.filter((p) => p === 'GigabitEthernet0/1'), ['GigabitEthernet0/1']);

  simEngine.runLabCommand(state, 'shutdown');
  assert.equal(state.interfaces['GigabitEthernet0/1'].shutdown, true);
  simEngine.runLabCommand(state, 'end');
  const intBrief = simEngine.runLabCommand(state, 'show ip interface brief');
  assert.ok(intBrief.output.some((line) => line.includes('GigabitEthernet0/1') && line.includes('administratively down')));

  simEngine.runLabCommand(state, 'configure terminal');
  simEngine.runLabCommand(state, 'interface Gi0/1');
  simEngine.runLabCommand(state, 'no shutdown');
  assert.equal(state.interfaces['GigabitEthernet0/1'].shutdown, false);

  simEngine.runLabCommand(state, 'interface Gi0/0');
  simEngine.runLabCommand(state, 'ip address 10.10.10.1 255.255.255.0');
  simEngine.runLabCommand(state, 'no shutdown');

  // Configure non-zero OSPF area (must NOT be rejected or hardcoded to 203.0.113.1)
  simEngine.runLabCommand(state, 'exit');
  simEngine.runLabCommand(state, 'router ospf 1');
  assert.equal(state.mode, 'router');
  const netRes = simEngine.runLabCommand(state, 'network 10.10.10.0 0.0.0.255 area 5');
  assert.equal(netRes.matched, true);
  simEngine.runLabCommand(state, 'passive-interface Gi0/1');
  simEngine.runLabCommand(state, 'end');
  assert.equal(state.mode, 'privileged');

  const ospfNbr = simEngine.runLabCommand(state, 'show ip ospf neighbor');
  assert.ok(ospfNbr.output.some((l) => l.includes('Area 5')));
  assert.ok(!ospfNbr.output.some((l) => l.includes('203.0.113.1')));

  const runCfg = simEngine.runLabCommand(state, 'show running-config').output.join('\n');
  assert.match(runCfg, /passive-interface GigabitEthernet0\/1/);
  assert.match(runCfg, /network 10\.10\.10\.0 0\.0\.0\.255 area 5/);
});

test('academy-sim-ui.js exists and passes syntax checks alongside academy-sim.css', () => {
  const root = path.resolve(__dirname, '..');
  const uiPath = path.join(root, 'server', 'www', 'academy-assets', 'academy-sim-ui.js');
  const cssPath = path.join(root, 'server', 'www', 'academy-assets', 'academy-sim.css');
  assert.equal(fs.existsSync(uiPath), true);
  assert.equal(fs.existsSync(cssPath), true);
  const uiText = fs.readFileSync(uiPath, 'utf8');
  assert.match(uiText, /window\.FamAcademySimUI\s*=\s*\{\s*render\s*\}/);
});
