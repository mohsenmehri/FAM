(() => {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const days = [['sat','شنبه'],['sun','یکشنبه'],['mon','دوشنبه'],['tue','سه‌شنبه'],['wed','چهارشنبه'],['thu','پنج‌شنبه'],['fri','جمعه']];
  const topics = [['osi-tcpip','OSI & TCP/IP'],['subnetting','Subnetting / VLSM'],['switching','Switching'],['routing','Routing'],['security','Security'],['automation','Automation']];
  const FALLBACK_FACULTIES = [
    { id: 'f0', badge: 'دانشکده ۰ · مبانی', title: 'آمادگی پایه و شبکه‌سازی مقدماتی', subtitle: 'OSI، TCP/IP، آدرس‌دهی IPv4 و مفاهیم پایه' },
    { id: 'f1', badge: 'دانشکده ۱ · CCNA', title: 'مهندسی شبکه با CCNA 200-301', subtitle: 'Switching، VLAN، OSPF، ACL، NAT و مبانی امنیت' },
    { id: 'f2', badge: 'دانشکده ۲ · R&S پیشرفته', title: 'سوییچینگ و مسیریابی سازمانی پیشرفته', subtitle: 'RSTP/MSTP، LACP، HSRP/VRRP، OSPF Multi-Area و VRF' },
    { id: 'f3', badge: 'دانشکده ۳ · CCNP', title: 'مهندسی هسته سازمانی (350-401 ENCOR)', subtitle: 'SD-Access، LISP، BGP پیشرفته، QoS و اتوماسیون' },
    { id: 'f4', badge: 'دانشکده ۴ · تخصصی', title: 'گرایش‌های Security، Data Center و SD-WAN', subtitle: '802.1X/ISE، EVPN/VXLAN و شبکه‌های تعریف‌شده با نرم‌افزار' },
    { id: 'f5', badge: 'دانشکده ۵ · CCIE', title: 'معماری تخصصی و سطح خبره (CCIE)', subtitle: 'MPLS L3VPN، MP-BGP، Segment Routing و TI-LFA' },
    { id: 'f6', badge: 'دانشکده ۶ · CCDE', title: 'طراحی کلان زیرساخت و معماری (CCDE)', subtitle: 'دامنه‌های شکست، معماری WAN چندمنطقه‌ای و تصمیم‌گیری کلان' }
  ];
  const facultyToLevel = fid => (fid === 'f0' || fid === 'f1') ? 'beginner' : (fid === 'f2' || fid === 'f3') ? 'intermediate' : 'advanced';
  let catalog = null;
  const current = () => window.FamAcademyBridge?.progress || { completed: [], labs: {} };
  const profile = () => current().profile || {};
  async function getCatalog() {
    if (!catalog) {
      const res = await fetch('/academy-assets/curriculum-catalog.json?v=20261123i', { cache:'no-store' });
      if (!res.ok) throw new Error('کاتالوگ در دسترس نیست');
      catalog = await res.json();
    }
    return catalog;
  }
  function openProfile({first = false} = {}) {
    if (document.getElementById('journey-profile-dialog')) return;
    const p = profile();
    const selectedDays = Array.isArray(p.studyDays) ? p.studyDays : ['sat','sun','mon','tue','wed','thu','fri'];
    const faculties = (window.FamAcademyPlacement?.FACULTIES?.length ? window.FamAcademyPlacement.FACULTIES : FALLBACK_FACULTIES);
    const activeFacultyId = p.facultyId || p.currentStage || (p.level === 'advanced' ? 'f4' : p.level === 'intermediate' ? 'f2' : 'f0');
    const d = document.createElement('dialog');
    d.id = 'journey-profile-dialog';
    d.className = 'journey-dialog journey-dialog-faculty';
    d.setAttribute('aria-labelledby', 'journey-profile-title');
    d.innerHTML = `<form id="journey-profile-form">
      <div class="journey-dialog-head">
        <span class="journey-kicker">YOUR LEARNING JOURNEY</span>
        ${first ? '' : '<button type="button" class="journey-close" aria-label="بستن">×</button>'}
      </div>
      <h2 id="journey-profile-title">${first ? 'انتخاب دانشکده و شروع مسیر' : 'انتخاب دانشکده و برنامهٔ یادگیری'}</h2>
      <p class="journey-form-intro">دانشکدهٔ مورد نظر خودتان را انتخاب کنید تا درس‌ها، مسیرها و پیشنهادهای آکادمی بر اساس همان سطح تنظیم شوند.</p>

      <fieldset>
        <div class="journey-faculty-legend-row">
          <legend>۱. دانشکدهٔ خود را انتخاب کنید (۷ سطح)</legend>
          <button type="button" class="journey-exam-link" id="journey-go-exam">یا شرکت در آزمون تعیین سطح ۱۴ سؤالی ←</button>
        </div>
        <div class="journey-faculty-grid">
          ${faculties.map(fac => `
            <label class="journey-choice journey-faculty-choice">
              <input type="radio" name="facultyId" value="${esc(fac.id)}" ${activeFacultyId === fac.id ? 'checked' : ''}>
              <span>
                <small class="journey-fac-badge">${esc(fac.badge)}</small>
                <b>${esc(fac.title)}</b>
                <small>${esc(fac.subtitle || '')}</small>
              </span>
            </label>`).join('')}
        </div>
      </fieldset>

      <div class="journey-form-row">
        <label>زمان مطالعه در روز
          <select name="minutes">
            <option value="30" ${Number(p.minutesPerDay)===30?'selected':''}>۳۰ دقیقه</option>
            <option value="45" ${Number(p.minutesPerDay)===45?'selected':''}>۴۵ دقیقه</option>
            <option value="60" ${Number(p.minutesPerDay)===60?'selected':''}>۶۰ دقیقه</option>
            <option value="90" ${Number(p.minutesPerDay)===90?'selected':''}>۹۰ دقیقه</option>
            <option value="120" ${!p.minutesPerDay||Number(p.minutesPerDay)===120?'selected':''}>۱۲۰ دقیقه (۲ ساعت — استاندارد آکادمی)</option>
          </select>
        </label>
        <label>تاریخ هدف <span class="muted">(اختیاری)</span>
          <input type="date" name="targetDate" value="${esc(p.targetDate || '')}">
        </label>
      </div>

      <fieldset>
        <legend>روزهای پیشنهادی مطالعه</legend>
        <div class="journey-days">${days.map(([v,t])=>`<label><input type="checkbox" name="studyDay" value="${v}" ${selectedDays.includes(v)?'checked':''}><span>${t}</span></label>`).join('')}</div>
      </fieldset>

      <fieldset>
        <legend>موضوعاتی که می‌خواهی بیشتر مرور کنی <span class="muted">(اختیاری)</span></legend>
        <div class="journey-days">${topics.map(([v,t])=>`<label><input type="checkbox" name="topic" value="${v}" ${(p.reviewTopics || []).includes(v)?'checked':''}><span dir="ltr">${t}</span></label>`).join('')}</div>
        <small>این انتخاب خودارزیابی است و به‌معنای تکمیل درس یا قبولی در آزمون نیست.</small>
      </fieldset>

      <p class="journey-form-error" role="alert"></p>
      <div class="journey-form-actions journey-form-sticky">
        <button class="journey-primary" type="submit">${first ? 'ورود به دانشکدهٔ انتخابی' : 'ذخیرهٔ دانشکده و تغییرات'} ←</button>
        ${first ? '<button type="button" class="journey-skip">بعداً تنظیم می‌کنم</button>' : '<button type="button" class="journey-skip">انصراف</button>'}
      </div>
    </form>`;
    document.body.appendChild(d);
    const close = () => { d.close(); d.remove(); };
    d.querySelector('.journey-close')?.addEventListener('click', close);
    d.querySelector('.journey-skip')?.addEventListener('click', close);
    d.querySelector('#journey-go-exam')?.addEventListener('click', () => {
      close();
      location.hash = '#/placement';
    });
    if (first) d.addEventListener('cancel', event => { event.preventDefault(); close(); });
    d.querySelector('form').addEventListener('submit', async event => {
      event.preventDefault();
      const f = new FormData(event.currentTarget);
      const selected = f.getAll('studyDay').map(String);
      const fid = String(f.get('facultyId') || 'f0');
      const err = d.querySelector('.journey-form-error');
      if (!selected.length) { err.textContent = 'حداقل یک روز مطالعه انتخاب کن.'; return; }
      const updated = {
        ...p,
        onboardingComplete: true,
        goal: 'fam-c5',
        facultyId: fid,
        currentStage: fid,
        level: facultyToLevel(fid),
        placementMode: 'manual',
        minutesPerDay: Number(f.get('minutes')),
        studyDays: selected,
        daysPerWeek: selected.length,
        targetDate: String(f.get('targetDate') || ''),
        reviewTopics: f.getAll('topic').map(String)
      };
      const button = d.querySelector('[type=submit]');
      button.disabled = true;
      err.textContent = 'در حال ذخیره…';
      const state = { ...current(), completed: [...window.FamAcademyCatalog.getCompletedSet()] };
      const ok = await window.FamAcademyBridge?.saveProgress({ ...state, profile: updated });
      button.disabled = false;
      if (!ok) { err.textContent = 'ذخیره انجام نشد؛ اتصال را بررسی و دوباره تلاش کن.'; return; }
      window.dispatchEvent(new CustomEvent('fam-journey-profile-changed', { detail: updated }));
      close();
      if (location.hash === '#/progress') renderProgress();
      else location.hash = '#/dashboard';
    });
    d.showModal();
  }
  async function renderProgress() {
    const root = document.getElementById('app-root');
    const requestId = String((Number(root.dataset.loadSequence) || 0) + 1);
    root.dataset.loadSequence = requestId;
    root.innerHTML = '<div class="fa-loading">در حال آماده‌سازی پیشرفت…</div>';
    try {
      const data = await getCatalog();
      if (root.dataset.loadSequence !== requestId) return;
      const p = profile();
      const all = data.paths.flatMap(path => path.courses.flatMap(course => course.lessons));
      const completed = window.FamAcademyCatalog.getCompletedSet();
      const done = all.filter(l => completed.has(l.id));
      const count = all.length;
      const pct = count ? Math.round(done.length * 100 / count) : 0;
      const selected = topics.filter(([v]) => (p.reviewTopics || []).includes(v));
      const activeFac = window.FamAcademyPlacement?.getActiveFaculty ? window.FamAcademyPlacement.getActiveFaculty() : null;
      const facDisplay = activeFac ? `${activeFac.badge} — ${activeFac.title}` : 'طرح جامع آکادمی (Curriculum 5.0)';
      root.innerHTML = `<div class="journey-progress-page"><div class="journey-progress-head"><div><span class="journey-kicker">YOUR LEARNING PROFILE</span><h1>پیشرفت و مسیر من</h1><p>یادگیری یک سفر است؛ اینجا می‌توانی قدم‌های ثبت‌شده‌ات را ببینی.</p></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="fam-btn-secondary" id="journey-change-level">تغییر سطح / آزمون تعیین سطح</button><button class="journey-primary small" id="journey-edit-profile">انتخاب دانشکده و برنامه ←</button></div></div>
        <div class="journey-progress-grid"><article class="journey-panel"><span class="journey-kicker">LESSONS COMPLETED</span><h2>درس‌های تکمیل‌شده</h2><div class="journey-stat">${done.length}<small>از ${count} درس</small></div><div class="fa-progress journey-meter"><span style="width:${pct}%"></span></div><p>بر اساس علامت‌گذاری دستی درس‌ها</p></article>
        <article class="journey-panel"><span class="journey-kicker">YOUR PLAN</span><h2>سطح فعال و برنامه</h2><div class="journey-stat" style="font-size:1.15rem">${esc(facDisplay)}<small>سطح فعلی شما (${p.placementMode === 'exam' ? 'آزمون هوشمند' : 'انتخاب دستی'})</small></div><p>${Number(p.minutesPerDay) || 120} دقیقه در روز · ${Number(p.daysPerWeek) || 7} روز در هفته</p><p>${p.targetDate ? `تاریخ هدف: <bdi dir="ltr">${esc(p.targetDate)}</bdi>` : 'تاریخ هدف تنظیم نشده است.'}</p></article>
        <article class="journey-panel"><span class="journey-kicker">REVIEW FOCUS</span><h2>موضوعات برای مرور</h2><p>${selected.length ? selected.map(([,t]) => esc(t)).join(' · ') : 'هنوز موضوعی برای مرور انتخاب نکرده‌ای.'}</p><p class="journey-note">این فهرست انتخاب خودت است، نه سنجش خودکار تسلط.</p></article></div>
        <section class="journey-history"><div class="journey-heading"><div><span class="journey-kicker">YOUR MILESTONES</span><h2>درس‌های ثبت‌شده</h2><p>برای هر درس تکمیل‌شده می‌توانی دوباره مطالعه را باز کنی.</p></div></div>${done.length ? `<div class="journey-history-list">${done.map(l => `<button class="journey-history-item" data-open-lesson="${esc(l.id)}"><span>✓</span><strong>${esc(l.title)}</strong><small>تکمیل‌شده ←</small></button>`).join('')}</div>` : '<div class="journey-empty">هنوز درسی را تکمیل‌شده علامت نزده‌ای. با اولین قدم شروع کن.</div>'}</section></div>`;
      root.querySelector('#journey-edit-profile').onclick = () => openProfile();
      root.querySelector('#journey-change-level').onclick = () => { location.hash = '#/placement'; };
      root.querySelectorAll('[data-open-lesson]').forEach(button => { button.onclick = () => { location.hash = '#' + button.dataset.openLesson; }; });
    } catch (err) {
      if (root.dataset.loadSequence === requestId) root.textContent = 'نمایش پیشرفت ناموفق بود: ' + err.message;
    }
  }
  window.FamJourney = { openProfile, renderProgress };
})();
