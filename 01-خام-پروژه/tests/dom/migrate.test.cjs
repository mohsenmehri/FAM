// jsdom, not a real browser or live deployment.
const {JSDOM} = require('jsdom');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const source=fs.readFileSync(path.resolve(__dirname,'../../server/private_ui/academy.html'),'utf8');
const script=source.match(/<script id="fam-academy-fam-bridge"[^>]*>([\s\S]*?)<\/script>/)[1];
const tick=()=>new Promise(resolve=>setImmediate(resolve));

async function testMigrationFlow() {
  const dom=new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-legacy-preview" hidden></button><button id="academy-legacy-migrate" hidden></button><button id="academy-legacy-archive-toggle" hidden></button><section id="academy-legacy-archive-panel" hidden></section>',{url:'https://fam.test/',runScripts:'outside-only'});
  const w=dom.window, requests=[];let confirmed=false;
  w.confirm=()=>confirmed;
  w.fetch=async(url,opts)=>{requests.push({url,opts}); if(url.endsWith('legacy-preview'))return {ok:true,json:async()=>({revision:4,uniqueCompletedCount:4,unmappedCount:1,blockedReason:null,eligible:['s01','s02','adv_bgp'],migrationAvailable:true})}; if(url.endsWith('/migrate'))return {ok:true,json:async()=>({revision:5})};throw Error('unexpected');};
  w.eval(script.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({csrf:'token',progressRevision:4,progress:{'fam4.learn.v1':JSON.stringify({completedLessons:['s01','s02','adv_bgp','unknown_legacy_99']})}})));
  await tick();
  const preview=w.document.getElementById('academy-legacy-preview'),migrate=w.document.getElementById('academy-legacy-migrate');
  const archiveToggle=w.document.getElementById('academy-legacy-archive-toggle');
  assert.equal(preview.hidden,false);
  assert.equal(archiveToggle.hidden,true,'archive viewer must stay hidden before archive exists');
  preview.click();await tick();await tick();
  assert.equal(migrate.hidden,false);
  assert.match(w.document.getElementById('academy-save-status').textContent,/بدون نگاشت: 1/);
  migrate.click();await tick();assert.equal(requests.length,1);
  confirmed=true;migrate.click();await tick();assert.equal(requests.length,2);
  assert.equal(requests[1].opts.headers['X-FAM-CSRF'],'token');
  assert.deepEqual(JSON.parse(requests[1].opts.body),{expectedRevision:4,selectedLessons:['s01','s02','adv_bgp']});
  assert.match(w.document.getElementById('academy-save-status').textContent,/بازخوانی/);
  assert.equal(await w.FamAcademyBridge.saveProgress({completed:[],labs:{}}),false);
  assert.equal(requests.length,2);
  dom.window.close();
}

async function testReadOnlyLegacyArchiveViewer() {
  const legacyArchive = {
    completedLessons: ['s01', 'adv_bgp'],
    examScore: 88,
    quizScores: { s01: 90, adv_bgp: 100 },
    notes: { adv_bgp: 'بررسی Local-Pref و MED\n<img src=x onerror=window.__xss=1>' },
    missions: ['lab-1']
  };
  const dom=new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-legacy-archive-toggle" aria-expanded="false" hidden></button><section id="academy-legacy-archive-panel" hidden></section>',{url:'https://fam.test/',runScripts:'outside-only'});
  const w=dom.window;
  let fetchCalled = false;
  w.fetch = async () => { fetchCalled = true; throw Error('viewer must be strictly read-only'); };
  w.eval(script.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({
    csrf:'token',
    progressRevision:5,
    progress:{
      'fam4.learn.v1': JSON.stringify({completed:['academy-stage-zero-osi-fa','adv_bgp'],labs:{}}),
      'fam.academy.legacy.archive.v1': JSON.stringify(legacyArchive)
    }
  })));
  await tick();
  const toggle=w.document.getElementById('academy-legacy-archive-toggle');
  const panel=w.document.getElementById('academy-legacy-archive-panel');
  assert.equal(toggle.hidden,false,'archive toggle should appear for authenticated user with archive');
  assert.equal(panel.hidden,true);
  toggle.click();
  assert.equal(panel.hidden,false);
  assert.equal(toggle.getAttribute('aria-expanded'),'true');
  assert.match(panel.textContent,/نمایش صرفاً خواندنی آرشیو نسخه قدیمی/);
  assert.match(panel.textContent,/examScore\): 88/);
  assert.match(panel.textContent,/adv_bgp: 100/);
  assert.match(panel.textContent,/بررسی Local-Pref و MED/);
  assert.match(panel.textContent,/<img src=x onerror=window\.__xss=1>/);
  assert.equal(panel.querySelectorAll('img').length,0,'notes must never be parsed as HTML');
  assert.equal(w.__xss,undefined);
  assert.equal(fetchCalled,false,'opening archive viewer must not send any network request');
  toggle.click();
  assert.equal(panel.hidden,true);
  dom.window.close();

  // Malformed archive JSON fails gracefully without throwing
  const domBad=new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-legacy-archive-toggle" hidden></button><section id="academy-legacy-archive-panel" hidden></section>',{url:'https://fam.test/',runScripts:'outside-only'});
  domBad.window.eval(script.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({
    csrf:'token',
    progressRevision:5,
    progress:{'fam4.learn.v1':'{"completed":[],"labs":{}}','fam.academy.legacy.archive.v1':'{broken-json'}
  })));
  await tick();
  domBad.window.document.getElementById('academy-legacy-archive-toggle').click();
  assert.match(domBad.window.document.getElementById('academy-legacy-archive-panel').textContent,/قابل تجزیه نیست/);
  domBad.window.close();
}

async function testEmptyLegacyArchiveUnlockFlow() {
  const dom=new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-legacy-preview" hidden></button><button id="academy-legacy-migrate" hidden></button><button id="academy-legacy-archive-unlock" hidden></button><button id="academy-legacy-reload" hidden></button>',{url:'https://fam.test/',runScripts:'outside-only'});
  const w=dom.window, requests=[]; let confirmed=true;
  w.confirm=()=>confirmed;
  w.fetch=async(url,opts)=>{
    requests.push({url,opts});
    if(url.endsWith('legacy-preview')) return {ok:true,json:async()=>({revision:2,uniqueCompletedCount:0,unmappedCount:0,blockedReason:'no_eligible',eligible:[],migrationAvailable:false})};
    if(url.endsWith('/archive-legacy')) return {ok:true,json:async()=>({ok:true,revision:3,archived:true})};
    throw Error('unexpected '+url);
  };
  w.eval(script.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({csrf:'tok',progressRevision:2,progress:{'fam4.learn.v1':JSON.stringify({completedLessons:[],notes:{}})}})));
  await tick();
  const preview=w.document.getElementById('academy-legacy-preview');
  const migrate=w.document.getElementById('academy-legacy-migrate');
  const unlock=w.document.getElementById('academy-legacy-archive-unlock');
  const reloadBtn=w.document.getElementById('academy-legacy-reload');
  assert.equal(preview.hidden,false);
  preview.click(); await tick(); await tick();
  assert.equal(migrate.hidden,true,'migrate must stay hidden when 0 eligible');
  assert.equal(unlock.hidden,false,'archive-unlock button must appear when 0 eligible');
  unlock.click(); await tick(); await tick();
  assert.equal(requests.length,2);
  assert.equal(requests[1].url,'/api/academy/progress/archive-legacy');
  assert.deepEqual(JSON.parse(requests[1].opts.body),{expectedRevision:2});
  assert.equal(reloadBtn.hidden,false,'reload CTA must appear after archive unlock');
  dom.window.close();
}

async function testResetFreshFlow() {
  const dom=new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-reset-fresh" hidden></button>',{url:'https://fam.test/',runScripts:'outside-only'});
  const w=dom.window, requests=[];
  w.confirm=()=>true;
  w.localStorage.setItem('fam.academy.theme','light');
  w.localStorage.setItem('fam.academy.missions.v1.admin','{"day":"2026-11-28","done":{"study-one":true}}');
  w.localStorage.setItem('fam.academy.timer.v1.admin','{"day":"2026-11-28","minutes":25}');
  w.fetch=async(url,opts)=>{
    requests.push({url,opts});
    if(url.endsWith('/reset-fresh')) return {ok:true,json:async()=>({ok:true,revision:5,reset:true})};
    throw Error('unexpected '+url);
  };
  w.eval(script.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({csrf:'tok',userName:'admin',progressRevision:4,progress:{'fam4.learn.v1':JSON.stringify({completed:['s02'],labs:{}})}})));
  await tick();
  const btn=w.document.getElementById('academy-reset-fresh');
  assert.equal(btn.hidden,false,'reset-fresh button must be visible');
  const ok = await w.FamAcademyBridge.resetFresh({noReload:true});
  assert.equal(ok,true);
  assert.equal(requests.length,1);
  assert.equal(requests[0].url,'/api/academy/progress/reset-fresh');
  assert.deepEqual(JSON.parse(requests[0].opts.body),{expectedRevision:4,confirmReset:true});
  assert.deepEqual(JSON.parse(JSON.stringify(w.FamAcademyBridge.progress)),{completed:[],labs:{}});
  assert.equal(w.localStorage.getItem('fam.academy.missions.v1.admin'),null,'missions must be cleared');
  assert.equal(w.localStorage.getItem('fam.academy.timer.v1.admin'),null,'timer must be cleared');
  assert.equal(w.localStorage.getItem('fam.academy.theme'),'light','theme preference must be preserved');
  dom.window.close();
}

(async()=>{
  await testMigrationFlow();
  await testReadOnlyLegacyArchiveViewer();
  await testEmptyLegacyArchiveUnlockFlow();
  await testResetFreshFlow();
  console.log('jsdom migration + archive-unlock + reset-fresh + read-only legacy archive viewer passed');
})().catch(e=>{console.error(e);process.exitCode=1});
