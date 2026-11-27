// Exercise the actual bridge and engines in a Node VM, not a browser.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');
const root = path.join(__dirname, '..', 'server');
const page = fs.readFileSync(path.join(root, 'private_ui', 'academy.html'), 'utf8');
const bridgeScript = page.match(/<script id="fam-academy-fam-bridge"[^>]*>([\s\S]*?)<\/script>/)[1];
const engine = fs.readFileSync(path.join(root, 'www', 'academy-assets', 'lesson-engine.js'), 'utf8');
const catalog = fs.readFileSync(path.join(root, 'www', 'academy-assets', 'academy-catalog.js'), 'utf8');
const boot = {csrf: 'test-csrf', userName: 'account-b', progress: {
  'fam4.learn.v1': JSON.stringify({completed: ['remote'], labs: {sections: {remote: ['a']}}})
}};
const storage = new Map([
  ['fam_academy_progress_v1', JSON.stringify(['other-account'])],
  ['fam_academy_sections_v1', JSON.stringify({remote: ['other-account-section']})]
]);
const requests = [];
const status = {textContent: ""};
const ctx = {
  window: {}, document: {documentElement: {dataset: {}}, addEventListener() {}, getElementById(id) {return id === "academy-save-status" ? status : null;}},
  localStorage: {getItem: key => storage.get(key) || null, setItem: (key, value) => storage.set(key, value)},
  fetch: (url, options) => new Promise(resolve => requests.push({url, options, resolve})),
  console, setTimeout, clearTimeout
};
vm.createContext(ctx);
vm.runInContext(bridgeScript.replace('__FAM_ACADEMY_BOOTSTRAP__', JSON.stringify(boot)), ctx);
vm.runInContext(engine, ctx);
vm.runInContext(catalog, ctx);
const {FamLessonEngine: lessons, FamAcademyCatalog: cards} = ctx.window;
const tick = () => new Promise(resolve => setImmediate(resolve));
(async () => {
  assert(lessons.isLessonDone('remote'));
  assert(!lessons.isLessonDone('other-account'));
  assert(!cards.getCompletedSet().has('other-account'));
  assert(lessons.isSectionDone('remote', 'a'));
  assert(!lessons.isSectionDone('remote', 'other-account-section'));

  assert.strictEqual(lessons.toggleLessonDone('remote'), false);
  assert(!lessons.isLessonDone('remote'));
  assert(!cards.getCompletedSet().has('remote'));
  assert.strictEqual(lessons.toggleLessonDone('new'), true);
  assert(lessons.isLessonDone('new'));
  await tick();
  assert.strictEqual(requests.length, 1, 'second write waits for first response');
  assert.strictEqual(requests[0].url, '/api/academy/progress');
  assert.strictEqual(requests[0].options.headers['X-FAM-CSRF'], 'test-csrf');
  const snapshot = req => JSON.parse(JSON.parse(req.options.body).changes['fam4.learn.v1']);
  assert.deepStrictEqual(snapshot(requests[0]).completed, []);
  requests[0].resolve({ok: true});
  await tick();
  assert.strictEqual(requests.length, 2);
  assert.deepStrictEqual(snapshot(requests[1]).completed, ['new']);
  requests[1].resolve({ok: true});
  await tick();
  assert(lessons.isLessonDone('new'), 'an older response must not overwrite the newer state');

  assert.strictEqual(lessons.toggleSectionDone('remote', 'a'), false);
  assert(!lessons.isSectionDone('remote', 'a'));
  await tick();
  assert.deepStrictEqual(snapshot(requests[2]).labs.sections.remote, []);
  requests[2].resolve({ok: false});
  await tick();
  assert(status.textContent.includes('ذخیره نشد')); 
  // Failed requests do not prevent a subsequent snapshot being sent.
  const result = ctx.window.FamAcademyBridge.saveProgress({completed: ['retry'], labs: {}});
  await tick();
  assert.strictEqual(requests.length, 4);
  requests[3].resolve({ok: true});
  assert.strictEqual(await result, true);
  assert.deepStrictEqual(snapshot(requests[3]).completed, ['retry']);
  assert(status.textContent.includes('ذخیره شد'));

  // In-flight requests capture a snapshot, not a mutable nested array.
  assert.strictEqual(lessons.toggleSectionDone('retry', 'x'), true);
  assert.strictEqual(lessons.toggleSectionDone('retry', 'x'), false);
  await tick();
  assert.deepStrictEqual(snapshot(requests[4]).labs.sections.retry, ['x']);
  requests[4].resolve({ok: true});
  await tick();
  assert.deepStrictEqual(snapshot(requests[5]).labs.sections.retry, []);
  requests[5].resolve({ok: true});
  await tick();

  // Without a bridge, standalone callers retain their existing local fallback.
  const offline = {window: {}, document: {addEventListener() {}}, localStorage: ctx.localStorage, console};
  vm.createContext(offline);
  vm.runInContext(engine, offline);
  vm.runInContext(catalog, offline);
  assert(offline.window.FamLessonEngine.isLessonDone('new'));
  assert(offline.window.FamAcademyCatalog.getCompletedSet().has('new'));
  console.log('progress behavior passed');
})().catch(err => {console.error(err); process.exitCode = 1;});
