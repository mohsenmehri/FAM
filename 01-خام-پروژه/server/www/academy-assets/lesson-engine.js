(() => {
  'use strict';

  const STORAGE_KEY = 'fam_academy_progress_v1';
  const SEC_STORAGE_KEY = 'fam_academy_sections_v1';
  const QUIZ_STORAGE_KEY = 'fam_academy_quiz_v1';

  function getSectionsMap() {
    // A bridge identifies the authenticated account. Never read or write
    // the browser-wide standalone keys during that session.
    const bridge = window.FamAcademyBridge;
    if (bridge) {
      const remote = bridge.progress?.labs?.sections;
      return remote && typeof remote === 'object' && !Array.isArray(remote)
        ? { ...remote } : {};
    }
    try {
      const raw = localStorage.getItem(SEC_STORAGE_KEY);
      const obj = raw ? JSON.parse(raw) : {};
      if (obj && typeof obj === 'object' && !Array.isArray(obj)) return obj;
    } catch {}
    return {};
  }

  function persistProgress(completed, labsOverride) {
    const bridge = window.FamAcademyBridge;
    if (!bridge || typeof bridge.saveProgress !== 'function') return;
    const current = bridge.progress || {};
    bridge.saveProgress({
      completed,
      labs: labsOverride || current.labs || {},
      selfAssessed: current.selfAssessed || [],
      profile: current.profile
    });
  }

  function getQuizAttempts() {
    const bridge = window.FamAcademyBridge;
    if (bridge) {
      const attempts = bridge.progress?.labs?.quizAttempts;
      return attempts && typeof attempts === 'object' && !Array.isArray(attempts) ? { ...attempts } : {};
    }
    try {
      const value = JSON.parse(localStorage.getItem(QUIZ_STORAGE_KEY) || '{}');
      if (value && typeof value === 'object' && !Array.isArray(value)) return value;
    } catch {}
    return {};
  }

  function saveQuizAttempt(lessonId, attempt) {
    const attempts = getQuizAttempts();
    attempts[lessonId] = attempt;
    const bridge = window.FamAcademyBridge;
    if (bridge) {
      persistProgress(getCompletedList(), { ...(bridge.progress?.labs || {}), quizAttempts: attempts });
    } else {
      try { localStorage.setItem(QUIZ_STORAGE_KEY, JSON.stringify(attempts)); } catch {}
    }
  }

  function isSectionDone(lessonId, secId) {
    const map = getSectionsMap();
    return Array.isArray(map[lessonId]) && map[lessonId].includes(secId);
  }

  function toggleSectionDone(lessonId, secId) {
    const map = getSectionsMap();
    const list = Array.isArray(map[lessonId]) ? map[lessonId] : [];
    const idx = list.indexOf(secId);
    if (idx >= 0) list.splice(idx, 1);
    else list.push(secId);
    map[lessonId] = list;
    // The signed-in bridge is account-specific; never put its progress in
    // the browser-wide standalone key, even as a fallback on save failure.
    if (!window.FamAcademyBridge) {
      try { localStorage.setItem(SEC_STORAGE_KEY, JSON.stringify(map)); } catch {}
    }
    const labs = { ...(window.FamAcademyBridge?.progress?.labs || {}), sections: map };
    persistProgress(getCompletedList(), labs);
    return idx < 0;
  }

  function getCompletedList() {
    const bridge = window.FamAcademyBridge;
    if (bridge) {
      const remote = bridge.progress?.completed;
      return [...new Set(Array.isArray(remote) ? remote : [])];
    }
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const arr = raw ? JSON.parse(raw) : [];
      if (Array.isArray(arr)) return [...new Set(arr)];
    } catch {}
    return [];
  }

  function isLessonDone(lessonId) {
    return getCompletedList().includes(lessonId);
  }

  function toggleLessonDone(lessonId) {
    const list = getCompletedList();
    const idx = list.indexOf(lessonId);
    if (idx >= 0) list.splice(idx, 1);
    else list.push(lessonId);
    if (!window.FamAcademyBridge) {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(list)); } catch {}
    }
    persistProgress(list);
    return idx < 0;
  }

  function getAdjacentLessons(catalog, lessonId) {
    if (!catalog?.paths) return { prev: null, next: null };
    const flat = [];
    catalog.paths.forEach(p => (p.courses || []).forEach(c => (c.lessons || []).forEach(l => flat.push({ ...l, track: p.code, courseTitle: c.title }))));
    const idx = flat.findIndex(l => l.id === lessonId);
    if (idx < 0) return { prev: null, next: null };
    return {
      prev: idx > 0 ? flat[idx - 1] : null,
      next: idx < flat.length - 1 ? flat[idx + 1] : null
    };
  }

  function renderUnreadyLesson(container, lessonMeta, opts = {}) {
    if (!container || !lessonMeta) return;
    const adj = getAdjacentLessons(opts.catalog, lessonMeta.id);
    container.innerHTML = `
      <div style="padding:16px;background:#0f172a;border:1px solid #1e293b;border-radius:10px;color:#e2e8f0">
        ${opts.onBackToCatalog ? `<button id="le-back-cat" class="btn" style="margin-bottom:12px;font-size:12px">← بازگشت به نقشه مسیر</button>` : ''}
        <div style="margin-bottom:10px">
          <span class="badge">${lessonMeta.track || 'CCNA'} · ${lessonMeta.courseTitle || ''}</span>
          <h2 style="margin:8px 0 6px;color:#fff;font-size:18px">${lessonMeta.title}</h2>
        </div>
        <div class="card" style="padding:16px;border:1px solid #f59e0b;background:#06090f;margin-bottom:14px">
          <strong style="color:#fbbf24;font-size:14px">این درس هنوز آماده نیست</strong>
          <p style="margin:6px 0 0;font-size:12px;color:#94a3b8">محتوای آموزشی و Blueprint این درس در مراحل بعدی اضافه خواهد شد.</p>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding-top:8px;border-top:1px solid #1e293b">
          <button id="le-prev-btn" class="btn" ${adj.prev ? '' : 'disabled style="opacity:.45"'}>← درس قبلی${adj.prev ? ': ' + adj.prev.title : ''}</button>
          <button id="le-next-btn" class="btn primary" ${adj.next ? '' : 'disabled style="opacity:.45"'}>${adj.next ? 'درس بعدی: ' + adj.next.title : 'درس بعدی'} →</button>
        </div>
      </div>`;
    const backBtn = container.querySelector('#le-back-cat');
    if (backBtn && opts.onBackToCatalog) backBtn.onclick = opts.onBackToCatalog;
    const prevBtn = container.querySelector('#le-prev-btn');
    if (prevBtn && adj.prev) {
      prevBtn.onclick = () => adj.prev.blueprint && opts.onNavigate ? opts.onNavigate(adj.prev.blueprint) : renderUnreadyLesson(container, adj.prev, opts);
    }
    const nextBtn = container.querySelector('#le-next-btn');
    if (nextBtn && adj.next) {
      nextBtn.onclick = () => adj.next.blueprint && opts.onNavigate ? opts.onNavigate(adj.next.blueprint) : renderUnreadyLesson(container, adj.next, opts);
    }
  }

  function renderVisualSvg(bp) {
    if (bp.visualType === 'trunk-8021q') {
      return `<svg dir="ltr" viewBox="0 0 540 140" style="width:100%;max-width:600px;background:#06090f;border:1px solid #1e293b;border-radius:8px">
        <rect x="14" y="22" width="110" height="44" rx="6" fill="#0f172a" stroke="#34d399" stroke-width="1.5"/>
        <text x="69" y="41" text-anchor="middle" fill="#34d399" font-size="11" font-weight="bold">Access (Untagged)</text>
        <text x="69" y="56" text-anchor="middle" fill="#94a3b8" font-size="9">SW1 Gi0/1 (VLAN 10)</text>
        <line x1="124" y1="44" x2="164" y2="44" stroke="#38bdf8" stroke-width="2"/>
        <rect x="164" y="14" width="212" height="60" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.8"/>
        <text x="270" y="32" text-anchor="middle" fill="#38bdf8" font-size="11" font-weight="bold">802.1Q Trunk (Tagged: 4 Bytes)</text>
        <rect x="174" y="40" width="52" height="24" rx="3" fill="#1e293b" stroke="#60a5fa"/><text x="200" y="55" text-anchor="middle" fill="#e2e8f0" font-size="9">TPID 0x8100</text>
        <rect x="230" y="40" width="38" height="24" rx="3" fill="#1e293b" stroke="#60a5fa"/><text x="249" y="55" text-anchor="middle" fill="#e2e8f0" font-size="9">PCP 3b</text>
        <rect x="272" y="40" width="34" height="24" rx="3" fill="#1e293b" stroke="#60a5fa"/><text x="289" y="55" text-anchor="middle" fill="#e2e8f0" font-size="9">DEI 1b</text>
        <rect x="310" y="40" width="56" height="24" rx="3" fill="#1d4ed8" stroke="#93c5fd"/><text x="338" y="55" text-anchor="middle" fill="#fff" font-size="9" font-weight="bold">VID 12b (10)</text>
        <line x1="376" y1="44" x2="416" y2="44" stroke="#38bdf8" stroke-width="2"/>
        <rect x="416" y="22" width="110" height="44" rx="6" fill="#0f172a" stroke="#34d399" stroke-width="1.5"/>
        <text x="471" y="41" text-anchor="middle" fill="#34d399" font-size="11" font-weight="bold">Access (Untagged)</text>
        <text x="471" y="56" text-anchor="middle" fill="#94a3b8" font-size="9">SW2 Gi0/1 (VLAN 10)</text>
        <text x="270" y="106" text-anchor="middle" fill="#cbd5e1" font-size="10">Tagging on SW1 Gi0/0  --->  Trunk Link  --->  Untagging on SW2 Gi0/0</text>
      </svg>`;
    }
    const domains = bp.visualDomains || [];
    const boxes = domains.map((d, i) => {
      const x = 16 + i * 252;
      return `<g>
        <rect x="${x}" y="14" width="232" height="96" rx="10" fill="#0f172a" stroke="${d.color}" stroke-width="1.8" stroke-dasharray="5 3"/>
        <text x="${x + 116}" y="38" text-anchor="middle" fill="${d.color}" font-size="13" font-weight="bold">VLAN ${d.vlan} (${d.name})</text>
        <text x="${x + 116}" y="60" text-anchor="middle" fill="#e2e8f0" font-size="11">${d.hosts.join('  ·  ')}</text>
        <text x="${x + 116}" y="82" text-anchor="middle" fill="#94a3b8" font-size="10">${d.subnet || ''}</text>
        <text x="${x + 116}" y="99" text-anchor="middle" fill="#64748b" font-size="9">Isolated Broadcast Domain</text>
      </g>`;
    }).join('');
    return `<svg dir="ltr" viewBox="0 0 516 124" style="width:100%;max-width:580px;background:#06090f;border:1px solid #1e293b;border-radius:8px">${boxes}</svg>`;
  }

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));

  function renderTopologySvg(bp) {
    const devices = bp.topology?.devices || [];
    const links = bp.topology?.links || [];
    if (!devices.length) return '';
    // Widen the original blueprint coordinates; labels belong in a separate
    // connection list so interfaces never collide with nodes or other labels.
    const minX = Math.min(...devices.map(d => Number(d.x) || 0));
    const minY = Math.min(...devices.map(d => Number(d.y) || 0));
    const points = Object.fromEntries(devices.map(d => [d.id, {
      x: 85 + ((Number(d.x) || 0) - minX) * 2.15,
      y: 65 + ((Number(d.y) || 0) - minY) * 1.65
    }]));
    const width = Math.max(...Object.values(points).map(p => p.x)) + 90;
    const height = Math.max(...Object.values(points).map(p => p.y)) + 80;
    const lines = links.map(link => {
      const a = points[String(link.a || '').split(':')[0]];
      const b = points[String(link.b || '').split(':')[0]];
      if (!a || !b) return '';
      return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="#60a5fa" stroke-width="3"/>`;
    }).join('');
    const nodes = devices.map(d => {
      const p = points[d.id];
      const kind = d.type === 'switch' ? 'Switch' : d.type === 'router' ? 'Router' : d.type === 'server' ? 'Server' : 'Host';
      return `<g><rect x="${p.x-53}" y="${p.y-24}" width="106" height="48" rx="10" fill="#12233a" stroke="#62a5e9" stroke-width="2"/>
        <text x="${p.x}" y="${p.y-3}" text-anchor="middle" fill="#f8fafc" font-size="14" font-weight="700">${escapeHtml(d.id)}</text>
        <text x="${p.x}" y="${p.y+14}" text-anchor="middle" fill="#a9bdd4" font-size="11">${kind}</text></g>`;
    }).join('');
    const legend = links.map(link => `<li><bdi dir="ltr">${escapeHtml(link.a)}</bdi><span aria-hidden="true">↔</span><bdi dir="ltr">${escapeHtml(link.b)}</bdi>${link.vlan != null ? `<span class="topology-vlan">VLAN ${escapeHtml(link.vlan)}</span>` : ''}</li>`).join('');
    return `<div class="topology-scroll"><svg class="topology-diagram" role="img" aria-label="نقشهٔ ارتباط تجهیزات؛ جزئیات اتصالات در فهرست زیر آمده است" dir="ltr" viewBox="0 0 ${width} ${height}">${lines}${nodes}</svg></div><ul class="topology-links" aria-label="اتصالات تجهیزات">${legend}</ul>`;
  }

  function renderDataTable(rows) {
    if (!Array.isArray(rows) || !rows.length) return '';
    const columns = [...new Set(rows.flatMap(row => Object.keys(row)))];
    return `<div class="lesson-table-scroll"><table class="lesson-data-table"><thead><tr>${columns.map(c => `<th scope="col">${escapeHtml(c)}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${columns.map(c => `<td><bdi dir="auto">${escapeHtml(row[c] ?? '—')}</bdi></td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }

  function linkGlossaryTerms(html, glossary) {
    if (!Array.isArray(glossary) || !glossary.length || !html) return html;
    const parts = html.split(/(<svg[\s\S]*?<\/svg>|<pre[\s\S]*?<\/pre>|<code[\s\S]*?<\/code>|<[^>]+>)/gi);
    const terms = glossary.map(g => g.term).filter(Boolean).sort((a, b) => b.length - a.length);
    if (!terms.length) return html;
    const re = new RegExp("\\b(" + terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")\\b", "g");
    return parts.map(p => {
      if (!p || p.startsWith("<")) return p;
      return p.replace(re, m => `<span class="fam-glossary-term" data-term="${escapeHtml(m)}" tabindex="0">${escapeHtml(m)}</span>`);
    }).join("");
  }

  function renderQuizQuestions(questions, instructions) {
    const normalized = questions.map(q => String(q.q || '').replace(/^سؤال\s*[0-9۰-۹٠-٩]+\s*/, '').trim());
    const repetitive = normalized.length > 1 && new Set(normalized).size === 1;
    return `<div class="lesson-quiz" data-lesson-quiz>
      ${instructions ? `<p>${escapeHtml(instructions)}</p>` : ''}
      ${repetitive ? '<p class="lesson-quiz-warning">سؤال‌های فعلی این درس تکراری و نیازمند بازبینی آموزشی هستند؛ این آزمون هنوز سنجش جامع نیست.</p>' : ''}
      ${questions.map((q, i) => `<fieldset class="lesson-quiz-question" data-question="${i}"><legend>${i + 1}. ${q.promptHtml || escapeHtml(q.q)}</legend>
        ${(Array.isArray(q.options) ? q.options : []).map((option, n) => `<label class="lesson-quiz-option"><input type="radio" name="lesson-question-${i}" value="${n}"> <span>${escapeHtml(option)}</span></label>`).join('')}
        <div class="lesson-quiz-feedback" data-feedback="${i}" hidden></div></fieldset>`).join('')}
      <div class="lesson-quiz-actions"><button class="btn primary" type="button" data-quiz-grade>ثبت و بررسی آزمون</button><button class="btn" type="button" data-quiz-retry>تلاش مجدد</button></div>
      <p class="lesson-quiz-result" role="status" aria-live="polite"></p></div>`;
  }

  function getQuizQuestions(bp) {
    if (Array.isArray(bp.interactiveQuiz) && bp.interactiveQuiz.length) {
      return bp.interactiveQuiz.map(q => ({ q: q.title, promptHtml: q.promptHtml,
        options: q.options, answer: q.correctIndex, explanationHtml: q.explanationHtml }));
    }
    return Array.isArray(bp.stages?.quiz?.questions) ? bp.stages.quiz.questions : [];
  }

  function buildObjectStages(bp) {
    const s = bp.stages;
    const standardOrder = ["concept", "example", "practice", "lab", "quiz", "summary"];
    const order = [...standardOrder, ...Object.keys(s).filter(key => !standardOrder.includes(key))];
    const esc = v => String(v || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    return order.filter(k => s[k]).map((k, idx) => {
      const st = s[k];
      let html = typeof st.html === "string" ? st.html : "";
      if (k === "concept" && !st.html) {
        html += `<p>${esc(st.whyLayered || st.summary)}</p>`;
        if (st.analogy) html += `<p><strong>تشبیه:</strong> ${esc(st.analogy)}</p>`;
        if (Array.isArray(st.deepDive)) html += st.deepDive.map(x => "<p>" + esc(x) + "</p>").join("");
        if (Array.isArray(st.keyIdeas)) html += "<h4>ایده‌های کلیدی</h4><ul>" + st.keyIdeas.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>";
        if (Array.isArray(st.osiLayers)) {
          html += `<div>` + st.osiLayers.map(l => `<div style="margin:8px 0;padding:10px;border:1px solid #1e293b;border-radius:8px;"><strong>لایه ${l.layer}: ${esc(l.name)}</strong><br/>عملکرد: ${esc(l.function || l.desc)}<br/>مثال واقعی: ${esc(l.realExample || "-")}<br/>پروتکل‌ها: <span dir="ltr">${esc(l.protocols || "-")}</span><br/>ارتباط: ${esc(l.layerRelation || "-")}</div>`).join("") + `</div>`;
        }
        if (st.encapsulation) html += `<p>${esc(st.encapsulation)}</p>`;
        if (Array.isArray(st.misconceptions)) html += "<h4>برداشت‌های اشتباه رایج</h4><ul>" + st.misconceptions.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>";
        if (Array.isArray(st.fieldNotes)) html += "<h4>نکته‌های عملی</h4><ul>" + st.fieldNotes.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>";
      } else if (k === "example") {
        if (st.scenario) html += `<p>${esc(st.scenario)}</p>`;
        if (bp.topology?.devices?.length) html += "<h4>نقشهٔ سناریو</h4><div class='lesson-topology'>" + renderTopologySvg(bp) + "</div>";
        if (Array.isArray(st.addressingTable) && st.addressingTable.length) {
          html += renderDataTable(st.addressingTable);
        }
        if (Array.isArray(st.packetFlow)) html += `<ol>` + st.packetFlow.map(p => `<li>${esc(p)}</li>`).join("") + `</ol>`;
        if (Array.isArray(st.workedExample)) html += "<h4>تحلیل نمونهٔ حل‌شده</h4>" + st.workedExample.map((x,i) => "<div class='lesson-case'><strong>" + (i+1) + ". " + esc(x.title || x.step || "گام") + "</strong><p>" + esc(x.explanation || x.reason || x.action || "") + "</p>" + (x.result ? "<small>" + esc(x.result) + "</small>" : "") + "</div>").join("");
        if (st.expectedBehavior) html += "<p>" + esc(st.expectedBehavior) + "</p>";
      } else if (k === "practice") {
        if (Array.isArray(st.troubleshootingTable)) {
          html += `<ul>` + st.troubleshootingTable.map(r => `<li><strong>${esc(r.layer)}:</strong> ${esc(r.checks)}</li>`).join("") + `</ul>`;
        }
        if (Array.isArray(st.drills)) html += `<ul>` + st.drills.map(d => `<li>${esc(d)}</li>`).join("") + `</ul>`;
        if (Array.isArray(st.troubleshootingCases)) html += "<h4>سناریوهای عیب‌یابی</h4>" + st.troubleshootingCases.map((t,i) => "<div class='lesson-case'><strong>" + (i+1) + ". نشانه: " + esc(t.symptom) + "</strong><p><b>علت محتمل:</b> " + esc(t.cause) + "</p><p><b>روش تشخیص:</b> " + esc(t.diagnosis) + "</p><p><b>راه‌حل:</b> " + esc(t.fix) + "</p>" + (t.verify ? "<p><b>راستی‌آزمایی:</b> " + esc(t.verify) + "</p>" : "") + "</div>").join("");
      } else if (k === "lab") {
        // Authored stage HTML takes precedence over the generic fallback lab.
        const topo = st.html ? null : st.pnetlabTopology;
        const configs = Object.values(topo?.configs || {});
        const legacySections = bp.sections && Object.keys(bp.sections).length && !bp.stages?.concept;
        const placeholderTopology = configs.length > 0 && configs.every(config => String(config).trim() === 'show running-config');
        const missingWorksheet = !topo && !st.commands?.length;
        if (!st.html && (legacySections || placeholderTopology || missingWorksheet)) {
          html += '<p class="lesson-quiz-warning">این بخش یک الگوی عمومی است و هنوز آزمایشگاه اختصاصی کامل این مبحث نیست. برای پیکربندی، بخش دستورات و سناریوی درس را بررسی کنید.</p>';
        }
        if (topo) {
          html += `<h4>${esc(topo.title)}</h4>`;
          if (Array.isArray(topo.portVlanTable)) {
            html += renderDataTable(topo.portVlanTable);
          }
          if (topo.configs) {
            html += Object.entries(topo.configs).map(([dev, cfg]) => `<div style="margin:10px 0;"><strong>${esc(dev)} Config:</strong><pre class="cli-block" dir="ltr" style="background:#020617;padding:10px;border-radius:8px;overflow:auto;"><code>${esc(cfg)}</code></pre></div>`).join("");
          }
          if (Array.isArray(topo.steps)) {
            html += `<ol>` + topo.steps.map(sp => `<li><strong>${esc(sp.action)}</strong><br/>خروجی مورد انتظار: <span dir="ltr">${esc(sp.expected)}</span></li>`).join("") + `</ol>`;
          }
        }
        if (Array.isArray(st.commands)) {
          html += st.commands.map(c => `<div style="margin:8px 0;"><pre class="cli-block" dir="ltr" style="background:#020617;padding:8px;border-radius:6px;"><code>${esc(c.cmd)}</code></pre><p>${esc(c.desc)}</p></div>`).join("");
        }
        if (st.verificationCommand) html += `<p><strong>Verification:</strong> <code dir="ltr">${esc(st.verificationCommand)}</code></p>`;
        if (st.expectedOutput) html += `<pre class="cli-block" dir="ltr" style="background:#020617;padding:10px;border-radius:8px;"><code>${esc(st.expectedOutput)}</code></pre>`;
        if (st.interpretation) html += `<p>${esc(st.interpretation)}</p>`;
        if (Array.isArray(st.verificationCommands)) html += "<h4>چک‌لیست Verification</h4>" + st.verificationCommands.map(c => "<div class='lesson-case'><code dir='ltr'>" + esc(c.cmd) + "</code><p>" + esc(c.purpose || c.desc || "") + "</p>" + (c.expected ? "<small>" + esc(c.expected) + "</small>" : "") + "</div>").join("");
        if (Array.isArray(st.commonMistakes)) html += "<h4>خطاهای رایج</h4><ul>" + st.commonMistakes.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>";
      } else if (k === "quiz") {
        const questions = getQuizQuestions(bp);
        if (questions.length) {
          html = html.replace(/<div\s+id=['"]encor-interactive-quiz['"]\s*><\/div>/g, '');
          html += renderQuizQuestions(questions, st.instructions);
        } else if (!st.html && st.questionCount) {
          html += `<p>این آزمون شامل <strong>${esc(st.questionCount)}</strong> سؤال تسلط است.</p>`;
        }
      } else if (k === "summary") {
        if (Array.isArray(st.takeaways)) html += `<ul>` + st.takeaways.map(t => `<li>${esc(t)}</li>`).join("") + `</ul>`;
        if (st.oneSentence) html += "<p><strong>اگر فقط یک نکته را به خاطر بسپاری:</strong> " + esc(st.oneSentence) + "</p>";
        if (Array.isArray(st.checklist)) html += "<h4>چک‌لیست تسلط</h4><ul>" + st.checklist.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>";
        if (Array.isArray(st.nextLessons)) html += "<h4>مباحث مرتبط برای ادامه</h4><ul>" + st.nextLessons.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>";
      }
      if (!html) html = `<p>${esc(st.summary || st.title || k)}</p>`;
      const defaultTitles = { concept: 'مفهوم پایه', example: 'مثال', practice: 'تمرین', lab: 'آزمایشگاه', quiz: 'آزمون', summary: 'جمع‌بندی' };
      const title = (st.title || defaultTitles[k] || k).replace(/^\s*[0-9۰-۹٠-٩]+[.،:۔-]\s*/, '');
      return { id: k, step: String(idx + 1), title, html: linkGlossaryTerms(html, bp.glossary), num: idx + 1 };
    });
  }

  function buildSections(bp) {
    const rawSections = Array.isArray(bp.sections) ? bp.sections :
      (bp.sections && typeof bp.sections === 'object' ? Object.keys(bp.sections)
        .sort((a, b) => Number(a) - Number(b)).map(k => bp.sections[k]) : []);
    const sections = rawSections.map((s, i) => ({
      id: s.id || `section-${i + 1}`, title: s.title || `بخش ${i + 1}`,
      html: linkGlossaryTerms(s.html || '', bp.glossary)
        .replace(/<div\s+id=['"]encor-interactive-quiz['"]\s*><\/div>/g,
          '<p>سؤال‌های تعاملی در بخش آزمون درس قرار دارند.</p>')
    }));
    let stages = [];
    if (Array.isArray(bp.stages)) {
      stages = bp.stages.map((s, i) => ({ id: s.id || `stage-${i + 1}`, title: s.title,
        html: linkGlossaryTerms(s.html, bp.glossary) }));
    } else if (bp.stages && typeof bp.stages === 'object') stages = buildObjectStages(bp);
    // A stage and a section may share an ID. Keep both without duplicate DOM IDs.
    const used = new Set();
    if (sections.length || stages.length) {
      return [...sections, ...stages].map((s, i) => {
        let id = s.id || `part-${i + 1}`;
        while (used.has(id)) id = `stage-${id}`;
        used.add(id);
        return { ...s, id, step: String(i + 1), num: i + 1 };
      });
    }
    const hosts = (bp.topology?.devices || []).filter(d => d.ip);
    const list = [];
    if (bp.beforeYouStart?.length) {
      list.push({ id: 'before', title: 'پیش‌نیازها (Before You Start)', html: `<ul style="margin:6px 0 0 18px;font-size:13px">${bp.beforeYouStart.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul>` });
    }
    if (bp.whyItMatters) {
      list.push({ id: 'why', title: 'چرا این مبحث مهم است؟ (Why It Matters)', html: `<p style="margin:6px 0 0;font-size:13px;line-height:1.7">${escapeHtml(bp.whyItMatters)}</p>` });
    }
    if (bp.objectives?.length) {
      list.push({ id: 'obj', title: 'اهداف یادگیری (Learning Objectives)', html: `<ul style="margin:6px 0 0 18px;font-size:13px">${bp.objectives.map(o => `<li>${escapeHtml(o)}</li>`).join('')}</ul>` });
    }
    if (bp.concept) {
      list.push({ id: 'concept', title: 'مفهوم پایه (Concept)', html: `<p style="margin:6px 0 0;font-size:13px;line-height:1.7">${escapeHtml(bp.concept)}</p>` });
    }
    if (bp.visualDomains?.length) {
      list.push({ id: 'visual', title: 'توضیح تصویری (Visual Explanation)', html: `<div style="margin-top:8px">${renderVisualSvg(bp)}</div>` });
    }
    if (bp.topology?.devices?.length) {
      list.push({ id: 'topo', title: 'توپولوژی شبکه (Network Topology)', html: `<div style="margin-top:8px">${renderTopologySvg(bp)}</div>` });
    }
    if (hosts.length) {
      list.push({ id: 'addr', title: 'جدول آدرس‌دهی (Addressing Plan — Layer 2 Only)', html: `<table style="width:100%;border-collapse:collapse;margin-top:8px;font-size:12px;direction:ltr;text-align:left"><thead><tr style="border-bottom:1px solid #334155;color:#94a3b8"><th>Device</th><th>Port</th><th>VLAN</th><th>IP / Mask</th><th>Gateway</th></tr></thead><tbody>${hosts.map(h => `<tr style="border-bottom:1px solid #1e293b"><td>${escapeHtml(h.id)}</td><td>${escapeHtml(h.port)}</td><td>${escapeHtml(h.vlan)}</td><td>${escapeHtml(h.ip)}</td><td>${escapeHtml(h.gw)}</td></tr>`).join('')}</tbody></table>` });
    }
    if (bp.configuration?.length) {
      list.push({ id: 'cfg', title: 'پیکربندی کامل و توضیح خط‌به‌خط دستورات', html: `<div style="margin-top:8px;display:flex;flex-direction:column;gap:4px">${bp.configuration.map(c => `<div dir="ltr" style="display:flex;justify-content:space-between;align-items:center;gap:12px;background:#06090f;padding:6px 10px;border-radius:6px;font-size:12px"><code style="color:#34d399;text-align:left">${escapeHtml(c.cmd)}</code><span dir="rtl" style="color:#94a3b8;text-align:right">${escapeHtml(c.explain)}</span></div>`).join('')}</div>` });
    }
    if (bp.verification) {
      list.push({ id: 'verify', title: 'بررسی و خروجی مورد انتظار (Verification)', html: `<pre style="direction:ltr;text-align:left;background:#06090f;padding:10px;border-radius:6px;font-size:11px;color:#bae6fd;margin-top:6px;overflow-x:auto">${escapeHtml(bp.verification.command)}\n\n${escapeHtml(bp.verification.expectedOutput)}</pre>` });
    }
    if (bp.troubleshooting?.length) {
      list.push({ id: 'tshoot', title: 'عیب‌یابی (Troubleshooting)', html: bp.troubleshooting.map(t => `<div style="font-size:12px;margin-top:8px;padding:8px;background:#06090f;border-radius:6px"><strong>نشانه:</strong> ${escapeHtml(t.symptom)}<br/><strong>علت:</strong> ${escapeHtml(t.cause)}<br/><strong>راه‌حل:</strong> ${escapeHtml(t.fix)}</div>`).join('') });
    }
    if (bp.practiceExercise?.steps?.length) {
      list.push({ id: 'practice', title: bp.practiceExercise.title || 'تمرین عملی (Practice Exercise)', html: `<ol style="margin:6px 0 0 18px;font-size:13px">${bp.practiceExercise.steps.map(s => `<li>${escapeHtml(s)}</li>`).join('')}</ol>` });
    }
    if (bp.knowledgeCheck?.length) {
      list.push({ id: 'quiz', title: 'آزمون ارزیابی (Knowledge Check)', html: `<div id="le-quiz" style="margin-top:8px;display:flex;flex-direction:column;gap:12px">${bp.knowledgeCheck.map((q, qi) => `<div style="padding:8px;background:#06090f;border-radius:6px"><div style="font-size:12px;font-weight:700;margin-bottom:6px">${qi + 1}. ${escapeHtml(q.q)}</div>${q.options.map((opt, oi) => `<label style="display:block;font-size:12px;cursor:pointer;margin:3px 0"><input type="radio" name="le-q-${qi}" value="${oi}"/> ${escapeHtml(opt)}</label>`).join('')}<div id="le-q-fb-${qi}" style="font-size:11px;margin-top:4px"></div></div>`).join('')}<button id="le-grade-btn" class="btn primary" style="align-self:flex-start">بررسی پاسخ‌ها</button><div id="le-quiz-res" style="font-size:13px;font-weight:700"></div></div>` });
    }
    if (bp.finalChallenge) {
      list.push({ id: 'challenge', title: 'چالش نهایی (Final Challenge)', html: `<p style="font-size:12px;margin:6px 0 0">${escapeHtml(bp.finalChallenge)}</p>` });
    }
    return list.map((s, idx) => ({ ...s, num: idx + 1 }));
  }

  function hasStages(bp) {
    return Array.isArray(bp?.stages)
      ? bp.stages.length > 0
      : !!bp?.stages && typeof bp.stages === "object" && Object.keys(bp.stages).length > 0;
  }

  function renderLesson(container, bp, opts = {}) {
    if (bp && !bp.lessonId && bp.id) bp.lessonId = bp.id;
    window.__famLastBp = bp;
    if (!container || !bp) return;
    const sections = buildSections(bp);
    const done = isLessonDone(bp.lessonId);
    const adj = getAdjacentLessons(opts.catalog, bp.lessonId);
    const stageLabels = { concept: 'مفهوم', example: 'مثال', practice: 'تمرین', lab: 'آزمایشگاه', quiz: 'آزمون', summary: 'جمع‌بندی' };
    const stageIcons = { concept:'M12 2a7 7 0 0 0-4 12.7V18h8v-3.3A7 7 0 0 0 12 2ZM9 21h6', example:'M5 3h14v18H5z M8 7h8M8 11h8M8 15h5', practice:'M4 20l4-1 11-11-3-3L5 16z M14 7l3 3', lab:'M9 3v7l-5 8a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-5-8V3 M8 3h8 M7 16h10', quiz:'M9 9a3 3 0 1 1 5 2c-1 .8-2 1-2 3 M12 18h.01 M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20', summary:'M5 4h14v17H5z M8 8h8 M8 12h8 M8 16h5' };
    const stageIcon = (id, index) => stageIcons[id] ? `<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${stageIcons[id]}"/></svg>` : String(index + 1);
    // Absence or an unfamiliar status is never presented as an approval.
    const review = typeof bp.reviewStatus === 'string' ? bp.reviewStatus.trim() : '';
    const pending = /\b(draft|pending)\b/i.test(review);
    const reviewLabel = !review ? 'وضعیت بازبینی مشخص نیست' : pending
      ? 'پیش‌نویس؛ در انتظار بازبینی فنی و محتوایی' : `وضعیت ثبت‌شده: ${review}`;
    const evidence = typeof bp.evidence === 'string' ? bp.evidence.trim() : '';
    const evidenceLabel = /^Designed\s*[—–-]\s*Not Run$/i.test(evidence)
      ? 'آزمایشگاه طراحی شده است؛ اجرای واقعی آن تأیید نشده است.'
      : evidence ? `وضعیت اجرای ثبت‌شده: ${evidence}` : 'وضعیت اجرای آزمایشگاه مشخص نیست.';

    container.innerHTML = `
      <div class="lesson-layout lesson-reference-unit">
        <header class="unit-head lesson-unit-head">
          <div class="lesson-unit-heading">
            <div>
              <div class="kicker">${escapeHtml(bp.track || '')} · درس</div>
              <span class="badge">${escapeHtml(bp.track || '')} · ${escapeHtml(bp.lessonId || '')}</span>
              <h1>${escapeHtml(bp.title || '')}</h1>
              <p class="lesson-unit-meta">${sections.length} بخش آموزشی · برای رفتن به هر بخش روی نام آن بزنید</p>
            </div>
            <div class="lesson-unit-actions">
              ${opts.onBackToCatalog ? '<button id="le-back-cat" class="btn" type="button">بازگشت به مسیرها</button>' : ''}
              <button id="fam-glossary-toggle" type="button" class="btn glossary-toggle" aria-pressed="true">واژه‌نامه: روشن</button>
              <button id="le-complete-btn" class="btn ${done ? '' : 'primary'}" type="button">${done ? '✅ تکمیل شده (لغو تکمیل)' : 'علامت‌گذاری به‌عنوان تکمیل‌شده'}</button>
            </div>
          </div>
        </header>
        <aside class="lesson-review-status" role="status" aria-label="وضعیت بازبینی و آزمایش درس" style="margin:12px 0;padding:12px 16px;border:1px solid #b45309;border-radius:10px;background:#fff7ed;color:#7c2d12;line-height:1.7">
          <strong>${escapeHtml(reviewLabel)}</strong><br><span>${escapeHtml(evidenceLabel)}</span>
        </aside>
        ${hasStages(bp) ? `
          <nav id="le-stage-bar" class="stepper lesson-stepper" aria-label="بخش‌های درس">
            ${sections.map((s, idx) => `<button type="button" id="side-sec-${escapeHtml(s.id)}" class="stepper-item le-stage-pill" data-stage-idx="${idx}" data-stage-id="${escapeHtml(s.id)}" aria-label="بخش ${idx + 1}: ${escapeHtml(s.title)}"><span class="stepper-dot">${stageIcon(s.id, idx)}</span><span class="stepper-label">${escapeHtml(stageLabels[s.id] || s.title)}</span></button>`).join('')}
          </nav>` : ''}
        <div class="lesson-body-grid">
          <div class="lesson-content">
            ${sections.map((s, idx) => {
              const hiddenStyle = (hasStages(bp) && idx !== 0) ? ' style="display:none"' : '';
              return `<article id="sec-${s.id}" class="card le-stage-card" data-stage-idx="${idx}"${hiddenStyle}><header class="lesson-stage-heading"><span class="lesson-stage-number">${idx + 1}</span><div><span class="lesson-stage-caption">بخش ${idx + 1} از ${sections.length}</span><h2>${escapeHtml(s.title)}</h2></div></header><div class="lesson-stage-content">${s.html}</div></article>`;
            }).join('')}
            ${hasStages(bp) ? `
            <div class="step-foot lesson-step-foot">
              <button id="le-stage-prev" class="btn" type="button">بخش قبلی</button>
              <button id="le-stage-next" class="btn primary" type="button">بخش بعدی</button>
            </div>` : ''}
            <div class="lesson-adjacent">
              <button id="le-prev-btn" class="btn" ${adj.prev ? '' : 'disabled'}>درس قبلی${adj.prev ? ': ' + escapeHtml(adj.prev.title) : ''}</button>
              <button id="le-next-btn" class="btn" ${adj.next ? '' : 'disabled'}>${adj.next ? 'درس بعدی: ' + escapeHtml(adj.next.title) : 'درس بعدی'}</button>
            </div>
          </div>
          <aside class="lesson-side-rail" aria-label="فهرست و یادداشت‌های درس">
            <section class="lesson-rail-card">
              <h3><span>فهرست بخش‌های درس</span><span class="side-pill">${sections.length}</span></h3>
              <nav class="lesson-toc-list" id="le-toc-list">
                ${sections.map((s, idx) => `<button type="button" class="lesson-toc-link${idx === 0 ? ' active' : ''}" data-toc-idx="${idx}" data-toc-target="sec-${escapeHtml(s.id)}"><span class="lesson-toc-num">${idx + 1}</span><span>${escapeHtml(s.title)}</span></button>`).join('')}
              </nav>
            </section>
            <section class="lesson-rail-card">
              <h3><span>یادداشت شخصی این درس</span></h3>
              <textarea id="le-lesson-notes" class="lesson-notes-area" placeholder="نکات کلیدی، فرمان‌های مهم یا سؤال‌های خود را اینجا بنویسید..."></textarea>
              <div id="le-notes-status" class="lesson-notes-meta">ذخیره خودکار محلی در همین مرورگر</div>
            </section>
          </aside>
        </div>
      </div>`;

    const backBtn = container.querySelector('#le-back-cat');
    if (backBtn && opts.onBackToCatalog) backBtn.onclick = opts.onBackToCatalog;
    setupGlossaryToggle(container);

    // Sticky TOC + Per-Lesson Personal Notes (local browser storage, safe try/catch)
    const NOTES_STORAGE_KEY = 'fam.academy.notes.v1';
    const notesArea = container.querySelector('#le-lesson-notes');
    const notesStatus = container.querySelector('#le-notes-status');
    if (notesArea && bp.lessonId) {
      try {
        const allNotes = JSON.parse(localStorage.getItem(NOTES_STORAGE_KEY) || '{}');
        if (allNotes && typeof allNotes[bp.lessonId] === 'string') notesArea.value = allNotes[bp.lessonId];
      } catch (_) {}
      let saveTimer = null;
      notesArea.addEventListener('input', () => {
        if (saveTimer) clearTimeout(saveTimer);
        saveTimer = setTimeout(() => {
          try {
            const allNotes = JSON.parse(localStorage.getItem(NOTES_STORAGE_KEY) || '{}') || {};
            allNotes[bp.lessonId] = notesArea.value;
            localStorage.setItem(NOTES_STORAGE_KEY, JSON.stringify(allNotes));
            if (notesStatus) notesStatus.textContent = 'یادداشت به‌صورت محلی ذخیره شد.';
          } catch (_) {
            if (notesStatus) notesStatus.textContent = 'ذخیره محلی یادداشت در دسترس نیست.';
          }
        }, 250);
      });
    }

    const syncTocActive = (idx) => {
      container.querySelectorAll('.lesson-toc-link').forEach((btn, i) => {
        btn.classList.toggle('active', i === idx);
      });
    };

    let activeStageIdx = 0;
    const isStaged = hasStages(bp) > 0;
    const updateStageProgress = () => {
      if (!isStaged) return;
      container.querySelectorAll('.le-stage-pill').forEach((pill, i) => {
        const current = i === activeStageIdx;
        pill.classList.toggle('current', current);
        if (current) pill.setAttribute('aria-current', 'step');
        else pill.removeAttribute('aria-current');
      });
      syncTocActive(activeStageIdx);
    };
    const setActiveStage = (nextIdx) => {
      if (!isStaged) return;
      activeStageIdx = Math.max(0, Math.min(sections.length - 1, nextIdx));
      container.querySelectorAll('.le-stage-card').forEach((card, i) => {
        card.style.display = i === activeStageIdx ? 'block' : 'none';
      });
      const prevS = container.querySelector('#le-stage-prev');
      const nextS = container.querySelector('#le-stage-next');
      if (prevS) prevS.disabled = activeStageIdx === 0;
      if (nextS) nextS.disabled = activeStageIdx === sections.length - 1;
      updateStageProgress();
    };
    container.querySelectorAll('.lesson-toc-link').forEach((btn, i) => {
      btn.onclick = () => {
        if (isStaged) {
          setActiveStage(i);
          container.querySelector('#le-stage-bar')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          syncTocActive(i);
          const target = container.querySelector('#' + btn.dataset.tocTarget);
          target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      };
    });
    if (isStaged) {
      container.querySelectorAll('.le-stage-pill').forEach((pill, i) => {
        pill.onclick = () => {
          setActiveStage(i);
          container.querySelector('#le-stage-bar')?.scrollIntoView({ block: 'start' });
        };
      });
      const prevS = container.querySelector('#le-stage-prev');
      const nextS = container.querySelector('#le-stage-next');
      const goToStage = index => {
        setActiveStage(index);
        container.querySelector('#le-stage-bar')?.scrollIntoView({ block: 'start' });
      };
      if (prevS) prevS.onclick = () => goToStage(activeStageIdx - 1);
      if (nextS) nextS.onclick = () => goToStage(activeStageIdx + 1);
      setActiveStage(0);
    }

    const compBtn = container.querySelector('#le-complete-btn');
    if (compBtn) {
      compBtn.onclick = () => {
        const nowDone = toggleLessonDone(bp.lessonId);
        compBtn.textContent = nowDone ? '✅ تکمیل شده (لغو تکمیل)' : 'علامت‌گذاری به‌عنوان تکمیل‌شده';
        compBtn.className = `btn ${nowDone ? '' : 'primary'}`;
        window.dispatchEvent(new CustomEvent('fam-academy-progress-updated'));
      };
    }

    const prevBtn = container.querySelector('#le-prev-btn');
    if (prevBtn && adj.prev) prevBtn.onclick = () => (adj.prev.blueprint && opts.onNavigate) ? opts.onNavigate(adj.prev.blueprint) : renderUnreadyLesson(container, adj.prev, opts);
    const nextBtn = container.querySelector('#le-next-btn');
    if (nextBtn && adj.next) nextBtn.onclick = () => (adj.next.blueprint && opts.onNavigate) ? opts.onNavigate(adj.next.blueprint) : renderUnreadyLesson(container, adj.next, opts);

    const lessonSections = [...container.querySelectorAll('div[id^="sec-"]')];
    const outline = container.querySelector('#lesson-outline');
    if (outline) {
      outline.innerHTML = lessonSections.map((section, index) => {
        const heading = section.querySelector('strong');
        const label = (heading?.textContent || section.id).replace(/^\s*\d+(?:\s*(?:&|-)\s*\d+)?\s*[.\u06D4]?\s*/, '').trim();
        if (heading) heading.textContent = `${index + 1}. ${label}`;
        return `<a href="#${escapeHtml(section.id)}" style="font-size:12px;color:#cbd5e1;text-decoration:none;padding:5px 8px;border-radius:6px;background:#06090f;border:1px solid #1e293b">${index + 1}. ${escapeHtml(label)}</a>`;
      }).join('');
    }

    const quiz = container.querySelector('[data-lesson-quiz]');
    const quizQuestions = getQuizQuestions(bp);
    if (quiz && Array.isArray(quizQuestions)) {
      const result = quiz.querySelector('.lesson-quiz-result');
      const previous = getQuizAttempts()[bp.lessonId];
      if (previous && Number.isInteger(previous.correct) && Number.isInteger(previous.total) && previous.total > 0) {
        result.textContent = `آخرین نتیجه ثبت‌شده: ${previous.correct} از ${previous.total} پاسخ درست`;
      }
      quiz.querySelector('[data-quiz-grade]').onclick = () => {
        let correct = 0, incorrect = 0, unanswered = 0;
        quizQuestions.forEach((q, i) => {
          const selected = quiz.querySelector(`input[name="lesson-question-${i}"]:checked`);
          const feedback = quiz.querySelector(`[data-feedback="${i}"]`);
          if (!selected) unanswered++;
          const isCorrect = selected && Number(selected.value) === q.answer;
          if (isCorrect) correct++; else if (selected) incorrect++;
          feedback.textContent = `${!selected ? 'بدون پاسخ' : isCorrect ? 'درست' : 'نادرست'} — پاسخ صحیح: ${q.options?.[q.answer] || 'نامشخص'}. ${q.explanation || ''}`;
          if (q.explanationHtml) feedback.insertAdjacentHTML('beforeend', q.explanationHtml);
          feedback.className = `lesson-quiz-feedback ${isCorrect ? 'is-correct' : 'is-incorrect'}`;
          feedback.hidden = false;
        });
        result.textContent = `نمره: ${Number((correct * 10 / quizQuestions.length).toFixed(2))} از ۱۰ | پاسخ درست: ${correct} از ${quizQuestions.length} | غلط: ${incorrect} | بدون پاسخ: ${unanswered}`;
        saveQuizAttempt(bp.lessonId, { correct, incorrect, unanswered, total: quizQuestions.length });
      };
      quiz.querySelector('[data-quiz-retry]').onclick = () => {
        quiz.querySelectorAll('input:checked').forEach(input => { input.checked = false; });
        quiz.querySelectorAll('[data-feedback]').forEach(feedback => { feedback.hidden = true; feedback.textContent = ''; });
        result.textContent = '';
      };
    }

    const gradeBtn = container.querySelector('#le-grade-btn');
    if (gradeBtn) {
      gradeBtn.onclick = () => {
        let score = 0;
        bp.knowledgeCheck.forEach((q, qi) => {
          const sel = container.querySelector(`input[name="le-q-${qi}"]:checked`);
          const fb = container.querySelector(`#le-q-fb-${qi}`);
          const ok = sel && Number(sel.value) === q.answerIndex;
          if (ok) score++;
          if (fb) {
            fb.style.color = ok ? '#34d399' : '#f87171';
            fb.textContent = (ok ? '✅ صحیح: ' : '❌ نادرست: ') + (q.explain || '');
          }
        });
        const resEl = container.querySelector('#le-quiz-res');
        if (resEl) resEl.textContent = `امتیاز نهایی: ${score} از ${bp.knowledgeCheck.length}`;
      };
    }

    if (window.FamAcademySimulator && typeof window.FamAcademySimulator.mount === 'function') {
      window.FamAcademySimulator.mount(container, bp);
    }
  }


  const GLOSSARY_SETTING = 'fam_academy_glossary_enabled';
  let glossaryEnabled = true;
  try { glossaryEnabled = localStorage.getItem(GLOSSARY_SETTING) !== 'off'; } catch (_) {}
  let tooltip = null;
  let hideTimer = null;
  let currentTerm = null;

  function hideGlossary() {
    clearTimeout(hideTimer);
    if (tooltip) tooltip.hidden = true;
    if (currentTerm) currentTerm.removeAttribute('aria-describedby');
    currentTerm = null;
  }
  function scheduleGlossaryHide() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hideGlossary, 180);
  }
  function setupGlossaryToggle(container) {
    const button = container.querySelector('#fam-glossary-toggle');
    if (!button) return;
    const update = () => {
      button.setAttribute('aria-pressed', String(glossaryEnabled));
      button.textContent = `واژه‌نامه: ${glossaryEnabled ? 'روشن' : 'خاموش'}`;
      container.querySelectorAll('.fam-glossary-term').forEach(term => {
        term.tabIndex = glossaryEnabled ? 0 : -1;
      });
      container.classList.toggle('glossary-disabled', !glossaryEnabled);
    };
    update();
    button.onclick = () => {
      glossaryEnabled = !glossaryEnabled;
      try { localStorage.setItem(GLOSSARY_SETTING, glossaryEnabled ? 'on' : 'off'); } catch (_) {}
      hideGlossary();
      update();
    };
  }
  function showGlossary(term) {
    if (!glossaryEnabled || !term) return;
    const item = (window.__famLastBp?.glossary || []).find(g => g.term === term.dataset.term);
    if (!item) return;
    clearTimeout(hideTimer);
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'fam-glossary-tooltip';
      tooltip.className = 'fam-glossary-tooltip';
      tooltip.setAttribute('dir', 'rtl');
      tooltip.setAttribute('role', 'tooltip');
      tooltip.addEventListener('pointerenter', () => clearTimeout(hideTimer));
      tooltip.addEventListener('pointerleave', scheduleGlossaryHide);
      tooltip.addEventListener('focusin', () => clearTimeout(hideTimer));
      tooltip.addEventListener('focusout', scheduleGlossaryHide);
      document.body.append(tooltip);
    }
    if (currentTerm && currentTerm !== term) currentTerm.removeAttribute('aria-describedby');
    currentTerm = term;
    term.setAttribute('aria-describedby', tooltip.id);
    const related = item.relatedLessonId ? `<a id="fam-glossary-rel-link" href="#${encodeURIComponent(item.relatedLessonId)}">مطالعهٔ درس مرتبط ←</a>` : '';
    tooltip.innerHTML = `<strong>${escapeHtml(item.term)}</strong><p>${escapeHtml(item.simple || item.fa || '')}</p>${related}`;
    tooltip.hidden = false;
    const rect = term.getBoundingClientRect();
    const box = tooltip.getBoundingClientRect();
    const left = Math.max(8, Math.min(window.innerWidth - box.width - 8, rect.right - box.width));
    const top = rect.bottom + 8 + box.height <= window.innerHeight ? rect.bottom + 8 : Math.max(8, rect.top - box.height - 8);
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  }

  if (!window.__famGlossaryWired) {
    window.__famGlossaryWired = true;
    document.addEventListener('pointerover', e => {
      if (e.pointerType === 'touch') return;
      const term = e.target.closest('.fam-glossary-term');
      if (term) showGlossary(term);
    });
    document.addEventListener('pointerout', e => {
      if (e.target.closest('.fam-glossary-term') && !e.relatedTarget?.closest?.('#fam-glossary-tooltip')) scheduleGlossaryHide();
    });
    document.addEventListener('focusin', e => {
      const term = e.target.closest('.fam-glossary-term');
      if (term) showGlossary(term);
    });
    document.addEventListener('focusout', e => {
      if (e.target.closest('.fam-glossary-term') && !e.relatedTarget?.closest?.('#fam-glossary-tooltip')) scheduleGlossaryHide();
    });
    // Touchscreens have no hover: tapping a term reveals the same definition.
    document.addEventListener('click', e => {
      const term = e.target.closest('.fam-glossary-term');
      if (term && glossaryEnabled) showGlossary(term);
      else if (e.target.closest('#fam-glossary-rel-link') || !e.target.closest('#fam-glossary-tooltip')) hideGlossary();
    });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') hideGlossary(); });
    document.addEventListener('scroll', hideGlossary, true);
  }

  window.FamLessonEngine = {
    buildSections,
    renderLesson,
    renderUnreadyLesson,
    renderVisualSvg,
    renderTopologySvg,
    isLessonDone,
    toggleLessonDone,
    getAdjacentLessons,
    isSectionDone,
    toggleSectionDone
  };
})();
