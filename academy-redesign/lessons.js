/* FAM Academy — Lesson viewer logic */
(function () {
  'use strict';
  const C = window.FAM_CURR;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const KEY = 'fam-lessons-v1';

  /* ---------- progress ---------- */
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || { done: {}, quiz: {} }; }
    catch (e) { return { done: {}, quiz: {} }; }
  }
  function save(p) {
    localStorage.setItem(KEY, JSON.stringify(p));
    window.dispatchEvent(new CustomEvent('fam-lessons-updated'));
    renderProgress();
  }

  /* ---------- flat index ---------- */
  const flat = [];
  C.faculties.forEach((f) => f.lessons.forEach((l) => flat.push({ f, l })));
  const pos = (id) => flat.findIndex((x) => x.l.id === id);

  /* ---------- icons for 11 sections ---------- */
  const SEC_META = [
    ['goal', '🎯', 'هدف جلسه'],
    ['prereq', '🧭', 'پیش‌نیازها'],
    ['concept', '💡', 'مفهوم اصلی'],
    ['protocol', '📡', 'پروتکل و بررسی'],
    ['ios', '⌨️', 'دستورات کلیدی'],
    ['diagram', '🗺️', 'نمودار'],
    ['lab', '🧪', 'آزمایشگاه'],
    ['trouble', '🩹', 'عیب‌یابی'],
    ['exercise', '✍️', 'تمرین'],
    ['quiz', '❓', 'آزمون'],
    ['notes', '📌', 'یادداشت‌ها'],
  ];

  /* ---------- block renderer ---------- */
  function renderBlocks(blocks) {
    if (!Array.isArray(blocks)) return '';
    return blocks.map((b) => {
      if (!Array.isArray(b)) return '';
      const t = b[0];
      if (t === 'p') return '<p>' + b[1] + '</p>';
      if (t === 'h3') return '<h3>' + esc(b[1]) + '</h3>';
      if (t === 'ul') return '<ul>' + b[1].map((x) => '<li>' + x + '</li>').join('') + '</ul>';
      if (t === 'ol') return '<ol>' + b[1].map((x) => '<li>' + x + '</li>').join('') + '</ol>';
      if (t === 'note') {
        const tag = b[1] === 'tip' ? 'نکته' : b[1] === 'warn' ? 'هشدار' : 'کلیدی';
        return '<div class="note ' + b[1] + '"><b class="tag">' + tag + '</b>' + b[2] + '</div>';
      }
      if (t === 'cli') {
        return '<div class="cli"><div class="cli-cap"><span>' + esc(b[1]) + '</span>' +
          '<button class="cp" type="button">کپی</button></div><pre>' + esc(b[2]) + '</pre></div>';
      }
      if (t === 'svg') {
        const svg = C.DIAGRAMS[b[1]];
        if (!svg) return '';
        return '<div class="dia">' + svg + '<div class="cap">' + esc(b[2] || 'نمودار مفهومی — برای بزرگ‌نمایی کلیک کن') + '</div></div>';
      }
      if (t === 'table') {
        const head = b[1], rows = b[2] || [];
        return '<div class="tbl-wrap"><table><thead><tr>' +
          head.map((h) => '<th>' + h + '</th>').join('') + '</tr></thead><tbody>' +
          rows.map((r) => '<tr>' + r.map((c) => '<td>' + c + '</td>').join('') + '</tr>').join('') +
          '</tbody></table></div>';
      }
      if (t === 'labs') {
        return b[1].map((lab) =>
          '<div class="lab"><div class="lt">🧪 ' + esc(lab.t) + '</div><ol>' +
          lab.steps.map((s) => '<li>' + s + '</li>').join('') + '</ol></div>').join('');
      }
      if (t === 'quiz') return b[1].map((it, i) => renderQuiz(it, i)).join('');
      if (t === 'faq') {
        return '<div class="faq">' + b[1].map((qa) =>
          '<details><summary>' + esc(qa.q) + '</summary><p>' + qa.a + '</p></details>').join('') + '</div>';
      }
      return '';
    }).join('');
  }

  /* ---------- quiz ---------- */
  function renderQuiz(it, i) {
    const id = 'q-' + Math.random().toString(36).slice(2, 9);
    return '<div class="quiz" data-a="' + it.a + '" data-i="' + i + '">' +
      '<div class="q">' + esc(it.q) + '</div>' +
      '<div class="opts">' + it.opts.map((o, j) =>
        '<label class="opt"><input type="radio" name="' + id + '" value="' + j + '"><span>' + o + '</span></label>').join('') +
      '</div>' +
      '<div class="acts"><button class="btn chk" type="button">بررسی پاسخ</button>' +
      '<button class="btn ghost rst" type="button">تلاش دوباره</button>' +
      '<span class="qscore"></span></div>' +
      '<div class="exp">✅ <b>درست.</b> ' + esc(it.exp) + '</div>' +
      '</div>';
  }

  function wireQuizzes(root, lessonId) {
    $$('.quiz', root).forEach((q, qi) => {
      const a = parseInt(q.dataset.a, 10);
      const exp = $('.exp', q);
      $('.chk', q).addEventListener('click', () => {
        const sel = $('input:checked', q);
        if (!sel) { $('.qscore', q).textContent = 'اول یک گزینه را انتخاب کن'; return; }
        const v = parseInt(sel.value, 10);
        q.classList.add('answered');
        $$('.opt', q).forEach((o, j) => {
          o.classList.remove('right', 'wrong');
          if (j === a) o.classList.add('right');
          else if (j === v) o.classList.add('wrong');
        });
        if (v === a) {
          exp.innerHTML = '✅ <b>درست!</b> ' + esc(q.dataset.exp || '');
          $('.qscore', q).textContent = '+۱';
        } else {
          exp.innerHTML = '❌ <b>نادرست.</b> پاسخ درست گزینهٔ ' + (a + 1) + ' است. ' + esc(q.dataset.exp || '');
          $('.qscore', q).textContent = '';
        }
        // persist lesson-quiz score
        const p = load();
        if (!p.quiz[lessonId]) p.quiz[lessonId] = { done: 0, right: 0 };
        p.quiz[lessonId].done = Math.max(p.quiz[lessonId].done, qi + 1);
        if (v === a) p.quiz[lessonId].right = Math.max(p.quiz[lessonId].right, qi + 1);
        save(p);
      });
      $('.rst', q).addEventListener('click', () => {
        q.classList.remove('answered');
        $$('input', q).forEach((i) => (i.checked = false));
        $$('.opt', q).forEach((o) => o.classList.remove('right', 'wrong'));
        $('.qscore', q).textContent = '';
      });
    });
    // attach exp text to dataset
    $$('.quiz', root).forEach((q, i) => {
      const blocks = lessonQuizBlocks;
      if (blocks && blocks[i]) q.dataset.exp = blocks[i].exp;
    });
    // copy buttons
    $$('.cli .cp', root).forEach((btn) => {
      btn.addEventListener('click', () => {
        const pre = btn.closest('.cli').querySelector('pre');
        navigator.clipboard && navigator.clipboard.writeText(pre.textContent);
        btn.textContent = 'شد ✓';
        setTimeout(() => (btn.textContent = 'کپی'), 1400);
      });
    });
  }
  let lessonQuizBlocks = null;

  /* ---------- tree ---------- */
  const FA_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const faNum = (n) => String(n).split('').map((d) => FA_DIGITS[+d] || d).join('');

  function renderTree() {
    const p = load();
    const tree = $('#tree');
    tree.innerHTML = C.faculties.map((f, fi) => {
      const open = flat.some((x) => x.f.id === f.id && x.l.id === currentId) || f.id === 'f0';
      return '<div class="fac' + (open ? ' open' : '') + '" data-f="' + f.id + '">' +
        '<button class="fac-head" type="button">' +
        '<span class="num">' + faNum(fi) + '</span>' +
        '<span class="ft">' + f.title + '<span class="fd">' + f.duration + ' · ' + f.tag + '</span></span>' +
        '<span class="chev">◀</span></button>' +
        '<div class="lessons">' + f.lessons.map((l) => {
          const done = p.done[l.id];
          return '<button class="lnk' + (l.id === currentId ? ' active' : '') + (done ? ' is-done' : '') +
            '" data-id="' + l.id + '" type="button">' +
            '<span class="mn">' + (l.minutes || '').split('·')[0].trim().slice(0, 6) + '</span>' +
            '<span class="pt">' + l.title + '</span><span class="done">✓</span></button>';
        }).join('') + '</div></div>';
    }).join('');
    $$('.fac-head', tree).forEach((h) =>
      h.addEventListener('click', () => h.parentElement.classList.toggle('open')));
    $$('.lnk', tree).forEach((b) =>
      b.addEventListener('click', () => (location.hash = '#/l/' + b.dataset.id)));
    renderProgress();
  }

  function renderProgress() {
    const p = load();
    const total = flat.length;
    const done = flat.filter((x) => p.done[x.l.id]).length;
    const pct = Math.round((done / total) * 100);
    const bar = $('#bar i'); if (bar) bar.style.width = pct + '%';
    const lab = $('#barLabel'); if (lab) lab.textContent = done + ' / ' + total + ' درس (' + pct + '%)';
  }

  /* ---------- lesson view ---------- */
  let currentId = null;

  function renderHome() {
    currentId = null;
    const stages = (C.meta.master || []).map((m) =>
      '<button class="mr-stage" data-to="' + m.to + '" type="button">' +
      '<span class="mr-n">' + m.n + '</span>' +
      '<b>' + m.en + '</b><i>' + m.fa + '</i>' +
      '<p>' + m.desc + '</p>' +
      '<span class="mr-go">شروع مرحله ←</span>' +
      '</button>').join('');
    $('#view').innerHTML =
      '<div class="home">' +
      '<div class="hero"><span class="chip">🎓 Cisco Master Roadmap — نقشهٔ نهایی</span>' +
      '<h1>از صفر تا متخصص ارشد شبکه</h1>' +
      '<p>هشت مرحلهٔ نهایی، روزانه ۲ ساعت، فارسی با اصطلاحات انگلیسی — از مبانی شبکه تا جایگاه ' +
      '<b>Principal Network Architect</b>. هر درس یازده بخش استاندارد دارد: هدف، پیش‌نیاز، مفهوم، پروتکل، ' +
      'دستورات، نمودار، آزمایشگاه واقعی، عیب‌یابی، تمرین، آزمون و یادداشت؛ و اثبات رفتار پروتکل با CLI یا Packet Capture.</p></div>' +
      '<div class="mr"><div class="mr-head"><h2>🗺️ Cisco Master Roadmap</h2>' +
      '<span>۸ مرحله · صفر تا متخصص ارشد</span></div>' +
      '<div class="mr-stages">' + stages + '</div></div>' +
      '<div class="mr-head" style="margin-top:6px"><h2>📚 دانشکده‌ها و درس‌ها</h2>' +
      '<span>' + flat.length + ' درس در ۹ دانشکده</span></div>' +
      '<div class="cards">' + C.faculties.map((f, fi) =>
        '<button class="card" data-f="' + f.id + '" type="button">' +
        '<span class="n">دانشکدهٔ ' + faNum(fi) + ' · ' + f.tag + '</span>' +
        '<b>' + f.title + '</b><span>' + f.intro.slice(0, 90) + '…</span>' +
        '<span class="meta"><span>📚 ' + f.lessons.length + ' درس</span><span>⏱ ' + f.duration + '</span></span>' +
        '</button>').join('') + '</div></div>';
    $$('.mr-stage').forEach((b) =>
      b.addEventListener('click', () => (location.hash = '#/l/' + b.dataset.to)));
    $$('.card', $('#view')).forEach((c) =>
      c.addEventListener('click', () => {
        const f = C.faculties.find((x) => x.id === c.dataset.f);
        if (f && f.lessons[0]) location.hash = '#/l/' + f.lessons[0].id;
      }));
    $$('.lnk').forEach((b) => b.classList.remove('active'));
    document.title = 'کلاس‌ها — آکادمی FAM';
  }

  function renderLesson(id) {
    const idx = pos(id);
    if (idx < 0) return renderHome();
    const { f, l } = flat[idx];
    currentId = id;
    const p = load();

    const secs = SEC_META.map(([k, ic, label]) => {
      const blocks = l.sec[k];
      if (!blocks) return '';
      if (k === 'quiz') lessonQuizBlocks = blocks[0] && blocks[0][0] === 'quiz' ? blocks[0][1] : blocks;
      return '<section class="sec" id="s-' + k + '"><h2><span class="ic">' + ic + '</span>' + label +
        '<small style="margin-inline-start:auto;color:var(--dim);font-size:11px;font-weight:400">بخش ' +
        (SEC_META.findIndex((x) => x[0] === k) + 1) + ' از ۱۱</small></h2>' +
        renderBlocks(blocks) + '</section>';
    }).join('');

    const faqHtml = l.faq && l.faq.length
      ? '<section class="sec"><h2><span class="ic">❓</span>سوالات متداول</h2>' +
        renderBlocks([['faq', l.faq]]) + '</section>' : '';

    const prev = flat[idx - 1], next = flat[idx + 1];
    $('#view').innerHTML =
      '<div class="l-head">' +
      '<span class="chip">🎓 دانشکدهٔ ' + faNum(C.faculties.indexOf(f)) + ' — ' + f.tag + '</span>' +
      '<h1>' + l.title + '</h1>' +
      '<div class="sub"><span>📁 ' + f.title + '</span><span>⏱ ' + (l.minutes || '') + '</span>' +
      '<span>🔖 ' + (l.sub || '') + '</span></div>' +
      '<div class="l-lead">' + l.lead + '</div>' +
      (p.done[id] ? '' : '<div style="margin-top:12px"><button class="btn" id="markDone" type="button">✓ درس را تمام کردم</button></div>') +
      '</div>' +
      secs + faqHtml +
      '<div class="lnav">' +
      (prev ? '<a href="#/l/' + prev.l.id + '"><small>قبلی</small>' + prev.l.title + '</a>' : '<span></span>') +
      (next ? '<a class="next" href="#/l/' + next.l.id + '"><small>بعدی</small>' + next.l.title + '</a>' : '<span></span>') +
      '</div>';

    wireQuizzes($('#view'), id);
    const md = $('#markDone');
    if (md) md.addEventListener('click', () => {
      const pp = load(); pp.done[id] = Date.now(); save(pp);
      md.outerHTML = '<span class="chip" style="border-color:rgba(52,211,153,.5);color:var(--gr);background:rgba(52,211,153,.1)">✓ درس تکمیل شد</span>';
      renderTree();
    });
    $$('.lnk').forEach((b) => b.classList.toggle('active', b.dataset.id === id));
    document.title = l.title + ' — آکادمی FAM';
    $('#view').scrollIntoView({ block: 'start' });
    window.scrollTo(0, 0);
  }

  /* ---------- router ---------- */
  function route() {
    const h = location.hash || '';
    if (h.startsWith('#/l/')) renderLesson(h.slice(4));
    else renderHome();
    renderTree();
  }

  /* ---------- theme ---------- */
  function initTheme() {
    const t = localStorage.getItem('fam-theme') || 'dark';
    document.documentElement.dataset.theme = t;
    $('#themeBtn').textContent = t === 'dark' ? '☀' : '☾';
    $('#themeBtn').addEventListener('click', () => {
      const n = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = n;
      localStorage.setItem('fam-theme', n);
      $('#themeBtn').textContent = n === 'dark' ? '☀' : '☾';
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    window.addEventListener('hashchange', route);
    route();
  });
})();
