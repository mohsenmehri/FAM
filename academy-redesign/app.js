/* FAM Academy — interactions (vanilla JS, no dependencies) */
(function () {
  'use strict';

  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  /* ---------- ارقام فارسی ---------- */
  const FA = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const toFa = (n) => String(n).replace(/\d/g, d => FA[+d]);

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
  const navAnchors = $$('.nav-links a');
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
  // فوراً هر چیزی که الان دیده می‌شود
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
    // ریست انیمیشن‌ها و پر شدن نوارهای ویوی جدید
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

  /* ---------- مأموریت‌ها (دمو تعاملی) ---------- */
  $$('.mission').forEach(m => {
    m.addEventListener('click', () => {
      m.classList.toggle('done');
      const total = $$('.mission').length;
      const done = $$('.mission.done').length;
      const foot = $('.missions-foot .bar i');
      if (foot) foot.style.width = Math.round(done / total * 100) + '%';
      const label = $('.missions-foot span');
      if (label) label.textContent = toFa(done) + ' از ' + toFa(total) + ' — تا پایان امروز';
    });
  });

  /* ---------- جستجوی سریع (Ctrl+K فقط نمایش پیام نمونه) ---------- */
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      const s = $('.search input');
      if (s) { e.preventDefault(); s.focus(); }
    }
  });
})();
