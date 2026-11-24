/* FAM Academy Two-Mode Level Selector & Smart Placement Exam */
(() => {
  'use strict';

  const esc = (v) =>
    String(v ?? '').replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));

  const DEFAULT_FACULTIES = [
    { id: 'f0', tier: 0, badge: 'دانشکده ۰ · ۱ ماه', title: 'ارزیابی و تکمیل مبانی', duration: '۱ ماه', note: 'آزمون تعیین سطح و پوشش شکاف‌های پایه (OSI، IPv4، Subnetting، ARP، DNS/DHCP)' },
    { id: 'f1', tier: 1, badge: 'دانشکده ۱ · ۳ + ۵ ماه (ماه ۲ تا ۶)', title: 'Network Engineering Foundations & CCNA 200-301', duration: '۳ + ۵ ماه (ماه ۲ تا ۶)', note: 'پایهٔ مهندسی شبکه، Switching/VLAN، OSPF، امنیت پایه و مدرک 200-301 CCNA' },
    { id: 'f2', tier: 2, badge: 'دانشکده ۲ · ۶ ماه (ماه ۷ تا ۱۲)', title: 'مهندسی Routing & Switching (Advanced)', duration: '۶ ماه (ماه ۷ تا ۱۲)', note: 'ایجاد مهندس شبکه واقعی فراتر از CCNA (RSTP/MST، EtherChannel، BGP، VRF، Redistribution)' },
    { id: 'f3', tier: 3, badge: 'دانشکده ۳ · ۸ ماه (ماه ۱۳ تا ۲۰)', title: 'CCNP Enterprise', duration: '۸ ماه (ماه ۱۳ تا ۲۰)', note: '350-401 ENCOR + آزمون تخصصی انتخابی' },
    { id: 'f4', tier: 4, badge: 'دانشکده ۴ · ۱۸ تا ۳۰ ماه', title: 'هشت مسیر تخصصی اصلی', duration: '۱۸ تا ۳۰ ماه', note: 'Enterprise، Security، Data Center، SP، Wireless، Collaboration، Automation، Cybersecurity' },
    { id: 'f5', tier: 5, badge: 'دانشکده ۵ / ۸ · ۱۲ تا ۲۴ ماه', title: 'CCIE در شاخه منتخب (Expert)', duration: '۱۲ تا ۲۴ ماه', note: 'آزمون Core + آزمون عملی Lab و ۲۰۰ سناریو' },
    { id: 'f6', tier: 6, badge: 'دانشکده ۶ / ۹ · ۱۲ تا ۱۸ ماه', title: 'CCDE و معماری زیرساخت', duration: '۱۲ تا ۱۸ ماه', note: 'تصمیم‌گیری معماری کلان و آزمون 400-007' }
  ];

  let bankCache = null;

  async function loadBank() {
    if (bankCache) return bankCache;
    const res = await fetch('/academy-assets/academy-placement-questions.json?v=20261123h', { credentials: 'same-origin', cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    bankCache = await res.json();
    return bankCache;
  }

  function getActiveFaculty() {
    const profile = window.FamAcademyBridge?.progress?.profile || {};
    const list = bankCache?.faculties || DEFAULT_FACULTIES;
    const fid = profile.facultyId || profile.currentStage;
    if (fid) {
      const found = list.find((f) => f.id === fid);
      if (found) return found;
    }
    const legacy = profile.level;
    if (legacy === 'advanced') return list[3] || list[0];
    if (legacy === 'intermediate') return list[1] || list[0];
    return list[0];
  }

  function mapFacultyToLevel(facultyId) {
    if (facultyId === 'f0') return 'beginner';
    if (facultyId === 'f1' || facultyId === 'f2') return 'intermediate';
    return 'advanced';
  }

  function evaluateOffline(bank, answers) {
    const faculties = bank.faculties || DEFAULT_FACULTIES;
    const questions = bank.questions || [];
    const tierStats = {};
    faculties.forEach((f) => {
      tierStats[f.tier] = { id: f.id, tier: f.tier, badge: f.badge, title: f.title, duration: f.duration, correct: 0, total: 0 };
    });
    let totalCorrect = 0;
    const items = questions.map((q) => {
      const sel = answers[q.id];
      const ok = sel === q.correctIndex;
      const st = tierStats[q.tier];
      if (st) {
        st.total += 1;
        if (ok) {
          st.correct += 1;
          totalCorrect += 1;
        }
      }
      return {
        id: q.id,
        tier: q.tier,
        topic: q.topic,
        answered: sel != null,
        selectedIndex: sel ?? null,
        correctIndex: q.correctIndex,
        correct: ok,
        correctOption: (q.options || [])[q.correctIndex] || '',
        explanation: q.explanation || ''
      };
    });
    const tiers = Object.keys(tierStats).map(Number).sort((a, b) => a - b);
    let recTier = tiers[0] ?? 0;
    const weakTiers = [];
    for (let i = 0; i < tiers.length; i += 1) {
      const t = tiers[i];
      const st = tierStats[t];
      if (st.total > 0 && st.correct === st.total) {
        recTier = Math.min(tiers[tiers.length - 1], t + 1);
      } else if (st.total > 0 && st.correct * 2 >= st.total && tierStats[t + 1] && tierStats[t + 1].correct === tierStats[t + 1].total) {
        weakTiers.push(st.title);
        recTier = t + 1;
      } else {
        recTier = t;
        if (st.correct < st.total) weakTiers.push(st.title);
        break;
      }
    }
    const breakdown = tiers.map((t) => {
      const st = tierStats[t];
      const status = st.total > 0 && st.correct === st.total ? 'mastered' : (st.correct > 0 ? 'partial' : 'gap');
      return { ...st, status };
    });
    const recFaculty = faculties.find((f) => f.tier === recTier) || faculties[0];
    const totalQuestions = questions.length;
    const scorePct = totalQuestions ? Math.round((totalCorrect * 100) / totalQuestions) : 0;
    return {
      ok: true,
      recommendedFaculty: recFaculty,
      recommendedTier: recTier,
      totalCorrect,
      totalQuestions,
      scorePct,
      tierBreakdown: breakdown,
      weakTiers,
      summaryFa: `بر اساس تحلیل مرحله‌به‌مرحلهٔ پاسخ‌های شما (${totalCorrect} از ${totalQuestions} پاسخ صحیح)، نقطهٔ شروع پیشنهادی شما «${recFaculty.badge} — ${recFaculty.title}» است.`,
      items
    };
  }

  async function saveSelectedFaculty({ facultyId, placementMode, minutesPerDay, placementResult }) {
    const progress = window.FamAcademyBridge?.progress || { completed: [], labs: {} };
    const existingProfile = progress.profile || {};
    const updatedProfile = {
      ...existingProfile,
      onboardingComplete: true,
      goal: 'fam-c5',
      facultyId,
      currentStage: facultyId,
      placementMode,
      level: mapFacultyToLevel(facultyId),
      minutesPerDay: Number(minutesPerDay) || Number(existingProfile.minutesPerDay) || 120,
      daysPerWeek: Number(existingProfile.daysPerWeek) || 7,
      studyDays: Array.isArray(existingProfile.studyDays) && existingProfile.studyDays.length
        ? existingProfile.studyDays
        : ['sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri'],
      placementResult: placementResult || existingProfile.placementResult || null
    };
    const completed = window.FamAcademyCatalog?.getCompletedSet
      ? [...window.FamAcademyCatalog.getCompletedSet()]
      : (Array.isArray(progress.completed) ? progress.completed : []);
    return window.FamAcademyBridge?.saveProgress({
      ...progress,
      completed,
      profile: updatedProfile
    });
  }

  async function renderPlacementView(container, opts = {}) {
    if (!container) return;
    container.innerHTML = '<div class="fa-loading">در حال آماده‌سازی انتخاب سطح و آزمون تعیین سطح…</div>';
    let bank;
    try {
      bank = await loadBank();
    } catch (e) {
      bank = { faculties: DEFAULT_FACULTIES, questions: [] };
    }

    const faculties = bank.faculties || DEFAULT_FACULTIES;
    const questions = bank.questions || [];
    const currentProfile = window.FamAcademyBridge?.progress?.profile || {};

    const state = {
      mode: currentProfile.placementMode === 'exam' && opts.startExam ? 'exam' : 'manual',
      selectedFacultyId: currentProfile.facultyId || faculties[0].id,
      minutesPerDay: Number(currentProfile.minutesPerDay) || 120,
      qIndex: 0,
      answers: {},
      examResult: null,
      saving: false,
      error: ''
    };

    function draw() {
      const modeCards = `
        <div class="fam-mode-switch" role="tablist" aria-label="روش انتخاب سطح">
          <button type="button" class="fam-mode-card ${state.mode === 'manual' ? 'is-active' : ''}" data-pmode="manual">
            <span class="fam-mode-badge">حالت ۱ · انتخاب مستقیم</span>
            <strong>سطح خودم را می‌دانم (انتخاب دستی)</strong>
            <span>اگر می‌دانی از کدام دانشکده (از مبانی تا CCNA، CCNP، تخصص‌ها، CCIE یا CCDE) شروع کنی، مستقیم دانشکدهٔ خودت را انتخاب کن.</span>
          </button>
          <button type="button" class="fam-mode-card ${state.mode === 'exam' ? 'is-active' : ''}" data-pmode="exam">
            <span class="fam-mode-badge">حالت ۲ · سنجش هوشمند</span>
            <strong>سطح خودم را نمی‌دانم (آزمون ۴گزینه‌ای هوشمند)</strong>
            <span>با ۱۴ سؤال استاندارد از تمام سطوح (دانشکده ۰ تا ۶)، سطح واقعی تو با تحلیل مرحله‌ای تشخیص داده می‌شود.</span>
          </button>
        </div>
      `;

      let panelHtml = '';
      if (state.mode === 'manual') {
        const cards = faculties.map((f) => {
          const picked = state.selectedFacultyId === f.id;
          return `
            <button type="button" class="fam-faculty-option ${picked ? 'is-selected' : ''}" data-pick-faculty="${esc(f.id)}">
              <div class="fam-faculty-top">
                <span class="fam-faculty-badge">${esc(f.badge)}</span>
                <span>${picked ? '✓ انتخاب‌شده' : 'انتخاب'}</span>
              </div>
              <strong>${esc(f.title)}</strong>
              <small>${esc(f.note)}</small>
            </button>
          `;
        }).join('');

        panelHtml = `
          <div class="fam-faculty-list">${cards}</div>
          <div class="fam-place-footer">
            <label>
              زمان مطالعهٔ روزانه:
              <select id="fam-place-mins">
                ${[30, 60, 90, 120].map((m) => `<option value="${m}" ${state.minutesPerDay === m ? 'selected' : ''}>${m} دقیقه</option>`).join('')}
              </select>
            </label>
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
              ${typeof opts.onCancel === 'function' ? '<button type="button" class="fam-btn-secondary" data-paction="cancel">انصراف</button>' : ''}
              <button type="button" class="fam-btn-primary" data-paction="confirm-manual" ${state.saving ? 'disabled' : ''}>
                ${state.saving ? 'در حال ذخیره…' : 'تأیید و ورود به مسیر یادگیری ←'}
              </button>
            </div>
          </div>
        `;
      } else if (!state.examResult) {
        if (!questions.length) {
          panelHtml = '<div class="fa-error">بانک سؤال آزمون تعیین سطح بارگذاری نشد.</div>';
        } else {
          const q = questions[state.qIndex];
          const fac = faculties.find((f) => f.id === q.facultyId) || faculties[0];
          const pct = Math.round(((state.qIndex + 1) / questions.length) * 100);
          const pickedIdx = state.answers[q.id];
          const answeredCount = Object.keys(state.answers).length;
          const optsHtml = (q.options || []).map((opt, idx) => `
            <button type="button" class="fam-exam-opt ${pickedIdx === idx ? 'is-picked' : ''}" data-pick-opt="${idx}">
              <strong>${idx + 1}.</strong>
              <span>${esc(opt)}</span>
            </button>
          `).join('');

          panelHtml = `
            <div class="fam-exam-card">
              <div class="fam-exam-progress">
                <div class="fam-exam-progress-meta">
                  <span>سؤال ${state.qIndex + 1} از ${questions.length} · <strong dir="ltr">${esc(q.topic)}</strong></span>
                  <span class="fam-faculty-badge">سطح ارزیابی: ${esc(fac.badge)}</span>
                </div>
                <div class="fam-exam-bar"><span style="width:${pct}%"></span></div>
              </div>
              <p class="fam-exam-q">${esc(q.question)}</p>
              <div class="fam-exam-opts">${optsHtml}</div>
              <div class="fam-exam-nav">
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                  <button type="button" class="fam-btn-secondary" data-paction="prev-q" ${state.qIndex === 0 ? 'disabled' : ''}>← سؤال قبلی</button>
                  <button type="button" class="fam-btn-secondary" data-paction="skip-q">نمی‌دانم / رد شدن</button>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
                  <small style="color:var(--c-text-3)">پاسخ‌داده‌شده: ${answeredCount} از ${questions.length}</small>
                  ${state.qIndex < questions.length - 1
                    ? '<button type="button" class="fam-btn-primary" data-paction="next-q">سؤال بعدی ←</button>'
                    : `<button type="button" class="fam-btn-primary" data-paction="submit-exam" ${state.saving ? 'disabled' : ''}>تحلیل هوشمند و تعیین سطح ←</button>`
                  }
                </div>
              </div>
            </div>
          `;
        }
      } else {
        const res = state.examResult;
        const rec = res.recommendedFaculty;
        const tierHtml = (res.tierBreakdown || []).map((t) => {
          const lbl = t.status === 'mastered' ? 'تسلط کامل' : t.status === 'partial' ? 'آشنایی نسبی' : 'نیاز به یادگیری';
          return `
            <div class="fam-tier-item is-${esc(t.status)}">
              <span class="fam-faculty-badge" style="width:fit-content">${esc(t.badge)}</span>
              <strong>${esc(t.title)}</strong>
              <small>${t.correct} از ${t.total} صحیح · <b>${lbl}</b></small>
            </div>
          `;
        }).join('');

        const reviewHtml = (res.items || []).map((it, idx) => `
          <details style="background:var(--c-surface-2);border:1px solid var(--c-border);border-radius:10px;padding:10px 12px">
            <summary style="cursor:pointer;font-weight:700;color:${it.correct ? 'var(--c-done)' : 'var(--c-review)'}">
              سؤال ${idx + 1} (${esc(it.topic)}) — ${it.correct ? '✓ پاسخ صحیح' : it.answered ? '✕ پاسخ نادرست' : '○ بدون پاسخ'}
            </summary>
            <p style="margin:8px 0 4px;font-size:.86rem"><strong>پاسخ صحیح:</strong> ${esc(it.correctOption)}</p>
            <p style="margin:0;font-size:.84rem;color:var(--c-text-2)">${esc(it.explanation)}</p>
          </details>
        `).join('');

        panelHtml = `
          <div class="fam-exam-card">
            <span class="fam-kicker">SMART PLACEMENT RESULT</span>
            <h2 style="margin:0;font-size:1.3rem">${esc(rec.badge)} — ${esc(rec.title)}</h2>
            <p style="margin:0;color:var(--c-text-2);line-height:1.8">${esc(res.summaryFa)}</p>
            ${res.weakTiers && res.weakTiers.length ? `<div class="fam-sim-note warn"><strong>نقاط نیازمند مرور / تمرکز:</strong> ${esc(res.weakTiers.join('، '))}</div>` : ''}
            <div class="fam-tier-grid">${tierHtml}</div>
            <div class="fam-place-footer">
              <label>
                زمان مطالعهٔ روزانه:
                <select id="fam-place-mins">
                  ${[30, 60, 90, 120].map((m) => `<option value="${m}" ${state.minutesPerDay === m ? 'selected' : ''}>${m} دقیقه</option>`).join('')}
                </select>
              </label>
              <div style="display:flex;gap:10px;flex-wrap:wrap">
                <button type="button" class="fam-btn-secondary" data-paction="retake-exam">آزمون مجدد</button>
                <button type="button" class="fam-btn-primary" data-paction="confirm-exam" ${state.saving ? 'disabled' : ''}>
                  ${state.saving ? 'در حال ذخیره…' : `شروع مسیر از ${esc(rec.badge)} ←`}
                </button>
              </div>
            </div>
            <div style="display:grid;gap:8px;margin-top:6px">
              <strong style="font-size:.92rem">تحلیل پرسش‌به‌پرسش</strong>
              ${reviewHtml}
            </div>
          </div>
        `;
      }

      container.innerHTML = `
        <div class="fam-clean-wrap">
          <section class="fam-place-hero">
            <span class="fam-kicker">STEP 1 · CHOOSE YOUR LEVEL</span>
            <h1>نقطهٔ شروع خودت در آکادمی FAM را انتخاب کن</h1>
            <p>برای اینکه در میان درس‌ها و مسیرها سردرگم نشوی، اول مشخص کن در کدام سطح هستی؛ یا اگر مطمئن نیستی، بگذار آزمون هوشمند ۴گزینه‌ای سطحت را تشخیص دهد.</p>
          </section>
          ${modeCards}
          ${state.error ? `<div class="fa-error">${esc(state.error)}</div>` : ''}
          ${panelHtml}
        </div>
      `;
    }

    container.onclick = async (e) => {
      const modeBtn = e.target.closest('[data-pmode]');
      if (modeBtn) {
        state.mode = modeBtn.dataset.pmode;
        state.error = '';
        draw();
        return;
      }
      const facBtn = e.target.closest('[data-pick-faculty]');
      if (facBtn) {
        state.selectedFacultyId = facBtn.dataset.pickFaculty;
        draw();
        return;
      }
      const optBtn = e.target.closest('[data-pick-opt]');
      if (optBtn) {
        const q = questions[state.qIndex];
        if (q) {
          state.answers[q.id] = Number(optBtn.dataset.pickOpt);
          draw();
        }
        return;
      }
      const actBtn = e.target.closest('[data-paction]');
      if (!actBtn) return;
      const act = actBtn.dataset.paction;

      const minsEl = container.querySelector('#fam-place-mins');
      if (minsEl) state.minutesPerDay = Number(minsEl.value) || 120;

      if (act === 'cancel') {
        if (typeof opts.onCancel === 'function') opts.onCancel();
      } else if (act === 'prev-q') {
        state.qIndex = Math.max(0, state.qIndex - 1);
        draw();
      } else if (act === 'next-q') {
        state.qIndex = Math.min(questions.length - 1, state.qIndex + 1);
        draw();
      } else if (act === 'skip-q') {
        const q = questions[state.qIndex];
        if (q) delete state.answers[q.id];
        if (state.qIndex < questions.length - 1) {
          state.qIndex += 1;
          draw();
        } else {
          state.saving = true;
          state.error = '';
          draw();
          let evaluated = null;
          if (window.FamAcademyBridge && typeof window.FamAcademyBridge.evaluatePlacement === 'function') {
            evaluated = await window.FamAcademyBridge.evaluatePlacement(state.answers);
          }
          if (!evaluated || !evaluated.ok) evaluated = evaluateOffline(bank, state.answers);
          state.saving = false;
          state.examResult = evaluated;
          state.selectedFacultyId = evaluated.recommendedFaculty.id;
          draw();
        }
      } else if (act === 'retake-exam') {
        state.answers = {};
        state.qIndex = 0;
        state.examResult = null;
        draw();
      } else if (act === 'submit-exam') {
        state.saving = true;
        state.error = '';
        draw();
        let evaluated = null;
        if (window.FamAcademyBridge && typeof window.FamAcademyBridge.evaluatePlacement === 'function') {
          evaluated = await window.FamAcademyBridge.evaluatePlacement(state.answers);
        }
        if (!evaluated || !evaluated.ok) {
          evaluated = evaluateOffline(bank, state.answers);
        }
        state.saving = false;
        state.examResult = evaluated;
        state.selectedFacultyId = evaluated.recommendedFaculty.id;
        draw();
      } else if (act === 'confirm-manual' || act === 'confirm-exam') {
        state.saving = true;
        state.error = '';
        draw();
        const chosenId = act === 'confirm-exam' && state.examResult
          ? state.examResult.recommendedFaculty.id
          : state.selectedFacultyId;
        const ok = await saveSelectedFaculty({
          facultyId: chosenId,
          placementMode: act === 'confirm-exam' ? 'exam' : 'manual',
          minutesPerDay: state.minutesPerDay,
          placementResult: act === 'confirm-exam' && state.examResult
            ? {
                scorePct: state.examResult.scorePct,
                totalCorrect: state.examResult.totalCorrect,
                totalQuestions: state.examResult.totalQuestions,
                recommendedFacultyId: chosenId
              }
            : null
        });
        state.saving = false;
        if (ok === false) {
          state.error = 'ذخیرهٔ سطح در سرور انجام نشد؛ لطفاً اتصال را بررسی کنید.';
          draw();
          return;
        }
        if (typeof opts.onComplete === 'function') opts.onComplete(chosenId);
        else location.hash = '#/dashboard';
      }
    };

    draw();
    window.scrollTo({ top: 0, behavior: 'auto' });
  }

  window.FamAcademyPlacement = {
    FACULTIES: DEFAULT_FACULTIES,
    getActiveFaculty,
    renderPlacementView
  };
})();
