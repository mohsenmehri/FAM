// jsdom bridge test, not a browser or production network test.
const {JSDOM} = require('jsdom');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.resolve(__dirname,'../../server/private_ui/academy.html'),'utf8');
const bridge = source.match(/<script id="fam-academy-fam-bridge"[^>]*>([\s\S]*?)<\/script>/)[1];
const dom = new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-backups-load" hidden></button><select id="academy-backups-select" hidden></select><button id="academy-backups-restore" hidden></button>',{url:'https://fam.test/',runScripts:'outside-only'});
const w=dom.window;const requests=[];let resolveRestore;
w.FAM_ACADEMY_BOOTSTRAP={};
w.confirm=()=>true;
w.fetch=(url,opts)=>{
  requests.push({url,opts});
  if(url.endsWith('/backups')) return Promise.resolve({ok:true,json:async()=>({currentRevision:5,backups:[{revision:2,saved_at:0}]})});
  if(url.endsWith('/restore')) return new Promise(resolve=>{resolveRestore=resolve});
  throw new Error('unexpected write after restore begins');
};
w.eval(bridge.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({csrf:'csrf',progressRevision:5,progress:{}})));
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await tick();
  const load=w.document.getElementById('academy-backups-load');const restore=w.document.getElementById('academy-backups-restore');
  assert.equal(load.hidden,false);load.click();await tick();await tick();
  assert.equal(requests[0].opts.headers['X-FAM-CSRF'],'csrf');assert.equal(restore.hidden,false);
  restore.click();await tick();
  assert.equal(requests.length,2);assert.deepEqual(JSON.parse(requests[1].opts.body),{backupRevision:2,expectedRevision:5});
  assert.equal(await w.FamAcademyBridge.saveProgress({completed:['late'],labs:{}}),false);
  assert.equal(requests.length,2);resolveRestore({ok:true});await tick();
  assert.match(w.document.getElementById('academy-save-status').textContent,/بازخوانی/);
  dom.window.close();console.log('jsdom recovery: account token, selection, CAS and stale-write stop passed');
})().catch(e=>{console.error(e);process.exitCode=1});
