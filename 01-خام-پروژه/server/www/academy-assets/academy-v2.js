/* FAM Academy v2 — vanilla SPA inside the FAM Academy shell. Data comes only from versioned v1 APIs. */
(function () {
  'use strict';
  var boot = window.FAM_ACADEMY_BOOTSTRAP || {};
  var Engine = window.FAMAcademyEngine;
  var root = document.getElementById('fam-app');
  var STORAGE_KEY = 'famAcademyV2.progress.v1';
  var API = {
    catalog: '/api/academy/v2/catalog',
    exercises: '/api/academy/v2/exercises',
    health: '/api/academy/v2/health',
    lesson: function (id) { return '/api/academy/v2/lesson/' + encodeURIComponent(id); },
    simulation: function (id) { return '/api/academy/v2/simulation/' + encodeURIComponent(id); },
    lab: function (id) { return '/api/academy/v2/lab/' + encodeURIComponent(id); },
    quiz: function (id) { return '/api/academy/v2/quiz/' + encodeURIComponent(id); }
  };
  var App = {
    catalog: null, exercises: [], lessons: new Map(), simulations: new Map(), labs: new Map(),
    progress: null, activeRoute: '#/dashboard', currentLessonId: null, currentLesson: null, lessonStage: 0,
    currentSim: null, simResult: null, simActive: 0, simTimer: null,
    currentLab: null, labState: null, labOutput: []
  };
  var STAGES = [
    { key: 'concept', title: '۱. مفهوم' },
    { key: 'visual', title: '۲. دیاگرام و مثال' },
    { key: 'practice', title: '۳. دستورات و عیبیابی' },
    { key: 'interactive', title: '۴. تمرین و شبیهسازی' },
    { key: 'assessment', title: '۵. ارزیابی' }
  ];

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function defaultProgress() {
    return { version: 1, completedLessons: [], quizScores: {}, labSteps: {}, simRuns: {}, lastLessonId: null, updatedAt: null };
  }
  function mergeProgress(base, extra) {
    if (!extra || typeof extra !== 'object') return base;
    return {
      version: 1,
      completedLessons: Array.isArray(extra.completedLessons) ? extra.completedLessons.filter(function (x) { return typeof x === 'string'; }) : base.completedLessons,
      quizScores: extra.quizScores && typeof extra.quizScores === 'object' ? extra.quizScores : base.quizScores,
      labSteps: extra.labSteps && typeof extra.labSteps === 'object' ? extra.labSteps : base.labSteps,
      simRuns: extra.simRuns && typeof extra.simRuns === 'object' ? extra.simRuns : base.simRuns,
      lastLessonId: typeof extra.lastLessonId === 'string' ? extra.lastLessonId : base.lastLessonId,
      updatedAt: extra.updatedAt || base.updatedAt
    };
  }
  function readProgress() {
    var base = defaultProgress();
    try {
      var server = boot.progress && boot.progress[STORAGE_KEY];
      if (typeof server === 'string') return mergeProgress(base, JSON.parse(server));
    } catch (_) {}
    try {
      var local = localStorage.getItem(STORAGE_KEY);
      if (local) return mergeProgress(base, JSON.parse(local));
    } catch (_) {}
    return base;
  }
  function saveProgress(p) {
    p.updatedAt = new Date().toISOString();
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(p)); } catch (_) {}
    if (!boot.csrf || boot.previewMode) return;
    try {
      fetch('/api/academy/progress', {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-FAM-CSRF': boot.csrf },
        body: JSON.stringify({ changes: { 'famAcademyV2.progress.v1': JSON.stringify(p) } })
      }).catch(function () {});
    } catch (_) {}
  }
  function apiGet(path) {
    return fetch(path, { credentials: 'same-origin', cache: 'no-store', headers: { 'Accept': 'application/json' } }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + path);
      return r.json();
    });
  }
  function apiPost(path, body) {
    var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    if (boot.csrf) headers['X-FAM-CSRF'] = boot.csrf;
    return fetch(path, { method: 'POST', credentials: 'same-origin', cache: 'no-store', headers: headers, body: JSON.stringify(body) }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + path);
      return r.json();
    });
  }
  function setView(html) {
    var view = document.getElementById('view');
    if (view) view.innerHTML = html;
  }
  function progressStats() {
    var totalLessons = App.catalog ? App.catalog.lessons.length : 0;
    var done = App.progress.completedLessons.length;
    var quizzes = Object.keys(App.progress.quizScores).length;
    var labSteps = Object.keys(App.progress.labSteps).reduce(function (n, k) { return n + (Array.isArray(App.progress.labSteps[k]) ? App.progress.labSteps[k].length : 0); }, 0);
    var simRuns = Object.keys(App.progress.simRuns).reduce(function (n, k) { return n + (Number(App.progress.simRuns[k]) || 0); }, 0);
    return { totalLessons: totalLessons, done: done, percent: totalLessons ? Math.round((done * 100) / totalLessons) : 0, quizzes: quizzes, labSteps: labSteps, simRuns: simRuns };
  }
  function pathById(id) { return App.catalog.paths.find(function (p) { return p.id === id; }); }
  function courseById(id) { return App.catalog.courses.find(function (c) { return c.id === id; }); }
  function lessonById(id) { return App.catalog.lessons.find(function (l) { return l.id === id; }); }
  function simById(id) { return App.catalog.simulations.find(function (s) { return s.id === id; }); }
  function labById(id) { return App.catalog.labs.find(function (l) { return l.id === id; }); }
  function courseProgress(course) {
    var ids = course.chapters.reduce(function (acc, c) { return acc.concat(c.lessonIds || []); }, []);
    var done = ids.filter(function (id) { return App.progress.completedLessons.indexOf(id) !== -1; }).length;
    return { total: ids.length, done: done, percent: ids.length ? Math.round((done * 100) / ids.length) : 0 };
  }
  function statusBadge(status) {
    return status === 'live' ? '<span class="badge live">آماده</span>' : '<span class="badge planned">P1 · نقشه راه</span>';
  }
  function footerHtml() {
    return '<div class="footer"><span>FAM Academy v2 · نسخه عمودی P0 · محتوای نسخهدار 2026.11.24-p0</span><span>خروجی دستورات و شبیهسازها: Sample / Simulated — Internal Simulator؛ هیچ اتصال به تجهیز واقعی برقرار نیست.</span></div>';
  }
  function heroVisual() {
    return '<svg viewBox="0 0 460 260" role="img" aria-label="نمای انتزاعی مسیر بسته در شبکه" dir="ltr">' +
      '<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>' +
      '<rect x="1" y="1" width="458" height="258" rx="20" fill="#0b1220" stroke="#263653"/>' +
      '<path d="M55 190 C 150 90, 300 90, 410 60" stroke="url(#g)" stroke-width="3" fill="none" stroke-dasharray="8 8"/>' +
      '<path d="M55 190 C 160 210, 300 190, 410 130" stroke="#22d3ee" stroke-width="2" fill="none" opacity=".7"/>' +
      '<g fill="#17233c" stroke="#3b4d72"><circle cx="55" cy="190" r="26"/><circle cx="190" cy="120" r="22"/><circle cx="310" cy="110" r="22"/><circle cx="410" cy="60" r="26"/><circle cx="410" cy="130" r="22"/></g>' +
      '<g fill="#e8eefb" font-size="11" text-anchor="middle" font-family="Segoe UI, sans-serif"><text x="55" y="194">Client</text><text x="190" y="124">Switch</text><text x="310" y="114">Router</text><text x="410" y="64">Server</text><text x="410" y="134">Lab</text></g>' +
      '<g fill="#94a6c7" font-size="10" text-anchor="middle" font-family="monospace"><text x="55" y="232">192.0.2.10</text><text x="410" y="232">203.0.113.10</text></g>' +
      '</svg>';
  }
  function sideLink(route, label, hint, glyph) {
    return '<a class="side-link" href="' + esc(route) + '" data-route="' + esc(route) + '">' +
      '<span class="side-icon">' + esc(glyph) + '</span>' +
      '<span class="side-copy"><span class="side-label">' + esc(label) + '</span><span class="side-hint">' + esc(hint) + '</span></span>' +
    '</a>';
  }
  function bottomLink(route, label, glyph) {
    return '<a href="' + esc(route) + '" data-route="' + esc(route) + '"><span>' + esc(glyph) + '</span><span>' + esc(label) + '</span></a>';
  }
  function syncTheme() {
    var html = document.documentElement || { dataset: {} };
    var light = html.dataset.theme === 'light';
    var button = document.querySelector('.theme-toggle');
    if (button) {
      if (button.textContent !== undefined || 'textContent' in button) button.textContent = light ? '☾' : '☀';
      if (button.setAttribute) {
        button.setAttribute('aria-label', light ? 'تغییر به تم تیره' : 'تغییر به تم روشن');
        button.setAttribute('title', light ? 'تغییر به تم تیره' : 'تغییر به تم روشن');
        button.setAttribute('aria-pressed', String(light));
      }
    }
  }
  function renderShell() {
    var s = progressStats();
    var user = boot.userName || (boot.user && (boot.user.name || boot.user.username)) || 'میهمان ارائه';
    var firstLesson = App.catalog.lessons[0] ? App.catalog.lessons[0].id : 'l01-osi-tcpip-encapsulation';
    var firstSim = App.catalog.simulations[0] ? App.catalog.simulations[0].id : 'sim-arp-discovery';
    var firstLab = App.catalog.labs[0] ? App.catalog.labs[0].id : 'lab-vlan-trunk';
    var live = App.catalog.courses.filter(function (c) { return c.status === 'live'; }).length;
    if (document.body && document.body.classList) document.body.classList.add('fam-academy-v2');
    root.className = 'page fam-academy-v2-root';
    root.innerHTML =
      '<div class="app-shell" id="academy-shell">' +
        '<aside class="sidebar" id="academy-sidebar">' +
          '<a class="brand" href="#/dashboard" data-route="#/dashboard" aria-label="آکادمی فام — خانه">' +
            '<span class="brand-logo">FA</span><span class="brand-copy"><b>FAM Academy</b><small>NETWORK ENGINEERING SCHOOL</small></span>' +
          '</a>' +
          '<nav class="side-nav" aria-label="ناوبری اصلی آکادمی">' +
            sideLink('#/dashboard', 'خانه', 'نمای کلی و شروع یادگیری', '⌂') +
            sideLink('#/paths', 'مسیرها', '۲۳ مسیر آموزشی', '◈') +
            sideLink('#/progress', 'پیشرفت من', 'درسها، آزمونها و لابها', '◉') +
            sideLink('#/sim/' + firstSim, 'شبیهسازها', 'ARP، VLAN و OSPF', '▤') +
            sideLink('#/lab/' + firstLab, 'آزمایشگاهها', 'Safe Internal Simulator', '▣') +
            sideLink('#/quiz/' + firstLesson, 'آزمون', 'ارزیابی و نتیجه', '✓') +
          '</nav>' +
          '<div class="side-path">' +
            '<div class="side-path-head">نسخه محتوا</div>' +
            '<div class="side-path-name">FAM Academy v2</div>' +
            '<div class="meter"><i></i></div>' +
            '<div class="side-path-meta">' + live + ' دوره متصل · ' + App.catalog.lessons.length + ' درس کامل</div>' +
          '</div>' +
          '<div class="side-foot"><span class="live-dot"></span><span>محتوای نسخهدار 2026.11.24-p0</span></div>' +
        '</aside>' +
        '<div class="app-main">' +
          '<header class="topbar">' +
            '<button class="icon-btn academy-menu-toggle" type="button" data-action="toggle-menu" aria-controls="academy-sidebar" aria-expanded="true" aria-label="باز و بسته کردن منو">☰</button>' +
            '<div class="academy-top-title"><b>آکادمی فام</b><small>FAM ACADEMY · LEARNING</small></div>' +
            '<nav class="crumbs academy-route-crumbs" id="academy-crumbs" aria-label="مسیر صفحه"><span class="crumb current">داشبورد</span></nav>' +
            '<div class="top-actions">' +
              '<button class="nav-btn" data-route="#/dashboard">داشبورد</button>' +
              '<button class="nav-btn" data-route="#/paths">مسیرها</button>' +
              '<button class="nav-btn" data-route="#/progress">پیشرفت</button>' +
              '<button class="icon-btn theme-toggle" type="button" data-action="toggle-theme" aria-label="تغییر تم">☀</button>' +
              '<a class="academy-section-switch" href="/app">بازگشت به FAM</a>' +
              '<span class="user-chip progress-pill" id="academy-progress-pill"><b>' + s.percent + '%</b> تکمیل · ' + esc(user) + '</span>' +
            '</div>' +
          '</header>' +
          '<section class="academy-section-head">' +
            '<div class="academy-section-heading"><span class="academy-head-mark">FAM</span><div><h2>آکادمی مهندسی شبکه</h2><div class="academy-section-sub">FAM ACADEMY · NETWORK ENGINEERING</div></div></div>' +
            '<div class="academy-section-actions">' +
              '<a class="academy-section-switch" href="/app#/panel">پایگاه داده ←</a>' +
              '<a class="academy-section-switch" href="/app#/equipment/inventory">مدیریت تجهیزات ←</a>' +
              '<a class="academy-section-switch" href="/app">انتخاب بخش</a>' +
            '</div>' +
          '</section>' +
          '<main class="view" id="view"></main>' +
          '<nav class="bottom-nav" aria-label="ناوبری موبایل">' +
            bottomLink('#/dashboard', 'خانه', '⌂') +
            bottomLink('#/paths', 'مسیرها', '◈') +
            bottomLink('#/progress', 'پیشرفت', '◉') +
            bottomLink('#/sim/' + firstSim, 'شبیهساز', '▤') +
            bottomLink('#/quiz/' + firstLesson, 'آزمون', '✓') +
          '</nav>' +
        '</div>' +
      '</div>';
  }
  function setActiveNav(hash) {
    var base = hash.split('/').slice(0, 2).join('/');
    var key = base.replace('#/', '') || 'dashboard';
    var labels = { dashboard: 'داشبورد', paths: 'مسیرها', progress: 'پیشرفت', course: 'دوره', lesson: 'درس', sim: 'شبیهساز', lab: 'آزمایشگاه', quiz: 'آزمون' };
    var crumb = labels[key] || 'آکادمی';
    var detail = hash === '' || hash === '#/' || hash.indexOf('#/course/') === 0 || hash.indexOf('#/lesson/') === 0 || hash.indexOf('#/sim/') === 0 || hash.indexOf('#/lab/') === 0 || hash.indexOf('#/quiz/') === 0;
    document.querySelectorAll('.nav-btn, .side-link, .bottom-nav a').forEach(function (b) {
      var r = b.dataset.route || '';
      var rBase = r.split('/').slice(0, 2).join('/');
      var active = rBase === base || (rBase === '#/dashboard' && detail);
      b.classList.toggle('active', active);
      if (b.setAttribute && b.classList.contains('side-link')) {
        if (active) b.setAttribute('aria-current', 'page');
        else if (b.removeAttribute) b.removeAttribute('aria-current');
      }
    });
    var crumbs = document.getElementById('academy-crumbs');
    if (crumbs) crumbs.innerHTML = '<span class="crumb current">' + esc(crumb) + '</span>';
    var pill = document.getElementById('academy-progress-pill');
    if (pill) {
      var s = progressStats();
      var user = boot.userName || (boot.user && (boot.user.name || boot.user.username)) || 'میهمان ارائه';
      pill.innerHTML = '<b>' + s.percent + '%</b> تکمیل · ' + esc(user);
    }
    document.title = crumb + ' — FAM Academy';
  }
  function clearSimTimer() { if (App.simTimer) { clearInterval(App.simTimer); App.simTimer = null; } }
  function renderError(message) {
    setView('<div class="error-box"><h2>خطا در بارگذاری</h2><p>' + esc(message) + '</p><button class="btn" data-route="#/dashboard">بازگشت به داشبورد</button></div>');
  }

  function courseCard(course) {
    var p = courseProgress(course);
    var lessonCount = course.chapters.reduce(function (n, c) { return n + (c.lessonIds || []).length; }, 0);
    return '<article class="course-card live">' +
      '<div class="card-top"><h3>' + esc(course.title) + '</h3><span class="badge level">' + esc(course.level) + '</span></div>' +
      '<p>' + esc(course.summary) + '</p>' +
      '<div class="meta-row"><span>' + lessonCount + ' درس</span><span>' + course.chapters.length + ' فصل</span><span>' + p.done + '/' + p.total + ' تکمیل</span></div>' +
      '<div class="progress-track"><div class="progress-fill" style="width:' + p.percent + '%"></div></div>' +
      '<div class="cta-row"><button class="btn btn-primary btn-small" data-route="#/course/' + esc(course.id) + '">ورود به دوره</button>' + statusBadge('live') + '</div>' +
    '</article>';
  }
  function pathCard(path) {
    var course = App.catalog.courses.find(function (c) { return c.pathId === path.id; });
    return '<article class="path-card ' + (course && course.status === 'live' ? '' : 'planned') + '">' +
      '<div class="card-top"><span class="order">PATH ' + String(path.order).padStart(2, '0') + '</span>' + (course ? statusBadge(course.status) : '') + '</div>' +
      '<h3>' + esc(path.title) + '</h3>' +
      '<p>' + esc(path.objectives[0]) + '</p>' +
      '<div class="meta-row"><span class="badge mini">' + esc(path.level) + '</span><span>پیشنیاز: ' + (path.prerequisites.length ? esc(path.prerequisites.length) + ' مسیر' : 'ندارد') + '</span></div>' +
      (course ? '<button class="btn btn-small" data-route="#/course/' + esc(course.id) + '">مشاهده ساختار</button>' : '') +
    '</article>';
  }
  function renderDashboard() {
    var s = progressStats();
    var live = App.catalog.courses.filter(function (c) { return c.status === 'live'; });
    var planned = App.catalog.courses.length - live.length;
    var html =
      '<section class="hero"><div class="hero-copy">' +
        '<div class="kicker">FAM ACADEMY · REBUILT FROM ZERO</div>' +
        '<h1>یادگیری شبکه، <span>قابل دیدن و قابل دستکاری</span></h1>' +
        '<p class="lead">مسیرها، درسهای عمیق، شبیهسازهای پروتکل، آزمایشگاه Cisco IOS و ارزیابی در یک تجربه RTL و تعاملی. نسخه حاضر یک Vertical Slice واقعی و قابل ارائه است؛ ۱۸ مسیر باقیمانده صادقانه بهعنوان نقشه راه P1 مشخص شدهاند.</p>' +
        '<div class="cta-row"><button class="btn btn-primary" data-route="#/course/' + esc(live[0].id) + '">شروع یادگیری</button><button class="btn" data-route="#/paths">همه مسیرها</button><button class="btn btn-ghost" data-route="#/sim/' + esc(App.catalog.simulations[0].id) + '">اجرای شبیهساز</button></div>' +
      '</div><div class="hero-visual">' + heroVisual() + '<div class="example-note">مقادیر آدرسها نمونه و مستندسازی هستند؛ در شبکه واقعی متفاوت خواهند بود.</div></div></section>' +
      '<section class="stat-grid">' +
        '<div class="stat-card"><div class="value">' + esc(App.catalog.paths.length) + '</div><div class="label">مسیر یادگیری</div></div>' +
        '<div class="stat-card"><div class="value">' + esc(App.catalog.lessons.length) + '</div><div class="label">درس کامل P0</div></div>' +
        '<div class="stat-card"><div class="value">' + esc(App.catalog.simulations.length) + '</div><div class="label">شبیهساز تعاملی</div></div>' +
        '<div class="stat-card"><div class="value">' + esc(App.catalog.labs.length) + '</div><div class="label">آزمایشگاه مرحلهای</div></div>' +
      '</section>' +
      '<section class="stat-grid">' +
        '<div class="stat-card"><div class="value">' + s.percent + '%</div><div class="label">پیشرفت شما</div></div>' +
        '<div class="stat-card"><div class="value">' + s.done + '/' + s.totalLessons + '</div><div class="label">درس تکمیلشده</div></div>' +
        '<div class="stat-card"><div class="value">' + s.quizzes + '</div><div class="label">آزمون ثبتشده</div></div>' +
        '<div class="stat-card"><div class="value">' + s.simRuns + '</div><div class="label">اجرای شبیهساز</div></div>' +
      '</section>' +
      '<div class="section-head"><div><h2>دورههای متصل و قابل ارائه</h2><p>' + live.length + ' دوره P0 با ' + App.catalog.lessons.length + ' درس کامل؛ ' + planned + ' دوره P1 فقط نقشه راه دارند.</p></div><span class="hint">کیفیت محتوا بر تعداد عنوانها ترجیح داده شده است.</span></div>' +
      '<div class="course-grid">' + live.map(courseCard).join('') + '</div>' +
      '<div class="section-head"><div><h2>شبیهسازهای تعاملی</h2><p>منطق آموزشی در یک موتور مستقل تستشده پیادهسازی شده است.</p></div></div>' +
      '<div class="sim-grid">' + App.catalog.simulations.map(function (sim) {
        return '<article class="sim-card"><div class="card-top"><h3>' + esc(sim.title) + '</h3><span class="badge live">Live</span></div><p>' + esc(sim.objective) + '</p><div class="meta-row"><span>' + esc(sim.logic) + '</span><span>' + esc(sim.limitations.length) + ' محدودیت اعلامشده</span></div><button class="btn btn-small btn-primary" data-route="#/sim/' + esc(sim.id) + '">اجرا</button></article>';
      }).join('') + '</div>' +
      '<div class="section-head"><div><h2>آزمایشگاهها</h2><p>دستورات در Simulator داخلی و امن اجرا میشوند؛ هیچ اتصال عملیاتی وجود ندارد.</p></div></div>' +
      '<div class="lab-grid">' + App.catalog.labs.map(function (lab) {
        return '<article class="lab-card"><div class="card-top"><h3>' + esc(lab.title) + '</h3><span class="badge live">Simulated</span></div><p>' + esc(lab.scenario) + '</p><button class="btn btn-small btn-primary" data-route="#/lab/' + esc(lab.id) + '">ورود به لاب</button></article>';
      }).join('') + '</div>' +
      '<div class="section-head"><div><h2>نقشه ۲۳ مسیر</h2><p>از مبانی تا معماری Cloud و آمادگی Cisco.</p></div><button class="btn btn-small" data-route="#/paths">نمایش کامل</button></div>' +
      '<div class="path-grid">' + App.catalog.paths.slice(0, 6).map(pathCard).join('') + '</div>' +
      footerHtml();
    setView(html);
  }
  function renderPaths() {
    setView('<div class="breadcrumb"><b>مسیرهای یادگیری</b> / ۲۳ مسیر از پایه تا پیشرفته</div>' +
      '<div class="section-head"><div><h2>معماری Curriculum</h2><p>پنج مسیر دارای دوره و درس کامل P0 هستند؛ سایر مسیرها ساختار فصل/تمرین/لاب مشخص دارند ولی محتوای ضعیف تولید نشده است.</p></div></div>' +
      '<div class="path-grid">' + App.catalog.paths.map(pathCard).join('') + '</div>' + footerHtml());
  }
  function renderCourse(id) {
    var course = courseById(id);
    if (!course) return renderError('دوره یافت نشد: ' + id);
    var p = courseProgress(course);
    var path = pathById(course.pathId);
    var objectives = (course.objectives || []).map(function (o) { return '<li>' + esc(o) + '</li>'; }).join('');
    var prereqs = (course.prerequisites || []).map(function (x) { var t = pathById(x); return '<li>' + esc(t ? t.title : x) + '</li>'; }).join('') || '<li>ندارد</li>';
    var chapters = course.chapters.map(function (ch) {
      var lessons = (ch.lessonIds || []).map(function (lid) {
        var l = lessonById(lid);
        if (!l) return '';
        var done = App.progress.completedLessons.indexOf(lid) !== -1;
        return '<div class="progress-row"><span>' + esc(l.title) + ' <span class="badge mini">' + esc(l.level) + ' · ' + esc(l.durationMinutes) + ' دقیقه</span></span><span><button class="btn btn-small" data-route="#/lesson/' + esc(lid) + '">مطالعه</button> ' + (done ? '<span class="badge live">تکمیل</span>' : '') + '</span></div>';
      }).join('');
      var sims = (ch.lessonIds || []).reduce(function (acc, lid) { var l = lessonById(lid); return acc.concat(l ? l.simulationIds : []); }, []).filter(function (v, i, a) { return a.indexOf(v) === i; });
      var labs = (ch.lessonIds || []).reduce(function (acc, lid) { var l = lessonById(lid); return acc.concat(l ? l.labIds : []); }, []).filter(function (v, i, a) { return a.indexOf(v) === i; });
      return '<div class="panel"><div class="card-top"><h2>' + esc(ch.title) + '</h2>' + statusBadge(ch.status) + '</div>' +
        (ch.outline ? '<ul class="list">' + ch.outline.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' : '') +
        '<div class="progress-list">' + (lessons || '<div class="empty-state">درسهای این فصل در P1 تولید خواهند شد.</div>') + '</div>' +
        (sims.length ? '<div class="next-steps">' + sims.map(function (sid) { return '<button class="btn btn-small" data-route="#/sim/' + esc(sid) + '">شبیهساز: ' + esc(simById(sid) ? simById(sid).title : sid) + '</button>'; }).join('') + '</div>' : '') +
        (labs.length ? '<div class="next-steps">' + labs.map(function (lid) { return '<button class="btn btn-small" data-route="#/lab/' + esc(lid) + '">لاب: ' + esc(labById(lid) ? labById(lid).title : lid) + '</button>'; }).join('') + '</div>' : '') +
      '</div>';
    }).join('');
    setView('<div class="breadcrumb"><b>' + esc(path ? path.title : course.pathId) + '</b> / ' + esc(course.title) + '</div>' +
      '<section class="hero" style="grid-template-columns:1fr"><div><div class="kicker">' + esc(course.level) + ' · ' + statusBadge(course.status) + '</div><h1>' + esc(course.title) + '</h1><p class="lead">' + esc(course.summary) + '</p><div class="progress-track"><div class="progress-fill" style="width:' + p.percent + '%"></div></div><div class="meta-row"><span>' + p.done + '/' + p.total + ' درس تکمیلشده</span><span>' + course.chapters.length + ' فصل</span></div></div></section>' +
      '<div class="two-col" style="margin-top:16px"><div class="panel"><h2>اهداف یادگیری</h2><ul class="list">' + objectives + '</ul></div><div class="panel"><h2>پیشنیازها</h2><ul class="list">' + prereqs + '</ul></div></div>' +
      '<div class="section-head"><h2>فصلها و درسها</h2></div>' + chapters + footerHtml());
  }

  async function loadLesson(id) {
    if (App.lessons.has(id)) return App.lessons.get(id);
    var data = await apiGet(API.lesson(id));
    App.lessons.set(id, data);
    return data;
  }
  function bodyHtml(body) {
    if (Array.isArray(body)) return '<ul class="list">' + body.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    if (typeof body === 'string') return '<p>' + esc(body) + '</p>';
    return '';
  }
  function commandsHtml(section) {
    if (!section.commands || !section.commands.length) return bodyHtml(section.body);
    return '<table class="command-table"><thead><tr><th>دستور</th><th>توضیح</th></tr></thead><tbody>' +
      section.commands.map(function (c) { return '<tr><td><code>' + esc(c.command) + '</code></td><td>' + esc(c.explain) + '</td></tr>'; }).join('') + '</tbody></table>';
  }
  function walkthroughHtml(section) {
    if (!section.lines || !section.lines.length) return bodyHtml(section.body);
    return '<table class="command-table"><thead><tr><th>خط</th><th>اثر</th></tr></thead><tbody>' +
      section.lines.map(function (l) { return '<tr><td><code>' + esc(l.line) + '</code></td><td>' + esc(l.explain) + '</td></tr>'; }).join('') + '</tbody></table>';
  }
  function sampleHtml(section) {
    return '<div class="output-label">' + esc(section.label) + '</div><pre class="code-block">' + esc((section.lines || []).join('\n')) + '</pre>';
  }
  function exerciseHtml(lesson) {
    var ex = App.exercises.find(function (e) { return e.id === lesson.exerciseId; });
    if (!ex) return '';
    return '<details class="exercise"><summary>تمرین: ' + esc(ex.title) + '</summary><p>' + esc(ex.prompt) + '</p><p><b>راهنما:</b> ' + esc(ex.hint) + '</p><p><b>پاسخ مورد انتظار:</b> ' + esc(ex.expected) + '</p></details>';
  }
  function stageContent(lesson, index) {
    var s = lesson.sections, key = STAGES[index].key;
    if (key === 'concept') {
      return '<div class="panel"><h2>' + esc(s.concept.title) + '</h2>' + bodyHtml(s.concept.body) + '<h3>' + esc(s.deepDive.title) + '</h3>' + bodyHtml(s.deepDive.body) + '</div>' +
        '<div class="two-col"><div class="panel"><h2>اهداف</h2><ul class="list">' + lesson.objectives.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div><div class="panel"><h2>پیشنیازها</h2><ul class="list">' + lesson.prerequisites.map(function (x) { var l = lessonById(x); return '<li>' + esc(l ? l.title : x) + '</li>'; }).join('') + '</ul></div></div>' +
        '<div class="two-col"><div class="panel"><h2>' + esc(s.keyPoints.title) + '</h2>' + bodyHtml(s.keyPoints.body) + '</div><div class="panel"><h2>' + esc(s.versionNotes.title) + '</h2>' + bodyHtml(s.versionNotes.body) + '</div></div>';
    }
    if (key === 'visual') {
      return '<div class="panel"><h2>' + esc(s.diagram.title) + '</h2><div class="diagram-frame"><img src="' + esc(lesson.diagramPath) + '" alt="' + esc(s.diagram.title) + '"><div class="caption">' + esc(s.diagram.body[0]) + '</div></div></div>' +
        '<div class="two-col"><div class="panel"><h2>' + esc(s.realExample.title) + '</h2>' + bodyHtml(s.realExample.body) + '</div><div class="panel"><h2>' + esc(s.scenario.title) + '</h2>' + bodyHtml(s.scenario.body) + '</div></div>';
    }
    if (key === 'practice') {
      return '<div class="panel"><h2>' + esc(s.commands.title) + '</h2>' + commandsHtml(s.commands) + '<h3>' + esc(s.commandWalkthrough.title) + '</h3>' + walkthroughHtml(s.commandWalkthrough) + '</div>' +
        '<div class="panel"><h2>' + esc(s.sampleOutput.title) + '</h2>' + sampleHtml(s.sampleOutput) + '</div>' +
        '<div class="two-col"><div class="panel"><h2>' + esc(s.commonMistakes.title) + '</h2>' + bodyHtml(s.commonMistakes.body) + '</div><div class="panel"><h2>' + esc(s.troubleshooting.title) + '</h2>' + bodyHtml(s.troubleshooting.body) + '</div></div>';
    }
    if (key === 'interactive') {
      var simCards = (lesson.simulationIds || []).map(function (sid) { var x = simById(sid); return x ? '<button class="btn btn-small btn-primary" data-route="#/sim/' + esc(sid) + '">اجرای ' + esc(x.title) + '</button>' : ''; }).join('');
      var labCards = (lesson.labIds || []).map(function (lid) { var x = labById(lid); return x ? '<button class="btn btn-small" data-route="#/lab/' + esc(lid) + '">ورود به ' + esc(x.title) + '</button>' : ''; }).join('');
      return '<div class="panel"><h2>تمرین و یادگیری عملی</h2>' + exerciseHtml(lesson) +
        '<div class="note">شبیهسازها از موتور مستقل <code>academy-engine.js</code> استفاده میکنند و پارامترها، جدول بستهها و محدودیتها را نمایش میدهند.</div>' +
        '<div class="next-steps">' + (simCards || '<span class="badge">این درس شبیهساز اختصاصی ندارد؛ تمرین تحلیلی بالا را انجام دهید.</span>') + labCards + '</div></div>' +
        '<div class="sim-grid">' + App.catalog.simulations.map(function (sim) { return '<article class="sim-card"><h3>' + esc(sim.title) + '</h3><p>' + esc(sim.objective) + '</p><button class="btn btn-small" data-route="#/sim/' + esc(sim.id) + '">مشاهده</button></article>'; }).join('') + '</div>';
    }
    return '<div class="panel"><h2>' + esc(s.summary.title) + '</h2>' + bodyHtml(s.summary.body) + '<h3>' + esc(s.references.title) + '</h3><ul class="list references">' + s.references.body.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>' +
      '<div class="panel"><h2>' + esc(s.quiz.title) + '</h2><div class="quiz-cta"><p>' + lesson.quiz.length + ' پرسش سناریومحور؛ نتیجه و پاسخ تشریحی پس از ثبت نمایش داده میشود.</p><button class="btn btn-primary" data-route="#/quiz/' + esc(lesson.id) + '">شروع آزمون</button></div></div>' +
      '<div class="panel"><h2>' + esc(s.nextSteps.title) + '</h2>' + bodyHtml(s.nextSteps.body) + '<div class="next-steps">' + (lesson.nextLessonIds || []).map(function (nid) { var n = lessonById(nid); return n ? '<button class="btn btn-small" data-route="#/lesson/' + esc(nid) + '">درس بعد: ' + esc(n.title) + '</button>' : ''; }).join('') + '</div></div>';
  }
  async function renderLesson(id) {
    var lesson = await loadLesson(id);
    if (App.currentLessonId !== id) { App.currentLessonId = id; App.lessonStage = 0; }
    App.currentLesson = lesson;
    App.progress.lastLessonId = id; saveProgress(App.progress);
    var course = courseById(lesson.courseId), path = pathById(lesson.pathId);
    var tabs = STAGES.map(function (st, i) { return '<button class="stage-btn ' + (i === App.lessonStage ? 'active' : '') + '" data-action="lesson-stage" data-stage="' + i + '">' + esc(st.title) + '</button>'; }).join('');
    var done = App.progress.completedLessons.indexOf(id) !== -1;
    var side = '<aside class="side-rail"><h3>اهداف درس</h3><ul class="list">' + lesson.objectives.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul><h3>پیشنیازها</h3><ul class="list">' + lesson.prerequisites.map(function (x) { var l = lessonById(x); return '<li>' + esc(l ? l.title : x) + '</li>'; }).join('') + '</ul><h3>گام بعد</h3><ul class="list">' + (lesson.nextLessonIds.length ? lesson.nextLessonIds.map(function (x) { var l = lessonById(x); return '<li>' + esc(l ? l.title : x) + '</li>'; }).join('') : '<li>پایان مسیر P0</li>') + '</ul><button class="btn btn-small" data-route="#/progress">پیشرفت من</button></aside>';
    var html = '<div class="breadcrumb"><b>' + esc(path ? path.title : lesson.pathId) + '</b> / ' + esc(course ? course.title : lesson.courseId) + ' / ' + esc(lesson.title) + '</div>' +
      '<div class="lesson-shell"><header class="lesson-header"><div class="card-top"><div><div class="kicker">LESSON ' + String(lesson.order).padStart(2, '0') + '</div><h1>' + esc(lesson.title) + '</h1><p class="lead">' + esc(lesson.summary) + '</p></div>' + (done ? '<span class="badge live">تکمیلشده</span>' : '') + '</div><div class="lesson-meta"><span class="badge level">' + esc(lesson.level) + '</span><span class="badge">' + esc(lesson.durationMinutes) + ' دقیقه</span><span class="badge">' + esc(lesson.quiz.length) + ' سؤال</span></div></header>' +
      side + '<div><div class="stage-tabs">' + tabs + '</div><div class="lesson-body">' + stageContent(lesson, App.lessonStage) + '</div><div class="panel"><div class="quiz-cta"><div><h2 style="margin:0">پیشرفت مرحلهای</h2><p style="margin:3px 0 0;color:var(--muted);font-size:12px">مرحله ' + (App.lessonStage + 1) + ' از ' + STAGES.length + '</p></div><div class="cta-row">' +
      (App.lessonStage > 0 ? '<button class="btn btn-small" data-action="lesson-stage" data-stage="' + (App.lessonStage - 1) + '">مرحله قبل</button>' : '') +
      (App.lessonStage < STAGES.length - 1 ? '<button class="btn btn-small btn-primary" data-action="lesson-stage" data-stage="' + (App.lessonStage + 1) + '">مرحله بعد</button>' : '<button class="btn btn-small btn-primary" data-route="#/quiz/' + esc(id) + '">آزمون</button>') +
      '<button class="btn btn-small" data-action="mark-complete">' + (done ? 'تکمیلشده ✓' : 'علامت تکمیل') + '</button></div></div></div></div></div>' + footerHtml();
    setView(html);
  }

  function paramInput(p) {
    var id = esc(p.id), label = esc(p.label), val = p.default;
    if (p.type === 'checkbox') return '<div class="field"><label for="p-' + id + '">' + label + '</label><input id="p-' + id + '" type="checkbox" data-param="' + id + '" ' + (val ? 'checked' : '') + '></div>';
    if (p.type === 'select') return '<div class="field"><label for="p-' + id + '">' + label + '</label><select id="p-' + id + '" data-param="' + id + '">' + (p.options || []).map(function (o) { return '<option value="' + esc(o) + '" ' + (o === val ? 'selected' : '') + '>' + esc(o) + '</option>'; }).join('') + '</select></div>';
    if (p.type === 'number') return '<div class="field"><label for="p-' + id + '">' + label + '</label><input id="p-' + id + '" type="number" data-param="' + id + '" value="' + esc(val) + '" ' + (p.min != null ? 'min="' + esc(p.min) + '"' : '') + ' ' + (p.max != null ? 'max="' + esc(p.max) + '"' : '') + '></div>';
    return '<div class="field"><label for="p-' + id + '">' + label + '</label><input id="p-' + id + '" type="text" data-param="' + id + '" value="' + esc(val) + '"></div>';
  }
  function collectSimParams(sim) {
    var params = {};
    sim.parameters.forEach(function (p) { params[p.id] = p.default; });
    document.querySelectorAll('[data-param]').forEach(function (el) {
      var id = el.dataset.param, p = sim.parameters.find(function (x) { return x.id === id; });
      if (!p) return;
      if (p.type === 'checkbox') params[id] = el.checked;
      else if (p.type === 'number') params[id] = Number(el.value);
      else params[id] = el.value;
    });
    return params;
  }
  async function runSimulation() {
    var sim = App.currentSim;
    if (!sim || !Engine || typeof Engine[sim.logic] !== 'function') return;
    var result = Engine[sim.logic](collectSimParams(sim));
    App.simResult = result; App.simActive = 0;
    App.progress.simRuns[sim.id] = (Number(App.progress.simRuns[sim.id]) || 0) + 1; saveProgress(App.progress);
    renderSimulationResult();
  }
  function renderSimulationResult() {
    var box = document.getElementById('sim-output');
    if (!box) return;
    var r = App.simResult;
    if (!r) { box.innerHTML = '<div class="empty-state">برای مشاهده رفتار پروتکل، دکمه «اجرا» را بزنید.</div>'; return; }
    if (!r.ok) { box.innerHTML = '<div class="error-box"><b>ورودی نامعتبر:</b> ' + esc(r.error) + '</div>'; return; }
    var steps = r.steps || [], active = Math.min(App.simActive, steps.length - 1);
    var stepHtml = steps.map(function (st, i) { return '<button class="step-item ' + (i === active ? 'active' : '') + '" data-action="sim-step-select" data-index="' + i + '">' + esc(i + 1) + '. ' + esc(st.title || st.message) + '</button>'; }).join('');
    var rows = (r.table || []).map(function (row, i) {
      return '<tr class="' + (i === active ? 'active-row' : '') + '"><td>' + esc(row.index || i + 1) + '</td><td>' + esc(row.time) + '</td><td>' + esc(row.from) + '</td><td>' + esc(row.to) + '</td><td>' + esc(row.protocol) + '</td><td><b>' + esc(row.message) + '</b><br><span style="color:var(--muted)">' + esc(row.detail) + '</span></td><td>' + esc(row.size) + '</td></tr>';
    }).join('');
    var detail = steps[active] ? '<div class="note"><b>' + esc(steps[active].title || steps[active].message) + '</b><br>' + esc(steps[active].detail) + '</div>' : '';
    box.innerHTML = '<div class="card-top"><h2>خروجی اجرا</h2><span class="badge live">' + esc(r.decision || r.finalState || 'اجرا شد') + '</span></div>' +
      '<div class="output-label">' + esc(r.label) + '</div>' +
      '<div class="result-box"><b>خلاصه:</b> ' + esc(r.summary) + '</div>' + detail +
      '<div class="section-head"><h3>مراحل</h3><div class="cta-row"><button class="btn btn-small" data-action="sim-play">پخش</button><button class="btn btn-small" data-action="sim-step">گام بعد</button><button class="btn btn-small" data-action="sim-reset">بازنشانی</button></div></div>' +
      '<div class="step-list">' + stepHtml + '</div>' +
      '<div style="overflow-x:auto"><table class="packet-table"><thead><tr><th>#</th><th>زمان</th><th>مبدأ</th><th>مقصد</th><th>پروتکل</th><th>پیام / توضیح</th><th>اندازه</th></tr></thead><tbody>' + rows + '</tbody></table></div>' +
      (r.warnings && r.warnings.length ? '<div class="warning"><b>هشدارها:</b><ul class="list">' + r.warnings.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul></div>' : '') +
      (r.limitations && r.limitations.length ? '<div class="note"><b>محدودیتهای صادقانه:</b><ul class="list">' + r.limitations.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul></div>' : '');
  }
  async function renderSimulation(id) {
    clearSimTimer();
    var data;
    if (App.simulations.has(id)) data = App.simulations.get(id); else { data = await apiGet(API.simulation(id)); App.simulations.set(id, data); }
    App.currentSim = data; App.simResult = null; App.simActive = 0;
    var controls = '<aside class="controls"><h2>پارامترها</h2>' + data.parameters.map(paramInput).join('') + '<div class="cta-row"><button class="btn btn-primary btn-small" data-action="sim-run">اجرا</button><button class="btn btn-small" data-action="sim-step">گام</button><button class="btn btn-small" data-action="sim-reset">بازنشانی</button></div><div class="note" style="margin-top:12px">تغییر پارامترها، منطق تصمیمگیری و جدول بستهها را تغییر میدهد؛ این یک انیمیشن تزئینی نیست.</div></aside>';
    setView('<div class="breadcrumb"><b>شبیهسازها</b> / ' + esc(data.title) + '</div>' +
      '<section class="hero" style="grid-template-columns:1fr"><div><div class="kicker">INTERACTIVE SIMULATION</div><h1>' + esc(data.title) + '</h1><p class="lead">' + esc(data.objective) + '</p></div></section>' +
      '<div class="sim-layout">' + controls + '<div><div class="sim-visual"><img src="' + esc(data.diagramPath) + '" alt="دیاگرام ' + esc(data.title) + '"></div><div class="sim-output" id="sim-output"></div></div></div>' + footerHtml());
    await runSimulation();
  }

  function renderLabOutput() {
    var el = document.getElementById('lab-output');
    if (!el) return;
    el.innerHTML = App.labOutput.map(function (line) {
      if (line.type === 'cmd') return '<span class="cmd">&gt; ' + esc(line.text) + '</span>';
      if (line.type === 'warn') return '<span class="warn">' + esc(line.text) + '</span>';
      return esc(line.text);
    }).join('\n');
    el.scrollTop = el.scrollHeight;
  }
  function executeLabCommand(cmd) {
    if (!App.labState || !cmd) return;
    var r = Engine.runLabCommand(App.labState, cmd);
    App.labOutput.push({ type: 'cmd', text: cmd });
    r.output.forEach(function (line) { App.labOutput.push({ type: r.matched ? 'out' : 'warn', text: line }); });
    renderLabOutput();
  }
  function labStepDone(stepId) {
    var arr = Array.isArray(App.progress.labSteps[App.currentLab.id]) ? App.progress.labSteps[App.currentLab.id] : [];
    if (arr.indexOf(stepId) === -1) { arr.push(stepId); App.progress.labSteps[App.currentLab.id] = arr; saveProgress(App.progress); }
    var btn = document.querySelector('[data-action="lab-step"][data-step="' + stepId + '"]');
    if (btn) btn.classList.add('done');
  }
  function renderLab(id) {
    clearSimTimer();
    var data;
    if (App.labs.has(id)) data = App.labs.get(id); else { data = apiGet(API.lab(id)); }
    return Promise.resolve(data).then(function (lab) {
      App.labs.set(id, lab); App.currentLab = lab; App.labState = Engine.createLabState(lab);
      App.labOutput = [{ type: 'out', text: Engine.OUTPUT_LABEL }, { type: 'out', text: 'Internal Simulator ready. No real device connection.' }];
      var doneSteps = Array.isArray(App.progress.labSteps[id]) ? App.progress.labSteps[id] : [];
      var addrRows = lab.addressingTable.map(function (r) { return '<tr><td>' + esc(r.device) + '</td><td>' + esc(r.interface) + '</td><td>' + esc(r.address) + '</td><td>' + esc(r.mask) + '</td><td>' + esc(r.gateway) + '</td><td>' + esc(r.vlan || r.area || '-') + '</td></tr>'; }).join('');
      var stepHtml = lab.steps.map(function (st, i) { return '<button class="step-run ' + (doneSteps.indexOf(st.id) !== -1 ? 'done' : '') + '" data-action="lab-step" data-step="' + esc(st.id) + '"><span>' + esc(i + 1) + '. ' + esc(st.title) + '</span><span>' + esc(st.commands.length) + ' دستور</span></button>'; }).join('');
      setView('<div class="breadcrumb"><b>آزمایشگاهها</b> / ' + esc(lab.title) + '</div>' +
        '<section class="hero" style="grid-template-columns:1fr"><div><div class="kicker">INTERNAL SIMULATOR · DESIGNED, NOT RUN ON REAL DEVICE</div><h1>' + esc(lab.title) + '</h1><p class="lead">' + esc(lab.scenario) + '</p><div class="meta-row"><span class="badge live">Simulated</span><span>' + esc(lab.executionMode) + '</span><span>' + esc(lab.status) + '</span></div></div></section>' +
        '<div class="lab-layout"><div class="lab-info"><h2>توپولوژی و آدرسدهی</h2><div class="diagram-frame"><img src="' + esc(lab.topology.diagramPath) + '" alt="توپولوژی ' + esc(lab.title) + '"></div><div class="caption">' + esc(lab.topology.summary) + '</div>' +
        '<table class="addressing-table"><thead><tr><th>تجهیز</th><th>اینترفیس</th><th>آدرس</th><th>Mask</th><th>Gateway</th><th>VLAN/Area</th></tr></thead><tbody>' + addrRows + '</tbody></table>' +
        '<h2>مراحل اجرا</h2><div class="steps-list">' + stepHtml + '</div>' +
        '<h2>سناریوی خرابی</h2><div class="warning">' + esc(lab.failureScenario) + '</div><h2>Troubleshooting</h2><ul class="list">' + lab.troubleshooting.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
        '<h2>معیار موفقیت</h2><ul class="list">' + lab.successCriteria.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
        '<div class="note"><b>معماری آینده:</b> ' + esc(lab.futureIntegration.note) + '</div></div>' +
        '<div class="terminal"><div class="terminal-head"><span>' + esc(lab.expectedOutput.label) + '</span><span>Cisco IOS-like educational subset</span></div><div class="terminal-output" id="lab-output"></div><div class="lab-input-row"><input id="lab-input" autocomplete="off" spellcheck="false" placeholder="show vlan brief"><button class="btn btn-primary btn-small" data-action="lab-command">اجرا</button></div></div></div>' +
        '<div class="panel"><h2>سؤالات بررسی</h2><ul class="list">' + lab.reviewQuestions.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>' + footerHtml());
      renderLabOutput();
    });
  }
  function executeLabStep(stepId) {
    var step = App.currentLab && App.currentLab.steps.find(function (s) { return s.id === stepId; });
    if (!step) return;
    step.commands.forEach(executeLabCommand);
    App.labOutput.push({ type: 'out', text: '--- Expected: ' + step.expectedState + ' ---' });
    renderLabOutput(); labStepDone(stepId);
  }

  async function renderQuiz(id) {
    clearSimTimer();
    var lesson = await loadLesson(id);
    App.currentLesson = lesson;
    var questions = lesson.quiz.map(function (q, i) {
      return '<div class="quiz-question"><h3>' + esc(i + 1) + '. ' + esc(q.prompt) + '</h3><div class="options">' + q.options.map(function (o, j) {
        return '<label class="option"><input type="radio" name="q' + i + '" value="' + j + '"><span>' + esc(o) + '</span></label>';
      }).join('') + '</div></div>';
    }).join('');
    setView('<div class="breadcrumb"><b>ارزیابی</b> / ' + esc(lesson.title) + '</div>' +
      '<section class="hero" style="grid-template-columns:1fr"><div><div class="kicker">ASSESSMENT</div><h1>آزمون: ' + esc(lesson.title) + '</h1><p class="lead">' + lesson.quiz.length + ' پرسش؛ نمره و پاسخ تشریحی پس از ثبت ذخیره میشود.</p></div></section>' +
      '<div class="quiz-list">' + questions + '</div><div class="panel"><button class="btn btn-primary" data-action="quiz-submit">ثبت پاسخها</button></div><div id="quiz-result"></div>' + footerHtml());
  }
  function renderQuizResult(lesson, result) {
    var correct = result.correct, total = result.total;
    var details = (result.details || []).map(function (d, i) {
      return '<div class="quiz-detail ' + (d.correct ? 'correct' : 'wrong') + '"><b>' + esc(i + 1) + '. ' + (d.correct ? 'درست' : 'نادرست') + '</b> — ' + esc(d.prompt) + '<br>پاسخ صحیح: ' + esc(d.options[d.correctIndex]) + '<br>' + esc(d.explanation) + '</div>';
    }).join('');
    var next = (lesson.nextLessonIds || [])[0];
    document.getElementById('quiz-result').innerHTML = '<div class="panel quiz-result"><div class="card-top"><div><div class="score-badge">' + esc(result.score) + '%</div><div class="label">' + correct + ' از ' + total + ' پاسخ درست</div></div><span class="badge ' + (result.score >= 70 ? 'live' : 'planned') + '">' + (result.score >= 70 ? 'قبول' : 'نیاز به مرور') + '</span></div>' + details +
      '<div class="next-steps"><button class="btn btn-small" data-route="#/lesson/' + esc(lesson.id) + '">بازگشت به درس</button>' + (next ? '<button class="btn btn-small btn-primary" data-route="#/lesson/' + esc(next) + '">درس بعد</button>' : '<button class="btn btn-small btn-primary" data-route="#/progress">مشاهده پیشرفت</button>') + '</div></div>';
  }
  async function submitQuiz() {
    var lesson = App.currentLesson;
    if (!lesson) return;
    var answers = lesson.quiz.map(function (_, i) { var el = document.querySelector('input[name="q' + i + '"]:checked'); return el ? Number(el.value) : null; });
    var result;
    try { result = await apiPost(API.quiz(lesson.id), { answers: answers }); }
    catch (_) { result = Engine.evaluateQuiz(lesson, answers); }
    App.progress.quizScores[lesson.id] = result.score;
    if (result.score >= 70 && App.progress.completedLessons.indexOf(lesson.id) === -1) App.progress.completedLessons.push(lesson.id);
    saveProgress(App.progress);
    renderQuizResult(lesson, result);
  }

  function renderProgress() {
    var s = progressStats();
    var completed = App.progress.completedLessons.map(function (id) { var l = lessonById(id); return l ? '<div class="progress-row"><span>' + esc(l.title) + '</span><span class="badge live">تکمیل</span></div>' : ''; }).join('');
    var quizzes = Object.keys(App.progress.quizScores).map(function (id) { var l = lessonById(id); return '<div class="progress-row"><span>' + esc(l ? l.title : id) + '</span><b>' + esc(App.progress.quizScores[id]) + '%</b></div>'; }).join('');
    var labs = Object.keys(App.progress.labSteps).map(function (id) { var l = labById(id); var steps = Array.isArray(App.progress.labSteps[id]) ? App.progress.labSteps[id] : []; return '<div class="progress-row"><span>' + esc(l ? l.title : id) + '</span><span>' + esc(steps.length) + ' مرحله</span></div>'; }).join('');
    var sims = Object.keys(App.progress.simRuns).map(function (id) { var x = simById(id); return '<div class="progress-row"><span>' + esc(x ? x.title : id) + '</span><span>' + esc(App.progress.simRuns[id]) + ' اجرا</span></div>'; }).join('');
    setView('<div class="breadcrumb"><b>پیشرفت من</b> / ذخیرهسازی محلی و همگامسازی امن با سرور</div>' +
      '<section class="stat-grid"><div class="stat-card"><div class="value">' + s.percent + '%</div><div class="label">پیشرفت کلی</div></div><div class="stat-card"><div class="value">' + s.done + '</div><div class="label">درس تکمیلشده</div></div><div class="stat-card"><div class="value">' + s.quizzes + '</div><div class="label">آزمون</div></div><div class="stat-card"><div class="value">' + s.labSteps + '</div><div class="label">مرحله لاب</div></div></section>' +
      '<div class="two-col"><div class="panel"><h2>درسها</h2><div class="progress-list">' + (completed || '<div class="empty-state">هنوز درسی تکمیل نشده است.</div>') + '</div></div><div class="panel"><h2>نمرات</h2><div class="progress-list">' + (quizzes || '<div class="empty-state">آزمونی ثبت نشده است.</div>') + '</div></div></div>' +
      '<div class="two-col"><div class="panel"><h2>آزمایشگاهها</h2><div class="progress-list">' + (labs || '<div class="empty-state">مرحلهای اجرا نشده است.</div>') + '</div></div><div class="panel"><h2>شبیهسازها</h2><div class="progress-list">' + (sims || '<div class="empty-state">اجرایی ثبت نشده است.</div>') + '</div></div></div>' +
      '<div class="note">پیشرفت نسخه جدید تحت کلید <code>famAcademyV2.progress.v1</code> ذخیره میشود؛ کلیدهای قدیمی کاربران حفظ میشوند و بازنویسی نمیشوند.</div>' + footerHtml());
  }

  async function renderRoute() {
    var hash = location.hash || '#/dashboard';
    App.activeRoute = hash; clearSimTimer(); setActiveNav(hash);
    var parts = hash.replace(/^#\/?/, '').split('/').filter(Boolean);
    var key = parts[0] || 'dashboard';
    try {
      if (key === 'dashboard') return renderDashboard();
      if (key === 'paths') return renderPaths();
      if (key === 'progress') return renderProgress();
      if (key === 'course' && parts[1]) return renderCourse(decodeURIComponent(parts[1]));
      if (key === 'lesson' && parts[1]) return await renderLesson(decodeURIComponent(parts[1]));
      if (key === 'sim' && parts[1]) return await renderSimulation(decodeURIComponent(parts[1]));
      if (key === 'lab' && parts[1]) return await renderLab(decodeURIComponent(parts[1]));
      if (key === 'quiz' && parts[1]) return await renderQuiz(decodeURIComponent(parts[1]));
      return renderDashboard();
    } catch (e) { return renderError(e && e.message ? e.message : String(e)); }
  }

  async function onClick(e) {
    var routeEl = e.target.closest('[data-route]');
    if (routeEl) { e.preventDefault(); location.hash = routeEl.dataset.route; return; }
    var el = e.target.closest('[data-action]');
    if (!el) return;
    e.preventDefault();
    var action = el.dataset.action;
    if (action === 'toggle-menu') {
      var shell = document.getElementById('academy-shell');
      if (shell && shell.classList) {
        shell.classList.toggle('academy-menu-collapsed');
        var collapsed = shell.classList.contains('academy-menu-collapsed');
        var sidebar = document.getElementById('academy-sidebar');
        if (sidebar && sidebar.setAttribute) sidebar.setAttribute('aria-hidden', String(collapsed));
        if (el.setAttribute) el.setAttribute('aria-expanded', String(!collapsed));
      }
      return;
    }
    if (action === 'toggle-theme') {
      var html = document.documentElement || { dataset: {} };
      var nextTheme = html.dataset.theme === 'light' ? 'dark' : 'light';
      html.dataset.theme = nextTheme;
      try {
        localStorage.setItem('fam.academy.theme', nextTheme);
        localStorage.setItem('fam.ui.theme', nextTheme === 'light' ? 'light' : 'original');
      } catch (_) {}
      syncTheme();
      return;
    }
    if (action === 'lesson-stage') { App.lessonStage = Number(el.dataset.stage); return renderLesson(App.currentLessonId); }
    if (action === 'mark-complete') {
      var id = App.currentLessonId;
      if (id && App.progress.completedLessons.indexOf(id) === -1) { App.progress.completedLessons.push(id); saveProgress(App.progress); }
      return renderLesson(id);
    }
    if (action === 'sim-run') return runSimulation();
    if (action === 'sim-step') {
      if (!App.simResult) await runSimulation();
      App.simActive = Math.min(App.simActive + 1, (App.simResult.steps || []).length - 1); return renderSimulationResult();
    }
    if (action === 'sim-reset') { App.simActive = 0; return renderSimulationResult(); }
    if (action === 'sim-step-select') { App.simActive = Number(el.dataset.index); return renderSimulationResult(); }
    if (action === 'sim-play') {
      if (!App.simResult) await runSimulation();
      clearSimTimer();
      App.simTimer = setInterval(function () {
        var max = (App.simResult.steps || []).length - 1;
        if (App.simActive >= max) { clearSimTimer(); return; }
        App.simActive += 1; renderSimulationResult();
      }, 700);
      return;
    }
    if (action === 'lab-step') return executeLabStep(el.dataset.step);
    if (action === 'lab-command') {
      var input = document.getElementById('lab-input');
      if (input && input.value.trim()) { executeLabCommand(input.value.trim()); input.value = ''; }
      return;
    }
    if (action === 'quiz-submit') return submitQuiz();
  }
  function onKeyDown(e) {
    if (e.key === 'Enter' && e.target && e.target.id === 'lab-input') {
      e.preventDefault();
      var input = e.target;
      if (input.value.trim()) { executeLabCommand(input.value.trim()); input.value = ''; }
    }
  }

  async function mount() {
    if (!Engine) { root.innerHTML = '<div class="error-box">موتور شبیهسازی بارگذاری نشد.</div>'; return; }
    try {
      App.progress = readProgress();
      App.catalog = await apiGet(API.catalog);
      var ex = await apiGet(API.exercises);
      App.exercises = ex.exercises || [];
      renderShell();
      syncTheme();
      if (!location.hash) location.hash = '#/dashboard';
      await renderRoute();
      window.addEventListener('hashchange', function () { renderRoute(); });
      document.addEventListener('click', onClick);
      document.addEventListener('keydown', onKeyDown);
    } catch (e) {
      root.innerHTML = '<div class="error-box"><h2>خطا در راهاندازی آکادمی</h2><p>' + esc(e && e.message ? e.message : String(e)) + '</p></div>';
    }
  }
  mount();
})();
