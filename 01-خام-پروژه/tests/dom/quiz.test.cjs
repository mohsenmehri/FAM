// Real DOM implementation (jsdom), not a real browser or network test.
const { JSDOM } = require('jsdom');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const engine = fs.readFileSync(path.join(root, 'server/www/academy-assets/lesson-engine.js'), 'utf8');
const bp = JSON.parse(fs.readFileSync(path.join(root, 'server/www/academy-assets/v5/blueprints/academy-automation-terraform.json'), 'utf8'));
const dom = new JSDOM('<!doctype html><div id="root"></div>', {url:'https://academy.test/', runScripts:'outside-only'});
const {window: w} = dom;
w.eval(engine);
const persisted = [];
w.FamAcademyBridge = {progress: {completed: [], labs: {}}, saveProgress(payload) {
  this.progress = JSON.parse(JSON.stringify(payload));
  persisted.push(this.progress);
  return Promise.resolve(true);
}};
const render = () => w.FamLessonEngine.renderLesson(w.document.querySelector('#root'), bp);
render();
const quiz = () => w.document.querySelector('[data-lesson-quiz]');
const grade = () => quiz().querySelector('[data-quiz-grade]').click();
const retry = () => quiz().querySelector('[data-quiz-retry]').click();
const result = () => quiz().querySelector('.lesson-quiz-result').textContent;
const choice = (i, n) => quiz().querySelector(`input[name="lesson-question-${i}"][value="${n}"]`).click();
assert.equal(quiz().querySelectorAll('fieldset').length, 12);
grade();
assert.match(result(), /نمره: 0 از ۱۰/);
assert.equal(persisted.at(-1).labs.quizAttempts[bp.lessonId].unanswered, 12);
assert.equal(persisted.at(-1).labs.quizAttempts[bp.lessonId].correct, 0);
retry();
assert.equal(result(), '');
assert.equal(quiz().querySelectorAll('input:checked').length, 0);
choice(0,bp.interactiveQuiz[0].correctIndex);
choice(1,(bp.interactiveQuiz[1].correctIndex + 1) % 4);
grade();
assert.match(result(), /پاسخ درست: 1 از 12/);
assert.deepEqual(persisted.at(-1).labs.quizAttempts[bp.lessonId], {correct:1, incorrect:1, unanswered:10, total:12});
assert.match(quiz().querySelector('[data-feedback="1"]').textContent, /نادرست/);
assert.equal(quiz().querySelector('[data-feedback="1"]').hidden, false);
retry();
bp.interactiveQuiz.forEach((question,i) => choice(i,question.correctIndex));
grade();
assert.match(result(), /نمره: 10 از ۱۰/);
assert.equal(persisted.at(-1).labs.quizAttempts[bp.lessonId].correct,12);
assert.deepEqual(persisted.at(-1).completed, [], 'quiz result is not automatic completion');
render();
assert.match(result(), /آخرین نتیجه ثبت‌شده: 12 از 12/);
// A different signed-in account does not load the first account's result.
w.FamAcademyBridge = {progress:{completed:[], labs:{}}, saveProgress(payload){this.progress=payload;return Promise.resolve(true);}};
render();
assert.equal(result(),'');
// A standalone session has its own local key, independent of authenticated data.
delete w.FamAcademyBridge;
render();
assert.equal(result(),'');
grade();
assert.equal(JSON.parse(w.localStorage.getItem('fam_academy_quiz_v1'))[bp.lessonId].correct,0);
render();
assert.match(result(), /آخرین نتیجه ثبت‌شده: 0 از 12/);
console.log('jsdom quiz: zero, partial, full, retry, persistence, account isolation: passed');
// Render the actual current catalog blueprints and verify the warning is
// visible in the lesson header, not just present in JSON metadata.
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'server/www/academy-assets/curriculum-catalog.json'), 'utf8'));
for (const item of catalog.paths.flatMap(track => track.courses.flatMap(course => course.lessons))) {
  const asset = item.blueprint.replace('/academy-assets/', 'server/www/academy-assets/');
  const lesson = JSON.parse(fs.readFileSync(path.join(root, asset), 'utf8'));
  w.FamLessonEngine.renderLesson(w.document.querySelector('#root'), lesson);
  const notice = w.document.querySelector('.lesson-review-status');
  assert(notice, `${item.id} must display a review notice`);
  if (["s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "s11", "s12", "ccna_01", "ccna_02"].includes(item.id)) {
    assert.match(notice.textContent, /بازبینی معنایی توسط نویسنده/);
    assert.match(notice.textContent, /بازبینی مستقل انجام نشده/);
  } else if (["auto_01", "auto_02", "auto_03", "auto_04", "auto_05", "auto_06", "auto_08", "auto_10", "auto_16", "auto_20", "ccna_02_vlan", "ccna_v1"].includes(item.id)) {
    assert.match(notice.textContent, /بازبینی فنی توسط یکپارچه‌ساز/);
    assert.match(notice.textContent, /بازبینی مستقل انسانی انجام نشده/);
    assert.match(notice.textContent, item.id === "auto_16" ? /شبیه‌سازی Python محلی/ : item.id === "ccna_v1" ? /شبیه‌سازی Python محلی/ : item.id === "auto_08" ? /شبیه‌سازی Python محلی/ : item.id === "ccna_02_vlan" ? /شبیه‌سازی Python محلی/ : item.id === "auto_06" ? /HTTP واقعی محلی/ : item.id === "auto_20" ? /شبیه‌سازی Python محلی/ : item.id === "auto_05" ? /پارس JSON و XML محلی/ : item.id === "auto_04" ? /Git محلی/ : /Python محلی/);
    assert.match(notice.textContent, item.id === "auto_01" ? /tcpdump مرجع است و روی تجهیز اجرا نشده/ : /سناریوی تجهیز مرجع/);
  } else {
    assert.match(notice.textContent, /در انتظار بازبینی/);
  }
  if (!["auto_01", "auto_02", "auto_03", "auto_04", "auto_05", "auto_06", "auto_08", "auto_10", "auto_16", "auto_20", "ccna_02_vlan", "ccna_v1"].includes(item.id)) assert.match(notice.textContent, /اجرای واقعی آن تأیید نشده/);
}
const unknown = {...bp, reviewStatus: '', evidence: ''};
w.FamLessonEngine.renderLesson(w.document.querySelector('#root'), unknown);
assert.match(w.document.querySelector('.lesson-review-status').textContent, /وضعیت بازبینی مشخص نیست/);
assert.match(w.document.querySelector('.lesson-review-status').textContent, /وضعیت اجرای آزمایشگاه مشخص نیست/);
const unsafe = {...bp, reviewStatus: '<img src=x onerror=alert(1)>', evidence: '<img src=x>'};
w.FamLessonEngine.renderLesson(w.document.querySelector('#root'), unsafe);
assert.equal(w.document.querySelector('.lesson-review-status img'), null);
assert.match(w.document.querySelector('.lesson-review-status').textContent, /<img/);
console.log('jsdom: review and execution status visible for all current lessons; unknown and escaping passed');
// Exercise score handling for the rewritten OSI lesson as well as Terraform.
const osi = JSON.parse(fs.readFileSync(path.join(root,'server/www/academy-assets/v5/blueprints/academy-stage-zero-osi-fa.json'),'utf8'));
w.FamLessonEngine.renderLesson(w.document.querySelector('#root'), osi);
const oq=w.document.querySelector('[data-lesson-quiz]');
assert.equal(oq.querySelectorAll('fieldset').length, 12);
osi.interactiveQuiz.forEach((question,i) => oq.querySelector(`input[name="lesson-question-${i}"][value="${question.correctIndex}"]`).click());
oq.querySelector('[data-quiz-grade]').click();
assert.match(oq.querySelector('.lesson-quiz-result').textContent, /نمره: 10 از ۱۰/);
console.log('jsdom: OSI quiz full-score interaction passed');
