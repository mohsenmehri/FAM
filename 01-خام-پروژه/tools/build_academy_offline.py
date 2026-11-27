#!/usr/bin/env python3
"""Build a standalone offline preview of the currently served curriculum.

The offline state is deliberately separate from the authenticated server.
No old 114-lesson data or remote equipment access is implied.
"""
import base64
import json
import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parent
ASSETS = PACKAGE / 'server' / 'www' / 'academy-assets'
PAGE = PACKAGE / 'server' / 'private_ui' / 'academy.html'
OUTPUT = REPO / 'FAM-Academy-Offline.html'


def safe_js_json(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':')).replace('<', r'\u003c').replace('>', r'\u003e').replace('&', r'\u0026')


def build():
    catalog = json.loads((ASSETS / 'curriculum-catalog.json').read_text(encoding='utf-8'))
    records = [lesson for path in catalog['paths'] for course in path['courses'] for lesson in course['lessons']]
    resources = {'/academy-assets/curriculum-catalog.json': catalog}
    for lesson in records:
        ref = lesson['blueprint']
        if not ref.startswith('/academy-assets/'):
            raise ValueError(f'unsafe blueprint path: {ref}')
        path = (ASSETS / ref.removeprefix('/academy-assets/')).resolve()
        if ASSETS.resolve() not in path.parents:
            raise ValueError(f'unsafe blueprint path: {ref}')
        resources[ref] = json.loads(path.read_text(encoding='utf-8'))
    page = PAGE.read_text(encoding='utf-8')
    assert page.count('__FAM_ACADEMY_BOOTSTRAP__') == 1
    page = page.replace('__FAM_ACADEMY_BOOTSTRAP__', "(() => { try { return { userName: 'آفلاین', progress: { 'fam4.learn.v1': localStorage.getItem('fam.academy.offline.v2') || '{}' } }; } catch (_) { return {userName:'آفلاین', progress:{}}; } })()")
    page = page.replace(' nonce="__FAM_CSP_NONCE__"', '')
    hook = '''
<script>
(() => {
  'use strict';
  const resources = __RESOURCES__;
  // Block all unbundled fetches rather than silently accessing the network.
  window.fetch = async input => {
    let url;
    try { url = new URL(typeof input === 'string' ? input : input.url, location.href); }
    catch (_) { return new Response('', {status:404}); }
    const data = resources[url.pathname];
    if (!data) return new Response('', {status:404});
    return new Response(JSON.stringify(data), {status:200, headers:{'Content-Type':'application/json'}});
  };
  const bridge = window.FamAcademyBridge;
  bridge.saveProgress = async function(payload) {
    const node = document.getElementById('academy-save-status');
    try {
      localStorage.setItem('fam.academy.offline.v2', JSON.stringify(payload));
      this.progress = JSON.parse(JSON.stringify(payload));
      if (node) node.textContent = 'پیشرفت در همین مرورگر ذخیره شد؛ با حساب آنلاین همگام نیست.';
      return true;
    } catch (_) {
      if (node) node.textContent = 'ذخیره آفلاین انجام نشد؛ دسترسی localStorage را بررسی کنید.';
      return false;
    }
  };
})();
</script>
'''.replace('__RESOURCES__', safe_js_json(resources))
    # Insert immediately after the existing bootstrap/bridge script.
    marker = '  </script>\n  <style'
    if page.count(marker) != 1:
        raise ValueError('bridge script marker changed')
    page = page.replace(marker, '  </script>\n' + hook + '  <style', 1)
    css_path = ASSETS / 'academy-reference-ui.css'
    css = css_path.read_text(encoding='utf-8')
    image = base64.b64encode((ASSETS / 'learning-journey.jpg').read_bytes()).decode('ascii')
    css = css.replace('/academy-assets/learning-journey.jpg', 'data:image/jpeg;base64,' + image)
    if re.search(r'</style', css, flags=re.I):
        raise ValueError('unsafe inline CSS')
    page, count = re.subn(r'<link rel="stylesheet" href="/academy-assets/academy-reference-ui\.css\?[^\"]+">', lambda _: '<style>' + css + '</style>', page)
    if count != 1:
        raise ValueError('stylesheet marker changed')
    pattern = re.compile(r'<script src="/academy-assets/([a-z0-9-]+\.js)(?:\?[^\"]*)?"></script>')
    def inline_js(match):
        source = (ASSETS / match.group(1)).read_text(encoding='utf-8')
        if re.search(r'</script', source, flags=re.I):
            raise ValueError('unsafe inline JavaScript')
        return '<script>\n' + source + '\n</script>'
    page, count = pattern.subn(inline_js, page)
    if count != 4:
        raise ValueError(f'expected four JS assets, got {count}')
    page = page.replace('href="/app"', 'href="#/dashboard"')
    banner = (f'<div role="note" style="padding:12px;background:#fff7ed;color:#7c2d12;text-align:center">'
              f'پیش‌نمایش آفلاین: فقط {len(records)} درس موجودِ نسخه فعلی؛ دوره ۱۱۴ درسی کامل نیست. '
              'پیشرفت فقط در همین مرورگر ذخیره می‌شود و با حساب آنلاین همگام نیست. '
              'محتوا در انتظار بازبینی است؛ اتصال به تجهیزات واقعی وجود ندارد.</div>')
    if page.count('<body>') != 1:
        raise ValueError('body marker changed')
    page = page.replace('<body>', '<body>\n' + banner, 1)
    return page


if __name__ == '__main__':
    OUTPUT.write_text(build(), encoding='utf-8')
    print(f'Built {OUTPUT}')
