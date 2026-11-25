/* FAM Academy — interactions (vanilla JS, CSP-safe, integrated with FAM session) */
(function () {
  'use strict';

  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  /* ---------- ارقام فارسی ---------- */
  const FA = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const toFa = (n) => String(n).replace(/\d/g, d => FA[+d]);

  /* ---------- هماهنگی با نشست FAM ---------- */
  const boot = window.FAM_ACADEMY_BOOTSTRAP || {};
  const csrf = boot.csrf || '';
  const stored = boot.progress || {};

  function readSavedMissions() {
    try {
      if (typeof stored['fam3.progress.v1'] === 'string') {
        const parsed = JSON.parse(stored['fam3.progress.v1']);
        if (parsed && Array.isArray(parsed.missions)) return parsed.missions;
      }
    } catch (_) {}
    return null;
  }

  async function saveMissions(missionIndices) {
    if (!csrf) return;
    try {
      await fetch('/api/academy/progress', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-FAM-CSRF': csrf },
        body: JSON.stringify({
          changes: { 'fam3.progress.v1': JSON.stringify({ missions: missionIndices }) }
        })
      });
    } catch (_) {}
  }

  const avatarEl = $('.avatar');
  if (avatarEl && boot.userName) {
    avatarEl.title = boot.userName;
    const firstChar = String(boot.userName).trim().charAt(0);
    if (firstChar) avatarEl.textContent = firstChar;
  }

  /* ---------- دکمه بازگشت به پنل اصلی بر اساس دسترسی ---------- */
  const backFamEls = $$('[data-fam-portal]');
  const canPortal = !boot.allowedViews || boot.allowedViews.panel || boot.allowedViews.equipment;
  backFamEls.forEach(el => {
    if (!canPortal) el.style.display = 'none';
  });

  /* ---------- منوی موبایل سایت ---------- */
  const burger = $('#navBurger');
  const navLinks = $('#navLinks');
  if (burger && navLinks) {
    burger.addEventListener('click', () => {
      burger.classList.toggle('open');
      navLinks.classList.toggle('open');
    });
    navLinks.addEventListener('click', e => {
      if (e.target.tagName === 'A') {
        burger.classList.remove('open');
        navLinks.classList.remove('open');
      }
    });
  }

  /* ---------- هایلایت لینک فعال هنگام اسکرول ---------- */
  const sections = $$('section[id]');
  const navAnchors = $$('.nav-links a[href^="#"]');
  if (sections.length && navAnchors.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        navAnchors.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + en.target.id));
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    sections.forEach(s => io.observe(s));
  }

  /* ---------- انیمیشن ورود (reveal) ---------- */
  const reveals = $$('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('in'));
  }

  /* ---------- شمارنده‌ها ---------- */
  const counters = $$('[data-count]');
  const runCounter = el => {
    const target = +el.dataset.count;
    const suffix = el.dataset.suffix || '';
    const dur = 1600;
    const t0 = performance.now();
    const tick = now => {
      const p = Math.min((now - t0) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const val = Math.round(target * eased);
      el.textContent = toFa(val.toLocaleString('en-US')) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if (counters.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) { runCounter(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.5 });
    counters.forEach(el => io.observe(el));
  } else {
    counters.forEach(runCounter);
  }

  /* ---------- پر شدن نوارها و حلقه‌ها هنگام دیده‌شدن ---------- */
  const fillBars = root => {
    $$('.bar i[data-w]', root).forEach(i => { i.style.width = i.dataset.w + '%'; });
    $$('.ring .fg[data-pct]', root).forEach(c => {
      const pct = +c.dataset.pct;
      c.style.strokeDashoffset = String(339 - 339 * pct / 100);
    });
    $$('.wbar[data-h]', root).forEach(b => { b.style.height = b.dataset.h + '%'; });
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) { fillBars(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.25 });
    $$('.card, .continue, .course-row, .view.active').forEach(el => io.observe(el));
  }
  setTimeout(() => fillBars(document), 350);

  /* ---------- تایپ زندهٔ ترمینال هیرو ---------- */
  const typeTarget = $('#typeTarget');
  if (typeTarget) {
    const lines = [
      'R1> enable',
      'R1# configure terminal',
      'R1(config)# interface g0/0',
      'R1(config-if)# ip address 10.0.0.1 255.255.255.0',
      'R1(config-if)# no shutdown',
      '%LINK-5-CHANGED: Interface Gi0/0, changed state to up',
      'R1(config-if)# exit',
      'R1# write memory  [OK]'
    ];
    let li = 0, ci = 0, out = '';
    const step = () => {
      if (li >= lines.length) {
        setTimeout(() => { out = ''; li = 0; ci = 0; typeTarget.textContent = ''; step(); }, 3400);
        return;
      }
      const line = lines[li];
      if (ci <= line.length) {
        typeTarget.textContent = out + line.slice(0, ci);
        ci++;
        setTimeout(step, line[ci - 1] === ' ' ? 14 : 26);
      } else {
        out += line + '\n';
        li++; ci = 0;
        setTimeout(step, 420);
      }
    };
    setTimeout(step, 700);
  }

  /* ================= داشبورد ================= */
  const side = $('#side');
  const sideToggle = $('#sideToggle');
  if (side && sideToggle) {
    sideToggle.addEventListener('click', () => side.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (window.innerWidth > 900) return;
      if (!side.contains(e.target) && !sideToggle.contains(e.target)) side.classList.remove('open');
    });
  }

  const titles = {
    home:     ['داشبورد', 'خانه ← نمای کلی'],
    courses:  ['دوره‌های من', 'یادگیری ← دوره‌ها'],
    lab:      ['آزمایشگاه', 'یادگیری ← آزمایشگاه شبیه‌ساز'],
    progress: ['پیشرفت', 'حساب ← آمار پیشرفت']
  };

  const gotoView = name => {
    const panel = $('[data-panel="' + name + '"]');
    if (!panel) return;
    $$('.view').forEach(v => v.classList.toggle('active', v === panel));
    $$('.snav[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === name));
    const t = titles[name] || ['داشبورد', ''];
    const titleEl = $('#viewTitle'), crumbEl = $('#viewCrumb');
    if (titleEl) titleEl.textContent = t[0];
    if (crumbEl) crumbEl.textContent = t[1];
    panel.querySelectorAll('.reveal').forEach(el => el.classList.remove('in'));
    requestAnimationFrame(() => {
      panel.querySelectorAll('.reveal').forEach((el, i) => setTimeout(() => el.classList.add('in'), i * 70));
      fillBars(panel);
    });
    if (side) side.classList.remove('open');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  $$('.snav[data-view]').forEach(btn => {
    btn.addEventListener('click', () => gotoView(btn.dataset.view));
  });
  $$('[data-goto]').forEach(el => {
    el.addEventListener('click', e => { e.preventDefault(); gotoView(el.dataset.goto); });
  });

  /* ---------- دکمه‌های بدون inline handler (سازگار با CSP) ---------- */
  $$('[data-action-alert]').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      alert(el.dataset.actionAlert);
    });
  });

  $$('[data-noop-link]').forEach(el => {
    el.addEventListener('click', e => e.preventDefault());
  });

  /* ---------- مأموریت‌ها (تعاملی + ذخیره در سرور FAM) ---------- */
  const missionEls = $$('.mission');
  function syncMissionsSummary() {
    const total = missionEls.length;
    if (!total) return;
    const done = $$('.mission.done').length;
    const foot = $('.missions-foot .bar i');
    if (foot) foot.style.width = Math.round(done / total * 100) + '%';
    const label = $('.missions-foot span');
    if (label) label.textContent = toFa(done) + ' از ' + toFa(total) + ' — تا پایان امروز';
  }
  const savedMissions = readSavedMissions();
  if (savedMissions && missionEls.length) {
    missionEls.forEach((m, idx) => m.classList.toggle('done', savedMissions.includes(idx)));
    syncMissionsSummary();
  }
  missionEls.forEach(m => {
    m.addEventListener('click', () => {
      m.classList.toggle('done');
      syncMissionsSummary();
      const doneIndices = missionEls
        .map((el, idx) => (el.classList.contains('done') ? idx : -1))
        .filter(idx => idx >= 0);
      saveMissions(doneIndices);
    });
  });

  /* ---------- جستجوی سریع (Ctrl+K) ---------- */
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      const s = $('.search input');
      if (s) { e.preventDefault(); s.focus(); }
    }
  });
})();
