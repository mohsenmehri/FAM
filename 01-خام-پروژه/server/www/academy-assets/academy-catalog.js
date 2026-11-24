(() => {
  'use strict';
  const STORAGE_KEY = 'fam_academy_progress_v1';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  function getCompletedSet() {
    let local = [];
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const arr = raw ? JSON.parse(raw) : [];
      if (Array.isArray(arr)) local = arr;
    } catch {}
    const server = window.FamAcademyBridge?.progress?.completed;
    return new Set([...(Array.isArray(server) ? server : []), ...local]);
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
        <section class="reference-cards"><article class="reference-next"><span class="journey-kicker">UP NEXT</span><h2>درس بعدی</h2>${next ? `<div class="reference-next-content"><span class="reference-topic-icon">✥</span><div><h3>${esc(next.title)}</h3><p>درس را با توضیح، مثال و تمرین‌های مرتبط دنبال کن.</p><button class="journey-primary small" data-journey-lesson="${esc(next.id)}">شروع درس ←</button></div></div>` : '<p>درس آمادهٔ جدیدی در این مسیر نیست.</p>'}</article><article class="reference-plan"><span class="journey-kicker">YOUR ROUTINE</span><h2>برنامه استاندارد روزانه آکادمی</h2><p>پیشنهاد روزانه: ۱۲۰ دقیقه</p><div class="reference-plan-number">${Number(profile.minutesPerDay) || 120} <small>دقیقه</small></div><p>۲۰ مرور + ۳۵ مفهوم + ۵۰ لابراتوار + ۱۵ مستندسازی</p><div class="academy-inline-links"><button class="journey-link" data-journey-action="profile">ویرایش برنامه ←</button><button class="journey-link" data-open-tree="1">درخت جامع ۹ دانشکده ←</button><button class="journey-link" data-open-sim="1">شبیه‌ساز و آزمایشگاه IOS ←</button></div></article></section>
        <section class="journey-paths"><div class="journey-heading"><div><h2>مسیرهای آموزشی و درخت جامع آکادمی</h2><p>از مبانی شبکه و جلسهٔ اول ترم ۱ تا CCNA، CCNP، هشت تخصص، CCIE و CCDE</p></div><button type="button" class="fa-action primary" data-open-tree="1">باز کردن درخت جامع ۱۷بخشی ←</button></div><div class="journey-path-grid">${paths.map((p,i) => { const prog=calcPathProgress(p,completed); return `<article class="journey-path"><span class="journey-path-mark">${i?'✳':'⌘'}</span><div><small>${esc(p.code)} · ${esc(p.level)}</small><h3>${esc(p.title)}</h3><p>${prog.done} از ${prog.total} درس تکمیل شده</p></div><button class="journey-link" data-open-path="${esc(p.id)}">نقشهٔ مسیر ←</button></article>`; }).join('')}</div></section>
      </div>`;
    container.querySelectorAll('[data-open-tree]').forEach(btn => { btn.onclick = () => { location.hash = '#/tree'; }; });
    container.querySelectorAll('[data-open-sim]').forEach(btn => { btn.onclick = () => { location.hash = '#/simulators'; }; });
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

  const blueprintCache = new Map();
  async function loadAllBlueprints(catalog) {
    const entries = [];
    for (const path of (catalog?.paths || [])) {
      for (const course of (path.courses || [])) {
        for (const lesson of (course.lessons || [])) {
          if (lesson.blueprint) entries.push({ path, course, lesson });
        }
      }
    }
    return Promise.all(entries.map(async entry => {
      const url = entry.lesson.blueprint;
      if (!blueprintCache.has(url)) {
        try {
          const res = await fetch(url, { credentials: 'same-origin', cache: 'no-store' });
          blueprintCache.set(url, res.ok ? await res.json() : null);
        } catch {
          blueprintCache.set(url, null);
        }
      }
      return { ...entry, bp: blueprintCache.get(url) };
    }));
  }

  function decodeHtmlEntities(text) {
    const ta = document.createElement('textarea');
    ta.innerHTML = text;
    return ta.value;
  }

  function extractCommandsFromBlueprint(bp) {
    if (!bp) return [];
    const blocks = [];
    const chunks = [];
    if (Array.isArray(bp.sections)) {
      for (const s of bp.sections) if (typeof s?.html === 'string') chunks.push({ section: s.title || '', html: s.html });
    }
    if (bp.stages && typeof bp.stages === 'object') {
      for (const s of Object.values(bp.stages)) if (typeof s?.html === 'string') chunks.push({ section: s.title || 'آزمایشگاه', html: s.html });
    }
    const seen = new Set();
    for (const chunk of chunks) {
      const matches = chunk.html.matchAll(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi);
      for (const m of matches) {
        const clean = decodeHtmlEntities(m[1].replace(/<[^>]+>/g, '')).trim();
        if (!clean || seen.has(clean)) continue;
        seen.add(clean);
        blocks.push({ section: chunk.section, code: clean });
      }
    }
    return blocks;
  }

  function renderLessonsIndex(container, catalog, onOpenLesson, onBack) {
    const completed = getCompletedSet();
    const assessed = new Set(window.FamAcademyBridge?.progress?.selfAssessed || []);
    const paths = catalog?.paths || [];
    const allLessons = paths.flatMap(p => (p.courses || []).flatMap(c => (c.lessons || []).map(l => ({ ...l, path: p, course: c }))));
    const total = allLessons.length;
    const doneCount = allLessons.filter(l => completed.has(l.id)).length;
    const pct = total ? Math.round((doneCount / total) * 100) : 0;
    let activeFilter = 'all';
    let query = '';

    const ready = l => (l.prerequisites || []).every(id => completed.has(id) || assessed.has(id));
    container.innerHTML = `
      <div class="fa-dashboard academy-directory">
        <div class="academy-directory-head">
          <div>
            <span class="journey-kicker">CURRICULUM LIBRARY</span>
            <h1>فهرست کامل درس‌ها</h1>
            <p>${doneCount.toLocaleString('fa-IR')} از ${total.toLocaleString('fa-IR')} درس تکمیل‌شده (${pct.toLocaleString('fa-IR')}٪)</p>
          </div>
          ${onBack ? '<button type="button" class="fa-action" id="acad-lib-back">← بازگشت به خانه آکادمی</button>' : ''}
        </div>
        <div class="academy-directory-toolbar">
          <div class="segmented" role="tablist" aria-label="فیلتر وضعیت درس">
            <button type="button" class="active" data-lib-filter="all">همه (${total.toLocaleString('fa-IR')})</button>
            <button type="button" data-lib-filter="ready">آمادهٔ مطالعه</button>
            <button type="button" data-lib-filter="done">تکمیل‌شده (${doneCount.toLocaleString('fa-IR')})</button>
            <button type="button" data-lib-filter="locked">دارای پیش‌نیاز</button>
          </div>
          <label class="search-box">
            <input type="search" id="acad-lib-search" placeholder="فیلتر عنوان یا کلیدواژه درس…">
          </label>
        </div>
        <div id="acad-lib-list"></div>
      </div>`;
    if (onBack) container.querySelector('#acad-lib-back').onclick = onBack;
    const listEl = container.querySelector('#acad-lib-list');
    const searchEl = container.querySelector('#acad-lib-search');

    function draw() {
      const q = query.trim().toLowerCase();
      const blocks = [];
      for (const path of paths) {
        for (const course of (path.courses || [])) {
          const items = (course.lessons || []).filter(lesson => {
            const isDone = completed.has(lesson.id);
            const isReady = ready(lesson);
            if (activeFilter === 'done' && !isDone) return false;
            if (activeFilter === 'ready' && (isDone || !isReady)) return false;
            if (activeFilter === 'locked' && (isDone || isReady)) return false;
            if (!q) return true;
            const hay = [lesson.title, lesson.titleEn, lesson.summary, ...(lesson.keywords || []), course.title].filter(Boolean).join(' ').toLowerCase();
            return hay.includes(q);
          });
          if (!items.length) continue;
          blocks.push(`<section class="fa-course">
            <div class="fa-course-head"><h3>${esc(course.title)}</h3><small>${items.length.toLocaleString('fa-IR')} درس</small></div>
            <div class="fa-lesson-list">${items.map((lesson, idx) => {
              const isDone = completed.has(lesson.id);
              const isReady = ready(lesson);
              const badge = isDone ? '<span class="status status-done">تکمیل‌شده</span>' : isReady ? '<span class="status status-progress">آمادهٔ مطالعه</span>' : '<span class="status status-locked">پیش‌نیاز دارد</span>';
              const mins = lesson.estimatedMinutes ? `${Number(lesson.estimatedMinutes).toLocaleString('fa-IR')} دقیقه` : '';
              return `<div class="fa-lesson-row">
                <span class="fa-lesson-num">${String(idx + 1).padStart(2, '0')}</span>
                <div class="fa-lesson-info"><strong>${esc(lesson.title)}</strong><small>${esc(lesson.summary || '')}</small></div>
                ${badge}
                ${mins ? `<span class="tag">${mins}</span>` : ''}
                <button type="button" class="fa-action ${isDone ? '' : 'primary'}" data-lib-open="${esc(lesson.blueprint || '')}">${isDone ? 'مرور درس' : 'شروع درس'} ←</button>
              </div>`;
            }).join('')}</div>
          </section>`);
        }
      }
      listEl.innerHTML = blocks.length ? blocks.join('') : '<div class="empty-state"><h3>درسی با این فیلتر یافت نشد</h3><p>فیلتر یا عبارت جست‌وجو را تغییر دهید.</p></div>';
      listEl.querySelectorAll('[data-lib-open]').forEach(btn => {
        btn.onclick = () => { if (btn.dataset.libOpen) onOpenLesson(btn.dataset.libOpen); };
      });
    }
    container.querySelectorAll('[data-lib-filter]').forEach(btn => {
      btn.onclick = () => {
        activeFilter = btn.dataset.libFilter;
        container.querySelectorAll('[data-lib-filter]').forEach(b => b.classList.toggle('active', b === btn));
        draw();
      };
    });
    searchEl.addEventListener('input', () => { query = searchEl.value; draw(); });
    draw();
  }

  async function renderCommandCoverage(container, catalog, onOpenLesson, onBack) {
    container.innerHTML = '<div class="fa-loading">در حال گردآوری مرجع فرمان‌های Cisco IOS از درس‌ها…</div>';
    const loaded = await loadAllBlueprints(catalog);
    const items = [];
    for (const entry of loaded) {
      for (const cmd of extractCommandsFromBlueprint(entry.bp)) {
        items.push({ lesson: entry.lesson, course: entry.course, section: cmd.section, code: cmd.code });
      }
    }
    let query = '';
    container.innerHTML = `
      <div class="fa-dashboard academy-directory">
        <div class="academy-directory-head">
          <div>
            <span class="journey-kicker">CISCO IOS COMMAND REFERENCE</span>
            <h1>مرجع و پوشش فرمان‌های IOS</h1>
            <p>${items.length.toLocaleString('fa-IR')} بلوک فرمان عملی استخراج‌شده از ${loaded.length.toLocaleString('fa-IR')} درس آموزشی</p>
          </div>
          ${onBack ? '<button type="button" class="fa-action" id="acad-cov-back">← بازگشت به خانه آکادمی</button>' : ''}
        </div>
        <div class="academy-directory-toolbar">
          <label class="search-box">
            <input type="search" id="acad-cov-search" placeholder="جست‌وجوی فرمان یا مبحث (مثلاً ospf، vlan، show ip route، switchport)…">
          </label>
        </div>
        <div id="acad-cov-list" class="academy-cmd-grid"></div>
      </div>`;
    if (onBack) container.querySelector('#acad-cov-back').onclick = onBack;
    const listEl = container.querySelector('#acad-cov-list');
    const searchEl = container.querySelector('#acad-cov-search');

    function draw() {
      const q = query.trim().toLowerCase();
      const filtered = q ? items.filter(it => (it.code + ' ' + it.lesson.title + ' ' + it.section).toLowerCase().includes(q)) : items;
      if (!filtered.length) {
        listEl.innerHTML = '<div class="empty-state"><h3>فرمانی با این عبارت یافت نشد</h3><p>عبارت دیگری مانند interface یا show وارد کنید.</p></div>';
        return;
      }
      listEl.innerHTML = filtered.map((it, idx) => `
        <article class="fa-course academy-cmd-card">
          <div class="fa-course-head">
            <div><h3>${esc(it.lesson.title)}</h3><small>${esc(it.section || it.course.title)}</small></div>
            <div class="actions">
              <button type="button" class="fa-action" data-copy-cmd="${idx}">کپی فرمان</button>
              <button type="button" class="fa-action primary" data-open-cmd="${esc(it.lesson.blueprint)}">باز کردن درس ←</button>
            </div>
          </div>
          <pre class="cli-block" dir="ltr"><code>${esc(it.code)}</code></pre>
        </article>`).join('');
      listEl.querySelectorAll('[data-open-cmd]').forEach(btn => {
        btn.onclick = () => onOpenLesson(btn.dataset.openCmd);
      });
      listEl.querySelectorAll('[data-copy-cmd]').forEach(btn => {
        btn.onclick = async () => {
          const item = filtered[Number(btn.dataset.copyCmd)];
          if (!item) return;
          try { await navigator.clipboard.writeText(item.code); btn.textContent = 'کپی شد ✓'; setTimeout(() => { btn.textContent = 'کپی فرمان'; }, 1400); } catch {}
        };
      });
    }
    searchEl.addEventListener('input', () => { query = searchEl.value; draw(); });
    draw();
  }

  async function renderGlossaryDirectory(container, catalog, onOpenLesson, onBack) {
    container.innerHTML = '<div class="fa-loading">در حال گردآوری واژه‌نامهٔ تخصصی شبکه…</div>';
    const loaded = await loadAllBlueprints(catalog);
    const terms = new Map();
    for (const entry of loaded) {
      for (const g of (entry.bp?.glossary || [])) {
        if (!g?.term) continue;
        const key = g.term.toLowerCase();
        if (!terms.has(key)) terms.set(key, { ...g, lesson: entry.lesson });
      }
    }
    const sorted = [...terms.values()].sort((a, b) => a.term.localeCompare(b.term));
    let query = '';
    container.innerHTML = `
      <div class="fa-dashboard academy-directory">
        <div class="academy-directory-head">
          <div>
            <span class="journey-kicker">NETWORKING GLOSSARY</span>
            <h1>واژه‌نامهٔ جامع شبکه</h1>
            <p>${sorted.length.toLocaleString('fa-IR')} اصطلاح تخصصی از تمام درس‌های Curriculum 5.0</p>
          </div>
          ${onBack ? '<button type="button" class="fa-action" id="acad-glo-back">← بازگشت به خانه آکادمی</button>' : ''}
        </div>
        <div class="academy-directory-toolbar">
          <label class="search-box">
            <input type="search" id="acad-glo-search" placeholder="جست‌وجوی اصطلاح انگلیسی یا فارسی (مثلاً ARP، VLAN، Broadcast)…">
          </label>
        </div>
        <div id="acad-glo-list" class="academy-glossary-grid"></div>
      </div>`;
    if (onBack) container.querySelector('#acad-glo-back').onclick = onBack;
    const listEl = container.querySelector('#acad-glo-list');
    const searchEl = container.querySelector('#acad-glo-search');

    function draw() {
      const q = query.trim().toLowerCase();
      const filtered = q ? sorted.filter(g => [g.term, g.fa, g.simple, g.lesson?.title].filter(Boolean).join(' ').toLowerCase().includes(q)) : sorted;
      if (!filtered.length) {
        listEl.innerHTML = '<div class="empty-state"><h3>اصطلاحی یافت نشد</h3><p>واژهٔ دیگری را جست‌وجو کنید.</p></div>';
        return;
      }
      listEl.innerHTML = filtered.map(g => `
        <article class="card academy-glossary-card">
          <div class="academy-glossary-top">
            <strong dir="ltr">${esc(g.term)}</strong>
            <span class="tag">${esc(g.fa || '')}</span>
          </div>
          <p>${esc(g.simple || g.fa || '')}</p>
          ${g.lesson?.blueprint ? `<button type="button" class="journey-link" data-glo-open="${esc(g.lesson.blueprint)}">مطالعه در: ${esc(g.lesson.title)} ←</button>` : ''}
        </article>`).join('');
      listEl.querySelectorAll('[data-glo-open]').forEach(btn => {
        btn.onclick = () => onOpenLesson(btn.dataset.gloOpen);
      });
    }
    searchEl.addEventListener('input', () => { query = searchEl.value; draw(); });
    draw();
  }

  let treeCache = null;
  async function loadAcademyTree() {
    if (treeCache) return treeCache;
    const res = await fetch('/academy-assets/academy-curriculum-tree.json', { credentials: 'same-origin', cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    treeCache = await res.json();
    return treeCache;
  }

  async function renderAcademyTree(container, catalog, onOpenLesson, onBack) {
    container.innerHTML = '<div class="fa-loading">در حال بارگذاری درخت جامع آکادمی سیسکو…</div>';
    let tree;
    try {
      tree = await loadAcademyTree();
    } catch (err) {
      container.innerHTML = `<div class="empty-state"><h3>خطا در دریافت درخت آکادمی</h3><p>${esc(err.message)}</p></div>`;
      return;
    }

    const allLessons = (catalog?.paths || []).flatMap(p => (p.courses || []).flatMap(c => c.lessons || []));
    const findLesson = id => allLessons.find(l => l.id === id);
    const DAILY_KEY = 'fam_academy_daily_routine_v1';
    const todayKey = new Date().toISOString().slice(0, 10);
    let dailyState = {};
    try {
      const saved = JSON.parse(localStorage.getItem(DAILY_KEY) || '{}');
      if (saved.date === todayKey && saved.checks) dailyState = saved.checks;
    } catch {}

    let activeTab = 'faculties';
    let activeFaculty = 'f0';
    let activeTrack = tree.facultyFourSpecialties?.tracks?.[0]?.id || 'enterprise';

    const renderTabContent = () => {
      if (activeTab === 'faculties') {
        const f0 = tree.facultyZero;
        const f1 = tree.facultyOneCCNA;
        const f2 = tree.facultyTwoAdvanced;
        const f3 = tree.facultyThreeCCNP;
        const f4 = tree.facultyFourSpecialties;
        const f5 = tree.facultyExpertCCIE;
        const f6 = tree.facultyArchitectureCCDE;
        const fMap = {
          f0: `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f0.duration)}</span><h2>${esc(f0.title)}</h2></div>
              <p>${esc(f0.intro)}</p>
              <div class="lesson-callout"><strong>آزمون ورودی:</strong> ${esc(f0.entryExam.summary)}</div>
              <div class="table-wrap"><table><thead><tr><th>هفته</th><th>مباحث</th><th>خروجی</th></tr></thead><tbody>${f0.weeks.map(w => `<tr><td>هفته ${esc(w.week)}</td><td>${esc(w.topics)}</td><td>${esc(w.output)}</td></tr>`).join('')}</tbody></table></div>
              <div class="tree-cta-row"><button type="button" class="fa-action primary" data-tree-lesson="academy-stage-zero-01-osi-tcpip-fa">شروع جلسه اول: OSI و TCP/IP ←</button></div>
            </div>`,
          f1: `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f1.duration)} · ${esc(f1.examCode)}</span><h2>${esc(f1.title)}</h2></div>
              <div class="tree-domain-grid">${f1.domains.map(d => `<article class="tree-subcard"><h3>${esc(d.title)}</h3><ul>${d.topics.map(t => `<li>${esc(t)}</li>`).join('')}</ul></article>`).join('')}</div>
              <h3 class="tree-subhead">۲۵ آزمایشگاه الزامی CCNA</h3>
              <div class="tree-pill-grid">${f1.labs.map(l => `<span class="tree-pill">${esc(l)}</span>`).join('')}</div>
              <div class="tree-capstone">
                <h3>${esc(f1.capstone.title)}</h3>
                <ul>${f1.capstone.requirements.map(r => `<li>${esc(r)}</li>`).join('')}</ul>
                <p><strong>شرط عبور:</strong> ${f1.capstone.passCriteria.map(esc).join(' | ')}</p>
              </div>
            </div>`,
          f2: `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f2.duration)}</span><h2>${esc(f2.title)}</h2></div>
              <p>${esc(f2.goal)}</p>
              <div class="tree-domain-grid">${f2.courses.map(c => `<article class="tree-subcard"><h3>${esc(c.title)}</h3><ul>${c.topics.map(t => `<li>${esc(t)}</li>`).join('')}</ul></article>`).join('')}</div>
              <h3 class="tree-subhead">۱۲ آزمایشگاه تخصصی دانشکده ۲</h3>
              <div class="tree-pill-grid">${f2.labs.map((l, i) => `<span class="tree-pill">${i + 1}. ${esc(l)}</span>`).join('')}</div>
              <div class="tree-capstone"><h3>پروژه نهایی دانشکده ۲</h3><p>${esc(f2.capstone)}</p></div>
            </div>`,
          f3: `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f3.duration)} · ${esc(f3.coreExam)}</span><h2>${esc(f3.title)}</h2></div>
              <h3 class="tree-subhead">آزمون اصلی: ${esc(f3.coreExam)}</h3>
              <div class="table-wrap"><table><thead><tr><th>حوزه</th><th>مباحث</th></tr></thead><tbody>${f3.encorDomains.map(d => `<tr><td><strong>${esc(d.domain)}</strong></td><td>${esc(d.topics)}</td></tr>`).join('')}</tbody></table></div>
              <h3 class="tree-subhead">آزمون‌های تخصصی انتخابی (Concentrations)</h3>
              <div class="table-wrap"><table><thead><tr><th>کد آزمون</th><th>تخصص</th><th>وضعیت پیشنهاد</th></tr></thead><tbody>${f3.concentrations.map(c => `<tr><td dir="ltr"><code>${esc(c.code)}</code></td><td>${esc(c.focus)}</td><td>${c.recommended ? '<span class="status status-done">پیشنهاد اول آکادمی</span>' : 'انتخابی'}</td></tr>`).join('')}</tbody></table></div>
              <div class="lesson-callout"><strong>پیشنهاد آکادمی:</strong> ${esc(f3.recommendation)}</div>
              <div class="tree-capstone"><h3>پروژه CCNP Enterprise</h3><p>${esc(f3.capstone)}</p></div>
            </div>`,
          f4: (() => {
            const cur = f4.tracks.find(t => t.id === activeTrack) || f4.tracks[0];
            return `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f4.duration)}</span><h2>${esc(f4.title)}</h2></div>
              <div class="tree-track-tabs">${f4.tracks.map(t => `<button type="button" class="tree-track-btn ${t.id === cur.id ? 'active' : ''}" data-select-track="${esc(t.id)}">${esc(t.number)} ${esc(t.title.replace('دانشکده ', ''))}</button>`).join('')}</div>
              <article class="tree-track-panel">
                <div class="tree-detail-head"><span class="tag" dir="ltr">${esc(cur.certs)}</span><h3>${esc(cur.number)} ${esc(cur.title)} — ${esc(cur.subtitle)}</h3></div>
                <div class="tree-two-col">
                  <div class="tree-subcard"><h4>فهرست دروس</h4><ul>${cur.courses.map(c => `<li>${esc(c)}</li>`).join('')}</ul></div>
                  <div class="tree-subcard"><h4>آزمایشگاه‌ها</h4><ul>${cur.labs.map(l => `<li>${esc(l)}</li>`).join('')}</ul></div>
                </div>
                <div class="tree-capstone"><h4>پروژه نهایی شاخه</h4><p>${esc(cur.project)}</p></div>
              </article>
            </div>`;
          })(),
          f5: `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f5.duration)}</span><h2>${esc(f5.title)}</h2></div>
              <p>${esc(f5.description)}</p>
              <div class="table-wrap"><table><thead><tr><th>مسیر CCIE</th><th>آزمون Core</th><th>آزمون عملی</th></tr></thead><tbody>${f5.tracks.map(t => `<tr><td><strong>${esc(t.track)}</strong></td><td dir="ltr"><code>${esc(t.core)}</code></td><td>${esc(t.lab)}</td></tr>`).join('')}</tbody></table></div>
              <h3 class="tree-subhead">استاندارد آمادگی CCIE</h3>
              <ul>${f5.standards.map(s => `<li>${esc(s)}</li>`).join('')}</ul>
            </div>`,
          f6: `
            <div class="tree-detail-card">
              <div class="tree-detail-head"><span class="tag">${esc(f6.duration)}</span><h2>${esc(f6.title)}</h2></div>
              <p><strong>مسیر مدرک:</strong> ${esc(f6.exam)}</p>
              <h3 class="tree-subhead">۲۰ سرفصل تخصصی CCDE</h3>
              <div class="tree-pill-grid">${f6.topics.map(t => `<span class="tree-pill">${esc(t)}</span>`).join('')}</div>
              <div class="tree-capstone"><h3>پروژه پایانی معماری</h3><p>${esc(f6.capstone)}</p></div>
            </div>`
        };

        return `
          <section class="tree-overview-strip">
            <div class="tree-stat"><span>ساعت روزانه</span><strong>${esc(tree.overview.dailyHours)}</strong></div>
            <div class="tree-stat"><span>ساعت هفتگی</span><strong>${esc(tree.overview.weeklyHours)}</strong></div>
            <div class="tree-stat"><span>زبان آموزش</span><strong>${esc(tree.overview.language)}</strong></div>
            <div class="tree-stat"><span>روش آموزش</span><strong>${esc(tree.overview.method)}</strong></div>
            <div class="tree-stat"><span>چشم‌انداز جامع</span><strong>۶ تا ۸ سال</strong></div>
          </section>
          <section class="tree-outputs-card">
            <h3>۴ خروجی الزامی هر مبحث در آکادمی</h3>
            <div class="tree-four-grid">${tree.fourOutputs.map(o => `<article class="tree-subcard"><span class="tag">خروجی ${o.id}</span><h4>${esc(o.title)}</h4><p>${esc(o.desc)}</p></article>`).join('')}</div>
          </section>
          <section class="tree-faculties-wrap">
            <h3>جدول کلان دانشکده‌ها (برای مشاهده جزئیات کامل، روی هر دانشکده بزنید)</h3>
            <div class="tree-faculty-tabs">${tree.facultiesSummary.map(f => `<button type="button" class="tree-faculty-btn ${activeFaculty === f.id ? 'active' : ''}" data-select-faculty="${esc(f.id)}"><small>دانشکده ${esc(f.number)} · ${esc(f.duration)}</small><strong>${esc(f.title)}</strong></button>`).join('')}</div>
            ${fMap[activeFaculty] || fMap.f0}
          </section>`;
      }

      if (activeTab === 'term1') {
        const t1 = tree.termOne30DayPlan;
        return `
          <section class="tree-detail-card">
            <div class="tree-detail-head"><span class="tag">۳۰ روز / ۳۰ جلسه</span><h2>${esc(t1.title)}</h2></div>
            <p>${esc(tree.facultyZero.intro)} — <strong>${esc(tree.facultyZero.entryExam.summary)}</strong></p>
            <div class="tree-cta-row"><button type="button" class="fa-action primary" data-tree-lesson="${esc(t1.firstSessionId)}">شروع جلسه اول: OSI و TCP/IP ←</button></div>
            <div class="tree-domain-grid">${t1.weeks.map(w => `
              <article class="tree-subcard">
                <h3>${esc(w.title)}</h3>
                <ol class="tree-session-list">${w.sessions.map(s => {
                  const found = s.lessonId ? findLesson(s.lessonId) : null;
                  return `<li><span>${esc(s.title)}</span>${found?.blueprint ? `<button type="button" class="journey-link" data-tree-lesson="${esc(found.id)}">باز کردن درس ←</button>` : '<small class="muted">برنامه ترم ۱</small>'}</li>`;
                }).join('')}</ol>
              </article>`).join('')}</div>
          </section>`;
      }

      if (activeTab === 'routine') {
        const ds = tree.dailySchedule;
        const doneMins = ds.blocks.filter(b => dailyState[b.id]).reduce((sum, b) => sum + b.minutes, 0);
        return `
          <section class="tree-detail-card">
            <div class="tree-detail-head"><span class="tag">۱۴ ساعت در هفته · ${ds.totalMinutes} دقیقه در روز</span><h2>برنامه زمان‌بندی روزانه و هفتگی</h2></div>
            <div class="lesson-callout"><strong>پیشرفت امروز (${todayKey}):</strong> ${doneMins} از ${ds.totalMinutes} دقیقه تکمیل شده است.</div>
            <div class="tree-four-grid">${ds.blocks.map(b => `
              <label class="tree-subcard tree-routine-check">
                <input type="checkbox" data-daily-block="${esc(b.id)}" ${dailyState[b.id] ? 'checked' : ''}/>
                <div>
                  <span class="tag">${b.minutes} دقیقه</span>
                  <h4>${esc(b.title)}</h4>
                  <p>${esc(b.desc)}</p>
                </div>
              </label>`).join('')}</div>
            <h3 class="tree-subhead">برنامهٔ هفتگی آکادمی (شنبه تا جمعه)</h3>
            <div class="table-wrap"><table><thead><tr><th>روز</th><th>برنامهٔ اجرایی</th></tr></thead><tbody>${ds.weekly.map(w => `<tr><td><strong>${esc(w.day)}</strong></td><td>${esc(w.activity)}</td></tr>`).join('')}</tbody></table></div>
            <h3 class="tree-subhead">استاندارد ۱۱مرحله‌ای تدریس هر جلسه</h3>
            <div class="tree-pill-grid">${tree.sessionStandard.map(st => `<span class="tree-pill">${esc(st)}</span>`).join('')}</div>
          </section>`;
      }

      if (activeTab === 'labs') {
        const li = tree.labInfrastructure;
        const ev = tree.evaluation;
        return `
          <section class="tree-detail-card">
            <h2>زیرساخت آزمایشگاهی و استاندارد ارزیابی</h2>
            <div class="lesson-callout"><strong>قانون طلایی آکادمی:</strong> ${esc(li.rule)}</div>
            <h3 class="tree-subhead">ابزارهای آزمایشگاهی (۱۱ ابزار)</h3>
            <div class="tree-four-grid">${li.tools.map(t => `<article class="tree-subcard"><strong dir="ltr">${esc(t.name)}</strong><p>${esc(t.use)}</p></article>`).join('')}</div>
            <h3 class="tree-subhead">استاندارد ارزیابی (حداقل نمرهٔ قبولی: ${ev.passingScore} از ۱۰۰)</h3>
            <div class="table-wrap"><table><thead><tr><th>بخش ارزیابی</th><th>سهم نمره</th></tr></thead><tbody>${ev.weights.map(w => `<tr><td>${esc(w.name)}</td><td><strong>${esc(w.weight)}</strong></td></tr>`).join('')}</tbody></table></div>
            <p class="muted">${esc(ev.note)}</p>
            <h3 class="tree-subhead">معیار نهایی موفقیت و فارغ‌التحصیلی</h3>
            <ul>${tree.graduationCriteria.map(g => `<li>${esc(g)}</li>`).join('')}</ul>
          </section>`;
      }

      const res = tree.resources;
      return `
        <section class="tree-detail-card">
          <h2>برنامهٔ زمانی جامع ۸ ساله و کتابخانهٔ منابع رسمی</h2>
          <div class="table-wrap"><table><thead><tr><th>سال</th><th>هدف اصلی</th></tr></thead><tbody>${tree.eightYearTimeline.map(y => `<tr><td><strong>${esc(y.year)}</strong></td><td>${esc(y.goal)}</td></tr>`).join('')}</tbody></table></div>
          <div class="lesson-callout"><strong>نکتهٔ مهم نسخه‌های CCNA:</strong> ${esc(res.ccnaVersionNote)}</div>
          <h3 class="tree-subhead">منابع رسمی سیسکو</h3>
          <div class="tree-four-grid">${res.items.map(r => `<article class="tree-subcard"><h4>${esc(r.name)}</h4><p>${esc(r.desc)}</p><a class="journey-link" href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">مشاهده منبع ↗</a></article>`).join('')}</div>
        </section>`;
    };

    const draw = () => {
      container.innerHTML = `
        <div class="fa-dashboard academy-tree-page">
          <div class="academy-directory-head">
            <div>
              <span class="journey-kicker">MASTER CURRICULUM TREE</span>
              <h1>${esc(tree.title)}</h1>
              <p>${esc(tree.subtitle)} — ${esc(tree.philosophy)}</p>
            </div>
            ${onBack ? '<button type="button" class="fa-action" id="acad-tree-back">← بازگشت به خانه آکادمی</button>' : ''}
          </div>
          <nav class="segmented tree-main-tabs" role="tablist" aria-label="بخش‌های درخت آکادمی">
            <button type="button" class="${activeTab === 'faculties' ? 'active' : ''}" data-tree-tab="faculties">۹ دانشکده و ۸ تخصص</button>
            <button type="button" class="${activeTab === 'term1' ? 'active' : ''}" data-tree-tab="term1">ترم اول ۳۰ روزه</button>
            <button type="button" class="${activeTab === 'routine' ? 'active' : ''}" data-tree-tab="routine">برنامه ۲ ساعته و ۱۱ گام</button>
            <button type="button" class="${activeTab === 'labs' ? 'active' : ''}" data-tree-tab="labs">لابراتوار و ارزیابی</button>
            <button type="button" class="${activeTab === 'roadmap8y' ? 'active' : ''}" data-tree-tab="roadmap8y">نقشه ۸ ساله و منابع</button>
          </nav>
          <div class="tree-stage">${renderTabContent()}</div>
        </div>`;

      if (onBack) container.querySelector('#acad-tree-back').onclick = onBack;
      container.querySelectorAll('[data-tree-tab]').forEach(btn => {
        btn.onclick = () => { activeTab = btn.dataset.treeTab; draw(); };
      });
      container.querySelectorAll('[data-select-faculty]').forEach(btn => {
        btn.onclick = () => { activeFaculty = btn.dataset.selectFaculty; draw(); };
      });
      container.querySelectorAll('[data-select-track]').forEach(btn => {
        btn.onclick = () => { activeTrack = btn.dataset.selectTrack; draw(); };
      });
      container.querySelectorAll('[data-tree-lesson]').forEach(btn => {
        btn.onclick = () => {
          const lesson = findLesson(btn.dataset.treeLesson);
          if (lesson?.blueprint) onOpenLesson(lesson.blueprint);
        };
      });
      container.querySelectorAll('[data-daily-block]').forEach(chk => {
        chk.onchange = () => {
          dailyState[chk.dataset.dailyBlock] = chk.checked;
          try { localStorage.setItem(DAILY_KEY, JSON.stringify({ date: todayKey, checks: dailyState })); } catch {}
          draw();
        };
      });
    };
    draw();
  }

  window.FamAcademyCatalog = {
    getCompletedSet,
    calcCourseProgress,
    calcPathProgress,
    renderDashboard,
    renderPathRoadmap,
    renderLessonsIndex,
    renderCommandCoverage,
    renderGlossaryDirectory,
    renderAcademyTree
  };
})();