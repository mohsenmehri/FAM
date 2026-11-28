// The generated page runs in jsdom; this is not a real-browser test.
const {JSDOM, VirtualConsole} = require('jsdom');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.resolve(__dirname,'../../../FAM-Academy-Offline.html'),'utf8');
const errors=[];
const vc = new VirtualConsole(); vc.on('jsdomError', e => errors.push(e.message));
function boot(saved, lesson='academy-stage-zero-osi-fa') {
  return new JSDOM(html, {url:`https://offline.fam.test/#${lesson}`,runScripts:'dangerously',virtualConsole:vc,
    beforeParse(w) {
      w.Response=global.Response;
      w.matchMedia=()=>({matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){}});
      w.fetch=()=>{throw new Error('unexpected network fetch')};
      w.HTMLElement.prototype.scrollIntoView=function(){};
      if(saved) w.localStorage.setItem('fam.academy.offline.v2',saved);
    }});
}
async function waitFor(fn) {
  for(let i=0;i<100;i++) {if(fn()) return; await new Promise(resolve=>setTimeout(resolve,20));}
  throw new Error('timed out waiting for offline view');
}
(async()=>{
  let dom=boot(); let w=dom.window;
  await waitFor(()=>w.document.querySelector('[data-lesson-quiz]'));
  assert.match(w.document.querySelector('[role=note]').textContent,/پوشش کامل ۱۱۴ شناسه تاریخی/);
  assert.match(w.document.querySelector('[role=note]').textContent,/با حساب آنلاین همگام نیست/);
  assert.ok(w.document.querySelector('[data-fam-cli-simulator]'));
  assert.match(w.document.querySelector('.lesson-review-status').textContent,/در انتظار بازبینی/);
  const response=await w.fetch('https://example.invalid/not-bundled');
  assert.equal(response.status,404);
  const q=w.document.querySelector('[data-lesson-quiz]');
  q.querySelector('input[name="lesson-question-0"][value="0"]').click();
  q.querySelector('[data-quiz-grade]').click();
  await waitFor(()=>w.localStorage.getItem('fam.academy.offline.v2'));
  const saved=w.localStorage.getItem('fam.academy.offline.v2');
  assert.equal(JSON.parse(saved).labs.quizAttempts['academy-stage-zero-osi-fa'].correct,1);
  assert.match(w.document.getElementById('academy-save-status').textContent,/همگام نیست/);
  dom.window.close();
  dom=boot(saved);w=dom.window;
  await waitFor(()=>w.document.querySelector('[data-lesson-quiz]'));
  assert.match(w.document.querySelector('.lesson-quiz-result').textContent,/آخرین نتیجه ثبت‌شده: 1 از 12/);
  dom.window.close();
  dom=boot(null, 'auto_05'); w=dom.window;
  await waitFor(()=>w.document.querySelector('[data-lesson-quiz]'));
  const status=w.document.querySelector('.lesson-review-status').textContent;
  assert.match(status,/بازبینی فنی توسط یکپارچه‌ساز/);
  assert.match(status,/بازبینی مستقل انسانی انجام نشده/);
  assert.match(status,/پارس JSON و XML محلی/);
  assert.match(status,/سناریوی تجهیز مرجع/);
  const autoQuiz=w.document.querySelector('[data-lesson-quiz]');
  autoQuiz.querySelector('input[name="lesson-question-0"][value="1"]').click();
  autoQuiz.querySelector('[data-quiz-grade]').click();
  await waitFor(()=>w.localStorage.getItem('fam.academy.offline.v2'));
  assert.equal(JSON.parse(w.localStorage.getItem('fam.academy.offline.v2')).labs.quizAttempts.auto_05.correct,1);
  dom.window.close();
  dom=boot(null, 'auto_04'); w=dom.window;
  await waitFor(()=>w.document.querySelector('[data-lesson-quiz]'));
  assert.match(w.document.querySelector('.lesson-review-status').textContent,/Git محلی/);
  assert.match(w.document.querySelector('.lesson-review-status').textContent,/بازبینی مستقل انسانی انجام نشده/);
  const gitQuiz=w.document.querySelector('[data-lesson-quiz]');
  gitQuiz.querySelector('input[name="lesson-question-0"][value="0"]').click();
  gitQuiz.querySelector('[data-quiz-grade]').click();
  await waitFor(()=>w.localStorage.getItem('fam.academy.offline.v2'));
  assert.equal(JSON.parse(w.localStorage.getItem('fam.academy.offline.v2')).labs.quizAttempts.auto_04.correct,1);
  dom.window.close();
  dom=boot(null, 'auto_02'); w=dom.window;
  await waitFor(()=>w.document.querySelector('[data-lesson-quiz]'));
  assert.match(w.document.querySelector('.lesson-review-status').textContent,/Python محلی/);
  assert.match(w.document.querySelector('.lesson-review-status').textContent,/بازبینی مستقل انسانی انجام نشده/);
  const pyQuiz=w.document.querySelector('[data-lesson-quiz]');
  pyQuiz.querySelector('input[name="lesson-question-0"][value="1"]').click();
  pyQuiz.querySelector('[data-quiz-grade]').click();
  await waitFor(()=>w.localStorage.getItem('fam.academy.offline.v2'));
  assert.equal(JSON.parse(w.localStorage.getItem('fam.academy.offline.v2')).labs.quizAttempts.auto_02.correct,1);
  dom.window.close();

  // Regression: Windows file:///C:/... URLs and about:blank/srcdoc must load bundled assets without HTTP 404,
  // while external-origin requests spoofing bundled pathnames remain blocked with 404.
  for (const testUrl of [
    'file:///C:/Users/Mohsen/Downloads/FAM-Academy-Offline.html#academy-stage-zero-osi-fa',
    'about:blank',
  ]) {
    const winDom = new JSDOM(html, {
      url: testUrl,
      runScripts: 'dangerously',
      virtualConsole: vc,
      beforeParse(win) {
        win.Response = global.Response;
        win.matchMedia = () => ({matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){}});
        win.fetch = () => { throw new Error('unexpected network fetch'); };
        win.HTMLElement.prototype.scrollIntoView = function(){};
      },
    });
    const ww = winDom.window;
    const okRes = await ww.fetch('/academy-assets/curriculum-catalog.json');
    assert.equal(okRes.status, 200, `bundled catalog must load under ${testUrl}`);
    const okQsRes = await ww.fetch('/academy-assets/curriculum-catalog.json?v=20261123c');
    assert.equal(okQsRes.status, 200, `query-string catalog must load under ${testUrl}`);
    const spoofRes = await ww.fetch('https://evil.invalid/academy-assets/curriculum-catalog.json');
    assert.equal(spoofRes.status, 404, `external origin spoofing bundled path must return 404 under ${testUrl}`);
    if (testUrl.startsWith('file:///C:/')) {
      await waitFor(() => ww.document.querySelector('[data-lesson-quiz]'));
      assert.equal(ww.document.querySelector('.fa-error'), null);
      // Verify v6 Live Topology UI upgrades: sticky TOC, per-lesson notes, study timer, offline banner host
      assert.ok(ww.document.querySelector('#le-toc-list .lesson-toc-link'), 'lesson TOC must render');
      assert.ok(ww.document.querySelector('#le-lesson-notes'), 'per-lesson notes textarea must render');
      assert.ok(ww.document.querySelector('.side-timer-display'), 'sidebar study timer must render');
      assert.ok(ww.document.querySelector('.offline-banner-host [role=note]'), 'offline banner must mount inside .offline-banner-host');
    }
    winDom.window.close();
  }

  // Verify dashboard Live Topology Hero, Daily Missions, Theme toggle, and dedicated #/lab Workbench
  const dashDom = new JSDOM(html, {
    url: 'file:///C:/Users/Mohsen/Downloads/FAM-Academy-Offline.html#/dashboard',
    runScripts: 'dangerously',
    virtualConsole: vc,
    beforeParse(win) {
      win.Response = global.Response;
      win.matchMedia = () => ({matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){}});
      win.fetch = () => { throw new Error('unexpected network fetch'); };
      win.HTMLElement.prototype.scrollIntoView = function(){};
    },
  });
  const dw = dashDom.window;
  await waitFor(() => dw.document.querySelector('.hero-topo-svg'));
  assert.ok(dw.document.querySelector('.mission-card [data-mission-id]'), 'daily missions must render');
  const themeBtn = dw.document.querySelector('.theme-toggle');
  assert.ok(themeBtn, 'theme toggle must exist');
  themeBtn.click();
  assert.equal(dw.document.documentElement.dataset.theme, 'light');
  themeBtn.click();
  assert.equal(dw.document.documentElement.dataset.theme, 'dark');
  dashDom.window.close();

  const labDom = new JSDOM(html, {
    url: 'file:///C:/Users/Mohsen/Downloads/FAM-Academy-Offline.html#/lab',
    runScripts: 'dangerously',
    virtualConsole: vc,
    beforeParse(win) {
      win.Response = global.Response;
      win.matchMedia = () => ({matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){}});
      win.fetch = () => { throw new Error('unexpected network fetch'); };
      win.HTMLElement.prototype.scrollIntoView = function(){};
    },
  });
  const lw = labDom.window;
  await waitFor(() => lw.document.querySelector('#lab-sim-mount [data-fam-cli-simulator]'));
  assert.ok(lw.document.querySelectorAll('.lab-scenario-item').length >= 47, 'lab workbench must list exact scenarios');
  labDom.window.close();

  assert.deepEqual(errors,[]);
  console.log('jsdom offline: bundled lessons, v6 Live Topology UI (hero, timer, missions, TOC, notes, #/lab, theme), Windows file:///C:/ + about:blank loading, network blocking, quiz local persistence and reload passed');
})().catch(e=>{console.error(e);process.exitCode=1});
