// Real headless Chromium smoke test. Requires puppeteer-core and a compatible
// Chromium supplied separately; run via run_browser_test.py in a disposable DB.
const puppeteer = require('puppeteer-core');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
(async () => {
 const browser=await puppeteer.launch({executablePath:process.env.FAM_CHROMIUM_PATH, args:['--no-sandbox','--disable-dev-shm-usage'],headless:true});
 try {
  const page=await browser.newPage(); const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(process.env.FAM_TEST_URL+'/',{waitUntil:'networkidle0'});
  await page.type('#username','admin');
  await page.type('#password','TestAdminPassword!2026');
  await Promise.all([page.waitForNavigation({waitUntil:'networkidle0'}),page.click('#submit')]);
  await page.evaluate(()=>localStorage.setItem('fam_academy_progress_v1','["standalone-sentinel"]'));
  await page.goto(process.env.FAM_TEST_URL+'/academy#academy-automation-terraform',{waitUntil:'networkidle0'});
  await page.waitForSelector('.lesson-review-status');
  assert.match(await page.$eval('.lesson-review-status',e=>e.textContent),/در انتظار بازبینی/);

  // Verify client-side CLI simulator mounts online with exact scenario, real mock output & strict IP rejection
  await page.waitForSelector('[data-fam-cli-simulator="academy-automation-terraform"]');
  assert.equal(await page.$eval('[data-fam-cli-simulator="academy-automation-terraform"]',e=>e.getAttribute('data-sim-match-type')),'exact');
  assert.match(await page.$eval('[data-sim-honesty]',e=>e.textContent),/شبیه‌ساز آموزشی سمت مرورگر/);
  await page.click('[data-sim-quick="terraform plan"]');
  assert.match(await page.$eval('[data-sim-output]',e=>e.textContent),/Plan: 1 to add, 0 to change, 0 to destroy/);
  assert.doesNotMatch(await page.$eval('[data-sim-output]',e=>e.textContent),/خروجی شبیه‌ساز برای/);
  await page.type('[data-sim-input]','ping 999.999.999.999');
  await page.keyboard.press('Enter');
  assert.match(await page.$eval('[data-sim-output]',e=>e.textContent),/آدرس IP نامعتبر/);

  await page.$eval('[data-stage-id=quiz]',e=>e.scrollIntoView({block:'center',inline:'center'}));
  await page.click('[data-stage-id=quiz]');
  await page.click('[data-quiz-grade]');
  assert.match(await page.$eval('.lesson-quiz-result',e=>e.textContent),/نمره: 0 از ۱۰/);
  await page.click('[data-quiz-retry]');
  await page.click('input[name="lesson-question-0"][value="0"]');
  await page.click('[data-quiz-grade]');
  assert.match(await page.$eval('.lesson-quiz-result',e=>e.textContent),/پاسخ درست: 1 از 12/);
  await page.waitForFunction(()=>document.querySelector('#academy-save-status')?.textContent.includes('پیشرفت ذخیره شد'));
  await page.click('[data-quiz-retry]');
  const answers=await page.evaluate(async()=> (await (await fetch('/academy-assets/v5/blueprints/academy-automation-terraform.json')).json()).interactiveQuiz.map(q=>q.correctIndex));
  for(let i=0;i<answers.length;i++) await page.click(`input[name="lesson-question-${i}"][value="${answers[i]}"]`);
  await page.click('[data-quiz-grade]');
  assert.match(await page.$eval('.lesson-quiz-result',e=>e.textContent),/نمره: 10 از ۱۰/);
  await page.waitForFunction(()=>document.querySelector('#academy-save-status')?.textContent.includes('پیشرفت ذخیره شد'));
  assert.equal(await page.evaluate(()=>window.FamAcademyBridge.progress.completed.includes('academy-automation-terraform')),false);
  assert.equal(await page.evaluate(()=>localStorage.getItem('fam_academy_progress_v1')),'["standalone-sentinel"]');
  await page.reload({waitUntil:'networkidle0'}); await page.waitForSelector('[data-lesson-quiz]');
  assert.match(await page.$eval('.lesson-quiz-result',e=>e.textContent),/آخرین نتیجه ثبت‌شده: 12 از 12/);
  const logout=await page.evaluate(async()=>{const r=await fetch('/api/logout',{method:'POST',headers:{'Content-Type':'application/json','X-FAM-CSRF':window.FAM_ACADEMY_BOOTSTRAP.csrf},body:'{}'});return r.status});
  assert.equal(logout,200);
  assert.equal(await page.evaluate(()=>localStorage.getItem('fam_academy_progress_v1')),'["standalone-sentinel"]');
  assert.equal((await page.goto(process.env.FAM_TEST_URL+'/academy')).status(),401);
  console.log('Chromium online: login UI, status, simulator, zero/partial/full quiz, server reload, logout/isolation passed');

  const offline=await browser.newPage(), network=[];
  offline.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
  offline.on('pageerror',e=>errors.push(String(e)));
  await offline.goto(pathToFileURL(process.env.FAM_OFFLINE_FILE).href+'#academy-stage-zero-osi-fa',{waitUntil:'networkidle0'});
  await offline.waitForSelector('.lesson-review-status');
  assert.match(await offline.$eval('.lesson-review-status',e=>e.textContent),/در انتظار بازبینی/);
  const offlineBanner=await offline.$eval('[role=note]',e=>e.textContent);
  assert.match(offlineBanner,/شامل هر 127 درس فعال/);
  assert.match(offlineBanner,/همگام نیست/);
  assert.match(offlineBanner,/نه بازبینی مستقل انسانی/);
  assert.match(offlineBanner,/اتصال به تجهیزات واقعی وجود ندارد/);
  await offline.waitForSelector('[data-fam-cli-simulator="academy-stage-zero-osi-fa"]');
  await offline.$eval('[data-stage-id=quiz]',e=>e.scrollIntoView({block:'center',inline:'center'}));
  await offline.click('[data-stage-id=quiz]');
  await offline.click('[data-quiz-grade]');
  assert.match(await offline.$eval('.lesson-quiz-result',e=>e.textContent),/نمره: 0 از ۱۰/);
  await offline.click('[data-quiz-retry]');
  await offline.click('input[name="lesson-question-0"][value="0"]');
  await offline.click('[data-quiz-grade]');
  assert.match(await offline.$eval('#academy-save-status',e=>e.textContent),/همگام نیست/);
  await offline.click('[data-quiz-retry]');
  const offlineAnswers=await offline.evaluate(async()=> (await (await fetch('/academy-assets/v5/blueprints/academy-stage-zero-osi-fa.json')).json()).interactiveQuiz.map(q=>q.correctIndex));
  for(let i=0;i<offlineAnswers.length;i++) await offline.click(`input[name="lesson-question-${i}"][value="${offlineAnswers[i]}"]`);
  await offline.click('[data-quiz-grade]');
  assert.match(await offline.$eval('.lesson-quiz-result',e=>e.textContent),/نمره: 10 از ۱۰/);
  await offline.reload({waitUntil:'networkidle0'}); await offline.waitForSelector('[data-lesson-quiz]');
  assert.match(await offline.$eval('.lesson-quiz-result',e=>e.textContent),/آخرین نتیجه ثبت‌شده: 12 از 12/);
  assert.deepEqual(network,[]);assert.deepEqual(errors,[]);
  console.log('Chromium file:// offline: 127-lesson banner, simulator, zero/partial/full quiz, localStorage reload and no HTTP requests passed');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
