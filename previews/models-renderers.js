(() => {
  'use strict';
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  const FAC = [
    { id: 'f0', tag: 'دانشکده ۰', title: 'مبانی و IPv4', lessons: 10, hrs: '۱۲ ساعت', col: 'var(--accent)' },
    { id: 'f1', tag: 'دانشکده ۱', title: 'CCNA 200-301', lessons: 48, hrs: '۶۵ ساعت', col: 'var(--accent2)' },
    { id: 'f2', tag: 'دانشکده ۲', title: 'R&S پیشرفته', lessons: 24, hrs: '۳۸ ساعت', col: 'var(--accent3)' },
    { id: 'f3', tag: 'دانشکده ۳', title: 'CCNP ENCOR', lessons: 36, hrs: '۵۸ ساعت', col: 'var(--accent)' },
    { id: 'f4', tag: 'دانشکده ۴', title: 'Security / EVPN / SD-WAN', lessons: 28, hrs: '۴۵ ساعت', col: 'var(--accent2)' },
    { id: 'f5', tag: 'دانشکده ۵', title: 'CCIE MPLS & SR', lessons: 20, hrs: '۷۰ ساعت', col: 'var(--accent3)' },
    { id: 'f6', tag: 'دانشکده ۶', title: 'CCDE Architecture', lessons: 16, hrs: '۴۰ ساعت', col: 'var(--accent)' }
  ];

  /* ===== قطعات مشترک SVG و تعاملی ===== */
  function flagshipTopologySvg(m) {
    const c1 = m.vars.accent, c2 = m.vars.accent2, c3 = m.vars.accent3, txt = m.vars.text, card = m.vars.panel2;
    return `<svg viewBox="0 0 600 410" width="100%" style="height:auto;display:block" aria-label="توپولوژی زنده">
      <defs><linearGradient id="g_${m.id}" x1="0" y1="0" x2="1" y2="0"><stop stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient></defs>
      <g fill="none" stroke="url(#g_${m.id})" stroke-width="2.4" stroke-dasharray="7 8">
        <path id="p1_${m.id}" d="M300 78 V142"><animate attributeName="stroke-dashoffset" from="30" to="0" dur="1.3s" repeatCount="indefinite"/></path>
        <path id="p2_${m.id}" d="M270 198 C210 225 165 245 140 266"><animate attributeName="stroke-dashoffset" from="30" to="0" dur="1.3s" repeatCount="indefinite"/></path>
        <path id="p3_${m.id}" d="M330 198 C390 225 435 245 460 266"><animate attributeName="stroke-dashoffset" from="30" to="0" dur="1.3s" repeatCount="indefinite"/></path>
        <path id="p4_${m.id}" d="M120 318 L80 364"/><path id="p5_${m.id}" d="M160 318 L295 364"/>
        <path id="p6_${m.id}" d="M440 318 L305 364"/><path id="p7_${m.id}" d="M480 318 L520 364"/>
      </g>
      <circle r="5" fill="${c1}"><animateMotion dur="2.2s" repeatCount="indefinite"><mpath href="#p1_${m.id}"/></animateMotion></circle>
      <circle r="5" fill="${c3}"><animateMotion dur="2.8s" repeatCount="indefinite" begin=".5s"><mpath href="#p2_${m.id}"/></animateMotion></circle>
      <circle r="5" fill="${c2}"><animateMotion dur="2.8s" repeatCount="indefinite" begin="1.2s"><mpath href="#p3_${m.id}"/></animateMotion></circle>
      <g transform="translate(300,52)"><rect x="-64" y="-24" width="128" height="48" rx="14" fill="${card}" stroke="${c1}" stroke-width="2"/><text y="5" text-anchor="middle" fill="${txt}" font-size="12" font-weight="800">INTERNET / WAN</text></g>
      <g transform="translate(300,170)"><rect x="-60" y="-28" width="120" height="56" rx="14" fill="${card}" stroke="${c1}" stroke-width="2.2"/><text y="5" text-anchor="middle" fill="${txt}" font-size="12" font-weight="800">R1 · CORE ROUTER</text></g>
      <g transform="translate(140,290)"><rect x="-56" y="-26" width="112" height="52" rx="12" fill="${card}" stroke="${c2}" stroke-width="2"/><text y="5" text-anchor="middle" fill="${txt}" font-size="11.5" font-weight="800">SW1 · ACCESS</text></g>
      <g transform="translate(460,290)"><rect x="-56" y="-26" width="112" height="52" rx="12" fill="${card}" stroke="${c2}" stroke-width="2"/><text y="5" text-anchor="middle" fill="${txt}" font-size="11.5" font-weight="800">SW2 · DIST</text></g>
      <g transform="translate(80,378)"><rect x="-38" y="-20" width="76" height="40" rx="10" fill="${card}" stroke="${c3}" stroke-width="1.8"/><text y="4" text-anchor="middle" fill="${txt}" font-size="11" font-weight="700">SRV</text></g>
      <g transform="translate(300,378)"><rect x="-44" y="-20" width="88" height="40" rx="10" fill="${card}" stroke="${c1}" stroke-width="1.8"/><text y="4" text-anchor="middle" fill="${txt}" font-size="11" font-weight="700">PC-VLAN10</text></g>
      <g transform="translate(520,378)"><rect x="-38" y="-20" width="76" height="40" rx="10" fill="${card}" stroke="${c2}" stroke-width="1.8"/><text y="4" text-anchor="middle" fill="${txt}" font-size="11" font-weight="700">LAP-B</text></g>
    </svg>`;
  }

  function metroMapSvg(m) {
    return `<svg viewBox="0 0 860 320" width="100%" style="height:auto;display:block" aria-label="نقشه مترو مسیر شبکه">
      <path d="M50 85 H360 L440 165 H810" fill="none" stroke="#0284c7" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M50 165 H390 L470 85 H810" fill="none" stroke="#dc2626" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M120 250 H740" fill="none" stroke="#16a34a" stroke-width="10" stroke-linecap="round"/>
      <line x1="405" y1="125" x2="405" y2="250" stroke="#0f172a" stroke-width="5" stroke-dasharray="5 4"/>
      ${[[90,85,'#0284c7','OSI & TCP/IP'],[230,85,'#0284c7','IPv4 & VLSM'],[405,125,'#0f172a','تقاطع CCNA'],[600,165,'#0284c7','OSPF & EIGRP'],[760,165,'#0284c7','آزمون CCNA'],
        [90,165,'#dc2626','STP / LACP'],[250,165,'#dc2626','VRF-Lite'],[580,85,'#dc2626','CCNP BGP'],[760,85,'#dc2626','SD-Access'],
        [160,250,'#16a34a','802.1X / ISE'],[405,250,'#16a34a','EVPN-VXLAN'],[670,250,'#16a34a','CCIE MPLS']
      ].map(([x,y,col,lbl]) => `
        <g transform="translate(${x},${y})">
          <circle r="12" fill="#fff" stroke="${col}" stroke-width="5"/>
          <rect x="-48" y="16" width="96" height="22" rx="6" fill="#0f172a"/>
          <text y="31" text-anchor="middle" fill="#fff" font-size="10.5" font-weight="800">${lbl}</text>
        </g>`).join('')}
    </svg>`;
  }

  function skillTreeSvg(m) {
    const a = m.vars.accent, b = m.vars.accent2, c = m.vars.accent3;
    return `<svg viewBox="0 0 640 360" width="100%" style="height:auto;display:block">
      <g stroke="rgba(255,255,255,.25)" stroke-width="4" fill="none">
        <path d="M320 46 L180 128"/><path d="M320 46 L460 128"/>
        <path d="M180 128 L100 220"/><path d="M180 128 L250 220"/>
        <path d="M460 128 L390 220"/><path d="M460 128 L540 220"/>
        <path d="M250 220 L320 310"/><path d="M390 220 L320 310"/>
      </g>
      ${[
        [320,46,b,'سطح ۱: مبانی OSI','✓ باز'],
        [180,128,b,'سطح ۲: Switching','✓ باز'],
        [460,128,a,'سطح ۳: Routing OSPF','★ فعال'],
        [100,220,c,'شاخه امنیت ISE','قفل ۲۲۰ XP'],
        [250,220,a,'CCNP ENCOR','مرحله بعد'],
        [390,220,c,'EVPN-VXLAN','تخصصی'],
        [540,220,c,'SD-WAN / API','اتوماسیون'],
        [320,310,a,'تاج CCIE / CCDE','★ نهایی']
      ].map(([x,y,col,t,sub]) => `
        <g transform="translate(${x},${y})">
          <circle r="24" fill="${m.vars.panel2}" stroke="${col}" stroke-width="3"/>
          <text y="-2" text-anchor="middle" fill="${m.vars.text}" font-size="10" font-weight="800">${t.split(':')[0]}</text>
          <text y="12" text-anchor="middle" fill="${col}" font-size="9" font-weight="800">${sub}</text>
          <text y="42" text-anchor="middle" fill="${m.vars.text}" font-size="11" font-weight="700">${t}</text>
        </g>`).join('')}
    </svg>`;
  }

  function socRadarSvg(m) {
    const a = m.vars.accent, b = m.vars.accent2, g = m.vars.accent3;
    return `<svg viewBox="0 0 380 380" width="100%" style="max-width:360px;margin:auto;display:block">
      <circle cx="190" cy="190" r="165" fill="none" stroke="${a}44" stroke-width="1.5" stroke-dasharray="6 4"/>
      <circle cx="190" cy="190" r="120" fill="none" stroke="${b}55" stroke-width="1.5"/>
      <circle cx="190" cy="190" r="75" fill="none" stroke="${g}66" stroke-width="2"/>
      <line x1="25" y1="190" x2="355" y2="190" stroke="${a}33"/><line x1="190" y1="25" x2="190" y2="355" stroke="${a}33"/>
      <path d="M190 190 L190 25 A165 165 0 0 1 320 90 Z" fill="${a}28">
        <animateTransform attributeName="transform" type="rotate" from="0 190 190" to="360 190 190" dur="4s" repeatCount="indefinite"/>
      </path>
      <circle cx="190" cy="190" r="24" fill="${m.vars.panel2}" stroke="${g}" stroke-width="2.5"/>
      <text x="190" y="194" text-anchor="middle" fill="#fff" font-size="10" font-weight="900">CORE</text>
      <circle cx="110" cy="115" r="7" fill="${a}"/><text x="110" y="102" text-anchor="middle" fill="#fff" font-size="10">802.1X</text>
      <circle cx="285" cy="135" r="7" fill="${b}"/><text x="285" y="122" text-anchor="middle" fill="#fff" font-size="10">ISE ZTNA</text>
      <circle cx="240" cy="285" r="7" fill="${g}"/><text x="240" y="305" text-anchor="middle" fill="#fff" font-size="10">NGFW IPS</text>
    </svg>`;
  }

  function aerospaceOrbitalSvg(m) {
    const a = m.vars.accent, g = m.vars.accent2;
    return `<svg viewBox="0 0 560 320" width="100%" style="height:auto;display:block">
      <ellipse cx="280" cy="190" rx="230" ry="90" fill="none" stroke="${a}44" stroke-width="1.5" stroke-dasharray="5 5"/>
      <ellipse cx="280" cy="190" rx="165" ry="60" fill="none" stroke="${g}44" stroke-width="1.5"/>
      <path id="orb1" d="M85 210 Q280 20 475 210" fill="none" stroke="${a}" stroke-width="2.6"/>
      <path id="orb2" d="M135 235 Q280 95 435 235" fill="none" stroke="${g}" stroke-width="2.2" stroke-dasharray="6 4"/>
      <circle r="5" fill="#fff"><animateMotion dur="2.6s" repeatCount="indefinite"><mpath href="#orb1"/></animateMotion></circle>
      <circle r="4.5" fill="${g}"><animateMotion dur="3.1s" repeatCount="indefinite"><mpath href="#orb2"/></animateMotion></circle>
      ${[[85,210,'TEHRAN-HQ'],[280,108,'SD-WAN HUB'],[475,210,'FRANKFURT-DC'],[135,235,'EDGE-01'],[435,235,'CLOUD-POP']].map(([x,y,t]) => `
        <g transform="translate(${x},${y})"><circle r="8" fill="${m.vars.panel2}" stroke="${a}" stroke-width="2.5"/><text y="22" text-anchor="middle" fill="#e2e8f0" font-size="10.5" font-weight="800">${t}</text></g>`).join('')}
    </svg>`;
  }

  function girihStarSvg(m) {
    const g = m.vars.accent2, c = m.vars.accent;
    return `<svg viewBox="0 0 360 360" width="100%" style="max-width:340px;margin:auto;display:block">
      <rect x="60" y="60" width="240" height="240" fill="none" stroke="${g}55" stroke-width="2"/>
      <rect x="60" y="60" width="240" height="240" fill="none" stroke="${c}77" stroke-width="2" transform="rotate(45 180 180)"/>
      <circle cx="180" cy="180" r="95" fill="none" stroke="${g}66" stroke-width="1.5" stroke-dasharray="6 4"/>
      <polygon points="180,68 206,154 292,180 206,206 180,292 154,206 68,180 154,154" fill="${c}18" stroke="${c}" stroke-width="2.2"/>
      <circle cx="180" cy="180" r="34" fill="${m.vars.panel}" stroke="${g}" stroke-width="2.5"/>
      <text x="180" y="185" text-anchor="middle" fill="#f8fafc" font-size="12" font-weight="900">FAM · CCIE</text>
      ${[[180,68,'f0'],[292,180,'f1'],[180,292,'f3'],[68,180,'f5']].map(([x,y,t]) => `
        <circle cx="${x}" cy="${y}" r="14" fill="${m.vars.panel2}" stroke="${g}" stroke-width="2"/><text x="${x}" y="${y+4}" text-anchor="middle" fill="#fff" font-size="10" font-weight="800">${t}</text>`).join('')}
    </svg>`;
  }

  /* ===== داشبوردهای متنوع بر اساس دستهٔ هر سبک ===== */
  function buildDashboard(m, sState) {
    const t = m.vars;
    const facCards = FAC.map((f, i) => `
      <div class="m-card" style="padding:14px;display:flex;align-items:center;justify-content:space-between;gap:10px">
        <div>
          <span class="m-tag">${esc(f.tag)}</span>
          <strong style="display:block;margin-top:4px">${esc(f.title)}</strong>
          <small style="color:${t.muted}">${f.lessons} درس · ${f.hrs}</small>
        </div>
        <button class="m-btn-pri" style="padding:7px 12px;font-size:12px">ورود ←</button>
      </div>`).join('');

    /* 1. داشبورد Apple Spatial / Bento (بدون سایدبار چپ/راست — داک بالایی یا پایینی + کارت‌های غول‌پیکر) */
    if (m.id === 2 || m.id === 6 || m.id === 17) {
      return `
        <div class="m-shell-topdock">
          <header class="m-pill-header">
            <strong>FAM · ${esc(m.enName)}</strong>
            <div class="m-seg-tabs">
              <button class="active">نمای کلی</button><button>۷ دانشکده</button><button>لابراتوار IOS</button>
              <button data-go="public">← صفحهٔ عمومی</button>
            </div>
            <span class="m-tag">🔥 ۱۲ روز پیاپی · سطح ۸</span>
          </header>
          <div class="m-container" style="padding:24px 0 80px;display:grid;gap:18px">
            <div class="m-bento-dash">
              <div class="m-card" style="grid-column:span 2;display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap">
                <div>
                  <span class="m-tag">ادامهٔ فوری یادگیری</span>
                  <h2 style="margin:8px 0 4px">CCNA · درس ۱۲: VLAN و Trunk 802.1Q</h2>
                  <p style="color:${t.muted};font-size:13.5px">۶۲٪ تکمیل‌شده · ۱۲ دقیقه تا پایان این جلسه</p>
                  <div style="display:flex;gap:10px;margin-top:14px"><button class="m-btn-pri">ادامهٔ درس ←</button><button class="m-btn-sec" data-go="public">نقشهٔ عمومی</button></div>
                </div>
                <div style="text-align:center;padding:16px 24px;border-radius:18px;background:${t.panel2};border:1px solid ${t.border}">
                  <strong style="font-size:32px;color:${t.accent}">۷۲٪</strong><small style="display:block;color:${t.muted}">کل مسیر CCNA</small>
                </div>
              </div>
              <div class="m-card"><h3>⚡ ترمینال سریع</h3><pre class="m-cli">R1# show ip ospf nei\n10.255.0.2 FULL/DR</pre></div>
              <div class="m-card"><h3>🎯 مأموریت امروز</h3><p style="font-size:13px;color:${t.muted};margin:6px 0">۲ از ۳ مأموریت تکمیل شده (+۴۰ XP)</p><button class="m-btn-pri" style="width:100%">اجرای آزمایشگاه ←</button></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px">${facCards}</div>
          </div>
          ${m.id === 17 || m.id === 6 ? `<div class="m-bottom-dock"><button class="active">🏠 خانه</button><button>📚 دانشکده‌ها</button><button>🧪 شبیه‌ساز</button><button data-go="public">🌐 صفحه عمومی</button></div>` : ''}
        </div>`;
    }

    /* 2. داشبورد CLI / tmux / Linear Command (پنل‌های ترمینالی و لیست فرمان‌محور) */
    if (m.id === 3 || m.id === 15) {
      return `
        <div class="m-container" style="padding:20px 0 48px;display:grid;gap:14px">
          <div class="m-card" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:14px 18px">
            <span class="m-mono" style="color:${t.accent}">fam-academy@lab:~/student-console$ status --faculty f1</span>
            <div style="display:flex;gap:8px"><button class="m-btn-sec" data-go="public">cd /public</button><button class="m-btn-pri">run-next-lab</button></div>
          </div>
          <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:14px">
            <div class="m-card">
              <div style="display:flex;justify-content:space-between;margin-bottom:10px"><strong>[PANE 01] مسیر فعال: CCNP / CCNA</strong><span class="m-tag">ACTIVE</span></div>
              <div style="display:grid;gap:8px">${FAC.slice(0,5).map((f,i)=>`<div style="display:flex;justify-content:space-between;padding:9px 12px;border:1px solid ${t.border};border-radius:8px;background:${t.panel2}"><span><b style="color:${t.accent}">0${i}</b> ${esc(f.title)}</span><small style="color:${t.muted}">${f.lessons} lessons</small></div>`).join('')}</div>
            </div>
            <div class="m-card">
              <div style="display:flex;justify-content:space-between;margin-bottom:10px"><strong>[PANE 02] IOS LIVE SESSION</strong><span class="m-tag">SSH READY</span></div>
              <pre class="m-cli" style="min-height:215px">R1# show ip bgp summary\nBGP router identifier 198.51.100.1\nAS 65100 · Neighbor 192.0.2.2 Up 4d12h (128 pfx)\n\nSW1# show interfaces trunk\nGi0/1  on  802.1q  trunking  99</pre>
            </div>
          </div>
        </div>`;
    }

    /* 3. داشبورد رَک سرور ۱۹ اینچ (تیغه‌های رک‌مونت با LED پورت‌ها) */
    if (m.id === 4) {
      return `
        <div class="m-container" style="padding:22px 0 48px;display:grid;gap:16px">
          <div class="m-card" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
            <div><span class="m-tag">RACK CABINET #01 · دانشجو</span><h2 style="margin-top:6px">میز کنترل سخت‌افزار و دروس رَک‌مونت</h2></div>
            <button class="m-btn-sec" data-go="public">← بازگشت به صفحهٔ عمومی</button>
          </div>
          <div class="m-rack-cabinet">
            ${FAC.map((f, i) => `
              <div class="m-rack-unit">
                <span class="m-u-num">${i+1}U</span>
                <div class="m-leds"><i class="on"></i><i class="on"></i><i class="${i<3?'on':'warn'}"></i><i></i></div>
                <div style="flex:1"><strong>${esc(f.tag)} — ${esc(f.title)}</strong><small style="display:block;color:${t.muted}">${f.lessons} ماژول · ${f.hrs}</small></div>
                <button class="m-btn-pri" style="padding:7px 14px;font-size:12px">${i===1?'ادامهٔ جلسه ←':'باز کردن'}</button>
              </div>`).join('')}
          </div>
        </div>`;
    }

    /* 4. داشبورد بوم دوپارچه روز/شب (مدل ۱۰) یا کانبان (مدل ۱۶) */
    if (m.id === 10 || m.id === 16) {
      if (m.id === 16) {
        const cols = [
          ['برای امروز', FAC.slice(0,2)],
          ['در حال یادگیری', FAC.slice(2,4)],
          ['پروژه و تکمیل‌شده', FAC.slice(4,7)]
        ];
        return `
          <div class="m-container" style="padding:22px 0 48px;display:grid;gap:16px">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
              <div><h2>برد کانبان پیشرفت دانشجو</h2><small style="color:${t.muted}">وضعیت تمام ۷ دانشکده در یک نگاه</small></div>
              <button class="m-btn-pri" data-go="public">← صفحهٔ عمومی</button>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px">
              ${cols.map(([title, list]) => `
                <div class="m-card" style="background:${t.bg2}">
                  <h3 style="margin-bottom:12px">${title} (${list.length})</h3>
                  <div style="display:grid;gap:10px">${list.map(f => `<div class="m-card" style="padding:14px"><span class="m-tag">${esc(f.tag)}</span><strong style="display:block;margin:6px 0">${esc(f.title)}</strong><button class="m-btn-sec" style="width:100%">شروع ←</button></div>`).join('')}</div>
                </div>`).join('')}
            </div>
          </div>`;
      }
      return `
        <div style="display:grid;grid-template-columns:1fr 1fr;min-height:85vh">
          <div style="padding:26px;background:#ffffff;color:#0f172a;display:grid;gap:14px;align-content:start">
            <div style="display:flex;justify-content:space-between;align-items:center"><span class="m-tag">دفتر مطالعه روشن</span><button class="m-btn-sec" data-go="public">← صفحه عمومی</button></div>
            <h2>جلسه ۱۲: VLAN و Trunking</h2>
            <p style="color:#475569;line-height:1.9">متون آموزشی در نیمهٔ روشن با کنتراست کاغذی قرار دارند تا چشم خسته نشود، و همزمان آزمایشگاه و توپولوژی در نیمهٔ تیرهٔ روبه‌رو فعال است.</p>
            ${FAC.slice(0,4).map(f => `<div style="padding:12px;border:1px solid #e2e8f0;border-radius:12px;display:flex;justify-content:space-between"><b>${esc(f.title)}</b><span style="color:#2563eb">${f.lessons} درس</span></div>`).join('')}
          </div>
          <div style="padding:26px;background:#0b1324;color:#e2e8f0;display:grid;gap:16px;align-content:start">
            <span style="color:#00d4ff;font-weight:800;font-size:12px">بوم آزمایشگاه تیره (LIVE CANVAS)</span>
            ${flagshipTopologySvg({...m, vars:{...m.vars, text:'#e2e8f0', panel2:'#121d36', accent:'#00d4ff', accent2:'#3b82f6', accent3:'#34d399'}})}
            <pre class="m-cli">SW1# show interfaces trunk\nGi0/1  on  802.1q  trunking  99</pre>
          </div>
        </div>`;
    }

    /* 5. داشبورد پیش‌فرض شیک (با سایدبار کناری + حلقه پیشرفت + مأموریت‌ها) */
    return `
      <div class="m-dash-grid">
        <aside class="m-dash-side">
          <div style="padding:6px 10px 14px;font-weight:900;font-size:16px">FAM <span style="color:${t.accent}">Academy</span></div>
          <button class="m-snav active">خانه داشبورد</button>
          <button class="m-snav">۷ دانشکده من</button>
          <button class="m-snav">آزمایشگاه شبیه‌ساز</button>
          <button class="m-snav">آزمون تعیین سطح</button>
          <button class="m-snav" data-go="public">← بازگشت به صفحهٔ عمومی</button>
          ${m.id === 20 ? `<div class="m-card" style="margin-top:auto;text-align:center"><small>تایمر پومودورو تمرکز</small><strong style="display:block;font-size:24px;color:${t.accent};margin:6px 0">۲۵:۰۰</strong><button class="m-btn-pri" style="width:100%">شروع جلسه</button></div>` : ''}
        </aside>
        <div style="padding:22px;display:grid;gap:16px;align-content:start">
          <div class="m-card" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px">
            <div>
              <span class="m-tag">${esc(m.badge)} · مسیر فعال</span>
              <h2 style="margin:8px 0 4px">CCNA · درس ۱۲: VLAN و Trunk 802.1Q</h2>
              <p style="color:${t.muted};font-size:13.5px">۱۲ دقیقه تا پایان درس · پیشرفت کل: ۷۲٪</p>
              <div style="display:flex;gap:10px;margin-top:12px"><button class="m-btn-pri">ادامهٔ درس ←</button><button class="m-btn-sec" data-go="public">تغییر دانشکده</button></div>
            </div>
            <div style="width:104px;height:104px;border-radius:50%;border:8px solid ${t.accent};display:grid;place-items:center;text-align:center">
              <div><strong style="font-size:20px">۷۲٪</strong><small style="display:block;font-size:10px;color:${t.muted}">CCNA</small></div>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px">
            <div class="m-card"><h3>🎯 مأموریت امروز</h3><p style="font-size:13px;color:${t.muted};margin:8px 0">۱ درس + ۱ لاب IOS + ۵ مرور</p><button class="m-btn-pri" style="width:100%">ثبت +۲۰ XP</button></div>
            <div class="m-card"><h3>🧪 ترمینال سریع</h3><pre class="m-cli" style="margin-top:8px">R1# show ip ospf nei\n10.255.0.2 FULL/DR</pre></div>
            <div class="m-card"><h3>🧭 قدم بعدی</h3><p style="font-size:13px;color:${t.muted};margin:8px 0">آماده‌سازی سناریوی OSPF Multi-Area</p><button class="m-btn-sec" style="width:100%">شروع لاب ←</button></div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px">${facCards}</div>
        </div>
      </div>`;
  }

  /* ===== ۲۰ صفحهٔ عمومی کاملاً متمایز ===== */
  function buildPublic(m) {
    const t = m.vars;
    const cards4 = FAC.slice(0, 4).map(f => `
      <article class="m-card m-course-card">
        <span class="m-tag">${esc(f.tag)}</span>
        <h3 style="margin:10px 0 6px">${esc(f.title)}</h3>
        <p style="font-size:13.5px;color:${t.muted};line-height:1.85">${f.lessons} درس تعاملی · ${f.hrs}</p>
        <button class="m-btn-pri" data-go="dashboard" style="margin-top:12px;width:100%">ورود به دوره ←</button>
      </article>`).join('');

    /* --- ۱: Live Topology Flagship --- */
    if (m.id === 1) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>FAM <span style="color:${t.accent}">Academy</span></strong><div class="m-nav-links"><button class="active">خانه</button><button>۷ دانشکده</button><button data-go="dashboard">داشبورد</button></div><button class="m-btn-pri" data-go="dashboard">شروع رایگان ←</button></div></header>
        <section class="m-container m-hero-2col">
          <div>
            <span class="m-tag">● آکادمی تخصصی شبکه و سیسکو</span>
            <h1 class="m-h1">مسیر شبکه، از <span style="color:${t.accent}">اولین پکت</span> تا <span style="color:${t.accent2}">گواهی CCNP</span></h1>
            <p class="m-lead">یادگیری شبکه اینجا به یک نقشهٔ زنده تبدیل می‌شود: توپولوژی واقعی، آزمایشگاه IOS و داشبوردی که همیشه می‌دانی کجایی.</p>
            <div class="m-actions"><button class="m-btn-pri" data-go="dashboard">ورود به داشبورد ←</button><button class="m-btn-sec">۷ دانشکده</button></div>
          </div>
          <div class="m-card" style="position:relative">${flagshipTopologySvg(m)}<pre class="m-cli" style="margin-top:10px">R1# show ip ospf neighbor -> FULL/DR (2ms)</pre></div>
        </section>
        <section class="m-container" style="padding-bottom:54px"><div class="m-grid-4">${cards4}</div></section>`;
    }

    /* --- ۲: Apple Spatial Minimal (ناوبری کپسولی وسط + هیرو متمرکز + کارت‌های سفید ابریشمی) --- */
    if (m.id === 2) {
      return `
        <div style="padding:18px 0"><nav class="m-floating-pill"><strong>FAM Academy</strong><button class="active">مسیرها</button><button>آزمایشگاه</button><button data-go="dashboard">داشبورد دانشجو ←</button></nav></div>
        <section class="m-container" style="text-align:center;padding:34px 0 48px">
          <span class="m-tag">طراحی مینیمال اپل · روشن و شفاف</span>
          <h1 class="m-h1" style="max-width:18ch;margin:16px auto">مهندسی شبکه با شفافیت مطلق.</h1>
          <p class="m-lead" style="margin:0 auto 24px;max-width:54ch">بدون منوهای پیچیده و شلوغی اضافه؛ از مبانی IPv4 تا معماری CCDE در ۷ دانشکدهٔ دقیق و آرام.</p>
          <div style="display:flex;justify-content:center;gap:12px;margin-bottom:32px"><button class="m-btn-pri" data-go="dashboard">شروع رایگان ←</button><button class="m-btn-sec">مشاهدهٔ سرفصل‌ها</button></div>
          <div class="m-card" style="max-width:860px;margin:0 auto;padding:24px">${flagshipTopologySvg(m)}</div>
          <div class="m-grid-4" style="margin-top:24px;text-align:right">${cards4}</div>
        </section>`;
    }

    /* --- ۳: CLI Workbench (هدر لینوکسی + ترمینال دوپنلی در قلب هیرو) --- */
    if (m.id === 3) {
      return `
        <header style="border-bottom:1px solid ${t.border};padding:12px 20px;display:flex;justify-content:space-between;align-items:center">
          <span class="m-mono" style="color:${t.accent}">~/fam-academy $ whoami -> network-engineer</span>
          <div style="display:flex;gap:8px"><button class="m-btn-sec">~/courses</button><button class="m-btn-pri" data-go="dashboard">./open-dashboard.sh</button></div>
        </header>
        <section class="m-container" style="padding:28px 0 54px;display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:stretch">
          <div class="m-card" style="display:flex;flex-direction:column;justify-content:space-between">
            <div>
              <span class="m-mono" style="color:${t.accent2}">[MODE: CLI-FIRST ACADEMY]</span>
              <h1 class="m-h1" style="font-size:clamp(26px,3.6vw,42px);margin:14px 0">تسلط بر Cisco IOS با خط فرمان زنده</h1>
              <p class="m-lead">اینجا به جای حفظ‌کردن اسلایدها، مستقیم روی روتر و سوییچ تایپ می‌کنی و خروجی واقعی می‌گیری.</p>
            </div>
            <div style="display:flex;gap:10px;margin-top:20px"><button class="m-btn-pri" data-go="dashboard">شروع در داشبورد CLI ←</button></div>
          </div>
          <div class="m-card">
            <pre class="m-cli" style="min-height:260px">R1# configure terminal\nR1(config)# router ospf 1\nR1(config-router)# network 10.0.0.0 0.255.255.255 area 0\nR1# show ip route ospf\nO    10.20.0.0/24 [110/2] via 10.12.0.2, Gi0/0\n\n[✓] Adjacency FULL · Ready for CCNP Lab</pre>
          </div>
        </section>
        <section class="m-container" style="padding-bottom:48px"><div class="m-grid-4">${cards4}</div></section>`;
    }

    /* --- ۴: 19" Server Rack Studio (کابینت سخت‌افزاری رَک سرور) --- */
    if (m.id === 4) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>FAM · 19" RACK LAB</strong><button class="m-btn-pri" data-go="dashboard">ورود به کابینت دانشجو ←</button></div></header>
        <section class="m-container" style="padding:28px 0 54px;display:grid;grid-template-columns:.95fr 1.05fr;gap:24px;align-items:start">
          <div>
            <span class="m-tag">HARDWARE RACK ARCHITECTURE</span>
            <h1 class="m-h1">هر دانشکده، یک ماژول <span style="color:${t.accent}">رک‌مونت واقعی</span></h1>
            <p class="m-lead">ظاهری کاملاً سخت‌افزاری با پورت‌های LED سبز و کهربایی؛ از 1U مبانی تا 7U معماری CCDE.</p>
            <div class="m-actions"><button class="m-btn-pri" data-go="dashboard">روشن‌کردن تجهیزات ←</button></div>
          </div>
          <div class="m-rack-cabinet">
            ${FAC.map((f,i)=>`<div class="m-rack-unit"><span class="m-u-num">${i+1}U</span><div class="m-leds"><i class="on"></i><i class="on"></i><i class="${i<2?'on':'warn'}"></i></div><div style="flex:1"><b>${esc(f.title)}</b><small style="display:block;color:${t.muted}">${f.lessons} ماژول</small></div><button class="m-btn-sec" data-go="dashboard" style="padding:5px 10px;font-size:11.5px">پچ ←</button></div>`).join('')}
          </div>
        </section>`;
    }

    /* --- ۵: Swiss Metro Transit Map (نقشه کامل خطوط مترو) --- */
    if (m.id === 5) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>FAM METRO TRANSIT</strong><div style="display:flex;gap:8px"><span class="m-tag" style="color:#0284c7">خط آبی: CCNA</span><span class="m-tag" style="color:#dc2626">خط قرمز: CCNP</span><span class="m-tag" style="color:#16a34a">خط سبز: CCIE</span></div><button class="m-btn-pri" data-go="dashboard">داشبورد سفر ←</button></div></header>
        <section class="m-container" style="padding:30px 0 54px;display:grid;gap:22px">
          <div style="display:flex;justify-content:space-between;align-items:end;flex-wrap:wrap;gap:14px">
            <div><h1 class="m-h1" style="margin:0">نقشهٔ متروی یادگیری شبکه</h1><p class="m-lead" style="margin:6px 0 0">ایستگاه فعلی خود را روی خطوط رنگی پیدا کنید و مستقیم حرکت کنید.</p></div>
            <button class="m-btn-pri" data-go="dashboard">شروع از ایستگاه من ←</button>
          </div>
          <div class="m-card" style="padding:20px">${metroMapSvg(m)}</div>
          <div class="m-grid-4">${cards4}</div>
        </section>`;
    }

    /* --- ۶: Modular Bento OS (گرید ۶ کاشی بنتو بالای صفحه) --- */
    if (m.id === 6) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>FAM Bento OS</strong><button class="m-btn-pri" data-go="dashboard">باز کردن داشبورد ←</button></div></header>
        <section class="m-container" style="padding:26px 0 54px">
          <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px">
            <div class="m-card" style="grid-column:span 2;grid-row:span 2;display:flex;flex-direction:column;justify-content:space-between">
              <div><span class="m-tag">BENTO MODULAR SYSTEM</span><h1 class="m-h1" style="font-size:32px;margin:12px 0">آکادمی شبکه، به سادگی سیستم‌عامل مدرن</h1><p class="m-lead">تمام ابزارها، مسیرها و آزمایشگاه‌ها در کاشی‌های منظم و مستقل.</p></div>
              <div style="display:flex;gap:10px;margin-top:16px"><button class="m-btn-pri" data-go="dashboard">ورود به داشبورد ←</button></div>
            </div>
            <div class="m-card" style="grid-column:span 2">${flagshipTopologySvg(m)}</div>
            <div class="m-card"><strong>۷ دانشکده</strong><p style="font-size:13px;color:${t.muted};margin-top:4px">مبانی تا CCDE</p></div>
            <div class="m-card"><strong>۹۴٪ قبولی</strong><p style="font-size:13px;color:${t.muted};margin-top:4px">آزمون‌های نگهبان</p></div>
          </div>
          <div class="m-grid-4" style="margin-top:16px">${cards4}</div>
        </section>`;
    }

    /* --- ۷: CAD Engineering Sheet (قاب نقشه مهندسی اتوکد) --- */
    if (m.id === 7) {
      return `
        <div class="m-container" style="padding:20px 0 50px">
          <div style="border:2px solid ${t.accent};padding:18px;position:relative">
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px dashed ${t.border};padding-bottom:12px;margin-bottom:18px;flex-wrap:wrap;gap:10px">
              <span class="m-mono">DWG NO: FAM-NET-07 | SCALE 1:1 | REV 5.0</span>
              <div style="display:flex;gap:8px"><button class="m-btn-pri" data-go="dashboard">OPEN INSPECTOR ←</button></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1.1fr;gap:20px;align-items:center">
              <div><span class="m-mono" style="color:${t.accent2}">// ARCHITECTURAL NETWORK DRAFT</span><h1 class="m-h1" style="margin:10px 0">نقشهٔ مهندسی آموزش شبکه و سیسکو</h1><p class="m-lead">محیط فنی با خطوط راهنما، ابعاد دقیق و شماتیک‌های مهندسی برای طراحی واقعی زیرساخت.</p></div>
              <div class="m-card">${flagshipTopologySvg(m)}</div>
            </div>
            <div class="m-grid-4" style="margin-top:20px">${cards4}</div>
          </div>
        </div>`;
    }

    /* --- ۸: Vertical Fiber Packet Story (تایم‌لاین عمودی درخشان وسط صفحه) --- */
    if (m.id === 8) {
      const steps = [
        ['فاز ۰۱: اولین پکت', 'آشنایی با مدل OSI، کپسوله‌سازی و آدرس‌دهی IPv4/VLSM'],
        ['فاز ۰۲: سوییچینگ لایه ۲', 'پیکربندی VLAN، Trunk 802.1Q، RSTP و تجمیع لینک LACP'],
        ['فاز ۰۳: قلب مسیریابی', 'OSPF Multi-Area، Redistribution و الگوریتم انتخاب مسیر BGP'],
        ['فاز ۰۴: معماری CCIE & CCDE', 'MPLS L3VPN، Segment Routing و طراحی دامنه‌های شکست']
      ];
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>FAM FIBER STORY</strong><button class="m-btn-pri" data-go="dashboard">داشبورد سفر ←</button></div></header>
        <section class="m-container" style="padding:34px 0 54px;text-align:center">
          <h1 class="m-h1">سفر عمودی یک پکت از مبانی تا CCDE</h1>
          <p class="m-lead" style="margin:0 auto 28px">ستون فیبر نوری مسیر شما را گام‌به‌گام به پایین هدایت می‌کند.</p>
          <div style="max-width:760px;margin:0 auto;position:relative;padding-right:28px;border-right:3px solid ${t.accent};text-align:right;display:grid;gap:18px">
            ${steps.map(([ti, de], i) => `
              <div class="m-card" style="position:relative">
                <span style="position:absolute;right:-39px;top:22px;width:18px;height:18px;border-radius:50%;background:${t.accent};border:3px solid ${t.bg}"></span>
                <span class="m-tag">مرحله ${i+1}</span>
                <h3 style="margin:6px 0">${ti}</h3>
                <p style="color:${t.muted};font-size:13.5px">${de}</p>
              </div>`).join('')}
          </div>
          <button class="m-btn-pri" data-go="dashboard" style="margin-top:24px">شروع سفر در داشبورد ←</button>
        </section>`;
    }

    /* --- ۹: Neo-Brutalist Zine --- */
    if (m.id === 9) {
      return `
        <header style="border-bottom:3px solid #111827;background:#fff;padding:14px 20px"><div class="m-container m-nav-in"><strong style="font-size:20px">FAM // ZINE</strong><button class="m-btn-pri" data-go="dashboard">بزن بریم داشبورد →</button></div></header>
        <section class="m-container" style="padding:32px 0 54px;display:grid;gap:22px">
          <div class="m-card" style="background:#a3e635;color:#111827;padding:30px">
            <span style="display:inline-block;background:#111827;color:#fff;padding:4px 10px;font-weight:900;font-size:12px;transform:rotate(-2deg)">HOT · CCNA TO CCDE</span>
            <h1 style="font-size:clamp(30px,5vw,56px);font-weight:900;line-height:1.25;margin:14px 0">شبکه یاد بگیر، بدون حوصله‌سربری!</h1>
            <p style="font-size:16px;font-weight:700;max-width:52ch">۲۹ درس تعاملی، شبیه‌ساز زنده IOS و ۷ دانشکده با کنتراست حداکثری و دسترسی برق‌آسا.</p>
            <button class="m-btn-pri" data-go="dashboard" style="margin-top:16px;background:#111827;color:#fff">ورود به داشبورد ←</button>
          </div>
          <div class="m-grid-4">${cards4}</div>
        </section>`;
    }

    /* --- ۱۰: Dual Split Studio (نمای دوپارچه سفید + تیره) --- */
    if (m.id === 10) {
      return `
        <div style="display:grid;grid-template-columns:1fr 1fr;min-height:100vh">
          <div style="padding:38px 34px;background:#ffffff;color:#0f172a;display:flex;flex-direction:column;justify-content:center;gap:18px">
            <span class="m-tag">سمت مطالعه و مسیر (روشن)</span>
            <h1 class="m-h1" style="margin:0">بهترینِ هر دو دنیا: جزوهٔ روشن کنار لابراتوار شبانه</h1>
            <p style="color:#475569;line-height:1.9">متن‌های فارسی در سمت راست با وضوح کاغذ سفید خوانده می‌شوند و توپولوژی و CLI همیشه در سمت چپ آماده‌اند.</p>
            <div style="display:flex;gap:10px"><button class="m-btn-pri" data-go="dashboard">ورود به داشبورد ←</button></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">${FAC.slice(0,4).map(f=>`<div style="padding:12px;border:1px solid #e2e8f0;border-radius:12px"><b>${esc(f.tag)}</b><small style="display:block;color:#475569">${esc(f.title)}</small></div>`).join('')}</div>
          </div>
          <div style="padding:34px;background:#0b1324;color:#e2e8f0;display:flex;flex-direction:column;justify-content:center;gap:16px">
            <span style="color:#00d4ff;font-weight:800;font-size:12px">بوم زندهٔ شبکه (تیره)</span>
            ${flagshipTopologySvg({...m, vars:{...m.vars, text:'#e2e8f0', panel2:'#121d36', accent:'#00d4ff', accent2:'#3b82f6', accent3:'#34d399'}})}
            <pre class="m-cli">R1# show ip ospf neighbor -> FULL/DR</pre>
          </div>
        </div>`;
    }

    /* --- ۱۱: RPG Skill-Tree Academy --- */
    if (m.id === 11) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>⚔ FAM SKILL-TREE</strong><span class="m-tag">LEVEL 8 · ۲۴۵۰ XP</span><button class="m-btn-pri" data-go="dashboard">ادامهٔ کوئست ←</button></div></header>
        <section class="m-container" style="padding:28px 0 54px;text-align:center">
          <h1 class="m-h1">درخت مهارت مهندسی سیسکو</h1>
          <p class="m-lead" style="margin:0 auto 20px">هر شاخه را با آزمون و آزمایشگاه باز کن و امتیاز XP بگیر.</p>
          <div class="m-card" style="padding:20px">${skillTreeSvg(m)}</div>
          <div class="m-grid-4" style="margin-top:20px;text-align:right">${cards4}</div>
        </section>`;
    }

    /* --- ۱۲: Swiss Editorial Magazine --- */
    if (m.id === 12) {
      return `
        <header style="border-bottom:1px solid ${t.border};padding:18px 0"><div class="m-container m-nav-in"><strong style="font-size:20px">فصلنامهٔ مهندسی شبکه FAM</strong><button class="m-btn-pri" data-go="dashboard">میز مطالعهٔ دانشجو ←</button></div></header>
        <section class="m-container" style="padding:36px 0 54px">
          <div style="border-bottom:2px solid #1c1917;padding-bottom:24px;margin-bottom:24px;display:grid;grid-template-columns:1.2fr .8fr;gap:24px;align-items:end">
            <h1 style="font-size:clamp(32px,4.5vw,52px);font-weight:900;line-height:1.3">۰۱ — معماری شبکه‌های سازمانی، از مبانی تا CCDE</h1>
            <div><p class="m-lead">طراحی مجله‌ای و آرام بر روی کاغذ کرم گرم؛ بدون خیرگی صفحه، مناسب مطالعهٔ عمیق مفاهیم و پروتکل‌ها.</p><button class="m-btn-pri" data-go="dashboard" style="margin-top:12px">شروع مطالعه ←</button></div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">
            ${FAC.slice(0,3).map((f,i)=>`<div style="border-top:2px solid ${t.accent};padding-top:14px"><span style="font-size:28px;font-weight:900;color:${t.accent}">۰${i+1}</span><h3 style="margin:6px 0">${esc(f.title)}</h3><p style="font-size:13.5px;color:${t.muted}">${f.lessons} درس تخصصی در ${f.hrs}</p></div>`).join('')}
          </div>
        </section>`;
    }

    /* --- ۱۳: Aerospace HUD --- */
    if (m.id === 13) {
      return `
        <div style="background:${t.panel};border-bottom:1px solid ${t.border};padding:7px 18px;font-size:11.5px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px" class="m-mono">
          <span>TELEMETRY: NOMINAL</span><span>OSPF-CORE: FULL</span><span>SDWAN-LOSS: 0.00%</span><span>FACULTIES: 7 ONLINE</span>
        </div>
        <section class="m-container" style="padding:30px 0 54px;display:grid;gap:20px">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px">
            <div><h1 class="m-h1" style="margin:0">کنترل مأموریت شبکه‌های WAN و Core</h1><p class="m-lead" style="margin:6px 0 0">دقت تله‌متری اتاق کنترل برای دوره‌های CCNP، SD-WAN و CCDE.</p></div>
            <button class="m-btn-pri" data-go="dashboard">ورود به کنسول دانشجو ←</button>
          </div>
          <div class="m-card">${aerospaceOrbitalSvg(m)}</div>
          <div class="m-grid-4">${cards4}</div>
        </section>`;
    }

    /* --- ۱۴: Persian Girih Architecture --- */
    if (m.id === 14) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>آکادمی شبکه و سیسکو · FAM</strong><button class="m-btn-pri" data-go="dashboard">ورود به تالار یادگیری ←</button></div></header>
        <section class="m-container m-hero-2col">
          <div>
            <span class="m-tag">هویت بومی ایرانی · لاجورد و فیروزه</span>
            <h1 class="m-h1">تلفیق هندسهٔ گره‌چینی ایرانی با <span style="color:${t.accent}">مهندسی مدرن سیسکو</span></h1>
            <p class="m-lead">گره‌های هندسی به‌عنوان استعاره‌ای از نودهای شبکه؛ با وقار، متقارن و اصیل.</p>
            <div class="m-actions"><button class="m-btn-pri" data-go="dashboard">شروع مسیر ←</button></div>
          </div>
          <div class="m-card">${girihStarSvg(m)}</div>
        </section>
        <section class="m-container" style="padding-bottom:54px"><div class="m-grid-4">${cards4}</div></section>`;
    }

    /* --- ۱۵: Linear ⌘K Command Palette --- */
    if (m.id === 15) {
      return `
        <header style="border-bottom:1px solid #27272a;padding:14px 20px"><div class="m-container m-nav-in"><strong>FAM · Linear</strong><button class="m-btn-pri" data-go="dashboard">داشبورد ⌘D ←</button></div></header>
        <section class="m-container" style="padding:46px 0 54px;text-align:center">
          <h1 class="m-h1" style="max-width:18ch;margin:0 auto 12px">سریع‌ترین مسیر رسیدن به هر مبحث شبکه</h1>
          <p class="m-lead" style="margin:0 auto 24px">با یک دستور ⌘K یا کلیک، مستقیم به درس، آزمایشگاه یا دانشکدهٔ مورد نظر بپرید.</p>
          <div class="m-card" style="max-width:680px;margin:0 auto;text-align:right;padding:14px">
            <div style="display:flex;align-items:center;gap:10px;border-bottom:1px solid #27272a;padding-bottom:10px;margin-bottom:10px">
              <span style="color:${t.accent}">⌘K</span>
              <input id="cmdk-input" type="search" placeholder="بنویسید: OSPF, BGP, EVPN, CCNA..." style="background:transparent;border:0;color:#fff;outline:0;width:100%;font-size:14px">
            </div>
            <div id="cmdk-list" style="display:grid;gap:6px">
              ${FAC.slice(0,5).map(f=>`<div class="cmdk-row" data-go="dashboard" style="padding:9px 12px;border-radius:8px;background:#16161f;display:flex;justify-content:space-between;cursor:pointer"><span>${esc(f.tag)} — ${esc(f.title)}</span><small style="color:${t.muted}">Enter ↵</small></div>`).join('')}
            </div>
          </div>
        </section>`;
    }

    /* --- ۱۶: Interactive Kanban Roadmap --- */
    if (m.id === 16) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>FAM Curriculum Board</strong><button class="m-btn-pri" data-go="dashboard">برد شخصی من ←</button></div></header>
        <section class="m-container" style="padding:30px 0 54px">
          <h1 class="m-h1" style="margin-bottom:16px">نقشهٔ راه ۴ ستونه از دانشکده ۰ تا CCDE</h1>
          <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px">
            ${[['شروع (f0)', FAC.slice(0,1)], ['هسته CCNA (f1-f2)', FAC.slice(1,3)], ['حرفه‌ای CCNP (f3-f4)', FAC.slice(3,5)], ['معماری خبره (f5-f6)', FAC.slice(5,7)]].map(([col, list])=>`
              <div class="m-card" style="background:${t.bg2}">
                <h3 style="margin-bottom:12px;font-size:15px">${col}</h3>
                <div style="display:grid;gap:10px">${list.map(f=>`<div class="m-card" style="padding:14px"><span class="m-tag">${esc(f.tag)}</span><strong style="display:block;margin:6px 0">${esc(f.title)}</strong><small style="color:${t.muted}">${f.lessons} درس</small><button class="m-btn-pri" data-go="dashboard" style="width:100%;margin-top:10px;padding:7px">ورود ←</button></div>`).join('')}</div>
              </div>`).join('')}
          </div>
        </section>`;
    }

    /* --- ۱۷: Glass Desktop OS + Bottom Dock --- */
    if (m.id === 17) {
      return `
        <section class="m-container" style="padding:28px 0 90px;display:grid;gap:18px">
          <div style="display:flex;justify-content:space-between;align-items:center"><strong>FAM Glass Desktop OS</strong><button class="m-btn-pri" data-go="dashboard">ورود به داشبورد ←</button></div>
          <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:18px">
            <div class="m-card" style="backdrop-filter:blur(22px)"><div style="display:flex;gap:6px;margin-bottom:12px"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><small style="margin-inline-start:auto;color:${t.muted}">Window: Topology.app</small></div>${flagshipTopologySvg(m)}</div>
            <div style="display:grid;gap:16px">
              <div class="m-card" style="backdrop-filter:blur(22px)"><h2>آکادمی پنجره‌ای شیشه‌ای</h2><p class="m-lead" style="font-size:14px">رابطی شبیه سیستم‌عامل دسکتاپ با پنجره‌های شیشه‌ای مات و داک پایین صفحه.</p><button class="m-btn-pri" data-go="dashboard" style="margin-top:10px">باز کردن محیط کار ←</button></div>
              <div class="m-card" style="backdrop-filter:blur(22px)"><pre class="m-cli">R1# show ip bgp summary -> 128 prefixes</pre></div>
            </div>
          </div>
        </section>
        <div class="m-bottom-dock"><button class="active">🌐 آکادمی</button><button data-go="dashboard">📊 داشبورد</button><button data-go="dashboard">🧪 ترمینال</button></div>`;
    }

    /* --- ۱۸: Zero-Trust SOC Radar --- */
    if (m.id === 18) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>🛡 FAM ZERO-TRUST SOC</strong><button class="m-btn-pri" data-go="dashboard">کنسول تحلیل‌گر ←</button></div></header>
        <section class="m-container m-hero-2col">
          <div>
            <span class="m-tag">SECURITY & ZERO-TRUST OPS</span>
            <h1 class="m-h1">آموزش امنیت شبکه با <span style="color:${t.accent}">رادار دفاعی زنده</span></h1>
            <p class="m-lead">ساختار الهام‌گرفته از مراکز SOC برای 802.1X، فایروال NGFW، Cisco ISE و تفکیک ترافیک.</p>
            <div class="m-actions"><button class="m-btn-pri" data-go="dashboard">ورود به SOC دانشجو ←</button></div>
          </div>
          <div class="m-card">${socRadarSvg(m)}</div>
        </section>
        <section class="m-container" style="padding-bottom:54px"><div class="m-grid-4">${cards4}</div></section>`;
    }

    /* --- ۱۹: Kinetic Cyber Arena (برش‌های مورب و شش‌ضلعی) --- */
    if (m.id === 19) {
      return `
        <header class="m-nav-glass"><div class="m-container m-nav-in"><strong>⚡ FAM CYBER ARENA</strong><button class="m-btn-pri" data-go="dashboard">ورود به آرنا ←</button></div></header>
        <section class="m-container" style="padding:32px 0 54px;display:grid;gap:24px">
          <div class="m-card" style="clip-path:polygon(0 0,100% 0,97% 100%,0 94%);padding:34px;background:linear-gradient(135deg,#140b2e,#25104d)">
            <span class="m-tag">HIGH-ENERGY CYBER ARENA</span>
            <h1 class="m-h1">چالش‌پذیر، پرانرژی و رقابتی</h1>
            <p class="m-lead">طراحی پویا با خطوط مورب و بج‌های شش‌ضلعی برای رقابت سالم و فتح مراحل CCNA تا CCIE.</p>
            <button class="m-btn-pri" data-go="dashboard" style="margin-top:12px">شروع رقابت در داشبورد ←</button>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:14px;justify-content:center">
            ${FAC.map(f=>`<div class="m-hex" data-go="dashboard" style="cursor:pointer"><b>${esc(f.tag)}</b><small>${esc(f.title)}</small></div>`).join('')}
          </div>
        </section>`;
    }

    /* --- ۲۰: Solarized Zen Study Studio --- */
    return `
      <header style="padding:22px 0"><div class="m-container m-nav-in"><strong>FAM · Zen Study</strong><button class="m-btn-pri" data-go="dashboard">اتاق تمرکز + پومودورو ←</button></div></header>
      <section class="m-container" style="max-width:780px;padding:30px 0 64px;display:grid;gap:22px;text-align:center">
        <span class="m-tag" style="margin:0 auto">SOLARIZED DEEP TEAL · ZERO NOISE</span>
        <h1 class="m-h1">فقط یک هدف: یادگیری عمیق و بدون حواس‌پرتی.</h1>
        <p class="m-lead" style="margin:0 auto">طراحی مینیمال سولارایزد مخصوص مطالعهٔ طولانی؛ یک کارت تمرکز، تایمر پومودورو و دسترسی مستقیم به ۷ دانشکده.</p>
        <div><button class="m-btn-pri" data-go="dashboard">شروع جلسهٔ ۲۵ دقیقه‌ای در داشبورد ←</button></div>
        <div style="display:grid;gap:10px;text-align:right;margin-top:12px">
          ${FAC.map(f=>`<div class="m-card" style="padding:14px 18px;display:flex;justify-content:space-between;align-items:center"><div><b>${esc(f.tag)}</b> — ${esc(f.title)}</div><button class="m-btn-sec" data-go="dashboard">مطالعه ←</button></div>`).join('')}
        </div>
      </section>`;
  }

  window.FAM_RENDERERS = { buildPublic, buildDashboard };
})();
