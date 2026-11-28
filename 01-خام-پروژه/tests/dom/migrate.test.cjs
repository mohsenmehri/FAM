// jsdom, not a real browser or live deployment.
const {JSDOM} = require('jsdom');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const source=fs.readFileSync(path.resolve(__dirname,'../../server/private_ui/academy.html'),'utf8');
const script=source.match(/<script id="fam-academy-fam-bridge"[^>]*>([\s\S]*?)<\/script>/)[1];
const dom=new JSDOM('<!doctype html><div id="academy-save-status"></div><button id="academy-legacy-preview" hidden></button><button id="academy-legacy-migrate" hidden></button>',{url:'https://fam.test/',runScripts:'outside-only'});
const w=dom.window, requests=[];let confirmed=false;
w.confirm=()=>confirmed;
w.fetch=async(url,opts)=>{requests.push({url,opts}); if(url.endsWith('legacy-preview'))return {ok:true,json:async()=>({revision:4,uniqueCompletedCount:4,unmappedCount:1,blockedReason:null,eligible:['s01','s02','adv_bgp'],migrationAvailable:true})}; if(url.endsWith('/migrate'))return {ok:true,json:async()=>({revision:5})};throw Error('unexpected');};
w.eval(script.replace('__FAM_ACADEMY_BOOTSTRAP__',JSON.stringify({csrf:'token',progressRevision:4,progress:{'fam4.learn.v1':JSON.stringify({completedLessons:['s01','s02','adv_bgp','unknown_legacy_99']})}})));
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{await tick();const preview=w.document.getElementById('academy-legacy-preview'),migrate=w.document.getElementById('academy-legacy-migrate');assert.equal(preview.hidden,false);preview.click();await tick();await tick();assert.equal(migrate.hidden,false);assert.match(w.document.getElementById('academy-save-status').textContent,/بدون نگاشت: 1/);migrate.click();await tick();assert.equal(requests.length,1);confirmed=true;migrate.click();await tick();assert.equal(requests.length,2);assert.equal(requests[1].opts.headers['X-FAM-CSRF'],'token');assert.deepEqual(JSON.parse(requests[1].opts.body),{expectedRevision:4,selectedLessons:['s01','s02','adv_bgp']});assert.match(w.document.getElementById('academy-save-status').textContent,/بازخوانی/);assert.equal(await w.FamAcademyBridge.saveProgress({completed:[],labs:{}}),false);assert.equal(requests.length,2);dom.window.close();console.log('jsdom migration: explicit consent, multi-lesson selection, token and stale page lock passed');})().catch(e=>{console.error(e);process.exitCode=1});
