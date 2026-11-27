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
const storageReads = [];
const storageWrites = [];
const status = {textContent: ""};
const ctx = {
  window: {}, document: {documentElement: {dataset: {}}, addEventListener() {}, getElementById(id) {return id === "academy-save-status" ? status : null;}},
  localStorage: {getItem: key => {storageReads.push(key); return storage.get(key) || null;}, setItem: (key, value) => {storageWrites.push(key); storage.set(key, value);}},
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

  // The account session did not read, overwrite or clear standalone progress,
  // including after a failed server save; sign-out leaves those keys intact.
  const sharedKeys = ['fam_academy_progress_v1', 'fam_academy_sections_v1', 'fam_academy_quiz_v1'];
  assert(!storageReads.some(key => sharedKeys.includes(key)));
  assert(!storageWrites.some(key => sharedKeys.includes(key)));
  // Without a bridge, standalone callers retain their existing local fallback.
  const offline = {window: {}, document: {addEventListener() {}}, localStorage: ctx.localStorage, console};
  vm.createContext(offline);
  vm.runInContext(engine, offline);
  vm.runInContext(catalog, offline);
  assert(offline.window.FamLessonEngine.isLessonDone('other-account'));
  assert(!offline.window.FamLessonEngine.isLessonDone('new'));
  assert(offline.window.FamAcademyCatalog.getCompletedSet().has('other-account'));
  assert(offline.window.FamLessonEngine.isSectionDone('remote', 'other-account-section'));
  assert(!offline.window.FamLessonEngine.isSectionDone('retry', 'x'));
  offline.window.FamLessonEngine.toggleLessonDone('standalone');
  assert(offline.window.FamAcademyCatalog.getCompletedSet().has('standalone'));
  assert(!lessons.isLessonDone('standalone'));
  // Historic, mixed and malformed values must not be overwritten. No automatic
  // ownership claim or conversion is made: recovery needs an explicit policy.
  const legacyValues = [
    JSON.stringify({completedLessons: ['s01'], quizScores: {s01: 100}, notes: {s01:'private'}}),
    JSON.stringify({completed:['new'], completedLessons:['s01']}),
    '{bad json', JSON.stringify({}), JSON.stringify(null)
  ];
  for (const value of legacyValues) {
    const savedStatus = {textContent: ''}; const sent = []; const handlers = {};
    const isolated = {window:{}, document:{documentElement:{dataset:{}},
      addEventListener(name, cb){handlers[name]=cb;}, getElementById(){return savedStatus;}},
      localStorage:ctx.localStorage, fetch(...args){sent.push(args);return Promise.resolve({ok:true});}, console};
    vm.createContext(isolated);
    const legacyBoot = {csrf:'token', progress:{'fam4.learn.v1':value}};
    vm.runInContext(bridgeScript.replace('__FAM_ACADEMY_BOOTSTRAP__', JSON.stringify(legacyBoot)), isolated);
    assert.strictEqual(isolated.window.FamAcademyBridge.sharedProgressLocked, true);
    handlers.DOMContentLoaded();
    assert.match(savedStatus.textContent, /ذخیره غیرفعال است/);
    assert.strictEqual(await isolated.window.FamAcademyBridge.saveProgress({completed:['s02'],labs:{}}), false);
    assert.strictEqual(sent.length, 0, 'must not overwrite historical or unknown data');
    assert.strictEqual(legacyBoot.progress['fam4.learn.v1'], value);
  }
  console.log('progress behavior passed');
})().catch(err => {console.error(err); process.exitCode = 1;});
