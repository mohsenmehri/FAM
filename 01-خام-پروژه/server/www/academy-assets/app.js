/* FAM Cisco Academy — Comprehensive Curriculum Engine (vanilla JS, CSP-safe, FAM session synced) */
(function () {
  'use strict';

  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const FA = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const toFa = (n) => String(n).replace(/\d/g, d => FA[+d]);

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  /* ---------- هماهنگی با نشست و ذخیره سرور FAM ---------- */
  const boot = window.FAM_ACADEMY_BOOTSTRAP || {};
  const csrf = boot.csrf || '';
  const stored = boot.progress || {};

  function loadState() {
    const def = {
      activeLesson: 's01',
      completedLessons: [],
      quizScores: {},
      notes: {},
      missions: [],
      examScore: null,
      cliMode: 'user'
    };
    try {
      if (typeof stored['fam4.learn.v1'] === 'string') {
        const parsed = JSON.parse(stored['fam4.learn.v1']);
        if (parsed && typeof parsed === 'object') return Object.assign(def, parsed);
      }
    } catch (_) {}
    try {
      if (typeof stored['fam3.progress.v1'] === 'string') {
        const p3 = JSON.parse(stored['fam3.progress.v1']);
        if (p3 && Array.isArray(p3.missions)) def.missions = p3.missions;
      }
    } catch (_) {}
    return def;
  }

  const state = loadState();
  let saveTimer = null;

  function persistState() {
    if (!csrf) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(async () => {
      try {
        await fetch('/api/academy/progress', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', 'X-FAM-CSRF': csrf },
          body: JSON.stringify({
            changes: {
              'fam4.learn.v1': JSON.stringify({
                activeLesson: state.activeLesson,
                completedLessons: state.completedLessons,
                quizScores: state.quizScores,
                notes: state.notes,
                missions: state.missions,
                examScore: state.examScore
              }),
              'fam3.progress.v1': JSON.stringify({ missions: state.missions })
            }
          })
        });
      } catch (_) {}
    }, 180);
  }

  /* ---------- پروفایل و دسترسی پنل FAM ---------- */
  const avatarEl = $('.avatar');
  if (avatarEl && boot.userName) {
    avatarEl.title = boot.userName;
    const fc = String(boot.userName).trim().charAt(0);
    if (fc) avatarEl.textContent = fc;
  }
  const canPortal = !boot.allowedViews || boot.allowedViews.panel || boot.allowedViews.equipment;
  $$('[data-fam-portal]').forEach(node => {
    if (!canPortal) node.style.display = 'none';
  });

  /* ---------- منوی موبایل صفحه عمومی ---------- */
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

  /* ---------- انیمیشن reveal و شمارنده‌ها ---------- */
  const reveals = $$('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.1 });
    reveals.forEach(x => io.observe(x));
  } else {
    reveals.forEach(x => x.classList.add('in'));
  }

  const counters = $$('[data-count]');
  const runCounter = node => {
    const target = +node.dataset.count;
    const suffix = node.dataset.suffix || '';
    const t0 = performance.now();
    const tick = now => {
      const p = Math.min((now - t0) / 1400, 1);
      const val = Math.round(target * (1 - Math.pow(1 - p, 3)));
      node.textContent = toFa(val.toLocaleString('en-US')) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if (counters.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) { runCounter(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach(x => io.observe(x));
  } else {
    counters.forEach(runCounter);
  }

  /* ---------- تایپ زنده ترمینال هیرو ---------- */
  const typeTarget = $('#typeTarget');
  if (typeTarget) {
    const lines = [
      'R1> enable',
      'R1# show ip interface brief',
      'Gi0/0  10.10.0.1  YES manual up  up',
      'R1# show ip route',
      'O  10.255.0.2/32 [110/2] via 10.10.0.2 (ECMP)',
      'R1# show arp',
      '10.10.0.2  aabb.cc00.0200  ARPA  Gi0/0',
      'R1# write memory  [OK]'
    ];
    let li = 0, ci = 0, out = '';
    const step = () => {
      if (li >= lines.length) {
        setTimeout(() => { out = ''; li = 0; ci = 0; typeTarget.textContent = ''; step(); }, 3200);
        return;
      }
      const line = lines[li];
      if (ci <= line.length) {
        typeTarget.textContent = out + line.slice(0, ci);
        ci++;
        setTimeout(step, line[ci - 1] === ' ' ? 14 : 24);
      } else {
        out += line + '\n';
        li++; ci = 0;
        setTimeout(step, 400);
      }
    };
    setTimeout(step, 600);
  }

  /* ---------- بارگذاری داده‌های جامع آکادمی ---------- */
  let ACADEMY = null;

  async function loadAcademyData() {
    try {
      const res = await fetch('/academy-assets/academy-data.json', { credentials: 'same-origin' });
      if (!res.ok) return null;
      ACADEMY = await res.json();
      return ACADEMY;
    } catch (_) {
      return null;
    }
  }

  /* ---------- ساخت دیاگرام SVG تمیز و خوانا برای هر درس ---------- */
  function buildDiagramSvg(type) {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 720 260');
    svg.setAttribute('role', 'img');

    function rect(x, y, w, h, stroke, fill) {
      const r = document.createElementNS(ns, 'rect');
      r.setAttribute('x', x); r.setAttribute('y', y);
      r.setAttribute('width', w); r.setAttribute('height', h);
      r.setAttribute('rx', '10'); r.setAttribute('fill', fill || '#0e1729');
      r.setAttribute('stroke', stroke); r.setAttribute('stroke-width', '2');
      svg.appendChild(r);
    }
    function txt(x, y, str, color, size, anchor) {
      const t = document.createElementNS(ns, 'text');
      t.setAttribute('x', x); t.setAttribute('y', y);
      t.setAttribute('fill', color || '#f8fafc');
      t.setAttribute('font-size', size || '13');
      t.setAttribute('font-weight', '700');
      t.setAttribute('text-anchor', anchor || 'middle');
      t.textContent = str;
      svg.appendChild(t);
    }
    function line(x1, y1, x2, y2, stroke) {
      const l = document.createElementNS(ns, 'line');
      l.setAttribute('x1', x1); l.setAttribute('y1', y1);
      l.setAttribute('x2', x2); l.setAttribute('y2', y2);
      l.setAttribute('stroke', stroke || '#38bdf8');
      l.setAttribute('stroke-width', '2');
      svg.appendChild(l);
    }

    if (type === 'osi') {
      const layers = [
        ['L7-5 · Application (Data)', '#a78bfa'],
        ['L4 · Transport (TCP/UDP Segment)', '#3b82f6'],
        ['L3 · Network (IP Packet)', '#00d4ff'],
        ['L2 · Data Link (Ethernet Frame + MAC)', '#34d399'],
        ['L1 · Physical (Bits / Fiber / Copper)', '#fbbf24']
      ];
      layers.forEach((L, idx) => {
        const y = 16 + idx * 46;
        rect(40, y, 310, 38, L[1], '#0d1628');
        txt(195, y + 23, L[0], '#f1f5f9', '12.5');
      });
      rect(400, 38, 280, 184, '#00d4ff', '#0b1424');
      txt(540, 66, 'Encapsulation Flow', '#7df9ff', '14');
      txt(540, 102, '[ Data ]', '#a78bfa', '12.5');
      txt(540, 134, '[ TCP | Data ]  -> Segment', '#60a5fa', '12.5');
      txt(540, 166, '[ IP | TCP | Data ]  -> Packet', '#00d4ff', '12.5');
      txt(540, 198, '[ MAC | IP | TCP | Data | FCS ]', '#34d399', '12');
      line(350, 80, 400, 120, '#00d4ff');
      line(350, 175, 400, 190, '#34d399');
    } else if (type === 'leafspine') {
      rect(180, 22, 130, 46, '#00d4ff', '#10203a'); txt(245, 50, 'SPINE-1', '#7df9ff', '13.5');
      rect(410, 22, 130, 46, '#00d4ff', '#10203a'); txt(475, 50, 'SPINE-2', '#7df9ff', '13.5');
      const leaves = [90, 285, 480];
      leaves.forEach((lx, i) => {
        rect(lx, 122, 130, 44, '#3b82f6', '#0e192e');
        txt(lx + 65, 149, 'LEAF-' + (i + 1) + ' (VTEP)', '#93c5fd', '12.5');
        line(lx + 45, 122, 245, 68, '#00d4ff');
        line(lx + 85, 122, 475, 68, '#38bdf8');
        rect(lx + 15, 200, 100, 38, '#34d399', '#0b1b21');
        txt(lx + 65, 224, 'SRV-' + (i + 1), '#6ee7b7', '12');
        line(lx + 65, 166, lx + 65, 200, '#34d399');
      });
      txt(360, 100, 'L3 IP Fabric (ECMP) + VXLAN EVPN Overlay', '#fbbf24', '12');
    } else {
      rect(290, 20, 140, 48, '#00d4ff', '#10203a'); txt(360, 49, 'R1 · CORE / GW', '#7df9ff', '13');
      rect(110, 118, 140, 46, '#3b82f6', '#0e192e'); txt(180, 146, 'SW1 · ACCESS', '#93c5fd', '12.5');
      rect(470, 118, 140, 46, '#3b82f6', '#0e192e'); txt(540, 146, 'SW2 · SERVERS', '#93c5fd', '12.5');
      line(330, 68, 180, 118, '#00d4ff');
      line(390, 68, 540, 118, '#00d4ff');
      line(250, 141, 470, 141, '#fbbf24');
      txt(360, 133, '802.1Q Trunk (VLAN 10, 20)', '#fde68a', '11');
      rect(95, 198, 170, 40, '#a78bfa', '#14132b'); txt(180, 223, 'PC-A · 10.10.0.10/24', '#ddd6fe', '12');
      rect(455, 198, 170, 40, '#34d399', '#0b1b21'); txt(540, 223, 'SRV · 10.20.0.10/26', '#6ee7b7', '12');
      line(180, 164, 180, 198, '#a78bfa');
      line(540, 164, 540, 198, '#34d399');
    }
    return svg;
  }

  /* ---------- شبیه‌ساز CLI آکادمی (وضعیت‌دار برای تمرین‌های پایه و VLAN/Interface) ---------- */
  function createInitialSim() {
    return {
      mode: 'user', // 'user' | 'priv' | 'config' | 'if' | 'vlan'
      activeIf: null,
      activeVlan: null,
      vlans: {
        1: { name: 'default', status: 'active' },
        10: { name: 'USERS', status: 'active' },
        20: { name: 'SERVERS', status: 'active' }
      },
      interfaces: {
        'GigabitEthernet0/0': { short: 'Gi0/0', ip: '10.10.0.1', adminUp: true, lineUp: true, mode: 'routed', accessVlan: 1, voiceVlan: null, nativeVlan: 1, allowedVlans: [1], nonegotiate: false, desc: 'WAN-LINK' },
        'GigabitEthernet0/1': { short: 'Gi0/1', ip: 'unassigned', adminUp: true, lineUp: true, mode: 'trunk', accessVlan: 1, voiceVlan: null, nativeVlan: 1, allowedVlans: [1, 10, 20], nonegotiate: false, desc: 'UPLINK' },
        'GigabitEthernet0/2': { short: 'Gi0/2', ip: 'unassigned', adminUp: false, lineUp: false, mode: 'access', accessVlan: 1, voiceVlan: null, nativeVlan: 1, allowedVlans: [1], nonegotiate: false, desc: 'PC-TEST' },
        'GigabitEthernet0/3': { short: 'Gi0/3', ip: 'unassigned', adminUp: true, lineUp: true, mode: 'access', accessVlan: 10, voiceVlan: null, nativeVlan: 1, allowedVlans: [10], nonegotiate: false, desc: 'FINANCE-PC' },
        'GigabitEthernet0/4': { short: 'Gi0/4', ip: 'unassigned', adminUp: true, lineUp: true, mode: 'access', accessVlan: 10, voiceVlan: null, nativeVlan: 1, allowedVlans: [10], nonegotiate: false, desc: 'FINANCE-PC2' },
        'GigabitEthernet0/5': { short: 'Gi0/5', ip: 'unassigned', adminUp: true, lineUp: true, mode: 'access', accessVlan: 20, voiceVlan: null, nativeVlan: 1, allowedVlans: [20], nonegotiate: false, desc: 'SERVER-1' },
        'GigabitEthernet0/6': { short: 'Gi0/6', ip: 'unassigned', adminUp: true, lineUp: true, mode: 'access', accessVlan: 1, voiceVlan: null, nativeVlan: 1, allowedVlans: [1], nonegotiate: false, desc: 'GUEST-PORT' },
        'GigabitEthernet0/7': { short: 'Gi0/7', ip: 'unassigned', adminUp: true, lineUp: true, mode: 'access', accessVlan: 1, voiceVlan: null, nativeVlan: 1, allowedVlans: [1], nonegotiate: false, desc: 'SPARE-PORT' },
        'Loopback0': { short: 'Lo0', ip: '10.255.0.1', adminUp: true, lineUp: true, mode: 'routed', accessVlan: 1, voiceVlan: null, nativeVlan: 1, allowedVlans: [1], nonegotiate: false, desc: 'MGMT' }
      }
    };
  }

  let sim = createInitialSim();

  function resolveIfName(raw) {
    const low = String(raw || '').trim().toLowerCase();
    return Object.keys(sim.interfaces).find(k =>
      k.toLowerCase() === low ||
      sim.interfaces[k].short.toLowerCase() === low ||
      k.toLowerCase().replace('gigabitethernet', 'g') === low
    ) || null;
  }

  function simPromptText() {
    if (sim.mode === 'if') return 'R1(config-if)#';
    if (sim.mode === 'vlan') return 'R1(config-vlan)#';
    if (sim.mode === 'config') return 'R1(config)#';
    if (sim.mode === 'priv') return 'R1#';
    return 'R1>';
  }

  function parseVlanList(str) {
    return String(str || '').split(',').map(x => parseInt(x.trim(), 10)).filter(n => !isNaN(n) && n >= 1 && n <= 4094);
  }

  function runIosCommand(rawCmd, outputEl, promptEl) {
    const cmd = String(rawCmd || '').trim();
    if (!cmd) return;
    let low = cmd.toLowerCase().replace(/\s+/g, ' ');
    const prefix = simPromptText() + ' ';
    let reply = '';
    const inConfigMode = (sim.mode === 'config' || sim.mode === 'if' || sim.mode === 'vlan');
    let isDoExec = false;

    if (low.startsWith('do ') && inConfigMode) {
      isDoExec = true;
      low = low.slice(3).trim();
    }

    const isExecCheckCmd = low.startsWith('show ') || low.startsWith('sh ') || low.startsWith('ping ') || low.startsWith('traceroute ');

    if (low === 'clear') {
      outputEl.textContent = '';
      return;
    } else if (low === 'reset lab') {
      sim = createInitialSim();
      state.cliMode = 'user';
      reply = 'وضعیت شبیه‌ساز به تنظیمات اولیهٔ آزمایشگاه بازنشانی شد.';
    } else if (low === 'help' || low === '?') {
      reply = [
        '۱) دستورات زنده و وضعیت‌دار (تغییر شما فوراً روی خروجی اثر می‌گذارد):',
        '  حالت‌ها: enable | configure terminal | interface Gi0/0..7 | exit | end | do <cmd> | reset lab',
        '  تنظیم پورت: description <NAME> | shutdown | no shutdown | switchport mode access|trunk',
        '              switchport access vlan <id> | switchport voice vlan <id> | switchport nonegotiate',
        '              switchport trunk native vlan <id> | switchport trunk allowed vlan [add] <id,id>',
        '  ساخت VLAN: vlan <id> -> name <NAME>',
        '  بررسی زنده: show running-config | show ip interface brief | show interfaces status | show vlan brief',
        '              show interfaces trunk | show interfaces Gi0/3 switchport | ping <ip> | traceroute <ip>',
        '۲) خروجی‌های نمونهٔ ثابت (برای آشنایی با ظاهر جدول؛ با تغییرات شما عوض نمی‌شوند):',
        '  show arp | show ip route | show mac address-table | show ip ospf neighbor | show ip bgp summary'
      ].join('\n');
    } else if (inConfigMode && !isDoExec && isExecCheckCmd) {
      reply = `% Invalid input detected in config mode.\n(راهنما: در Cisco IOS، در حالت تنظیمات برای اجرای show یا ping یا ابتدا با end به R1# برگردید یا قبل از دستور کلمهٔ do بنویسید؛ مثلاً: do ${cmd})`;
    } else if (low === 'enable' || low === 'en') {
      sim.mode = 'priv';
      state.cliMode = 'priv';
      reply = 'حالت Privileged EXEC فعال شد.';
    } else if (low === 'configure terminal' || low === 'conf t') {
      if (sim.mode === 'user') {
        reply = '% ابتدا دستور enable را وارد کنید.';
      } else {
        sim.mode = 'config';
        sim.activeIf = null;
        sim.activeVlan = null;
        state.cliMode = 'config';
        reply = 'Enter configuration commands, one per line. End with CNTL/Z.';
      }
    } else if (low === 'exit') {
      if (sim.mode === 'if' || sim.mode === 'vlan') {
        sim.mode = 'config';
        sim.activeIf = null;
        sim.activeVlan = null;
      } else if (sim.mode === 'config') {
        sim.mode = 'priv';
      } else {
        sim.mode = 'user';
      }
      state.cliMode = sim.mode === 'config' ? 'config' : (sim.mode === 'priv' ? 'priv' : 'user');
      reply = 'بازگشت به سطح قبلی.';
    } else if (low === 'end') {
      sim.mode = 'priv';
      sim.activeIf = null;
      sim.activeVlan = null;
      state.cliMode = 'priv';
      reply = 'بازگشت به حالت R1#.';
    } else if (low.startsWith('interface ') || low.startsWith('int ')) {
      if (sim.mode === 'user' || sim.mode === 'priv') {
        reply = '% ابتدا با configure terminal وارد حالت تنظیمات شوید.';
      } else {
        const arg = cmd.split(/\s+/).slice(1).join(' ');
        const resolved = resolveIfName(arg);
        if (resolved) {
          sim.mode = 'if';
          sim.activeIf = resolved;
          reply = `وارد تنظیمات پورت ${resolved} شدید.`;
        } else {
          reply = `% اینترفیس "${arg}" در این شبیه‌ساز وجود ندارد (پورت‌های موجود: Gi0/0 تا Gi0/7 و Loopback0).`;
        }
      }
    } else if (/^vlan \d+$/.test(low)) {
      if (sim.mode !== 'config' && sim.mode !== 'if' && sim.mode !== 'vlan') {
        reply = '% ابتدا با configure terminal وارد حالت تنظیمات شوید.';
      } else {
        const vid = parseInt(low.split(' ')[1], 10);
        if (vid < 1 || vid > 4094) {
          reply = '% شماره VLAN باید بین 1 تا 4094 باشد.';
        } else {
          if (!sim.vlans[vid]) sim.vlans[vid] = { name: `VLAN${String(vid).padStart(4, '0')}`, status: 'active' };
          sim.mode = 'vlan';
          sim.activeVlan = vid;
          reply = `VLAN ${vid} انتخاب شد (می‌توانید با دستور name نام آن را تغییر دهید).`;
        }
      }
    } else if (low.startsWith('name ') && sim.mode === 'vlan' && sim.activeVlan) {
      const vname = cmd.split(/\s+/).slice(1).join('_');
      sim.vlans[sim.activeVlan].name = vname;
      reply = `نام VLAN ${sim.activeVlan} به ${vname} تغییر یافت.`;
    } else if (low.startsWith('description ') && sim.mode === 'if' && sim.activeIf) {
      const descTxt = cmd.split(/\s+/).slice(1).join('_');
      sim.interfaces[sim.activeIf].desc = descTxt || 'PORT';
      reply = `توضیحات پورت ${sim.activeIf} به "${sim.interfaces[sim.activeIf].desc}" تغییر یافت.`;
    } else if (low === 'shutdown' && sim.mode === 'if' && sim.activeIf) {
      const iface = sim.interfaces[sim.activeIf];
      iface.adminUp = false;
      iface.lineUp = false;
      reply = `%LINK-5-CHANGED: Interface ${sim.activeIf}, changed state to administratively down`;
    } else if (low === 'no shutdown' && sim.mode === 'if' && sim.activeIf) {
      const iface = sim.interfaces[sim.activeIf];
      iface.adminUp = true;
      iface.lineUp = true;
      reply = `%LINK-3-UPDOWN: Interface ${sim.activeIf}, changed state to up\n%LINEPROTO-5-UPDOWN: Line protocol on Interface ${sim.activeIf}, changed state to up`;
    } else if (low === 'no shutdown') {
      reply = '% ابتدا با interface <name> یک پورت را انتخاب کنید (یا در آزمایشگاه درس ۱: configure terminal -> interface Gi0/2 -> no shutdown).';
    } else if (low === 'switchport mode access' && sim.mode === 'if' && sim.activeIf) {
      const inf = sim.interfaces[sim.activeIf];
      inf.mode = 'access';
      reply = `پورت ${sim.activeIf} در حالت static access قرار گرفت${inf.nonegotiate ? ' (تنظیم switchport nonegotiate قبلی حفظ شد)' : ''}.`;
    } else if (low === 'no switchport nonegotiate' && sim.mode === 'if' && sim.activeIf) {
      const inf = sim.interfaces[sim.activeIf];
      if (inf.mode === 'routed') {
        reply = `% Command rejected: ${sim.activeIf} is a routed interface.`;
      } else {
        inf.nonegotiate = false;
        reply = `تنظیم switchport nonegotiate روی ${sim.activeIf} برداشته شد.`;
      }
    } else if (low === 'switchport mode trunk' && sim.mode === 'if' && sim.activeIf) {
      sim.interfaces[sim.activeIf].mode = 'trunk';
      reply = `پورت ${sim.activeIf} به حالت trunk تنظیم شد.`;
    } else if (low === 'switchport trunk encapsulation dot1q' && sim.mode === 'if' && sim.activeIf) {
      reply = `کپسوله‌سازی 802.1Q روی ${sim.activeIf} تایید شد.`;
    } else if (low === 'switchport nonegotiate' && sim.mode === 'if' && sim.activeIf) {
      const inf = sim.interfaces[sim.activeIf];
      if (inf.mode === 'routed') {
        reply = `% Command rejected: ${sim.activeIf} is a routed interface (دستور switchport nonegotiate روی پورت لایه ۳ مجاز نیست؛ در سوئیچ‌های Catalyst مانند 2960 این دستور در حالت static access یا trunk معتبر است و در مد dynamic رد می‌شود).`;
      } else {
        inf.nonegotiate = true;
        reply = `مذاکرهٔ DTP روی ${sim.activeIf} (حالت ${inf.mode === 'trunk' ? 'trunk' : 'static access'}) غیرفعال شد.`;
      }
    } else if (/^switchport access vlan \d+$/.test(low) && sim.mode === 'if' && sim.activeIf) {
      const vid = parseInt(low.split(' ').pop(), 10);
      if (!sim.vlans[vid]) sim.vlans[vid] = { name: `VLAN${String(vid).padStart(4, '0')}`, status: 'active' };
      sim.interfaces[sim.activeIf].accessVlan = vid;
      reply = `پورت ${sim.activeIf} عضو VLAN ${vid} شد.`;
    } else if (/^switchport voice vlan \d+$/.test(low) && sim.mode === 'if' && sim.activeIf) {
      const vid = parseInt(low.split(' ').pop(), 10);
      if (!sim.vlans[vid]) sim.vlans[vid] = { name: `VLAN${String(vid).padStart(4, '0')}`, status: 'active' };
      sim.interfaces[sim.activeIf].voiceVlan = vid;
      reply = `Voice VLAN پورت ${sim.activeIf} روی ${vid} تنظیم شد.`;
    } else if (/^switchport trunk native vlan \d+$/.test(low) && sim.mode === 'if' && sim.activeIf) {
      const vid = parseInt(low.split(' ').pop(), 10);
      if (!sim.vlans[vid]) sim.vlans[vid] = { name: `VLAN${String(vid).padStart(4, '0')}`, status: 'active' };
      sim.interfaces[sim.activeIf].nativeVlan = vid;
      reply = `Native VLAN روی ترانک ${sim.activeIf} برابر ${vid} شد.`;
    } else if (low.startsWith('switchport trunk allowed vlan ') && sim.mode === 'if' && sim.activeIf) {
      const rest = low.replace('switchport trunk allowed vlan ', '').trim();
      const iface = sim.interfaces[sim.activeIf];
      if (rest.startsWith('add ')) {
        const addIds = parseVlanList(rest.slice(4));
        iface.allowedVlans = Array.from(new Set(iface.allowedVlans.concat(addIds))).sort((a, b) => a - b);
        reply = `VLANهای جدید اضافه شدند. لیست مجاز فعلی: ${iface.allowedVlans.join(',')}`;
      } else {
        const ids = parseVlanList(rest);
        iface.allowedVlans = ids.sort((a, b) => a - b);
        reply = `لیست مجاز ترانک جایگزین شد: ${iface.allowedVlans.join(',') || 'none'}`;
      }
    } else if (low === 'show running-config' || low === 'sh run') {
      if (sim.mode === 'user') {
        reply = '% Invalid input detected (دستور show running-config در مد کاربر R1> مجاز نیست؛ ابتدا دستور enable را وارد کنید).';
      } else {
        const lines = ['Building configuration...', '', 'Current configuration:', '!', 'hostname R1', '!'];
        Object.keys(sim.vlans).map(Number).sort((a, b) => a - b).filter(v => v !== 1).forEach(vid => {
          lines.push(`vlan ${vid}`, ` name ${sim.vlans[vid].name}`, '!');
        });
        Object.entries(sim.interfaces).forEach(([name, inf]) => {
          lines.push(`interface ${name}`);
          if (inf.desc) lines.push(` description ${inf.desc}`);
          if (inf.ip && inf.ip !== 'unassigned') lines.push(` ip address ${inf.ip} 255.255.255.0`);
          if (inf.mode === 'access') {
            lines.push(' switchport mode access');
            if (inf.accessVlan !== 1) lines.push(` switchport access vlan ${inf.accessVlan}`);
            if (inf.voiceVlan) lines.push(` switchport voice vlan ${inf.voiceVlan}`);
            if (inf.nonegotiate) lines.push(' switchport nonegotiate');
          } else if (inf.mode === 'trunk') {
            lines.push(' switchport trunk encapsulation dot1q', ' switchport mode trunk');
            if (inf.nonegotiate) lines.push(' switchport nonegotiate');
            if (inf.nativeVlan !== 1) lines.push(` switchport trunk native vlan ${inf.nativeVlan}`);
            lines.push(` switchport trunk allowed vlan ${inf.allowedVlans.join(',')}`);
          }
          if (!inf.adminUp) lines.push(' shutdown');
          lines.push('!');
        });
        lines.push('end');
        reply = lines.join('\n');
      }
    } else if (low === 'show ip interface brief' || low === 'sh ip int br') {
      const lines = ['Interface              IP-Address      OK? Method Status                Protocol'];
      Object.entries(sim.interfaces).forEach(([name, inf]) => {
        const st = inf.adminUp ? (inf.lineUp ? 'up' : 'down') : 'administratively down';
        const pr = inf.adminUp && inf.lineUp ? 'up' : 'down';
        lines.push(`${name.padEnd(23)}${inf.ip.padEnd(16)}YES manual ${st.padEnd(22)}${pr}`);
      });
      reply = lines.join('\n');
    } else if (low === 'show interfaces status' || low === 'sh int status') {
      const lines = ['Port      Name            Status       Vlan       Duplex  Speed   Type'];
      Object.values(sim.interfaces).filter(i => i.short.startsWith('Gi')).forEach(inf => {
        const st = inf.adminUp ? (inf.lineUp ? 'connected' : 'notconnect') : 'disabled';
        const vl = inf.mode === 'trunk' ? 'trunk' : (inf.mode === 'routed' ? 'routed' : String(inf.accessVlan));
        lines.push(`${inf.short.padEnd(10)}${inf.desc.padEnd(16)}${st.padEnd(13)}${vl.padEnd(11)}a-full  a-1000  10/100/1000BaseTX`);
      });
      reply = lines.join('\n');
    } else if (low === 'show vlan brief' || low === 'sh vlan br') {
      const lines = ['VLAN Name                             Status    Ports', '---- -------------------------------- --------- -------------------------------'];
      Object.keys(sim.vlans).map(Number).sort((a, b) => a - b).forEach(vid => {
        const v = sim.vlans[vid];
        const ports = Object.values(sim.interfaces)
          .filter(i => i.mode === 'access' && i.accessVlan === vid)
          .map(i => i.short)
          .join(', ');
        lines.push(`${String(vid).padEnd(5)}${v.name.padEnd(33)}${v.status.padEnd(10)}${ports}`);
      });
      reply = lines.join('\n');
    } else if (low === 'show interfaces trunk' || low === 'sh int trunk') {
      const trunks = Object.values(sim.interfaces).filter(i => i.mode === 'trunk' && i.adminUp);
      if (!trunks.length) {
        reply = '(هیچ پورت فعالی در حالت Trunk قرار ندارد)';
      } else {
        const lines = ['Port        Mode             Encapsulation  Status        Native vlan'];
        trunks.forEach(t => lines.push(`${t.short.padEnd(12)}on               802.1q         trunking      ${t.nativeVlan}`));
        lines.push('', 'Port        Vlans allowed on trunk');
        trunks.forEach(t => lines.push(`${t.short.padEnd(12)}${t.allowedVlans.join(',') || 'none'}`));
        reply = lines.join('\n');
      }
    } else if (/^show interfaces .+ switchport$/.test(low)) {
      const ifPart = low.split(/\s+/)[2];
      const resolved = resolveIfName(ifPart);
      if (!resolved) {
        reply = `% اینترفیس ${ifPart} یافت نشد.`;
      } else {
        const inf = sim.interfaces[resolved];
        const vName = (sim.vlans[inf.accessVlan] && sim.vlans[inf.accessVlan].name) || '';
        reply = [
          `Name: ${inf.short}`,
          'Switchport: Enabled',
          `Administrative Mode: ${inf.mode === 'trunk' ? 'trunk' : 'static access'}`,
          `Operational Mode: ${inf.mode === 'trunk' ? 'trunk' : 'static access'}`,
          `Negotiation of Trunking: ${(inf.mode === 'access' || inf.nonegotiate) ? 'Off' : 'On'}`,
          `Access Mode VLAN: ${inf.accessVlan} (${vName})`,
          `Trunking Native Mode VLAN: ${inf.nativeVlan}`,
          `Voice VLAN: ${inf.voiceVlan ? inf.voiceVlan : 'none'}`
        ].join('\n');
      }
    } else if (low.startsWith('ping ')) {
      const ip = low.split(/\s+/)[1] || '';
      const g0 = sim.interfaces['GigabitEthernet0/0'];
      const g0Ok = g0 && g0.adminUp && g0.lineUp;
      const reachable = (ip === '10.10.0.1' && g0Ok) || (ip === '10.255.0.1') || ((ip === '10.10.0.2' || ip === '10.255.0.2') && g0Ok);
      if (!ip) {
        reply = '% آدرس IP مقصد را وارد کنید (مثلاً ping 10.10.0.2).';
      } else if (reachable) {
        reply = `Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to ${ip}, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/2/3 ms`;
      } else {
        const reason = !g0Ok ? ' (توجه: اینترفیس خروجی Gi0/0 خاموش است!)' : ' (این آدرس در جدول توپولوژی این آزمایشگاه سبک دسترس‌پذیر نیست یا مسیرش قطع است)';
        reply = `Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to ${ip}, timeout is 2 seconds:\n.....\nSuccess rate is 0 percent (0/5)${reason}`;
      }
    } else if (low.startsWith('traceroute ')) {
      const ip = low.split(/\s+/)[1] || '10.255.0.2';
      const g0 = sim.interfaces['GigabitEthernet0/0'];
      if (g0 && g0.adminUp && g0.lineUp && (ip === '10.10.0.2' || ip === '10.255.0.2')) {
        reply = `Tracing the route to ${ip}\n  1 10.10.0.2 2 msec 1 msec 2 msec\n  2 ${ip} 3 msec 2 msec *`;
      } else {
        reply = `Tracing the route to ${ip}\n  1 * * *\n  2 * * * (مقصد در دسترس نیست یا پورت خروجی خاموش است)`;
      }
    } else if (ACADEMY && ACADEMY.cliResponses && ACADEMY.cliResponses[low]) {
      reply = ACADEMY.cliResponses[low] + '\n\n[یادداشت شبیه‌ساز: این خروجی یک نمونهٔ ثابت آموزشی است و به تغییرات فعلی شما واکنش نشان نمی‌دهد.]';
    } else {
      reply = `% دستور "${cmd}" در این شبیه‌ساز پشتیبانی نمی‌شود. برای دیدن دستورات پشتیبانی‌شده عبارت help را بزنید.`;
    }

    if (promptEl) promptEl.textContent = simPromptText();
    outputEl.textContent += (outputEl.textContent ? '\n\n' : '') + prefix + cmd + '\n' + reply;
    outputEl.scrollTop = outputEl.scrollHeight;
  }

  /* ---------- رندر صفحه عمومی (/academy) ---------- */
  function renderLandingFaculties() {
    const grid = $('#landingFaculties');
    if (!grid || !ACADEMY) return;
    grid.textContent = '';
    ACADEMY.faculties.forEach((f, idx) => {
      const card = el('article', 'fac-card reveal in');
      card.style.setProperty('--d', (idx * 0.05) + 's');

      const top = el('div', 'fac-top');
      top.appendChild(el('span', 'fac-num', 'دانشکده ' + f.num));
      top.appendChild(el('span', 'fac-dur', f.duration));
      card.appendChild(top);

      card.appendChild(el('h3', '', f.title));
      card.appendChild(el('p', '', f.summary));

      const chips = el('div', 'fac-chips');
      f.sections.slice(0, 4).forEach(s => {
        chips.appendChild(el('span', 'fac-chip', s.title));
      });
      card.appendChild(chips);

      const foot = el('div', 'fac-foot');
      foot.appendChild(el('span', 'fac-cert', f.cert));
      const link = el('a', 'btn btn-primary', 'باز کردن سرفصل ←');
      link.href = '/academy/dashboard#faculty-' + f.id;
      foot.appendChild(link);
      card.appendChild(foot);

      grid.appendChild(card);
    });
  }

  /* ================= داشبورد دانشجو ================= */
  const side = $('#side');
  const sideToggle = $('#sideToggle');
  if (side && sideToggle) {
    sideToggle.addEventListener('click', () => side.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (window.innerWidth > 900) return;
      if (!side.contains(e.target) && !sideToggle.contains(e.target)) side.classList.remove('open');
    });
  }

  const viewTitles = {
    home: ['داشبورد آکادمی سیسکو', 'خانه ← نمای کلی برنامه ۶ تا ۸ ساله'],
    lesson: ['کلاس درس تعاملی', 'یادگیری ← آموزش ۱۱ بخشی + آزمایشگاه CLI'],
    courses: ['۷ دانشکده و ۸ تخصص', 'نقشه کامل ← از دانشکده ۰ تا CCDE'],
    lab: ['آزمایشگاه شبیه‌ساز', 'عملی ← ترمینال Cisco IOS و ۳۷ لاب الزامی'],
    exam: ['آزمون ورودی و ارزیابی', 'دانشکده ۰ ← تعیین سطح و حدنصاب ۸۵٪'],
    progress: ['پیشرفت و نقشه ۸ ساله', 'گزارش ← سال ۱ تا ۸ و منابع رسمی'],
    glossary: ['واژه‌نامه جامع و ارجاعات', 'مرجع اصطلاحات ← توضیح فوری و لینک مستقیم به درس']
  };

  /* ---------- موتور واژه‌نامه هوشمند و ارجاع بین‌درسی ---------- */
  let glossMap = new Map();
  let glossRegex = null;
  let glossHideTimer = null;

  function buildGlossaryIndex() {
    if (!ACADEMY || !Array.isArray(ACADEMY.glossary)) return;
    glossMap = new Map();
    const terms = [];
    ACADEMY.glossary.forEach(item => {
      if (!item || !item.term) return;
      glossMap.set(item.term.toLowerCase(), item);
      terms.push(item.term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    });
    terms.sort((a, b) => b.length - a.length);
    if (terms.length) {
      glossRegex = new RegExp('(?<![A-Za-z0-9_])(' + terms.join('|') + ')(?![A-Za-z0-9_])', 'gi');
    }
    const pillG = $('#pillGlossary');
    if (pillG) pillG.textContent = toFa(ACADEMY.glossary.length);
  }

  function openLessonById(lessonId) {
    if (!ACADEMY || !ACADEMY.lessons[lessonId]) return;
    hideGlossaryPopover();
    const grp = (ACADEMY.curriculumGroups || []).find(g => g.lessons.includes(lessonId));
    if (grp) activeLessonFaculty = grp.facultyId;
    state.activeLesson = lessonId;
    persistState();
    renderLessonToc();
    renderLessonArticle(ACADEMY.lessons[lessonId]);
    updateHomeSummary();
    gotoView('lesson');
  }

  function hideGlossaryPopover() {
    const pop = $('#glossPopover');
    if (pop) pop.classList.remove('open');
  }

  function showGlossaryPopover(termObj, anchorEl, currentLessonId) {
    const pop = $('#glossPopover');
    if (!pop || !termObj) return;
    clearTimeout(glossHideTimer);
    pop.textContent = '';

    const head = el('div', 'gp-head');
    head.appendChild(el('span', 'gp-term', termObj.term));
    const closeBtn = el('button', 'gp-close', '×');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'بستن');
    closeBtn.addEventListener('click', hideGlossaryPopover);
    head.appendChild(closeBtn);
    pop.appendChild(head);

    if (termObj.full) pop.appendChild(el('div', 'gp-full', termObj.full));
    pop.appendChild(el('p', 'gp-desc', termObj.desc));

    const refLesson = ACADEMY && ACADEMY.lessons && termObj.ref ? ACADEMY.lessons[termObj.ref] : null;
    if (refLesson) {
      const refRow = el('div', 'gp-ref');
      if (termObj.ref === currentLessonId) {
        refRow.appendChild(el('small', '', '✓ این مبحث در همین درس توضیح داده شده است'));
      } else {
        refRow.appendChild(el('small', '', 'مرجع کامل: ' + refLesson.title));
        const go = el('button', 'btn btn-primary', 'برو به درس ←');
        go.type = 'button';
        go.style.padding = '5px 10px';
        go.style.fontSize = '11.5px';
        go.addEventListener('click', () => openLessonById(termObj.ref));
        refRow.appendChild(go);
      }
      pop.appendChild(refRow);
    }

    pop.classList.add('open');
    const r = anchorEl.getBoundingClientRect();
    const pw = Math.min(360, window.innerWidth - 24);
    const left = Math.max(12, Math.min(window.innerWidth - pw - 12, r.left));
    const spaceBelow = window.innerHeight - r.bottom;
    const top = spaceBelow > 210 ? (r.bottom + 8) : Math.max(12, r.top - 200);
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
  }

  function bindPopoverLifecycle() {
    const pop = $('#glossPopover');
    if (!pop || pop.dataset.bound) return;
    pop.dataset.bound = '1';
    pop.addEventListener('mouseenter', () => clearTimeout(glossHideTimer));
    pop.addEventListener('mouseleave', () => {
      glossHideTimer = setTimeout(hideGlossaryPopover, 260);
    });
    document.addEventListener('click', e => {
      if (!pop.classList.contains('open')) return;
      if (!pop.contains(e.target) && !e.target.classList.contains('gloss-term')) hideGlossaryPopover();
    });
  }

  function appendPlainRichText(parent, text, currentLessonId) {
    const str = String(text || '');
    if (!glossRegex || !str) {
      parent.appendChild(document.createTextNode(str));
      return;
    }
    glossRegex.lastIndex = 0;
    let last = 0;
    let m;
    while ((m = glossRegex.exec(str)) !== null) {
      if (m.index > last) {
        parent.appendChild(document.createTextNode(str.slice(last, m.index)));
      }
      const matched = m[0];
      const entry = glossMap.get(matched.toLowerCase());
      if (entry) {
        const btn = el('button', 'gloss-term', matched);
        btn.type = 'button';
        btn.addEventListener('mouseenter', () => showGlossaryPopover(entry, btn, currentLessonId));
        btn.addEventListener('mouseleave', () => {
          glossHideTimer = setTimeout(hideGlossaryPopover, 260);
        });
        btn.addEventListener('click', e => {
          e.stopPropagation();
          showGlossaryPopover(entry, btn, currentLessonId);
        });
        parent.appendChild(btn);
      } else {
        parent.appendChild(document.createTextNode(matched));
      }
      last = m.index + matched.length;
    }
    if (last < str.length) {
      parent.appendChild(document.createTextNode(str.slice(last)));
    }
  }

  function appendRichText(parent, text, currentLessonId) {
    const str = String(text || '');
    if (!str.includes('```')) {
      appendPlainRichText(parent, str, currentLessonId);
      return;
    }
    const fenceRe = /```([A-Za-z0-9_-]*)\r?\n([\s\S]*?)```/g;
    let last = 0;
    let m;
    while ((m = fenceRe.exec(str)) !== null) {
      if (m.index > last) {
        appendPlainRichText(parent, str.slice(last, m.index), currentLessonId);
      }
      const lang = (m[1] || 'code').trim() || 'code';
      const codeText = m[2].replace(/\r\n/g, '\n').replace(/\n+$/, '');
      const wrap = el('div', 'code-block-wrap');
      wrap.setAttribute('dir', 'ltr');
      const head = el('div', 'code-block-head');
      head.appendChild(el('span', 'code-lang', lang));
      const copyBtn = el('button', 'code-copy-btn', 'کپی کد');
      copyBtn.type = 'button';
      copyBtn.addEventListener('click', () => {
        if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(codeText).then(() => {
            copyBtn.textContent = 'کپی شد ✓';
            setTimeout(() => { copyBtn.textContent = 'کپی کد'; }, 1400);
          }).catch(() => {});
        }
      });
      head.appendChild(copyBtn);
      wrap.appendChild(head);
      const pre = el('pre', 'code-block');
      pre.setAttribute('dir', 'ltr');
      const codeEl = el('code', '', codeText);
      pre.appendChild(codeEl);
      wrap.appendChild(pre);
      parent.appendChild(wrap);
      last = m.index + m[0].length;
    }
    if (last < str.length) {
      appendPlainRichText(parent, str.slice(last), currentLessonId);
    }
  }

  function fillBars(root) {
    $$('.bar i[data-w]', root).forEach(i => { i.style.width = i.dataset.w + '%'; });
    $$('.ring .fg[data-pct]', root).forEach(c => {
      c.style.strokeDashoffset = String(339 - 339 * (+c.dataset.pct) / 100);
    });
  }

  function gotoView(name) {
    const panel = $('[data-panel="' + name + '"]');
    if (!panel) return;
    $$('.view').forEach(v => v.classList.toggle('active', v === panel));
    $$('.snav[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === name));
    const t = viewTitles[name] || ['داشبورد', ''];
    const titleEl = $('#viewTitle'), crumbEl = $('#viewCrumb');
    if (titleEl) titleEl.textContent = t[0];
    if (crumbEl) crumbEl.textContent = t[1];
    panel.querySelectorAll('.reveal').forEach(x => x.classList.add('in'));
    fillBars(panel);
    if (side) side.classList.remove('open');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  $$('.snav[data-view]').forEach(btn => btn.addEventListener('click', () => gotoView(btn.dataset.view)));
  $$('[data-goto]').forEach(node => node.addEventListener('click', e => { e.preventDefault(); gotoView(node.dataset.goto); }));

  /* ---------- رندر خانه داشبورد ---------- */
  function updateHomeSummary() {
    if (!ACADEMY) return;
    const totalLessons = Object.keys(ACADEMY.lessons).length;
    const doneCount = state.completedLessons.length;
    const pct = Math.min(100, Math.round((doneCount / totalLessons) * 100));

    const bar = $('#homeProgBar');
    if (bar) { bar.dataset.w = String(pct); bar.style.width = pct + '%'; }
    const txt = $('#homeProgText');
    if (txt) txt.textContent = toFa(doneCount) + ' از ' + toFa(totalLessons) + ' جلسه';
    const ringFg = $('#homeRingFg');
    if (ringFg) { ringFg.dataset.pct = String(pct); ringFg.style.strokeDashoffset = String(339 - 339 * pct / 100); }
    const ringPct = $('#homeRingPct');
    if (ringPct) ringPct.textContent = toFa(pct) + '٪';
    const xp = $('#homeXpLabel');
    if (xp) xp.textContent = toFa(doneCount * 100 + state.missions.length * 25) + ' امتیاز آکادمی';

    const cur = ACADEMY.lessons[state.activeLesson] || ACADEMY.lessons.s01;
    if (cur) {
      const ht = $('#homeActiveTitle');
      if (ht) ht.textContent = cur.title;
      const hs = $('#homeActiveSub');
      if (hs) hs.textContent = cur.faculty + ' · ۱۲۰ دقیقه روزانه (۲۰ مرور + ۳۵ مفهوم + ۵۰ آزمایشگاه + ۱۵ مستندسازی)';
    }
  }

  function renderHomeBlocks() {
    if (!ACADEMY) return;
    const wBox = $('#homeWeights');
    if (wBox) {
      wBox.textContent = '';
      ACADEMY.meta.weights.forEach(w => {
        const row = el('div', 'skill');
        row.style.marginTop = '10px';
        row.appendChild(el('b', '', w.label));
        const bar = el('div', 'bar');
        const i = el('i');
        i.dataset.w = String(w.pct);
        i.style.width = w.pct + '%';
        bar.appendChild(i);
        row.appendChild(bar);
        row.appendChild(el('span', 'pct', toFa(w.pct) + '٪'));
        wBox.appendChild(row);
      });
    }

    const strip = $('#weeklyStrip');
    if (strip) {
      strip.textContent = '';
      ACADEMY.meta.weeklyPlan.forEach(d => {
        const box = el('div', 'wstrip-item');
        box.appendChild(el('b', '', d.day));
        box.appendChild(el('small', '', d.activity));
        strip.appendChild(box);
      });
    }
  }

  /* ---------- چک‌لیست روزانه ۱۲۰ دقیقه + تایمر ---------- */
  function initDailyMissionsAndTimer() {
    const missionEls = $$('#dailyMissions .mission');
    const syncFoot = () => {
      const done = $$('#dailyMissions .mission.done').length;
      const bar = $('.missions-foot .bar i');
      if (bar) bar.style.width = Math.round((done / 4) * 100) + '%';
      const lbl = $('.missions-foot span');
      if (lbl) lbl.textContent = toFa(done) + ' از ۴ بخش امروز';
    };
    missionEls.forEach((m, idx) => {
      if (state.missions.includes(idx)) m.classList.add('done');
      m.addEventListener('click', () => {
        m.classList.toggle('done');
        state.missions = missionEls.map((x, i) => x.classList.contains('done') ? i : -1).filter(i => i >= 0);
        syncFoot();
        updateHomeSummary();
        persistState();
      });
    });
    syncFoot();

    const tBtn = $('#timerToggleBtn');
    const tDisp = $('#timerDisplay');
    let secLeft = 120 * 60;
    let tId = null;
    if (tBtn && tDisp) {
      tBtn.addEventListener('click', () => {
        if (tId) {
          clearInterval(tId);
          tId = null;
          tBtn.textContent = 'ادامه تایمر ۱۲۰ دقیقه‌ای';
          return;
        }
        tBtn.textContent = 'توقف موقت';
        tId = setInterval(() => {
          if (secLeft <= 0) { clearInterval(tId); tId = null; return; }
          secLeft--;
          const mm = String(Math.floor(secLeft / 60)).padStart(2, '0');
          const ss = String(secLeft % 60).padStart(2, '0');
          tDisp.textContent = toFa(mm + ':' + ss);
        }, 1000);
      });
    }
  }

  /* ---------- کلاس درس ۱۱ بخشی (سبک امن‌افزار رایکا) ---------- */
  function buildAutoLesson(id, title, facultyLabel) {
    return {
      id,
      faculty: facultyLabel || 'دانشکده تخصصی',
      title,
      lead: `در این مبحث استاندارد، ${title} را با ساختار چهارخروجی آکادمی (درک مفهومی، دستورات پیکربندی، آزمایشگاه عملی و عیب‌یابی واقعی) بررسی می‌کنیم.`,
      goal: `تسلط مفهومی و عملی بر ${title}، شناخت پارامترهای کلیدی در Cisco IOS و قابلیت عیب‌یابی در شبکه واقعی.`,
      prereq: 'گذراندن مباحث پایه ترم اول یا آزمون ورودی با حدنصاب ۸۵ از ۱۰۰.',
      sections: [
        { h: `${title} چیست و چرا اهمیت دارد؟`, p: [`در معماری شبکه‌های سازمانی سیسکو، ${title} یکی از ستون‌های اصلی پایداری، امنیت و مقیاس‌پذیری زیرساخت است. مهندس شبکه باید قبل از نوشتن دستور در CLI، بداند این فناوری دقیقاً کدام مسئله را در Control Plane یا Data Plane حل می‌کند.`] },
        { h: 'چارچوب اجرایی ۴ مرحله‌ای در آکادمی', cards: [
          { t: '۱. درک مفهومی', d: 'شناخت فلسفه طراحی، ساختار بسته‌ها و تعامل با سایر لایه‌ها.' },
          { t: '۲. تسلط بر CLI', d: 'پیکربندی تمیز، خواندن خروجی showها و پرهیز از حفظ طوطی‌وار.' },
          { t: '۳. تایید با Packet / Lab', d: 'مشاهده تغییر واقعی در توپولوژی و Wireshark.' },
          { t: '۴. عیب‌یابی مهندسی', d: 'جداسازی ریشه خطا در شرایط خرابی ترکیبی.' }
        ] }
      ],
      protocolAnalysis: ['پروتکل‌ها و وضعیت اینترفیس‌ها همواره باید با خروجی show و Packet Capture تایید شوند.'],
      iosCommands: [
        { cmd: 'show ip interface brief', out: 'Gi0/0  10.10.0.1  up  up', note: 'بررسی وضعیت لایه ۱ تا ۳ پیش از شروع پیکربندی' },
        { cmd: 'show ip route', out: 'C 10.10.0.0/24 ... O 10.255.0.2/32', note: 'تایید جدول مسیریابی' }
      ],
      diagramSvg: 'topo',
      lab: { title: `آزمایشگاه عملی: ${title}`, steps: ['۱. وضعیت شبکه پایه را با show ip interface brief و show ip route بررسی کنید.', '۲. یادداشت مهندسی و تحلیل سناریو را در بخش مستندسازی ثبت کنید.'], verifyCmds: ['show ip interface brief', 'show ip route'] },
      troubleshooting: { fault: 'خرابی عمدی: ارتباط بین دو بخش پس از تغییر تنظیمات قطع شده است.', analysis: 'لایه ۱ تا ۳ را به ترتیب با show interfaces status، show vlan/trunk و show ip route بررسی کنید.', fix: 'اصلاح پارامتر ناهماهنگ و ذخیره با copy run start.' },
      exercise: `سناریوی کاربردی ${title} را در یک سازمان با ۲ شعبه طراحی کرده و دستورات کلیدی آن را یادداشت کنید.`,
      quiz: [{ q: `هدف اصلی از یادگیری ${title} در نظام آکادمی سیسکو چیست؟`, opts: ['فقط حفظ کردن تعاریف', 'درک مفهومی + پیکربندی + آزمایشگاه واقعی + عیب‌یابی (با حدنصاب ۸۵٪)', 'بدون نیاز به آزمایشگاه'], ans: 1, exp: 'طبق قانون آکادمی، هر مبحث باید به هر ۴ خروجی واقعی منجر شود.' }]
    };
  }

  let activeLessonFaculty = 'all';

  function renderLessonToc() {
    const toc = $('#lessonToc');
    const filterBar = $('#lessonFacultyFilter');
    if (!toc || !ACADEMY) return;

    const pill = $('#pillLessons');
    const totalCount = Object.keys(ACADEMY.lessons).length;
    if (pill) pill.textContent = toFa(totalCount);

    const groups = ACADEMY.curriculumGroups || [
      { facultyId: 'f0', title: 'ترم اول', lessons: Object.keys(ACADEMY.lessons) }
    ];

    if (filterBar) {
      filterBar.textContent = '';
      const allBtn = el('button', 'tab-btn' + (activeLessonFaculty === 'all' ? ' active' : ''), `همه دانشکده‌ها (${toFa(totalCount)})`);
      allBtn.addEventListener('click', () => { activeLessonFaculty = 'all'; renderLessonToc(); });
      filterBar.appendChild(allBtn);

      groups.forEach(g => {
        const label = g.title.split('·')[0].trim() + ` (${toFa(g.lessons.length)})`;
        const b = el('button', 'tab-btn' + (activeLessonFaculty === g.facultyId ? ' active' : ''), label);
        b.addEventListener('click', () => {
          activeLessonFaculty = g.facultyId;
          if (!g.lessons.includes(state.activeLesson) && g.lessons.length) {
            state.activeLesson = g.lessons[0];
            persistState();
            renderLessonArticle(ACADEMY.lessons[state.activeLesson]);
            updateHomeSummary();
          }
          renderLessonToc();
        });
        filterBar.appendChild(b);
      });
    }

    toc.textContent = '';
    toc.appendChild(el('h3', '', `فهرست دروس ۷ دانشکده (${toFa(totalCount)} درس کامل)`));

    groups
      .filter(g => activeLessonFaculty === 'all' || g.facultyId === activeLessonFaculty)
      .forEach(g => {
        const box = el('div', 'toc-wk');
        box.appendChild(el('b', '', g.title));
        g.lessons.forEach(lid => {
          const lessonObj = ACADEMY.lessons[lid];
          if (!lessonObj) return;
          const isDone = state.completedLessons.includes(lid);
          const btn = el('button', 'toc-btn' + (state.activeLesson === lid ? ' active' : '') + (isDone ? ' done' : ''));
          btn.appendChild(el('span', '', lessonObj.title));
          btn.appendChild(el('i', '', isDone ? '✓' : '←'));
          btn.addEventListener('click', () => {
            state.activeLesson = lid;
            persistState();
            renderLessonToc();
            renderLessonArticle(lessonObj);
            updateHomeSummary();
          });
          box.appendChild(btn);
        });
        toc.appendChild(box);
      });
  }

  function renderLessonArticle(lessonObj) {
    const host = $('#lessonArticle');
    if (!host || !lessonObj) return;
    host.textContent = '';

    const meta = el('div', 'article-meta');
    meta.appendChild(el('span', 'fac-num', lessonObj.faculty));
    if (state.completedLessons.includes(lessonObj.id)) {
      meta.appendChild(el('span', 'fac-cert', '✓ تکمیل‌شده'));
    }
    host.appendChild(meta);

    host.appendChild(el('h1', 'article-h1', lessonObj.title));
    const leadDiv = el('div', 'article-lead');
    appendRichText(leadDiv, lessonObj.lead, lessonObj.id);
    host.appendChild(leadDiv);

    if (lessonObj.analogy) {
      const ab = el('div', 'analogy-box');
      ab.appendChild(el('b', '', '💡 مثال روزمره (برای ساختن تصویر ذهنی)'));
      const ap = el('p');
      appendRichText(ap, lessonObj.analogy, lessonObj.id);
      ab.appendChild(ap);
      host.appendChild(ab);
    }

    // ۱ و ۲: هدف درس و پیش‌نیاز
    const b1 = el('div', 'step-block');
    b1.appendChild(el('span', 'step-tag', 'بخش ۱ و ۲ · هدف درس و پیش‌نیاز'));
    const gp = el('p');
    appendRichText(gp, 'هدف درس: ' + lessonObj.goal, lessonObj.id);
    b1.appendChild(gp);
    const pp = el('p');
    appendRichText(pp, 'پیش‌نیاز: ' + lessonObj.prereq, lessonObj.id);
    b1.appendChild(pp);
    host.appendChild(b1);

    // ۳: آموزش مفهومی عمیق (سبک امن‌افزار رایکا + جدول مقایسه + FAQ + واژه‌نامه)
    const b3 = el('div', 'step-block');
    b3.appendChild(el('span', 'step-tag', 'بخش ۳ · آموزش مفهومی (ساختار استاندارد + واژه‌نامه تعاملی)'));
    lessonObj.sections.forEach(sec => {
      b3.appendChild(el('h2', '', sec.h));
      if (Array.isArray(sec.p)) {
        sec.p.forEach(para => {
          const pNode = el('p');
          appendRichText(pNode, para, lessonObj.id);
          b3.appendChild(pNode);
        });
      }
      if (Array.isArray(sec.cards)) {
        const g = el('div', 'cards-2');
        sec.cards.forEach(c => {
          const mc = el('div', 'mini-info');
          mc.appendChild(el('b', '', c.t));
          const mp = el('p');
          appendRichText(mp, c.d, lessonObj.id);
          mc.appendChild(mp);
          g.appendChild(mc);
        });
        b3.appendChild(g);
      }
      if (Array.isArray(sec.steps)) {
        const ul = el('ul', 'step-list');
        sec.steps.forEach(st => {
          const li = el('li');
          appendRichText(li, st, lessonObj.id);
          ul.appendChild(li);
        });
        b3.appendChild(ul);
      }
      if (Array.isArray(sec.bullets)) {
        const ul = el('ul', 'step-list');
        sec.bullets.forEach(bt => {
          const li = el('li');
          appendRichText(li, bt, lessonObj.id);
          ul.appendChild(li);
        });
        b3.appendChild(ul);
      }
      if (sec.think && sec.think.q) {
        const tb = el('div', 'think-box');
        const tq = el('div', 'think-q');
        appendRichText(tq, '🤔 مکث فعال: ' + sec.think.q, lessonObj.id);
        tb.appendChild(tq);
        const btn = el('button', 'btn btn-ghost', 'نمایش استدلال و پاسخ');
        btn.type = 'button';
        btn.style.fontSize = '12px';
        const ta = el('div', 'think-a');
        appendRichText(ta, sec.think.a || '', lessonObj.id);
        btn.addEventListener('click', () => {
          const opened = ta.classList.toggle('open');
          btn.textContent = opened ? 'بستن پاسخ' : 'نمایش استدلال و پاسخ';
        });
        tb.appendChild(btn);
        tb.appendChild(ta);
        b3.appendChild(tb);
      }
    });

    if (lessonObj.table && Array.isArray(lessonObj.table.headers) && Array.isArray(lessonObj.table.rows)) {
      const tw = el('div', 'lesson-table-wrap');
      if (lessonObj.table.title) tw.appendChild(el('div', 'lesson-table-title', lessonObj.table.title));
      const tbl = el('table', 'lesson-table');
      const thead = el('thead');
      const htr = el('tr');
      lessonObj.table.headers.forEach(h => htr.appendChild(el('th', '', h)));
      thead.appendChild(htr);
      tbl.appendChild(thead);
      const tbody = el('tbody');
      lessonObj.table.rows.forEach(row => {
        const tr = el('tr');
        row.forEach(cell => {
          const td = el('td');
          appendRichText(td, cell, lessonObj.id);
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      tbl.appendChild(tbody);
      tw.appendChild(tbl);
      b3.appendChild(tw);
    }

    if (Array.isArray(lessonObj.faq) && lessonObj.faq.length) {
      const fh = el('h2', '', 'سوالات متداول (FAQ)');
      fh.style.marginTop = '18px';
      b3.appendChild(fh);
      const fl = el('div', 'faq-list');
      lessonObj.faq.forEach(fq => {
        const fi = el('div', 'faq-item');
        fi.appendChild(el('b', '', fq.q));
        const fp = el('p');
        appendRichText(fp, fq.a, lessonObj.id);
        fi.appendChild(fp);
        fl.appendChild(fi);
      });
      b3.appendChild(fl);
    }

    if (lessonObj.summary) {
      const sb = el('div', 'summary-box');
      sb.appendChild(el('b', '', '✨ جمع‌بندی ساده'));
      const sp = el('p');
      appendRichText(sp, lessonObj.summary, lessonObj.id);
      sb.appendChild(sp);
      b3.appendChild(sb);
    }
    if (lessonObj.ciscoRef) {
      const cr = el('div', 'cisco-ref-box');
      cr.appendChild(el('b', '', '📘 منبع رسمی سیسکو:'));
      cr.appendChild(el('span', '', lessonObj.ciscoRef));
      b3.appendChild(cr);
    }
    host.appendChild(b3);

    // ۴: تحلیل پروتکل
    const b4 = el('div', 'step-block');
    b4.appendChild(el('span', 'step-tag', 'بخش ۴ · تحلیل رفتار پروتکل و بسته'));
    const ul4 = el('ul', 'step-list');
    lessonObj.protocolAnalysis.forEach(item => {
      const li = el('li');
      appendRichText(li, item, lessonObj.id);
      ul4.appendChild(li);
    });
    b4.appendChild(ul4);
    host.appendChild(b4);

    // ۵: دستورات Cisco IOS
    const b5 = el('div', 'step-block');
    b5.appendChild(el('span', 'step-tag', 'بخش ۵ · دستورات کلیدی Cisco IOS (چرا، ساختار و تفسیر خروجی)'));
    lessonObj.iosCommands.forEach(c => {
      const box = el('div', 'mini-info');
      box.style.marginBottom = '10px';
      box.appendChild(el('b', '', c.cmd));
      const pre = el('pre', 'cli-out', c.out);
      pre.style.margin = '6px 0';
      box.appendChild(pre);
      const noteP = el('p');
      appendRichText(noteP, c.note, lessonObj.id);
      box.appendChild(noteP);
      if (c.why || c.anatomy || c.lookFor || c.ifUnexpected) {
        const det = el('div', 'cmd-details');
        const rows = [
          ['چرا اجرا می‌شود:', c.why],
          ['معنای بخش‌های دستور:', c.anatomy],
          ['در خروجی دنبال چه بگردیم:', c.lookFor],
          ['اگر نتیجه متفاوت بود:', c.ifUnexpected]
        ];
        rows.forEach(([lbl, val]) => {
          if (!val) return;
          const r = el('div', 'cmd-detail-row');
          r.appendChild(el('b', '', lbl));
          appendRichText(r, val, lessonObj.id);
          det.appendChild(r);
        });
        box.appendChild(det);
      }
      b5.appendChild(box);
    });
    host.appendChild(b5);

    // ۶: دیاگرام
    const b6 = el('div', 'step-block');
    b6.appendChild(el('span', 'step-tag', 'بخش ۶ · دیاگرام معماری درس'));
    const dbox = el('div', 'diagram-box');
    dbox.appendChild(buildDiagramSvg(lessonObj.diagramSvg || 'topo'));
    b6.appendChild(dbox);
    host.appendChild(b6);

    // ۷: Lab تعاملی داخل درس
    const b7 = el('div', 'step-block');
    b7.appendChild(el('span', 'step-tag', 'بخش ۷ · آزمایشگاه عملی (Lab)'));
    b7.appendChild(el('h2', '', lessonObj.lab.title));
    const simNote = el('p', '', 'مرز شبیه‌ساز: در این ترمینال، دستورات پیکربندی پورت (Gi0/0..7، shutdown/no shutdown)، ساخت و نام‌گذاری VLAN، تنظیمات Access/Trunk، و دستورات show running-config / show ip interface brief / show interfaces status / show vlan brief / show interfaces trunk / switchport / ping / traceroute به‌صورت زنده و وضعیت‌دار به تغییرات شما واکنش می‌دهند (در حالت تنظیمات از end یا پیشوند do استفاده کنید). سایر دستورات مانند show arp یا show ip route صرفاً خروجی نمونهٔ ثابت نمایش می‌دهند و با علامت [خروجی نمونهٔ ثابت] مشخص می‌شوند.');
    simNote.style.fontSize = '12.5px';
    simNote.style.color = '#93c5fd';
    b7.appendChild(simNote);
    const ul7 = el('ul', 'step-list');
    lessonObj.lab.steps.forEach(s => {
      const li = el('li');
      appendRichText(li, s, lessonObj.id);
      ul7.appendChild(li);
    });
    b7.appendChild(ul7);

    const qRow = el('div', 'cli-quick');
    (lessonObj.lab.verifyCmds || ['show ip interface brief']).forEach(cmdStr => {
      const qb = el('button', 'cli-qbtn', cmdStr);
      qb.addEventListener('click', () => runIosCommand(cmdStr, cliOut, cliPrompt));
      qRow.appendChild(qb);
    });
    b7.appendChild(qRow);

    const cliWrap = el('div', 'cli-box');
    const cliOut = el('div', 'cli-out', 'R1> (دستورات آزمایشگاه را اینجا وارد کنید یا از دکمه‌های بالا بزنید)');
    const cliRow = el('div', 'cli-in-row');
    const cliPrompt = el('span', '', 'R1>');
    const cliIn = el('input');
    cliIn.type = 'text';
    cliIn.placeholder = 'enable  |  show ip interface brief  |  help';
    const cliBtn = el('button', 'btn btn-primary', 'اجرا');
    const exec = () => {
      runIosCommand(cliIn.value, cliOut, cliPrompt);
      cliIn.value = '';
    };
    cliBtn.addEventListener('click', exec);
    cliIn.addEventListener('keydown', e => { if (e.key === 'Enter') exec(); });
    cliRow.appendChild(cliPrompt);
    cliRow.appendChild(cliIn);
    cliRow.appendChild(cliBtn);
    cliWrap.appendChild(cliOut);
    cliWrap.appendChild(cliRow);
    b7.appendChild(cliWrap);
    host.appendChild(b7);

    // ۸: عیب‌یابی (Troubleshooting)
    const b8 = el('div', 'step-block');
    b8.appendChild(el('span', 'step-tag', 'بخش ۸ · عیب‌یابی سناریوی خطا (Troubleshooting)'));
    const tb = el('div', 'trouble-box');
    const tf = el('p'); appendRichText(tf, lessonObj.troubleshooting.fault, lessonObj.id); tb.appendChild(tf);
    const ta8 = el('p'); appendRichText(ta8, 'تحلیل ریشه‌ای: ' + lessonObj.troubleshooting.analysis, lessonObj.id); tb.appendChild(ta8);
    const tx8 = el('p'); appendRichText(tx8, 'راه‌حل اصلاحی: ' + lessonObj.troubleshooting.fix, lessonObj.id); tb.appendChild(tx8);
    b8.appendChild(tb);
    if (Array.isArray(lessonObj.misconceptions) && lessonObj.misconceptions.length) {
      b8.appendChild(el('h2', '', 'اشتباهات و سوءبرداشت‌های رایج (و روش تشخیص آن‌ها)'));
      const mg = el('div', 'mis-grid');
      lessonObj.misconceptions.forEach(m => {
        const mc = el('div', 'mis-card');
        mc.appendChild(el('b', '', '⚠️ سوءبرداشت: ' + m.myth));
        const mp1 = el('p'); appendRichText(mp1, 'چرا اشتباه است و واقعیت چیست: ' + m.reality, lessonObj.id); mc.appendChild(mp1);
        if (m.howToSpot) {
          const mp2 = el('p'); appendRichText(mp2, 'چطور خودت تشخیص بدهی: ' + m.howToSpot, lessonObj.id); mc.appendChild(mp2);
        }
        mg.appendChild(mc);
      });
      b8.appendChild(mg);
    }
    host.appendChild(b8);

    // ۹: تمرین مستقل
    const b9 = el('div', 'step-block');
    b9.appendChild(el('span', 'step-tag', 'بخش ۹ · تمرین مستقل دانشجو (از ساده تا چالشی)'));
    if (Array.isArray(lessonObj.exercises) && lessonObj.exercises.length) {
      const exl = el('div', 'ex-list');
      lessonObj.exercises.forEach((ex, idx) => {
        const ec = el('div', 'ex-card');
        const eh = el('div', 'ex-head');
        eh.appendChild(el('b', '', 'تمرین ' + toFa(idx + 1)));
        if (ex.level) eh.appendChild(el('span', 'ex-lvl', ex.level));
        ec.appendChild(eh);
        const ep = el('p'); appendRichText(ep, ex.task, lessonObj.id); ec.appendChild(ep);
        const acts = el('div', 'ex-actions');
        const revBox = el('div', 'ex-reveal');
        if (ex.hint) {
          const hBtn = el('button', 'btn btn-ghost', 'راهنمای حل');
          hBtn.type = 'button'; hBtn.style.fontSize = '12px';
          hBtn.addEventListener('click', () => {
            revBox.textContent = '';
            const hb = el('b', '', 'راهنما: ');
            revBox.appendChild(hb);
            appendRichText(revBox, ex.hint, lessonObj.id);
            revBox.classList.add('open');
          });
          acts.appendChild(hBtn);
        }
        if (ex.solution) {
          const sBtn = el('button', 'btn btn-ghost', 'پاسخ تشریحی');
          sBtn.type = 'button'; sBtn.style.fontSize = '12px';
          sBtn.addEventListener('click', () => {
            revBox.textContent = '';
            const sb = el('b', '', 'پاسخ تشریحی: ');
            revBox.appendChild(sb);
            appendRichText(revBox, ex.solution, lessonObj.id);
            revBox.classList.add('open');
          });
          acts.appendChild(sBtn);
        }
        ec.appendChild(acts);
        ec.appendChild(revBox);
        exl.appendChild(ec);
      });
      b9.appendChild(exl);
    } else {
      const exP = el('p');
      appendRichText(exP, lessonObj.exercise, lessonObj.id);
      b9.appendChild(exP);
    }
    host.appendChild(b9);

    // ۱۰: آزمون درس (با ارزیابی و حدنصاب ۸۵٪)
    const b10 = el('div', 'step-block');
    b10.appendChild(el('span', 'step-tag', 'بخش ۱۰ · آزمون پایانی جلسه (حدنصاب قبولی ۸۵٪)'));
    const qBox = el('div', 'quiz-box');
    const selected = {};
    const expNodes = [];
    (lessonObj.quiz || []).forEach((q, qi) => {
      const qc = el('div', 'q-card');
      qc.appendChild(el('b', '', toFa(qi + 1) + '. ' + q.q));
      const opts = el('div', 'q-opts');
      q.opts.forEach((op, oi) => {
        const lbl = el('label', 'q-opt');
        const radio = el('input');
        radio.type = 'radio';
        radio.name = 'quiz_' + lessonObj.id + '_' + qi;
        radio.addEventListener('change', () => { selected[qi] = oi; });
        lbl.appendChild(radio);
        lbl.appendChild(el('span', '', op));
        opts.appendChild(lbl);
      });
      qc.appendChild(opts);
      const exp = el('div', 'q-exp', '');
      expNodes.push({ exp, q, qi });
      qc.appendChild(exp);
      qBox.appendChild(qc);
    });
    b10.appendChild(qBox);

    const qRes = el('p', '', '');
    qRes.style.marginTop = '12px';
    const qSubmit = el('button', 'btn btn-primary', 'ثبت و نمره‌دهی آزمون جلسه');
    qSubmit.style.marginTop = '12px';
    qSubmit.addEventListener('click', () => {
      const qs = lessonObj.quiz || [];
      let correct = 0;
      expNodes.forEach(({ exp, q, qi }) => {
        const ok = selected[qi] === q.ans;
        if (ok) correct++;
        exp.textContent = (ok ? '✓ صحیح — ' : '✗ پاسخ صحیح: ' + q.opts[q.ans] + ' — ') + q.exp;
        exp.style.color = ok ? '#34d399' : '#fbbf24';
      });
      const score = qs.length ? Math.round((correct / qs.length) * 100) : 100;
      state.quizScores[lessonObj.id] = score;
      if (score >= 85 && !state.completedLessons.includes(lessonObj.id)) {
        state.completedLessons.push(lessonObj.id);
      }
      persistState();
      renderLessonToc();
      updateHomeSummary();
      renderProgressView();
      qRes.textContent = `نمره شما: ${toFa(score)} از ۱۰۰ ` + (score >= 85 ? '— قبولی و ثبت تکمیل جلسه ✓' : '— برای عبور حداقل ۸۵ از ۱۰۰ لازم است.');
      qRes.style.color = score >= 85 ? '#34d399' : '#fbbf24';
    });
    b10.appendChild(qSubmit);
    b10.appendChild(qRes);
    host.appendChild(b10);

    // ۱۱: مستندسازی (دفترچه یادداشت متصل به سرور)
    const b11 = el('div', 'step-block');
    b11.appendChild(el('span', 'step-tag', 'بخش ۱۱ · مستندسازی و دفترچه یادداشت'));
    const ta = el('textarea', 'note-area');
    ta.placeholder = 'خلاصه دستورات، یافته‌های Wireshark و نکات عیب‌یابی این جلسه را بنویسید...';
    ta.value = state.notes[lessonObj.id] || '';
    const saveNoteBtn = el('button', 'btn btn-ghost', 'ذخیره یادداشت در پروفایل');
    saveNoteBtn.style.marginTop = '10px';
    const noteMsg = el('span', '', '');
    noteMsg.style.marginInlineStart = '12px';
    noteMsg.style.color = '#34d399';
    saveNoteBtn.addEventListener('click', () => {
      state.notes[lessonObj.id] = ta.value;
      persistState();
      noteMsg.textContent = 'در سرور FAM ذخیره شد ✓';
    });
    b11.appendChild(ta);
    b11.appendChild(saveNoteBtn);
    b11.appendChild(noteMsg);
    host.appendChild(b11);

    if (lessonObj.bridge) {
      const br = el('div', 'bridge-box');
      br.appendChild(el('b', '', '🔗 پیوند به درس‌های دیگر و ادامه مسیر'));
      if (lessonObj.bridge.whereUsed) {
        const p1 = el('p'); appendRichText(p1, 'کجا به کار می‌آید: ' + lessonObj.bridge.whereUsed, lessonObj.id); br.appendChild(p1);
      }
      if (lessonObj.bridge.nextQuestion) {
        const p2 = el('p'); appendRichText(p2, 'پرسش پیش روی ما برای درس بعد: ' + lessonObj.bridge.nextQuestion, lessonObj.id); br.appendChild(p2);
      }
      if (lessonObj.bridge.nextId && ACADEMY.lessons[lessonObj.bridge.nextId]) {
        const nLesson = ACADEMY.lessons[lessonObj.bridge.nextId];
        const nb = el('button', 'btn btn-primary', 'رفتن به درس بعدی: ' + nLesson.title + ' ←');
        nb.type = 'button';
        nb.style.justifySelf = 'start';
        nb.addEventListener('click', () => openLessonById(lessonObj.bridge.nextId));
        br.appendChild(nb);
      }
      host.appendChild(br);
    }
  }

  /* ---------- رندر ۷ دانشکده و ۸ تخصص ---------- */
  let activeFacultyId = 'f0';
  function renderFacultiesView() {
    const tabs = $('#facultyTabs');
    const area = $('#facultyDetailArea');
    if (!tabs || !area || !ACADEMY) return;

    tabs.textContent = '';
    ACADEMY.faculties.forEach(f => {
      const b = el('button', 'tab-btn' + (f.id === activeFacultyId ? ' active' : ''), `دانشکده ${f.num}: ${f.title}`);
      b.addEventListener('click', () => { activeFacultyId = f.id; renderFacultiesView(); });
      tabs.appendChild(b);
    });

    const f = ACADEMY.faculties.find(x => x.id === activeFacultyId) || ACADEMY.faculties[0];
    area.textContent = '';

    const box = el('div', 'fac-detail-box');
    const head = el('div', 'fac-top');
    head.appendChild(el('span', 'fac-num', `دانشکده ${f.num} · ${f.duration}`));
    head.appendChild(el('span', 'fac-cert', f.cert));
    box.appendChild(head);
    box.appendChild(el('h3', '', f.title));
    box.appendChild(el('p', '', f.summary));

    const grp = (ACADEMY.curriculumGroups || []).find(g => g.facultyId === f.id);
    if (grp && grp.lessons.length) {
      const lBox = el('div', 'fac-detail-box');
      lBox.style.marginTop = '14px';
      const lHead = el('div', 'fac-top');
      lHead.appendChild(el('b', '', `دروس کامل این دانشکده (${toFa(grp.lessons.length)} درس ۱۱ بخشی)`));
      const allInCls = el('button', 'btn btn-primary', 'مشاهده همه در کلاس درس ←');
      allInCls.addEventListener('click', () => {
        activeLessonFaculty = f.id;
        state.activeLesson = grp.lessons[0];
        renderLessonToc();
        renderLessonArticle(ACADEMY.lessons[grp.lessons[0]]);
        gotoView('lesson');
      });
      lHead.appendChild(allInCls);
      lBox.appendChild(lHead);

      const lGrid = el('div', 'cards-2');
      lGrid.style.marginTop = '12px';
      grp.lessons.forEach(lid => {
        const lObj = ACADEMY.lessons[lid];
        if (!lObj) return;
        const lc = el('div', 'mini-info');
        lc.appendChild(el('b', '', lObj.title));
        lc.appendChild(el('p', '', lObj.goal));
        const goBtn = el('button', 'btn btn-ghost', 'ورود به این درس ←');
        goBtn.style.marginTop = '8px';
        goBtn.addEventListener('click', () => {
          activeLessonFaculty = f.id;
          state.activeLesson = lid;
          persistState();
          renderLessonToc();
          renderLessonArticle(lObj);
          gotoView('lesson');
        });
        lc.appendChild(goBtn);
        lGrid.appendChild(lc);
      });
      lBox.appendChild(lGrid);
      box.appendChild(lBox);
    }

    const secGrid = el('div', 'cards-2');
    secGrid.style.marginTop = '16px';
    f.sections.forEach((sec, si) => {
      const mc = el('div', 'mini-info');
      mc.appendChild(el('b', '', sec.title));
      const ul = el('ul', 'step-list');
      sec.items.forEach(it => ul.appendChild(el('li', '', it)));
      mc.appendChild(ul);
      const openBtn = el('button', 'btn btn-ghost', 'باز کردن در کلاس درس ←');
      openBtn.style.marginTop = '10px';
      openBtn.addEventListener('click', () => {
        const auto = buildAutoLesson(f.id + '_' + si, sec.title, `دانشکده ${f.num} · ${f.title}`);
        renderLessonArticle(auto);
        gotoView('lesson');
      });
      mc.appendChild(openBtn);
      secGrid.appendChild(mc);
    });
    box.appendChild(secGrid);

    const labSec = el('div', 'fac-detail-box');
    labSec.appendChild(el('h3', '', 'آزمایشگاه‌های شاخص این دانشکده'));
    const lul = el('ul', 'step-list');
    f.labs.forEach(lb => lul.appendChild(el('li', '', lb)));
    labSec.appendChild(lul);

    const proj = el('div', 'article-lead');
    proj.style.marginTop = '14px';
    proj.textContent = 'پروژه پایانی دانشکده: ' + f.project;
    labSec.appendChild(proj);

    area.appendChild(box);
    area.appendChild(labSec);
  }

  /* ---------- رندر آزمایشگاه و ۳۷ لاب + ۱۱ ابزار ---------- */
  let activeLabTab = 'ccna';
  function renderLabView() {
    if (!ACADEMY) return;
    const quick = $('#labQuickBtns');
    const out = $('#labCliOut');
    const prompt = $('#labCliPrompt');
    const inp = $('#labCliInput');
    const runBtn = $('#labCliRun');

    if (quick && out && inp && runBtn && !quick.dataset.bound) {
      quick.dataset.bound = '1';
      ['help', 'enable', 'show ip interface brief', 'show vlan brief', 'show interfaces trunk', 'show ip route', 'show ip ospf neighbor', 'show ip bgp summary', 'ping 10.10.0.2', 'clear'].forEach(c => {
        const b = el('button', 'cli-qbtn', c);
        b.addEventListener('click', () => runIosCommand(c, out, prompt));
        quick.appendChild(b);
      });
      const go = () => { runIosCommand(inp.value, out, prompt); inp.value = ''; };
      runBtn.addEventListener('click', go);
      inp.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
    }

    const listEl = $('#mandatoryLabsList');
    if (listEl) {
      listEl.textContent = '';
      const src = activeLabTab === 'ccna' ? ACADEMY.faculties[1].labs : ACADEMY.faculties[2].labs;
      src.forEach((name, idx) => {
        const row = el('div', 'lab-item');
        row.appendChild(el('span', 'lab-ic', '🧪'));
        const span = el('span');
        span.appendChild(el('b', '', name));
        span.appendChild(el('small', '', activeLabTab === 'ccna' ? 'CCNA 200-301 · الزامی' : 'Advanced R&S · عملی'));
        row.appendChild(span);
        const btn = el('button', 'st st-run', 'اجرا در درس');
        btn.style.cursor = 'pointer';
        btn.addEventListener('click', () => {
          renderLessonArticle(buildAutoLesson('lab_' + activeLabTab + '_' + idx, name, 'آزمایشگاه عملی آکادمی'));
          gotoView('lesson');
        });
        row.appendChild(btn);
        listEl.appendChild(row);
      });
    }

    $$('[data-labtab]').forEach(tb => {
      if (tb.dataset.bound) return;
      tb.dataset.bound = '1';
      tb.addEventListener('click', () => {
        activeLabTab = tb.dataset.labtab;
        $$('[data-labtab]').forEach(x => x.classList.toggle('active', x.dataset.labtab === activeLabTab));
        renderLabView();
      });
    });

    const toolsEl = $('#labToolsList');
    if (toolsEl && !toolsEl.dataset.bound) {
      toolsEl.dataset.bound = '1';
      ACADEMY.meta.labTools.forEach(t => {
        const item = el('div', 'fitem');
        item.appendChild(el('span', 'fic', '⚙'));
        const sp = el('span');
        sp.appendChild(el('b', '', t.name));
        sp.appendChild(el('small', '', t.use));
        item.appendChild(sp);
        toolsEl.appendChild(item);
      });
    }
  }

  /* ---------- رندر آزمون ورودی دانشکده ۰ ---------- */
  function renderEntranceExam() {
    const card = $('#entranceExamCard');
    if (!card || !ACADEMY) return;
    card.textContent = '';
    card.appendChild(el('h3', '', 'آزمون ورودی ارزیابی مبانی (۱۰ سؤال نمونه از بانک ۵۰+۱۰ سؤالی)'));
    const qBox = el('div', 'quiz-box');
    const picks = {};
    ACADEMY.entranceExam.forEach((q, i) => {
      const qc = el('div', 'q-card');
      qc.appendChild(el('b', '', `${toFa(i + 1)}. [${q.topic}] ${q.q}`));
      const opts = el('div', 'q-opts');
      q.opts.forEach((op, oi) => {
        const lbl = el('label', 'q-opt');
        const r = el('input');
        r.type = 'radio';
        r.name = 'ent_' + q.id;
        r.addEventListener('change', () => { picks[i] = oi; });
        lbl.appendChild(r);
        lbl.appendChild(el('span', '', op));
        opts.appendChild(lbl);
      });
      qc.appendChild(opts);
      qBox.appendChild(qc);
    });
    card.appendChild(qBox);

    const resBox = el('p', '', state.examScore !== null ? `آخرین نمره ثبت‌شده شما: ${toFa(state.examScore)} از ۱۰۰` : '');
    resBox.style.marginTop = '12px';
    const sub = el('button', 'btn btn-primary', 'محاسبه نمره و تعیین مسیر پیشنهادی');
    sub.style.marginTop = '14px';
    sub.addEventListener('click', () => {
      let ok = 0;
      ACADEMY.entranceExam.forEach((q, i) => { if (picks[i] === q.ans) ok++; });
      const pct = Math.round((ok / ACADEMY.entranceExam.length) * 100);
      state.examScore = pct;
      persistState();
      resBox.textContent = pct >= 85
        ? `عالی! نمره ${toFa(pct)} از ۱۰۰ — آماده ورود مستقیم به دانشکده ۱ (CCNA 200-301) هستید.`
        : `نمره ${toFa(pct)} از ۱۰۰ — پیشنهاد می‌شود ترم اول (هفته ۱ تا ۴ مبانی و Subnetting) را کامل بگذرانید تا به بالای ۸۵ برسید.`;
      resBox.style.color = pct >= 85 ? '#34d399' : '#fbbf24';
    });
    card.appendChild(sub);
    card.appendChild(resBox);
  }

  /* ---------- رندر پیشرفت، نقشه ۸ ساله و منابع رسمی ---------- */
  function renderProgressView() {
    if (!ACADEMY) return;
    const yt = $('#yearsTimeline');
    if (yt) {
      yt.textContent = '';
      ACADEMY.meta.yearsPlan.forEach(y => {
        const it = el('div', 'fitem');
        it.appendChild(el('span', 'fic', '📆'));
        const sp = el('span');
        sp.appendChild(el('b', '', y.year));
        sp.appendChild(el('small', '', y.goal));
        it.appendChild(sp);
        yt.appendChild(it);
      });
    }

    const res = $('#officialResources');
    if (res) {
      res.textContent = '';
      ACADEMY.meta.resources.forEach(r => {
        const it = el('div', 'fitem');
        it.appendChild(el('span', 'fic', '🔗'));
        const sp = el('span');
        sp.appendChild(el('b', '', r.name));
        sp.appendChild(el('small', '', r.desc));
        it.appendChild(sp);
        res.appendChild(it);
      });
    }

    const certs = $('#progressCerts');
    if (certs) {
      certs.textContent = '';
      const doneCount = state.completedLessons.length;
      const items = [
        ['تکمیل جلسات ترم ۱', `${toFa(doneCount)} جلسه قبول‌شده (≥۸۵٪)`, doneCount >= 1],
        ['آزمون ورودی مبانی', state.examScore !== null ? `نمره: ${toFa(state.examScore)}٪` : 'در انتظار آزمون', (state.examScore || 0) >= 85],
        ['CCNA 200-301', 'پس از ۲۵ آزمایشگاه و پروژه سه‌طبقه', false],
        ['CCNP / CCIE / CCDE', 'مسیر بلندمدت ۶ تا ۸ ساله', false]
      ];
      items.forEach(([t, s, open]) => {
        const c = el('div', 'cert' + (open ? '' : ' locked'));
        c.appendChild(el('b', '', t));
        c.appendChild(el('small', '', s));
        certs.appendChild(c);
      });
    }
  }

  /* ---------- جستجوی سریع (Ctrl+K) ---------- */
  const searchInp = $('#dashSearch');
  if (searchInp) {
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        searchInp.focus();
      }
    });
    searchInp.addEventListener('keydown', e => {
      if (e.key !== 'Enter' || !ACADEMY) return;
      const q = searchInp.value.trim().toLowerCase();
      if (!q) return;
      const found = Object.values(ACADEMY.lessons).find(l => (l.title + ' ' + l.lead).toLowerCase().includes(q));
      if (found) {
        state.activeLesson = found.id;
        renderLessonToc();
        renderLessonArticle(found);
        gotoView('lesson');
      }
    });
  }

  /* ---------- رندر واژه‌نامه جامع ---------- */
  function renderGlossaryView(filterStr) {
    const grid = $('#glossaryGrid');
    const search = $('#glossarySearch');
    if (!grid || !ACADEMY || !Array.isArray(ACADEMY.glossary)) return;

    if (search && !search.dataset.bound) {
      search.dataset.bound = '1';
      search.addEventListener('input', () => renderGlossaryView(search.value));
    }

    const q = String(filterStr || '').trim().toLowerCase();
    const list = ACADEMY.glossary.filter(item =>
      !q || (item.term + ' ' + item.full + ' ' + item.desc).toLowerCase().includes(q)
    );
    grid.textContent = '';
    list.forEach(item => {
      const card = el('div', 'gloss-card');
      const top = el('div', 'gloss-card-top');
      top.appendChild(el('b', '', item.term));
      if (item.full) top.appendChild(el('small', '', item.full));
      card.appendChild(top);
      card.appendChild(el('p', '', item.desc));

      const refLesson = item.ref && ACADEMY.lessons[item.ref] ? ACADEMY.lessons[item.ref] : null;
      if (refLesson) {
        const btn = el('button', 'btn btn-ghost', '📚 درس مرجع: ' + refLesson.title);
        btn.type = 'button';
        btn.style.marginTop = 'auto';
        btn.style.fontSize = '12px';
        btn.style.justifyContent = 'flex-start';
        btn.addEventListener('click', () => openLessonById(item.ref));
        card.appendChild(btn);
      }
      grid.appendChild(card);
    });
  }

  /* ---------- راه‌اندازی ---------- */
  loadAcademyData().then(data => {
    if (!data) return;
    buildGlossaryIndex();
    bindPopoverLifecycle();
    renderLandingFaculties();
    renderHomeBlocks();
    updateHomeSummary();
    initDailyMissionsAndTimer();
    renderLessonToc();
    renderLessonArticle(ACADEMY.lessons[state.activeLesson] || ACADEMY.lessons.s01);
    renderFacultiesView();
    renderLabView();
    renderEntranceExam();
    renderProgressView();
    renderGlossaryView('');

    const h = window.location.hash || '';
    if (h.startsWith('#lesson-')) {
      const id = h.replace('#lesson-', '');
      if (ACADEMY.lessons[id]) {
        state.activeLesson = id;
        renderLessonToc();
        renderLessonArticle(ACADEMY.lessons[id]);
      }
      gotoView('lesson');
    } else if (h.startsWith('#faculty-')) {
      const fid = h.replace('#faculty-', '');
      if (ACADEMY.faculties.some(x => x.id === fid)) activeFacultyId = fid;
      renderFacultiesView();
      gotoView('courses');
    } else if (h === '#exam') {
      gotoView('exam');
    } else if (h === '#courses') {
      gotoView('courses');
    }
  });
})();
