// jsdom test for client-side educational CLI simulator (online asset + offline HTML).
// This is a jsdom test, not a real browser or live Cisco IOS device test.
const { JSDOM, VirtualConsole } = require('jsdom');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const simSrc = fs.readFileSync(path.resolve(__dirname, '../../server/www/academy-assets/academy-simulator.js'), 'utf8');
const offlineHtml = fs.readFileSync(path.resolve(__dirname, '../../../FAM-Academy-Offline.html'), 'utf8');

async function testStandaloneSimulator() {
  const dom = new JSDOM('<!doctype html><div id="root"><div data-lesson-quiz></div></div>', {
    url: 'https://fam.test/',
    runScripts: 'dangerously'
  });
  const w = dom.window;
  w.eval(simSrc);
  assert.ok(w.FamAcademySimulator);
  assert.ok(w.FamAcademySimulator.commandCount >= 100);

  const root = w.document.getElementById('root');
  const mounted = w.FamAcademySimulator.mount(root, { lessonId: 'adv_bgp', title: 'BGP' });
  assert.ok(mounted);
  const card = root.querySelector('[data-fam-cli-simulator="adv_bgp"]');
  assert.ok(card);
  assert.match(card.querySelector('[data-sim-honesty]').textContent, /شبیه‌ساز آموزشی سمت مرورگر/);
  assert.match(card.querySelector('[data-sim-honesty]').textContent, /هیچ تجهیز واقعی شبکه/);
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'EDGE-BGP1# ');

  // Quick chip click
  const bgpChip = card.querySelector('[data-sim-quick="show ip bgp summary"]');
  assert.ok(bgpChip);
  bgpChip.click();
  assert.match(card.querySelector('[data-sim-output]').textContent, /BGP router identifier/);

  // Stateful mode transitions + hostname
  mounted.runCommand('configure terminal');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'EDGE-BGP1(config)# ');
  mounted.runCommand('hostname CORE-R9');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'CORE-R9(config)# ');
  mounted.runCommand('end');
  assert.equal(card.querySelector('[data-sim-prompt]').textContent, 'CORE-R9# ');

  // Safe handling of XSS-like input (plain textContent, never injected as DOM script)
  mounted.runCommand('<script>window.__xss=1</script>');
  assert.equal(w.__xss, undefined);
  assert.equal(card.querySelectorAll('script').length, 0);
  assert.match(card.querySelector('[data-sim-output]').textContent, /تعریف نشده است/);

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
  sim.querySelector('[data-sim-quick="show sdwan bfd sessions"]').click();
  assert.match(sim.querySelector('[data-sim-output]').textContent, /biz-internet/);
  assert.deepEqual(errors, []);
  dom.window.close();
}

(async () => {
  await testStandaloneSimulator();
  await testOfflineSimulatorIntegration();
  console.log('jsdom simulator: online asset + offline HTML lesson binding, state modes & XSS safety passed');
})().catch(e => { console.error(e); process.exitCode = 1; });
