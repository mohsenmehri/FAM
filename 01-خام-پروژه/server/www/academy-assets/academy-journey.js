(() => {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const days = [['sat','شنبه'],['sun','یکشنبه'],['mon','دوشنبه'],['tue','سه‌شنبه'],['wed','چهارشنبه'],['thu','پنج‌شنبه'],['fri','جمعه']];
  const topics = [['osi-tcpip','OSI & TCP/IP'],['subnetting','Subnetting / VLSM'],['switching','Switching'],['routing','Routing'],['security','Security'],['automation','Automation']];
  let catalog = null;
  const current = () => window.FamAcademyBridge?.progress || { completed: [], labs: {} };
  const profile = () => current().profile || {};
  async function getCatalog() {
    if (!catalog) {
      const res = await fetch('/academy-assets/curriculum-catalog.json?v=20261123h', { cache:'no-store' });
      if (!res.ok) throw new Error('کاتالوگ در دسترس نیست');
      catalog = await res.json();
    }
    return catalog;
  }
  function openProfile({first = false} = {}) {
    if (document.getElementById('journey-profile-dialog')) return;
    const p = profile(), selectedDays = Array.isArray(p.studyDays) ? p.studyDays : ['sat','sun','mon','tue','wed','thu','fri'];
    const d = document.createElement('dialog'); d.id='journey-profile-dialog'; d.className='journey-dialog';
    d.setAttribute('aria-labelledby','journey-profile-title');
    d.innerHTML = `<form id="journey-profile-form"><div class="journey-dialog-head"><span class="journey-kicker">YOUR LEARNING JOURNEY</span>${first ? '' : '<button type="button" class="journey-close" aria-label="بستن">×</button>'}</div>
      <h2 id="journey-profile-title">${first ? 'مسیر یادگیری‌ات را بساز' : 'هدف و برنامهٔ یادگیری'}</h2><p class="journey-form-intro">چند انتخاب کوتاه کمک می‌کند قدم بعدی مناسب‌تری ببینی. هر زمان می‌توانی آن‌ها را تغییر بدهی.</p>
      <fieldset><legend>۱. کدام مسیر را دنبال می‌کنی؟</legend><div class="journey-choice-grid">${[['fam-c5','طرح جامع آکادمی (Curriculum 5.0)','از دانشکده صفر تا CCNA، CCNP، ۸ تخصص، CCIE و CCDE']].map(([v,t,sub]) => `<label class="journey-choice"><input type="radio" name="goal" value="${v}" ${((p.goal || 'fam-c5')===v)?'checked':''}><span><b>${t}</b><small>${sub}</small></span></label>`).join('')}</div></fieldset>
      <fieldset><legend>۲. چقدر با شبکه آشنایی داری؟</legend><div class="journey-choice-grid three">${[['beginner','تازه شروع می‌کنم'],['intermediate','مبانی را می‌دانم'],['advanced','تجربهٔ عملی دارم']].map(([v,t]) => `<label class="journey-choice"><input type="radio" name="level" value="${v}" ${((p.level || 'beginner')===v)?'checked':''}><span><b>${t}</b></span></label>`).join('')}</div></fieldset>
      <div class="journey-form-row"><label>زمان مطالعه در روز <select name="minutes"><option value="30" ${Number(p.minutesPerDay)===30?'selected':''}>۳۰ دقیقه</option><option value="45" ${Number(p.minutesPerDay)===45?'selected':''}>۴۵ دقیقه</option><option value="60" ${Number(p.minutesPerDay)===60?'selected':''}>۶۰ دقیقه</option><option value="90" ${Number(p.minutesPerDay)===90?'selected':''}>۹۰ دقیقه</option><option value="120" ${!p.minutesPerDay||Number(p.minutesPerDay)===120?'selected':''}>۱۲۰ دقیقه (۲ ساعت — استاندارد آکادمی)</option></select></label><label>تاریخ هدف <span class="muted">(اختیاری)</span><input type="date" name="targetDate" value="${esc(p.targetDate || '')}"></label></div>
      <fieldset><legend>روزهای پیشنهادی مطالعه</legend><div class="journey-days">${days.map(([v,t])=>`<label><input type="checkbox" name="studyDay" value="${v}" ${selectedDays.includes(v)?'checked':''}><span>${t}</span></label>`).join('')}</div></fieldset>
      <fieldset><legend>موضوعاتی که می‌خواهی بیشتر مرور کنی <span class="muted">(اختیاری)</span></legend><div class="journey-days">${topics.map(([v,t])=>`<label><input type="checkbox" name="topic" value="${v}" ${(p.reviewTopics || []).includes(v)?'checked':''}><span dir="ltr">${t}</span></label>`).join('')}</div><small>این انتخاب خودارزیابی است و به‌معنای تکمیل درس یا قبولی در آزمون نیست.</small></fieldset>
      <p class="journey-form-error" role="alert"></p><div class="journey-form-actions"><button class="journey-primary" type="submit">${first?'شروع مسیر یادگیری':'ذخیرهٔ تغییرات'} ←</button>${first?'<button type="button" class="journey-skip">بعداً تنظیم می‌کنم</button>':''}</div></form>`;
    document.body.appendChild(d);
    const close = () => { d.close(); d.remove(); };
    d.querySelector('.journey-close')?.addEventListener('click',close);
    d.querySelector('.journey-skip')?.addEventListener('click', close);
    if (first) d.addEventListener('cancel', event => { event.preventDefault(); close(); });
    d.querySelector('form').addEventListener('submit', async event => {
      event.preventDefault();
      const f = new FormData(event.currentTarget), selected = f.getAll('studyDay').map(String);
      const err = d.querySelector('.journey-form-error');
      if (!selected.length) { err.textContent='حداقل یک روز مطالعه انتخاب کن.'; return; }
      const updated = { ...p, onboardingComplete:true, goal:String(f.get('goal')), level:String(f.get('level')), minutesPerDay:Number(f.get('minutes')), studyDays:selected, daysPerWeek:selected.length, targetDate:String(f.get('targetDate') || ''), reviewTopics:f.getAll('topic').map(String) };
      const button=d.querySelector('[type=submit]'); button.disabled=true; err.textContent='در حال ذخیره…';
      const state={ ...current(), completed: [...window.FamAcademyCatalog.getCompletedSet()] };
      const ok=await window.FamAcademyBridge?.saveProgress({ ...state, profile:updated });
      button.disabled=false;
      if (!ok) { err.textContent='ذخیره انجام نشد؛ اتصال را بررسی و دوباره تلاش کن.'; return; }
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
      const activeFac=window.FamAcademyPlacement?.getActiveFaculty ? window.FamAcademyPlacement.getActiveFaculty() : null;
      const facDisplay=activeFac ? `${activeFac.badge} — ${activeFac.title}` : 'طرح جامع آکادمی (Curriculum 5.0)';
      root.innerHTML=`<div class="journey-progress-page"><div class="journey-progress-head"><div><span class="journey-kicker">YOUR LEARNING PROFILE</span><h1>پیشرفت و مسیر من</h1><p>یادگیری یک سفر است؛ اینجا می‌توانی قدم‌های ثبت‌شده‌ات را ببینی.</p></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="fam-btn-secondary" id="journey-change-level">تغییر سطح / آزمون تعیین سطح</button><button class="journey-primary small" id="journey-edit-profile">ویرایش هدف و برنامه ←</button></div></div>
        <div class="journey-progress-grid"><article class="journey-panel"><span class="journey-kicker">LESSONS COMPLETED</span><h2>درس‌های تکمیل‌شده</h2><div class="journey-stat">${done.length}<small>از ${count} درس</small></div><div class="fa-progress journey-meter"><span style="width:${pct}%"></span></div><p>بر اساس علامت‌گذاری دستی درس‌ها</p></article>
        <article class="journey-panel"><span class="journey-kicker">YOUR PLAN</span><h2>سطح فعال و برنامه</h2><div class="journey-stat" style="font-size:1.15rem">${esc(facDisplay)}<small>سطح فعلی شما (${p.placementMode==='exam'?'آزمون هوشمند':'انتخاب دستی'})</small></div><p>${Number(p.minutesPerDay)||120} دقیقه در روز · ${Number(p.daysPerWeek)||7} روز در هفته</p><p>${p.targetDate ? `تاریخ هدف: <bdi dir="ltr">${esc(p.targetDate)}</bdi>` : 'تاریخ هدف تنظیم نشده است.'}</p></article>
        <article class="journey-panel"><span class="journey-kicker">REVIEW FOCUS</span><h2>موضوعات برای مرور</h2><p>${selected.length ? selected.map(([,t])=>esc(t)).join(' · ') : 'هنوز موضوعی برای مرور انتخاب نکرده‌ای.'}</p><p class="journey-note">این فهرست انتخاب خودت است، نه سنجش خودکار تسلط.</p></article></div>
        <section class="journey-history"><div class="journey-heading"><div><span class="journey-kicker">YOUR MILESTONES</span><h2>درس‌های ثبت‌شده</h2><p>برای هر درس تکمیل‌شده می‌توانی دوباره مطالعه را باز کنی.</p></div></div>${done.length?`<div class="journey-history-list">${done.map(l=>`<button class="journey-history-item" data-open-lesson="${esc(l.id)}"><span>✓</span><strong>${esc(l.title)}</strong><small>تکمیل‌شده ←</small></button>`).join('')}</div>`:'<div class="journey-empty">هنوز درسی را تکمیل‌شده علامت نزده‌ای. با اولین قدم شروع کن.</div>'}</section></div>`;
      root.querySelector('#journey-edit-profile').onclick=()=>openProfile();
      root.querySelector('#journey-change-level').onclick=()=>{location.hash='#/placement';};
      root.querySelectorAll('[data-open-lesson]').forEach(button=>{button.onclick=()=>{location.hash='#'+button.dataset.openLesson;};});
    } catch(err) { if(root.dataset.loadSequence===requestId) root.textContent='نمایش پیشرفت ناموفق بود: '+err.message; }
  }
  window.FamJourney={openProfile,renderProgress};
})();
