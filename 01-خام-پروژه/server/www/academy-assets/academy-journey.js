(() => {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const days = [['sat','شنبه'],['sun','یکشنبه'],['mon','دوشنبه'],['tue','سه‌شنبه'],['wed','چهارشنبه'],['thu','پنج‌شنبه'],['fri','جمعه']];
  const topics = [
    ['switching','Switching & L2'],
    ['routing','Routing & BGP'],
    ['security','Security & Zero Trust'],
    ['sdwan','SD-WAN & Enterprise'],
    ['dc-sp','Data Center & SP'],
    ['wireless-collab','Wireless & Collab'],
    ['ccie-ccde','CCIE / CCDE Design'],
    ['automation','Automation & NetDevOps']
  ];
  const focusStages = [
    ['all', 'کل مسیر از ابتدا تا CCDE (۱۰۷ درس)'],
    ['c5-stage-zero', 'Stage Zero — مبانی از صفر (۱۳ درس)'],
    ['c5-ccna-v11-d1', 'CCNA 200-301 v1.1 (۲۶ درس)'],
    ['c5-advanced-eng', 'مهندسی پیشرفته شبکه (۱۲ درس)'],
    ['c5-ccnp-enterprise', 'CCNP Enterprise — ENCOR / ENARSI / SD-WAN (۱۱ درس)'],
    ['c5-specialties', 'تخصص‌ها — DC / Security / SP / Wireless / Collab (۱۸ درس)'],
    ['c5-ccie-expert', 'سطح خبره CCIE Tracks (۷ درس)'],
    ['c5-ccde-design', 'طراحی معماری کلان CCDE 400-007 (۲۰ درس)']
  ];
  const stageLabelMap = Object.fromEntries(focusStages);
  let catalog = null;
  const current = () => window.FamAcademyBridge?.progress || { completed: [], labs: {} };
  const profile = () => current().profile || {};
  async function getCatalog() {
    if (!catalog) {
      if (window.FamAcademyBridge && typeof window.FamAcademyBridge.fetchCatalog === 'function') {
        catalog = await window.FamAcademyBridge.fetchCatalog();
      } else {
        const res = await fetch('/academy-assets/curriculum-catalog.json', { cache:'no-store' });
        if (!res.ok) throw new Error('کاتالوگ در دسترس نیست');
        catalog = await res.json();
      }
    }
    return catalog;
  }
  function openProfile({first = false} = {}) {
    if (document.getElementById('journey-profile-dialog')) return;
    const p = profile(), selectedDays = Array.isArray(p.studyDays) ? p.studyDays : ['sat','sun','mon','tue','wed'];
    const currentGoal = p.goal === 'fam-automation' ? 'fam-automation' : 'fam-c5';
    const currentFocus = stageLabelMap[p.focusStage] ? p.focusStage : 'all';
    const d = document.createElement('dialog'); d.id='journey-profile-dialog'; d.className='journey-dialog';
    d.setAttribute('aria-labelledby','journey-profile-title');
    d.innerHTML = `<form id="journey-profile-form"><div class="journey-dialog-head"><span class="journey-kicker">YOUR LEARNING JOURNEY</span>${first ? '' : '<button type="button" class="journey-close" aria-label="بستن">×</button>'}</div>
      <h2 id="journey-profile-title">${first ? 'مسیر یادگیری‌ات را بساز' : 'هدف و برنامهٔ یادگیری'}</h2><p class="journey-form-intro">مسیر اصلی و مرحله هدف (از Stage Zero و CCNA تا مفاهیم پیشرفته CCNP، امنیت، طراحی شبکه یا اتوماسیون) را انتخاب کن تا پیشنهاد درس بعدی دقیق تنظیم شود.</p>
      <fieldset><legend>۱. کدام مسیر اصلی را دنبال می‌کنی؟</legend><div class="journey-choice-grid">${[
        ['fam-c5','Curriculum 5.0 (۱۰۷ درس)','از صفر تا CCNA، مفاهیم پیشرفته CCNP، امنیت و طراحی معماری شبکه'],
        ['fam-automation','Automation / NetDevOps (۲۰ درس)','Linux، Python، API، YANG، Ansible، Docker و Terraform']
      ].map(([v,t,sub]) => `<label class="journey-choice"><input type="radio" name="goal" value="${v}" ${(currentGoal===v)?'checked':''}><span><b>${t}</b><small>${sub}</small></span></label>`).join('')}</div></fieldset>
      <fieldset id="journey-focus-stage-fieldset"><legend>۲. تمرکز فعلی روی کدام دوره باشد؟ (در Curriculum 5.0)</legend><select name="focusStage" aria-label="انتخاب دوره تمرکز فعلی" style="width:100%;padding:9px 11px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--text)">${focusStages.map(([v,t]) => `<option value="${v}" ${currentFocus===v?'selected':''}>${t}</option>`).join('')}</select></fieldset>
      <fieldset><legend>۳. چقدر با شبکه آشنایی داری؟</legend><div class="journey-choice-grid three">${[['beginner','تازه شروع می‌کنم'],['intermediate','مبانی را می‌دانم'],['advanced','تجربهٔ عملی دارم']].map(([v,t]) => `<label class="journey-choice"><input type="radio" name="level" value="${v}" ${((p.level || 'beginner')===v)?'checked':''}><span><b>${t}</b></span></label>`).join('')}</div></fieldset>
      <div class="journey-form-row"><label>زمان مطالعه در روز <select name="minutes"><option value="15" ${Number(p.minutesPerDay)===15?'selected':''}>۱۵ دقیقه</option><option value="30" ${Number(p.minutesPerDay)===30?'selected':''}>۳۰ دقیقه</option><option value="45" ${!p.minutesPerDay||Number(p.minutesPerDay)===45?'selected':''}>۴۵ دقیقه</option><option value="60" ${Number(p.minutesPerDay)===60?'selected':''}>۶۰ دقیقه</option><option value="90" ${Number(p.minutesPerDay)===90?'selected':''}>۹۰ دقیقه</option></select></label><label>تاریخ هدف <span class="muted">(اختیاری)</span><input type="date" name="targetDate" value="${esc(p.targetDate || '')}"></label></div>
      <fieldset><legend>روزهای پیشنهادی مطالعه</legend><div class="journey-days">${days.map(([v,t])=>`<label><input type="checkbox" name="studyDay" value="${v}" ${selectedDays.includes(v)?'checked':''}><span>${t}</span></label>`).join('')}</div></fieldset>
      <fieldset><legend>موضوعاتی که می‌خواهی بیشتر مرور کنی <span class="muted">(اختیاری)</span></legend><div class="journey-days">${topics.map(([v,t])=>`<label><input type="checkbox" name="topic" value="${v}" ${(p.reviewTopics || []).includes(v)?'checked':''}><span dir="ltr">${t}</span></label>`).join('')}</div><small>این انتخاب خودارزیابی است و به‌معنای تکمیل درس یا قبولی در آزمون نیست.</small></fieldset>
      <p class="journey-form-error" role="alert"></p><div class="journey-form-actions"><button class="journey-primary" type="submit">${first?'شروع مسیر یادگیری':'ذخیرهٔ تغییرات'} ←</button>${first?'<button type="button" class="journey-skip">بعداً تنظیم می‌کنم</button>':''}</div></form>`;
    document.body.appendChild(d);
    const focusFieldset = d.querySelector('#journey-focus-stage-fieldset');
    const syncFocusVis = () => {
      const chosenGoal = d.querySelector('input[name="goal"]:checked')?.value || 'fam-c5';
      if (focusFieldset) focusFieldset.hidden = chosenGoal !== 'fam-c5';
    };
    d.querySelectorAll('input[name="goal"]').forEach(r => r.addEventListener('change', syncFocusVis));
    syncFocusVis();
    const close = () => { if (d.open) d.close(); d.remove(); };
    d.addEventListener('close', () => d.remove());
    d.querySelector('.journey-close')?.addEventListener('click', close);
    d.querySelector('.journey-skip')?.addEventListener('click', close);
    if (first) d.addEventListener('cancel', event => { event.preventDefault(); close(); });
    d.querySelector('form').addEventListener('submit', async event => {
      event.preventDefault();
      const f = new FormData(event.currentTarget), selected = f.getAll('studyDay').map(String);
      const err = d.querySelector('.journey-form-error');
      if (!selected.length) { err.textContent='حداقل یک روز مطالعه انتخاب کن.'; return; }
      const goalVal = String(f.get('goal') || 'fam-c5');
      const focusVal = goalVal === 'fam-c5' ? String(f.get('focusStage') || 'all') : 'all';
      const updated = { ...p, onboardingComplete:true, goal:goalVal, focusStage:focusVal, level:String(f.get('level')), minutesPerDay:Number(f.get('minutes')), studyDays:selected, daysPerWeek:selected.length, targetDate:String(f.get('targetDate') || ''), reviewTopics:f.getAll('topic').map(String) };
      const button=d.querySelector('[type=submit]'); button.disabled=true; err.textContent='در حال ذخیره…';
      const state={ ...current(), completed: [...window.FamAcademyCatalog.getCompletedSet()] };
      const ok=await window.FamAcademyBridge?.saveProgress({ ...state, profile:updated });
      button.disabled=false;
      if (!ok) {
        const bridge = window.FamAcademyBridge || {};
        const reason = bridge.lastError || 'ذخیره انجام نشد؛ اتصال را بررسی و دوباره تلاش کن.';
        err.replaceChildren();
        err.append(document.createTextNode(reason + ' '));
        if (bridge.lastStatus === 401 && !bridge.offline) {
          const loginLink = document.createElement('a');
          loginLink.href = '/login.html';
          loginLink.textContent = 'ورود مجدد به حساب ←';
          loginLink.style.cssText = 'color:var(--cyan);font-weight:800;text-decoration:underline;margin-inline-start:6px';
          err.append(loginLink);
        } else if (bridge.lastCode === 'shared_progress_locked' && !bridge.offline) {
          const unlockBtn = document.createElement('button');
          unlockBtn.type = 'button';
          unlockBtn.className = 'journey-primary small';
          unlockBtn.textContent = 'بررسی و باز کردن قفل پیشرفت قدیمی ←';
          unlockBtn.style.cssText = 'margin-inline-start:8px;padding:4px 12px;font-size:12px';
          unlockBtn.addEventListener('click', () => {
            close();
            const tools = document.getElementById('academy-account-tools');
            const previewBtn = document.getElementById('academy-legacy-preview');
            if (tools) {
              tools.classList.add('is-locked');
              tools.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            if (previewBtn && !previewBtn.hidden) previewBtn.click();
          });
          err.append(unlockBtn);
        } else if ((bridge.lastStatus === 403 || bridge.lastStatus === 409) && !bridge.offline) {
          const reloadBtn = document.createElement('button');
          reloadBtn.type = 'button';
          reloadBtn.className = 'btn';
          reloadBtn.textContent = 'بازخوانی صفحه';
          reloadBtn.style.cssText = 'margin-inline-start:6px;padding:3px 10px;font-size:12px';
          reloadBtn.addEventListener('click', () => location.reload());
          err.append(reloadBtn);
        }
        return;
      }
      window.dispatchEvent(new CustomEvent('fam-journey-profile-changed',{detail:updated}));
      close();
      if (location.hash === '#/progress') renderProgress();
      else document.getElementById('btn-paths')?.click();
    });
    d.showModal();
  }
  async function renderProgress() {
    const root=document.getElementById('app-root');
    const requestId=String((Number(root.dataset.loadSequence)||0)+1); root.dataset.loadSequence=requestId;
    root.innerHTML='<div class="fa-loading">در حال آماده‌سازی پیشرفت…</div>';
    try {
      const data=await getCatalog(); if(root.dataset.loadSequence!==requestId)return;
      const p=profile(), all=data.paths.flatMap(path=>path.courses.flatMap(course=>course.lessons));
      const completed=window.FamAcademyCatalog.getCompletedSet();
      const done=all.filter(l=>completed.has(l.id));
      const count=all.length, pct=count?Math.round(done.length*100/count):0;
      const selected=topics.filter(([v])=>(p.reviewTopics||[]).includes(v));
      const goalTitle = p.goal === 'fam-automation' ? 'Automation (۲۰ درس)' : 'Curriculum 5.0 (۱۰۷ درس)';
      const focusTitle = p.goal !== 'fam-automation' && p.focusStage && p.focusStage !== 'all' && stageLabelMap[p.focusStage]
        ? stageLabelMap[p.focusStage] : '';
      const isSignedInOnline = Boolean(window.FamAcademyBridge && !window.FamAcademyBridge.offline && window.FamAcademyBridge.user);
      let quizAttempts = current().labs?.quizAttempts;
      if ((!quizAttempts || typeof quizAttempts !== 'object') && !isSignedInOnline) {
        try { quizAttempts = JSON.parse(localStorage.getItem('fam_academy_quiz_v1') || '{}'); } catch (_) { quizAttempts = {}; }
      }
      if (!quizAttempts || typeof quizAttempts !== 'object') quizAttempts = {};
      const attemptEntries = Object.entries(quizAttempts || {}).filter(([, v]) => v && Number(v.total) > 0);
      const quizCount = attemptEntries.length;
      const avgScore = quizCount
        ? Number((attemptEntries.reduce((s, [, v]) => s + (Number(v.correct || 0) * 10 / Number(v.total)), 0) / quizCount).toFixed(1))
        : 0;
      const passedCount = attemptEntries.filter(([, v]) => (Number(v.correct || 0) / Number(v.total)) >= 0.7).length;
      const courseBreakdown = data.paths.flatMap(path => (path.courses || []).map(course => {
        const ls = course.lessons || [];
        const cDone = ls.filter(l => completed.has(l.id)).length;
        const cPct = ls.length ? Math.round(cDone * 100 / ls.length) : 0;
        const cQuizzes = ls.map(l => quizAttempts?.[l.id]).filter(v => v && Number(v.total) > 0);
        const cAvg = cQuizzes.length
          ? Number((cQuizzes.reduce((s, v) => s + (Number(v.correct || 0) * 10 / Number(v.total)), 0) / cQuizzes.length).toFixed(1))
          : null;
        return { title: course.title, done: cDone, total: ls.length, pct: cPct, quizCount: cQuizzes.length, avg: cAvg };
      }));
      let quizHistory = current().labs?.quizHistory;
      if ((!quizHistory || typeof quizHistory !== 'object') && !isSignedInOnline) {
        try { quizHistory = JSON.parse(localStorage.getItem('fam_academy_quiz_history_v1') || '{}'); } catch (_) { quizHistory = {}; }
      }
      if (!quizHistory || typeof quizHistory !== 'object') quizHistory = {};
      const scoreBadge = lessonId => {
        const q = quizAttempts?.[lessonId];
        if (!q || !Number(q.total)) return '';
        const ratio = Number(q.correct || 0) / Number(q.total);
        const sc = Number((ratio * 10).toFixed(1));
        const h = quizHistory?.[lessonId];
        const bestPart = h && Number.isInteger(h.bestCorrect) && h.attempts > 1
          ? ` · بهترین: ${Number((h.bestCorrect * 10 / Number(q.total)).toFixed(1))} (${h.attempts} تلاش)`
          : '';
        return `<span class="journey-score-badge ${ratio >= 0.7 ? 'is-pass' : 'is-low'}">آزمون: ${sc}/۱۰${bestPart}</span>`;
      };
      root.innerHTML=`<div class="journey-progress-page"><div class="journey-progress-head"><div><span class="journey-kicker">YOUR LEARNING PROFILE</span><h1>پیشرفت و سنجش تسلط من</h1><p>ترکیبی از درس‌های تکمیل‌شده، نمرات آزمون ۱۲سؤالی و پیشرفت هر دوره.</p></div><div class="journey-head-actions"><button class="journey-primary small" id="journey-edit-profile" type="button">ویرایش هدف و برنامه ←</button><button class="btn btn-reset-fresh" id="journey-reset-fresh" type="button">شروع از صفر (حالت خام)</button></div></div>
        <div class="journey-progress-grid"><article class="journey-panel"><span class="journey-kicker">LESSONS COMPLETED</span><h2>درس‌های تکمیل‌شده</h2><div class="journey-stat">${done.length}<small>از ${count} درس</small></div><div class="fa-progress journey-meter"><span style="width:${pct}%"></span></div><p>بر اساس تکمیل ثبت‌شده درس‌ها</p></article>
        <article class="journey-panel"><span class="journey-kicker">ASSESSMENT MASTERY</span><h2>میانگین آزمون‌ها</h2><div class="journey-stat">${quizCount ? avgScore : '—'}<small>${quizCount ? 'از ۱۰' : 'هنوز آزمونی ثبت نشده'}</small></div><p>${quizCount ? `${quizCount.toLocaleString('fa-IR')} آزمون ثبت‌شده · ${passedCount.toLocaleString('fa-IR')} قبولی (نمره ۷+)` : 'با ثبت اولین آزمون ۱۲سؤالی، میانگین تسلط اینجا محاسبه می‌شود.'}</p></article>
        <article class="journey-panel"><span class="journey-kicker">YOUR PLAN</span><h2>هدف و برنامه</h2><div class="journey-stat" style="font-size:22px">${esc(goalTitle)}</div>${focusTitle ? `<p style="color:var(--cyan);font-weight:700">تمرکز مرحله: ${esc(focusTitle)}</p>` : ''}<p>${Number(p.minutesPerDay)||45} دقیقه در روز · ${Number(p.daysPerWeek)||5} روز در هفته</p><p>${p.targetDate ? `تاریخ هدف: <bdi dir="ltr">${esc(p.targetDate)}</bdi>` : 'تاریخ هدف تنظیم نشده است.'}</p></article>
        <article class="journey-panel"><span class="journey-kicker">REVIEW FOCUS</span><h2>موضوعات برای مرور</h2><p>${selected.length ? selected.map(([,t])=>esc(t)).join(' · ') : 'هنوز موضوعی برای مرور انتخاب نکرده‌ای.'}</p><p class="journey-note">این فهرست انتخاب خودت است، نه سنجش خودکار تسلط.</p></article></div>
        <section class="journey-history"><div class="journey-heading"><div><span class="journey-kicker">COURSE BREAKDOWN</span><h2>پیشرفت به تفکیک دوره‌ها</h2><p>وضعیت تکمیل و میانگین نمره آزمون هر دوره در یک نگاه.</p></div></div>
          <div class="journey-course-grid">${courseBreakdown.map(c => `<article class="journey-course-item"><div class="journey-course-item-head"><strong>${esc(c.title)}</strong><span>${c.pct}٪</span></div><div class="fa-progress"><span style="width:${c.pct}%"></span></div><small class="muted">${c.done} از ${c.total} درس${c.avg !== null ? ` · میانگین آزمون: ${c.avg}/۱۰ (${c.quizCount} آزمون)` : ''}</small></article>`).join('')}</div>
        </section>
        <section class="journey-history"><div class="journey-heading"><div><span class="journey-kicker">YOUR MILESTONES</span><h2>درس‌های ثبت‌شده</h2><p>برای هر درس تکمیل‌شده می‌توانی دوباره مطالعه را باز کنی.</p></div></div>${done.length?`<div class="journey-history-list">${done.map(l=>`<button class="journey-history-item" data-open-lesson="${esc(l.id)}"><span>✓</span><strong>${esc(l.title)}</strong>${scoreBadge(l.id)}<small>تکمیل‌شده ←</small></button>`).join('')}</div>`:'<div class="journey-empty">هنوز درسی را تکمیل‌شده علامت نزده‌ای. با اولین قدم شروع کن.</div>'}</section></div>`;
      root.querySelector('#journey-edit-profile').onclick=()=>openProfile();
      const resetFreshBtn = root.querySelector('#journey-reset-fresh');
      if (resetFreshBtn) {
        resetFreshBtn.onclick = async () => {
          if (window.FamAcademyBridge && typeof window.FamAcademyBridge.resetFresh === 'function') {
            resetFreshBtn.disabled = true;
            const ok = await window.FamAcademyBridge.resetFresh();
            if (!ok) resetFreshBtn.disabled = false;
          }
        };
      }
      root.querySelectorAll('[data-open-lesson]').forEach(button=>{button.onclick=()=>{location.hash='#'+button.dataset.openLesson;};});
    } catch(err) { if(root.dataset.loadSequence===requestId) root.textContent='نمایش پیشرفت ناموفق بود: '+err.message; }
  }
  window.FamJourney={openProfile,renderProgress};
})();
