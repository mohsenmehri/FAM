(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const root = $('app-root');
  if (!root || document.querySelector('.app-shell')) return;

  const oldHeader = document.querySelector('.fa-topbar');
  const oldButtons = ['btn-paths', 'btn-blueprint', 'btn-coverage', 'btn-back-paths']
    .map($).filter(Boolean);
  const stageBar = $('fam-stage4-bar');
  const searchWrap = $('s4-search-wrap');
  const planner = $('fam-stage4-panel');
  const offlineNote = document.querySelector('body > [role="note"]');
  const accountTools = $('academy-account-tools');

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  const skip = el('a', 'skip-link', 'پرش به محتوا');
  skip.href = '#app-root';
  const backdrop = el('div', 'fam-campus-backdrop');
  backdrop.setAttribute('aria-hidden', 'true');
  document.body.insertBefore(backdrop, document.body.firstChild);
  document.body.insertBefore(skip, backdrop);

  const iconPaths = {
    home: 'M3 10.5 12 3l9 7.5M5.5 9.5V20h13V9.5M10 20v-6h4v6',
    route: 'M6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM18 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM8 17h6.5a3.5 3.5 0 0 0 0-7h-5a3.5 3.5 0 0 1 0-7H16',
    lab: 'M9 3h6M10 3v6L4.5 19a2 2 0 0 0 1.8 3h11.4a2 2 0 0 0 1.8-3L14 9V3M7.5 15h9',
    book: 'M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15ZM4 20.5A2.5 2.5 0 0 1 6.5 23H20M9 7.5h7M9 11h5',
    chart: 'M4 20V10M10 20V4M16 20v-8M21 20H3',
    glossary: 'M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15ZM9 7h7M9 11h7M9 15h4',
    search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM20 20l-4-4',
    menu: 'M4 7h16M4 12h16M4 17h16',
    sun: 'M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
    moon: 'M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z',
    user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4.5 20.5a7.5 7.5 0 0 1 15 0',
    help: 'M9.1 9a3 3 0 1 1 5.8 1c-.7 1.2-2.9 1.6-2.9 3.5M12 17.5h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
    portal: 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z'
  };

  function icon(name, size = 18) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', String(size));
    svg.setAttribute('height', String(size));
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '1.8');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', iconPaths[name] || iconPaths.book);
    svg.appendChild(p);
    return svg;
  }

  function hexBrandSvg() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 40 40');
    svg.setAttribute('width', '28');
    svg.setAttribute('height', '28');
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML =
      '<defs><linearGradient id="famHexG" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#00d4ff"/><stop offset="1" stop-color="#3b82f6"/></linearGradient></defs>' +
      '<path d="M20 3 L34.7 11.5 V28.5 L20 37 L5.3 28.5 V11.5 Z" fill="none" stroke="url(#famHexG)" stroke-width="2.4"/>' +
      '<path d="M20 13 L13 26 M20 13 L27 26 M13 26 L27 26" stroke="#7dd3fc" stroke-width="1.5" opacity=".85"/>' +
      '<circle cx="20" cy="13" r="3.2" fill="#00d4ff"/>' +
      '<circle cx="13" cy="26" r="2.6" fill="#3b82f6"/>' +
      '<circle cx="27" cy="26" r="2.6" fill="#34d399"/>';
    return svg;
  }

  const shell = el('div', 'app-shell');
  const sidebar = el('aside', 'sidebar');
  sidebar.id = 'academy-sidebar';

  const brand = el('a', 'brand');
  brand.href = '#/dashboard';
  brand.dataset.action = 'home';
  brand.setAttribute('aria-label', 'FAM Academy — خانه');
  const logo = el('span', 'brand-logo');
  logo.append(hexBrandSvg());
  const brandCopy = el('span', 'brand-copy');
  const brandName = el('b', 'ltr');
  brandName.innerHTML = 'FAM<em>Academy</em>';
  const brandSub = el('small', 'ltr', 'NETWORK ENGINEERING');
  brandCopy.append(brandName, brandSub);
  brand.append(logo, brandCopy);

  const nav = el('nav', 'side-nav');
  nav.setAttribute('aria-label', 'ناوبری اصلی');
  const navItems = [
    ['home', 'خانه و داشبورد', 'home', 'home', ''],
    ['paths', 'مسیرها و ۱۲۷ درس', 'route', 'paths', '۱۲۷'],
    ['lab', 'آزمایشگاه و شبیه‌ساز CLI', 'lab', 'lab', '۱۲۵'],
    ['progress', 'پیشرفت و آمار من', 'chart', 'progress', ''],
    ['planner', 'برنامه مطالعه و نقشه راه', 'book', 'planner', ''],
    ['glossary', 'واژه‌نامه جامع شبکه', 'glossary', 'glossary', ''],
    ['coverage', 'پوشش فرمان‌های IOS', 'book', 'coverage', '']
  ];
  const navLinks = new Map();
  let lessonsPill = null;
  for (const [id, label, ico, act, pillText] of navItems) {
    const a = el('a', 'side-link');
    a.href = '#' + act;
    a.dataset.action = act;
    const i = el('span', 'side-icon');
    i.append(icon(ico, 19));
    const copy = el('span', 'side-copy');
    copy.append(el('span', 'side-label', label));
    a.append(i, copy);
    if (pillText) {
      const pill = el('span', 'side-pill', pillText);
      if (id === 'paths') lessonsPill = pill;
      a.append(pill);
    }
    nav.append(a);
    navLinks.set(id, a);
  }

  // Study Focus Timer widget (inspired by 641d02e)
  const timerBox = el('div', 'side-timer');
  const timerHead = el('div', 'side-timer-head');
  timerHead.append(el('span', '', 'تایمر مطالعه متمرکز'));
  const timerPreset = el('button', 'side-timer-btn', '۴۵ دقیقه');
  timerPreset.type = 'button';
  timerPreset.title = 'تغییر مدت (۲۵ / ۴۵ / ۶۰ دقیقه)';
  timerHead.append(timerPreset);
  const timerDisplay = el('div', 'side-timer-display', '45:00');
  const timerControls = el('div', 'side-timer-controls');
  const timerStart = el('button', 'side-timer-btn primary', 'شروع');
  timerStart.type = 'button';
  const timerReset = el('button', 'side-timer-btn', 'ریست');
  timerReset.type = 'button';
  timerControls.append(timerStart, timerReset);
  const timerMeta = el('div', 'side-timer-meta', 'مطالعه امروز: ۰ دقیقه');
  timerBox.append(timerHead, timerDisplay, timerControls, timerMeta);

  const TIMER_KEY = 'fam.academy.timer.v1';
  const presets = [25, 45, 60];
  let presetIdx = 1;
  let remainingSec = presets[presetIdx] * 60;
  let timerHandle = null;
  const todayKey = () => new Date().toISOString().slice(0, 10);
  const loadTodayMins = () => {
    try {
      const raw = JSON.parse(localStorage.getItem(TIMER_KEY) || '{}');
      return raw.day === todayKey() ? Math.max(0, Number(raw.minutes) || 0) : 0;
    } catch (_) { return 0; }
  };
  let todayMinutes = loadTodayMins();
  const renderTimer = () => {
    const m = Math.floor(remainingSec / 60);
    const s = remainingSec % 60;
    timerDisplay.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    timerPreset.textContent = `${presets[presetIdx].toLocaleString('fa-IR')} دقیقه`;
    timerMeta.textContent = `مطالعه امروز: ${todayMinutes.toLocaleString('fa-IR')} دقیقه`;
    timerStart.textContent = timerHandle ? 'توقف' : 'شروع';
  };
  let secAccum = 0;
  timerStart.addEventListener('click', () => {
    if (timerHandle) {
      clearInterval(timerHandle);
      timerHandle = null;
      renderTimer();
      return;
    }
    timerHandle = setInterval(() => {
      if (remainingSec > 0) {
        remainingSec -= 1;
        secAccum += 1;
        if (secAccum >= 60) {
          secAccum = 0;
          todayMinutes += 1;
          try { localStorage.setItem(TIMER_KEY, JSON.stringify({ day: todayKey(), minutes: todayMinutes })); } catch (_) {}
        }
      } else {
        clearInterval(timerHandle);
        timerHandle = null;
      }
      renderTimer();
    }, 1000);
    renderTimer();
  });
  timerReset.addEventListener('click', () => {
    if (timerHandle) { clearInterval(timerHandle); timerHandle = null; }
    remainingSec = presets[presetIdx] * 60;
    secAccum = 0;
    renderTimer();
  });
  timerPreset.addEventListener('click', () => {
    if (timerHandle) { clearInterval(timerHandle); timerHandle = null; }
    presetIdx = (presetIdx + 1) % presets.length;
    remainingSec = presets[presetIdx] * 60;
    secAccum = 0;
    renderTimer();
  });
  renderTimer();

  // Sidebar Progress Card
  const pathCard = el('div', 'side-path');
  pathCard.append(el('div', 'side-path-head', 'پیشرفت کل آکادمی'), el('div', 'side-path-name', 'Curriculum 5.0 + Automation'));
  const pathMeter = el('div', 'meter');
  const pathFill = el('i');
  pathMeter.append(pathFill);
  const pathMeta = el('div', 'side-path-meta', '');
  pathCard.append(pathMeter, pathMeta);

  let totalCatalogLessons = 127;
  const syncSidebarProgress = () => {
    const done = window.FamAcademyCatalog?.getCompletedSet ? window.FamAcademyCatalog.getCompletedSet().size : 0;
    const pct = totalCatalogLessons ? Math.round((done * 100) / totalCatalogLessons) : 0;
    pathFill.style.width = `${pct}%`;
    pathMeta.textContent = `${done.toLocaleString('fa-IR')} از ${totalCatalogLessons.toLocaleString('fa-IR')} درس (${pct.toLocaleString('fa-IR')}٪)`;
  };
  fetch('/academy-assets/curriculum-catalog.json?v=20261123c', { cache: 'no-store' })
    .then(response => { if (!response.ok) throw new Error('catalog unavailable'); return response.json(); })
    .then(catalog => {
      totalCatalogLessons = (catalog.paths || []).reduce((sum, path) =>
        sum + (path.courses || []).reduce((courseSum, course) => courseSum + (course.lessons || []).length, 0), 0);
      if (lessonsPill) lessonsPill.textContent = totalCatalogLessons.toLocaleString('fa-IR');
      syncSidebarProgress();
    })
    .catch(() => { pathMeta.textContent = 'فهرست درس‌ها در دسترس نیست'; });

  const portalNav = el('nav', 'side-nav');
  portalNav.setAttribute('aria-label', 'دسترسی به پنل FAM');
  const backFam = el('a', 'side-link');
  backFam.href = window.FamAcademyBridge?.offline ? '#/dashboard' : '/app';
  const backIcon = el('span', 'side-icon');
  backIcon.append(icon('portal', 18));
  backFam.append(backIcon, el('span', 'side-label', window.FamAcademyBridge?.offline ? 'نسخه آفلاین محلی' : 'بازگشت به پنل اصلی FAM'));
  portalNav.append(backFam);

  const sideFoot = el('div', 'side-foot');
  sideFoot.append(el('span', 'live-dot'), el('span', '', 'محتوای آموزشی و شبیه‌ساز محلی'));

  sidebar.append(
    brand,
    el('div', 'side-sep', 'مسیر آموزش'),
    nav,
    el('div', 'side-sep', 'تمرکز و پیشرفت'),
    timerBox,
    pathCard,
    el('div', 'side-sep', 'دسترسی‌ها'),
    portalNav,
    sideFoot
  );

  // Main Area & Sticky Glass Topbar
  const appMain = el('div', 'app-main');
  const topbar = el('header', 'topbar');
  const menuButton = el('button', 'icon-btn academy-menu-toggle');
  menuButton.type = 'button';
  menuButton.setAttribute('aria-controls', 'academy-sidebar');
  menuButton.setAttribute('aria-expanded', 'true');
  menuButton.setAttribute('aria-label', 'باز و بسته کردن منو');
  menuButton.title = 'باز و بسته کردن منو';
  menuButton.append(icon('menu', 18));

  const topTitle = el('div', 'academy-top-title');
  topTitle.append(el('b', '', 'آکادمی فام'), el('small', 'ltr', 'FAM ACADEMY · LIVE TOPOLOGY UI'));

  const crumbs = el('nav', 'crumbs academy-route-crumbs');
  crumbs.setAttribute('aria-label', 'مسیر صفحه');

  const topActions = el('div', 'top-actions');
  const search = el('button', 'search-trigger');
  search.type = 'button';
  search.setAttribute('aria-label', 'جست‌وجو');
  search.append(icon('search', 16), el('span', '', 'جست‌وجو در ۱۲۷ درس'), el('kbd', '', 'Ctrl K'));

  const labQuick = el('a', 'top-chip');
  labQuick.href = '#/lab';
  labQuick.dataset.action = 'lab';
  labQuick.append(el('span', '', 'آزمایشگاه CLI'));

  const theme = el('button', 'icon-btn theme-toggle');
  theme.type = 'button';
  const help = el('button', 'icon-btn');
  help.type = 'button';
  help.setAttribute('aria-label', 'راهنمای آکادمی');
  help.title = 'راهنمای آکادمی';
  help.append(icon('help', 18));

  const progressBtn = el('a', 'icon-btn');
  progressBtn.href = '#/progress';
  progressBtn.dataset.action = 'progress';
  progressBtn.setAttribute('aria-label', 'پیشرفت من');
  progressBtn.title = 'پیشرفت من';
  progressBtn.append(icon('user', 18));

  topActions.append(search, labQuick, theme, help, progressBtn);
  topbar.append(menuButton, topTitle, crumbs, topActions);

  const hiddenTools = el('div', 'sr-only');
  hiddenTools.hidden = true;
  for (const button of oldButtons) hiddenTools.append(button);

  const offlineHost = el('div', 'offline-banner-host');
  if (offlineNote) offlineHost.append(offlineNote);

  root.className = 'page';
  root.removeAttribute('style');
  appMain.append(topbar);
  if (offlineNote) appMain.append(offlineHost);
  appMain.append(root, hiddenTools);
  if (accountTools) appMain.append(accountTools);
  for (const node of [searchWrap, stageBar, planner]) if (node) appMain.append(node);

  // Mobile Bottom Nav
  const bottom = el('nav', 'bottom-nav');
  bottom.setAttribute('aria-label', 'ناوبری اصلی موبایل');
  const bottomActions = [
    ['home', 'خانه', 'home'],
    ['paths', 'مسیرها', 'route'],
    ['lab', 'آزمایشگاه', 'lab'],
    ['progress', 'پیشرفت', 'chart'],
    ['planner', 'برنامه', 'book']
  ];
  for (const [act, label, ico] of bottomActions) {
    const a = el('a', '');
    a.href = '#' + act;
    a.dataset.action = act;
    a.append(icon(ico, 20), el('span', '', label));
    bottom.append(a);
  }

  shell.append(sidebar, appMain, bottom);
  document.body.insertBefore(shell, oldHeader || document.body.firstChild);
  oldHeader?.remove();

  function setActive(act) {
    const group = navLinks.has(act) ? act : 'home';
    for (const [id, a] of navLinks) {
      const active = id === group;
      a.classList.toggle('active', active);
      if (active) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    }
    bottom.querySelectorAll('a').forEach(a => a.classList.toggle('active', a.dataset.action === group));
    const labels = {
      home: 'خانه و داشبورد',
      paths: 'مسیرهای یادگیری',
      lab: 'آزمایشگاه و شبیه‌ساز CLI',
      progress: 'پیشرفت من',
      planner: 'برنامه مطالعه',
      glossary: 'واژه‌نامه جامع',
      coverage: 'پوشش فرمان‌های IOS'
    };
    crumbs.replaceChildren(el('span', 'crumb current', labels[group] || 'آکادمی'));
    document.title = (labels[group] || 'آکادمی') + ' — FAM Academy';
    syncSidebarProgress();
  }

  function clickExisting(id) {
    const b = $(id);
    if (b) b.click();
  }
  function showPlanner(target) {
    if (planner) {
      planner.classList.add('open');
      planner.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (target) {
      const node = $(target);
      if (node) node.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function action(act) {
    setActive(act);
    if (act === 'paths') {
      if (location.hash !== '#/paths') location.hash = '#/paths';
      else { location.hash = '#/dashboard'; location.hash = '#/paths'; }
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (act === 'lab') {
      if (location.hash !== '#/lab') location.hash = '#/lab';
      else window.FamAcademyCatalog?.renderLabWorkbench && window.dispatchEvent(new CustomEvent('fam-open-lab'));
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (act === 'home' || act === 'lessons') {
      if (location.hash !== '#/dashboard') location.hash = '#/dashboard';
      else clickExisting('btn-paths');
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (act === 'progress') {
      if (location.hash !== '#/progress') location.hash = '#/progress';
      else window.FamJourney?.renderProgress();
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (act === 'coverage') {
      clickExisting('btn-coverage');
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (act === 'sample') {
      clickExisting('btn-blueprint');
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (act === 'planner') {
      clickExisting('s4-toggle-btn');
      showPlanner();
    } else if (act === 'glossary') {
      showPlanner('s4-glossary-card');
    }
  }

  shell.addEventListener('click', (event) => {
    const a = event.target.closest('[data-action]');
    if (!a) return;
    event.preventDefault();
    action(a.dataset.action);
    if (shell.classList.contains('academy-menu-mobile-open')) {
      shell.classList.remove('academy-menu-mobile-open');
      syncMenu(false);
    }
  });

  function syncMenu(open) {
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.classList.toggle('is-collapsed', !open);
    sidebar.inert = !open;
    sidebar.setAttribute('aria-hidden', String(!open));
  }
  const mobile = window.matchMedia('(max-width: 860px)').matches;
  syncMenu(!mobile);
  menuButton.addEventListener('click', () => {
    if (window.matchMedia('(max-width: 860px)').matches) {
      const open = shell.classList.toggle('academy-menu-mobile-open');
      syncMenu(open);
    } else {
      const collapsed = shell.classList.toggle('academy-menu-collapsed');
      syncMenu(!collapsed);
    }
  });

  search.addEventListener('click', () => {
    const input = $('s4-search');
    if (input) {
      input.focus();
      input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      search.click();
    }
  });

  function syncTheme() {
    const light = document.documentElement.dataset.theme === 'light';
    theme.replaceChildren(icon(light ? 'moon' : 'sun', 18));
    theme.setAttribute('aria-label', light ? 'تغییر به تم تیره' : 'تغییر به تم روشن');
    theme.title = light ? 'تغییر به تم تیره' : 'تغییر به تم روشن';
    theme.setAttribute('aria-pressed', String(light));
  }
  syncTheme();
  theme.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem('fam.academy.theme', next);
      localStorage.setItem('fam.ui.theme', next === 'light' ? 'light' : 'original');
    } catch (_) {}
    syncTheme();
  });

  help.addEventListener('click', () => {
    let dialog = $('academy-help-dialog');
    if (!dialog) {
      dialog = el('dialog', 'card');
      dialog.id = 'academy-help-dialog';
      const close = el('button', 'btn primary', 'بستن');
      close.type = 'button';
      close.addEventListener('click', () => dialog.close());
      dialog.append(
        el('h2', '', 'راهنمای سریع آکادمی فام'),
        el('p', '', 'از منوی راست می‌توانید بین داشبورد، مسیرهای یادگیری (۱۲۷ درس)، آزمایشگاه مستقل CLI، آمار پیشرفت و واژه‌نامه جابه‌جا شوید. داخل هر درس فهرست بخش‌ها (TOC)، یادداشت شخصی، شبیه‌ساز CLI و آزمون ۱۲سؤالی در دسترس است. با کلید Ctrl+K سریع در تمام درس‌ها جست‌وجو کنید.'),
        close
      );
      document.body.append(dialog);
    }
    if (!dialog.open) dialog.showModal();
  });

  const syncHashState = () => {
    if (location.hash === '#/progress') setActive('progress');
    else if (location.hash === '#/paths') setActive('paths');
    else if (location.hash === '#/lab') setActive('lab');
    else setActive('home');
  };
  window.addEventListener('hashchange', syncHashState);
  window.addEventListener('fam-academy-progress-updated', syncSidebarProgress);
  syncHashState();
})();
