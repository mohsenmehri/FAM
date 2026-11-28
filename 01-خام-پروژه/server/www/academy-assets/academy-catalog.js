(() => {
  'use strict';
  const STORAGE_KEY = 'fam_academy_progress_v1';
  const MISSION_KEY = 'fam.academy.missions.v1';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const normSearch = s => String(s || '').replace(/[\u200c\u0640]/g, '').replace(/ي/g, 'ی').replace(/ك/g, 'ک').replace(/[إأآ]/g, 'ا').replace(/ة/g, 'ه').toLowerCase().trim();
  const missionStorageKey = () => `${MISSION_KEY}.${window.FamAcademyBridge?.user?.username || 'guest'}`;

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
    const d = 'M12 4a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM5 16a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM19 16a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM10 9 7 16 M14 9l3 7 M8 19h8';
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;
  }

  function liveTopologySvg() {
    const simTotal = Number(window.FamAcademySimulator?.commandCount || 0) + 10;
    return `
      <div class="hero-topo-wrap">
        <svg class="hero-topo-svg" viewBox="0 0 640 360" role="img" aria-label="نمودار نمادین ساختار مسیرهای یادگیری شبکه از لایه دسترسی تا هسته">
          <defs>
            <linearGradient id="famLinkG" x1="0" y1="0" x2="1" y2="0">
              <stop stop-color="#00d4ff"/><stop offset="1" stop-color="#3b82f6"/>
            </linearGradient>
            <linearGradient id="famNodeG" x1="0" y1="0" x2="0" y2="1">
              <stop stop-color="#132038"/><stop offset="1" stop-color="#0a1222"/>
            </linearGradient>
          </defs>
          <g fill="none" stroke="url(#famLinkG)" stroke-width="2.2" stroke-linecap="round" opacity="0.88">
            <path id="topoL1" d="M320 68 V130"/>
            <path id="topoL2" d="M292 178 C240 202 195 215 154 232"/>
            <path id="topoL3" d="M348 178 C400 202 445 215 486 232"/>
            <path id="topoL4" d="M132 280 C108 300 92 312 82 325"/>
            <path id="topoL5" d="M174 280 C216 300 264 312 300 325"/>
            <path id="topoL6" d="M466 280 C424 300 376 312 340 325"/>
            <path id="topoL7" d="M508 280 C532 300 548 312 558 325"/>
          </g>
          <g class="topo-packet-layer" aria-hidden="true">
            <circle r="4.5" fill="#7df9ff"><animateMotion dur="2.6s" repeatCount="indefinite"><mpath href="#topoL1"/></animateMotion></circle>
            <circle r="4.2" fill="#34d399"><animateMotion dur="3.2s" repeatCount="indefinite" begin="0.5s"><mpath href="#topoL2"/></animateMotion></circle>
            <circle r="4.2" fill="#fbbf24"><animateMotion dur="3.2s" repeatCount="indefinite" begin="1.4s"><mpath href="#topoL3"/></animateMotion></circle>
            <circle r="3.8" fill="#a78bfa"><animateMotion dur="2.9s" repeatCount="indefinite" begin="0.9s"><mpath href="#topoL5"/></animateMotion></circle>
            <circle r="3.8" fill="#38bdf8"><animateMotion dur="2.9s" repeatCount="indefinite" begin="1.9s"><mpath href="#topoL6"/></animateMotion></circle>
          </g>
          <!-- Core Router -->
          <g transform="translate(242,16)">
            <rect width="156" height="52" rx="12" fill="url(#famNodeG)" stroke="#00d4ff" stroke-width="1.6"/>
            <circle cx="18" cy="26" r="4.5" fill="#34d399"/>
            <text x="86" y="23" text-anchor="middle" fill="#e9f0fb" font-size="12" font-weight="800" font-family="ui-monospace,monospace">CORE-BGP-R1</text>
            <text x="86" y="40" text-anchor="middle" fill="#7dd3fc" font-size="10" font-family="ui-monospace,monospace">AS 65001 · MPLS/SR</text>
          </g>
          <!-- Distribution -->
          <g transform="translate(232,128)">
            <rect width="176" height="52" rx="12" fill="url(#famNodeG)" stroke="#3b82f6" stroke-width="1.6"/>
            <circle cx="18" cy="26" r="4.5" fill="#00d4ff"/>
            <text x="96" y="23" text-anchor="middle" fill="#e9f0fb" font-size="12" font-weight="800" font-family="ui-monospace,monospace">DIST-OSPF-SW0</text>
            <text x="96" y="40" text-anchor="middle" fill="#93c5fd" font-size="10" font-family="ui-monospace,monospace">Area 0 · VRF · HSRP</text>
          </g>
          <!-- Access Left -->
          <g transform="translate(68,230)">
            <rect width="168" height="50" rx="12" fill="url(#famNodeG)" stroke="#34d399" stroke-width="1.4"/>
            <text x="84" y="22" text-anchor="middle" fill="#e9f0fb" font-size="11.5" font-weight="800" font-family="ui-monospace,monospace">ACCESS-L2-SW1</text>
            <text x="84" y="38" text-anchor="middle" fill="#6ee7b7" font-size="10" font-family="ui-monospace,monospace">VLAN 10/20 · RSTP</text>
          </g>
          <!-- Access Right -->
          <g transform="translate(404,230)">
            <rect width="168" height="50" rx="12" fill="url(#famNodeG)" stroke="#a78bfa" stroke-width="1.4"/>
            <text x="84" y="22" text-anchor="middle" fill="#e9f0fb" font-size="11.5" font-weight="800" font-family="ui-monospace,monospace">NETOPS-AUTO-01</text>
            <text x="84" y="38" text-anchor="middle" fill="#c4b5fd" font-size="10" font-family="ui-monospace,monospace">Ansible · Terraform</text>
          </g>
          <!-- Endpoints -->
          <g fill="#0f172a" stroke="#475569" stroke-width="1.2" font-family="ui-monospace,monospace" font-size="10">
            <rect x="24" y="322" width="116" height="28" rx="8"/><text x="82" y="340" text-anchor="middle" fill="#cbd5e1">CCNA · Switching</text>
            <rect x="242" y="322" width="156" height="28" rx="8"/><text x="320" y="340" text-anchor="middle" fill="#cbd5e1">CCNP · Security/SD-WAN</text>
            <rect x="498" y="322" width="118" height="28" rx="8"/><text x="557" y="340" text-anchor="middle" fill="#cbd5e1">CCIE · CCDE</text>
          </g>
        </svg>
        <div class="hero-topo-caption">
          <span>توپولوژی نمادین مسیر یادگیری از مبانی تا معماری شبکه</span>
          <span class="ltr">CLI Sim · ${simTotal > 10 ? simTotal : 134} cmds</span>
        </div>
      </div>`;
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

  function localDateKey() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }
  function loadMissionRecord() {
    const today = localDateKey();
    const bridge = window.FamAcademyBridge;
    const remote = bridge && !bridge.offline ? bridge.progress?.labs?.dailyMissions : null;
    if (remote && remote.day === today && remote.done && typeof remote.done === 'object') {
      const cliCmds = Array.isArray(remote.cliCmds) ? remote.cliCmds.filter(Boolean) : [];
      return { day: today, done: { ...remote.done }, cliCmds, cliCount: Math.max(cliCmds.length, Number(remote.cliCount) || 0) };
    }
    try {
      const raw = JSON.parse(localStorage.getItem(missionStorageKey()) || '{}');
      if (raw.day === today && raw.done && typeof raw.done === 'object') {
        const cliCmds = Array.isArray(raw.cliCmds) ? raw.cliCmds.filter(Boolean) : [];
        return { day: today, done: raw.done, cliCmds, cliCount: Math.max(cliCmds.length, Number(raw.cliCount) || 0) };
      }
    } catch (_) {}
    return { day: today, done: {}, cliCmds: [], cliCount: 0 };
  }
  let missionSyncTimer = null;
  function saveMissionRecord(record) {
    const cliCmds = Array.isArray(record.cliCmds) ? Array.from(new Set(record.cliCmds)).slice(0, 50) : [];
    const payload = {
      day: localDateKey(),
      done: record.done || {},
      cliCmds,
      cliCount: Math.max(cliCmds.length, Number(record.cliCount) || 0)
    };
    try { localStorage.setItem(missionStorageKey(), JSON.stringify(payload)); } catch (_) {}
    const bridge = window.FamAcademyBridge;
    if (bridge && !bridge.offline && !bridge.sharedProgressLocked && typeof bridge.saveProgress === 'function') {
      const cur = bridge.progress && typeof bridge.progress === 'object' ? bridge.progress : { completed: [], labs: {} };
      const next = {
        ...cur,
        completed: Array.isArray(cur.completed) ? cur.completed : [],
        labs: { ...(cur.labs && typeof cur.labs === 'object' ? cur.labs : {}), dailyMissions: payload }
      };
      bridge.progress = next;
      clearTimeout(missionSyncTimer);
      missionSyncTimer = setTimeout(() => {
        bridge.saveProgress(next).catch(() => {});
      }, 450);
    }
  }
  function loadDailyMissions() { return loadMissionRecord().done; }
  function saveDailyMissions(doneMap) {
    const rec = loadMissionRecord();
    rec.done = doneMap;
    saveMissionRecord(rec);
  }
  if (!window.__famMissionsWired && typeof window.addEventListener === 'function') {
    window.__famMissionsWired = true;
    window.addEventListener('fam-lesson-opened', () => {
      const rec = loadMissionRecord();
      rec.done['study-one'] = true;
      saveMissionRecord(rec);
    });
    window.addEventListener('fam-cli-executed', e => {
      const det = e && e.detail ? e.detail : {};
      const cmdKey = String(det.cmd || '').trim().toLowerCase().replace(/\s+/g, ' ');
      if (!cmdKey || det.isHelp || /^(help|\?|clear|cls)$/.test(cmdKey)) return;
      const rec = loadMissionRecord();
      if (!rec.cliCmds.includes(cmdKey)) {
        rec.cliCmds.push(cmdKey);
        rec.cliCount = rec.cliCmds.length;
      }
      if (rec.cliCmds.length >= 3) rec.done['cli-practice'] = true;
      saveMissionRecord(rec);
    });
    window.addEventListener('fam-quiz-graded', e => {
      const det = e && e.detail ? e.detail : {};
      if (Number(det.answered || 0) <= 0) return;
      const rec = loadMissionRecord();
      rec.done['quiz-check'] = true;
      saveMissionRecord(rec);
    });
  }

  function renderDashboard(container, catalog, onOpenLesson) {
    const completed = getCompletedSet(), paths = catalog?.paths || [];
    const profile = window.FamAcademyBridge?.progress?.profile || {};
    const all = paths.flatMap(p => (p.courses || []).flatMap(c => c.lessons || []));
    const chosen = paths.find(p => p.id === profile.goal) || paths[0];
    const focusedCourse = chosen?.id === 'fam-c5' && profile.focusStage && profile.focusStage !== 'all'
      ? (chosen.courses || []).find(c => c.id === profile.focusStage)
      : null;
    const target = focusedCourse
      ? (focusedCourse.lessons || [])
      : (chosen?.courses || []).flatMap(c => c.lessons || []);
    const assessed = new Set(window.FamAcademyBridge?.progress?.selfAssessed || []);
    const ready = item => (item.prerequisites || []).every(id => completed.has(id) || assessed.has(id));
    const next = target.find(l => !completed.has(l.id) && l.blueprint && ready(l))
      || target.find(l => !completed.has(l.id) && l.blueprint)
      || all.find(l => !completed.has(l.id) && l.blueprint && ready(l));
    const doneAll = all.filter(l => completed.has(l.id)).length;
    const doneTarget = target.filter(l => completed.has(l.id)).length;
    const pctTarget = target.length ? Math.round(doneTarget / target.length * 100) : 0;
    const user = window.FamAcademyBridge?.user?.username || '';
    const greeting = user && !window.FamAcademyBridge?.offline ? `سلام ${esc(user)}؛ ` : '';
    const level = ({ beginner: 'سطح پایه', intermediate: 'سطح میانی', advanced: 'سطح پیشرفته' })[profile.level] || 'مسیر منعطف';
    const nodes = target.slice(0, 6);
    const missionRec = loadMissionRecord();
    const missionsState = missionRec.done;
    const cliCount = Math.min(3, missionRec.cliCount || 0);
    const dailyMissions = [
      { id: 'study-one', title: 'مطالعه حداقل ۱ درس و مرور بخش‌های کلیدی', badge: missionsState['study-one'] ? 'ثبت خودکار ✓' : '۲۰ دقیقه' },
      { id: 'cli-practice', title: 'اجرای حداقل ۳ فرمان متمایز در شبیه‌ساز CLI', badge: missionsState['cli-practice'] ? '۳/۳ ✓' : `${cliCount.toLocaleString('fa-IR')}/۳ عملی` },
      { id: 'quiz-check', title: 'پاسخ‌دهی به آزمون ۱۲سؤالی یک درس و بررسی نکات', badge: missionsState['quiz-check'] ? 'ثبت خودکار ✓' : 'ارزیابی' }
    ];

    container.innerHTML = `
      <div class="fa-dashboard journey-dashboard reference-home">
        <section class="reference-hero">
          <div class="reference-welcome">
            <span class="hero-badge-pill"><i class="kicker-dot"></i> طرح جامع آکادمی شبکه · ${esc(chosen?.code || 'Curriculum 5.0')} · ${esc(level)}</span>
            <h1>${greeting}مسیر مهندسی شبکه، از <em>اولین پکت</em> تا <em>معماری Expert</em></h1>
            <p>آموزش ساختارمند در ${all.length.toLocaleString('fa-IR')} درس فعال همراه با نمودار توپولوژی، شبیه‌ساز تعاملی CLI، یادداشت شخصی، واژه‌نامه و آزمون ۱۲سؤالی.</p>
            <div class="hero-cta-row">
              ${next ? '<button class="journey-primary" id="fa-continue" type="button">ادامه یادگیری ←</button>' : ''}
              <button class="btn" id="fa-open-lab" type="button">ورود به آزمایشگاه CLI</button>
              <button class="journey-text-btn" data-journey-action="profile" type="button">تنظیم هدف و برنامه</button>
            </div>
            <ul class="hero-trust">
              <li><b>${doneAll.toLocaleString('fa-IR')} از ${all.length.toLocaleString('fa-IR')}</b><span>درس تکمیل‌شده کل</span></li>
              <li><b>${(Number(profile.minutesPerDay) || 45).toLocaleString('fa-IR')} دقیقه</b><span>برنامه روزانه شما</span></li>
              <li><b>${pctTarget.toLocaleString('fa-IR')}٪</b><span>پیشرفت مسیر انتخابی</span></li>
            </ul>
          </div>
          ${liveTopologySvg()}
        </section>

        <section class="home-missions-grid">
          <article class="mission-card">
            <span class="journey-kicker">DAILY MISSIONS</span>
            <h2 style="margin:4px 0 2px;font-size:18px">مأموریت‌های مطالعه امروز</h2>
            <p style="margin:0;font-size:12.5px;color:var(--muted)">با مطالعه درس، اجرای ۳ فرمان CLI و ثبت آزمون به‌صورت خودکار تیک می‌خورند (قابل ویرایش دستی)</p>
            <div class="mission-list">
              ${dailyMissions.map(m => `
                <label class="mission-item ${missionsState[m.id] ? 'is-done' : ''}">
                  <input type="checkbox" data-mission-id="${esc(m.id)}" ${missionsState[m.id] ? 'checked' : ''}>
                  <span><strong>${esc(m.title)}</strong></span>
                  <small>${esc(m.badge)}</small>
                </label>`).join('')}
            </div>
          </article>
          <aside class="reference-summary">
            <span class="journey-kicker">YOUR PROGRESS</span>
            <h3>پیشرفت مسیر فعلی</h3>
            <div class="reference-ring" style="--progress:${pctTarget}%"><span><strong>${pctTarget}٪</strong><small>تکمیل مسیر</small></span></div>
            <p>${doneTarget.toLocaleString('fa-IR')} از ${target.length.toLocaleString('fa-IR')} درس تکمیل‌شده</p>
            <button class="journey-link" data-journey-action="progress" type="button">مشاهده آمار کامل ←</button>
          </aside>
        </section>

        <section class="reference-track">
          <div class="journey-heading">
            <div><h2>نمای سریع مسیر یادگیری</h2><p>${esc(focusedCourse ? focusedCourse.title : (chosen?.title || ''))}</p></div>
            <button class="journey-link" data-journey-path="${esc(chosen?.id || '')}" type="button">مشاهده تمام درس‌ها ←</button>
          </div>
          <div class="journey-track" aria-label="نمایی از مسیر یادگیری">
            ${nodes.map(l => `
              <button class="journey-node ${completed.has(l.id) ? 'is-done' : next?.id === l.id ? 'is-current' : ''}" data-journey-lesson="${esc(l.id)}" type="button">
                <span class="journey-node-dot">${completed.has(l.id) ? '✓' : lessonIcon(l.id)}</span>
                <strong>${esc(l.title)}</strong>
                <small>${completed.has(l.id) ? 'تکمیل‌شده' : next?.id === l.id ? 'گام پیشنهادی' : ready(l) ? 'آماده مطالعه' : 'پیش‌نیاز دارد'}</small>
              </button>`).join('')}
          </div>
        </section>

        <section class="reference-cards">
          <article class="reference-next">
            <span class="journey-kicker">UP NEXT</span>
            <h2>درس پیشنهادی بعدی</h2>
            ${next ? `
              <div class="reference-next-content">
                <span class="reference-topic-icon">⌘</span>
                <div>
                  <h3>${esc(next.title)}</h3>
                  <p>مطالعه درس همراه با فهرست بخش‌ها، یادداشت شخصی، شبیه‌ساز CLI و آزمون ۱۲سؤالی.</p>
                  <button class="journey-primary small" data-journey-lesson="${esc(next.id)}" type="button">شروع درس ←</button>
                </div>
              </div>` : '<p>تمام درس‌های آماده این مسیر تکمیل شده‌اند.</p>'}
          </article>
          <article class="reference-plan">
            <span class="journey-kicker">YOUR ROUTINE</span>
            <h2>برنامه مطالعه</h2>
            <p>هدف روزانه تنظیم‌شده</p>
            <div class="reference-plan-number">${Number(profile.minutesPerDay) || 45} <small>دقیقه</small></div>
            <p>${Number(profile.daysPerWeek) || 5} روز در هفته</p>
            <button class="journey-link" data-journey-action="profile" type="button">ویرایش برنامه ←</button>
          </article>
        </section>

        <section class="journey-paths">
          <div class="journey-heading"><div><h2>دانشکده‌ها و مسیرهای آموزشی</h2><p>انتخاب مسیر برای مشاهده نقشه پیش‌نیازها و فهرست کامل درس‌ها</p></div></div>
          <div class="journey-path-grid">
            ${paths.map((p, i) => {
              const prog = calcPathProgress(p, completed);
              return `
                <article class="journey-path">
                  <span class="journey-path-mark">${i ? '⚡' : '◈'}</span>
                  <div>
                    <small>${esc(p.code)} · ${esc(p.level)}</small>
                    <h3>${esc(p.title)}</h3>
                    <p>${prog.done.toLocaleString('fa-IR')} از ${prog.total.toLocaleString('fa-IR')} درس تکمیل‌شده (${prog.pct}٪)</p>
                    <div class="fa-progress" style="margin-top:8px"><span style="width:${prog.pct}%"></span></div>
                  </div>
                  <button class="journey-link" data-open-path="${esc(p.id)}" type="button">نقشه مسیر ←</button>
                </article>`;
            }).join('')}
          </div>
        </section>
      </div>`;

    container.querySelectorAll('[data-mission-id]').forEach(cb => {
      cb.addEventListener('change', () => {
        missionsState[cb.dataset.missionId] = cb.checked;
        saveDailyMissions(missionsState);
        cb.closest('.mission-item')?.classList.toggle('is-done', cb.checked);
      });
    });
    container.querySelectorAll('[data-open-path], [data-journey-path]').forEach(btn => {
      btn.onclick = () => {
        const path = paths.find(p => p.id === (btn.dataset.openPath || btn.dataset.journeyPath));
        if (path) renderPathRoadmap(container, path, () => renderDashboard(container, catalog, onOpenLesson), onOpenLesson, catalog);
      };
    });
    container.querySelectorAll('[data-journey-lesson]').forEach(btn => {
      btn.onclick = () => {
        const lesson = all.find(l => l.id === btn.dataset.journeyLesson);
        if (lesson?.blueprint) onOpenLesson(lesson.blueprint);
      };
    });
    container.querySelectorAll('[data-journey-action]').forEach(btn => {
      btn.onclick = () => {
        if (btn.dataset.journeyAction === 'profile') window.FamJourney?.openProfile();
        else location.hash = '#/progress';
      };
    });
    const continueBtn = container.querySelector('#fa-continue');
    if (continueBtn && next) continueBtn.onclick = () => onOpenLesson(next.blueprint);
    const labBtn = container.querySelector('#fa-open-lab');
    if (labBtn) labBtn.onclick = () => { location.hash = '#/lab'; };
  }

  function renderPathRoadmap(container, path, onBack, onOpenLesson, catalog) {
    const completed = getCompletedSet(), prog = calcPathProgress(path, completed);
    let index = 0;
    const allPaths = catalog?.paths || [path];
    const all = allPaths.flatMap(p => (p.courses || []).flatMap(c => c.lessons || []));
    const lessons = (path.courses || []).flatMap(c => c.lessons || []);
    const assessed = new Set(window.FamAcademyBridge?.progress?.selfAssessed || []);
    const ready = l => (l.prerequisites || []).every(id => completed.has(id) || assessed.has(id));
    const next = lessons.find(l => !completed.has(l.id) && ready(l) && l.blueprint) || lessons.find(l => !completed.has(l.id)) || lessons[0];
    const cols = 4, stepX = 210, stepY = 150, rows = Math.ceil(lessons.length / cols), graphWidth = 960, graphHeight = Math.max(230, rows * stepY + 60);
    const point = i => ({ x: 110 + (i % cols) * stepX, y: 65 + Math.floor(i / cols) * stepY });
    const lines = lessons.flatMap((l, i) => (l.prerequisites || []).map(id => {
      const j = lessons.findIndex(item => item.id === id);
      if (j < 0) return '';
      const a = point(j), b = point(i), mid = (a.x + b.x) / 2;
      return `<path d="M ${a.x} ${a.y} C ${mid} ${a.y}, ${mid} ${b.y}, ${b.x} ${b.y}" class="${completed.has(id) && completed.has(l.id) ? 'edge-done' : ''}"/>`;
    })).join('');

    const graph = `<div class="reference-map-scroll"><div class="reference-map-canvas" style="width:${graphWidth}px;height:${graphHeight}px"><svg class="reference-map-lines" viewBox="0 0 ${graphWidth} ${graphHeight}" aria-hidden="true">${lines}</svg>${lessons.map((l, i) => {
      const p = point(i), done = completed.has(l.id);
      return `<button class="reference-map-node ${done ? 'is-done' : l.id === next?.id ? 'is-current' : ''}" style="left:${p.x}px;top:${p.y}px" data-map-node="${esc(l.id)}" aria-label="${esc(l.title)}" type="button"><span class="reference-map-dot">${done ? '✓' : lessonIcon(l.id)}</span><strong>${esc(l.title)}</strong><small>${done ? 'تکمیل‌شده' : ready(l) ? 'آماده مطالعه' : 'پیش‌نیاز دارد'}</small></button>`;
    }).join('')}</div></div>`;

    container.innerHTML = `
      <div class="fa-dashboard reference-roadmap">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
          <button id="fa-catalog-back" class="fa-action" type="button">← بازگشت به داشبورد</button>
          <div class="roadmap-path-tabs" role="tablist" aria-label="تغییر مسیر آموزشی">
            ${allPaths.map(p => `<button type="button" role="tab" aria-selected="${p.id === path.id ? 'true' : 'false'}" class="roadmap-path-tab ${p.id === path.id ? 'active' : ''}" data-switch-path="${esc(p.id)}">${esc(p.title)} (${(p.courses || []).reduce((s, c) => s + (c.lessons || []).length, 0)})</button>`).join('')}
          </div>
        </div>
        <div class="reference-roadmap-heading">
          <span class="journey-kicker">LEARNING ROADMAP · ${esc(path.code)}</span>
          <h1>${esc(path.title)}</h1>
          <p>${esc(path.description || '')}</p>
        </div>
        <div class="reference-roadmap-layout">
          <section class="reference-map-main">
            <div class="reference-map-legend"><span><i class="done"></i> تکمیل‌شده</span><span><i class="current"></i> گام پیشنهادی</span><span><i></i> سایر درس‌ها</span></div>
            ${graph}
            <div class="reference-map-summary">
              <span>◷ <b>${Number(path.estimatedHours) || 0} ساعت</b><small>مدت تقریبی مسیر</small></span>
              <span>⌁ <b>${prog.pct}٪</b><small>پیشرفت کل مسیر</small></span>
              <span>◎ <b>${prog.done} از ${prog.total}</b><small>درس تکمیل‌شده</small></span>
            </div>
          </section>
          <aside class="reference-map-detail" aria-live="polite"></aside>
        </div>
        <h2 class="reference-course-title" style="margin:6px 0 0">همه درس‌های این مسیر</h2>
        ${(path.courses || []).map(course => {
          const cp = calcCourseProgress(course, completed);
          return `<section class="fa-course">
            <div class="fa-course-head"><h3>${esc(course.title)}</h3><small>${cp.done}/${cp.total} درس · ${cp.pct}٪ تکمیل</small></div>
            <div class="fa-lesson-list">
              ${(course.lessons || []).map(lesson => {
                const isDone = completed.has(lesson.id), n = ++index;
                const prereq = Array.isArray(lesson.prerequisites) && lesson.prerequisites.length ? 'پیش‌نیاز: ' + lesson.prerequisites.length + ' مبحث' : 'بدون پیش‌نیاز';
                return `<div class="fa-lesson-row">
                  <span class="fa-lesson-num">${String(n).padStart(2, '0')}</span>
                  <div class="fa-lesson-info"><strong>${esc(lesson.title)}</strong><small>${esc(prereq)} · ${isDone ? '<span class="fa-complete">تکمیل‌شده</span>' : 'آماده یادگیری'}</small></div>
                  ${lesson.blueprint ? `<button class="fa-action primary" data-open-blueprint="${esc(lesson.blueprint)}" type="button">شروع درس ←</button>` : `<button class="fa-action" data-open-unready="${esc(lesson.id)}" data-course-title="${esc(course.title)}" type="button">مشاهده سرفصل</button>`}
                </div>`;
              }).join('')}
            </div>
          </section>`;
        }).join('')}
      </div>`;

    container.querySelectorAll('[data-switch-path]').forEach(btn => {
      btn.onclick = () => {
        const nextPath = allPaths.find(p => p.id === btn.dataset.switchPath);
        if (nextPath && nextPath.id !== path.id) renderPathRoadmap(container, nextPath, onBack, onOpenLesson, catalog);
      };
    });

    const detail = container.querySelector('.reference-map-detail');
    const showDetail = lesson => {
      if (!lesson) { detail.textContent = 'درسی در این مسیر ثبت نشده است.'; return; }
      const prerequisites = (lesson.prerequisites || []).map(id => all.find(l => l.id === id)).filter(Boolean);
      const done = completed.has(lesson.id);
      detail.innerHTML = `<span class="journey-kicker">LESSON DETAILS</span><div class="reference-detail-icon">⌘</div><h2>${esc(lesson.title)}</h2><span class="reference-detail-status">${done ? 'تکمیل‌شده' : ready(lesson) ? 'آماده مطالعه' : 'پیش‌نیاز دارد'}</span><div class="fa-progress"><span style="width:${done ? 100 : 0}%"></span></div><div class="reference-detail-block"><h3>درباره این درس</h3><p>${esc(lesson.summary || lesson.description || 'محتوای آموزشی و تمرین‌های مرتبط با این مبحث.')}</p></div><div class="reference-detail-block"><h3>پیش‌نیازها</h3>${prerequisites.length ? prerequisites.map(l => `<div class="reference-prereq"><span>${esc(l.title)}</span><b>${completed.has(l.id) ? '✓' : assessed.has(l.id) ? 'خودارزیابی' : '○'}</b></div>`).join('') : '<p>پیش‌نیازی ثبت نشده است.</p>'}</div><button class="journey-primary reference-detail-open" type="button">${lesson.blueprint ? 'شروع درس ←' : 'مشاهده سرفصل ←'}</button>`;
      detail.querySelector('button').onclick = () => {
        if (lesson.blueprint) onOpenLesson(lesson.blueprint);
        else if (window.FamLessonEngine?.renderUnreadyLesson) window.FamLessonEngine.renderUnreadyLesson(container, { ...lesson, track: path.code }, { catalog, onNavigate: onOpenLesson, onBackToCatalog: onBack });
      };
      container.querySelectorAll('[data-map-node]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mapNode === lesson.id)));
    };
    container.querySelectorAll('[data-map-node]').forEach(button => button.onclick = () => showDetail(lessons.find(l => l.id === button.dataset.mapNode)));
    showDetail(next);
    container.querySelector('#fa-catalog-back').onclick = onBack;
    container.querySelectorAll('[data-open-blueprint]').forEach(btn => btn.onclick = () => onOpenLesson(btn.dataset.openBlueprint));
    container.querySelectorAll('[data-open-unready]').forEach(btn => {
      btn.onclick = () => {
        const lesson = (path.courses.find(c => c.title === btn.dataset.courseTitle)?.lessons || []).find(l => l.id === btn.dataset.openUnready);
        if (lesson && window.FamLessonEngine?.renderUnreadyLesson) {
          window.FamLessonEngine.renderUnreadyLesson(container, { ...lesson, track: path.code, courseTitle: btn.dataset.courseTitle }, { catalog, onNavigate: onOpenLesson, onBackToCatalog: onBack });
        }
      };
    });
  }

  function renderLabWorkbench(container, catalog, onOpenLesson) {
    const sim = window.FamAcademySimulator;
    const all = (catalog?.paths || []).flatMap(p =>
      (p.courses || []).flatMap(c =>
        (c.lessons || []).map(l => ({ ...l, pathId: p.id, pathCode: p.code, courseTitle: c.title }))
      )
    );
    const hasExact = id => Boolean(sim && typeof sim.scenarioForLesson === 'function' && sim.scenarioForLesson(id)?.matchType === 'exact');
    const exactCount = all.filter(l => hasExact(l.id)).length;
    const totalSimCmds = Number(sim?.commandCount || 0) + 10;
    let activeFilter = 'exact';
    let query = '';
    let selected = all.find(l => l.id === 'adv_bgp') || all.find(l => hasExact(l.id)) || all[0];

    container.innerHTML = `
      <div class="lab-workbench">
        <header class="lab-workbench-head">
          <div>
            <span class="journey-kicker">INTERACTIVE CLI WORKBENCH</span>
            <h1>آزمایشگاه مستقل و شبیه‌ساز CLI</h1>
            <p>تمرین مستقیم روی ${totalSimCmds.toLocaleString('fa-IR')} فرمان آموزشی بدون خروجی جعلی — ${exactCount.toLocaleString('fa-IR')} سناریوی اختصاصی درس + ${(all.length - exactCount).toLocaleString('fa-IR')} سناریوی پایه مسیر (شبیه‌ساز آموزشی مرورگر؛ بدون اتصال به تجهیز واقعی).</p>
          </div>
          <button class="btn" id="lab-back-home" type="button">← بازگشت به داشبورد</button>
        </header>
        <div class="lab-workbench-grid">
          <aside class="lab-picker-card">
            <input type="search" id="lab-search-input" class="lab-search-input" placeholder="جست‌وجوی درس یا موضوع (مثلاً BGP، OSPF، Terraform)...">
            <div class="lab-filter-row" role="group" aria-label="فیلتر سناریوها">
              <button type="button" class="lab-filter-btn active" data-lab-filter="exact">سناریوهای اختصاصی (${exactCount})</button>
              <button type="button" class="lab-filter-btn" data-lab-filter="all">همه (${all.length})</button>
              <button type="button" class="lab-filter-btn" data-lab-filter="fam-automation">Automation</button>
            </div>
            <div class="lab-scenario-list" id="lab-scenario-list"></div>
          </aside>
          <section class="lab-terminal-stage">
            <div id="lab-stage-head" style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px"></div>
            <div id="lab-sim-mount"></div>
          </section>
        </div>
      </div>`;

    container.querySelector('#lab-back-home').onclick = () => { location.hash = '#/dashboard'; };
    const listEl = container.querySelector('#lab-scenario-list');
    const stageHead = container.querySelector('#lab-stage-head');
    const mountEl = container.querySelector('#lab-sim-mount');

    const mountSelected = () => {
      if (!selected) return;
      const isExact = hasExact(selected.id);
      stageHead.innerHTML = `
        <div>
          <span class="journey-kicker">${esc(selected.pathCode)} · ${isExact ? 'سناریوی اختصاصی درس' : 'سناریوی پایه مسیر'}</span>
          <h2 style="margin:2px 0 0;font-size:18px">${esc(selected.title)}</h2>
        </div>
        ${selected.blueprint ? '<button type="button" class="journey-link" id="lab-open-lesson">مطالعه متن کامل این درس ←</button>' : ''}`;
      const openBtn = stageHead.querySelector('#lab-open-lesson');
      if (openBtn) openBtn.onclick = () => onOpenLesson(selected.blueprint);
      mountEl.replaceChildren();
      if (sim && typeof sim.mount === 'function') {
        sim.mount(mountEl, { lessonId: selected.id, track: selected.pathCode, title: selected.title });
      } else {
        mountEl.textContent = 'ماژول شبیه‌ساز بارگذاری نشده است.';
      }
    };

    const renderList = () => {
      const q = normSearch(query);
      const filtered = all.filter(l => {
        if (activeFilter === 'exact' && !hasExact(l.id)) return false;
        if (activeFilter === 'fam-automation' && l.pathId !== 'fam-automation') return false;
        if (q && !(normSearch(l.title).includes(q) || normSearch(l.id).includes(q) || normSearch(l.courseTitle || '').includes(q))) return false;
        return true;
      });
      listEl.replaceChildren();
      if (!filtered.length) {
        const empty = document.createElement('div');
        empty.style.cssText = 'padding:12px;color:var(--muted);font-size:13px';
        empty.textContent = 'سناریویی با این فیلتر یافت نشد.';
        listEl.appendChild(empty);
        return;
      }
      for (const l of filtered) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'lab-scenario-item' + (selected && selected.id === l.id ? ' active' : '');
        const title = document.createElement('strong');
        title.textContent = l.title;
        const meta = document.createElement('small');
        meta.textContent = `${l.id} · ${hasExact(l.id) ? 'سناریوی اختصاصی' : 'سناریوی پایه مسیر'}`;
        btn.append(title, meta);
        btn.onclick = () => {
          selected = l;
          renderList();
          mountSelected();
        };
        listEl.appendChild(btn);
      }
    };

    container.querySelector('#lab-search-input').addEventListener('input', e => {
      query = e.target.value || '';
      renderList();
    });
    container.querySelectorAll('[data-lab-filter]').forEach(btn => {
      btn.onclick = () => {
        activeFilter = btn.dataset.labFilter;
        container.querySelectorAll('[data-lab-filter]').forEach(b => b.classList.toggle('active', b === btn));
        renderList();
      };
    });

    renderList();
    mountSelected();
  }

  function renderCoverageView(container, catalog, onOpenLesson) {
    const sim = window.FamAcademySimulator;
    const cmds = sim && typeof sim.getSupportedCommands === 'function' ? sim.getSupportedCommands() : [];
    const statefulCmds = [
      { cmd: 'configure terminal', cat: 'Stateful Config', note: 'ورود به حالت پیکربندی سراسری (config)#' },
      { cmd: 'hostname <NAME>', cat: 'Stateful Config', note: 'تغییر نام دستگاه و انعکاس در running-config' },
      { cmd: 'vlan <1-4094>', cat: 'Stateful Config', note: 'ساخت VLAN جدید و نمایش در show vlan brief' },
      { cmd: 'interface <name>', cat: 'Stateful Config', note: 'انتخاب اینترفیس و ورود به (config-if)#' },
      { cmd: 'ip address <IPv4> <MASK>', cat: 'Stateful Config', note: 'تنظیم IPv4 و انعکاس در show ip interface brief' },
      { cmd: 'no shutdown / shutdown', cat: 'Stateful Config', note: 'فعال/غیرفعال‌سازی وضعیت لینک اینترفیس' },
      { cmd: 'switchport mode access|trunk', cat: 'Stateful Config', note: 'تعیین حالت پورت لایه ۲' },
      { cmd: 'switchport access vlan <1-4094>', cat: 'Stateful Config', note: 'تخصیص VLAN دسترسی و ثبت در جدول VLAN' },
      { cmd: 'switchport voice vlan <1-4094>', cat: 'Stateful Config', note: 'تخصیص VLAN صوتی به پورت' },
      { cmd: 'do <show ...>', cat: 'Stateful Config', note: 'اجرای فرمان‌های show بدون خروج از حالت config' }
    ];
    const classify = c => {
      const s = c.toLowerCase();
      if (/^(terraform|ansible|git|python|pip|yamllint|curl|ssh|openssl|nso_cli|ip -br|ss )/.test(s) || /netconf|restconf|yang/.test(s)) return 'Automation & Linux';
      if (/ospf|eigrp|bgp|route|cef|vrf|bfd|mroute|rpf|protocols/.test(s)) return 'Routing & L3';
      if (/vlan|trunk|mac|spanning|etherchannel|vpc|fex|cdp|lldp|interfaces status/.test(s)) return 'Switching & L2';
      if (/sdwan|dmvpn|crypto|acl|access-lists|auth|aaa|cts|ssh|policy-map|ntp|nat|dhcp/.test(s)) return 'Security, QoS & WAN';
      return 'Core IOS & Platform';
    };
    const allItems = [
      ...statefulCmds,
      ...cmds.map(c => ({ cmd: c, cat: classify(c), note: 'خروجی مرجع آموزشی (Mock)' }))
    ];
    const categories = ['همه', 'Stateful Config', 'Switching & L2', 'Routing & L3', 'Security, QoS & WAN', 'Automation & Linux', 'Core IOS & Platform'];
    let activeCat = 'همه';
    let query = '';

    container.innerHTML = `
      <div class="coverage-view">
        <div class="journey-progress-head">
          <div>
            <span class="journey-kicker">CLI COMMAND COVERAGE</span>
            <h1>پوشش فرمان‌های IOS و NetDevOps</h1>
            <p>فهرست کامل ${(cmds.length + statefulCmds.length).toLocaleString('fa-IR')} فرمان پشتیبانی‌شده در شبیه‌ساز آموزشی (شامل ${statefulCmds.length.toLocaleString('fa-IR')} فرمان پیکربندی Stateful و ${cmds.length.toLocaleString('fa-IR')} فرمان نمایشی و ابزار NetOps).</p>
          </div>
          <button type="button" class="journey-primary small" id="cov-go-lab">تمرین در آزمایشگاه CLI ←</button>
        </div>
        <div class="coverage-toolbar">
          <input type="search" id="cov-search" class="coverage-search" placeholder="جست‌وجوی فرمان (مثلاً ospf، vlan، bgp، ip address، terraform)…">
          <div class="roadmap-path-tabs" id="cov-tabs" role="tablist" aria-label="فیلتر دسته فرمان‌ها">
            ${categories.map(cat => `<button type="button" role="tab" aria-selected="${cat === activeCat ? 'true' : 'false'}" class="roadmap-path-tab ${cat === activeCat ? 'active' : ''}" data-cov-cat="${esc(cat)}">${esc(cat)}</button>`).join('')}
          </div>
        </div>
        <div class="coverage-grid" id="cov-grid"></div>
      </div>`;

    const grid = container.querySelector('#cov-grid');
    const renderGrid = () => {
      const q = normSearch(query);
      const filtered = allItems.filter(it => {
        if (activeCat !== 'همه' && it.cat !== activeCat) return false;
        if (q && !(normSearch(it.cmd).includes(q) || normSearch(it.cat).includes(q) || normSearch(it.note).includes(q))) return false;
        return true;
      });
      if (!filtered.length) {
        grid.innerHTML = '<div class="journey-empty">فرمانی با این فیلتر پیدا نشد.</div>';
        return;
      }
      grid.innerHTML = filtered.map(it => `
        <article class="coverage-cmd-card">
          <code>${esc(it.cmd)}</code>
          <div class="coverage-cmd-meta"><span>${esc(it.cat)}</span><span>${esc(it.note)}</span></div>
        </article>`).join('');
    };

    container.querySelector('#cov-go-lab').onclick = () => { location.hash = '#/lab'; };
    container.querySelector('#cov-search').addEventListener('input', e => { query = e.target.value || ''; renderGrid(); });
    container.querySelectorAll('[data-cov-cat]').forEach(btn => {
      btn.onclick = () => {
        activeCat = btn.dataset.covCat;
        container.querySelectorAll('[data-cov-cat]').forEach(b => {
          b.classList.toggle('active', b === btn);
          b.setAttribute('aria-selected', b === btn ? 'true' : 'false');
        });
        renderGrid();
      };
    });
    renderGrid();
  }

  window.FamAcademyCatalog = { getCompletedSet, calcCourseProgress, calcPathProgress, renderDashboard, renderPathRoadmap, renderLabWorkbench, renderCoverageView };
})();
