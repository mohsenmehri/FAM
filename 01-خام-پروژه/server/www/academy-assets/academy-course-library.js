(() => {
  'use strict';

  const CONTENT_ROOT = '/academy-content/';
  const CATALOG_URL = CONTENT_ROOT + 'catalog.json';
  const rootElement = () => document.getElementById('app-root');
  let catalogPromise = null;
  let routeSequence = 0;
  let activeFilter = 'all';
  let activeQuery = '';
  let currentCatalog = null;
  let documentsById = new Map();
  let diagramsByFile = new Map();

  const FILTERS = [
    ['all', 'همهٔ محتوا'],
    ['stage-zero', 'مرحلهٔ صفر'],
    ['ccna', 'درس‌های CCNA'],
    ['worksheets', 'کاربرگ‌ها'],
    ['diagrams', 'نمودارها'],
    ['references', 'مراجع']
  ];

  const GROUP_LABELS = {
    'stage-zero': 'مرحلهٔ صفر',
    fundamentals: 'بنیادهای شبکه',
    access: 'دسترسی شبکه',
    connectivity: 'اتصال IP',
    services: 'خدمات IP',
    security: 'مبانی امنیت',
    automation: 'اتوماسیون و برنامه‌پذیری',
    references: 'مرجع آموزشی'
  };

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function button(text, className, onClick) {
    const node = element('button', className || 'btn', text);
    node.type = 'button';
    node.addEventListener('click', onClick);
    return node;
  }

  function normalizeSearch(value) {
    return String(value || '').toLowerCase().replace(/[\s\u200c\u200f]+/g, ' ').trim();
  }

  async function loadCatalog() {
    if (!catalogPromise) {
      catalogPromise = fetch(CATALOG_URL, {
        credentials: 'same-origin',
        cache: 'no-store',
        headers: { Accept: 'application/json' }
      }).then(async response => {
        if (response.status === 401) throw new Error('نشست FAM معتبر نیست؛ دوباره وارد شوید.');
        if (!response.ok) throw new Error('دریافت فهرست محتوا ناموفق بود (' + response.status + ').');
        const value = await response.json();
        if (!value || value.schemaVersion !== '1.0' || !Array.isArray(value.documents) ||
            !Array.isArray(value.worksheets) || !Array.isArray(value.diagrams)) {
          throw new Error('ساختار فهرست محتوای آکادمی معتبر نیست.');
        }
        const safeId = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
        if (value.documents.some(item => !item || !safeId.test(item.id) || item.file !== item.id + '.md') ||
            value.diagrams.some(item => !item || !/^[a-z0-9]+(?:-[a-z0-9]+)*\.svg$/.test(item.file))) {
          throw new Error('شناسهٔ فایل در فهرست محتوا معتبر نیست.');
        }
        currentCatalog = value;
        documentsById = new Map(value.documents.map(item => [item.id, item]));
        diagramsByFile = new Map(value.diagrams.map(item => [item.file, item]));
        return value;
      }).catch(error => {
        catalogPromise = null;
        throw error;
      });
    }
    return catalogPromise;
  }

  function navigate(root, hash) {
    if (location.hash === hash) route(root);
    else location.hash = hash;
  }

  function documentHash(id, anchor) {
    const base = '#/course-library/doc/' + encodeURIComponent(id);
    return anchor ? base + '/section/' + encodeURIComponent(anchor) : base;
  }

  function makeDashboardHeader(index) {
    const header = element('header', 'fam-library-header');
    const copy = element('div', 'fam-library-heading');
    copy.append(
      element('div', 'fam-library-kicker', 'کتابخانهٔ محتوای FAM Academy'),
      element('h1', '', 'درس‌ها، کاربرگ‌ها و نمودارها'),
      element('p', 'fam-library-intro',
        'متن کامل درس‌ها در همین صفحه باز می‌شود. نمودارهای SVG، تمرین‌های داخل درس، کاربرگ‌های مستقل و مراجع نیز در فهرست جداگانه در دسترس‌اند.')
    );
    const stats = element('div', 'fam-library-stats');
    const counts = index.counts || {};
    [
      [counts.stageZeroLessons, 'درس مرحلهٔ صفر'],
      [counts.ccnaLessons, 'درس CCNA'],
      [counts.inventoryWorksheetTitles, 'عنوان کاربرگ در موجودی'],
      [counts.independentWorksheets, 'کاربرگ مستقل'],
      [counts.diagrams, 'نمودار SVG']
    ].forEach(([value, label]) => {
      const item = element('div', 'fam-library-stat');
      item.append(element('strong', '', value), element('span', '', label));
      stats.append(item);
    });
    copy.append(stats);
    const side = element('div', 'fam-library-header-actions');
    side.append(button('بازگشت به مسیرهای یادگیری', 'btn fam-library-back', () => navigate(root, '#/dashboard')));
    header.append(copy, side);
    return header;
  }

  function searchableText(item) {
    return normalizeSearch([item.title, item.code, item.categoryLabel, item.sectionTitle, item.groupLabel, item.kindLabel].filter(Boolean).join(' '));
  }

  function renderDocumentCards(target, items, root, query) {
    const filtered = items.filter(item => !query || searchableText(item).includes(query));
    if (!filtered.length) {
      target.append(element('p', 'fam-library-empty', 'موردی با این عبارت پیدا نشد.'));
      return;
    }
    const grid = element('div', 'fam-library-grid');
    filtered.forEach(item => {
      const card = button('', 'fam-library-card', () => navigate(root, documentHash(item.id)));
      card.setAttribute('aria-label', 'باز کردن ' + item.title);
      const meta = element('div', 'fam-library-card-meta');
      meta.append(element('span', 'fam-library-tag', item.code || GROUP_LABELS[item.category] || GROUP_LABELS[item.collection] || 'محتوا'));
      meta.append(element('span', 'fam-library-card-type', item.type === 'reference' ? 'مرجع' : 'درس'));
      card.append(meta, element('strong', 'fam-library-card-title', item.title));
      const description = item.groupLabel || GROUP_LABELS[item.category] || GROUP_LABELS[item.collection] || '';
      if (description) card.append(element('span', 'fam-library-card-subtitle', description));
      grid.append(card);
    });
    target.append(grid);
  }

  function renderWorksheetCards(target, index, root, query) {
    const items = index.worksheets.filter(item => !query || normalizeSearch(
      [item.title, item.sectionTitle, item.code, item.kind === 'embedded' ? 'داخل درس' : 'کاربرگ مستقل'].join(' ')
    ).includes(query));
    if (!items.length) {
      target.append(element('p', 'fam-library-empty', 'کاربرگی با این عبارت پیدا نشد.'));
      return;
    }
    target.append(element('p', 'fam-library-note',
      '۲۷ عنوان از موجودی کاربرگ‌ها، همراه با ۲ سند مستقل. این شمارش به معنی ۲۷ کاربرگ مستقل یا اجرای تأییدشده نیست؛ بخش‌های درسی داخل متن کامل همان درس باز می‌شوند.'));
    const grid = element('div', 'fam-library-grid');
    items.forEach(item => {
      const card = button('', 'fam-library-card', () => navigate(root, documentHash(item.docId, item.anchor)));
      card.setAttribute('aria-label', 'باز کردن ' + item.title);
      card.append(
        element('div', 'fam-library-card-meta', ''),
        element('strong', 'fam-library-card-title', item.title),
        element('span', 'fam-library-card-subtitle', item.kind === 'embedded' ? item.sectionTitle : 'سند مستقل · ' + item.sectionTitle)
      );
      const code = item.code ? element('span', 'fam-library-tag', item.code) : null;
      if (code) card.querySelector('.fam-library-card-meta').append(code);
      grid.append(card);
    });
    target.append(grid);
  }

  function renderDiagramCards(target, index, root, query) {
    const items = index.diagrams.filter(item => !query || normalizeSearch([item.title, item.alt, item.file, item.lessonTitle].join(' ')).includes(query));
    if (!items.length) {
      target.append(element('p', 'fam-library-empty', 'نموداری با این عبارت پیدا نشد.'));
      return;
    }
    const grid = element('div', 'fam-library-diagram-grid');
    items.forEach(item => {
      const card = element('article', 'fam-library-diagram-card');
      const image = element('img', 'fam-library-diagram-image');
      image.src = CONTENT_ROOT + 'images/' + encodeURIComponent(item.file);
      image.alt = item.alt || item.title;
      image.loading = 'lazy';
      image.decoding = 'async';
      const caption = element('div', 'fam-library-diagram-caption');
      caption.append(element('strong', '', item.title || item.alt || item.file));
      if (item.lessonTitle) caption.append(element('small', '', item.lessonTitle));
      if (item.docId && documentsById.has(item.docId)) {
        caption.append(button('باز کردن درس', 'fam-library-inline-link', () => navigate(root, documentHash(item.docId))));
      }
      card.append(image, caption);
      grid.append(card);
    });
    target.append(grid);
  }

  function renderResults(target, index, root, filter, query) {
    target.replaceChildren();
    if (filter === 'worksheets') {
      renderWorksheetCards(target, index, root, query);
      return;
    }
    if (filter === 'diagrams') {
      renderDiagramCards(target, index, root, query);
      return;
    }
    let documents = index.documents;
    if (filter === 'stage-zero') documents = documents.filter(item => item.collection === 'stage-zero');
    else if (filter === 'ccna') documents = documents.filter(item => item.collection === 'ccna');
    else if (filter === 'references') documents = documents.filter(item => item.collection === 'references');
    renderDocumentCards(target, documents, root, query);
  }

  function renderDashboard(root, index, sequence) {
    const page = element('section', 'fam-library fam-library-dashboard');
    page.append(makeDashboardHeader(index));
    const controls = element('div', 'fam-library-controls');
    const tabs = element('div', 'fam-library-tabs');
    tabs.setAttribute('role', 'tablist');
    const results = element('div', 'fam-library-results');
    const searchLabel = element('label', 'fam-library-search');
    searchLabel.append(element('span', '', 'جست‌وجو در عنوان و شناسه'));
    const search = element('input', '');
    search.type = 'search';
    search.autocomplete = 'off';
    search.placeholder = 'برای نمونه: OSPF، VLAN، NF-10…';
    search.value = activeQuery;
    search.setAttribute('aria-label', 'جست‌وجو در عنوان و شناسهٔ محتوا');
    searchLabel.append(search);
    controls.append(tabs, searchLabel);
    page.append(controls, results);
    root.replaceChildren(page);

    FILTERS.forEach(([id, title]) => {
      const tab = button(title, 'fam-library-tab', () => {
        activeFilter = id;
        updateTabs();
        renderResults(results, index, root, activeFilter, normalizeSearch(activeQuery));
      });
      tab.dataset.libraryFilter = id;
      tab.setAttribute('role', 'tab');
      tabs.append(tab);
    });
    function updateTabs() {
      tabs.querySelectorAll('[data-library-filter]').forEach(tab => {
        const selected = tab.dataset.libraryFilter === activeFilter;
        tab.setAttribute('aria-selected', String(selected));
        tab.classList.toggle('active', selected);
      });
    }
    search.addEventListener('input', () => {
      activeQuery = search.value;
      renderResults(results, index, root, activeFilter, normalizeSearch(activeQuery));
    });
    updateTabs();
    renderResults(results, index, root, activeFilter, normalizeSearch(activeQuery));
    if (sequence !== routeSequence) return;
  }

  function appendSafeLink(parent, label, href, index, sourceDocument) {
    const raw = String(href || '').trim();
    const local = /^(?:\.\/)?([a-z0-9]+(?:-[a-z0-9]+)*)\.md(?:#[^\s]*)?$/.exec(raw);
    if (local && documentsById.has(local[1])) {
      const link = element('a', '', '');
      appendInline(link, label, index, sourceDocument, 0);
      link.href = documentHash(local[1]);
      link.addEventListener('click', event => {
        event.preventDefault();
        navigate(rootElement(), documentHash(local[1]));
      });
      parent.append(link);
      return;
    }
    let parsed;
    try { parsed = new URL(raw); } catch (_) { parent.append(document.createTextNode(label)); return; }
    if (parsed.protocol !== 'https:' || parsed.username || parsed.password) {
      parent.append(document.createTextNode(label));
      return;
    }
    const link = element('a', '', '');
    appendInline(link, label, index, sourceDocument, 0);
    link.href = parsed.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    parent.append(link);
  }

  const INLINE_TOKEN = /(`+[^`\n]+?`+|!\[[^\]\n]*\]\([^)\n]+\)|\[[^\]\n]+\]\([^)\n]+\)|\*\*.+?\*\*|__.+?__|~~.+?~~|\*[^*\n]+\*|_[^_\n]+_)/g;

  function appendInline(parent, value, index, sourceDocument, depth) {
    const text = String(value || '');
    if (depth > 4) {
      parent.append(document.createTextNode(text));
      return;
    }
    let cursor = 0;
    for (const match of text.matchAll(INLINE_TOKEN)) {
      if (match.index > cursor) parent.append(document.createTextNode(text.slice(cursor, match.index)));
      const token = match[0];
      if (token[0] === '`') {
        const ticks = /^`+/.exec(token)[0].length;
        const code = element('code', 'fam-course-inline-code', token.slice(ticks, token.length - ticks));
        parent.append(code);
      } else if (token.startsWith('![')) {
        const imageMatch = /^!\[([^\]]*)\]\(([^)]+)\)$/.exec(token);
        if (imageMatch) {
          const path = imageMatch[2].trim().replace(/^\.\//, '');
          const imagePath = /^academy-images\/([a-z0-9]+(?:-[a-z0-9]+)*)\.svg$/.exec(path);
          if (imagePath && diagramsByFile.has(imagePath[1] + '.svg')) {
            const image = element('img', 'fam-course-inline-image');
            image.src = CONTENT_ROOT + 'images/' + encodeURIComponent(imagePath[1] + '.svg');
            image.alt = imageMatch[1];
            image.loading = 'lazy';
            image.decoding = 'async';
            parent.append(image);
          } else {
            parent.append(document.createTextNode(token));
          }
        } else parent.append(document.createTextNode(token));
      } else if (token[0] === '[') {
        const linkMatch = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(token);
        if (linkMatch) appendSafeLink(parent, linkMatch[1], linkMatch[2], index, sourceDocument);
        else parent.append(document.createTextNode(token));
      } else {
        let tag = 'em';
        let inner = token.slice(1, -1);
        if (token.startsWith('**') || token.startsWith('__')) {
          tag = 'strong';
          inner = token.slice(2, -2);
        } else if (token.startsWith('~~')) {
          tag = 'del';
          inner = token.slice(2, -2);
        }
        const wrapper = element(tag, '');
        appendInline(wrapper, inner, index, sourceDocument, depth + 1);
        parent.append(wrapper);
      }
      cursor = match.index + token.length;
    }
    if (cursor < text.length) parent.append(document.createTextNode(text.slice(cursor)));
  }

  function fenceStart(line) {
    return /^ {0,3}(`{3,}|~{3,})(.*)$/.exec(line);
  }

  function headingMatch(line) {
    return /^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$/.exec(line);
  }

  function listMatch(line) {
    const match = /^( *)([-+*]|\d+[.)])\s+(.*)$/.exec(line);
    if (!match) return null;
    return { indent: match[1].length, marker: match[2], text: match[3], ordered: /^\d/.test(match[2]) };
  }

  function isEscaped(text, position) {
    let count = 0;
    for (let cursor = position - 1; cursor >= 0 && text.charCodeAt(cursor) === 92; cursor -= 1) count += 1;
    return count % 2 === 1;
  }

  function splitTableRow(line) {
    let raw = line.trim();
    if (raw.startsWith('|')) raw = raw.slice(1);
    if (raw.endsWith('|') && !isEscaped(raw, raw.length - 1)) raw = raw.slice(0, -1);
    const cells = [];
    let cell = '';
    let codeTicks = 0;
    let escaped = false;
    for (let i = 0; i < raw.length; i += 1) {
      const char = raw[i];
      if (escaped) {
        cell += char;
        escaped = false;
      } else if (char.charCodeAt(0) === 92) {
        cell += char;
        escaped = true;
      } else if (char === '`') {
        let end = i + 1;
        while (raw[end] === '`') end += 1;
        const count = end - i;
        codeTicks = codeTicks === 0 ? count : (codeTicks === count ? 0 : codeTicks);
        cell += raw.slice(i, end);
        i = end - 1;
      } else if (char === '|' && codeTicks === 0) {
        cells.push(cell.trim());
        cell = '';
      } else {
        cell += char;
      }
    }
    cells.push(cell.trim());
    return cells;
  }

  function isTableDivider(line, headerCells) {
    if (!line.includes('|')) return false;
    const cells = splitTableRow(line);
    return cells.length === headerCells && cells.every(cell => /^:?-{3,}:?$/.test(cell));
  }

  function renderList(parent, lines, start, index, sourceDocument) {
    const first = listMatch(lines[start]);
    const list = element(first.ordered ? 'ol' : 'ul', 'fam-course-list');
    const baseIndent = first.indent;
    let cursor = start;
    let lastItem = null;
    while (cursor < lines.length) {
      const item = listMatch(lines[cursor]);
      if (!item || item.indent < baseIndent) break;
      if (item.indent > baseIndent) {
        if (!lastItem) break;
        const nested = renderList(lastItem, lines, cursor, index, sourceDocument);
        if (nested.next <= cursor) break;
        cursor = nested.next;
        continue;
      }
      if (item.ordered !== first.ordered) break;
      lastItem = element('li', '');
      appendInline(lastItem, item.text, index, sourceDocument, 0);
      list.append(lastItem);
      cursor += 1;
      while (cursor < lines.length) {
        if (!lines[cursor].trim()) {
          const nextList = cursor + 1 < lines.length ? listMatch(lines[cursor + 1]) : null;
          if (nextList && nextList.indent >= baseIndent) {
            cursor += 1;
            break;
          }
          return { node: list, next: cursor + 1 };
        }
        const continuation = listMatch(lines[cursor]);
        if (continuation) break;
        const indent = /^ */.exec(lines[cursor])[0].length;
        if (indent <= baseIndent || isBlockStart(lines, cursor)) break;
        const paragraph = element('span', 'fam-course-list-continuation');
        appendInline(paragraph, lines[cursor].trim(), index, sourceDocument, 0);
        lastItem.append(document.createTextNode(' '), paragraph);
        cursor += 1;
      }
    }
    return { node: list, next: cursor };
  }

  function isBlockStart(lines, cursor) {
    const line = lines[cursor] || '';
    return !line.trim() || Boolean(fenceStart(line)) || Boolean(headingMatch(line)) ||
      /^ {0,3}(?:[-*_])(?:\s*[-*_]){2,}\s*$/.test(line) || /^ {0,3}>/.test(line) || Boolean(listMatch(line));
  }

  function isClosingFence(line, marker, minimumLength) {
    let spaces = 0;
    while (line[spaces] === ' ') spaces += 1;
    if (spaces > 3) return false;
    let count = 0;
    while (line[spaces + count] === marker) count += 1;
    return count >= minimumLength && line.slice(spaces + count).trim() === '';
  }

  function renderMarkdown(container, markdown, index, sourceDocument) {
    const lines = String(markdown || '').replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n').split('\n');
    const state = { heading: 0 };
    let cursor = 0;
    while (cursor < lines.length) {
      const line = lines[cursor];
      if (!line.trim()) { cursor += 1; continue; }
      const fence = fenceStart(line);
      if (fence) {
        const marker = fence[1][0];
        const markerLength = fence[1].length;
        let end = cursor + 1;
        const codeLines = [];
        for (; end < lines.length; end += 1) {
          if (isClosingFence(lines[end], marker, markerLength)) break;
          codeLines.push(lines[end]);
        }
        const pre = element('pre', 'fam-course-code');
        const code = element('code', '');
        code.textContent = codeLines.join('\n');
        pre.append(code);
        container.append(pre);
        cursor = end < lines.length ? end + 1 : end;
        continue;
      }
      const heading = headingMatch(line);
      if (heading) {
        const level = heading[1].length;
        const headingNode = element('h' + level, 'fam-course-heading');
        state.heading += 1;
        headingNode.id = 'heading-' + state.heading;
        appendInline(headingNode, heading[2], index, sourceDocument, 0);
        container.append(headingNode);
        cursor += 1;
        continue;
      }
      if (/^ {0,3}(?:[-*_])(?:\s*[-*_]){2,}\s*$/.test(line)) {
        container.append(element('hr', 'fam-course-rule'));
        cursor += 1;
        continue;
      }
      if (/^ {0,3}>/.test(line)) {
        const quoted = [];
        while (cursor < lines.length && /^ {0,3}>/.test(lines[cursor])) {
          quoted.push(lines[cursor].replace(/^ {0,3}> ?/, ''));
          cursor += 1;
        }
        const quote = element('blockquote', 'fam-course-quote');
        renderMarkdown(quote, quoted.join('\n'), index, sourceDocument);
        container.append(quote);
        continue;
      }
      const list = listMatch(line);
      if (list) {
        const rendered = renderList(container, lines, cursor, index, sourceDocument);
        container.append(rendered.node);
        cursor = rendered.next > cursor ? rendered.next : cursor + 1;
        continue;
      }
      if (line.includes('|') && cursor + 1 < lines.length) {
        const headers = splitTableRow(line);
        if (isTableDivider(lines[cursor + 1], headers)) {
          const wrapper = element('div', 'fam-course-table-wrap');
          const table = element('table', 'fam-course-table');
          const thead = element('thead', '');
          const headerRow = element('tr', '');
          headers.forEach(value => {
            const cell = element('th', '');
            cell.scope = 'col';
            appendInline(cell, value, index, sourceDocument, 0);
            headerRow.append(cell);
          });
          thead.append(headerRow);
          table.append(thead);
          const tbody = element('tbody', '');
          cursor += 2;
          while (cursor < lines.length && lines[cursor].includes('|') && lines[cursor].trim()) {
            const values = splitTableRow(lines[cursor]);
            const row = element('tr', '');
            for (let column = 0; column < headers.length; column += 1) {
              const cell = element('td', '');
              appendInline(cell, values[column] || '', index, sourceDocument, 0);
              row.append(cell);
            }
            tbody.append(row);
            cursor += 1;
          }
          table.append(tbody);
          wrapper.append(table);
          container.append(wrapper);
          continue;
        }
      }
      const paragraphLines = [];
      while (cursor < lines.length && !isBlockStart(lines, cursor)) {
        if (lines[cursor].includes('|') && cursor + 1 < lines.length) {
          const headerCells = splitTableRow(lines[cursor]);
          if (isTableDivider(lines[cursor + 1], headerCells)) break;
        }
        paragraphLines.push(lines[cursor].trim());
        cursor += 1;
      }
      if (!paragraphLines.length) {
        paragraphLines.push(lines[cursor]);
        cursor += 1;
      }
      const paragraph = element('p', 'fam-course-paragraph');
      appendInline(paragraph, paragraphLines.join(' '), index, sourceDocument, 0);
      container.append(paragraph);
    }
  }

  async function renderDocument(root, index, id, anchor, sequence) {
    const item = documentsById.get(id);
    const page = element('section', 'fam-library fam-library-document');
    const header = element('header', 'fam-library-document-header');
    header.append(
      button('بازگشت به فهرست', 'btn fam-library-back', () => navigate(root, '#/course-library')),
      element('div', 'fam-library-kicker', GROUP_LABELS[item?.category] || GROUP_LABELS[item?.collection] || 'محتوای دوره'),
      element('h1', '', item?.title || 'درس')
    );
    if (item?.code) header.append(element('p', 'fam-library-document-code', item.code));
    page.append(header);
    const article = element('article', 'fam-course-markdown');
    article.setAttribute('aria-label', item?.title || 'محتوای درس');
    article.append(element('p', 'fam-library-loading', 'در حال بارگذاری متن کامل…'));
    page.append(article);
    root.replaceChildren(page);

    if (!item) {
      article.replaceChildren(element('p', 'fam-library-error', 'این سند در فهرست مجاز محتوا نیست.'));
      return;
    }
    try {
      const response = await fetch(CONTENT_ROOT + encodeURIComponent(item.file), {
        credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'text/markdown' }
      });
      if (sequence !== routeSequence) return;
      if (response.status === 401) throw new Error('نشست FAM معتبر نیست؛ دوباره وارد شوید.');
      if (!response.ok) throw new Error('دریافت سند ناموفق بود (' + response.status + ').');
      const markdown = await response.text();
      if (sequence !== routeSequence) return;
      article.replaceChildren();
      renderMarkdown(article, markdown, index, item);
      if (anchor) requestAnimationFrame(() => document.getElementById(anchor)?.scrollIntoView({ block: 'start', behavior: 'smooth' }));
    } catch (error) {
      if (sequence !== routeSequence) return;
      article.replaceChildren(element('p', 'fam-library-error', String(error.message || error)));
    }
  }

  async function route(root) {
    if (!root) return;
    const sequence = ++routeSequence;
    root.replaceChildren(element('p', 'fam-library-loading', 'در حال آماده‌سازی محتوای دوره…'));
    try {
      const index = await loadCatalog();
      if (sequence !== routeSequence) return;
      const match = /^#\/course-library\/doc\/([a-z0-9]+(?:-[a-z0-9]+)*)(?:\/section\/(heading-\d+))?$/.exec(location.hash);
      if (match) {
        await renderDocument(root, index, decodeURIComponent(match[1]), match[2] || '', sequence);
        return;
      }
      if (location.hash !== '#/course-library') {
        if (location.hash.startsWith('#/course-library')) {
          root.replaceChildren(element('p', 'fam-library-error', 'نشانی این بخش از کتابخانه معتبر نیست.'));
          return;
        }
        return;
      }
      renderDashboard(root, index, sequence);
    } catch (error) {
      if (sequence !== routeSequence) return;
      const page = element('section', 'fam-library fam-library-error-page');
      page.append(
        element('h1', '', 'کتابخانهٔ محتوا بارگذاری نشد'),
        element('p', 'fam-library-error', String(error.message || error)),
        button('بازگشت به مسیرهای یادگیری', 'btn fam-library-back', () => navigate(root, '#/dashboard'))
      );
      root.replaceChildren(page);
    }
  }

  function open(root) {
    const current = root || rootElement();
    if (location.hash === '#/course-library') route(current);
    else location.hash = '#/course-library';
  }

  window.FamCourseLibrary = Object.freeze({ open, route });
})();
