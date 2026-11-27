(() => {
  'use strict';
  const STORAGE_KEY = 'fam_academy_progress_v1';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  function getCompletedSet() {
    const bridge = window.FamAcademyBridge;
    if (bridge) {
      const server = bridge.progress?.completed;
      return new Set(Array.isArray(server) ? server : []);
    }
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const arr = raw ? JSON.parse(raw) : [];
      if (Array.isArray(arr)) return new Set(arr);
    } catch {}
    return new Set();
  }

  function lessonIcon() {
    // Generic academy glyph; the catalog no longer carries per-lesson icons.
    const d = 'M12 4a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM5 16a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM19 16a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM10 9 7 16 M14 9l3 7 M8 19h8';
    return `<svg viewBox="0 0 24 24" width="27" height="27" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;
  }
  function calcCourseProgress(course, completed) {
    const lessons = course.lessons || [], done = lessons.filter(l => completed.has(l.id)).length;
    return { done, total: lessons.length, pct: lessons.length ? Math.round(done / lessons.length * 100) : 0 };
  }
  function calcPathProgress(path, completed) {
    let done = 0, total = 0;
    (path.courses || []).forEach(course => { const p = calcCourseProgress(course, completed); done += p.done; total += p.total; });
    return { done, total, pct: total ? Math.round(done / total * 100) : 0 };
  }
  function renderDashboard(container, catalog, onOpenLesson) {
    const completed = getCompletedSet(), paths = catalog?.paths || [];
    const profile = window.FamAcademyBridge?.progress?.profile || {};
    const all = paths.flatMap(p => (p.courses || []).flatMap(c => c.lessons || []));
    const chosen = paths.find(p => p.id === profile.goal) || paths[0];
    const target = (chosen?.courses || []).flatMap(c => c.lessons || []);
    const assessed = new Set(window.FamAcademyBridge?.progress?.selfAssessed || []);
    const ready = item => (item.prerequisites || []).every(id => completed.has(id) || assessed.has(id));
    const next = target.find(l => !completed.has(l.id) && l.blueprint && ready(l)) || all.find(l => !completed.has(l.id) && l.blueprint && ready(l));
    const done = target.filter(l => completed.has(l.id)).length;
    const pct = target.length ? Math.round(done / target.length * 100) : 0;
    const user = window.FamAcademyBridge?.user?.username || '';
    const greeting = user && user !== 'e2e-test-user' ? `سلام، ${esc(user)}` : 'سلام، یادگیرندهٔ شبکه';
    const level = ({ beginner:'تازه شروع می‌کنم', intermediate:'با مبانی آشنا هستم', advanced:'تجربهٔ عملی دارم' })[profile.level] || 'سطح خود را انتخاب کنید';
    const nodes = target.slice(0, 6);
    container.innerHTML = `
      <div class="fa-dashboard journey-dashboard reference-home">
        <section class="reference-hero">
          <div class="reference-welcome"><span class="journey-kicker">FAM NETWORK ACADEMY</span><h1>${greeting.replace('سلام،','خوش آمدی،')}</h1><h2>مسیر یادگیری‌ات ادامه دارد</h2><p>هر روز یک قدم به شبکه‌کار حرفه‌ای شدن نزدیک‌تری.</p><div class="reference-pill"><span>${esc(chosen?.code || 'Curriculum 5.0')}</span><i></i>${esc(level)} <b>▥</b></div><div>${next ? '<button class="journey-primary" id="fa-continue">ادامه یادگیری <span>←</span></button>' : '<span>درس آمادهٔ جدیدی در این مسیر نیست.</span>'}</div><button class="journey-text-btn" data-journey-action="profile">تنظیم مسیر و برنامه ↗</button></div>
          <div class="reference-route-art" aria-hidden="true"><svg viewBox="0 0 520 450" preserveAspectRatio="xMidYMid meet"><defs><linearGradient id="route-light" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#6ea8ff"/><stop offset=".53" stop-color="#35c992"/><stop offset="1" stop-color="#6ea8ff"/></linearGradient><filter id="route-glow"><feGaussianBlur stdDeviation="7"/></filter></defs><path d="M460 435 C200 390 230 360 285 330 S345 290 285 260 S210 230 270 205 S310 175 255 155 S200 130 235 110 S255 85 220 68 S220 48 237 40" fill="none" stroke="url(#route-light)" stroke-width="15" opacity=".55" filter="url(#route-glow)"/><path d="M460 435 C200 390 230 360 285 330 S345 290 285 260 S210 230 270 205 S310 175 255 155 S200 130 235 110 S255 85 220 68 S220 48 237 40" fill="none" stroke="url(#route-light)" stroke-width="4"/><circle cx="285" cy="330" r="14" fill="#4ce0d7" opacity=".4"/><circle cx="285" cy="330" r="5" fill="#ddfffd"/><path d="M237 40V4l27 10-27 12" fill="#2f6fe4" stroke="#b7d4ff" stroke-width="2"/></svg></div>
          <aside class="reference-summary"><span class="journey-kicker">YOUR PROGRESS</span><h3>پیشرفت مسیر</h3><div class="reference-ring" style="--progress:${pct}%"><span><strong>${pct}٪</strong><small>تکمیل مسیر</small></span></div><p>${done} از ${target.length} درس تکمیل شده</p><button class="journey-link" data-journey-action="progress">مشاهده پیشرفت ←</button></aside>
        </section>
        <section class="reference-track"><div class="journey-heading"><div><h2>مسیر یادگیری</h2><p>${esc(chosen?.title || '')}</p></div><button class="journey-link" data-journey-path="${esc(chosen?.id || '')}">مشاهده کامل ←</button></div><div class="journey-track" aria-label="نمایی از مسیر یادگیری">${nodes.map((l,i) => `<button class="journey-node ${completed.has(l.id) ? 'is-done' : next?.id === l.id ? 'is-current' : ''}" data-journey-lesson="${esc(l.id)}"><span class="journey-node-dot">${completed.has(l.id) ? '✓' : lessonIcon(l.id)}</span><strong>${esc(l.title)}</strong><small>${completed.has(l.id) ? 'تکمیل‌شده' : next?.id === l.id ? 'گام پیشنهادی' : ready(l) ? 'آمادهٔ مطالعه' : 'پیش‌نیاز دارد'}</small></button>`).join('')}</div></section>
        <section class="reference-cards"><article class="reference-next"><span class="journey-kicker">UP NEXT</span><h2>درس بعدی</h2>${next ? `<div class="reference-next-content"><span class="reference-topic-icon">✥</span><div><h3>${esc(next.title)}</h3><p>درس را با توضیح، مثال و تمرین‌های مرتبط دنبال کن.</p><button class="journey-primary small" data-journey-lesson="${esc(next.id)}">شروع درس ←</button></div></div>` : '<p>درس آمادهٔ جدیدی در این مسیر نیست.</p>'}</article><article class="reference-plan"><span class="journey-kicker">YOUR ROUTINE</span><h2>برنامه مطالعه</h2><p>هدف روزانه</p><div class="reference-plan-number">${Number(profile.minutesPerDay) || 45} <small>دقیقه</small></div><p>${Number(profile.daysPerWeek) || 5} روز در هفته</p><button class="journey-link" data-journey-action="profile">ویرایش برنامه ←</button></article></section>
        <section class="journey-paths"><div class="journey-heading"><div><h2>مسیرهای آموزشی</h2><p>از مبانی شبکه تا مباحث پیشرفتهٔ سازمانی</p></div></div><div class="journey-path-grid">${paths.map((p,i) => { const prog=calcPathProgress(p,completed); return `<article class="journey-path"><span class="journey-path-mark">${i?'✳':'⌘'}</span><div><small>${esc(p.code)} · ${esc(p.level)}</small><h3>${esc(p.title)}</h3><p>${prog.done} از ${prog.total} درس تکمیل شده</p></div><button class="journey-link" data-open-path="${esc(p.id)}">نقشهٔ مسیر ←</button></article>`; }).join('')}</div></section>
      </div>`;
    container.querySelectorAll('[data-open-path], [data-journey-path]').forEach(btn => { btn.onclick = () => {
      const path = paths.find(p => p.id === (btn.dataset.openPath || btn.dataset.journeyPath));
      if (path) renderPathRoadmap(container, path, () => renderDashboard(container, catalog, onOpenLesson), onOpenLesson, catalog);
    }; });
    container.querySelectorAll('[data-journey-lesson]').forEach(btn => { btn.onclick = () => {
      const lesson = all.find(l => l.id === btn.dataset.journeyLesson);
      if (lesson?.blueprint) onOpenLesson(lesson.blueprint);
    }; });
    container.querySelectorAll('[data-journey-action]').forEach(btn => { btn.onclick = () => {
      if (btn.dataset.journeyAction === 'profile') window.FamJourney?.openProfile();
      else location.hash = '#/progress';
    }; });
    const continueBtn = container.querySelector('#fa-continue');
    if (continueBtn && next) continueBtn.onclick = () => onOpenLesson(next.blueprint);
  }
  function renderPathRoadmap(container, path, onBack, onOpenLesson, catalog) {
    const completed = getCompletedSet(), prog = calcPathProgress(path, completed);
    let index = 0;
    const all = catalog.paths.flatMap(p => (p.courses || []).flatMap(c => c.lessons || []));
    const lessons = (path.courses || []).flatMap(c => c.lessons || []);
    const assessed = new Set(window.FamAcademyBridge?.progress?.selfAssessed || []);
    const ready = l => (l.prerequisites || []).every(id => completed.has(id) || assessed.has(id));
    const next = lessons.find(l => !completed.has(l.id) && ready(l) && l.blueprint) || lessons.find(l => !completed.has(l.id)) || lessons[0];
    const cols = 4, stepX = 210, stepY = 150, rows = Math.ceil(lessons.length / cols), graphWidth = 850, graphHeight = Math.max(230, rows * stepY + 60);
    const point = i => ({ x: 110 + (i % cols) * stepX, y: 65 + Math.floor(i / cols) * stepY });
    const lines = lessons.flatMap((l,i) => (l.prerequisites || []).map(id => {
      const j = lessons.findIndex(item => item.id === id); if (j < 0) return '';
      const a = point(j), b = point(i), mid = (a.x + b.x) / 2;
      return `<path d="M ${a.x} ${a.y} C ${mid} ${a.y}, ${mid} ${b.y}, ${b.x} ${b.y}" class="${completed.has(id) && completed.has(l.id) ? 'edge-done' : ''}"/>`;
    })).join('');
    const graph = `<div class="reference-map-scroll"><div class="reference-map-canvas" style="width:${graphWidth}px;height:${graphHeight}px"><svg class="reference-map-lines" viewBox="0 0 ${graphWidth} ${graphHeight}" aria-hidden="true">${lines}</svg>${lessons.map((l,i) => { const p = point(i), done = completed.has(l.id); return `<button class="reference-map-node ${done?'is-done':l.id === next?.id?'is-current':''}" style="left:${p.x}px;top:${p.y}px" data-map-node="${esc(l.id)}" aria-label="${esc(l.title)}"><span class="reference-map-dot">${done?'✓':lessonIcon(l.id)}</span><strong>${esc(l.title)}</strong><small>${done?'تکمیل‌شده':ready(l)?'آمادهٔ مطالعه':'پیش‌نیاز دارد'}</small></button>`; }).join('')}</div></div>`;
    container.innerHTML = `
      <div class="fa-dashboard reference-roadmap">
        <button id="fa-catalog-back" class="fa-action fa-back-btn">← بازگشت به مسیرهای یادگیری</button>
        <div class="reference-roadmap-heading"><span class="journey-kicker">YOUR LEARNING JOURNEY · ${esc(path.code)}</span><h1>ماجراجویی یادگیری</h1><p>${esc(path.title)} · ${esc(path.description || '')}</p></div>
        <div class="reference-roadmap-layout"><section class="reference-map-main"><div class="reference-map-legend"><span><i class="done"></i> تکمیل‌شده</span><span><i class="current"></i> گام پیشنهادی</span><span><i></i> سایر درس‌ها</span></div>${graph}<div class="reference-map-summary"><span>◷ <b>${Number(path.estimatedHours)||0} ساعت</b><small>مدت تقریبی مسیر</small></span><span>⌁ <b>${prog.pct}٪</b><small>پیشرفت کل مسیر</small></span><span>◎ <b>${prog.done} از ${prog.total}</b><small>درس تکمیل‌شده</small></span></div></section><aside class="reference-map-detail" aria-live="polite"></aside></div>
        <h2 class="reference-course-title">همهٔ درس‌های این مسیر</h2>
        ${(path.courses||[]).map(course => {
          const cp = calcCourseProgress(course, completed);
          return `<section class="fa-course">
            <div class="fa-course-head"><h3>${esc(course.title)}</h3><small>${cp.done}/${cp.total} درس · ${cp.pct}٪ تکمیل</small></div>
            <div class="fa-lesson-list">
              ${(course.lessons||[]).map(lesson => {
                const isDone = completed.has(lesson.id), n = ++index;
                const prereq = Array.isArray(lesson.prerequisites) && lesson.prerequisites.length ? 'پیش‌نیاز: ' + lesson.prerequisites.length + ' مبحث' : 'بدون پیش‌نیاز';
                return `<div class="fa-lesson-row">
                  <span class="fa-lesson-num">${String(n).padStart(2,'0')}</span>
                  <div class="fa-lesson-info"><strong>${esc(lesson.title)}</strong><small>${esc(prereq)} · ${isDone ? '<span class="fa-complete">تکمیل‌شده</span>' : 'آماده یادگیری'}</small></div>
                  ${lesson.blueprint ? `<button class="fa-action primary" data-open-blueprint="${esc(lesson.blueprint)}">شروع درس ←</button>` : `<button class="fa-action" data-open-unready="${esc(lesson.id)}" data-course-title="${esc(course.title)}">مشاهده سرفصل</button>`}
                </div>`;
              }).join('')}
            </div>
          </section>`;
        }).join('')}
      </div>`;
    const detail = container.querySelector('.reference-map-detail');
    const showDetail = lesson => {
      if (!lesson) { detail.textContent = 'درسی در این مسیر ثبت نشده است.'; return; }
      const prerequisites = (lesson.prerequisites || []).map(id => all.find(l => l.id === id)).filter(Boolean);
      const done = completed.has(lesson.id);
      detail.innerHTML = `<span class="journey-kicker">LESSON DETAILS</span><div class="reference-detail-icon">✥</div><h2>${esc(lesson.title)}</h2><span class="reference-detail-status">${done ? 'تکمیل‌شده' : ready(lesson) ? 'آمادهٔ مطالعه' : 'پیش‌نیاز دارد'}</span><div class="fa-progress journey-meter"><span style="width:${done?100:0}%"></span></div><p>وضعیت ثبت‌شدهٔ درس</p><div class="reference-detail-block"><h3>درباره این درس</h3><p>${esc(lesson.summary || lesson.description || 'محتوای آموزشی و تمرین‌های مرتبط با این مبحث.')}</p></div><div class="reference-detail-block"><h3>پیش‌نیازها</h3>${prerequisites.length ? prerequisites.map(l => `<div class="reference-prereq"><span>${esc(l.title)}</span><b>${completed.has(l.id)?'✓':assessed.has(l.id)?'خودارزیابی':'○'}</b></div>`).join('') : '<p>پیش‌نیازی ثبت نشده است.</p>'}</div><button class="journey-primary reference-detail-open" type="button">${lesson.blueprint ? 'شروع درس ←' : 'مشاهده سرفصل ←'}</button>`;
      detail.querySelector('button').onclick = () => {
        if (lesson.blueprint) onOpenLesson(lesson.blueprint);
        else if (window.FamLessonEngine?.renderUnreadyLesson) window.FamLessonEngine.renderUnreadyLesson(container, {...lesson,track:path.code}, {catalog,onNavigate:onOpenLesson,onBackToCatalog:onBack});
      };
      container.querySelectorAll('[data-map-node]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.mapNode === lesson.id)));
    };
    container.querySelectorAll('[data-map-node]').forEach(button => button.onclick = () => showDetail(lessons.find(l => l.id === button.dataset.mapNode)));
    showDetail(next);
    container.querySelector('#fa-catalog-back').onclick = onBack;
    container.querySelectorAll('[data-open-blueprint]').forEach(btn => btn.onclick = () => onOpenLesson(btn.dataset.openBlueprint));
    container.querySelectorAll('[data-open-unready]').forEach(btn => {
      btn.onclick = () => {
        const lesson = (path.courses.find(c => c.title === btn.dataset.courseTitle)?.lessons || []).find(l => l.id === btn.dataset.openUnready);
        if (lesson && window.FamLessonEngine?.renderUnreadyLesson) {
          window.FamLessonEngine.renderUnreadyLesson(container, {...lesson, track:path.code, courseTitle:btn.dataset.courseTitle}, {
            catalog,
            onNavigate:onOpenLesson,
            onBackToCatalog:onBack
          });
        }
      };
    });
  }
  window.FamAcademyCatalog = { getCompletedSet, calcCourseProgress, calcPathProgress, renderDashboard, renderPathRoadmap };
})();