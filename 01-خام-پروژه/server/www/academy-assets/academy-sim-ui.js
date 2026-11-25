/* FAM Academy Interactive Simulators & Educational IOS CLI Lab UI */
(() => {
  'use strict';

  const esc = (v) =>
    String(v ?? '').replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));

  let activeTimer = null;
  function clearPlayTimer() {
    if (activeTimer) {
      clearInterval(activeTimer);
      activeTimer = null;
    }
  }

  function promptFor(state) {
    const host = state.hostname || 'Switch';
    if (state.mode === 'user') return host + '>';
    if (state.mode === 'privileged') return host + '#';
    if (state.mode === 'config') return host + '(config)#';
    if (state.mode === 'interface') return host + '(config-if)#';
    if (state.mode === 'vlan') return host + '(config-vlan)#';
    if (state.mode === 'router') return host + '(config-router)#';
    return host + '>';
  }

  function renderParamInput(p) {
    const id = esc(p.id);
    const label = esc(p.label);
    if (p.type === 'checkbox') {
      return `<label class="fam-sim-check"><input type="checkbox" data-sim-param="${id}" ${p.default ? 'checked' : ''}><span>${label}</span></label>`;
    }
    if (p.type === 'select') {
      const opts = (p.options || []).map((o) =>
        `<option value="${esc(o)}" ${o === p.default ? 'selected' : ''}>${esc(o)}</option>`
      ).join('');
      return `<div class="fam-sim-field"><label for="sim-p-${id}">${label}</label><select id="sim-p-${id}" data-sim-param="${id}">${opts}</select></div>`;
    }
    if (p.type === 'number') {
      const minAttr = p.min != null ? `min="${esc(p.min)}"` : '';
      const maxAttr = p.max != null ? `max="${esc(p.max)}"` : '';
      return `<div class="fam-sim-field"><label for="sim-p-${id}">${label}</label><input id="sim-p-${id}" type="number" data-sim-param="${id}" value="${esc(p.default)}" ${minAttr} ${maxAttr}></div>`;
    }
    return `<div class="fam-sim-field"><label for="sim-p-${id}">${label}</label><input id="sim-p-${id}" type="text" data-sim-param="${id}" value="${esc(p.default)}"></div>`;
  }

  function render(container, opts = {}) {
    clearPlayTimer();
    const Engine = window.FAMAcademySimEngine;
    if (!container) return;
    if (!Engine) {
      container.innerHTML = '<div class="fa-error">موتور شبیه‌ساز (academy-sim-engine.js) بارگذاری نشد.</div>';
      return;
    }

    const sims = Engine.SIMULATOR_DEFINITIONS || [];
    const labs = Engine.LAB_PRESETS || [];

    const state = {
      tab: opts.tab === 'labs' ? 'labs' : 'protocols',
      simId: opts.simId || (sims[0] && sims[0].id) || 'sim-arp',
      simResult: null,
      simActive: 0,
      labId: opts.labId || (labs[0] && labs[0].id) || 'lab-vlan-trunk',
      labState: null,
      labLog: [],
      labDoneSteps: new Set(),
      cmdHistory: [],
      cmdCursor: -1
    };

    function currentSim() {
      return sims.find((s) => s.id === state.simId) || sims[0];
    }

    function currentLab() {
      return labs.find((l) => l.id === state.labId) || labs[0];
    }

    function initLab(lab) {
      state.labState = Engine.createLabState(lab);
      state.labDoneSteps = new Set();
      state.labLog = [
        { type: 'out', text: Engine.OUTPUT_LABEL },
        { type: 'out', text: 'Educational Cisco IOS-like simulator ready (No real hardware connection).' },
        { type: 'out', text: 'Type "help" or click any guided step on the right.' }
      ];
    }
    initLab(currentLab());

    function collectParams(sim) {
      const out = {};
      sim.parameters.forEach((p) => { out[p.id] = p.default; });
      container.querySelectorAll('[data-sim-param]').forEach((el) => {
        const key = el.dataset.simParam;
        const def = sim.parameters.find((p) => p.id === key);
        if (!def) return;
        if (def.type === 'checkbox') out[key] = el.checked;
        else if (def.type === 'number') out[key] = Number(el.value);
        else out[key] = el.value;
      });
      return out;
    }

    function renderSimResultBox() {
      const box = container.querySelector('#fam-sim-result');
      if (!box) return;
      const r = state.simResult;
      if (!r) {
        box.innerHTML = '<div class="fam-sim-note">پارامترها را تغییر دهید و دکمهٔ «اجرا» را بزنید.</div>';
        return;
      }
      if (!r.ok) {
        box.innerHTML = `<div class="fam-sim-note warn"><strong>ورودی نامعتبر:</strong> ${esc(r.error)}</div>`;
        return;
      }

      const steps = r.steps || [];
      const active = Math.max(0, Math.min(state.simActive, steps.length - 1));
      const activeStep = steps[active];
      const stepBtns = steps.map((st, idx) =>
        `<button type="button" class="fam-sim-step-btn ${idx === active ? 'is-active' : ''}" data-sim-step="${idx}">${idx + 1}. ${esc(st.title || st.message)}</button>`
      ).join('');
      const rows = (r.table || []).map((row, idx) =>
        `<tr class="${idx === active ? 'is-active' : ''}">
          <td class="fam-sim-ltr">${esc(row.index || idx + 1)}</td>
          <td class="fam-sim-ltr">${esc(row.time)}</td>
          <td class="fam-sim-ltr">${esc(row.from)}</td>
          <td class="fam-sim-ltr">${esc(row.to)}</td>
          <td class="fam-sim-ltr">${esc(row.protocol)}</td>
          <td><strong>${esc(row.message)}</strong><br><span style="color:var(--c-text-2)">${esc(row.detail)}</span></td>
          <td class="fam-sim-ltr">${esc(row.size)}</td>
        </tr>`
      ).join('');

      box.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px">
          <span class="fam-sim-badge">${esc(r.label)}</span>
          <span class="fam-sim-badge ok">${esc(r.decision || r.finalState || 'اجرا شد')}</span>
        </div>
        <div class="fam-sim-summary"><strong>خلاصهٔ تحلیل:</strong> ${esc(r.summary)}</div>
        ${activeStep ? `<div class="fam-sim-note"><strong>گام ${active + 1}: ${esc(activeStep.title || activeStep.message)}</strong><br>${esc(activeStep.detail)}</div>` : ''}
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-top:12px">
          <strong style="font-size:.9rem">گام‌های تبادل و تصمیم</strong>
          <div class="fam-sim-actions">
            <button type="button" class="fam-sim-btn" data-sim-ctrl="play">پخش خودکار</button>
            <button type="button" class="fam-sim-btn" data-sim-ctrl="next">گام بعد</button>
            <button type="button" class="fam-sim-btn" data-sim-ctrl="reset">بازنشانی</button>
          </div>
        </div>
        <div class="fam-sim-steps">${stepBtns}</div>
        <div class="fam-sim-table-wrap">
          <table class="fam-sim-table">
            <thead>
              <tr><th>#</th><th>زمان</th><th>مبدأ</th><th>مقصد</th><th>پروتکل</th><th>پیام / جزئیات</th><th>اندازه</th></tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
        ${r.warnings && r.warnings.length ? `<div class="fam-sim-note warn"><strong>نکات و هشدارها:</strong><ul>${r.warnings.map((w) => `<li>${esc(w)}</li>`).join('')}</ul></div>` : ''}
        ${r.limitations && r.limitations.length ? `<div class="fam-sim-note"><strong>محدودیت‌های صادقانهٔ مدل:</strong><ul>${r.limitations.map((l) => `<li>${esc(l)}</li>`).join('')}</ul></div>` : ''}
      `;
    }

    function runCurrentSim() {
      clearPlayTimer();
      const sim = currentSim();
      const params = collectParams(sim);
      state.simResult = Engine[sim.logic](params);
      state.simActive = 0;
      renderSimResultBox();
    }

    function appendLabOutput(cmdText) {
      const clean = String(cmdText || '').trim();
      if (!clean) return;
      if (/^clear$/i.test(clean)) {
        state.labLog = [{ type: 'out', text: Engine.OUTPUT_LABEL }];
        updateLabTerminal();
        return;
      }
      state.cmdHistory.push(clean);
      state.cmdCursor = state.cmdHistory.length;
      const pfx = promptFor(state.labState);
      const res = Engine.runLabCommand(state.labState, clean);
      state.labLog.push({ type: 'cmd', text: pfx + ' ' + clean });
      res.output.forEach((line) => state.labLog.push({ type: res.matched ? 'out' : 'warn', text: line }));
      updateLabTerminal();
    }

    function updateLabTerminal() {
      const logEl = container.querySelector('#fam-lab-log');
      const promptEl = container.querySelector('#fam-lab-prompt');
      if (promptEl && state.labState) promptEl.textContent = promptFor(state.labState);
      if (!logEl) return;
      logEl.innerHTML = state.labLog.map((entry) => {
        if (entry.type === 'cmd') return `<span class="is-cmd">${esc(entry.text)}</span>`;
        if (entry.type === 'warn') return `<span class="is-warn">${esc(entry.text)}</span>`;
        return esc(entry.text);
      }).join('\n');
      logEl.scrollTop = logEl.scrollHeight;
    }

    function renderView() {
      clearPlayTimer();
      const backBar = typeof opts.onBack === 'function'
        ? '<button type="button" class="fa-action fa-back-btn" id="fam-sim-back">← بازگشت به نمای قبلی</button>'
        : '';
      const header = `
        <section class="fam-sim-hero">
          <div>
            <span class="fam-sim-kicker">INTERACTIVE SIMULATOR &amp; SAFE CLI SANDBOX</span>
            <h1>شبیه‌سازهای تعاملی شبکه و ترمینال Cisco IOS</h1>
            <p>آزمایش تغییر پارامترهای پروتکل (ARP، VLAN/Trunk، OSPF) و اجرای دستورات IOS در محیط شبیه‌سازی‌شده بدون اتصال به تجهیزات واقعی.</p>
          </div>
          <div class="fam-sim-tabs" role="tablist" aria-label="بخش‌های شبیه‌ساز">
            <button type="button" class="fam-sim-tab ${state.tab === 'protocols' ? 'is-active' : ''}" data-sim-tab="protocols">شبیه‌ساز پروتکل‌ها</button>
            <button type="button" class="fam-sim-tab ${state.tab === 'labs' ? 'is-active' : ''}" data-sim-tab="labs">آزمایشگاه ترمینال IOS</button>
          </div>
        </section>
      `;

      let body = '';
      if (state.tab === 'protocols') {
        const sim = currentSim();
        const chips = sims.map((s) =>
          `<button type="button" class="fam-sim-chip ${s.id === sim.id ? 'is-active' : ''}" data-sim-pick="${esc(s.id)}">${esc(s.title)}</button>`
        ).join('');
        body = `
          <div class="fam-sim-card">
            <div class="fam-sim-selector">${chips}</div>
            <p style="margin:0 0 14px;color:var(--c-text-2);font-size:.88rem">${esc(sim.objective)}</p>
            <div class="fam-sim-grid">
              <aside class="fam-sim-controls">
                <h2>پارامترهای ورودی</h2>
                ${sim.parameters.map(renderParamInput).join('')}
                <div class="fam-sim-actions">
                  <button type="button" class="fam-sim-btn primary" data-sim-ctrl="run">اجرای شبیه‌ساز</button>
                  <button type="button" class="fam-sim-btn" data-sim-ctrl="reset-params">مقادیر پیش‌فرض</button>
                </div>
              </aside>
              <div id="fam-sim-result"></div>
            </div>
          </div>
        `;
      } else {
        const lab = currentLab();
        const labChips = labs.map((l) =>
          `<button type="button" class="fam-sim-chip ${l.id === lab.id ? 'is-active' : ''}" data-lab-pick="${esc(l.id)}">${esc(l.title)}</button>`
        ).join('');
        const stepsHtml = lab.steps.map((st, idx) =>
          `<button type="button" class="fam-sim-step-btn ${state.labDoneSteps.has(st.id) ? 'is-done' : ''}" data-lab-step="${esc(st.id)}">
            ${idx + 1}. ${esc(st.title)} (${st.commands.length} دستور)
          </button>`
        ).join('');
        body = `
          <div class="fam-sim-card">
            <div class="fam-sim-selector">${labChips}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px">
              <p style="margin:0;color:var(--c-text-2);font-size:.88rem">${esc(lab.scenario)}</p>
              <span class="fam-sim-badge warn">${esc(Engine.OUTPUT_LABEL)}</span>
            </div>
            <div class="fam-sim-grid">
              <aside class="fam-sim-controls">
                <h2>گام‌های هدایت‌شدهٔ لاب</h2>
                <div style="display:grid;gap:8px">${stepsHtml}</div>
                <div class="fam-sim-actions">
                  <button type="button" class="fam-sim-btn" data-lab-ctrl="reset">بازنشانی ترمینال لاب</button>
                </div>
                <div class="fam-sim-note" style="margin-top:4px">
                  می‌توانید گام‌ها را کلیک کنید یا مستقیماً دستور Cisco IOS را در ترمینال بنویسید (برای فهرست دستورها <code>help</code> بزنید).
                </div>
              </aside>
              <div class="fam-sim-terminal">
                <div class="fam-sim-term-head">
                  <span>FAM Educational IOS CLI Sandbox</span>
                  <span>No live hardware connection</span>
                </div>
                <pre class="fam-sim-term-log" id="fam-lab-log"></pre>
                <div class="fam-sim-term-input">
                  <span class="fam-sim-prompt" id="fam-lab-prompt">${esc(promptFor(state.labState))}</span>
                  <input id="fam-lab-cmd" type="text" autocomplete="off" spellcheck="false" placeholder="enable / configure terminal / show vlan brief / help">
                  <button type="button" class="fam-sim-btn primary" data-lab-ctrl="exec">اجرا</button>
                </div>
              </div>
            </div>
          </div>
        `;
      }

      container.innerHTML = `<div class="fam-sim-wrap">${backBar}${header}${body}</div>`;

      if (state.tab === 'protocols') {
        runCurrentSim();
      } else {
        updateLabTerminal();
      }

      const backBtn = container.querySelector('#fam-sim-back');
      if (backBtn) backBtn.onclick = () => { clearPlayTimer(); opts.onBack(); };
    }

    container.onclick = (e) => {
      const tabBtn = e.target.closest('[data-sim-tab]');
      if (tabBtn) {
        state.tab = tabBtn.dataset.simTab;
        renderView();
        return;
      }
      const simPick = e.target.closest('[data-sim-pick]');
      if (simPick) {
        state.simId = simPick.dataset.simPick;
        renderView();
        return;
      }
      const simStep = e.target.closest('[data-sim-step]');
      if (simStep) {
        clearPlayTimer();
        state.simActive = Number(simStep.dataset.simStep) || 0;
        renderSimResultBox();
        return;
      }
      const simCtrl = e.target.closest('[data-sim-ctrl]');
      if (simCtrl) {
        const act = simCtrl.dataset.simCtrl;
        if (act === 'run') runCurrentSim();
        else if (act === 'reset-params') renderView();
        else if (act === 'reset') {
          clearPlayTimer();
          state.simActive = 0;
          renderSimResultBox();
        } else if (act === 'next') {
          clearPlayTimer();
          if (!state.simResult) runCurrentSim();
          const max = Math.max(0, (state.simResult?.steps?.length || 1) - 1);
          state.simActive = Math.min(max, state.simActive + 1);
          renderSimResultBox();
        } else if (act === 'play') {
          if (!state.simResult) runCurrentSim();
          clearPlayTimer();
          state.simActive = 0;
          renderSimResultBox();
          activeTimer = setInterval(() => {
            const max = Math.max(0, (state.simResult?.steps?.length || 1) - 1);
            if (state.simActive >= max) {
              clearPlayTimer();
              return;
            }
            state.simActive += 1;
            renderSimResultBox();
          }, 750);
        }
        return;
      }

      const labPick = e.target.closest('[data-lab-pick]');
      if (labPick) {
        state.labId = labPick.dataset.labPick;
        initLab(currentLab());
        renderView();
        return;
      }
      const labStep = e.target.closest('[data-lab-step]');
      if (labStep) {
        const sid = labStep.dataset.labStep;
        const stepObj = currentLab().steps.find((s) => s.id === sid);
        if (stepObj) {
          stepObj.commands.forEach((c) => appendLabOutput(c));
          state.labDoneSteps.add(sid);
          container.querySelectorAll('[data-lab-step]').forEach((btn) => {
            if (btn.dataset.labStep === sid) btn.classList.add('is-done');
          });
        }
        return;
      }
      const labCtrl = e.target.closest('[data-lab-ctrl]');
      if (labCtrl) {
        const act = labCtrl.dataset.labCtrl;
        if (act === 'reset') {
          initLab(currentLab());
          renderView();
        } else if (act === 'exec') {
          const inp = container.querySelector('#fam-lab-cmd');
          if (inp && inp.value.trim()) {
            appendLabOutput(inp.value);
            inp.value = '';
          }
        }
      }
    };

    container.onkeydown = (e) => {
      if (e.target && e.target.id === 'fam-lab-cmd') {
        if (e.key === 'Enter') {
          e.preventDefault();
          if (e.target.value.trim()) {
            appendLabOutput(e.target.value);
            e.target.value = '';
          }
        } else if (e.key === 'ArrowUp' && state.cmdHistory.length) {
          e.preventDefault();
          state.cmdCursor = Math.max(0, state.cmdCursor - 1);
          e.target.value = state.cmdHistory[state.cmdCursor] || '';
        } else if (e.key === 'ArrowDown' && state.cmdHistory.length) {
          e.preventDefault();
          state.cmdCursor = Math.min(state.cmdHistory.length, state.cmdCursor + 1);
          e.target.value = state.cmdHistory[state.cmdCursor] || '';
        }
      }
    };

    renderView();
  }

  window.FamAcademySimUI = { render };
})();
