// jsdom test for client-side educational CLI simulator (online asset + offline HTML).
// This is a jsdom test, not a real browser or live Cisco IOS device test.
const { JSDOM, VirtualConsole } = require('jsdom');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const simSrc = fs.readFileSync(path.resolve(__dirname, '../../server/www/academy-assets/academy-simulator.js'), 'utf8');
const catalog = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../server/www/academy-assets/curriculum-catalog.json'), 'utf8'));
const offlineHtml = fs.readFileSync(path.resolve(__dirname, '../../../FAM-Academy-Offline.html'), 'utf8');

async function testStandaloneSimulator() {
  const dom = new JSDOM('<!doctype html><div id="root"><div data-lesson-quiz></div></div>', {
    url: 'https://fam.test/',
    runScripts: 'dangerously'
  });
  const w = dom.window;
  w.eval(simSrc);
  const api = w.FamAcademySimulator;
  assert.ok(api);
  assert.equal(api.commandCount, 134);
  assert.equal(api.exactScenarioCount, 47);

  // 1. ZERO placeholder responses across all registered CLI commands
  const cmds = api.getSupportedCommands();
  assert.equal(cmds.length, 134);
  for (const cmd of cmds) {
    assert.ok(!/^#/.test(cmd), `comment key leaked into CLI_DB: ${cmd}`);
    const out = String(api.getCommandOutput(cmd) || '');
    assert.ok(!out.includes('خروجی شبیه‌ساز برای'), `placeholder output found for command: ${cmd}`);
    assert.ok(out.trim().length >= 20, `suspiciously short output for command: ${cmd}`);
  }

  // Spot-check formerly placeholder commands now return realistic reference mock outputs
  const checkSession = api.createSession('AUDIT-R1');
  assert.match(checkSession.execute('terraform plan').output, /Plan: 1 to add, 0 to change, 0 to destroy/);
  assert.match(checkSession.execute('show sip-ua calls').output, /SIP UAC|Call-ID|INVITE/i);
  assert.match(checkSession.execute('acidiag fnvread').output, /apic|leaf/i);
  assert.match(checkSession.execute('show vpc').output, /vPC domain/i);
  assert.match(checkSession.execute('show isis segment-routing label-table').output, /SRGB|SID|Label/i);

  // 2. Strict IPv4/IPv6 validation on ping & traceroute (positive + negative)
  for (const okCmd of ['ping 10.1.1.1', 'ping 0.0.0.0', 'ping 255.255.255.255', 'ping 2001:db8::1', 'ping ::1', 'traceroute 10.0.0.1', 'traceroute 2001:db8::1']) {
    const r = checkSession.execute(okCmd);
    assert.equal(r.matched, true, `expected valid IP command to match: ${okCmd}`);
  }
  for (const badCmd of [
    'ping 999.999.999.999',
    'ping 256.1.1.1',
    'ping 01.2.3.4',
    'ping 1.2.3',
    'ping 1.2.3.4.5',
    'ping :::1',
    'ping 2001::db8::1',
    'ping not-an-ip',
    'traceroute 999.0.0.1',
    'traceroute 300.1.2.3',
    'traceroute 2001:::1'
  ]) {
    const r = checkSession.execute(badCmd);
    assert.equal(r.matched, false, `expected invalid IP command to be rejected: ${badCmd}`);
    assert.match(r.output, /آدرس IP نامعتبر/);
  }

  // 3. Exact vs track-default scenario honesty across all 127 catalog lessons
  const allLessons = catalog.paths.flatMap(p => p.courses.flatMap(c => c.lessons));
  assert.equal(allLessons.length, 127);
  let exactCount = 0;
  let trackDefaultCount = 0;
  for (const l of allLessons) {
    const sc = api.scenarioForLesson(l);
    if (sc.matchType === 'exact') exactCount++;
    else if (sc.matchType === 'track-default') trackDefaultCount++;
    else assert.fail(`unexpected matchType ${sc.matchType} for ${l.id}`);
    const s = api.createSession(sc.host);
    for (const c of sc.cmds) {
      const r = s.execute(c);
      assert.equal(r.matched, true, `quick command "${c}" failed on lesson ${l.id}`);
      assert.ok(!String(r.output).includes('خروجی شبیه‌ساز برای'), `placeholder in quick command ${c}`);
    }
  }
  assert.equal(exactCount, 47);
  assert.equal(trackDefaultCount, 80);

  // 4. DOM mount: exact lesson scenario UI + stateful modes including (config-if)#
  const root = w.document.getElementById('root');
  const mounted = api.mount(root, { lessonId: 'adv_bgp', title: 'BGP' });
  assert.ok(mounted);
  const card = root.querySelector('[data-fam-cli-simulator="adv_bgp"]');
  assert.ok(card);
  assert.equal(card.getAttribute('data-sim-match-type'), 'exact');
  assert.match(card.querySelector('h3').textContent, /سناریوی اختصاصی این درس/);
  assert.match(card.querySelector('[data-sim-honesty]').textContent, /شبیه‌ساز آموزشی سمت مرورگر/);
  assert.match(card.querySelector('[data-sim-honesty]').textContent, /هیچ تجهیز واقعی شبکه/);
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'EDGE-BGP1# ');

  // Quick chip click
  const bgpChip = card.querySelector('[data-sim-quick="show ip bgp summary"]');
  assert.ok(bgpChip);
  bgpChip.click();
  assert.match(card.querySelector('[data-sim-output]').textContent, /BGP router identifier/);

  // Stateful mode transitions + hostname + interface mode + switchport voice vlan
  const errVoiceOut = mounted.runCommand('switchport voice vlan 20');
  assert.equal(errVoiceOut.matched, false);
  mounted.runCommand('configure terminal');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'EDGE-BGP1(config)# ');
  mounted.runCommand('hostname CORE-R9');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'CORE-R9(config)# ');
  mounted.runCommand('vlan 50');
  mounted.runCommand('interface GigabitEthernet0/1');
  assert.equal(mounted.runCommand('ip address 10.50.0.1 255.255.255.0').matched, true);
  assert.equal(mounted.runCommand('no shutdown').matched, true);
  assert.equal(mounted.runCommand('switchport access vlan 50').matched, true);
  const doBrief = mounted.runCommand('do show ip interface brief');
  assert.equal(doBrief.matched, true);
  assert.match(doBrief.output, /10\.50\.0\.1/);
  assert.match(mounted.runCommand('do show running-config').output, /hostname CORE-R9/);
  assert.match(mounted.runCommand('do show vlan brief').output, /50\s+VLAN0050/);
  assert.equal(mounted.runCommand('do show ip protocols').matched, true);
  assert.equal(mounted.runCommand('do show ip ospf interface').matched, true);
  assert.equal(mounted.runCommand('do show version').matched, true);
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'CORE-R9(config-if)# ');
  const okVoice = mounted.runCommand('switchport voice vlan 20');
  assert.equal(okVoice.matched, true);
  assert.match(okVoice.output, /Voice VLAN 20/);
  const badVoice = mounted.runCommand('switchport voice vlan 5000');
  assert.equal(badVoice.matched, false);
  mounted.runCommand('exit');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'CORE-R9(config)# ');
  mounted.runCommand('end');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'CORE-R9# ');

  // Safe handling of XSS-like input (plain textContent, never injected as DOM script)
  mounted.runCommand('<script>window.__xss=1</script>');
  assert.equal(w.__xss, undefined);
  assert.equal(card.querySelectorAll('script').length, 0);
  assert.match(card.querySelector('[data-sim-output]').textContent, /پشتیبانی نمی‌شود/);

  // Track-default lesson UI badge check
  api.mount(root, { lessonId: 'ccde_01', title: 'CCDE' });
  const defaultCard = root.querySelector('[data-fam-cli-simulator="ccde_01"]');
  assert.equal(defaultCard.getAttribute('data-sim-match-type'), 'track-default');
  assert.match(defaultCard.querySelector('h3').textContent, /سناریوی پیش‌فرض مسیر/);

  dom.window.close();
}

async function testOfflineSimulatorIntegration() {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(offlineHtml, {
    url: 'https://offline.fam.test/#ccnp_ensdwi',
    runScripts: 'dangerously',
    virtualConsole: vc,
    beforeParse(w) {
      w.Response = global.Response;
      w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} });
      w.fetch = () => { throw new Error('unexpected network fetch'); };
      w.HTMLElement.prototype.scrollIntoView = function() {};
    }
  });
  const w = dom.window;
  for (let i = 0; i < 100; i++) {
    if (w.document.querySelector('[data-fam-cli-simulator="ccnp_ensdwi"]')) break;
    await new Promise(r => setTimeout(r, 20));
  }
  const sim = w.document.querySelector('[data-fam-cli-simulator="ccnp_ensdwi"]');
  assert.ok(sim, 'simulator should mount on ccnp_ensdwi in offline HTML');
  assert.equal(sim.getAttribute('data-sim-match-type'), 'exact');
  sim.querySelector('[data-sim-quick="show sdwan bfd sessions"]').click();
  assert.match(sim.querySelector('[data-sim-output]').textContent, /biz-internet/);
  assert.deepEqual(errors, []);
  dom.window.close();
}

(async () => {
  await testStandaloneSimulator();
  await testOfflineSimulatorIntegration();
  console.log('jsdom simulator: 0 placeholders, strict IPv4/IPv6 validation, (config-if)# mode, 47 exact / 80 track-default & offline HTML passed');
})().catch(e => { console.error(e); process.exitCode = 1; });
