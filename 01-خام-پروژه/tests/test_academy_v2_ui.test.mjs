/* FAM Academy v2 SPA integration test with a minimal DOM shim.
 *
 * This is NOT a visual browser test: no Chromium/Playwright/Selenium is
 * available in the sandbox. It executes the real academy-v2.js against a
 * deterministic DOM/fetch shim and either the local versioned JSON files or,
 * when ACADEMY_V2_API_BASE is set, the real preview HTTP API. It verifies the
 * full presentation flow: dashboard -> paths -> course -> lesson -> simulator
 * -> lab -> quiz -> saved progress.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const require = createRequire(import.meta.url);
const here = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(here, '..');
const serverRoot = join(packageRoot, 'server');
const assets = join(serverRoot, 'www', 'academy-assets');
const v1 = join(serverRoot, 'www', 'academy-content', 'v1');
const appPath = join(assets, 'academy-v2.js');
const engine = require(join(assets, 'academy-engine.js'));
const API_BASE = process.env.ACADEMY_V2_API_BASE || '';
const nativeFetch = globalThis.fetch;

function readJson(rel) {
  return JSON.parse(readFileSync(join(v1, rel), 'utf8'));
}

const catalog = readJson('catalog.json');
const exercises = readJson('exercises.json');
const references = readJson('references.json');
const lessons = new Map(catalog.lessons.map((s) => [s.id, readJson(`lessons/${s.id}.json`)]));
const simulations = new Map(catalog.simulations.map((s) => [s.id, readJson(`simulations/${s.id}.json`)]));
const labs = new Map(catalog.labs.map((l) => [l.id, readJson(`labs/${l.id}.json`)]));

function makeClassList() {
  const values = new Set();
  return {
    add(name) { values.add(name); },
    remove(name) { values.delete(name); },
    contains(name) { return values.has(name); },
    toggle(name, force) {
      const next = force === undefined ? !values.has(name) : Boolean(force);
      if (next) values.add(name); else values.delete(name);
      return next;
    },
  };
}

function createHarness() {
  let rootHtml = '';
  let viewHtml = '';
  let hash = '';
  const elements = new Map();
  const windowListeners = new Map();
  const documentListeners = new Map();
  const localStorageMap = new Map();
  const checkedAnswers = new Map();
  const paramOverrides = new Map();

  function makeElement(id = '') {
    const el = {
      id,
      dataset: {},
      classList: makeClassList(),
      value: '',
      checked: false,
      scrollTop: 0,
      scrollHeight: 0,
      style: {},
      _html: '',
    };
    Object.defineProperty(el, 'innerHTML', {
      get() { return el._html; },
      set(value) {
        el._html = String(value);
        registerIds(el._html);
        if (el.id === 'fam-app') rootHtml = el._html;
        if (el.id === 'view') viewHtml = el._html;
      },
    });
    return el;
  }

  function registerIds(html) {
    const re = /id="([^"]+)"/g;
    let match;
    while ((match = re.exec(html)) !== null) {
      const id = match[1];
      if (!elements.has(id)) elements.set(id, makeElement(id));
    }
  }

  const root = makeElement('fam-app');
  elements.set('fam-app', root);

  const location = {
    get hash() { return hash; },
    set hash(value) { hash = String(value); },
  };

  function parseParamElements() {
    const result = [];
    const tagRe = /<(input|select)\b([^>]*)>/gi;
    let match;
    while ((match = tagRe.exec(viewHtml)) !== null) {
      const tagName = match[1].toLowerCase();
      const attrs = match[2];
      const paramMatch = /data-param="([^"]+)"/.exec(attrs);
      if (!paramMatch) continue;
      const id = paramMatch[1];
      const el = { dataset: { param: id }, value: '', checked: false, classList: makeClassList() };
      if (/type="checkbox"/i.test(attrs)) {
        el.checked = /\bchecked\b/i.test(attrs);
      } else if (tagName === 'select') {
        const end = viewHtml.indexOf('</select>', match.index);
        const block = viewHtml.slice(match.index, end >= 0 ? end + 9 : viewHtml.length);
        const optionRe = /<option\b([^>]*)>/gi;
        let option;
        while ((option = optionRe.exec(block)) !== null) {
          if (/\bselected\b/i.test(option[1])) {
            const value = /value="([^"]*)"/i.exec(option[1]);
            el.value = value ? value[1] : '';
            break;
          }
        }
      } else {
        const value = /value="([^"]*)"/i.exec(attrs);
        el.value = value ? value[1] : '';
      }
      if (paramOverrides.has(id)) {
        const override = paramOverrides.get(id);
        if (typeof override === 'boolean') el.checked = override;
        else el.value = String(override);
      }
      result.push(el);
    }
    return result;
  }

  function querySelectorAll(selector) {
    if (selector.indexOf('.nav-btn') !== -1) {
      const result = [];
      const re = /<button\b[^>]*class="[^"]*nav-btn[^"]*"[^>]*data-route="([^"]+)"[^>]*>/gi;
      let match;
      while ((match = re.exec(rootHtml)) !== null) {
        result.push({ dataset: { route: match[1] }, classList: makeClassList() });
      }
      return result;
    }
    if (selector === '[data-param]') return parseParamElements();
    return [];
  }

  function querySelector(selector) {
    const radio = /^input\[name="q(\d+)"\]:checked$/.exec(selector);
    if (radio) {
      const index = Number(radio[1]);
      return checkedAnswers.has(index) ? { value: String(checkedAnswers.get(index)) } : null;
    }
    const labStep = /^\[data-action="lab-step"\]\[data-step="([^"]+)"\]$/.exec(selector);
    if (labStep) return { dataset: { step: labStep[1] }, classList: makeClassList() };
    return null;
  }

  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeElement(id));
      return elements.get(id);
    },
    querySelector,
    querySelectorAll,
    addEventListener(type, listener) {
      if (!documentListeners.has(type)) documentListeners.set(type, []);
      documentListeners.get(type).push(listener);
    },
  };

  const window = {
    FAM_ACADEMY_BOOTSTRAP: {
      previewMode: true,
      userName: 'میهمان تست',
      csrf: '',
      progress: {},
      academyVersion: 'v2',
      contentVersion: '2026.11.24-p0',
    },
    FAMAcademyEngine: engine,
    addEventListener(type, listener) {
      if (!windowListeners.has(type)) windowListeners.set(type, []);
      windowListeners.get(type).push(listener);
    },
  };

  const localStorage = {
    getItem(key) { return localStorageMap.has(key) ? localStorageMap.get(key) : null; },
    setItem(key, value) { localStorageMap.set(key, String(value)); },
    removeItem(key) { localStorageMap.delete(key); },
    clear() { localStorageMap.clear(); },
  };

  function fakeResponse(data, status = 200) {
    return { ok: status >= 200 && status < 300, status, json: async () => data };
  }

  async function fetchImpl(url, init = {}) {
    if (API_BASE) {
      const options = {
        method: init.method || 'GET',
        headers: init.headers || {},
      };
      if (init.body !== undefined) options.body = init.body;
      return nativeFetch(new URL(url, API_BASE), options);
    }
    const path = new URL(url, 'http://preview.local').pathname;
    const method = init.method || 'GET';
    if (path === '/api/academy/v2/catalog') return fakeResponse(catalog);
    if (path === '/api/academy/v2/exercises') return fakeResponse(exercises);
    if (path === '/api/academy/v2/references') return fakeResponse(references);
    if (path === '/api/academy/v2/health') return fakeResponse({ ok: true, service: 'fixture', schemaVersion: 'fam-academy-v1' });
    if (path.startsWith('/api/academy/v2/lesson/')) {
      const id = decodeURIComponent(path.split('/').pop());
      return lessons.has(id) ? fakeResponse(lessons.get(id)) : fakeResponse({ error: 'not found' }, 404);
    }
    if (path.startsWith('/api/academy/v2/simulation/')) {
      const id = decodeURIComponent(path.split('/').pop());
      return simulations.has(id) ? fakeResponse(simulations.get(id)) : fakeResponse({ error: 'not found' }, 404);
    }
    if (path.startsWith('/api/academy/v2/lab/')) {
      const id = decodeURIComponent(path.split('/').pop());
      return labs.has(id) ? fakeResponse(labs.get(id)) : fakeResponse({ error: 'not found' }, 404);
    }
    if (path.startsWith('/api/academy/v2/quiz/') && method === 'POST') {
      const id = decodeURIComponent(path.split('/').pop());
      const body = JSON.parse(init.body || '{}');
      return lessons.has(id)
        ? fakeResponse(engine.evaluateQuiz(lessons.get(id), body.answers || []))
        : fakeResponse({ ok: false, error: 'lesson not found' }, 404);
    }
    if (path === '/api/academy/progress') return fakeResponse({ ok: true, preview: true, progress: {} });
    return fakeResponse({ error: 'not found' }, 404);
  }

  const sandbox = {
    window,
    document,
    location,
    localStorage,
    fetch: fetchImpl,
    console,
    setInterval,
    clearInterval,
    setTimeout,
    clearTimeout,
  };

  async function dispatchHashChange() {
    for (const listener of windowListeners.get('hashchange') || []) {
      await listener({ type: 'hashchange' });
    }
  }

  async function setHash(value) {
    location.hash = value;
    await dispatchHashChange();
  }

  async function click(dataset) {
    const event = {
      preventDefault() {},
      target: {
        closest(selector) {
          if (selector === '[data-route]' && dataset.route) return { dataset: { route: dataset.route } };
          if (selector === '[data-action]' && dataset.action) return { dataset: { ...dataset } };
          return null;
        },
      },
    };
    for (const listener of documentListeners.get('click') || []) {
      await listener(event);
    }
    if (dataset.route) await dispatchHashChange();
  }

  function getElementHtml(id) {
    return elements.has(id) ? elements.get(id)._html : '';
  }

  function getProgress() {
    const raw = localStorage.getItem('famAcademyV2.progress.v1');
    return raw ? JSON.parse(raw) : null;
  }

  function snapshot() {
    return { rootHtml, viewHtml, hash, locationHash: location.hash };
  }

  async function waitFor(predicate, label, timeoutMs = 4000) {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (predicate()) return;
      await new Promise((resolve) => setTimeout(resolve, 15));
    }
    const state = snapshot();
    throw new Error(`timeout waiting for ${label}; view length=${state.viewHtml.length}, hash=${state.hash}`);
  }

  return {
    sandbox,
    document,
    window,
    location,
    setHash,
    click,
    waitFor,
    snapshot,
    getElementHtml,
    getProgress,
    getElement(id) { return elements.has(id) ? elements.get(id) : null; },
    getLocalStorage() { return localStorage; },
    setParamOverride(id, value) { paramOverrides.set(id, value); },
    setCheckedAnswers(values) {
      checkedAnswers.clear();
      values.forEach((value, index) => checkedAnswers.set(index, value));
    },
  };
}

test('SPA presentation flow connects dashboard, paths, course, lesson, simulator, lab, quiz and progress', async () => {
  const dom = createHarness();
  const source = readFileSync(appPath, 'utf8');
  vm.runInNewContext(source, dom.sandbox, { filename: 'academy-v2.js' });

  await dom.waitFor(
    () => dom.snapshot().rootHtml.includes('topbar') && dom.snapshot().viewHtml.includes('یادگیری شبکه'),
    'dashboard mount',
  );
  assert.match(dom.snapshot().viewHtml, /۲۳ مسیر|23/);
  assert.match(dom.snapshot().viewHtml, /دورههای متصل و قابل ارائه/);
  assert.match(dom.snapshot().viewHtml, /شبیهسازهای تعاملی/);
  assert.match(dom.snapshot().rootHtml, /class="app-shell" id="academy-shell"/);
  assert.match(dom.snapshot().rootHtml, /class="sidebar" id="academy-sidebar"/);
  assert.match(dom.snapshot().rootHtml, /academy-section-head/);
  assert.match(dom.snapshot().rootHtml, /href="\/app"/);
  assert.match(dom.getElementHtml('academy-crumbs'), /داشبورد/);

  await dom.click({ action: 'toggle-theme' });
  assert.ok(['light', 'dark'].includes(dom.getLocalStorage().getItem('fam.academy.theme')));
  await dom.click({ action: 'toggle-menu' });
  assert.ok(dom.getElement('academy-shell').classList.contains('academy-menu-collapsed'));

  await dom.setHash('#/paths');
  await dom.waitFor(() => dom.snapshot().viewHtml.includes('معماری Curriculum'), 'paths view');
  assert.match(dom.snapshot().viewHtml, /PATH 23/);
  assert.match(dom.getElementHtml('academy-crumbs'), /مسیرها/);

  const liveCourse = catalog.courses.find((course) => course.status === 'live');
  await dom.setHash(`#/course/${liveCourse.id}`);
  await dom.waitFor(() => dom.snapshot().viewHtml.includes('فصلها و درسها'), 'course view');
  assert.ok(dom.snapshot().viewHtml.includes(liveCourse.title));

  const lessonId = catalog.lessons[0].id;
  const lesson = lessons.get(lessonId);
  await dom.setHash(`#/lesson/${lessonId}`);
  await dom.waitFor(() => dom.snapshot().viewHtml.includes('LESSON 01'), 'lesson view');
  assert.match(dom.snapshot().viewHtml, /توضیح مفهومی/);
  assert.match(dom.snapshot().viewHtml, /پیشرفت مرحلهای/);

  await dom.click({ action: 'lesson-stage', stage: '4' });
  await dom.waitFor(() => dom.snapshot().viewHtml.includes('شروع آزمون'), 'assessment lesson stage');

  const arpSim = catalog.simulations.find((sim) => sim.logic === 'arpResolve');
  await dom.setHash(`#/sim/${arpSim.id}`);
  await dom.waitFor(
    () => dom.snapshot().viewHtml.includes('INTERACTIVE SIMULATION') && dom.getElementHtml('sim-output').includes('Local delivery'),
    'initial ARP simulation',
  );
  assert.match(dom.getElementHtml('sim-output'), /Sample \/ Simulated/);
  assert.ok(dom.getProgress().simRuns[arpSim.id] >= 1);

  dom.setParamOverride('targetIp', '203.0.113.10');
  await dom.click({ action: 'sim-run' });
  await dom.waitFor(
    () => dom.getElementHtml('sim-output').includes('Remote delivery via gateway'),
    'parameter-sensitive ARP simulation',
  );
  assert.match(dom.getElementHtml('sim-output'), /Gateway/);

  const labId = catalog.labs[0].id;
  const lab = labs.get(labId);
  await dom.setHash(`#/lab/${labId}`);
  await dom.waitFor(
    () => dom.snapshot().viewHtml.includes('INTERNAL SIMULATOR') && dom.getElementHtml('lab-output').includes('ready'),
    'lab view',
  );
  assert.match(dom.snapshot().viewHtml, /Sample \/ Simulated/);
  assert.match(dom.snapshot().viewHtml, /real device connection|هیچ اتصال/);

  const firstStep = lab.steps[0].id;
  await dom.click({ action: 'lab-step', step: firstStep });
  await dom.waitFor(() => dom.getElementHtml('lab-output').includes('Expected:'), 'lab step execution');
  assert.ok(dom.getProgress().labSteps[labId].includes(firstStep));

  await dom.setHash(`#/quiz/${lessonId}`);
  await dom.waitFor(() => dom.snapshot().viewHtml.includes('ASSESSMENT'), 'quiz view');
  dom.setCheckedAnswers(lesson.quiz.map((q) => q.answerIndex));
  await dom.click({ action: 'quiz-submit' });
  await dom.waitFor(() => dom.getElementHtml('quiz-result').includes('100%'), 'quiz result');
  assert.match(dom.getElementHtml('quiz-result'), /قبول/);
  assert.match(dom.getElementHtml('quiz-result'), /پاسخ صحیح/);

  const progressAfterQuiz = dom.getProgress();
  assert.equal(progressAfterQuiz.quizScores[lessonId], 100);
  assert.ok(progressAfterQuiz.completedLessons.includes(lessonId));
  assert.equal(progressAfterQuiz.lastLessonId, lessonId);

  await dom.setHash('#/progress');
  await dom.waitFor(() => dom.snapshot().viewHtml.includes('پیشرفت من'), 'progress view');
  assert.match(dom.snapshot().viewHtml, /100%/);
  assert.ok(dom.snapshot().viewHtml.includes(lesson.title));
  assert.match(dom.snapshot().viewHtml, /famAcademyV2\.progress\.v1/);
});
