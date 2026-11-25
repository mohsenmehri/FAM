/* FAM Academy — طرح جامع آموزشی (CCNA تا Expert) — دادهٔ کامل برنامهٔ درسی */
window.FAM_CURR = {
meta: {
  title: 'طرح جامع آکادمی سیسکو؛ از CCNA تا سطح معماری و Expert',
  tagline: 'برنامهٔ آموزشی جامع · روزانه ۲ ساعت · زبان فارسی',
  intro: 'این آکادمی را به‌صورت یک دانشگاه تخصصی مهندسی شبکه طراحی می‌کنیم؛ دانشجو از سطح فعلی خود (آشنایی با شبکه و شروع CCNA) حرکت می‌کند و در نهایت توانایی طراحی، پیاده‌سازی، امنیت، اتوماسیون و معماری زیرساخت‌های بزرگ را به دست می‌آورد.',
  principle: 'هیچ مبحثی صرفاً برای حفظ کردن تدریس نمی‌شود. هر مبحث باید چهار خروجی داشته باشد:',
  outputs: [
    'درک مفهومی و شناخت پروتکل',
    'تسلط بر دستورات و پیکربندی',
    'اجرای آزمایشگاه و مشاهدهٔ رفتار واقعی شبکه',
    'توانایی عیب‌یابی و استفاده در پروژهٔ واقعی'
  ],
  specs: [['زمان روزانه','۲ ساعت'],['زمان هفتگی','۱۴ ساعت'],['زبان آموزش','فارسی + اصطلاحات انگلیسی'],['روش یادگیری','تئوری + لابراتوار + پروژه'],['مدت پیشنهادی کل','۶ تا ۸ سال']],
  totalNote: 'این زمان برای مسیر جامع چندشاخه‌ای و رسیدن به سطح Expert و معماری است؛ دریافت تمام مدارک سیسکو شرط فارغ‌التحصیلی نیست.',
  table9: [
    ['۰','ارزیابی و تکمیل مبانی','۱ ماه'],
    ['۱','Network Engineering Foundations','۳ ماه'],
    ['۲','CCNA 200-301','۵ ماه'],
    ['۳','مهندسی Routing & Switching','۶ ماه'],
    ['۴','CCNP Enterprise','۸ ماه'],
    ['۵','تخصص‌های پیشرفتهٔ سیسکو','۱۸ ماه'],
    ['۶','مسیرهای تخصصی مستقل','۱۸ تا ۳۰ ماه'],
    ['۷','CCIE در شاخهٔ منتخب','۱۲ تا ۲۴ ماه'],
    ['۸','CCDE و معماری زیرساخت','۱۲ تا ۱۸ ماه']
  ],
  tableNote: 'این جدول یک نقشهٔ آموزشی است، نه جمع ساده و اجباری تمام مدت‌ها؛ بعضی درس‌ها و شاخه‌ها هم‌زمان پیش می‌روند.',
  dailyPattern: [['مرور درس قبلی','۲۰ دقیقه','مرور مفاهیم، دستورات و اشتباهات'],['آموزش مفهومی','۳۵ دقیقه','درس جدید، پروتکل و تحلیل عملکرد'],['آزمایشگاه عملی','۵۰ دقیقه','پیکربندی، مشاهدهٔ Packet و عیب‌یابی'],['مستندسازی','۱۵ دقیقه','یادداشت، دستورات و گزارش آزمایشگاه']],
  dailyTotal: '۱۲۰ دقیقه در هر روز آموزشی',
  week: [['شنبه','درس جدید + لابراتوار'],['یکشنبه','درس جدید + لابراتوار'],['دوشنبه','درس جدید + لابراتوار'],['سه‌شنبه','درس جدید + لابراتوار'],['چهارشنبه','تکمیل درس و سناریو'],['پنجشنبه','پروژهٔ عملی و Troubleshooting'],['جمعه','آزمون هفتگی و مرور اشتباهات']],
  grades: [['آزمون مفهومی','۲۰٪',20],['دستورات و پیکربندی','۲۰٪',20],['آزمایشگاه عملی','۳۵٪',35],['پروژه و عیب‌یابی','۲۵٪',25]],
  pass: 'حداقل نمرهٔ قبولی: ۸۵ از ۱۰۰',
  passNote: 'برای پروژه‌های عملی، تکمیل تمام بخش‌های الزامی نیز ضروری است؛ نمرهٔ بالا جایگزین انجام پروژه نمی‌شود. مدارک رسمی سیسکو جداگانه و طبق استاندارد آزمون رسمی صادر می‌شوند؛ گواهی پایان هر دانشکده در آکادمی، مدرک داخلی آموزشی است و جایگزین مدرک Cisco نیست.',
  master: [
      {n:'۱',en:'Networking Fundamentals',fa:'مبانی شبکه',desc:'TCP/IP، OSI، Subnetting و پروتکل‌های پایه',to:'fnd-w1'},
      {n:'۲',en:'Cisco Entry / CCST',fa:'ورود به سیسکو — CCST',desc:'آشنایی با تجهیزات و عملیات پایه',to:'ccst-w1'},
      {n:'۳',en:'CCNA',fa:'CCNA 200-301',desc:'Routing، Switching، IP Services و Security',to:'f1-p1'},
      {n:'۴',en:'CCNP Specialization',fa:'تتخصص CCNP',desc:'انتخاب یک یا چند مسیر تخصصی — ENCOR و آزمون انتخابی',to:'f3-enc1'},
      {n:'۵',en:'Advanced Technologies',fa:'فناوری‌های پیشرفته',desc:'MPLS، BGP، VXLAN، SD-WAN، VPN و Automation',to:'f2-l1'},
      {n:'۶',en:'CCIE',fa:'CCIE',desc:'تسلط تخصصی و عملی در شاخهٔ انتخابی',to:'f5-l1'},
      {n:'۷',en:'CCDE',fa:'CCDE',desc:'طراحی شبکه‌های پیچیده در مقیاس بزرگ',to:'f6-d1'},
      {n:'۸',en:'Principal Network Architect',fa:'معمار ارشد شبکه',desc:'جایگاه شغلی معماری ارشد — نه یک مدرک واحد سیسکو',to:'f6-arch'}
    ],
    roadmap: [['سال اول','مبانی، CCNA و مهندسی شبکه'],['سال دوم','CCNP Enterprise و پروژه‌های سازمانی'],['سال سوم','Security و Service Provider'],['سال چهارم','Data Center و Wireless'],['سال پنجم','Collaboration و Automation'],['سال ششم','Cybersecurity و تکمیل تخصص‌ها'],['سال هفتم','آمادگی CCIE در شاخهٔ منتخب'],['سال هشتم','CCDE و معماری پیشرفته']],
  tools: [['Packet Tracer','آموزش مقدماتی و CCNA'],['PNETLab','آزمایشگاه تجهیزات شبکه'],['EVE-NG','سناریوهای پیشرفته'],['Cisco CML','شبیه‌سازی رسمی سیسکو'],['Wireshark','تحلیل Packet'],['GNS3','شبیه‌سازی و اتصال به محیط واقعی'],['Linux Ubuntu','سرویس‌ها و ابزارهای شبکه'],['Docker','سرویس‌های آزمایشگاهی'],['Python','اتوماسیون'],['GitHub','نگهداری پروژه‌ها'],['ELK / Grafana','مانیتورینگ و تحلیل']],
  law: 'هرجا امکانش باشد، رفتار پروتکل باید با Packet Capture یا خروجی واقعی CLI اثبات شود؛ صرفاً مشاهدهٔ تصویر توپولوژی کافی نیست.',
  resources: [['Cisco Learning Network','مسیرهای رسمی مدارک، سرفصل آزمون‌ها و منابع یادگیری'],['Cisco U','دوره‌های آموزشی، تمرین‌ها و مسیرهای آمادگی آزمون'],['Cisco Press','کتاب‌های مرجع، راهنمای رسمی آزمون و کتاب‌های تخصصی'],['Cisco Skills for All','دوره‌های مقدماتی و آموزش رایگان شبکه و امنیت']],
  ccnaNote: 'سیسکو اعلام کرده نسخهٔ ۱.۱ آزمون 200-301 تا ۲ فوریهٔ ۲۰۲۷ قابل برگزاری است و نسخهٔ ۲.۰ از ۳ فوریهٔ ۲۰۲۷ آغاز می‌شود؛ چون دورهٔ ما از انتهای ۲۰۲۶ شروع می‌شود و احتمالاً آزمون در سال ۲۰۲۷ خواهد بود، باید سرفصل و منابع را بر اساس نسخهٔ جدید تنظیم کنیم.',
  gradStandard: 'فارغ‌التحصیل نهایی باید بتواند: از شبکهٔ کوچک تا شبکهٔ چندصدشعبه‌ای را طراحی کند · Routing و Switching پیشرفته را اجرا کند · شبکه‌های MPLS و BGP را مهندسی کند · زیرساخت Data Center را طراحی کند · Firewall و VPN و NAC را پیاده‌سازی کند · VoIP و Wireless را مدیریت کند · با Python و API شبکه را اتوماتیک کند · سیستم‌های مانیتورینگ و امنیت بسازد · در سطح Expert عیب‌یابی کند · معماری کلان شبکه را با توجه به نیاز کسب‌وکار طراحی کند.'
},

/* ---------- دیاگرام‌های مشترک ---------- */
DIAGRAMS: {
osi: `<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="لایه‌های OSI و TCP/IP">
<defs><linearGradient id="og1" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#00d4ff"/><stop offset="1" stop-color="#3b82f6"/></linearGradient></defs>
<g font-family="Vazirmatn,sans-serif" font-size="12" text-anchor="middle">
${[7,6,5,4,3,2,1].map((n,i)=>`<rect x="40" y="${14+i*40}" width="240" height="34" rx="8" fill="${i%2?'#0e1b2e':'#12233c'}" stroke="#1e3a5f"/><text x="160" y="${36+i*40}" fill="#e6f7ff">L${n} · ${['Application','Presentation','Session','Transport','Network','Data Link','Physical'][i]}</text>`).join('')}
<rect x="360" y="54" width="240" height="154" rx="10" fill="none" stroke="url(#og1)" stroke-width="2" stroke-dasharray="6 5"/>
<text x="480" y="46" fill="#00d4ff" font-size="13" font-weight="bold">مدل TCP/IP</text>
<text x="480" y="230" fill="#93a1bd" font-size="11">Application ← Presentation ← Session</text>
<text x="480" y="252" fill="#93a1bd" font-size="11">Transport (TCP/UDP) · Network (IP)</text>
<text x="480" y="274" fill="#93a1bd" font-size="11">Network Access (L2 + L1)</text>
<path d="M300 160 L355 160" stroke="#34d399" stroke-width="2" marker-end="url(#ar)"/>
<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#34d399"/></marker></defs>
<text x="328" y="150" fill="#34d399" font-size="10">نگاشت</text></g></svg>`,

encap: `<svg viewBox="0 0 640 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="_encapsulation">
<g font-family="Vazirmatn,sans-serif" font-size="11" text-anchor="middle">
<rect x="30" y="70" width="120" height="60" rx="8" fill="#12233c" stroke="#00d4ff"/><text x="90" y="96" fill="#00d4ff">DATA</text><text x="90" y="116" fill="#93a1bd">لایهٔ ۷</text>
<rect x="170" y="55" width="150" height="90" rx="8" fill="#101c2e" stroke="#3b82f6"/><text x="245" y="80" fill="#7dd3fc">+ TCP/UDP Header</text><text x="245" y="104" fill="#93a1bd">پورت مبدأ/مقصد</text><text x="245" y="126" fill="#e6f7ff" font-size="10">→ SEGMENT</text>
<rect x="340" y="40" width="160" height="120" rx="8" fill="#0e1a2b" stroke="#3b82f6"/><text x="420" y="66" fill="#7dd3fc">+ IP Header</text><text x="420" y="90" fill="#93a1bd">آدرس مبدأ/مقصد</text><text x="420" y="114" fill="#93a1bd">TTL · DSCP</text><text x="420" y="140" fill="#e6f7ff" font-size="10">→ PACKET</text>
<rect x="520" y="25" width="100" height="150" rx="8" fill="#0b1524" stroke="#34d399"/><text x="570" y="55" fill="#34d399">+ MAC</text><text x="570" y="80" fill="#93a1bd">FCS</text><text x="570" y="110" fill="#e6f7ff" font-size="10">FRAME</text><text x="570" y="140" fill="#93a1bd" font-size="10">→ BITS</text>
<path d="M155 100 L165 100 M325 100 L335 100 M505 100 L515 100" stroke="#ffd43b" stroke-width="2"/>
<text x="320" y="200" fill="#93a1bd">هر لایه، کتیبه‌ای اضافه می‌کند — لایهٔ مقابل همان را برمی‌دارد</text></g></svg>`,

vlan: `<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="VLAN و Trunk">
<g font-family="Vazirmatn,sans-serif" font-size="11" text-anchor="middle">
<rect x="40" y="40" width="170" height="180" rx="12" fill="#12233c" stroke="#1e3a5f"/><text x="125" y="66" fill="#e6f7ff" font-weight="bold">SW1</text>
<rect x="60" y="86" width="130" height="44" rx="8" fill="#0e2b1d" stroke="#34d399"/><text x="125" y="112" fill="#34d399">VLAN 10 · STUDENTS</text>
<rect x="60" y="146" width="130" height="44" rx="8" fill="#2b1522" stroke="#f06595"/><text x="125" y="172" fill="#f8a8c6">VLAN 20 · VOICE</text>
<rect x="430" y="40" width="170" height="180" rx="12" fill="#12233c" stroke="#1e3a5f"/><text x="515" y="66" fill="#e6f7ff" font-weight="bold">SW2</text>
<rect x="450" y="86" width="130" height="44" rx="8" fill="#0e2b1d" stroke="#34d399"/><text x="515" y="112" fill="#34d399">VLAN 10</text>
<rect x="450" y="146" width="130" height="44" rx="8" fill="#2b1522" stroke="#f06595"/><text x="515" y="172" fill="#f8a8c6">VLAN 20</text>
<line x1="210" y1="130" x2="430" y2="130" stroke="#00d4ff" stroke-width="4"/>
<rect x="255" y="104" width="130" height="24" rx="6" fill="#0b1524" stroke="#00d4ff"/><text x="320" y="120" fill="#00d4ff">TRUNK 802.1Q</text>
<circle cx="240" cy="130" r="7" fill="#34d399"/><circle cx="300" cy="130" r="7" fill="#f06595"/><circle cx="360" cy="130" r="7" fill="#34d399"/><circle cx="400" cy="130" r="7" fill="#f06595"/>
<text x="320" y="170" fill="#93a1bd">هر بسته با تگ VLAN برچسب می‌خورد تا دو شبکه قاطی نشوند</text>
<text x="320" y="196" fill="#ffd43b" font-size="10">access port = یک VLAN · trunk = همهٔ VLANها</text></g></svg>`,

ospf: `<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="همسایگی OSPF">
<g font-family="Vazirmatn,sans-serif" font-size="11" text-anchor="middle">
<circle cx="120" cy="80" r="34" fill="#12233c" stroke="#00d4ff" stroke-width="2"/><text x="120" y="76" fill="#00d4ff">R1</text><text x="120" y="94" fill="#93a1bd" font-size="9">1.1.1.1</text>
<circle cx="320" cy="80" r="34" fill="#12233c" stroke="#00d4ff" stroke-width="2"/><text x="320" y="76" fill="#00d4ff">R2</text><text x="320" y="94" fill="#93a1bd" font-size="9">2.2.2.2</text>
<circle cx="520" cy="80" r="34" fill="#12233c" stroke="#00d4ff" stroke-width="2"/><text x="520" y="76" fill="#00d4ff">R3</text><text x="520" y="94" fill="#93a1bd" font-size="9">3.3.3.3</text>
<line x1="154" y1="80" x2="286" y2="80" stroke="#34d399" stroke-width="3"/><line x1="354" y1="80" x2="486" y2="80" stroke="#34d399" stroke-width="3"/>
<rect x="176" y="52" width="88" height="20" rx="10" fill="#0e2b1d" stroke="#34d399"/><text x="220" y="66" fill="#34d399" font-size="9">FULL ✓</text>
<rect x="376" y="52" width="88" height="20" rx="10" fill="#0e2b1d" stroke="#34d399"/><text x="420" y="66" fill="#34d399" font-size="9">FULL ✓</text>
<rect x="200" y="150" width="240" height="64" rx="10" fill="#0b1524" stroke="#1e3a5f"/>
<text x="320" y="176" fill="#ffd43b">HELLO → DBD → LSR/LSU → FULL</text>
<text x="320" y="200" fill="#93a1bd" font-size="10">Neighbor table · Database table · Routing table</text></g></svg>`,

leaf: `<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="معماری Leaf-Spine">
<g font-family="Vazirmatn,sans-serif" font-size="11" text-anchor="middle">
${[160,320,480].map((x,i)=>`<rect x="${x-55}" y="36" width="110" height="40" rx="10" fill="#1a1233" stroke="#a78bfa" stroke-width="2"/><text x="${x}" y="61" fill="#c3b2ff">SPINE ${i+1}</text>`).join('')}
${[110,270,430,560].map((x,i)=>`<rect x="${x-50}" y="216" width="100" height="40" rx="10" fill="#0e2b1d" stroke="#34d399" stroke-width="2"/><text x="${x}" y="241" fill="#8ce99a">LEAF ${i+1}</text>`).join('')}
${[110,270,430,560].map(lx=>[160,320,480].map(sx=>`<line x1="${lx}" y1="216" x2="${sx}" y2="76" stroke="#00d4ff" stroke-width="1.4" opacity=".65"/>`).join('')).join('')}
${[110,270,430,560].map(x=>`<rect x="${x-34}" y="272" width="68" height="22" rx="6" fill="#0b1524" stroke="#1e3a5f"/><text x="${x}" y="287" fill="#93a1bd" font-size="9">Server</text>`).join('')}
<text x="320" y="18" fill="#ffd43b" font-size="12" font-weight="bold">Full-Mesh · ECMP · حداکثر ۲ Hop · بدون STP</text>
<text x="320" y="150" fill="#7dd3fc" font-size="10">هر Leaf به همهٔ Spineها · هیچ لینک Leaf↔Leaf نیست</text></g></svg>`,

topo: `<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="توپولوژی سه‌طبقه">
<g font-family="Vazirmatn,sans-serif" font-size="11" text-anchor="middle">
<rect x="250" y="24" width="140" height="40" rx="10" fill="#12233c" stroke="#00d4ff" stroke-width="2"/><text x="320" y="49" fill="#00d4ff">CORE</text>
<rect x="120" y="110" width="130" height="40" rx="10" fill="#101c2e" stroke="#3b82f6" stroke-width="2"/><text x="185" y="135" fill="#7dd3fc">DISTRIBUTION A</text>
<rect x="390" y="110" width="130" height="40" rx="10" fill="#101c2e" stroke="#3b82f6" stroke-width="2"/><text x="455" y="135" fill="#7dd3fc">DISTRIBUTION B</text>
<rect x="40" y="200" width="110" height="36" rx="10" fill="#0e2b1d" stroke="#34d399"/><text x="95" y="223" fill="#8ce99a">ACCESS 1</text>
<rect x="170" y="200" width="110" height="36" rx="10" fill="#0e2b1d" stroke="#34d399"/><text x="225" y="223" fill="#8ce99a">ACCESS 2</text>
<rect x="360" y="200" width="110" height="36" rx="10" fill="#0e2b1d" stroke="#34d399"/><text x="415" y="223" fill="#8ce99a">ACCESS 3</text>
<rect x="490" y="200" width="110" height="36" rx="10" fill="#0e2b1d" stroke="#34d399"/><text x="545" y="223" fill="#8ce99a">ACCESS 4</text>
<path d="M320 64 L185 110 M320 64 L455 110 M185 150 L95 200 M185 150 L225 200 M455 150 L415 200 M455 150 L545 200" stroke="#1e3a5f" stroke-width="2"/>
<text x="320" y="255" fill="#93a1bd" font-size="10">سه‌طبقه: Core ← Distribution ← Access — پروژهٔ پایان CCNA</text></g></svg>`
},

faculties: [
{
  id:'f0', num:'۰', title:'ارزیابی و تکمیل پیش‌نیازها', duration:'۱ ماه', tag:'ماه اول · دانشکدهٔ صفر',
  intro:'چون سطح شروع CCNA است، آموزش را از صفر مطلق آغاز نمی‌کنیم؛ ابتدا نقاط ضعف و قوت را شناسایی می‌کنیم و زمان را به نقاط ضعف اختصاص می‌دهیم. آزمون ورودی: ۵۰ سؤال مفهومی، ۱۰ مسئلهٔ Subnetting و یک سناریوی عملی شبکه.',
  lessons:[
    { id:'f0-w1', title:'OSI، TCP/IP، Ethernet و MAC', sub:'هفتهٔ ۱ · خروجی: تحلیل ارتباط دو دستگاه', minutes:'۴ جلسهٔ ۲ ساعته',
      lead:'در اولین جلسهٔ آکادمی قرار است یک پرسش ساده اما بنیادین را جواب بدهیم: «دو دستگاه در دو سرِ یک سیم، چطور با هم حرف می‌زنند؟» پاسخ، همان مدل‌های لایه‌ای است. به‌جای حفظ هفت نام، می‌خواهیم ببینیم هر لایه چه مشکلی را حل می‌کند، چرا اختراع شد و در یک فریم واقعی Ethernet کجا پیدایش می‌کنیم.',
      sec:{
        goal:[['p','پس از این جلسه می‌توانی یک ارتباط دو دستگاه را لایه‌به‌لایه توضیح بدهی، تفاوت مدل OSI با TCP/IP را بگویی، فریم Ethernet را بشناسی و با تحلیل دو دستگاه ( ARP و MAC ) رفتار شبکه را پیش‌بینی کنی.']],
        prereq:[['ul',['آشنایی مقدماتی با اینترنت و کابل شبکه','نصب Wireshark روی سیستم شخصی','یک Packet Tracer خالی برای تمرین']]],
        concept:[
          ['p','شبکهٔ کامپیوتری از آنجا شروع شد که دو دستگاه خواستند داده‌ای را روی یک کابل مشترک رد و بدل کنند. مشکل اینجاست که «فرستادن یک بایت» در عمل به ده‌ها کار تبدیل می‌شود: باید بدانیم چه کسی می‌فرستد، چه کسی می‌گیرد، دادهٔ خراب چگونه تشخیص داده شود، و اگر دو نفر هم‌زمان حرف زدند چه کنیم. مدل لایه‌ای دقیقاً برای همین است: هر مشکل را یک لایه حل می‌کند.'],
          ['h3','مدل OSI — هفت لایهٔ مسئولیت'],
          ['p','OSI هفت لایه دارد و هر کدام یک «شغل» دارند: لایهٔ فیزیکی (۱) بیت‌ها را روی کابل می‌فرستد؛ لایهٔ پیوند داده (۲) فریم می‌سازد، آدرس MAC دارد و با سوئیچ کار می‌کند؛ لایهٔ شبکه (۳) مسیر را انتخاب می‌کند و آدرس منطقی (IP) دارد؛ لایهٔ انتقال (۴) پورت و اعتمادپذیری (TCP/UDP) را مدیریت می‌کند؛ سه لایهٔ بالایی (۵ تا ۷) با session، رمزگذاری و خودِ برنامه سروکار دارند.'],
          ['p','نکتهٔ کلیدی این است که این لایه‌ها فقط «طبقه‌بندی» نیستند؛ هر لایه به لایهٔ بالاتر یک سرویس می‌دهد و از لایهٔ پایین‌تر یک سرویس می‌گیرد. وقتی می‌گویی «لایهٔ ۳ کارش تمام شد»، یعنی بسته آمادهٔ تحویل به لایهٔ ۲ شده است.'],
          ['h3','مدل TCP/IP — مدلی که واقعاً روی شبکه کار می‌کند'],
          ['p','TCP/IP چهار لایه دارد و همان چیزی است که اینترنت امروز روی آن ساخته شده: Application (ترکیب لایه‌های ۵ تا ۷ OSI)، Transport (لایهٔ ۴)، Internet (لایهٔ ۳) و Network Access (لایه‌های ۱ و ۲). در آزمون CCNA و در دنیای واقعی، OSI زبان گفتگو و TCP/IP زبان اجراست؛ هر دو را باید بلد باشی.'],
          ['h3','Ethernet و آدرس MAC'],
          ['p','Ethernet استاندارد لایهٔ ۲ است. هر کارت شبکه یک آدرس MAC منحصربه‌فرد ۴۸ بیتی دارد (مثلاً 00:1A:2B:3C:4D:5E) که مثل شمارهٔ تلفن روی سیم نوشته شده. سوئیچ با همین آدرس‌ها یاد می‌گیرد هر پورت به کدام دستگاه وصل است. فریم Ethernet یعنی بستهٔ لایهٔ ۲: مقصد، مبدأ، نوع ( EtherType ) و داده با چک‌سام.'],
          ['note','key','یک جملهٔ حفظی کافی نیست؛ باید بتوانی یک ping را لایه‌به‌لایه توضیح بدهی: از برنامه (L7) تا بیت روی کابل (L1) و برگشت.']
        ],
        protocol:[
          ['p','برای دیدن لایه‌ها در عمل، کافی است یک ارتباط ساده را بگیریم. وقتی PC1 به PC2 ping می‌زند، چهار اتفاق می‌افتد که در Wireshark کاملاً دیده می‌شود:'],
          ['ol',['ARP: PC1 اول می‌پرسد «IP مقصد، کدام MAC است؟» و یک ARP Request broadcast می‌فرستد','ICMP Echo Request: بستهٔ ping با آدرس IP مقصد ساخته می‌شود','فریم‌سازی: لایهٔ ۲ فریم را با MAC مقصد می‌بندد و روی کابل می‌فرستد','ICMP Echo Reply: مقصد جواب می‌دهد و مسیر برگشت را همین‌طور طی می‌کند']],
          ['cli','مشاهدهٔ زنده در Wireshark','filter: arp or icmp\n\nARP  Who has 192.168.1.2?  Tell 192.168.1.1\nARP  192.168.1.2 is at 00:1A:2B:3C:4D:5E\nICMP Echo (ping) request  192.168.1.1 → 192.168.1.2\nICMP Echo (ping) reply    192.168.1.2 → 192.168.1.1'],
          ['p','در این خروجی سه لایه را هم‌زمان می‌بینی: آدرس‌دهی لایهٔ ۳ (IPها)، فریم‌سازی لایهٔ ۲ (MACها) و خودِ سرویس لایهٔ ۷/۳ (ICMP). همین چهار خط، کل مدل لایه‌ای را اثبات می‌کند.']
        ],
        ios:[
          ['p','در جلسهٔ اول با دستورات پایهٔ مشاهدهٔ IOS آشنا می‌شویم؛ خروجی این دستورها همان چیزی است که بعداً در عیب‌یابی استفاده می‌کنی:'],
          ['cli','دستورات مشاهدهٔ پایه','Router> enable\nRouter# show version            ! نسخه و سلامت دستگاه\nRouter# show ip interface brief ! وضعیت پورت‌ها و IPها\nRouter# show mac address-table  ! جدول MAC سوئیچ\nRouter# ping 192.168.1.2        ! تست لایهٔ ۳\nRouter# traceroute 8.8.8.8      ! مسیر تا مقصد'],
          ['note','tip','پیش از هر پیکربندی، اول ببین دستگاه در چه وضعیتی است. show ،بهترین دوست مهندس شبکه است.']
        ],
        diagram:[['svg','osi'],['svg','encap'],['p','دیاگرام بالا: نگاشت لایه‌های OSI به مدل TCP/IP و فرآیند encapsulation — هر لایه کتیبهٔ خودش را اضافه می‌کند و لایهٔ مقابل همان را برمی‌دارد.']],
        lab:[
          ['labs',[
            {t:'آزمایشگاه ۱ — ارتباط دو دستگاه در Packet Tracer',steps:['دو PC و یک سوئیچ بساز و با کابل مستقیم وصل کن','به هر PC یک IP در یک زیرشبکه بده (192.168.1.0/24)','از PC1 به PC2 ping بزن و در Wireshark پاسخ را بگیر','در پنل Details، Ethernet Header ،IP Header و ICMP را پیدا کن و بنویس کدام لایه است','آدرس MAC سوئیچ را با show mac address-table تطبیق بده']},
            {t:'آزمایشگاه ۲ — تولید ترافیک ARP',steps:['کش PC1 را پاک کن (arp -d * در خط فرمان)','دوباره ping بزن و اولین فریم ARP Request را در Wireshark تحلیل کن','بنویس: چرا ARP Request broadcast است ولی Reply unicast؟']}
          ]]
        ],
        trouble:[
          ['ul',['ping بدون جواب ولی لینک سبز: اول ARP را چک کن — آیا اصلاً MAC مقصد یاد گرفته شده؟','فریم‌های CRC Error در show interfaces: مشکل لایهٔ ۱/۲ است، نه لایهٔ ۳','دو دستگاه در دو subnet مختلف بدون روتر: مکالمهٔ لایهٔ ۳ هرگز شروع نمی‌شود']],
          ['note','warn','این سه حالت را عمداً در لاب بساز؛ عیب‌یابی یادگیری نیست مگر اینکه اول خرابی را دیده باشی.']
        ],
        exercise:[
          ['ol',['بدون نگاه به مدل، بنویس: یک فریم Ethernet از کدام فیلدها تشکیل شده و هر فیلد توسط کدام لایه پر می‌شود؟','تفاوت broadcast domain با collision domain را با یک مثال از کلاس خودت توضیح بده','مسیر یک پکت ping از PC1 تا سرور در VLAN دیگر را لایه‌به‌لایه بنویس']]
        ],
        quiz:[
          ['quiz',[
            {q:'کدام لایه آدرس MAC را مدیریت می‌کند؟',opts:['لایهٔ ۳ Network','لایهٔ ۲ Data Link','لایهٔ ۴ Transport','لایهٔ ۷ Application'],a:1,exp:'لایهٔ ۲ (Data Link) فریم می‌سازد و آدرس MAC دارد؛ سوئیچ هم در همین لایه کار می‌کند.'},
            {q:'در مدل TCP/IP، لایهٔ Internet معادل کدام لایهٔ OSI است؟',opts:['لایهٔ ۴','لایهٔ ۳','لایهٔ ۲','لایهٔ ۵'],a:1,exp:'لایهٔ Internet در TCP/IP همان لایهٔ ۳ Network در OSI است — جایی که IP و مسیریابی زندگی می‌کنند.'},
            {q:'چرا ARP Request همیشه broadcast است؟',opts:['چون IP مقصد را نداریم و باید از همه بپرسیم','چون پورت مقصد نامشخص است','چون TCP connection نداریم','چون VLAN trunk شده'],a:0,exp:'در لحظهٔ ARP فقط IP مقصد را داریم و MAC آن را نه؛ پس از همه می‌پرسیم: «فلان IP کجاست؟»'},
            {q:'نقش FCS در فریم Ethernet چیست؟',opts:['رمزگذاری داده','تشخیص خطای انتقال','آدرس‌دهی منطقی','مدیریت پورت'],a:1,exp:'FCS یک چک‌سام است؛ اگر بیت‌ها در مسیر خراب شده باشند، فریم دور انداخته می‌شود.'}
          ]]
        ],
        notes:[
          ['ul',['جدول لایه‌ها و پروتکل‌های هر کدام را با دست خودت یک بار بنویس','خروجی show ip interface brief و show mac address-table را در دفترچهٔ آکادمی نگه دار','هر جلسه: یک بند «چه یاد گرفتم + چه سؤالی دارم» ثبت کن']]
        ]
      },
      faq:[{q:'آیا باید هفت نام لایهٔ OSI را حفظ کنم؟',a:'حفظِ خالی فایده ندارد، اما ترتیب و نقش هر لایه را باید بدانی؛ در آزمون و در عیب‌یابی، «کدام لایه؟» پرسش همیشگی است.'},{q:'تفاوت broadcast domain و collision domain چیست؟',a:'دامنهٔ برخورد (collision) با هاب و سوئیچ پورت به پورت جدا می‌شود؛ دامنهٔ پخش (broadcast) با روتر (یا VLAN) جدا می‌شود. سوئیچ هر پورت را یک collision domain مستقل می‌کند.'},{q:'Wireshark چه کمکی به یادگیری می‌کند؟',a:'مدل لایه‌ای را «دیدنی» می‌کند؛ وقتی خودت کتیبهٔ TCP یا تگ VLAN را در بایت‌ها پیدا می‌کنی، دیگر فراموش نمی‌کنی.'}]
    },
    { id:'f0-w2', title:'IPv4، Subnetting، VLSM و CIDR', sub:'هفتهٔ ۲ · خروجی: طراحی آدرس‌دهی', minutes:'۴ جلسهٔ ۲ ساعته',
      lead:'آدرس‌دهی قلب شبکه است. در این هفته یاد می‌گیریم یک محدودهٔ IP را طوری برش بزنیم که هر VLAN به اندازهٔ نیازش هاست داشته باشد، بدون اینکه یک آدرس هدر برود. هدف نهایی: طراحی یک IP Plan کامل برای یک سازمان.',
      sec:{
        goal:[['p','طراحی زیرشبکه با Subnetting کلاسیک، VLSM و CIDR؛ محاسبهٔ تعداد هاست، broadcast و subnet ID در کمتر از ۳۰ ثانیه؛ و خواندن جدول آدرس‌دهی یک سازمان.']],
        prereq:[['ul',['درک مفهوم باینری و هگزادسیمال','جلسهٔ قبل: لایهٔ ۳ و نقش IP','ماشین‌حساب یا ذهنی برای توان ۲']]],
        concept:[
          ['p','هر آدرس IPv4 یک عدد ۳۲ بیتی است که ما آن را چهار عدد ۰ تا ۲۵۵ می‌بینیم. ماسک زیرشبکه (Subnet Mask) مشخص می‌کند چند بیت ابتدایی «شبکه» هستند و بقیه «هاست». وقتی می‌گوییم 192.168.1.0/24 ،یعنی ۲۴ بیت شبکه و ۸ بیت هاست: ۲۵۶ آدرس داریم که ۲۵۴ تای آن قابل استفاده است (اولی شبکه، آخری broadcast).'],
          ['h3','Subnetting — بریدن یک شبکه به چند تا'],
          ['p','با وام گرفتن بیت از بخش هاست، یک شبکه را به چند زیرشبکه می‌بریم. مثلاً از /24 به /26 برسی: ۶ بیت بیشتر شبکه، یعنی ۶۴ زیرشبکه و در هر کدام ۶۲ هاست. منطقی ساده است: هر بیتی که به شبکه می‌دهی، نصف هاست‌ها را از دست می‌دهی و دو برابر زیرشبکه می‌گیری.'],
          ['h3','VLSM — برشِ اندازه‌ای'],
          ['p','در VLSM هر زیرشبکه به اندازهٔ واقعی‌اش برش می‌خورد: سرورها /26، ورک‌استیشن‌ها /27، لینک‌های روتربه‌روتر /30 و پشتیبان‌گیری فقط /30 لازم دارد. این‌طوری هیچ آدرسی هدر نمی‌رود و جدول مرتب و فشرده می‌شود.'],
          ['h3','CIDR و Summarization'],
          ['p','CIDR یعنی کلاس‌ها دیگر ملاک نیستند؛ با یک پیشوند /n شبکه را توصیف می‌کنیم. Summarization معکوس کار است: چند زیرشبکهٔ مجاور را در یک مسیر خلاصه می‌کنیم تا جدول روتینگ کوچک بماند — پایهٔ کار هر شبکهٔ بزرگ.']
        ],
        protocol:[
          ['p','رویکرد محاسبه سه قدمی است:'],
          ['ol',['تعداد هاست مورد نیاز هر بخش را بنویس (با ۲۰٪ ذخیره)','نزدیک‌ترین توان ۲ را پیدا کن → ماسک همان را بنویس','بلاک‌ها را پشت سر هم بچین و اولین/آخری هر بلاک را بنویس']],
          ['table',['بخش','تعداد هاست','زیرشبکه','ماسک','محدوده'],[['سرورها','۵۰','192.168.1.0','/26','.1 – .62'],['ورک‌استیشن','۱۰۰','192.168.1.64','/25','.65 – .190'],['VoIP','۳۰','192.168.1.192','/27','.193 – .222'],['لینک R1-R2','۲','192.168.1.224','/30','.225 – .226'],['پشتیبان','۲','192.168.1.228','/30','.229 – .230']]],
          ['note','key','یک /26 دقیقاً ۶۴ آدرس و ۶۲ هاست دارد؛ یادگیری همین جدول‌های کوچک ( /24 تا /30 ) سرعتت را در آزمون چند برابر می‌کند.']
        ],
        ios:[
          ['cli','اعمال آدرس‌دهی روی روتر و سوئیچ','Router(config)# interface g0/0\nRouter(config-if)# ip address 192.168.1.1 255.255.255.192\nRouter(config-if)# no shutdown\n\nSwitch(config)# interface vlan 10\nSwitch(config-if)# ip address 192.168.1.62 255.255.255.192\nSwitch(config-if)# exit\nSwitch(config)# ip default-gateway 192.168.1.1'],
          ['cli','راستی‌آزمایی','Router# show ip interface brief\nRouter# show ip route\nC  192.168.1.0/26 is directly connected, GigabitEthernet0/0']
        ],
        diagram:[['p','در دیاگرام هفتهٔ ۱ (encap) بخش IP Header را با آدرس‌دهی این هفته کامل کن: مقصد و مبدأ در لایهٔ ۳ تصمیم می‌گیرند، ماسک مسیر را مشخص می‌کند. یک جدول بزرگ از زیرشبکه‌ها روی دیوار کلاس بکش.']],
        lab:[
          ['labs',[
            {t:'آزمایشگاه ۲ — IP Addressing و Subnetting (الزامی CCNA)',steps:['یک سازمان با ۴ بخش طراحی کن: Management ,Servers ,Users ,VoIP','هر بخش را با VLSM برش بزن و جدول IP Plan بنویس','در Packet Tracer پیاده‌سازی کن و به هر دستگاه IP بده','با ping و traceroute صحت محدوده‌ها را اثبات کن','اشتباه عمداً بساز: یک IP تکراری بده و با show ip interface brief پیدایش کن']}
          ]]
        ],
        trouble:[
          ['ul',['دو دستگاه در یک VLAN ولی ping نمی‌شوند: اول ماسک را چک کن — یکی /24 و دیگری /25 یعنی هم‌زیرشبکه نیستند','آدرس network یا broadcast به عنوان IP تجهیز: پیکربندی رد می‌شود یا لینک بالا نمی‌آید','gateway اشتباه: دستگاه داخلی را می‌بیند ولی بیرون نمی‌رود']]
        ],
        exercise:[
          ['ol',['۱۰۰۰ هاست در یک /16 موجودی: چند /24 لازم داری؟','یک /28 چند هاست قابل استفاده دارد؟ (جواب را با باینری اثبات کن)','Summarization: دو مسیر 10.1.0.0/16 و 10.2.0.0/16 را در یک مسیر خلاصه کن']]
        ],
        quiz:[
          ['quiz',[
            {q:'یک /27 چند هاست قابل استفاده دارد؟',opts:['۳۰','۳۲','۶۲','۶۴'],a:0,exp:'۲^۵=۳۲ آدرس؛ منهای network و broadcast → ۳۰ هاست.'},
            {q:'در VLSM، هدف اصلی چیست؟',opts:['یکسان‌سازی همهٔ ماسک‌ها','تخصیص اندازه‌ای آدرس بدون هدررفت','حذف روترها','افزایش تعداد broadcast'],a:1,exp:'VLSM هر بلاک را به اندازهٔ نیاز واقعی می‌برد تا از آدرس هدر نرود.'},
            {q:'بلوک 192.168.1.64/26 چه محدوده‌ای است؟',opts:['.1 تا .64','.65 تا .126','.64 تا .127','.128 تا .191'],a:2,exp:'/26 یعنی بلاک‌های ۶۴تایی: 0-63 ،64-127 ،128-191 ...؛ بنابراین .64 تا .127.'}
          ]]
        ],
        notes:[
          ['ul',['جدول /24 تا /30 (تعداد subnet و host) را حفظ کن و هر روز ۵ محاسبه تمرین کن','IP Plan نهایی هفته را در دفترچه ثبت کن — همین جدول پروژهٔ پایان CCNA می‌شود']]
        ]
      }
    },
    { id:'f0-w3', title:'IPv6، TCP، UDP، ARP و ICMP', sub:'هفتهٔ ۳ · خروجی: تحلیل بسته‌ها', minutes:'۴ جلسهٔ ۲ ساعته',
      lead:'در این هفته پروتکل‌های لایه‌های ۳ و ۴ را از نزدیک می‌بینیم: IPv6 با آدرس‌دهی بی‌انتهایش، TCP با دست‌سازی سه‌طرفه، UDP با سرعت بی‌قیدش، و دو پروتکل تشخیصی ARP و ICMP که بدون آن‌ها هیچ عیب‌یابی‌ای ممکن نیست.',
      sec:{
        goal:[['p','تفاوت TCP و UDP را با مثال واقعی توضیح دادن، مراحل TCP Handshake را رسم کردن، آدرس‌دهی IPv6 و انواع آدرس‌هایش را تشخیص دادن، و با ping/traceroute و Wireshark بسته‌ها را تحلیل کردن.']],
        prereq:[['ul',['هفتهٔ ۲: آدرس‌دهی IPv4 و ماسک','مفاهیم لایهٔ ۴ و پورت','نصب Wireshark']]],
        concept:[
          ['p','IPv6 با ۱۲۸ بیت آدرس می‌آید تا مشکل تمام شدن آدرس و مصرف بیش از حد NAT را حل کند. شکل نوشتنش هگزادسیمال با دو نقطه است (مثل 2001:db8::1) و قاعدهٔ ساده‌ای دارد: یک سری صفر متوالی می‌تواند با :: جایگزین شود. مهم‌ترین انواع آدرس: Global Unicast (عمومی مثل IPv4)، Link-Local (fe80:: — فقط داخل یک لینک، پایهٔ همهٔ ارتباطات داخلی) و Multicast (ff02:: برای گروه‌ها).'],
          ['h3','TCP در برابر UDP'],
          ['p','TCP قابل‌اعتماد است: دست سازی سه‌طرفه (SYN → SYN/ACK → ACK) می‌سازد، شمارهٔ ترتیب دارد، تأیید می‌گیرد و بستهٔ گم‌شده را دوباره می‌فرستد؛ به قیمت تأخیر و سربار. UDP بی‌قاعده است: فقط می‌فرستد، نه دست می‌دهد نه جواب می‌گیرد. وب و ایمیل TCP می‌خواهند؛ DNS کوتاه، VoIP زنده و استریم ویدیو UDP ترجیح می‌دهند چون تأخیر برایشان مرگبارتر از یک بستهٔ گم‌شده است.'],
          ['h3','ARP و ICMP — ابزارهای تشخیص'],
          ['p','ARP پل میان IP و MAC است و ICMP زبان «سلام و خطا»ی لایهٔ ۳: echo request/reply برای تست، time exceeded برای اعلام اتمام TTL، و destination unreachable برای گفتن «مقصد در دسترس نیست». هر عیب‌یابی شبکه‌ای با همین چهار پیام شروع می‌شود.']
        ],
        protocol:[
          ['h3','دست سازی TCP سه‌طرفه'],
          ['ol',['Client: SYN (شمارهٔ ترتیب x)','Server: SYN/ACK (x تأیید، شمارهٔ خودش y)','Client: ACK (y تأیید)','پس از آن انتقال داده و بستهٔ چهارمی FIN برای بستن']],
          ['cli','مشاهدهٔ Handshake در Wireshark','filter: tcp.flags.syn==1 and tcp.flags.ack==0\n\nNo.  Info\n1    192.168.1.10 → 93.184.216.34  [SYN]  Seq=0\n2    93.184.216.34 → 192.168.1.10  [SYN, ACK] Seq=0 Ack=1\n3    192.168.1.10 → 93.184.216.34  [ACK]  Ack=1'],
          ['cli','نشانه‌های خطا در ICMP','PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.\nFrom 10.0.0.1 icmp_seq=1 Destination Host Unreachable\nFrom 10.0.0.1 icmp_seq=2 Time to live exceeded']
        ],
        ios:[
          ['cli','تست‌های لایهٔ ۳ و ۴','PC> ping 2001:db8::1\nPC> traceroute 8.8.8.8\nRouter# show tcp brief     ! نشست‌های TCP باز\nRouter# show ipv6 interface brief'],
          ['note','tip','traceroute لایهٔ ۳ را نشان می‌دهد و nc/telnet لایهٔ ۴ را؛ ترکیب هر دو = نقشهٔ کامل مسیر و پورت.']
        ],
        diagram:[['svg','encap'],['p','در بستهٔ بالا، هدر TCP/UDP پورت‌ها را حمل می‌کند (لایهٔ ۴) و هدر IP مسیر را (لایهٔ ۳). آدرس IPv6 جای آدرس IPv4 می‌نشیند، بقیهٔ ساختار همان می‌ماند.']],
        lab:[
          ['labs',[
            {t:'آزمایشگاه ۲۳ — تحلیل Packet با Wireshark',steps:['ترافیک وب و DNS ایجاد کن و capture بگیر','دست سازی TCP سه‌طرفه و بستن (FIN) را پیدا کن و مراحل را شماره‌گذاری کن','یک DNS Query/Reply و یک ICMP ping را فیلتر کن','مقایسه کن: چند بسته برای یک وب‌صفحهٔ ساده؟ چندتایش UDP است؟']},
            {t:'آزمایشگاه ۱۶ — IPv6 و SLAAC',steps:['روی یک روتر IPv6 را فعال کن (ipv6 unicast-routing)','روی لینک ها RA بفرست و آدرس link-local را ببین','از PC با ipconfig /all آدرس SLAAC را بررسی و ping داخلی بزن']}
          ]]
        ],
        trouble:[
          ['ul',['ping به IPv6 جواب نمی‌دهد ولی link-local هست: مسیر default یا RA نداری','SYN بدون SYN/ACK: یا firewall مسیر برگشت را می‌بندد یا پورت بسته است','time exceeded در traceroute: مسیر طولانی‌تر از TTL یا حلقهٔ مسیریابی داری']]
        ],
        exercise:[
          ['ol',['چرا DNS هم TCP و هم UDP استفاده می‌کند؟','مراحل Handshake را با شمارهٔ ترتیب (Seq/Ack) رسم کن','سه تفاوت کلیدی IPv4 و IPv6 را در یک جدول بنویس']]
        ],
        quiz:[
          ['quiz',[
            {q:'کدام پروتکل برای VoIP ترجیح داده می‌شود و چرا؟',opts:['TCP — قابل‌اعتماد','UDP — تأخیر کم','ICMP — سریع','ARP — لایهٔ ۲'],a:1,exp:'در صدا، تأخیر بدتر از یک بستهٔ گم‌شده است؛ پس UDP با سربار کم.'},
            {q:'آدرس fe80:: متعلق به کدام نوع است؟',opts:['Global Unicast','Link-Local','Multicast','Loopback فقط'],a:1,exp:'fe80::/10 فقط داخل یک لینک معتبر است و پایهٔ ارتباطات داخلی IPv6 است.'},
            {q:'پیام ICMP «Time to live exceeded» چه می‌گوید؟',opts:['مقصد خاموش است','بسته به مقصد نرسید و TTL صفر شد','پورت بسته است','آدرس اشتباه است'],a:1,exp:'معمولاً یعنی مسیر طولانی‌تر از TTL است یا حلقهٔ مسیریابی داریم.'}
          ]]
        ],
        notes:[['ul',['جدول TCP vs UDP و مثال هر کدام را بنویس','خروجی traceroute واقعی خودت را در دفترچهٔ آکادمی نگه دار']]
        ]
      }
    },
    { id:'f0-w4', title:'DNS، DHCP، NAT، SSH و Wireshark', sub:'هفتهٔ ۴ · خروجی: آزمون تعیین سطح', minutes:'۴ جلسهٔ ۲ ساعته',
      lead:'آخرین هفتهٔ مبانی، سرویس‌هایی را می‌بینیم که هر روز بدون دیدنشان کار می‌کنند: DNS نام را به IP تبدیل می‌کند، DHCP آدرس می‌دهد، NAT خصوصی را به عمومی وصل می‌کند و SSH راه امن مدیریت است. در پایان، آزمون تعیین سطح ۵۰+۱۰+۱ برگزار می‌شود.',
      sec:{
        goal:[['p','پیکربندی و عیب‌یابی چهار سرویس پایه (DNS، DHCP، NAT، SSH) و استفادهٔ حرفه‌ای از Wireshark برای اثبات رفتار آن‌ها؛ آمادگی برای آزمون تعیین سطح ورودی آکادمی.']],
        prereq:[['ul',['سه هفتهٔ قبل: مدل لایه‌ها، آدرس‌دهی، پروتکل‌های انتقال','آشنایی با خط فرمان سیستم‌عامل']]],
        concept:[
          ['h3','DNS — دفتر تلفن اینترنت'],
          ['p','DNS نام‌ها را به IP تبدیل می‌کند تا مجبور نباشیم اعداد را حفظ کنیم. سلسله‌مراتب دارد: ریشه، TLD (.ir ,.com)، دامنهٔ سازمانی و رکوردهای داخلی (A، AAAA، CNAME، MX). وقتی «مرورگر باز نمی‌شود ولی ping به IP جواب می‌دهد»، معمولاً ۹۰٪ مشکل DNS است.'],
          ['h3','DHCP — آدرس‌دهی خودکار'],
          ['p','DHCP چهار پیام دارد: DISCOVER (کجا هست کسی؟)، OFFER (بیا این را بگیر)، REQUEST (همان را می‌خواهم) و ACK (ثبت شد). سرور علاوه بر IP، ماسک، gateway و DNS را هم می‌دهد. در شبکه‌های چند-VLAN از DHCP Relay استفاده می‌کنیم تا یک سرور مرکزی به همهٔ VLANها سرویس بدهد.'],
          ['h3','NAT — پل خصوصی به عمومی'],
          ['p','آدرس‌های خصوصی (10/8، 172.16/12، 192.168/16) در اینترنت مسیر ندارند؛ NAT در لبه آن‌ها را به آدرس عمومی روتر ترجمه می‌کند. PAT (یا NAT Overload) با پورت‌های متفاوت صدها دستگاه را پشت یک IP عمومی می‌نشاند.'],
          ['h3','SSH — پوستهٔ امن'],
          ['p','Telnet پسورد را روی شبکه لخت می‌فرستد؛ SSH همه‌چیز را رمز می‌کند و جایگزین استاندارد مدیریت تجهیزات است. فعال‌سازی‌اش در همان ۵ دقیقهٔ اول پیکربندی هر دستگاه انجام می‌شود — نه بعداً.']
        ],
        protocol:[
          ['cli','چهار سرویس در یک نگاه','! --- DNS ---\nRouter(config)# ip name-server 8.8.8.8\n\n! --- DHCP (server) ---\nRouter(config)# ip dhcp pool USERS\nRouter(dhcp-config)# network 192.168.1.0 255.255.255.0\nRouter(dhcp-config)# default-router 192.168.1.1\nRouter(dhcp-config)# dns-server 8.8.8.8\n\n! --- NAT ---\nRouter(config)# access-list 1 permit 192.168.1.0 0.0.0.255\nRouter(config)# interface g0/1\nRouter(config-if)# ip nat inside\nRouter(config-if)# interface g0/0\nRouter(config-if)# ip nat outside\nRouter(config-if)# ip nat inside source list 1 interface g0/0 overload\n\n! --- SSH ---\nRouter(config)# hostname R1\nRouter(config)# ip domain-name fam.academy\nRouter(config)# crypto key generate rsa modulus 2048\nRouter(config)# line vty 0 4\nRouter(config-line)# transport input ssh\nRouter(config-line)# login local'],
          ['cli','اثبات با Wireshark','DHCP filter: bootp or dhcp\nDNS  filter: dns\nNAT : پس از NAT، آدرس مبدأ در بستهٔ خروجی را با capture بیرونی مقایسه کن']
        ],
        ios:[['cli','دستورهای کلیدی و بررسی','show ip interface brief\nshow ip route\nshow running-config | include name-server\nshow ip dhcp binding\nshow ip nat translations\nshow access-lists']],
        diagram:[['svg','topo'],['p','لبهٔ شبکه (جای NAT)، سرور داخلی (DNS/DHCP) و روترهای مسیر — همین چهار سرویس، همهٔ ارتباط یک LAN با دنیا را ممکن می‌کنند.']],
        lab:[
          ['labs',[
            {t:'آزمایشگاه ۱۱ — DHCP Server و Relay',steps:['DHCP pool با network/default-router/dns بساز','یک کلاینت آدرس بگیر و با ipconfig تأیید کن','در VLAN دیگر ip helper-address بده و relay را تست کن','رزرو یک IP برای پرینتر با dhcp binding']},
            {t:'آزمایشگاه ۱۲ — NAT و PAT',steps:['inside/outside و ACL تعریف کن','Overload بساز و از چند کلاینت به بیرون ping بزن','با debug ip nat یا capture، ترجمه را ببین','یک port-forwarding برای سرور داخلی اضافه کن']},
            {t:'آزمایشگاه ۱۷ — SSH و Hardening',steps:['hostname/domain/RSA key تنظیم کن','line vty فقط ssh + login local','پسورد enable و سطوح دسترسی را پیکربندی کن','از یک کلاینت واقعی SSH وصل شو و Telnet را رد کن']}
          ]]
        ],
        trouble:[
          ['ul',['کلاینت IP نمی‌گیرد: VLAN interface up است؟ helper-address دارد؟ pool تمام نشده؟','وب باز نمی‌شود ولی ping به IP جواب می‌دهد: DNS را چک کن','SSH بعد از crypto key هم رد می‌شود: transport input فقط ssh باشد، پسورد local تعریف شده باشد','NAT کار نمی‌کند: inside/outside جا به جا؟ ACL مبدأ را می‌گیرد؟']]
        ],
        exercise:[
          ['ol',['چهار پیام DHCP را با شرح هر کدام بنویس','چرا NAT و DHCP مکمل‌اند؟ با یک نقشهٔ ساده توضیح بده','تفاوت ip nat inside source static با overload چیست؟']]
        ],
        quiz:[
          ['quiz',[
            {q:'چرا از DHCP Relay استفاده می‌کنیم؟',opts:['برای رمزگذاری ترافیک','چون broadcast DHCP به VLAN دیگر نمی‌رود','برای تبدیل IP به MAC','برای افزایش پهنای باند'],a:1,exp:'broadcast در لایهٔ ۳ مرز VLAN را رد نمی‌کند؛ helper-address پیام را به سرور مرکزی می‌رساند.'},
            {q:'در PAT، چند دستگاه می‌توانند پشت یک IP عمومی باشند؟',opts:['فقط یکی','دو تا','به تعداد پورت‌های خالی','محدودیت ندارد ولی معمولاً ۶۵هزار'],a:2,exp:'هر اتصال با ترکیب IP+پورت یکتا می‌شود؛ عملاً ده‌ها هزار اتصال همزمان.'},
            {q:'کدام گزینه امنیت SSH را کامل می‌کند؟',opts:['فقط hostname','transport input ssh + login local + کلید RSA','غیرفعال کردن vty','پسورد enable خالی'],a:1,exp:'همهٔ لازم‌ها با هم: کلید برای رمز، فقط SSH برای ورود، و پسورد محلی برای احراز.'}
          ]]
        ],
        notes:[['ul',['هر چهار سرویس را یک‌بار از صفر روی Packet Tracer پیاده‌سازی کن','نتایج آزمون تعیین سطح را ثبت کن — نقاط ضعف، برنامهٔ ماه دوم']]
        ]
      },
      faq:[{q:'آزمون تعیین سطح چطور است؟',a:'۵۰ سؤال مفهومی + ۱۰ مسئلهٔ Subnetting + یک سناریوی عملی شبکه. اگر در مبحثی تسلط داشته باشی، از تکرار آن عبور می‌کنی و زمان به نقاط ضعفت اختصاص می‌یابد.'},{q:'اگر نمرهٔ ورودی پایین بیاید چه می‌شود؟',a:'مشکلی نیست — دانشکدهٔ صفر دقیقاً برای همین است؛ چهار هفته روی همان ضعف‌ها کار می‌کنی و دوباره تست می‌شوی.'}]
    },
  ]
},
{
  id:'fnd', num:'۱', title:'دانشکدهٔ مبانی — Network Engineering Foundations', duration:'۳ ماه', tag:'Foundations',
  intro:'پس از ارزیابی، نوبت به ساختن پایه به‌صورت منظم است: Ethernet و کابل‌ها، آدرس‌دهی عمیق، پروتکل‌های حمل‌ونقل و سرویس‌ها، و اولین تماس با Cisco IOS. خروجی این دانشکده: دانشجویی است که هر بسته را از کابل تا سرویس ردیابی می‌کند و آدرس‌دهی را بدون ماشین‌حساب طراحی می‌کند.',
  lessons:[
    { id:'fnd-w1', title:'Ethernet، کابل‌ها و توپولوژی‌ها — لایه ۱ و ۲', sub:'Foundations · هفتهٔ ۱', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'شبکه از یک قاب Ethernet و یک کابل شروع می‌شود. در این درس اجزاء فیزیکی، فریم، MAC و مفاهیم دامنهٔ برخورد/پخش را می‌سازیم — پایه‌ای که همهٔ درس‌های بعدی روی آن می‌ایستند.',
      sec:{
        goal:[['p','در پایان: اجزای شبکه (سوئیچ، روتر، سوئیچ لایه ۲/۳)، انواع کابل (مسی/فیبر) و کاربردشان، ساختار فریم Ethernet، نقش MAC، و تفاوت collision domain و broadcast domain را می‌توانی توضیح دهی و با نمودار نشان دهی.']],
        prereq:[['ul',['هدف از شبکه و ارتباط دو دستگاه','کمی ریاضی برای محاسبات بعدی','دسترسی به Packet Tracer یا یک سوئیچ واقعی']]],
        concept:[['h3','چرا Ethernet؟'],['p','Ethernet (IEEE 802.3) زبان فریم‌سازی لایه ۲ است: هر بستهٔ IP قبل از رفتن در کابل، داخل قابی با آدرس مبدأ/مقصد MAC بسته‌بندی می‌شود. سوئیچ فقط با همین قاب کار می‌کند: جدول MAC می‌سازد و قاب را به پورت درست می‌فرستد — نه بیشتر.'],['h3','دامنه‌ها'],['p','Collision Domain یعنی چند دستگاه هم‌زمان حرف بزنند و بسته‌ها به هم بخورند (در سوئیچ هر پورت یک دامنه است). Broadcast Domain یعنی بستهٔ broadcast به همه برسد (VLAN مرز آن است). هرچه دامنهٔ برخورد کوچک‌تر، شبکه تمیزتر.'],['h3','کابل‌ها و فیبر'],['p','مسی (Cat5e/6/6a) تا ~۱۰۰ متر و 1G/10G؛ فیبر (SMF/MMF) برای فواصل بلند و لینک‌های uplink. فیبر دو نوع دارد: چندحالته برای داخل ساختمان، تک‌حالته برای فواصل شهری/کیلومتری.']],
        protocol:[['h3','ساختار فریم Ethernet'],['table',['بخش','طول تقریبی','نقش'],[
          ['Preamble','7 بایت','همگام‌سازی ساعت'],
          ['SFD','1 بایت','شروع فریم'],
          ['Dst MAC','6 بایت','گیرنده'],
          ['Src MAC','6 بایت','فرستنده'],
          ['Type/Length','2 بایت','پروتکل بالاتر (مثلاً IPv4=0x0800)'],
          ['Payload','46–1500 بایت','داده (IP packet)'],
          ['FCS','4 بایت','CRC برای سلامت'],
        ]],['cli','مشاهدهٔ MAC و پورت‌ها','Switch# show version | include MAC\nSwitch# show mac address-table\nSwitch# show interfaces status\n\nPC> ipconfig /all   ! آدرس MAC را ببین']],
        ios:[['cli','ابزارهای شناسایی لایه ۲','Switch# show version\nSwitch# show mac address-table\nSwitch# show interfaces status\nSwitch# show cdp neighbors detail']],
        diagram:[['svg','osi'],['p','نکته: سوئیچ در لایه ۲ کار می‌کند و فقط به MAC نگاه می‌کند؛ روتر در لایه ۳ و به IP.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — ساخت LAN و مشاهدهٔ MAC',steps:['سه PC + یک سوئیچ در PT بساز','show mac address-table را بعد از ping ببین: کدام MAC به کدام پورت یاد گرفته شد؟','کابل را جابه‌جا کن و جدول را دوباره چک کن ( Aging )']},
          {t:'آزمایشگاه ۲ — تفاوت دامنه‌ها',steps:['هاب (در صورت وجود) یا hub-like را با سوئیچ مقایسه کن','broadcast را capture کن و ببین به چه کسانی می‌رسد','دو سوئیچ زنجیره‌ای: broadcast domain مشترک، collision domain جدا']},
        ]]],
        trouble:[['ul',['لینک up است ولی پینگ نمی‌رود: کابل straight-through vs crossover؟ (امروزه auto-MDI/X اغلب جبران می‌کند)','MAC در جدول نیست: هنوز broadcast/arp نشده — ping کن و دوباره ببین','سرعت 100 بجای 1000: کابل Cat5 یا پورت معیوب — show interfaces counters errors']]],
        exercise:[['ol',['فریم Ethernet را با طول هر بخش از حفظ رسم کن','برای ساختمان ۳ طبقه، نوع کابل هر لینک (مسی/فیبر) را انتخاب و توجیه کن','collision domain و broadcast domain را برای یک توپولوژی ۴ سوئیچی شماره‌گذاری کن']]],
        quiz:[['quiz',[
          {q:'سوئیچ لایه ۲ بر اساس کدام آدرس تصمیم می‌گیرد؟',opts:['IP','MAC','پورت مقصد','DNS'],a:1,exp:'جدول MAC آدرس فیزیکی را به پورت نگاشت می‌کند؛ قاب همان‌جا فوروارد می‌شود.'},
          {q:'هر پورت سوئیچ چند collision domain دارد؟',opts:['صفر','یک','به تعداد VLAN','به تعداد MAC'],a:1,exp:'سوئیچ هر پورت را جدا می‌کند — برخلاف هاب که همه در یک دامنه‌اند.'},
          {q:'مرز broadcast domain با چه چیزی ساخته می‌شود؟',opts:['کابل','VLAN','MAC','FCS'],a:1,exp:'بستهٔ broadcast فقط داخل VLAN خودش می‌ماند — VLAN = مرز دامنهٔ پخش.'},
          {q:'فیبر تک‌حالته معمولاً برای چه؟',opts:['کابل ۵ متری میز','فواصل بلند/شهری','فقط داخل رک','اتصال کیبورد'],a:1,exp:'SMF برد و پهنای باند بیشتری دارد — لینک‌های uplink و مسافت‌های طولانی.'},
        ]]],
        notes:[['ul',['جدول فریم Ethernet و طول بخش‌ها را یک بار از حفظ بنویس','خروجی show mac address-table را برای پنج پورت تفسیر کن']]],
      },
    },
    { id:'fnd-w2', title:'IPv4 عمیق — Subnetting، VLSM و CIDR', sub:'Foundations · هفتهٔ ۲', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'آدرس‌دهی قلب مهندسی شبکه است. این درس را باید طوری تمام کنی که هر نقشهٔ IP را بدون ماشین‌حساب و در کمتر از دو دقیقه بخوانی و بسازی.',
      sec:{
        goal:[['p','در پایان: معنای network/broadcast/usable را حساب می‌کنی، subnetting سریع با /N انجام می‌دهی، VLSM برای نقشهٔ واقعی می‌زنی، و CIDR/Summarization را توضیح می‌دهی.']],
        prereq:[['ul',['هفتهٔ ۱ تمام شده','دهگان و باینری روان','مفهوم شبکه و broadcast از درس قبل']]],
        concept:[['h3','سه عدد کلیدی'],['p','هر subnet سه بخش دارد: Network (هویت شبکه)، Broadcast (آدرس پخش)، Usable (میزبان‌ها بین آن دو). تعداد میزبان = 2^(32-mask) − 2 (دو تای اول و آخر رزرو).'],['h3','روش سریع تقسیم'],['p','به جای باینری‌نویسی طولانی: ببین ماسک چند بیت شبکه دارد؛ 2^(نقطهٔ تقسیم) تا زیرشبکه می‌سازی و هر کدام 2^(باقی‌مانده) − 2 آدرس می‌دهد. تمرین روزانه ۱۰ مسئله تا ملکهٔ ذهن شود.'],['h3','VLSM و Summarization'],['p','VLSM یعنی به هر بخش همان اندازه‌ای بدهی که لازم دارد (سرورخانه /28، کاربران /23) — نه همه /24. Summarization معکوس آن است: چند پیشوند را در یک مسیر خلاصه کن تا جدول روت کوچک بماند.']],
        protocol:[['table',['پیشوند','ماسک','تعداد آدرس','قابل استفاده','کاربرد'],[
          ['/24','255.255.255.0','256','254','یک VLAN معمولی'],
          ['/25','255.255.255.128','128','126','دو نیمهٔ VLAN'],
          ['/26','255.255.255.192','64','62','چهار گروه کوچک'],
          ['/27','255.255.255.224','32','30','اتاق/طبقه'],
          ['/28','255.255.255.240','16','14','سرورها/شبکهٔ مدیریت'],
          ['/30','255.255.255.252','4','2','لینک روتر به روتر'],
        ]],['cli','محاسبه و بررسی','R1(config)# interface g0/0\nR1(config-if)# ip address 192.168.10.65 255.255.255.192\nR1(config-if)# no shutdown\n\nR1# show ip interface brief\nR1# show ip route   ! پیشوند دقیق را در جدول ببین']],
        ios:[['cli','ابزارهای شناسایی لایه ۲','Switch# show version\nSwitch# show mac address-table\nSwitch# show interfaces status\nSwitch# show cdp neighbors detail']],
        diagram:[['svg','encap'],['p','یک /26 را روی کاغذ نصف کن: دو /27 با مرز 128 — این تمرین اصلی هفتهٔ دوم است.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — ۱۰ مسئلهٔ سریع',steps:['۱۰ پیشوند متفاوت (/24 تا /30) در ۲ دقیقه هرکدام: network، broadcast، usable','دو پیشوند را با هم جمع بزنی Summarization درست بدهد؟ تست کن']},
          {t:'آزمایشگاه ۲ — نقشهٔ IP واقعی',steps:['یک شرکت: ۱۲۰ کاربر، ۲۰ سرور، ۸ لینک روتر، ۴ رزرو','نقشه را با VLSM بچین بدون هدر رفت آدرس','همه را در PT پیکربندی و پینگ متقابل کن']},
        ]]],
        trouble:[['ul',['پینگ داخل subnet می‌رود بیرون نه: ماسک را چک کن — ممکن است broadcast را گرفته باشی','دو subnet تداخل دارند: مرزها را روی کاغذ بکش','لینک /30 جواب نمی‌دهد: آدرس مبدأ/مقصد را از usableها انتخاب کن']]],
        exercise:[['ol',['در ۳ دقیقه: 10.20.0.0/22 را به چهار /24 و هر کدام را به دو /25 تقسیم کن','یک VLSM برای ساختمان ۳ طبقه با تعداد کاربر مشخص بنویس','چرا /30 برای لینک روتر انتخاب می‌شود؟']]],
        quiz:[['quiz',[
          {q:'در /27 چند آدرس قابل استفاده داریم؟',opts:['30','32','62','28'],a:0,exp:'2^5=32 کل آدرس؛ منهای network و broadcast → 30 قابل استفاده.'},
          {q:'آدرس 192.168.5.66/26 به کدام subnet تعلق دارد؟',opts:['192.168.5.0/26','192.168.5.64/26','192.168.5.128/26','192.168.5.32/26'],a:1,exp:'گام 64: بلوک‌ها 0/64/128/192 — 66 داخل بلوک 64 تا 127 است.'},
          {q:'VLSM چه فایده‌ای دارد؟',opts:['افزایش سرعت لینک','استفادهٔ بهینه از فضای آدرسی','کاهش تعداد VLAN','حذف روتر'],a:1,exp:'به هر بخش همان اندازه‌ای داده می‌شود که لازم است — هدر رفت آدرس حذف می‌شود.'},
          {q:'Summarization در جدول روت چه می‌کند؟',opts:['تعداد مسیرها را زیاد می‌کند','چند پیشوند را در یک مسیر خلاصه می‌کند','AD را عوض می‌کند','MTU را کم می‌کند'],a:1,exp:'مسیرهای کمتر = جدول کوچک‌تر و جستجوی سریع‌تر — پایهٔ مقیاس شبکه.'},
        ]]],
        notes:[['ul',['هر روز ۱۰ مسئلهٔ subnetting در ۱۰ دقیقه — تا سرعت ۲ دقیقه برسی','نقشهٔ VLSM پروژه را در Git ذخیره کن']]],
      },
    },
    { id:'fnd-w3', title:'پروتکل‌های TCP/IP — TCP، UDP، ARP، ICMP و سرویس‌ها', sub:'Foundations · هفتهٔ ۳', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'بالای آدرس‌دهی، پروتکل‌ها زندگی می‌کنند: TCP قابل‌اعتماد، UDP سریع، ARP پل لایه ۲ و ۳، ICMP پیام‌رسان، و سرویس‌هایی مثل DNS/DHCP/NAT که شبکه را قابل استفاده می‌کنند.',
      sec:{
        goal:[['p','در پایان: handshake سه‌مرحله‌ای TCP را رسم می‌کنی، تفاوت TCP/UDP را با مثال می‌گویی، ARP و ICMP را در capture ردیابی می‌کنی، و نقش DNS/DHCP/NAT را در یک شبکهٔ واقعی توضیح می‌دهی.']],
        prereq:[['ul',['هفتهٔ ۲ تمام شده','پورت و لایه‌ها را می‌شناسی','Wireshark نصب شده']]],
        concept:[['h3','TCP در برابر UDP'],['p','TCP قابل‌اعتماد است: سه‌مرحله‌ای (SYN → SYN-ACK → ACK)، شماره‌گذاری، ACK تأیید و retransmission — برای وب، ایمیل، فایل. UDP سبک است بدون تضمین — برای DNS کوتاه، ویدیو/صدا که تأخیر بدتر از از دست رفتن بسته است.'],['h3','ARP پل دو لایه'],['p','وقتی می‌خواهی به 192.168.1.10 بفرستی ولی لایه ۲ به MAC نیاز دارد، ARP فریاد می‌زند: «192.168.1.10 کجاست؟» و جواب با MAC می‌آید. همین فریاد اولیه در هر subnet دیده می‌شود — در Wireshark.'],['h3','سرویس‌های سه‌گانه'],['p','DNS نام را به IP تبدیل می‌کند؛ DHCP آدرس/ماسک/گیت‌وی/DNS را خودکار می‌دهد (DORA: Discover-Offer-Request-Ack)؛ NAT آدرس‌های خصوصی را در خروجی به عمومی ترجمه می‌کند تا آدرس عمومی صرفه‌جویی شود.']],
        protocol:[['h3','TCP Handshake و مهم‌ترین پورت‌ها'],['ol',['Client: SYN → سرور','سرور: SYN-ACK → کلاینت','Client: ACK → سرور؛ اتصال برقرار','Data: هر طرف شماره‌گذاری و تأیید می‌کند؛ FIN برای بستن']],
          ['table',['پروتکل','پورت','لایهٔ حمل'],[
            ['HTTP','80','TCP'],['HTTPS','443','TCP'],['SSH','22','TCP'],
            ['DNS','53','TCP/UDP'],['DHCP','67/68','UDP'],['ICMP','—','لایه ۳'],
          ]],
        ['cli','مشاهده در CLI و Capture','PC> ping 8.8.8.8\nPC> nslookup google.com\n\n! در Wireshark: filter کن\nicmp or dns or tcp.port==443\n\nR1# show ip arp\nR1# show processes cpu | include ARP']],
        ios:[['cli','ساخت و بررسی subnet','R1# show ip interface brief\nR1# show ip route\nR1# show running-config | include ip address']],
        diagram:[['svg','encap'],['p','یک پینگ را در Wireshark باز کن: ARP، ICMP echo/reply، و DNS query/answer را پشت سر هم ببین — دقیقاً همین ترتیب زندگی یک بسته است.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — TCP در capture',steps:['یک وب‌سیر را باز کن و capture را شروع کن','سه‌مرحله handshake را پیدا و شماره‌گذاری‌ها را بخوان','یک بسته را عمداً گم کن (فلتر) و ببین retransmission می‌آید؟']},
          {t:'آزمایشگاه ۲ — DORA و ARP',steps:['DHCP را با ipconfig /release و /renew در PT اجرا کن','چهار پیام DORA را در capture ببین','ARP برای گیت‌وی را قبل از خروج ببین: who has 192.168.1.1?']},
          {t:'آزمایشگاه ۳ — NAT در عمل',steps:['یک روتر NAT overload بساز','show ip nat translations: قبل/بعد آدرس داخلی و خروجی را مقایسه کن','یک اتصال قطع و وصل کن و عمر ورودی‌ها را ببین']},
        ]]],
        trouble:[['ul',['DNS کار نمی‌کند ولی IP می‌رود: سرور DNS در ipconfig/ DHCP درست؟','ARP نمی‌آید: دو طرف در یک subnet و mask یکسان؟ VLAN یکسان؟','پینگ داخلی رفت بیرون نمی‌رود: گیت‌وی خالی یا NAT rule ناقص']]],
        exercise:[['ol',['TCP و UDP را در جدولی ۶ ستونه مقایسه کن','مراحل DHCP (DORA) را شماره‌گذاری کن و بگو هر پیام چه می‌فرستد','در یک capture، پنج پروتکل پرتکرار را لیست و پورت‌هایشان را بنویس']]],
        quiz:[['quiz',[
          {q:'تفاوت کلیدی TCP و UDP؟',opts:['TCP سریع‌تر است','TCP ترتیب و تأیید دارد، UDP ندارد','UDP فقط برای وب','هر دو قابل‌اعتماد‌اند'],a:1,exp:'TCP با شماره/ACK/timer قابل‌اعتماد است؛ UDP برای تأخیر کم و تحمل از دست رفتن بسته.'},
          {q:'ARP چه چیزی را پیدا می‌کند؟',opts:['IP از نام','MAC از IP','پورت از نام','DNS از MAC'],a:1,exp:'نقشهٔ لایه ۳ به لایه ۲ — بدون آن فریم Ethernet ساخته نمی‌شود.'},
          {q:'چرا NAT مفید است؟',opts:['سرعت را زیاد می‌کند','آدرس عمومی را برای چند دستگاه خصوصی به اشتراک می‌گذارد','DNS را جایگزین می‌کند','UDP را تبدیل به TCP می‌کند'],a:1,exp:'صرفه‌جویی در آدرس عمومی + یک لایهٔ پنهان‌سازی داخلی.'},
          {q:'DNS چه پورتی معمولاً دارد؟',opts:['80','53','22','67'],a:1,exp:'UDP/TCP پورت 53 — جستجوی نام و zone transfer.'},
        ]]],
        notes:[['ul',['یک capture تمیز از ping+DNS+web را در دفترچه نگه دار و برچسب بزن','جدول پورت‌های پرکاربرد را حفظ کن — حداقل ۱۵ تا']]],
      },
    },
    { id:'fnd-w4', title:'ورود به Cisco IOS، معماری دستگاه‌ها و پروژهٔ پایان مبانی', sub:'Foundations · هفتهٔ ۴', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'آخرین هفتهٔ پایه: اولین تماس جدی با CLI سیسکو، فهم معماری روتر/سوئیچ (CPU، حافظه، پورت‌ها، NVRAM)، و یک پروژهٔ کوچک که همهٔ سه هفتهٔ قبل را جمع می‌کند.',
      sec:{
        goal:[['p','در پایان: وارد CLI می‌شوی، حالت‌ها (user/exec/config) را می‌شناسی، یک پیکربندی پایه می‌زنی و ذخیره می‌کنی، خروجی show را می‌خوانی، و پروژهٔ پایان مبانی را تحویل می‌دهی.']],
        prereq:[['ul',['سه هفتهٔ قبل کامل','Packet Tracer یا PNETLab آماده','دفترچهٔ آکادمی شروع شده']]],
        concept:[['h3','معماری دستگاه'],['p','روتر: CPU، RAM (جداول و پیکربندی زنده)، NVRAM (startup-config)، Flash (IOS و فایل‌ها)، و پورت‌ها. سوئیچ لایه ۲ همین‌ها را با MAC table دارد؛ سوئیچ لایه ۳ علاوه بر آن روتینگ. دانستن این حافظه‌ها یعنی فهمیدن «پیکربندی کجا ذخیره می‌شود و چرا بعد از reboot ناپدید می‌شود».'],['h3','حالت‌ها و سلسله‌مراتب'],['p','User EXEC (>) فقط نگاه، Privileged (#) دستورهای show و بیشتر، Global Config (#) تغییرات، و زیرحالت‌ها (interface، router). قانون طلایی: قبل از هر تغییر بدان کجایی؛ بعد از تغییر save کن.']],
        protocol:[['cli','اولین پیکربندی کامل','Router> enable\nRouter# configure terminal\nRouter(config)# hostname R1\nR1(config)# interface g0/0\nR1(config-if)# ip address 192.168.1.1 255.255.255.0\nR1(config-if)# no shutdown\nR1(config-if)# exit\nR1(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.1\nR1(config)# end\nR1# write memory\n\n! خواندن وضعیت\nR1# show ip interface brief\nR1# show running-config\nR1# show startup-config']],
        ios:[['cli','ساخت و بررسی subnet','R1# show ip interface brief\nR1# show ip route\nR1# show running-config | include ip address']],
        diagram:[['svg','topo'],['p','روی نمودار: PC → سوئیچ → روتر → اینترنت؛ برای هر hop بگو کدام لایه و کدام آدرس تصمیم می‌گیرد.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — حالت‌ها و ذخیره',steps:['از > به # به config برو و برگرد','یک hostname و banner بده، سپس write memory و reload — ببین می‌ماند؟','startup-config را پاک کن و reload: دستگاه به حالت اولیه برمی‌گردد؟']},
          {t:'آزمایشگاه ۲ — روتر و سوئیچ پایه',steps:['دو شبکه را به یک روتر وصل و IP بزن','show ip route: مسیرهای C و S را بخوان','یک مسیر استاتیک بنویس و با ping اثبات کن']},
          {t:'آزمایشگاه ۳ — پروژهٔ پایان مبانی',steps:['نقشهٔ IP از هفتهٔ ۲ + VLAN پایه + یک مسیر استاتیک','یک فایل configs.txt از همهٔ دستورها بنویس (تمرین Git)','گزارش ۲ صفحه‌ای: توپولوژی، آدرس‌ها، دستورها، خروجی show']},
        ]]],
        trouble:[['ul',['دستور ناشناخته: دستیابی را چک کن — در حالت config دستور interface اجرا می‌شود نه show','ذخیره نشد: write memory یا copy running-config startup-config زده‌ای؟','پورت up نیست: no shutdown — پیش‌فرض پورت‌ها administratively down است']]],
        exercise:[['ol',['سلسله‌مراتب حالت‌ها را با یک مثال دستی رسم کن','پنج دستور show پرکاربرد و خروجی‌شان را توضیح بده','یک فایل پیکربندی تمیز برای توپولوژی پروژه بنویس']]],
        quiz:[['quiz',[
          {q:'پیکربندی زنده کجاست؟',opts:['NVRAM','RAM (running-config)','Flash','ROM'],a:1,exp:'running-config در RAM است؛ با write memory به NVRAM کپی می‌شود تا بعد از reboot بماند.'},
          {q:'پورت‌ها پیش‌فرض در چه حالتی‌اند؟',opts:['up و working','administratively down','shutdown نرم','روی VLAN 1'],a:1,exp:'تا no shutdown نزنی، پورت up نمی‌شود — دلیل شماره یک «لینک هست ولی کار نمی‌کند».'},
          {q:'کدام حالت دستور show را می‌پذیرد؟',opts:['فقط user EXEC','user و privileged','فقط config','فقط ROMMON'],a:1,exp:'هم در > و هم در # دستورهای show در دسترس‌اند (با دامنهٔ متفاوت).'},
          {q:'بعد از تغییر، برای ماندگاری؟',opts:['reload','write memory','clear ip route *','copy flash tftp'],a:1,exp:'running → startup با write memory؛ وگرنه با reboot برمی‌گردد.'},
        ]]],
        notes:[['ul',['پروژهٔ گزارشی را در Git ذخیره کن — اولین commit رسمی آکادمی','لیست ۱۰ دستور show که هر روز استفاده می‌کنی را بنویس']]],
      },
    },
  ]
},
{
  id:'ccst', num:'۲', title:'دانشکدهٔ ورود — Cisco Entry / CCST', duration:'۲ ماه', tag:'CCST 100-150',
  intro:'مدرک ورود سیسکو (CCST Networking) برای کسی است که می‌خواهد وارد حرفه شود: شناخت تجهیزات، اتصال درست، کار با IOS، پیکربندی پایه و اصول امنیت و نظارت — بدون پیش‌فرض پیشرفته. این دانشکده پل مبانی تا CCNA است.',
  lessons:[
    { id:'ccst-w1', title:'تجهیزات، کابل‌ها و استانداردهای اتصال', sub:'CCST · جلسه ۱', minutes:'۴ جلسه · ۸ ساعت',
      lead:'کار تکنسین شبکه از همین‌جا شروع می‌شود: این دستگاه چیست، چطور وصل می‌شود، و کدام کابل برای کدام لینک. شناخت تجهیزات، سریع‌ترین راه ورود به بازار کار است.',
      sec:{
        goal:[['p','در پایان: انواع دستگاه‌ها (سوئیچ، روتر، AP، firewall، WLC، سرور) و نقش هرکدام را می‌شناسی؛ کابل مسی/فیبر و استانداردهای CAT/SMF/MMF را انتخاب می‌کنی؛ پورت‌ها و اتصالات رایج (RJ45، SFP، Console) را می‌شناسی.']],
        prereq:[['ul',['هیچ پیش‌نیاز فنی الزامی نیست','دانش عمومی رایانه','آمادگی برای کار با دست (کابل‌کشی)']]],
        concept:[['h3','خانوادهٔ تجهیزات'],['p','سوئیچ = اتصال کاربران در LAN؛ روتر = اتصال شبکه‌ها به هم؛ AP/WLC = وایرلس؛ firewall = مرز امنیت؛ سرور = سرویس (DNS، فایل، اپلیکیشن). در یک شرکت کوچک معمولاً روتر+سوئیچ+AP در یک دستگاه ترکیبی‌اند — اما نقش‌ها جداست.'],['h3','کابل‌ها و استانداردها'],['p','مسی Cat5e (1G)، Cat6/6a (1G/10G تا ~۱۰۰ متر). فیبر: MMF برای داخل ساختمان (چندحالته، برد کوتاه‌تر)، SMF برای فواصل بلند. کابل Console (RS-232/USB) برای مدیریت مستقیم دستگاه — اولین ابزار تکنسین.'],['h3','پورت‌ها و اتصالات'],['p','RJ45 برای مسی، SFP/SFP+ برای فیبر/لینک‌های بالا، Console برای مدیریت، و USB/AUX در برخی دستگاه‌ها. ترتیب استاندارد: هر دستگاه را اول با Console ببین، بعد IP بده، بعد لینک‌های شبکه.']],
        protocol:[['table',['تجهیزات','لایه/نقش','اتصال معمولی'],[
          ['Switch','لایه ۲ — LAN','RJ45 به کاربران'],
          ['Router','لایه ۳ — بین شبکه‌ها',' WAN/LAN + SFP'],
          ['Access Point','وایرلس لایه ۲','PoE به سوئیچ'],
          ['WLC','کنترل APها','لینک trunk به هسته'],
          ['Firewall','مرز امنیت','WAN + LAN/DMZ'],
          ['Modem/ONT','اتصال ISP','فیبر/مسی ISP'],
        ]],['cli','اولین تماس Console','! در PC: ترمینال (PuTTY/TeraTerm) با COM یا USB\nSwitch> enable\nSwitch# show version   ! مدل، IOS، حافظه\nSwitch# show interfaces status\nSwitch# show cdp neighbors detail']],
        ios:[['cli','شناسایی دستگاه و لینک‌ها','Switch# show version\nSwitch# show cdp neighbors detail\nSwitch# show interfaces status\nSwitch# show inventory']],
        diagram:[['svg','topo'],['p','نقشهٔ یک دفتر کوچک: ISP → روتر/FW → سوئیچ → کاربران + AP؛ برای هر لینک نوع کابل را بنویس.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — شناسایی تجهیزات',steps:['۵ دستگاه مجازی/تصویری: مدل و نقش هرکدام را بنویس','show version و show cdp neighbors را روی هرکدام بگیر','لینک Console را تمرین کن (یا در PT sim)']},
          {t:'آزمایشگاه ۲ — کابل‌کشی درست',steps:['برای هر اتصال کابل straight/crossover/fiber انتخاب کن','اتصالات را در PT بساز و لینک up را با status ببین','یک کابل خراب عمداً انتخاب کن: علامت‌های خطا را بخوان']},
        ]]],
        trouble:[['ul',['لینک up نیست: کابل درست؟ پورت no shutdown؟ سرعت دوطرفه؟','Console جواب نمی‌دهد: کابل/ترمینال/بود rate (9600) را چک کن','CDP همسایه را نشان نمی‌دهد: لینک یا پورت VLAN اشتباه']]],
        exercise:[['ol',['برای ۲۰ نفر + ۵ AP + ۲ سرور، لیست تجهیزات و کابل‌ها را بنویس','تفاوت MMF و SMF را در یک جدول مقایسه کن','ترتیب اولین بازدید از یک دستگاه جدید را گام‌به‌گام بنویس']]],
        quiz:[['quiz',[
          {q:'کدام دستگاه کاربران دو VLAN را به هم وصل می‌کند؟',opts:['سوئیچ لایه ۲ خالص','روتر (لایه ۳)','هاب','کابل'],a:1,exp:'مرز VLAN با لایه ۳ است — سوئیچ لایه ۲ ترافیک بین VLAN را فوروارد نمی‌کند.'},
          {q:'کابل Console برای چیست؟',opts:['اینترنت','مدیریت مستقیم دستگاه بدون شبکه','PoE','فیبر'],a:1,exp:'دسترسی out-of-band — حتی وقتی IP ندارد یا شبکه قطع است.'},
          {q:'Cat6a حداکثر برای چه لینکی مناسب است؟',opts:['100M تا ۱۰۰متر','10G تا ~۱۰۰متر','فقط فیبر','فقط WAN'],a:1,exp:'10GBase-T روی مسی تا حدود ۱۰۰ متر — استاندارد رایج رک/کاربر.'},
          {q:'در یک دفتر کوچک، AP معمولاً به چه چیزی وصل می‌شود؟',opts:['مستقیم به مودم','PoE سوئیچ','روتر فقط','سرور'],a:1,exp:'PoE هم برق و هم داده را روی یک کابل می‌دهد — تمیزترین نصب وایرلس.'},
        ]]],
        notes:[['ul',['لیست تجهیزات دفتر واقعی خودت یا یک نمونه را بنویس','تصویر پورت‌های جلو/پشت یک سوئیچ را با نام هرکدام علامت بزن']]],
      },
    },
    { id:'ccst-w2', title:'Cisco IOS و عملیات پایه — show، ping، ذخیره و پشتیبان', sub:'CCST · جلسه ۲', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'روز کار یک تکنسین با دستورات ساده شروع می‌شود: وضعیت را ببین، تست کن، ذخیره کن، پشتیبان بگیر. این درس همان مهارت روز اول شغلی است.',
      sec:{
        goal:[['p','در پایان: با CLI راحتی؛ دستورهای show پایه، ping/trace، ذخیرهٔ پیکربندی، خواندن خروجی show running-config، و گرفتن/برگرداندن پشتیبان از TFTP یا فایل را اجرا می‌کنی.']],
        prereq:[['ul',['جلسهٔ ۱ تمام شده','دسترسی به PT یا دستگاه شبیه‌سازی‌شده','مفاهیم IP از مبانی']]],
        concept:[['h3','سه فرمان روزانه'],['p','show برای دیدن، ping برای تست، configure برای تغییر. اکثر مشکلات با همین سه تا شروع می‌شوند؛ تکنسین خوب کسی است که دقیقاً بداند کدام show جواب می‌دهد.'],['h3','ذخیره و پشتیبان'],['p','running-config در RAM است؛ با write memory در NVRAM ماندگار می‌شود. پشتیبان حرفه‌ای: کپی running-config به TFTP/گیت یا export فایل، و نگه‌داشتن نسخه‌های تاریخ‌دار — قبل از هر تغییر بزرگ.']],
        protocol:[['cli','دستورات روزانهٔ تکنسین','Switch> enable\nSwitch# show version\nSwitch# show ip interface brief\nSwitch# show interfaces status\nSwitch# show running-config\n\n! تست\nSwitch# ping 192.168.1.1\nSwitch# traceroute 10.0.0.1\n\n! ذخیره و پشتیبان\nSwitch# write memory\nSwitch# copy running-config tftp:\nAddress or name of remote host? []? 10.10.10.5\nDestination filename [switch-confg]? backup-2026-11-25.cfg\n\n! بازگردانی\nSwitch# copy tftp: running-config']],
        ios:[['cli','وضعیت و پشتیبان','Switch# show ip interface brief\nSwitch# show running-config\nSwitch# show startup-config\nSwitch# copy running-config tftp:']],
        diagram:[['svg','topo'],['p','گردش کار: دستگاه ← show (وضعیت) ← ping (تست) ← تغییر ← write ← پشتیبان — این حلقه را هر روز تکرار کن.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — خواندن وضعیت',steps:['پنج show پرکاربرد را روی سوئیچ بگیر و خروجی را ذخیره کن','از show ip interface brief بگو کدام پورت up/down و چرا','show cdp neighbors را تفسیر کن']},
          {t:'آزمایشگاه ۲ — پشتیبان و بازگردانی',steps:['running-config را به TFTP (یا فایل) کپی کن','تنظیمات را عوض کن، سپس از پشتیبان برگردان','مقایسه کن: همه چیز برگشت؟']},
          {t:'آزمایشگاه ۳ — ping و traceroute',steps:['ping داخل شبکه، تا گیت‌وی، تا اینترنت (در PT)','traceroute مسیر را رسم کن','یک hop قطع بساز و ببین پینگ کجا می‌ایستد']},
        ]]],
        trouble:[['ul',['copy tftp شکست خورد: IP سرور TFTP؟ فایروال؟ نام فایل دقیق؟','ping هدر می‌دهد: گیت‌وی، ماسک، VLAN، و up بودن لینک را مرحله‌ای چک کن','دستور در حالت اشتباه: اول show running-config ببین کجایی، بعد دستور بزن']]],
        exercise:[['ol',['چک‌لیست ۸تایی «بازدید اول از دستگاه» با show ها بنویس','مراحل پشتیبان و بازگردانی را شماره‌گذاری کن','فرق write memory و copy running-config startup-config را توضیح بده']]],
        quiz:[['quiz',[
          {q:'کدام دستور پیکربندی زنده را نشان می‌دهد؟',opts:['show startup-config','show running-config','show flash','show clock'],a:1,exp:'running-config همان چیزی است که الان در RAM اجرا می‌شود.'},
          {q:'برای ماندگاری تغییر بعد از reboot؟',opts:['reload','write memory','clear','erase'],a:1,exp:'ذخیرهٔ running در startup (NVRAM) — وگرنه با reboot برمی‌گردد.'},
          {q:'traceroute چه چیزی را نشان می‌دهد؟',opts:['سرعت لینک','مسیر hop به hop تا مقصد','جدول MAC','لاگ خطاها'],a:1,exp:'لیست روترهای وسط مسیر — اولین ابزار محدودسازی مشکل در شبکه.'},
          {q:'قبل از تغییر بزرگ روی دستگاه تولید؟',opts:['هیچ','پشتیبان گرفتن','reboot','پاک کردن'],a:1,exp:'بدون پشتیبان، rollback وجود ندارد — قانون اول عملیات.'},
        ]]],
        notes:[['ul',['خروجی پنج show را در دفترچه نگه دار و با نمونهٔ سالم مقایسه کن','یک پشتیبان واقعی از پیکربندی یک دستگاه بگیر و تاریخ بزن']]],
      },
    },
    { id:'ccst-w3', title:'پیکربندی پایه، امنیت و نظارت — آمادگی آزمون CCST', sub:'CCST · جلسه ۳', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'جمع‌بندی مسیر Entry: پیکربندی یک دستگاه کوچک از صفر (IP، VLAN ساده، روت پایه)، چند خط امنیت پایه (رمز، پورت، بستن سرویس‌ها)، و آشنایی با نظارت — سپس آزمون ترکیبی.',
      sec:{
        goal:[['p','در پایان: یک سوئیچ/روتر کوچک را کامل پیکربندی می‌کنی (نام، IP، VLAN، مسیر پایه)، امنیت حداقلی می‌زنی (SSH، رمز، بستن سرویس‌های غیرضروری)، با ping و show راستی‌آزمایی می‌کنی، و برای آزمون CCST آماده می‌شوی.']],
        prereq:[['ul',['جلسهٔ ۲ تمام شده','subnetting پایه','کار با حالت‌های CLI روان']]],
        concept:[['h3','یک پیکربندی تمیز'],['p','ترتیب استاندارد: hostname → رمزها → VLAN و IP → مسیر پایه → سرویس‌های لازم → ذخیره و پشتیبان → تست. همین ترتیب در CCNA و بعد هم هست؛ فقط عمق زیاد می‌شود.'],['h3','امنیت پایه (همان کافی برای Entry)'],['p','رمز قوی enable و VTY، غیرفعال کردن HTTP/Telnet (فقط SSH)، shutdown کردن پورت‌های بلااستفاده، و اندازه‌گیری با show. هرکدام یک بند از چک‌لیست hardening است.'],['h3','نظارت پایه'],['p','برای شروع: show log، ping مکرر، و چک کردن وضعیت پورت‌ها. در سطح بالاتر SNMP/Syslog می‌آید — اینجا فقط عادت دیدن داشته باش.']],
        protocol:[['cli','پیکربندی کامل یک دستگاه Entry','Switch# configure terminal\nSwitch(config)# hostname SW1\nSW1(config)# enable secret Str0ngPass!\nSW1(config)# line vty 0 15\nSW1(config-line)# login local\nSW1(config-line)# transport input ssh\nSW1(config-line)# exit\nSW1(config)# username admin secret Str0ngPass!\nSW1(config)# ip domain-name fam.local\nSW1(config)# crypto key generate rsa\nSW1(config)# vlan 10\nSW1(config-vlan)# name USERS\nSW1(config)# interface vlan 10\nSW1(config-if)# ip address 192.168.10.2 255.255.255.0\nSW1(config)# ip default-gateway 192.168.10.1\nSW1(config)# no ip http server\nSW1(config)# end\nSW1# write memory\n\nSW1# show ip interface brief\nSW1# show vlan brief']],
        ios:[['cli','پیکربندی و راستی‌آزمایی','SW1# show ip interface brief\nSW1# show vlan brief\nSW1# show ssh\nSW1# show line\nSW1# show running-config | include secret']],
        diagram:[['svg','vlan'],['p','یک سوئیچ + یک PC در VLAN 10 + گیت‌وی روتر — دقیقاً کوچک‌ترین شبکهٔ قابل تحویل.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — صفر تا صد',steps:['دستگاه خام: hostname، رمز، VLAN، IP، gateway','PC را وصل و ping تا گیت‌وی و تا اینترنت را تست کن','همه را ذخیره و فایل پیکربندی را پشتیبان بگیر']},
          {t:'آزمایشگاه ۲ — hardening پایه',steps:['Telnet/HTTP را ببند و SSH را روشن کن','پورت بلااستفاده را shutdown و توضیح بده','show running-config: چک‌لیست امنیت را تیک بزن']},
          {t:'آزمایشگاه ۳ — آزمون ترکیبی',steps:['۵۰ سؤال مفهومی + ۱۰ مسئله subnetting (زمان‌دار)','یک سناریوی عملی: پیکربندی + عیب‌یابی یک خرابی','نمره و مرور خطاها']},
        ]]],
        trouble:[['ul',['SSH وصل نمی‌شود: crypto key؟ domain-name؟ transport input ssh؟','پورت VLAN آدرس ندارد: interface vlan up؟ IP و gateway درست؟','آزمون قبول نشد: خطاها را دسته‌بندی کن (مفهومی/محاسباتی/عملی) و فقط آن‌ها را مرور کن']]],
        exercise:[['ol',['چک‌لیست hardening ۷بندی برای سوئیچ تازه بنویس','یک پیکربندی کامل را از حفظ و بدون اشتباه روی PT بزن','۲۰ سؤال نمونه CCST با پاسخ توضیحی بنویس']]],
        quiz:[['quiz',[
          {q:'بهترین راه بستن Telnet؟',opts:['رمز سخت‌تر','transport input ssh فقط + غیرفعال کردن http/telnet','حذف VTY','پورت shutdown'],a:1,exp:'مسیر دسترسی را محدود کن: فقط SSH با authenticate محلی.'},
          {q:'IP سوئیچ برای ارتباط بین VLANها؟',opts:['لیاق need نیست','روی interface vlan (SVI) با gateway درست','روی پورت فیزیکی','در startup'],a:1,exp:'SVI به VLAN وصل است؛ بدون gateway داخلی فقط در همان VLAN می‌رود.'},
          {q:'اولین قدم بعد از پیکربندی؟',opts:['reboot','ذخیره و پشتیبان','تغییر رمز دوباره','پاک کردن log'],a:1,exp:'ذخیره + پشتیبان = امکان بازگشت؛ بدون آن هر تغییر مخاطره است.'},
          {q:'اگر در آزمون subnetting گیر کردی؟',opts:['رد شدن از سؤال','برگشت به روش گام‌به‌گام: کل → قابل استفاده → مرزها','حدس زدن','تماس با مربی'],a:1,exp:'روش را دانستن مهم‌تر از سرعت است؛ با روش درست زمان برمی‌گردد.'},
        ]]],
        notes:[['ul',['چک‌لیست hardening و پیکربندی تمیز را در دفترچه قالب‌بندی کن — برای CCNA هم استفاده می‌شود','نمرهٔ آزمون ترکیبی و لیست خطاها را ثبت کن']]],
      },
    },
  ]
},
{
  id:'f1', num:'۱', title:'دانشکدهٔ اول — CCNA کامل', duration:'۵ ماه (ماه ۲ تا ۶)', tag:'مدرک هدف: 200-301 CCNA',
  intro:'این دانشکده شش بخش رسمی آزمون 200-301 را پوشش می‌دهد؛ هر بخش با چهار خروجی اجرا می‌شود: مفهوم، دستور، لاب و عیب‌یابی. حداقل ۲۵ سناریوی عملی الزامی است و پروژهٔ پایان، یک شبکهٔ سازمانی سه‌طبقه با مستندات کامل. شرط عبور: تئوری ۸۵، لاب ۸۵ و تأیید پروژه.',
  lessons:[
    { id:'f1-p1', title:'بخش اول: Network Fundamentals', sub:'CCNA · بخش ۱ از ۶', lessonsCount:'۱۲ موضوع', minutes:'۳ هفته',
      lead:'پایه‌ترین بخش CCNA همان چیزی است که در دانشکدهٔ صفر ساختی؛ اینجا آن را تا سطح استاندارد آزمون بالا می‌آوریم: اجزای شبکه، توپولوژی‌ها، مدل‌ها، Ethernet، آدرس‌دهی دو نسخه، بی‌سیم، کابل‌ها و مجازی‌سازی. تمرکز بر «کاربرد» است، نه فهرست.',
      sec:{
        goal:[['p','شناخت کامل اجزای شبکه (سوئیچ، روتر، AP، WLC، فایروال، سرور) و توپولوژی‌ها؛ تحلیل ارتباط دو دستگاه؛ طراحی آدرس‌دهی IPv4/IPv6 و درک TCP/UDP در برابر پروتکل‌های برنامه.']],
        prereq:[['ul',['دانشکدهٔ صفر (۴ هفته)','آشنایی با Packet Tracer']]],
        concept:[
          ['h3','Network Components و Topologies'],
          ['p','هر شبکه‌ای از چهار جزء ساخته می‌شود: دستگاه‌های انتهایی (Host)، دستگاه‌های انتقال (سوئیچ لایهٔ ۲ و روتر لایهٔ ۳)، رسانه (کابل مسی، فیبر، بی‌سیم) و سرویس‌ها (DNS، DHCP، دسترسی از راه دور). توپولوژی (ستاره‌ای، مش، درختی، هیبرید) شکل اتصال را توصیف می‌کند؛ در دنیای واقعی امروز تقریباً همهٔ LANها ستاره‌ای‌اند و WAN از هیبرید استفاده می‌کند.'],
          ['h3','سوئیچینگ، Ethernet و MAC'],
          ['p','سوئیچ در لایهٔ ۲ کار می‌کند: جدول MAC می‌سازد، فریم را فقط به پورت مقصد می‌فرستد و دامنهٔ برخورد را پورت‌به‌پورت جدا می‌کند. سرعت‌های رایج 10/100/1000 و 10G و استانداردهای 802.3 برای سیم و 802.11 برای بی‌سیم.'],
          ['h3','آدرس‌دهی IPv4 و IPv6'],
          ['p','IPv4 با ماسک و زیرشبکه (دانشکدهٔ صفر) و IPv6 با آدرس‌های Global و Link-Local و SLAAC. در CCNA باید هر دو را هم‌زمان بلد باشی چون پیکربندی‌ها معمولاً دوزبانه‌اند.'],
          ['h3','Wireless، کابل و مجازی‌سازی'],
          ['p','کابل‌های مسی Cat5e/6/6a و فیبرهای Single-mode و Multi-mode با کاربردشان؛ در بی‌سیم: باند، کانال، SSID و تفاوت AP با WLC. مجازی‌سازی (VM، Container، vSwitch) امروز بخشی از شبکه است چون سرور مجازی هم مثل سرور واقعی آدرس و پورت دارد.'],
          ['h3','TCP، UDP و پروتکل‌های برنامه'],
          ['p','نقطهٔ اتصال لایهٔ ۴ به ۷: پورت‌ها. HTTP/HTTPS (80/443)، DNS (53)، DHCP (67/68)، SSH (22)، SMTP (25) و… را باید با پروتکل زیرین (TCP یا UDP) بشناسی — سؤال همیشگی آزمون.']
        ],
        protocol:[['cli','خواندن جدول روت و اتصال','Router# show ip route\nCodes: C - connected, S - static, O - OSPF\nC  192.168.1.0/24 is directly connected, Gi0/0\nS  10.0.0.0/8 [1/0] via 192.168.1.254\n\nPC> ping 192.168.1.1\nPC> nslookup cisco.com']],
        ios:[['cli','مشاهدهٔ اجزا','Switch# show version\nSwitch# show ip interface brief\nSwitch# show mac address-table\nRouter# show cdp neighbors      ! همسایگان لایهٔ ۲\nRouter# show lldp neighbors']],
        diagram:[['svg','topo'],['p','توپولوژی سه‌طبقهٔ پروژهٔ CCNA — در این بخش با نقش هر طبقه آشنا می‌شوی؛ پیاده‌سازی کاملش پروژهٔ پایان است.']],
        lab:[['labs',[{t:'آزمایشگاه ۱ — ساخت شبکهٔ LAN',steps:['یک سوئیچ و ۴ کلاینت بساز','کابل‌ها و وضعیت پورت‌ها را چک کن','با ping ارتباط داخلی و با show cdp همسایگی را اثبات کن']},{t:'آزمایشگاه ۲۳ — Wireshark و Packet Analysis',steps:['ترافیک وب و DNS را capture کن','فیلترها و ستون‌های Info را سفارشی کن','سه پروتکل مختلف را پیدا و مستند کن']}]]],
        trouble:[['ul',['لینک up ولی ارتباط نیست: VLAN پورت، سرعت دوطرفه (auto/auto) و کابل را چک کن','CDP همسایه را نشان نمی‌دهد: لینک فیزیکی یا پورت روی VLAN اشتباه','سرعت 100 مگا بجای 1000: کابل یا پورت معیوب — show interfaces counters errors']]],
        exercise:[['ol',['پنج توپولوژی را رسم کن و برای هر کدام یک کاربرد واقعی بنویس','لیست ۱۰ پورت پرکاربرد با پروتکل زیرینشان','تفاوت collision domain و broadcast domain را برای یک سوئیچ و یک روتر توضیح بده']]],
        quiz:[['quiz',[
          {q:'کدام دستگاه دامنهٔ پخش (broadcast domain) را جدا می‌کند؟',opts:['سوئیچ لایهٔ ۲','هاب','روتر','مودم'],a:2,exp:'روتر مرز لایهٔ ۳ است و broadcast را عبور نمی‌دهد؛ سوئیچ فقط collision domain را جدا می‌کند.'},
          {q:'پورت HTTPS روی کدام پروتکل لایهٔ ۴ است؟',opts:['UDP 443','TCP 443','TCP 80','UDP 80'],a:1,exp:'HTTPS از TCP/443 استفاده می‌کند؛ HTTP روی TCP/80.'}
        ]]],
        notes:[['ul',['فهرست پورت‌ها و پروتکل‌ها را در دفترچهٔ آکادمی جدولی بنویس','هر اصطلاح انگلیسی جدید را با یک مثال فارسی معادل‌سازی کن']]
        ]
      }
    },
    { id:'f1-p2', title:'بخش دوم: Network Access — VLAN و Trunk', sub:'CCNA · بخش ۲ از ۶', minutes:'۴ هفته',
      lead:'قلب عملی CCNA همین‌جاست: سوئیچ، VLAN، Trunk و STP. هدف این است که وقتی گفتند «دو VLAN نباید قاطی شوند»، دقیقاً بدانی چه اتفاقی در کابل می‌افتد و چه دستوری آن را می‌سازد.',
      sec:{
        goal:[['p','پیکربندی VLAN و Access/Trunk/Native VLAN، مسیریابی بین VLANها، EtherChannel با LACP و پایداری STP/RSTP — و عیب‌یابی هر کدام با خروجی واقعی CLI.']],
        prereq:[['ul',['فایل‌های MAC و فریم Ethernet','دانشکدهٔ صفر: آدرس‌دهی زیرشبکه','آزمایشگاه ۱ — ساخت LAN']]],
        concept:[
          ['h3','چرا VLAN؟'],
          ['p','بدون VLAN، هر دستگاه متصل به سوئیچ در یک دامنهٔ پخش بزرگ است: طوفان broadcast، امنیت صفر و انعطاف صفر. VLAN یعنی سوئیچ منطقی را به چند سوئیچ مجازی تکه‌تکه کنی؛ هر تکه یک broadcast domain مستقل. پورتی که فقط به یک VLAN تعلق دارد Access است.'],
          ['h3','Trunk و تگ 802.1Q'],
          ['p','وقتی دو سوئیچ باید چند VLAN را هم‌زمان حمل کنند، لینک بین آن‌ها Trunk می‌شود: هر فریم با یک تگ ۴ بایتی VLAN برچسب می‌خورد تا گیرنده بداند برای کدام VLAN است. Native VLAN همان VLAN بدون تگ است — و اگر دو طرف Native متفاوت داشته باشند، دقیقاً همان جایی است که مهاجمان VLAN hopping را اجرا می‌کنند؛ پس باید روی هر دو طرف یکسان و ترجیحاً غیرفعال باشد.'],
          ['h3','Inter-VLAN Routing'],
          ['p','VLANها قطعه‌قطعه‌اند؛ برای حرف زدن بین آن‌ها یا روتر لازم است (روی هر VLAN یک sub-interface با router-on-a-stick) یا سوئیچ لایهٔ ۳ با SVI. هر دو را باید بسازی.'],
          ['h3','EtherChannel و LACP'],
          ['p','چند لینک موازی بدون EtherChannel توسط STP یکی‌شان مسدود می‌شود؛ با LACP یا PAgP همان لینک‌ها یک لینک منطقی می‌شوند: پهنای باند جمع، افزونگی و بدون حلقه.'],
          ['h3','STP و RSTP'],
          ['p','استپینگ‌تری (STP) جلوی حلقهٔ لایهٔ ۲ را با انتخاب Root Bridge و مسدود کردن یک پورت می‌گیرد؛ RSTP سریع‌تر (ثانیه‌ای) و مدرن‌تر است. در اجرای واقعی، BPDU Guard روی پورت‌های کاربری و Root Guard روی لینک‌های حساس ضروری‌اند.'],
          ['h3','CDP/LLDP و Wireless مقدماتی'],
          ['p','CDP (سیسکو) و LLDP (استاندارد) همسایه‌ها را معرفی می‌کنند؛ در عیب‌یابی لینک، اولین نگاه همین است. در بی‌سیم: SSID، باند، کانال و تفاوت AP مستقل با Lightweight که به WLC وصل می‌شود.']
        ],
        protocol:[
          ['svg','vlan'],
          ['p','در دیاگرام: دو VLAN روی یک لینک Trunk — تگ 802.1Q (۴ بایت: TPID + TCI) هویت هر فریم را حمل می‌کند. بدون تگ، فریم در Native VLAN قرار می‌گیرد.'],
          ['cli','نگاه به تگ در خروجی','Switch# show interfaces trunk\nPort    Mode         Encapsulation   Status        Native vlan\nGi0/1   on           802.1q          trunking      99\n\nSwitch# show interfaces g0/1 switchport\nName: Gi0/1\nMode: trunk\nNegotiation of Trunking: On\nAccess Mode VLAN: 1 (default)\nTrunking Native Mode VLAN: 99 (MANAGEMENT)']
        ],
        ios:[
          ['cli','پیکربندی کامل VLAN و Trunk','Switch(config)# vlan 10\nSwitch(config-vlan)# name STUDENTS\nSwitch(config)# vlan 20\nSwitch(config-vlan)# name VOICE\n\nSwitch(config)# interface range g0/1 - 4\nSwitch(config-if-range)# switchport mode access\nSwitch(config-if-range)# switchport access vlan 10\nSwitch(config-if-range)# spanning-tree portfast\nSwitch(config-if-range)# spanning-tree bpduguard enable\n\nSwitch(config)# interface g0/1\nSwitch(config-if)# switchport mode trunk\nSwitch(config-if)# switchport trunk native vlan 99\nSwitch(config-if)# switchport trunk allowed vlan 10,20,99\n\n! --- Inter-VLAN روی روتر (router-on-a-stick) ---\nRouter(config)# interface g0/0.10\nRouter(config-subif)# encapsulation dot1Q 10\nRouter(config-subif)# ip address 192.168.10.1 255.255.255.0\nRouter(config)# interface g0/0.20\nRouter(config-subif)# encapsulation dot1Q 20\nRouter(config-subif)# ip address 192.168.20.1 255.255.255.0'],
          ['cli','EtherChannel با LACP','Switch(config)# interface range g0/1 - 2\nSwitch(config-if-range)# channel-group 1 mode active\nSwitch(config)# port-channel 1\nSwitch(config-if)# switchport mode trunk'],
          ['note','warn','Native VLAN دو طرف Trunk باید یکسان باشد؛ و بهتر است از VLAN 1 خارج و غیرفعال شود.']
        ],
        diagram:[['svg','vlan'],['p','بالا: دو سوئیچ با Trunk برچسب‌دار — همان چیزی که در show interfaces trunk می‌بینی.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۳ — VLAN و Access Port',steps:['VLAN 10 و 20 بساز و نام بگذار','۴ پورت را access و تقسیم کن','بین دو کلاینت همان VLAN ping و بین دو VLAN عدم ارتباط را اثبات کن','show vlan brief خروجی را مستند کن']},
          {t:'آزمایشگاه ۴ — Trunk و Native VLAN',steps:['لینک بین دو سوئیچ را trunk کن','native vlan 99 تعریف و روی دو طرف یکسان کن','allowed vlan محدود کن و با show interfaces trunk بررسی کن','عمداً native دو طرف را متفاوت کن و با capture ببین چه اتفاقی می‌افتد']},
          {t:'آزمایشگاه ۵ — Inter-VLAN Routing',steps:['روی روتر subinterface با dot1Q بساز','هر VLAN یک gateway بگیرد','بین سه VLAN روتینگ کن و با traceroute مسیر را نشان بده']},
          {t:'آزمایشگاه ۷ — EtherChannel و LACP',steps:['دو لینک را با channel-group active جمع کن','وضعیت port-channel را با show etherchannel چک کن','یک لینک را قطع کن و اثبات کن ارتباط قطع نمی‌شود']}
        ]]],
        trouble:[['ul',['کلاینت VLAN 10 به سرور VLAN 20 نمی‌رسد: gateway تعریف شده؟ SVI/subinterface up است؟','Trunk بالا نمی‌آید: mode access/trunk؟ allowed vlan؟ دو طرف LACP هم‌شکل؟','دستگاه‌های VLAN 1 ناگهان قطع شدند: کسی native را عوض کرده — show interfaces trunk','حلقهٔ STP: کابل اضافی زده؟ با show spanning-tree پورت blocked را پیدا کن']]],
        exercise:[['ol',['یک نقشهٔ ۴ VLANی برای یک دفتر طراحی کن (کاربر، VoIP، سرور، مدیریت) و جدول پورت‌ها را بنویس','چرا LACP بهتر از دو لینک مستقل با STP است؟','آزمون امنیتی: چرا native VLAN پیش‌فرض خطرناک است؟']]],
        quiz:[['quiz',[
          {q:'فریم در Trunk با تگ VLAN 5 — چه اتفاقی برایش می‌افتد؟',opts:['دور انداخته می‌شود','با تگ به گیرنده می‌رسد و گیرنده تگ را برمی‌دارد','به VLAN 1 می‌رود','رمز می‌شود'],a:1,exp:'گیرنده تگ 802.1Q را می‌خواند، فریم را به VLAN مربوطه تحویل می‌دهد و تگ را برای دستگاه انتهایی حذف می‌کند.'},
          {q:'دستور spanning-tree portfast چه می‌کند؟',opts:['سرعت پورت را زیاد می‌کند','پورت را فوراً forwarding می‌کند (بدون listen/learn)','STP را غیرفعال می‌کند','لینک را trunk می‌کند'],a:1,exp:'portfast پورت کاربری را از حالت listen/learn عبور می‌دهد؛ معمولاً با bpduguard همراه می‌شود.'},
          {q:'بهترین راه جلوگیری از VLAN hopping چیست؟',opts:['افزایش تعداد VLANها','یکسان‌سازی و غیرفعال‌سازی Native VLAN غیراستفاده','استفاده از hub','تغییر SSID'],a:1,exp:'حمله روی ناهمسانی یا پیش‌فرض بودن Native VLAN سوار می‌شود؛ یکسان و غیرفعالش کن.'},
          {q:'در router-on-a-stick چه دستوری VLAN را به subinterface وصل می‌کند؟',opts:['ip address','encapsulation dot1Q 10','switchport access vlan','channel-group'],a:1,exp:'encapsulation dot1Q شمارهٔ VLAN را روی subinterface تعریف می‌کند؛ بعد IP می‌دهیم.'}
        ]]],
        notes:[['ul',['خروجی show interfaces trunk و show vlan brief را در دفترچه نگه دار','لیست پورت‌های هر VLAN را برای پروژهٔ نهایی همین‌جا طراحی کن','اشتباه native VLAN را یک بار عمداً بساز و رفعش کن']]
        ]
      },
      faq:[{q:'فرق access port با trunk port در یک جمله؟',a:'access فقط یک VLAN را می‌بیند و تگ ندارد؛ trunk همهٔ VLANهای مجاز را با تگ حمل می‌کند.'},{q:'چرا STP لازم است اگر لایهٔ ۳ روترینگ دارد؟',a:'چون در لایهٔ ۲ حلقه = طوفان broadcast بدون TTL؛ روتر حلقه را نمی‌بیند چون broadcast را عبور نمی‌دهد.'},{q:'Inter-VLAN با سوئیچ لایهٔ ۳ بهتر است یا روتر؟',a:'سوئیچ لایهٔ ۳ (SVI) سریع‌تر و یکپارچه‌تر است؛ router-on-a-stick برای لاب و شبکه‌های کوچک اقتصادی است. هر دو در آزمون هست.'}]
    },
    { id:'f1-p3', title:'بخش سوم: IP Connectivity — استاتیک و OSPF', sub:'CCNA · بخش ۳ از ۶', minutes:'۴ هفته',
      lead:'تا اینجا لایهٔ ۲ را ساختیم؛ حالا باید بسته از شبکه‌ای به شبکهٔ دیگر برود. جدول روت، Longest Prefix Match، روت‌های استاتیک و OSPF تک‌ناحیه در این بخش جمع می‌شوند.',
      sec:{
        goal:[['p','خواندن و ساخت جدول روت، اعمال Longest Prefix Match، پیکربندی روت استاتیک/پیش‌فرض/شناور، و راه‌اندازی OSPF تک‌ناحیه با همسایگی، DR/BDR، AD و متریک — همراه عیب‌یابی.']],
        prereq:[['ul',['زیرشبکه و ماسک (دانشکدهٔ صفر)','لایهٔ ۳ و IP Header','آزمایشگاه‌های ۳ تا ۵']]],
        concept:[
          ['h3','جدول روت و Longest Prefix Match'],
          ['p','روتر برای هر بسته در جدولش دنبال بهترین مسیر می‌گردد؛ اگر چند مسیر همپوشان باشد، بلندترین پیشوند (بیشترین تعداد بیت یکسان) برنده است. جدول از منابع مختلفی پر می‌شود: connected (C)، static (S)، OSPF (O) و… که هرکدام اولویت (Administrative Distance) خودشان را دارند.'],
          ['h3','روت‌های استاتیک، پیش‌فرض و شناور'],
          ['p','استاتیک: «برای رسیدن به این شبکه، از اینجا برو» — ساده و قابل پیش‌بینی، اما بدون افزونگی. روت پیش‌فرض (0.0.0.0/0) یعنی «هر چه نشناختم، از اینجا» — همان گیت‌وی خروج. روت شناور (Floating Static) با AD بالاتر، پشت‌یبانِ پروتکل پویا است: وقتی OSPF قطع شد، بالا می‌آید.'],
          ['h3','OSPF تک‌ناحیه'],
          ['p','OSPF یک پروتکل لینک‌-state است: هر روتر لینک‌هایش را با Hello پیدا می‌کند، LSDB می‌سازد و با الگوریتم Dijkstra بهترین مسیر را حساب می‌کند. برای تشکیل همسایگی، چند شرط لازم است: همان Area، همان Subnet و Mask، همان پورت‌ها (mtu، authentication) و Timers یکسان. نقش DR/BDR در شبکه‌های broadcast کاهش تعداد نشست‌هاست.'],
          ['h3','AD و Metric'],
          ['p','Administrative Distance اعتماد به منبع است (connected=0، static=1، OSPF=110) و Metric هزینهٔ مسیر داخلی همان پروتکل (در OSPF: 10^8 / پهنای باند). وقتی دو مسیر با AD یکسان داری، متریک تصمیم می‌گیرد؛ وقتی AD متفاوت، AD برنده است.']
        ],
        protocol:[
          ['svg','ospf'],
          ['cli','دست زدن به جدول روت','R1# show ip route\nO   10.1.1.0/24 [110/2] via 192.168.12.2, 00:05:22, GigabitEthernet0/0\nS*  0.0.0.0/0 [1/0] via 192.168.12.2\n\nR1# show ip ospf neighbor\nNeighbor ID     Pri   State           Dead Time   Address         Interface\n10.2.2.2          1   FULL/  -       00:00:34    192.168.12.2    GigabitEthernet0/0'],
          ['p','خط O یعنی OSPF، عدد داخل [110/2] یعنی AD=110 و Metric=2. در همسایگی، FULL شدن یعنی دیتابیس‌ها هم‌اند.']
        ],
        ios:[
          ['cli','روت استاتیک و شناور','Router(config)# ip route 172.16.0.0 255.255.0.0 10.0.0.2\nRouter(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.1\n! شناور: AD بالاتر از OSPF (مثلاً 130)\nRouter(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.3 130'],
          ['cli','OSPF تک‌ناحیه','Router(config)# router ospf 1\nRouter(config-router)# router-id 1.1.1.1\nRouter(config-router)# network 192.168.12.0 0.0.0.0 area 0\nRouter(config-router)# network 10.1.1.0 0.0.0.255 area 0\nRouter(config-router)# passive-interface g0/1\n\nR1# show ip ospf interface brief\nR1# show ip protocols'],
          ['note','tip','network با wildcard است: 0.0.0.0 یعنی دقیقاً همان آدرس. اشتباه رایج: netmask به‌جای wildcard.']
        ],
        diagram:[['svg','ospf'],['p','همسایگی سه روتر — HELLO تا FULL و سه جدول (Neighbor، Database، Routing).']],
        lab:[['labs',[
          {t:'آزمایشگاه ۸ — Static Routing',steps:['دو شبکهٔ جدا با یک روتر وصل کن','روت استاتیک دوطرفه بده','با ping و traceroute اثبات کن','بدون روت، بستهٔ unreachable را ببین']},
          {t:'آزمایشگاه ۹ — Default و Floating Route',steps:['روت پیش‌فرض به سمت ISP بساز','روت شناور با AD 130 اضافه کن','لینک اصلی را قطع و بالا آمدن خودکار شناور را اثبات کن']},
          {t:'آزمایشگاه ۱۰ — OSPF Single Area',steps:['روی سه روتر OSPF area 0 با router-id یکتا فعال کن','neighbor را با show ip ospf neighbor تا FULL بررسی کن','MTU و timers را چک کن','یکی از لینک‌ها را قطع و مسیر جایگزین را در جدول ببین']}
        ]]],
        trouble:[['ul',['همسایه FULL نمی‌شود: area/mask/timers یکسان؟ پورت passive نیست؟ MTU یکسان؟','روت استاتیک کار نمی‌کند: next-hop در دسترس است؟ مسیر خروجی درست؟ AD را چک کن','دو مسیر داری و اشتباهی انتخاب می‌شود: LPM را روی پیشوندها حساب کن — گاهی /32 برندهٔ /8 است']]],
        exercise:[['ol',['جدول روتی با ۴ مسیر همپوشان بساز و با LPM برنده را مشخص کن','محاسبهٔ Metric OSPF برای لینک 1Gbps و 100Mbps','چرا روت شناور AD بالاتر می‌خواهد؟']]],
        quiz:[['quiz',[
          {q:'AD روت استاتیک پیش‌فرض چند است؟',opts:['0','1','90','110'],a:1,exp:'static = 1؛ فقط connected (0) از آن مطمئن‌تر است.'},
          {q:'در OSPF Metric چطور حساب می‌شود؟',opts:['تعداد hop','10^8 تقسیم بر پهنای باند','زمان تأخیر صفر','تعداد همسایگان'],a:1,exp:'Cost = Reference Bandwidth / Bandwidth پورت؛ هرچه پهنای باند بیشتر، هزینه کمتر.'},
          {q:'کدام عامل جلوی همسایگی OSPF را می‌گیرد؟',opts:['پورت passive','یکسان بودن router-id','روت داشتن','نام hostname'],a:0,exp:'passive-interface فقط Hello نمی‌فرستد؛ پس همسایگی تشکیل نمی‌شود.'}
        ]]],
        notes:[['ul',['جدول AD همهٔ منابع را حفظ کن (متداول‌ترها: 0،1،90،110،170)','خروجی show ip route را رنگی و توضیح‌دار کن']]
        ]
      }
    },
    { id:'f1-p4', title:'بخش چهارم: IP Services', sub:'CCNA · بخش ۴ از ۶', minutes:'۳ هفته',
      lead:'سرویس‌هایی که شبکه را «قابل استفاده» می‌کنند: DHCP با relay، DNS، NAT/PAT، NTP برای هم‌زمانی، SNMP و Syslog برای دیدن، QoS برای اولویت‌بندی، SSH برای مدیریت، FHRP برای گیت‌وی افزوده و Port Mirroring برای تحلیل.',
      sec:{
        goal:[['p','پیکربندی و عیب‌یابی سرویس‌های لایهٔ ۳/۴ شبکه؛ درک نقش هر کدام در یک شبکهٔ واقعی و اثبات رفتارشان با خروجی CLI یا capture.']],
        prereq:[['ul',['دانشکدهٔ صفر: DNS/DHCP/NAT/SSH','روتینگ استاتیک و OSPF','آزمایشگاه‌های ۱۱، ۱۲، ۱۷']]],
        concept:[
          ['h3','DHCP و Relay'],
          ['p','DHCP چهار پیام DISCOVER/OFFER/REQUEST/ACK را برای آدرس‌دهی خودکار می‌فرستد؛ در شبکه‌های چند-VLAN چون broadcast به بیرون نمی‌رود، با ip helper-address (DHCP Relay) پیام را به سرور مرکزی می‌رسانیم. سرور علاوه بر IP، ماسک، گیت‌وی، DNS و Lease را می‌دهد.'],
          ['h3','NAT و PAT'],
          ['p','NAT آدرس خصوصی را عمومی می‌کند؛ PAT (Overload) با پورت‌ها ده‌ها کلاینت را پشت یک IP می‌نشاند. سه نوع: static (برای سرور داخلی)، dynamic pool و overload پرکاربردترین.'],
          ['h3','NTP، SNMP و Syslog'],
          ['p','NTP ساعت دستگاه‌ها را هم‌زمان می‌کند (بدون آن، لاگ‌ها بی‌معنا می‌شوند). SNMP نسخهٔ ۳ امن است و وضعیت را می‌خواند؛ Syslog خطاها را به سرور مرکزی می‌فرستد. ترکیب هر سه = چشم و حافظهٔ شبکه.'],
          ['h3','QoS Fundamentals و FHRP'],
          ['p','QoS با علامت‌گذاری (DSCP/CoS) ترافیک حساس مثل VoIP را جلوی صف می‌نشاند. FHRP (HSRP/VRRP/GLBP) دو روتر را پشت یک گیت‌وی مجازی جمع می‌کند تا خرابی روتر اول قطعی ندهد.'],
          ['h3','Port Mirroring (SPAN)'],
          ['p','با SPAN ترافیک یک پورت را روی پورت تحلیل کپی می‌کنیم تا Wireshark بدون وصل فیزیکی، ترافیک را ببیند — پل اجباری بین «دیدن» و «عیب‌یابی».']
        ],
        protocol:[['cli','چهار سرویس کلیدی','! DHCP Relay\nRouter(config)# interface vlan 20\nRouter(config-if)# ip helper-address 10.10.10.20\n\n! NAT Overload\nRouter(config)# access-list 1 permit 192.168.0.0 0.0.0.255\nRouter(config)# interface g0/0\nRouter(config-if)# ip nat outside\nRouter(config)# interface g0/1\nRouter(config-if)# ip nat inside\nRouter(config)# ip nat inside source list 1 interface g0/0 overload\n\n! HSRP\nRouter(config)# interface g0/0\nRouter(config-if)# standby 1 ip 192.168.1.254\nRouter(config-if)# standby 1 priority 110\nRouter(config-if)# standby 1 preempt\n\n! SPAN\nSwitch(config)# monitor session 1 source interface g0/3\nSwitch(config)# monitor session 1 destination interface g0/10']],
        ios:[['cli','مشاوره‌ها','Router# show ip nat translations\nRouter# show ip dhcp binding\nRouter# show standby brief\nSwitch# show monitor session 1\nRouter# show ntp status\nRouter# show logging']],
        diagram:[['svg','topo'],['p','لبهٔ شبکه: NAT بیرون، DHCP/DNS داخل، HSRP روی دو روتر گیت‌وی و SPAN روی سوئیچ — همین چهار جعبه، خدمات این بخش‌اند.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱۱ — DHCP Server و Relay',steps:['pool با network/default-router/dns','helper-address در VLAN دیگر','رزرو IP و بررسی binding']},
          {t:'آزمایشگاه ۱۲ — NAT و PAT',steps:['inside/outside و overload','چند کلاینت پشت یک IP خروجی','static NAT برای یک سرور داخلی']},
          {t:'آزمایشگاه ۱۵ — HSRP',steps:['دو روتر با standby group و priority','preempt و تست failover با قطع روتر اول','بررسی با show standby brief']},
          {t:'آزمایشگاه ۲۱ و ۲۲ — SNMP و NTP',steps:['SNMPv3 با کاربر امن','NTP server/client و هم‌زمانی','Syslog به سرور مرکزی و خواندن لاگ']}
        ]]],
        trouble:[['ul',['کلاینت IP نمی‌گیرد: helper-address، pool و وضعیت پورت VLAN را چک کن','NAT کار نمی‌کند: inside/outside جا به جا؟ ACL مبدأ را می‌گیرد؟','ساعت دستگاه اشتباه: NTP reachability — لاگ‌ها را قابل اعتماد نکن','HSRP فعال نمی‌شود: گروه و پورت یکسان؟ preempt؟']]],
        exercise:[['ol',['یک IP Plan برای سه VLAN با DHCP مرکزی و relay بنویس','سه تفاوت static NAT و dynamic و overload را در جدول','چرا بدون NTP، تحلیل Syslog شکست می‌خورد؟']]],
        quiz:[['quiz',[
          {q:'ip helper-address دقیقاً چه می‌کند؟',opts:['روت پیش‌فرض می‌دهد','broadcast های خاص (مثل DHCP) را unicast به سرور می‌فرستد','NAT می‌کند','DNS را کش می‌کند'],a:1,exp:'relay یعنی broadcast مرز VLAN را رد نمی‌کند؛ helper آن را به سرور دور می‌رساند.'},
          {q:'کدام QoS برای VoIP مناسب‌تر است؟',opts:['بهترین کلاس Best Effort','اولویت (Priority queuing) برای کلاس EF','بدون علامت‌گذاری','افزایش queue depth'],a:1,exp:'صدا تأخیر را تحمل نمی‌کند؛ EF با priority queue همیشه اول سرویس می‌گیرد.'}
        ]]],
        notes:[['ul',['خروجی show ip nat translations و show standby brief را نمونه‌وار ثبت کن','پورت‌های SPAN و نحوهٔ وصل Wireshark را تمرین کن']]
        ]
      }
    },
    { id:'f1-p5', title:'بخش پنجم: Security Fundamentals', sub:'CCNA · بخش ۵ از ۶', minutes:'۳ هفته',
      lead:'امنیت در CCNA یعنی چند لایهٔ ساده اما اجباری: رمز محکم، ACL برای فیلتر، Port Security برای کنترل دسترسی لایهٔ ۲، DHCP Snooping و DAI برای دفاع از LAN و 802.1X برای ورود کنترل‌شده.',
      sec:{
        goal:[['p','تهدیدهای رایج را شناختن، ACL استاندارد و گسترش‌یافته را نوشتن، hardening دستگاه و دفاع‌های لایهٔ ۲ (Port Security، Snooping، DAI) را پیاده‌سازی کردن، و VPN و 802.1X را مفهومی فهمیدن.']],
        prereq:[['ul',['پورت‌ها و پروتکل‌ها','روتینگ و VLAN','دانشکدهٔ صفر: SSH']]],
        concept:[
          ['h3','تهدید و AAA'],
          ['p','تهدید رایج LAN:شنود (Sniffing)، ARP Spoofing، DHCP Rogue، دسترسی فیزیکی غیرمجاز و حملات رمز. AAA چارچوب پاسخ است: Authentication (کیستی؟)، Authorization (چه کاری؟) و Accounting (چه کردی؟) با TACACS+ (سیسکو، پورت جدا) یا RADIUS (استاندارد، پورت 1812).'],
          ['h3','ACL — درِ ورودی'],
          ['p','ACL لیستی از قواعد است که روی بسته اعمال می‌شود؛ از بالا به پایین می‌خوانده، اولین تطبیق برنده است و در انتها implicit deny. استاندارد (شماره ۱ تا ۹۹) فقط آدرس مبدأ را می‌بیند؛ گسترش‌یافته (100-199 و 2000-2699) پروتکل و پورت و مقصد را هم. جایگذاری: «near the source برای استاندارد، near the destination برای گسترش‌یافته».'],
          ['h3','Hardening و Port Security'],
          ['p','پسورد enable، سطوح line، غیرفعال کردن سرویس‌های بی‌استفاده (http server، CDP روی پورت کاربری)، no ip unreachables و فقط SSH. Port Security تعداد MAC مجاز هر پورت را محدود می‌کند و با violation shutdown یا protect واکنش نشان می‌دهد.'],
          ['h3','DHCP Snooping و DAI'],
          ['p','Snooping جدول اعتماد (IP ↔ MAC ↔ پورت) می‌سازد و پورت‌های کاربری را «untrusted» می‌کند تا سرور قلابی جواب ندهد. DAI با همان جدول، ARPهای دروغین را فیلتر می‌کند؛ IP Source Guard هم آدرس مبدأ را کنترل می‌کند. این سه، واکسن LAN در برابر spoofing هستند.'],
          ['h3','802.1X و VPN'],
          ['p','802.1X ورود کنترل‌شدهٔ پورت را با Supplicant/Authenticator/Server سه‌طرفه می‌کند؛ VPN (IPsec یا SSL) تونل رمزگذاری‌شدهٔ امن از راه دور می‌سازد — پایهٔ هر کار از راه دور امن.']
        ],
        protocol:[['cli','ACL در عمل','! استاندارد: فقط مبدأ\nRouter(config)# access-list 10 deny 192.168.1.100\nRouter(config)# access-list 10 permit any\nRouter(config)# interface g0/0\nRouter(config-if)# ip access-group 10 in\n\n! گسترش‌یافته: مبدأ، مقصد، پروتکل، پورت\nRouter(config)# ip access-list extended BLOCK_WEB\nRouter(config-acl)# deny tcp host 192.168.1.50 host 10.10.10.80 eq 80\nRouter(config-acl)# deny tcp host 192.168.1.50 host 10.10.10.80 eq 443\nRouter(config-acl)# permit ip any any\nRouter(config-acl)# exit\nRouter(config)# interface g0/1\nRouter(config-if)# ip access-group BLOCK_WEB out\n\n! Port Security\nSwitch(config)# interface g0/3\nSwitch(config-if)# switchport port-security\nSwitch(config-if)# switchport port-security maximum 2\nSwitch(config-if)# switchport port-security violation shutdown\n\n! DHCP Snooping\nSwitch(config)# ip dhcp snooping\nSwitch(config)# ip dhcp snooping vlan 10,20\nSwitch(config)# interface g0/3\nSwitch(config-if)# ip dhcp snooping trust        ! فقط پورت سرور/سوئیچ\n\n! DAI\nSwitch(config)# ip arp inspection vlan 10,20']],
        ios:[['cli','بررسی امنیتی','Switch# show port-security\nSwitch# show port-security address\nSwitch# show ip dhcp snooping binding\nSwitch# show ip arp inspection statistics vlan 10\nRouter# show access-lists']],
        diagram:[['p','نقشهٔ لایه‌های دفاع: فیزیکی (پورت) ← لایهٔ ۲ (PortSec/Snooping/DAI) ← لایهٔ ۳ (ACL) ← دسترسی (AAA/802.1X) ← تونل (VPN). هر لایه بدون لایهٔ پایین بی‌معناست.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱۳ — Standard ACL',steps:['ACL شماره‌ای با deny مشخص و permit any','در نزدیک‌ترین نقطهٔ مبدأ اعمال کن','با ping اثبات کن چه کسی رد شد و چه کسی نه','show access-lists ترتیب تطبیق را نشان می‌دهد']},
          {t:'آزمایشگاه ۱۴ — Extended ACL',steps:['فیلتر ترافیک وب به یک سرور خاص','شمارش hit counter برای اثبات','جابه‌جایی to/from و دیدن تفاوت نتیجه']},
          {t:'آزمایشگاه ۱۸ — Port Security',steps:['maximum 2 و violation shutdown','اتصال سومین MAC و دیدن err-disable','بازیابی با errdisable recovery']},
          {t:'آزمایشگاه ۱۹ و ۲۰ — DHCP Snooping و DAI',steps:['Snooping و trust/untrust','ساخت ARP دروغین و فیلتر شدن با DAI','binding table را با show ببین']}
        ]]],
        trouble:[['ul',['ACL اعمال شد ولی ترافیک همچنان می‌رود: implicit permit در انتهای لیست نداری؟ ترتیب قواعد؟','به خودت lock out شدی: always یک permit برای management از مسیر امن در اول لیست','err-disable پورت: show port-security violation — مهاجم یا loop؟','ARP دروغین با DAI رد نشد: binding کامل است؟ پورت trust؟']]],
        exercise:[['ol',['ACL بنویس: فقط VLAN 10 به سرور HTTP دسترسی دارد، بقیه نه','سه خط hardening استاندارد برای یک سوئیچ تازه اضافه‌شده','چرا DAI بدون Snooping کار نمی‌کند؟']]],
        quiz:[['quiz',[
          {q:'ACL استاندارد چه چیزی را بررسی نمی‌کند؟',opts:['آدرس مبدأ','پورت مقصد','هر دو','هیچ‌کدام'],a:1,exp:'استاندارد فقط آدرس مبدأ (و در بعضی موارد مبدأ+مقصد طبقه‌ای) را می‌بیند؛ پورت نه.'},
          {q:'پس از همهٔ قواعد ACL چه اتفاقی می‌افتد؟',opts:['permit همه','deny همه (implicit deny)','بسته دور انداخته نمی‌شود','به مبدأ برمی‌گردد'],a:1,exp:'implicit deny any در انتهای هر ACL هست — به همین دلیل همیشه permit صریح لازم است.'},
          {q:'کدام ویژگی جلوی ARP Spoofing را می‌گیرد؟',opts:['STP','Dynamic ARP Inspection','PortFast','EtherChannel'],a:1,exp:'DAI با جدول Snooping، ARPهای مغایر با binding را رد می‌کند.'}
        ]]],
        notes:[['ul',['قالب hardening شخصی‌ات را برای هر دستگاه بنویس و به آن پایبند باش','هر ACL را با hit counter مستند کن']]
        ]
      }
    },
    { id:'f1-p6', title:'بخش ششم: Automation and Programmability', sub:'CCNA · بخش ۶ از ۶', minutes:'۲ هفته',
      lead:'شبکه‌های امروز با CLI تک‌به‌تک مدیریت نمی‌شوند؛ SDN، کنترلرها، REST API و JSON پایهٔ اتوماسیون‌اند. در CCNA همین‌قدر که مفهوم، ساختار و یک نمونهٔ واقعی را ببینی کافی است — عمق عملی در دانشکدهٔ Automation می‌آید.',
      sec:{
        goal:[['p','تفاوت مدل سنتی با کنترلر-محور، فهم SDN و DNA Center/Catalyst Center، خواندن یک پاسخ REST API به‌صورت JSON، و درک نقش اتوماسیون و AI در شبکهٔ مدرن.']],
        prereq:[['ul',['کار با CLI و پیکربندی دستی','مفاهیم لایه‌ها و API چیست؟','آشنایی مقدماتی با HTTP']]],
        concept:[
          ['h3','Traditional vs Controller-Based'],
          ['p','در مدل سنتی هر دستگاه مستقل تصمیم می‌گیرد (چرخشی ۳۰ دستگاه × ۲۰ دقیقه). در مدل کنترلر-محور، یک سیاست مرکزی (Controller) تعریف می‌شود و دستگاه‌ها اجرا می‌کنند: تغییر در ثانیه‌ها، نه ساعت‌ها.'],
          ['h3','SDN و سه لایه'],
          ['p','SDN سه لایه دارد: داده (Data Plane — انتقال بسته)، کنترل (Control Plane — تصمیم‌گیری با کنترلر) و مدیریت (Management Plane — پیکربندی و مانیتور). DNA Center / Catalyst Center سیاست‌محور (Policy-Based) شبکه‌های سیسکو را از یک داشبورد مدیریت می‌کند.'],
          ['h3','REST API و JSON'],
          ['p','REST یعنی با HTTP و متدهای GET/POST/PUT/DELETE روی «منابع» کار کنی؛ خروجی معمولاً JSON است — همان آرایه‌ها و جفت‌کلید-مقدارهایی که در فایل‌های پیکربندی جدید می‌بینی. یک GET ساده می‌تواند وضعیت هزار پورت را در یک ثانیه بدهد.'],
          ['h3','Configuration Management و AI'],
          ['p',' Ansible/Terraform/Python تغییرات را تکرارپذیر و نسخه‌دار می‌کنند (با Git). AI/ML در شبکه برای الگویابی ترافیک، پیش‌بینی خرابی و پیشنهاد رفع به کار می‌رود — جایی که انسان نمی‌تواند میلیون‌ها نمونه را ببیند.']
        ],
        protocol:[['cli','یک REST API واقعی با cURL','GET https://sandboxdnacenter.com/dna/intent/api/v1/network-device\nHeaders: X-Auth-Token: <token>\n\n{\n  "response": [\n    {\n      "hostname": "access-sw-01",\n      "reachabilityStatus": "Reachable",\n      "platformId": "C9300"\n    }\n  ]\n}'],
          ['cli','از CLI تا API','! پیکربندی سنتی\nSwitch(config)# vlan 30\n\n! همان تغییر با RESTCONF (مفهومی)\nPATCH /restconf/data/...\nContent-Type: application/yang-data+json\n\n{"vlan":{"id":30}}']],
        ios:[['cli','ابزارهای مشاهده','Switch# show running-config | section vlan\n! خروجی JSON مانند (در دستگاه‌های مدرن):\nSwitch# show interfaces brief | format json']],
        diagram:[['p','سه لایهٔ SDN: Management (سیاست و داشبورد) ← Control (کنترلر تصمیم می‌گیرد) ← Data (بسته را جابه‌جا می‌کند). در مدل سنتی هر سه در خودِ دستگاه‌اند.']],
        lab:[['labs',[{t:'آزمایشگاه — اولین API شبکه',steps:['یک سندسند devnet sandbox وصل شو (حساب رایگان)','اولین GET را با cURL بزن و JSON را بخوان','یک تغییر را با POST/PATCH اعمال و با show تأیید کن','نتیجه را در Git مستند کن']}]]],
        trouble:[['ul',['401 Unauthorized: توکن یا header اشتباه است','404: مسیر منابع را با مستندات API چک کن','تغییر اعمال نشد: مدل دستگاه از آن منبع YANG پشتیبانی نمی‌کند — show version + مستندات']]],
        exercise:[['ol',['تفاوت Data و Control و Management Plane را با یک مثال CLI بنویس','یک نمونهٔ JSON از خروجی show خودت بساز','چرا Git برای پیکربندی شبکه لازم است؟']]],
        quiz:[['quiz',[
          {q:'در SDN، کدام لایه تصمیم مسیر را می‌گیرد؟',opts:['Data Plane دستگاه‌ها','Control Plane کنترلر','Management Plane کاربر','لایهٔ فیزیک'],a:1,exp:'کنترلر (مثل DNA Center یا SDN controller) سیاست و مسیر را مرکزی تصمیم می‌گیرد و به دستگاه‌ها می‌دهد.'},
          {q:'کدام متد HTTP یک منبع را می‌خواند؟',opts:['GET','POST','DELETE','PATCH'],a:0,exp:'GET = خواندن؛ POST = ساختن؛ PUT/PATCH = ویرایش؛ DELETE = حذف.'},
          {q:'JSON در شبکه عمدتاً چه نقشی دارد؟',opts:['روتینگ لایهٔ ۳','قالب دادهٔ API ها و خروجی‌ها','جایگزین CLI','استاندارد کابل'],a:1,exp:'JSON زبان مشترک API هاست تا اسکریپت‌ها بتوانند داده را پردازش کنند.'}
        ]]],
        notes:[['ul',['یک حساب DevNet Sandbox بساز و اولین API را همین هفته بزن','تفاوت سه لایهٔ SDN را با نقشهٔ ساده ثبت کن']]
        ]
      }
    },
    { id:'f1-labs', title:'آزمایشگاه‌های الزامی CCNA — ۲۵ سناریو', sub:'خروجی: مستندات و فایل تنظیمات', minutes:'۲۵ × ۵۰ دقیقه',
      lead:'شرط عبور از دانشکدهٔ CCNA: حداقل ۲۵ سناریوی عملی با مستندات کامل (فایل تنظیمات + خروجی‌ها + گزارش یک‌صفحه‌ای). هر سناریو یک مهارت را از «ساخت» تا «عیب‌یابی» پوشش می‌دهد.',
      sec:{
        goal:[['p','اجرای ۲۵ سناریوی زیر در Packet Tracer یا PNETLab، با ثبت خروجی show هر مرحله و گزارش یک‌صفحه‌ای برای هرکدام. نمرهٔ لاب: حداقل ۸۵.']],
        prereq:[['ul',['بخش‌های ۱ تا ۶ CCNA پیش رفته باشند','دفترچهٔ آکادمی و قالب گزارش']]],
        concept:[['p','لاب‌ها تصادفی نیستند: ردیف ۱ تا ۵ ساخت و اتصال، ۶ تا ۱۰ روتینگ، ۱۱ تا ۱۲ سرویس، ۱۳ تا ۱۵ امنیت و دسترسی، ۱۶ تا ۲۲ پیکربندی پیشرفتهٔ خدمات و امنیت، ۲۳ تا ۲۵ تحلیل و عیب‌یابی ترکیبی. اگر سناریویی را بدون مستندات اجرا کنی، انجام‌نشده حساب می‌شود.']],
        protocol:[['table',['شماره','آزمایشگاه','مهارت کلیدی'],[
          ['۱','ساخت شبکهٔ LAN','کابل، پورت، تست ارتباط'],
          ['۲','IP Addressing و Subnetting','VLSM و جدول IP Plan'],
          ['۳','VLAN و Access Port','تفکیک پخش'],
          ['۴','Trunk و Native VLAN','802.1Q و امنیت'],
          ['۵','Inter-VLAN Routing','router-on-a-stick / SVI'],
          ['۶','STP و Root Bridge','انتخاب ریشه و blocked'],
          ['۷','EtherChannel و LACP','لینک منطقی و افزونگی'],
          ['۸','Static Routing','روت دستی دوطرفه'],
          ['۹','Default و Floating Route','خروج و پشتیبان'],
          ['۱۰','OSPF Single Area','همسایگی و جدول'],
          ['۱۱','DHCP Server و Relay','آدرس‌دهی خودکار چند VLAN'],
          ['۱۲','NAT و PAT','خصوصی به عمومی'],
          ['۱۳','Standard ACL','فیلتر مبدأ'],
          ['۱۴','Extended ACL','فیلتر پروتکل/پورت'],
          ['۱۵','HSRP','گیت‌وی افزوده'],
          ['۱۶','IPv6 و SLAAC','آدرس‌دهی نسل دو'],
          ['۱۷','SSH و Hardening','مدیریت امن'],
          ['۱۸','Port Security','کنترل MAC پورت'],
          ['۱۹','DHCP Snooping','دفاع از DHCP'],
          ['۲۰','DAI','دفاع از ARP'],
          ['۲۱','SNMP و Syslog','دیدن و لاگ'],
          ['۲۲','NTP','هم‌زمانی ساعت'],
          ['۲۳','Wireshark و Packet Analysis','دیدن بسته'],
          ['۲۴','WLAN مقدماتی','SSID و AP'],
          ['۲۵','عیب‌یابی شبکهٔ ترکیبی','ترکیب همهٔ مهارت‌ها']
        ]]],
        ios:[['note','tip','قالب گزارش هر لاب: هدف ← توپولوژی (اسکرین‌شات) ← مراحل ← خروجی show کلیدی ← مشکل احتمالی و رفعش ← یک بند «چه یاد گرفتم».']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'استاندارد قبولی هر سناریو',steps:['اجرا بدون راهنمای قدم‌به‌قدم (فقط برای بار اول نگاه می‌کنی)','خروجی showهای کلیدی ثبت شده باشد','یک خطای عمدی ایجاد و رفع شده باشد','فایل .pkt یا پیکربندی کامل ذخیره شده باشد']}]]],
        trouble:[['ul',['سناریو ۲۵ ترکیبی است: اگر قبلاً ۲۴ تا را مستند نکرده باشی، اینجا گیر می‌کنی — مرور کن، نه حفظ','اگر لابی دو بار نیاز به راهنما داشت، آن مهارت را در دفترچه علامت «نیاز به تکرار» بزن']]],
        exercise:[['ol',['از ۲۵ لاب، سه موردی که بیشتر درشان گیر کردی را لیست کن و برای هرکدام یک تکرار ۳۰ دقیقه‌ای برنامه‌ریزی کن']]],
        quiz:[['quiz',[
          {q:'شرایط قبولی آزمایشگاه CCNA چیست؟',opts:['هر نمره‌ای','حداقل ۸۵ از ۱۰۰ + مستندات','فقط اجرا','فکس گزارش'],a:1,exp:'هم نمرهٔ حداقل ۸۵، هم تکمیل مستندات الزامی — نمره جایگزین انجام نمی‌شود.'},
          {q:'کدام سناریو مهارت‌های همهٔ بخش‌ها را جمع می‌کند؟',opts:['سناریوی ۳','سناریوی ۲۵','سناریوی ۱','سناریوی ۱۰'],a:1,exp:'عیب‌یابی ترکیبی (۲۵) آخرین آزمون عملی دانشکده است.'}
        ]]],
        notes:[['ul',['وضعیت ۲۵ لاب را در جدول پیشرفت علامت بزن (localStorage داشبورد)','هر فایل تنظیمات را با نام سناریو در Git ذخیره کن']]
        ]
      }
    },
    { id:'f1-proj', title:'پروژهٔ پایان CCNA — شبکهٔ سازمانی سه‌طبقه', sub:'خروجی: طراحی + اجرا + عیب‌یابی + مستندات', minutes:'۲ هفته',
      lead:'آزمون بزرگ دانشکدهٔ CCNA: یک شبکهٔ واقعی از صفر تا مستندات. یک Core Switch، دو Distribution، چهار Access، چهار VLAN، روتینگ، سرویس‌ها و امنیت — همه با هم، مثل پروژهٔ واقعی.',
      sec:{
        goal:[['p','طراحی، پیاده‌سازی و عیب‌یابی شبکهٔ سه‌طبقه با مشخصات زیر + مستندات کامل (IP Plan، نقشه، پیکربندی، گزارش). شرط قبولی: تأیید طراحی، اجرا و عیب‌یابی.']],
        prereq:[['ul',['۲۵ آزمایشگاه الزامی','نمرهٔ تئوری حداقل ۸۵','نمرهٔ لاب حداقل ۸۵']]],
        concept:[
          ['h3','مشخصات الزامی'],
          ['ul',['یک Core Switch (لایهٔ ۳)','دو Distribution Switch','چهار Access Switch','VLAN های مدیریت، کاربران، سرورها و VoIP','Inter-VLAN Routing','OSPF تک‌ناحیه (حداقل)','DHCP مرکزی با Relay','NAT در لبه','ACL دسترسی سرور','HSRP برای گیت‌وی','مستندسازی کامل شبکه']],
          ['h3','معیار تأیید'],
          ['p','طراحی (IP Plan و نقشه) باید قبل از پیکربندی تأیید شود؛ اجرا باید بدون خطای پایدار (ping بین همهٔ VLANها، خروجی show سالم)؛ عیب‌یابی یعنی سه خطای عمداً واردشده (مثلاً native VLAN ناهمسان، روت اشتباه، ACL بیش از حد) را پیدا و رفع کنی.']
        ],
        protocol:[['svg','topo'],['p','نقشهٔ نهایی: Core وسط، دو Distribution با افزونگی، چهار Access زیر هر کدام — دقیقاً همان چیزی که در مستندات تحویل می‌دهی.']],
        ios:[['cli','نمونهٔ بخشی از پیکربندی نهایی','! Inter-VLAN روی Core\nCore(config)# interface vlan 10\nCore(config-if)# ip address 192.168.10.1 255.255.255.0\n\n! OSPF بین Core و Distribution\nCore(config)# router ospf 1\nCore(config-router)# network 10.0.0.0 0.0.0.3 area 0\n\n! HSRP روی گیت‌وی کاربران\nDist-A(config)# interface vlan 10\nDist-A(config-if)# standby 10 ip 192.168.10.254\nDist-A(config-if)# standby 10 priority 110\nDist-A(config-if)# standby 10 preempt']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'چک‌لیست تحویل پروژه',steps:['IP Plan تأییدشده (جدول VLAN/Subnet/Range/Gateway)','نقشهٔ فیزیکی و منطقی','پیکربندی کامل هر دستگاه (فایل جدا)','گزارش عیب‌یابی ۳ خرابی عمداً','فایل نهایی در Git با تاریخچهٔ commit']}]]],
        trouble:[['ul',['پروژه گیر می‌کند: از پایین به بالا بررسی کن — لینک، VLAN، IP، روت، سرویس، ACL','اختلاف نمرهٔ لاب و تئوری: اگر تئوری ۸۵ شد ولی لاب نه، پروژه را شروع نکن — اول لاب']]],
        exercise:[['ol',['قبل از اجرا، یک صفحه «Risk» بنویس: سه احتمال خرابی و راه‌حلشان']]],
        quiz:[['quiz',[
          {q:'شرط عبور از دانشکدهٔ CCNA؟',opts:['فقط آزمون تئوری ۸۵','تئوری ۸۵ + لاب ۸۵ + تأیید پروژه','فقط پروژه','حضور منظم'],a:1,exp:'سه پای شرط با هم؛ نمرهٔ بالا جایگزین بخش‌های الزامی نمی‌شود.'},
          {q:'کدام VLAN معمولاً HSRP می‌خواهد؟',opts:['VLAN سرور فقط','هر VLAN کاربری با گیت‌وی دو روتری','VLAN مدیریت تک‌روتری','VLAN خالی'],a:1,exp:'گیت‌وی کاربران باید افزوده باشد تا خرابی یک روتر شبکه را نخواباند.'}
        ]]],
        notes:[['ul',['نمرات تئوری/لاب/پروژه را در داشبورد ثبت کن','گواهی داخلی دانشکدهٔ CCNA پس از تأیید صادر می‌شود (جایگزین مدرک رسمی Cisco نیست)']]
        ]
      }
    }
  ]
},
{
  id:'f2', num:'۲', title:'دانشکدهٔ دوم — مسیریابی و سوئیچینگ پیشرفته', duration:'۶ ماه', tag:'R&S',
  intro:'پس از CCNA نوبت به عمق می‌رسد: OSPF چندناحیه، EIGRP، BGP مقدماتی، IPv6 کامل، MPLS و مهارت حل مسئله. هدف این دانشکده این است که مهندس بتواند مسیر یک بسته را از لحظه تولید تا مقصد با دست بگیرد و دلیل انتخاب هر مسیر را توضیح دهد.',
  lessons:[
    { id:'f2-l1', title:'OSPF چندناحیه و LSA Types', sub:'ریشه‌های پیشرفته · جلسه ۱', minutes:'۴ جلسه · ۸ ساعت',
      lead:'OSPF در CCNA با یک ناحیه و چند کلمه دستور تمام شد؛ اما شبکه واقعی ده‌ها ناحیه دارد و هر LSA نوعی از واقعیت را روایت می‌کند. این جلسه: معماری چندناحیه، انواع LSA، و مهارت طراحی منطقه‌بندی.',
      sec:{
        goal:[['p','شامل: Area 0 و ناحیه‌های غیرمتمرکز، انواع LSA (۱ تا ۵ و ۷)، ABR و ASBR، Summarization، طراحی منطقه‌بندی.']],
        prereq:[['ul',['دانشکدهٔ CCNA و OSPF تک‌ناحیه','تبانی DR/BDR را می‌شناسی','مبانی subnetting روان است']]],
        concept:[['h3','چرا چندناحیه؟'],['p','تک‌ناحیه یعنی همهٔ LSAها در یک اقیانوس — هر تغییر link همه را به لرزه درمی‌آورد (SPF دوباره). ناحیه‌بندی = تقسیم فضای LSDB و مهار موج SPF.'],['h3','نقش ABR و ASBR'],['p','ABR (Area Border Router) پل دو ناحیه است و LSA نوع ۳ می‌سازد؛ ASBR (Autonomous System Boundary Router) مسیرهای خارجی (مثل static redistributed) را با LSA نوع ۵ وارد می‌کند.']],
        protocol:[['h3','انواع LSA (حفظی-کاربردی)'],['table',['LSA','سازنده','دامنه','نقش'],[
          ['Type 1','هر Router','ناحیهٔ خودش','نقشهٔ لینک‌ها و روترهای ناحیه'],
          ['Type 2','DR','ناحیه','لیست روترهای شبکهٔ چنددسترسی'],
          ['Type 3','ABR','بین ناحیه‌ها','خلاصهٔ پیشوندهای ناحیهٔ دیگر'],
          ['Type 4','ABR','تا ASBR','مسیر تا ASBR (فقط برای external)'],
          ['Type 5','ASBR','کل AS','پیشوندهای خارجی (redistribute)'],
          ['Type 7','DR ناحیهٔ NSSA','NSSA','مثل Type 5 داخل NSSA']],
        ]],
        ios:[['cli','چندناحیه + Summarization','R1(config)# router ospf 1\nR1(config-router)# network 10.0.0.0 0.0.0.255 area 0\nR1(config-router)# network 10.0.1.0 0.0.0.255 area 1\nR1(config-router)# area 1 range 10.0.1.0 255.255.255.0\n\nR2(config)# router ospf 1\nR2(config-router)# area 1 stub\n\n! بررسی\nR2# show ip ospf database\nR2# show ip ospf border-routers']],
        diagram:[['svg','ospf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — سه ناحیه',steps:['R1/R2/R3 زنجیره‌ای: Area0 — Area1 — Area2','به هر ناحیه دو LAN بده و تحویل بین‌ناحیه را تست کن','area range را روی ABR ببند و show ip ospf database را مقایسه کن']},
          {t:'آزمایشگاه ۲ — Stub و NSSA',steps:['ناحیهٔ لبه را stub کن: رد شدن LSA5 را قبل/بعد ببین','NSSA طراحی کن و Type 7→5 را در ABR ردیابی کن','summarize مسیرهای stub و شمردن LSAها با show ip ospf database summary']},
          {t:'آزمایشگاه ۳ — تعمیر مسیر',steps:['یک link را down کن و زمان بازیابی (SPF throttle) را اندازه بگیر','metric دستی بده و مسیر جایگزین را مجبور به انتخاب کن']},
        ]]],
        trouble:[['ul',['ناحیه‌ها FULL نمی‌شوند: هلو/Dead یکسان؟ Authentication یکسان؟ MTU یکسان؟','ASBR نمایان نمی‌شود: LSA4 نیست — ABR مسیر تا ASBR را ندارد','Summary اعمال نشد: summarize باید روی ABR و مرز ناحیه باشد، نه هر روتر']]],
        exercise:[['ol',['برای شبکه‌ای با ۵ ناحیه نقشهٔ منطقه‌بندی بکش و ABRها را مشخص کن','جدول LSA ۱..۷ را از حفظ برای یک کاربر بنویس','بگو چرا NSSA به Type 7 نیاز دارد']]],
        quiz:[['quiz',[
          {q:'LSA نوع ۳ را چه کسی می‌سازد؟',opts:['هر روتر','DR','ABR','ASBR'],a:2,exp:'ABR خلاصهٔ ناحیهٔ دیگر را با Type 3 بین ناحیه‌ها می‌برد.'},
          {q:'در ناحیهٔ Stub چه LSA ای حذف می‌شود؟',opts:['Type 1','Type 2','Type 3','Type 5'],a:3,exp:'Stub ناحیهٔ لبه است: مسیرهای خارجی Type 5 وارد نمی‌شوند و جایگزین به ABR ختم می‌شود.'},
          {q:'ASBR کیست؟',opts:['روتر منطقهٔ ۰','روتری که مسیر خارجی redistribute می‌کند','سوئیچ لایهٔ ۳','ABR اولیه'],a:1,exp:'ASBR مسیرهای خارجی (static/EGP/BGP) را داخل OSPF تزریق می‌کند و Type 5 می‌سازد.'},
          {q:'دستور area range چه می‌کند؟',opts:['لینک را خلاصه می‌کند','پیشوندهای یک ناحیه را در Type 3 خلاصه می‌کند','metric را جمع می‌کند','ناحیه را می‌بندد'],a:1,exp:'Summarization در ABR: به جای هر پیشوند، یک مسیر خلاصه رد می‌شود — LSDB سبک‌تر، تکان کمتر.'},
        ]]],
        notes:[['ul',['LSA 1-7 را روی کاغذ رسم کن و برای هرکدام یک مثال بزن','خروجی show ip ospf database را نگه دار و Typeها را شماره‌گذاری کن']]],
      },
    },
    { id:'f2-l2', title:'EIGRP و مبانی BGP', sub:'ریشه‌های پیشرفته · جلسه ۲', minutes:'۴ جلسه · ۸ ساعت',
      lead:'EIGRP مسیریابی سیسکو با FDiffusing Update است؛ BGP دروازهٔ اینترنت است. هر دو با یک سؤال در آمده‌اند: این مسیر از کجا آمد و چرا برنده شد؟',
      sec:{
        goal:[['p','شامل: EIGRP (Neighbors، DUAL، Variance، Stub)، BGP (Neighbor، iBGP/eBGP، Attributeهای پایه، Route-Map).']],
        prereq:[['ul',['OSPF چندناحیه تمام شده','جدول AD و Metric را داری','مفهوم مسیر پیشوندی روان است']]],
        concept:[['h3','EIGRP سه پرسش'],['p','EIGRP فقط می‌پرسد: همسایه کیست؟ مسیر فایزیبل چیست؟ مسیرهای feasible successor کجاست؟ اگر مسیر اصلی رفت و مقادیر Feasible Distance پشتی را ندید، EIGRP دوباره جستجو می‌کند (Diffusing Update).'],['h3','BGP — پروتکل مسیر سیاست'],['p','BGP مسیر «بهترین» را با معیار تکنیکی مثل پاسخگویی نمی‌سنجد؛ با سیاست: AS-Path (کوتاه‌تر = بهتر)، Local-Preference، MED و سیاست اپراتور. BGP روترهای AS را به هم وصل می‌کند، نه هاست‌ها را.']],
        protocol:[['cli','EIGRP و BGP کنار هم','! EIGRP\nR1(config)# router eigrp 100\nR1(config-router)# network 10.0.0.0\nR1(config-router)# variance 2\nR1(config-router)# eigrp stub\n\n! BGP eBGP\nR1(config)# router bgp 65001\nR1(config-router)# neighbor 10.10.10.2 remote-as 65002\nR1(config-router)# network 192.168.0.0 mask 255.255.0.0\n\n! اعمال سیاست روی مسیر ورودی\nR1(config)# route-map SET_LP permit 10\nR1(config-route-map)# set local-preference 200\nR1(config-router)# neighbor 10.10.10.2 route-map SET_LP in']],
        ios:[['cli','بررسی EIGRP/BGP','R1# show ip eigrp neighbors\nR1# show ip eigrp topology\nR1# show ip protocols\n\nR1# show ip bgp summary\nR1# show ip bgp\nR1# show ip route bgp']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — EIGRP DUAL',steps:['دو مسیر موازی بساز، successor و feasible successor را با show ip eigrp topology ببین','یک لینک را down کن: بدون Query شبکه برگشت؟','variance 2 بده و load-balancing واقعی را ببین']},
          {t:'آزمایشگاه ۲ — BGP ساده',steps:['دو AS شبیه‌سازی (65001/65002) و neighbor حالت Established','show ip bgp: مسیر و Next-hop و AS-Path را بخوان','local-preference را روی یک مسیر ورودی بزن و مسیر خروجی عوض شد را ببین']},
        ]]],
        trouble:[['ul',['neighbor حالت Idle می‌ماند: AS-Remote یا IP/ACL اشتباه است','EIGRP همسایه نمی‌شود: AS number یکسان؟ network درست؟ hello مسدود نشده؟','BGP مسیر یکسان رد نمی‌شود: اول next-hop reachability داخل IGP را چک کن']]],
        exercise:[['ol',['سه معیار بهترین مسیر BGP را به ترتیب اولویت بنویس','EIGRP Stub چه نوع Query را کور می‌کند و چرا؟','یک route-map بنویس که مسیرهای AS 65500 را نپذیرد']]],
        quiz:[['quiz',[
          {q:'EIGRP از چه الگوریتمی استفاده می‌کند؟',opts:['Dijkstra','DUAL','Bellman-Ford','Spanning Tree'],a:1,exp:'DUAL مسیر فایزیبل را با کمترین FD نگه می‌دارد و بدون تکان مسیر پشتی می‌سازد.'},
          {q:'معیار اول بهترین مسیر BGP چیست؟',opts:['MED','AS-Path کوتاه‌تر','Local-Preference','_hop count'],a:1,exp:'پیش از هر چیز AS-Path کوتاه‌تر = مسیر از AS کمتری عبور کرده (ساده‌شدهٔ قاعدهٔ اصلی).'},
          {q:'eigrp stub چه می‌کند؟',opts:['تحلیل DUAL را غیرفعال می‌کند','Query از روتر stub نمی‌آید/نمی‌رود','مسیرها را summarize می‌کند','BGP را باز می‌کند'],a:1,exp:'Stub یعنی این روتر فقط مسیرهای محلی/متصل و summarize را اعلام می‌کند — Query در لبه می‌میرد.'},
          {q:'iBGP و eBGP در چه فرق دارند؟',opts:['پروتکل متفاوت','remote-as هم‌سیستم در برابر بیگانه','پورت متفاوت','نیاز به IGP ندارد'],a:1,exp:'iBGP داخل یک AS، eBGP بین دو AS؛ معمولاً iBGP full-mesh می‌خواهد یا Route-Reflector.'},
        ]]],
        notes:[['ul',['جدول AD: EIGRP=90، OSPF=110، eBGP=20 را حفظ کن','خروجی show ip bgp و show ip eigrp topology را تفسیر محور بنویس']]],
      },
    },
    { id:'f2-l3', title:'IPv6 کامل در عمل', sub:'ریشه‌های پیشرفته · جلسه ۳', minutes:'۴ جلسه · ۸ ساعت',
      lead:'IPv6 فقط آدرس بلندتر نیست: SLAAC، NDP جای ARP را گرفته، دیگر Broadcast نداریم، و امنیت در هسته است. مهندس امروز باید هر طرحی را دوزبانه (v4/v6) ببیند.',
      sec:{
        goal:[['p','شامل: ساختار آدرس، انواع (GUA/ULA/LA)، SLAAC و ND RA/RD/NS/NA، Dual-Stack، تونل‌های ساده، امنیت NDP.']],
        prereq:[['ul',['IPv4 و subnetting کامل',' OSPF چندناحیه را دیده‌ای','مفاهیم MAC و ARP را می‌دانی']]],
        concept:[['h3','ساختار آدرس'],['p','۱۲۸ بیت به شکل هشت گروه هگزادسیمی (مثلاً 2001:db8::1). پیشوند شبکه + Interface Identifier. انواع کلیدی: GUA (عمومی، قابل مسیریابی)، ULA (fd00::/8 — معادل private)، Link-Local (fe80::/10 — فقط لینک، پایهٔ NDP).'],['h3','NDP جای ARP'],['p','به جای ARP Broadcast: Node با RA (Router Advertisement) پیشوند را یاد می‌گیرد (SLAAC)، آدرس را DAD تأیید می‌کند، و با NS/NA مک یک IP را می‌پرسد. چون broadcast نیست، پخش کنترل‌شده با multicast (ff02::) انجام می‌شود.']],
        protocol:[['cli','پیکربندی و بررسی IPv6','R1(config)# ipv6 unicast-routing\nR1(config)# interface g0/0\nR1(config-if)# ipv6 address 2001:db8:1::1/64\nR1(config-if)# ipv6 ospf 1 area 0\n\nPC>\nipconfig /all          ! آدرس GUA و fe80 و default gateway از RA\nR1# show ipv6 neighbors   ! معادل ARP cache\nR1# show ipv6 ospf neighbor\n\n! آدرس‌دهی stateless (SLAAC) روی لینک\nR1(config-if)# ipv6 nd ra interval 200']],
        ios:[['cli','دستورهای کلیدی IPv6','R1# show ipv6 interface brief\nR1# show ipv6 neighbors\nR1# show ipv6 route\nR1# show ipv6 ospf interface\n\nPC> ping6 -n 3 2001:db8:1::2\nPC> tracert6 2001:db8:2::1']],
        diagram:[['svg','encap']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — Dual-Stack',steps:['روی دو روتر v4+v6 هم‌زمان و OSPF دو فامیلی','ping6 بین دو سمت و پینگ v4 را هم‌زمان تست کن','NDP را با show ipv6 neighbors مشاهده کن']},
          {t:'آزمایشگاه ۲ — RA و DAD',steps:['ra interval را کم کن و لحظهٔ رسیدن RA را در Wireshark ببین','یک آدرس تکراری دستی بده و پیام Duplicate Address Detection را ببین','ULA و GUA را روی یک هاست مقایسه کن']},
        ]]],
        trouble:[['ul',['ping به link-local جواب نمی‌دهد: scope-id لازم است (fe80::1%Gig0/0)','همسایه IPv6 نمی‌آید: ipv6 unicast-routing فعال نشده یا RA فیلتر شده','مسیر v6 دیده نمی‌شود: OSPFv3 روی interface صراحتاً فعال شود']]],
        exercise:[['ol',['یک طرح Dual-Stack با پیشوندهای GUA و ULA برای دفتر بنویس','گام‌های SLAAC را به ترتیب شماره‌گذاری کن','چرا DAD قبل از استفاده از آدرس لازم است؟']]],
        quiz:[['quiz',[
          {q:'آدرس Link-Local چه پیشوندی دارد؟',opts:['2000::/3','fd00::/8','fe80::/10','::1/128'],a:2,exp:'fe80::/10 فقط داخل لینک است و پایهٔ NDP و مسیریابی همسایگی است.'},
          {q:'ARP در IPv6 با چه جایگزین شد؟',opts:['ICMPv6 NDP','DHCPv6','DNS','EtherType'],a:0,exp:'NDP (Neighbor Discovery) روی ICMPv6 با NS/NA و RA/RS کار می‌کند — بدون broadcast.'},
          {q:'SLAAC چیست؟',opts:['آدرس‌دهی stateful با سرور','یادگیری پیشوند از RA و ساخت آدرس خودکار','روش فشرده‌سازی آدرس','تونل v6 در v4'],a:1,exp:'روتر RA می‌دهد، هاست پیشوند + IID (EUI-64 یا تصادفی) را می‌سازد — بدون DHCP لازم.'},
          {q:'پیشوند ULA معادل چیست در v4؟',opts:['Public','Loopback','Private (10/8 و...)','Multicast'],a:2,exp:'fd00::/8 برای آدرس‌دهی داخلی بدون قابل مسیریابی عمومی.'},
        ]]],
        notes:[['ul',['جدول انواع آدرس v6 را با یک مثال عددی بنویس','خروجی ipconfig و show ipv6 neighbors را برای دفترچه عکس/کپی کن']]],
      },
    },
    { id:'f2-l4', title:'MPLS L3VPN مفهومی و QoS', sub:'ریشه‌های پیشرفته · جلسه ۴', minutes:'۴ جلسه · ۸ ساعت',
      lead:'اپراتورها و سازمان‌های بزرگ ترافیک را برچسب می‌زنند (MPLS) و کیفیت سرویس را می‌خرند (QoS). این جلسه مسیر لایهٔ ۳ لجستیک سازمانی و صف‌بندی عادلانه را می‌بندد.',
      sec:{
        goal:[['p','شامل: LDP و Label Switching، VRF و Route Distinguisher، L3VPN (PE-CE) مفهومی، و QoS: دسته‌بندی، marking، شکل‌دهی صف (WFQ/LLQ).']],
        prereq:[['ul',['BGP و OSPF چندناحیه','مفهوم Routing Table و VRF (l3 مبانی)','lایه‌های encapsulation را می‌دانی']]],
        concept:[['h3','MPLS در یک جمله'],['p','روترهای هسته (LSR) به جای نگاه به جدول IP، فقط به برچسب (Label) نگاه می‌کنند: ورودی → جدول label → خروجی با swap/pop. LDP برچسب‌ها را بین LSRها توزیع می‌کند.'],['h3','VRF و VPN'],['p','در PE، هر مشتری جدول مسیریابی جدا دارد (VRF) تا آدرس‌های تکراری دو مشتری هم‌زیست شوند. Route Distinguisher آدرس خصوصی را یکتا می‌کند؛ RD:IPv4 = VPNv4. L3VPN یعنی PE با CE روترهای لایهٔ ۳ می‌نشیند و مسیر مشتری را در همان VRF می‌بیند.'],['h3','QoS چهار اقدام'],['p','Classification (شناستن ترافیک با DSCP/IP Prec) → Marking (برچسب در سر بسته) → Queuing (صف عادلانه: LLQ برای صدا، WFQ برای بقیه) → Shaping/Policing (کنترل نرخ).']],
        protocol:[['cli','علامت‌گذاری و صف','! شناستن ترافیک صدا و علامت‌گذاری\nR1(config)# class-map match-any VOICE\nR1(config-cmap)# match dscp ef\nR1(config)# policy-map WAN\nR1(config-pmap)# class VOICE\nR1(config-pmap-c)# priority percent 10\nR1(config)# interface g0/0\nR1(config-if)# service-policy output WAN\n\n! MPLS LDP\nR1(config)# mpls ldp router-id Loopback0 force\nR1(config-if)# mpls ip']],
        ios:[['cli','بررسی MPLS و QoS','R1# show mpls ldp neighbor\nR1# show mpls forwarding-table\nR1# show policy-map interface g0/0\nR1# show class-map\nR1# show vrf']],
        diagram:[['svg','ospf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — صف صدا',steps:['iperf ترافیک بساز و هم‌زمان RTP شبیه‌سازی کن','LLQ با priority percent ده درصد ببند','تأخیر صدا (delay) را با و بدون policy مقایسه کن']},
          {t:'آزمایشگاه ۲ — VRF ساده',steps:['دو VRF با آدرس تکراری 10.0.0.0/8 روی یک PE بساز','ping بین VRFها باید شکست بخورد؛ import/export با RT شبیه‌سازی کن','show ip route vrf و show vrf مسیرها را ببین']},
        ]]],
        trouble:[['ul',['سیاست اعمال نمی‌شود: class-map match با DSCP روی همان interface خروجی؟','صدا هنوز قطع می‌شود: LLQ جای enough bandwidth ندارد — policer سر صدا را می‌زند','بین دو PE مسیر VPN نیست: RT import/export نمی‌خورد یا MP-BGP up نیست']]],
        exercise:[['ol',['یک طرح QoS برای WAN با سه کلاس (صدا، کنترل، دانلود) بنویس','چرا آدرس تکراری دو مشتری در یک روتر لایهٔ ۳ بدون VRF ممکن نیست؟','تفاوت Shaping و Policing را با یک مثال صف بیان کن']]],
        quiz:[['quiz',[
          {q:'کلاس بهترین برای VoIP در DSCP چیست؟',opts:['CS0','EF','AF31','BE'],a:1,exp:'EF ( Expedited Forwarding) معمولاً برای صدا علامت می‌خورد و priority queue می‌گیرد.'},
          {q:'VRF چه مشکلی را حل می‌کند؟',opts:['کشش پورت','جداسازی جداول مسیریابی چند مستأجر','سرعت لینک','امنیت لینک'],a:1,exp:'هر مشتری routing table خودش را دارد؛ آدرس تکراری بدون تداخل.'},
          {q:'برچسب MPLS در کجا خوانده می‌شود؟',opts:['در لایه ۲ فقط','در شاهین بین لایه ۲ و ۳ (shim)','در Payload TCP','در هاست مقصد'],a:1,exp:'MPLS label یک شاهین ۴ بایتی بین Ethernet header و Payload است — لایه ۲.۵.'},
          {q:'چرا LLQ به VoIP داده می‌شود؟',opts:['چون کوچک است','چون تأخیر/جانبازی کم می‌خواهد','چون UDP دارد','چون گران است'],a:1,exp:'صدا حساس به تأخیر است؛ priority queue به شرط پهنای باند کافی، delay را پایین نگه می‌دارد.'},
        ]]],
        notes:[['ul',['یک معماری QoS سه کلاسی برای سازمان خودت رسم کن','MPLS label stack را در یک لینک دستی بکش: push/swap/pop']]],
      },
    },
    { id:'f2-labs', title:'آزمایشگاه‌های الزامی R&S — ۲۰ سناریوی پیشرفته', sub:'ریشه‌های پیشرفته · کارگاه', minutes:'۳ جلسه · ۶ ساعت',
      lead:'شرط عبور از دانشکدهٔ R&S: بیست سناریوی زیر را با گزارش مهندسی (قبل/بعد، خروجی CLI، علت انتخاب مسیر) تحویل دهی.',
      sec:{
        goal:[['p','اجرای ۲۰ سناریوی پیشرفته و تحویل گزارش فنی هرکدام.']],
        prereq:[['ul',['چهار درس قبلی','دفترچهٔ LSA/AD پر شده','پلتفرم PT/PNETLab/EVE آماده']]],
        concept:[['p','تفاوت این سطح با CCNA: در CCNA «بالا بیاید» کافی بود؛ اینجا باید بتوانی «چرا این مسیر انتخاب شد» و «با تغییر کدام پارامتر مسیر عوض می‌شود» را با خروجی نشان دهی.']],
        protocol:[['table',['شماره','سناریو','مهارت کلیدی'],[
          ['1','OSPF چهارناحیه با ABR/ASBR','LSA و Summarization'],
          ['2','Stub/NSSA و فیلتر Type5','کنترل مسیر خارجی'],
          ['3','EIGRP variance و Feasible Successor','بارگذاری چندمسیره'],
          ['4','EIGRP Stub در لبه','مهار Query'],
          ['5','iBGP با Route-Reflector','مقیاس BGP داخل AS'],
          ['6','eBGP با AS-Path prepend','مهندسی ترافیک خروجی'],
          ['7','Local-Preference در ورودی','انتخاب مسیر ورودی'],
          ['8','IPv6 Dual-Stack end-to-end','هم‌زیستی v4/v6'],
          ['9','SLAAC + NDP در Wireshark','بسته‌بندی واقعی'],
          ['10','IPv6 OSPFv3','مسیریابی v6'],
          ['11','LLQ برای VoIP','Queueing'],
          ['12','Shaping در WAN مشتری','کنترل نرخ'],
          ['13','VRF با آدرس تکراری','چندمستأجری'],
          ['14','MPLS label در capture','شاهین لایه ۲.۵'],
          ['15','Redistribution دوطرفه با route-map','کنترل تزریق'],
          ['16','Filter-list و route tagging','جلوگیری از حلقه'],
          ['17','Floating static پشت OSPF','مسیر پشتیبان'],
          ['18','DHCPv6-PD ساده','آدرس‌دهی خودکار v6'],
          ['19','Syslog/NTP/SNMP روی روترهای چندناحیه','عملیات'],
          ['20','عیب‌یابی ترکیبی: قطعی یک ناحیه','تحلیل چندپروتکلی'],
        ]]],
        ios:[['note','key','گزارش هر سناریو: ۱) توپولوژی ۲) دستورهای کلیدی ۳) خروجی show قبل/بعد ۴) توضیح انتخاب مسیر ۵) اگر پارامتر را عوض کنم چه می‌شود؟']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'استاندارد قبولی',steps:['اجرای واقعی در PT/PNETLab/EVE-NG','خروجی‌ها در دفترچه','توضیح شفاهی یک سناریو برای مربی یا ضبط ویدیو']}]]],
        trouble:[['ul',['گیر چندناحیه: با show ip ospf neighbor و show ip ospf database مرحله به مرحله برو','گیر redistribution: همیشه route-map و tag را چک کن','گیر BGP: اول show ip bgp summary ببین دقیقاً در کدام state ایستاده']]],
        exercise:[['ol',['سه سناریویی که بیشتر گیر کردی را عیب‌یابی ریشه‌ای کن','یک گزارش نمونهٔ کامل از سناریو ۱۰ بنویس']]],
        quiz:[['quiz',[
          {q:'شرط عبور این دانشکده چیست؟',opts:['خواندن یک کتاب','۲۰ سناریو با گزارش مهندسی','حفظ فرمان‌ها','تماشای ویدیو'],a:1,exp:'اجرا + گزارش + توضیح مهندسی، نه فقط «بالا آمده».'},
          {q:'در گزارش چه چیزی از همه مهم‌تر است؟',opts:['رنگ ترمینال','تحلیل چرا این مسیر انتخاب شد','تعداد دستور','طول گزارش'],a:1,exp:'مهارت نهایی تفسیر است: علت انتخاب مسیر و پیش‌بینی رفتار با تغییر پارامتر.'},
        ]]],
        notes:[['ul',['وضعیت ۲۰ سناریو را در جدول پیشرفت علامت بزن','هر خروجی را در Git ذخیره کن']]],
      },
    },
    { id:'f2-proj', title:'پروژهٔ پایان R&S — هستهٔ سه‌ناحیه‌ای', sub:'ریشه‌های پیشرفته · پروژه', minutes:'۳ جلسه · ۶ ساعت',
      lead:'ساخت یک هستهٔ سه‌ناحیه‌ای با OSPF چندناحیه، EIGRP در لبه، IPv6 دوزبانه و QoS روی WAN — پروژه‌ای که می‌تواند نمونهٔ کار مصاحبه باشد.',
      sec:{
        goal:[['p','طراحی و پیاده‌سازی هسته‌ای که: OSPF Area0/1/2 + لبهٔ EIGRP + Dual-Stack + LLQ روی WAN را با هم تحمل کند.']],
        prereq:[['ul',['۲۰ سناریوی R&S','طرح IP Plan با v4/v6','کانفیگ QoS آزمایشگاه‌ها']]],
        concept:[['h3','معماری'],['p','دو Core در Area0؛ Distribution در Area1 با ABR؛ Access/Ledge با EIGRP stub (اگر سمت مشتری EIGRP است)؛ روی لینک‌های WAN دو زبانه IPv4/IPv6 و policy خروجی صدا.']],
        protocol:[['svg','topo'],['p','نکتهٔ تحویل: مسیر یک بستهٔ صوتی v6 را از یک سمت تا سمت دیگر قدم‌به‌قدم با خروجی CLI دنبال کن.']],
        ios:[['cli','قالب policy صدا','policy-map WAN-POLICY\n class VOICE\n  priority percent 10\n class class-default\n  fair-queue\n\ninterface g0/0\n service-policy output WAN-POLICY']],
        diagram:[['svg','ospf']],
        lab:[['labs',[
          {t:'چک‌لیست تحویل',steps:['نقشهٔ IP Plan (v4/v6)','OSPF چندناحیه + summarization','EIGRP stub در لبه','QoS: صدا priority، بقیه fair','گزارش ۵ صفحه‌ای: مسیر صدا با خروجی']},
        ]]],
        trouble:[['ul',['اختلاف رفتار v4 و v6: همیشه هر دو فامیلی را جدا چک کن — پیشوند، neighbor، policy','QoS روی لینک بیکار: خروجی interface درست؟ class-map match می‌خورد؟']]],
        exercise:[['ol',['یک صفحه «Risk»: سه خرابی محتمل و پلان عیب‌یابی','تحلیل: اگر ABR قطع شود، سرنوشت مسیرهای بین‌ناحیه چیست؟']]],
        quiz:[['quiz',[
          {q:'در این پروژه صدا چرا اولویت می‌گیرد؟',opts:['کوچک‌تر است','حساس به تأخیر است','UDP است','رایگان است'],a:1,exp:'Real-time حساس به jitter/delay؛ priority queue تأخیر را پایین نگه می‌دارد.'},
          {q:'EIGRP stub در کجا می‌آید؟',opts:['هسته','لبهٔ دسترسی','WAN سازنده','جایی ندارد'],a:1,exp:'لبه فقط مسیرهای محلی/متصل/summarize اعلام می‌کند — Query کور می‌شود.'},
        ]]],
        notes:[['ul',['پروژه را در Git با تگ versioned ذخیره کن','نمرهٔ پروژه به پیوستگی طرح و تحلیل، نه به تعداد دستور است']]],
      },
    },
  ]
},
{
  id:'f3', num:'۳', title:'دانشکدهٔ سوم — Enterprise (Core) — همان CCNP ENCOR', duration:'۸ ماه', tag:'ENCOR 350-401',
  intro:'این دانشکده همان قلب مدرک CCNP ENCOR است: هستهٔ Enterprise، امنیت بنیادی، اتوماسیون و معماری — سپس یک مسیر انتخابی (در این نسخه: ENARSI پیشرفته). خروجی: مهندسی که می‌تواند یک شبکهٔ سازمانی را طراحی، پیاده‌سازی، امن و خودکار کند.',
  lessons:[
    { id:'f3-enc1', title:'هستهٔ Enterprise — OSPF، BGP و Route Policies', sub:'ENCOR · پنج حوزهٔ الزامی · جلسه ۱', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'ENCOR با مسیریابی باز می‌شود: شما باید بتوانید مسیرها را نه فقط بیاورید، بلکه فیلتر، علامت‌گذاری و جهت‌دهی کنید. تفاوت CCNA تا اینجا در همین کلمه است: policy.',
      sec:{
        goal:[['p','شامل: OSPF پیشرفته (Graceful Restart، LFA مفهومی)، BGP کامل (Session، Path Selection، Communities)، Route-Map، Prefix-List، Filtering و Tagging.']],
        prereq:[['ul',['دانشکدهٔ R&S کامل','OSPF چندناحیه و BGP مبانی','لاب‌های redistribution را دیده‌ای']]],
        concept:[['h3','چرا policy؟'],['p','در CCNA مسیر خودش «بهترین» را پیدا می‌کرد؛ در Enterprise مهندس تعیین می‌کند کدام مسیر بهتر است: مثلاً ترافیک ورودی از یک uplink خاص را با local-preference بالاتر ببر، یا پیشوند مشتری را در AS خودت نپذیر. ابزارها: route-map (شرط + اقدام)، prefix-list (فقط پیشوندها)، tag (برچسب برای ردیابی).'],['h3','مسیر BGP در یک نما'],['p','Weight → Local-Pref → مسیر محلی → AS-Path کوتاه‌تر → Origin → MED → eBGP over iBGP → قدیمی‌ترین → IGP کوتاه‌تر → Router-ID. مهندس روی Local-Pref و AS-Path بیشترین دسترسی را دارد.']],
        protocol:[['cli','فیلتر و علامت‌گذاری حرفه‌ای','! فقط پیشوندهای خاص را از همسایه بپذیر\nR1(config)# ip prefix-list CUSTOMERS seq 10 permit 203.0.113.0/24\nR1(config)# ip prefix-list CUSTOMERS seq 20 deny 0.0.0.0/0 le 32\n\n! روی ورودی BGP اعمال شود\nR1(config)# router bgp 65001\nR1(config-router)# neighbor 10.10.10.2 prefix-list CUSTOMERS in\n\n! route-map با tag برای redistribution\nR1(config)# route-map OSPF-IN deny 10\nR1(config-route-map)# match ip address prefix-list CUSTOMERS\nR1(config)# route-map OSPF-IN permit 20\nR1(config-route-map)# set tag 100\nR1(config)# router ospf 1\nR1(config-router)# redistribute bgp 65001 route-map OSPF-IN subnets']],
        ios:[['cli','بررسی policy','R1# show ip prefix-list\nR1# show ip route-map\nR1# show ip bgp neighbors 10.10.10.2 routes\nR1# show ip ospf database external']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — Prefix-List در عمل',steps:['سه پیشوند با طول‌های مختلف بساز و le/ge را تست کن','پیشوندی که نباید بیاید را رد کن و show ip bgp را قبل/بعد ببین']},
          {t:'آزمایشگاه ۲ — Route-Map ترکیبی',steps:['یک route-map سه‌مرحله‌ای: deny مشخص، set local-preference، permit بقیه','روی دو همسایهٔ BGP اثر متفاوت بگذار و مسیر خروجی را عوض کن']},
          {t:'آزمایشگاه ۳ — Tag و Loop Guard',steps:[' redistributedها را tag کن و در ورودی جای دیگر filter کن','یک حلقهٔ redistribution بساز و با tag بشکن']},
        ]]],
        trouble:[['ul',['prefix-list اثر نمی‌کند: جهت in/out و شمارهٔ seq و le/ge را چک کن','route-map به مسیر نمی‌خورد: مسیر از کجا می‌آید؟ matchها با همان منبع هم‌خوان‌اند؟','redistribution حلقه می‌سازد: tag یا admin-distance بالاتر برای مسیر بازگشتی']]],
        exercise:[['ol',['یک policy برای مشتری بنویس: فقط /24، با local-preference 150، بقیه reject','ترتیب قوانین route-map را توضیح بده: چرا اول deny مهم است؟','روش شکستن حلقهٔ redistribution با tag را گام‌به‌گام بنویس']]],
        quiz:[['quiz',[
          {q:'ابزار فیلتر کردن «پیشوند» در BGP چیست؟',opts:['route-map به تنهایی','prefix-list','distribute-list دقیق','CSPF'],a:1,exp:'prefix-list پیشوند/طول را دقیق می‌سنجد؛ route-map شرط+اقدام دارد و اغلب با prefix-list ترکیب می‌شود.'},
          {q:'set local-preference در کدام جهت معنا دارد؟',opts:['روی مسیر ورودی از همسایه','روی مسیر خروجی به همسایه','فقط داخل AS روی همه','روی مسیر متصل'],a:0,exp:'Local-Pref داخل AS معتبر است: روی ورودی می‌زنیم تا همهٔ روترهای AS همان مسیر را بخواهند.'},
          {q:'چرا tag به مسیر redistributed می‌زنیم؟',opts:['برای سرعت','برای شناسایی و جلوگیری از بازتزریق/حلقه','برای رمزنگاری','برای QoS'],a:1,exp:'مسیری که از OSPF وارد BGP شده با tag علامت می‌خورد تا در جای دیگر دوباره redistribute نشود.'},
          {q:'ترتیب بهترین مسیر BGP بعد از Local-Pref؟',opts:['MED','AS-Path کوتاه‌تر','قدیمی‌ترین','Router-ID'],a:1,exp:'معیار اصلی بعد از Local-Pref: AS-Path کوتاه‌تر (به ترتیب ساده‌شدهٔ الگوریتم).'},
        ]]],
        notes:[['ul',['جدول ۹ مرحله‌ای بهترین مسیر BGP را یک بار از حفظ بنویس','خروجی show ip bgp route-map و show ip prefix-list را در دفترچه نگه دار']]],
      },
    },
    { id:'f3-enc2', title:'امنیت بنیادی Enterprise — AAA، ISE و Segmentation', sub:'ENCOR · پنج حوزهٔ الزامی · جلسه ۲', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'دیگر پورت ترک نیست: کاربر هویت دارد، دسترسی‌اش سیاست دارد، و حرکتش باید ثبت شود. این جلسه چارچوب 3A و تقسیم‌بندی شبکه را می‌بندد.',
      sec:{
        goal:[['p','شامل: معماری AAA (RADIUS/TACACS+)، Cisco ISE مفهومی (Policy Set، Profiling)، 802.1X، تفکیک Segmentation (VRF/TrustSec مفهومی) و Hardening پایه.']],
        prereq:[['ul',['دانشکدهٔ CCNA امنیت','Concept لایه‌های Access/Trunk','مبانی کار با سرور Radius دیده شده']]],
        concept:[['h3','سه سؤال AAA'],['p','Authentication: کیستی؟ Authorization: چه کاری؟ Accounting: چه کردی؟ TACACS+ سیسکویی و جلسه‌محور (دستور را می‌بیند)، RADIUS استاندارد و بسته‌محور (رمز در payload). ترمینال اول TACACS+، شبکهٔ مهمان/سیمی 802.1X با RADIUS.'],['h3','ISE تصمیم‌گیرنده است'],['p','ISE کاربر/دستگاه را profile می‌کند، هویت را از منبع (AD/LDAP) می‌گیرد و به سوئیچ/وایرلس دستور می‌دهد: کدام VLAN/ACL روی کدام پورت. Policy Set = چه کسی + چه دستگاهی + کجا = چه اتفاقی بیفتد.'],['h3','Segmentation چرا لازم است'],['p','شبکهٔ تخت یعنی نفوذ آزاد؛ Segmentation یعنی هر بخش (کاربر، مهمان، سرور، OT) در مرز خودش بماند: با VRF، TrustSec/SGT یا ساده‌تر VLAN+ACL+Firewall.']],
        protocol:[['cli','AAA روی سوئیچ','Switch(config)# aaa new-model\nSwitch(config)# aaa authentication login default local group radius\nSwitch(config)# aaa authorization exec default local group radius\nSwitch(config)# aaa accounting exec default start-stop group radius\n\nSwitch(config)# radius-server host 10.10.10.5 key Secret123\nSwitch(config)# line vty 0 15\nSwitch(config-line)# transport input ssh\nSwitch(config-line)# login authentication default\n\n! 802.1X روی پورت کاربر\nSwitch(config)# dot1x system-auth-control\nSwitch(config)# interface g0/1\nSwitch(config-if)# dot1x port-control auto']],
        ios:[['cli','بررسی AAA و 802.1X','Switch# show aaa sessions\nSwitch# show dot1x all\nSwitch# show authentication session\nSwitch# show logging | include DOT1X']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — TACACS+ نظارتی',steps:['ادغام با سرور (یا شبیه‌ساز) و login با حساب مشترک','هر دستور CLI را در لاگ ببین (authorization + accounting)','لاگ out را با نشست مقایسه کن']},
          {t:'آزمایشگاه ۲ — 802.1X ساده',steps:['یک پورت را auto کن، کلاینت بدون هویت باید قطع شود','auth موفق = VLAN مهمان/کاربر طبق policy','reauth و اعمال روی دستگاه ناشناخته (MAB) را تست کن']},
          {t:'آزمایشگاه ۳ — Segmentation',steps:['دو VRF برای کاربر و مهمان بساز','ACL مرزی بین VRF و سرور بگذار و ترافیک مجاز/غیرمجاز را تست کن']},
        ]]],
        trouble:[['ul',['802.1X پورت را می‌بندد: سرور RADIUS بالا؟ دسترسی سوئیچ به سرور؟ فهرست VLAN برای شاخه؟','TACACS+ رد می‌شود: aaa new-model فعال؟ کلید مشترک؟ پورت 49 که ACL نبسته باشد','کاربر بعد از auth هم قطع است: authorization ناموفق — فرمان exec را سرور نپذیرفته']]],
        exercise:[['ol',['تفاوت TACACS+ و RADIUS را در جدولی ۵ ستونه بنویس','یک Policy Set سه‌شرطی برای کاربران IT در سایت B بنویس','چرا Segmentation بدون AAA فقط نیمی از راه است؟']]],
        quiz:[['quiz',[
          {q:'کدام پروتکل دستورهای CLI را می‌بیند؟',opts:['RADIUS','TACACS+','SNMPv3','Syslog'],a:1,exp:'TACACS+ جلسه‌محور است: هر فرمان جدا authorize/accounting می‌شود — نظارت دقیق.'},
          {q:'802.1X سه نقش کلیدی دارد؛ غیر از آن‌ها کدام است؟',opts:['Supplicant','Authenticator','Authentication Server','DNS Server'],a:3,exp:'سوکلاینت (کلاینت)، Authenticator (سوئیچ/AP)، Authentication Server (ISE/RADIUS) — DNS بیگانه است.'},
          {q:'هدف Segmentation چیست؟',opts:['افزایش سرعت','محدودسازی دامنهٔ نفوذ و دسترسی','کاهش هزینه لایسنس','جایگزین AAA'],a:1,exp:'هر بخش در مرز خودش؛ نفوذ به یک VLAN مهمان نباید به سرورهای حساس برسد.'},
          {q:'حسابداری (Accounting) چه ثبت می‌کند؟',opts:['رمز کاربر','چه کسی، چه کی، چه کرد','فقط خطاها','فقط login ناموفق'],a:1,exp:'رکورد نشست/دستور/زمان — پایهٔ ممیزی و ردیابی حادثه.'},
        ]]],
        notes:[['ul',['معماری AAA را با سه فلش (کلاینت → سوئیچ → ISE → AD) رسم کن','فهرست hardening پورت (portfast/bpduguard/unused shutdown) را تیک بزن']]],
      },
    },
    { id:'f3-enc3', title:'اتوماسیون و معماری — Python، Ansible و SD-WAN', sub:'ENCOR · پنج حوزهٔ الزامی · جلسه ۳', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'دیگر نمی‌شود ۲۰۰ روتر را دستی ساخت. ENCOR از شما زبان می‌خواهد: REST، JSON، YANG/NETCONF، اسکریپت Python و درک SD-WAN و دسترسی از راه دور مدرن.',
      sec:{
        goal:[['p','شامل: مدل‌های API (REST/JSON)، نمونهٔ کدنویسی با Python (requests)، Ansible playbook ساده، مفهوم YANG/NETCONF، معماری SD-WAN و Zero-Trust (SDA مفهومی).']],
        prereq:[['ul',['Automation در CCNA','مبانی Python (متغیر، حلقه، dict)','دسترسی DevNet Sandbox یا شبیه‌ساز']]],
        concept:[['h3','از CLI به API'],['p','CLI برای انسان است، API برای ماشین: GET/POST/PUT/DELETE روی منابع، بدنهٔ JSON، توکن احراز. تفاوت مهم: تغییر با API قابل تکرار، قابل تست و قابل ثبت در Git است.'],['h3','YANG و NETCONF'],['p','YANG مدل دادهٔ دستگاه را توصیف می‌کند (چه فیلدهایی هست)، NETCONF/RESTCONF راه انتقال و تغییر آن را — با قواعد (candidate/commit، rollback). نتیجه: پیکربندی نه متن پراکنده، بلکه state قابل اعتبارسنجی.'],['h3','SD-WAN در یک جمله'],['p','کنترل‌پلن جدا از دیتاپلن؛ مسیر بین سایتها بر اساس سیاست (بهترین link برای ویدیو، مسیر پشتی برای داده) انتخاب می‌شود؛ پیکربندی از کنسول مرکزی می‌آید نه از هر دستگاه.']],
        protocol:[['cli','یک API واقعی + یک playbook','! دریافت لیست دستگاه‌ها\nGET /dna/intent/api/v1/network-device\nHeaders: X-Auth-Token: <token>\n\n{\n  "response": [\n    { "hostname": "access-01", "reachabilityStatus": "Reachable" }\n  ]\n}\n\n# Python کوتاه\nimport requests\nr = requests.get(URL, headers={"X-Auth-Token": TOKEN}, verify=True)\nfor d in r.json()["response"]:\n    print(d["hostname"], d["reachabilityStatus"])',
          ], ['cli','Ansible ساده','- hosts: switches\n  connection: ansible.netcommon.network_cli\n  gather_facts: no\n  tasks:\n    - name: set hostname\n      cisco.ios.ios_config:\n        lines:\n          - hostname {{ inventory_hostname }}\n    - name: save\n      cisco.ios.ios_command:\n        commands: write memory']],
        ios:[['cli','اجرای اتوماسیون','ansible-playbook -i inventory site.yml --check\nansible-playbook -i inventory site.yml --diff\n\ncurl -H "X-Auth-Token: $TOKEN" https://sandboxdnacenter.com/dna/intent/api/v1/network-device | jq .response[0]']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — REST با cURL/Python',steps:['توکن بگیر، GET بزن، JSON را parse کن','یک POST تغییر بده و state را قبل/بعد ببین','خطای 401/404 را عمداً بساز و بخوان']},
          {t:'آزمایشگاه ۲ — Ansible',steps:['inventory ساده از دو سوئیچ','playbook: hostname + banner + show version','ansible-playbook --check سپس اجرا و diff را ببین']},
        ]]],
        trouble:[['ul',['401: توکن نادرست یا منقضی — Header را چک کن',' Ansible نمی‌connect می‌شود: network_cli درست؟ credenrialها؟ انگلیسی بودن پیام خطا را بخوان','SD-WAN control down: به دیتاپلن نگاه نکن — اول reachability کنسول تا vSmart']]],
        exercise:[['ol',['یک اسکریپت بنویس که از خروجی show ip interface brief یک گزارش CSV بسازد','تفاوت model-driven (YANG) و CLI را با مثال بنویس','سه مزیت SD-WAN برای شرکت دارای ۱۰ شعبه را بنویس']]],
        quiz:[['quiz',[
          {q:'روش استاندارد تغییر پیکربندی در API چیست؟',opts:['SSH دستی','POST/PUT با بدنهٔ JSON','Telnet','SNMP trap'],a:1,exp:'REST: منبع، متد، بدنهٔ JSON — قابل تکرار و تست.'},
          {q:'YANG چه توصیف می‌کند؟',opts:['لینک فیزیکی','مدل داده و state دستگاه','روتر مسیر','رمز عبور'],a:1,exp:'شکل داده (فیلدها، محدودیت‌ها) — NETCONF انتقال/تغییر آن را می‌کند.'},
          {q:'در SD-WAN کنترل‌پلن کجاست؟',opts:['داخل هر شاخه فقط','جدا و مرکزی (vSmart/vManage)','روی لینک uplink','در سوئیچ دسترسی'],a:1,exp:'کنترل جدا از دیتا: سیاست از کنسول می‌آید، بسته‌ها مستقیم بین سایتها می‌روند.'},
          {q:'متد GET در REST برای چیست؟',opts:['حذف منبع','خواندن منبع','تغییر منبع','ساخت منبع'],a:1,exp:'GET خواندن است؛ تغییر با POST/PUT و حذف با DELETE.'},
        ]]],
        notes:[['ul',['یک کلاینت Python 50 خطی برای یک API واقعی بنویس و در Git بگذار','playbook اول را با --check و سپس اجرا کن و diff را نگه دار']]],
      },
    },
    { id:'f3-sel', title:'مسیر انتخابی — ENARSI پیشرفته (پیشنهادی)', sub:'ENCOR · انتخابی · جلسه ۴', minutes:'۸ جلسه · ۱۶ ساعت',
      lead:'ENCOR پنج حوزهٔ الزامی دارد و یک گزینه. در این نسخه از آکادمی، مسیر انتخابی ENARSI (Enterprise Routing & Services) انتخاب شده چون مستقیم به عمق همان هسته می‌رود: Troubleshooting پیشرفته، MPLS L3VPN، QoS و امنیت مسیر.',
      sec:{
        goal:[['p','شامل: تکنیک‌های عیب‌یابی سیستماتیک، BGP در مقیاس (Route-Reflector، Confederation مفهومی)، MPLS L3VPN عملی، QoS در WAN و امنیت مسیر (uRPF، TTL Security).']],
        prereq:[['ul',['پنج حوزهٔ ENCOR تمام شده','دانشکدهٔ R&S کامل','لاب MPLS/QoS را دیده‌ای']]],
        concept:[['h3','عیب‌یابی سیستماتیک'],['p','به جای حدس، مدل: 1) مشکل کجاست (لینک/پروتکل/سیاست)؟ 2) کدام لایه (پزیکی → لایه ۲ → لایه ۳ → policy)؟ 3) کدام دستور شواهد می‌دهد؟ 4) رفع و راستی‌آزمایی. هر مهندسی که این مدل را دارد، از هر مصاحبهٔ عیب‌یابی عبور می‌کند.'],['h3','BGP در مقیاس'],['p','Full-mesh iBGP با 1000 روتر جواب نمی‌دهد: Route-Reflector (مرکز اعلام) یا Confederation (زیر-AS). نکته: RR مسیر را می‌پذیرد و به کلاینت‌هایش می‌دهد — احتمال loop با originator-id/cluster-list کنترل می‌شود.']],
        protocol:[['cli','لیست شواهد عیب‌یابی','! پنج فرمانی که باید سریع بیاید\nR# show ip interface brief\nR# show ip route\nR# show ip ospf neighbor\nR# show ip bgp summary\nR# show logging | section %OSPF\n\n! مسیر مشکوک را قدم به قدم\nR# show ip route 203.0.113.0\nR# show ip route 203.0.113.0 longer-prefixes\nR# show ip cef 203.0.113.0 detail']],
        ios:[['cli','شواهد BGP و VPN','R# show ip bgp neighbors 10.10.10.2 received-routes\nR# show mpls ldp neighbor\nR# show vrf detail\nR# show ip route vrf CUST-A']],
        diagram:[['svg','ospf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — RR ساده',steps:['دو کلاینت + یک RR بساز','اعلام مسیر بین کلاینت‌ها بدون full-mesh را ببین','cluster-list را در show ip bgp بخوان']},
          {t:'آزمایشگاه ۲ — L3VPN عملی',steps:['دو VRF با RT مکمل و MP-BGP بالا','ping بین سایت‌ها از هر مشتری','یک خرابی عمداً: RT غلط — علامت‌ها را بخوان']},
          {t:'آزمایشگاه ۳ — QoS و uRPF',steps:['LLQ را قبل/بعد با iperf بساز','strict/loose uRPF را روی uplink تست کن','TTL Security را روی لینک همسایه فعال و تأثیرش را ببین']},
        ]]],
        trouble:[['ul',['RR مسیر را رد نمی‌کند: کلاینت درست؟ next-hop از مسیر ورودی reachability دارد؟','VPN پینگ ندارد: RT import/export؟ RD منحصر؟ MP-BGP بالا؟','uRPF پورت مجاز را می‌بندد: مسیر برگشتی دستگاه وجود دارد؟ loose mode یا null route؟']]],
        exercise:[['ol',['یک check-list 10 تایی عیب‌یابی OSPF بنویس (از لینک تا LSA)','چرا RR به جای full-mesh؟ و کدام حلقه را cluster-list می‌گیرد؟','تفاوت strict و loose uRPF را با نقشه توضیح بده']]],
        quiz:[['quiz',[
          {q:'در عیب‌یابی، اولین قدم؟',opts:['reboot','تعیین مرز مشکل (لایه/دامنه)','پاک کردن تنظیمات','تماس با فروشنده'],a:1,exp:'مرزبندی: لینک یا پروتکل؟ لایه ۲ یا ۳؟ سیاست یا انتقال؟ بعد شواهد.'},
          {q:'Route-Reflector جای چه چیز را می‌گیرد؟',opts:['NAT','full-mesh iBGP','DHCP','STP'],a:1,exp:'اعلام بین iBGP همسایه‌ها را متمرکز می‌کند تا از O(n²) خلاص شویم.'},
          {q:'در L3VPN چه چیزی دو مشتری با آدرس یکسان را جدا می‌کند؟',opts:['پورت فیزیکی','VRF + RD','MAC آدرس','VLAN 1'],a:1,exp:'جدول هر VRF جدا + RD یکتای مسیر در control-plane اپراتور.'},
          {q:'strict uRPF چه می‌خواهد؟',opts:['هر بسته از مسیری بیاید که آدرس مبدأ در همان جهت در جدول است','فقط TCP','فقط ICMP','نیاز به ACL ندارد و همه را رد می‌کند'],a:0,exp:'معکوسِ مسیر رسیدن باید با مسیر خروجِ آدرس مبدأ بخواند — نفوذ با مبدأ جعلی را می‌گیرد (به شرط جدول درست).'},
        ]]],
        notes:[['ul',['مدل چهارمرحله‌ای عیب‌یابی را روی یک قطعی واقعی تمرین کن','خروجی show ip cef detail را برای یک مسیر تفسیر محور بنویس']]],
      },
    },
    { id:'f3-labs', title:'آزمایشگاه‌های الزامی ENCOR — ۳۰ سناریوی ترکیبی', sub:'ENCOR · کارگاه', minutes:'۴ جلسه · ۸ ساعت',
      lead:'سی‌هامین سناریوی ترکیبی: هرکدام بخشی از پنج حوزهٔ ENCOR را می‌سنجد. قبولی با گزارش مهندسی و حداقل ۲۴ سناریوی مستند.',
      sec:{
        goal:[['p','اجرای ۳۰ سناریو و تحویل گزارش برای حداقل ۲۴ تای آن‌ها (بقیه تمرین آزاد).']],
        prereq:[['ul',['سه درس ENCOR','Git برای ذخیرهٔ خروجی','دسترسی PT/PNETLab/EVE']]],
        concept:[['p','این‌جا دیگر «دستور درست» کافی نیست: سناریو عمداً گره دارد (conflict policy، مسیر متضاد، خرابی جزئی) و باید گزارش دهی که چرا شبکه این‌طور رفتار می‌کند.']],
        protocol:[['table',['دسته','نمونه سناریوها','تعداد'],[
          ['Routing','OSPF multi-area، tag/filter، BGP policy، RR','8'],
          ['Switching','STP عیب‌یابی، EtherChannel غلط، VLAN امنیتی','5'],
          ['Security','AAA، 802.1X، ACL پیچیده، hardening','5'],
          ['Automation','REST تغییر، Ansible diff، گزارش خودکار','5'],
          ['Architecture','SD-WAN مفهوم، segmentation، QoS end-to-end','7'],
        ]]],
        ios:[['note','key','قالب گزارش هر سناریو: هدف ← مدل ← دستورها ← شواهد ← نتیجه ← آموزه.']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'استاندارد قبولی',steps:['اجرای واقعی ۳۰ سناریو','گزارش ۲۴ سناریو در Git','مرور گروهی دو سناریوی سخت با مربی']}]]],
        trouble:[['ul',['سناریوی automation وصل نمی‌شود: سندباکس یا شبیه‌ساز؟ اول reachability بعد auth','سناریوی routing گره دارد: به policyها و tag ها شک کن، نه به دستورها']]],
        exercise:[['ol',['دو سناریو را خودت طراحی کن و جوابش را بنویس (معکوس‌سازی یادگیری)','لیست ۵ خطای رایج خودت را از این ۳۰ سناریو استخراج کن']]],
        quiz:[['quiz',[
          {q:'قبولی ENCOR با چند سناریوی گزارش‌شده است؟',opts:['۵','۱۲','۲۴ از ۳۰','همه باید عالی باشند'],a:2,exp:'حداقل ۲۴ سناریوی مستند؛ کیفیت گزارش مهم‌تر از تعداد کامل است.'},
          {q:'در گزارش، «شواهد» یعنی چه؟',opts:['حدس مهندس','خروجی show/capture قبل و بعد','نقشهٔ زیبا','نام دستگاه'],a:1,exp:'بدون شواهد، ادعا مهندسی نیست: CLI یا packet capture.'},
        ]]],
        notes:[['ul',['پیشرفت ۳۰ سناریو را در داشبورد علامت بزن','دو گزارش برتر را برای نمونهٔ مصاحبه نگه دار']]],
      },
    },
    { id:'f3-proj', title:'پروژهٔ پایان ENCOR — سیاست، امنیت و اتوماسیون یکپارچه', sub:'ENCOR · پروژه', minutes:'۴ جلسه · ۸ ساعت',
      lead:'پروژهٔ نهایی: یک شاخهٔ Enterprise با هستهٔ مسیریابی policy-محور، AAA/Segmentation، و یک خط لولهٔ اتوماسیون برای پیکربندی و گزارش — تحویل با دموی زنده.',
      sec:{
        goal:[['p','ساخت و ارائهٔ سه‌لایه: Routing policy + Security segmentation + Automation pipeline، با دموی زنده و گزارش معماری.']],
        prereq:[['ul',['سه درس ENCOR و ۲۴ سناریو','طرح IP/Policy از پیش نوشته','یک مخزن Git خالی برای پروژه']]],
        concept:[['h3','معماری تحویلی'],['p','لایهٔ ۱: هسته با prefix-list/route-map و BGP policy؛ لایهٔ ۲: AAA + VLAN/VRF segmentation؛ لایهٔ ۳: اسکریپت خواندن وضعیت + playbook اعمال تغییر + گزارش HTML. هر لایه بدون لایهٔ دیگر در دنیای واقعی نمی‌ایستد — پروژه هم همین‌طور.']],
        protocol:[['svg','topo'],['p','در دمو: یک تغییر سیاست را از طریق pipeline اعمال کن، اثرش را روی مسیر نشان بده، و یک خرابی عمدی را با مدل عیب‌یابی حل کن.']],
        ios:[['cli','نمونهٔ گزارش خودکار','# خروجی یکپارچه از سه دستگاه\nfor host in core1 core2 edge1; do\n  ssh admin@$host "show ip ospf neighbor" >> evidence/ospf.txt\ndone\n\n# سپس اسکریپت: بررسی FULL بودن همسایگان + خروجی HTML']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'چک‌لیست تحویل',steps:['سند معماری ۵ صفحه‌ای','پیکربندی policy و security روی توپولوژی','اسکریپت جمع‌آوری evidence','دموی زنده ۱۵ دقیقه‌ای + Q&A']}]]],
        trouble:[['ul',['پروژه گره می‌خورد: از لایهٔ ۱ (لینک/مبنایی) شروع کن، سپس سیاست، سپس اتوماسیون','automation دستی اجرا می‌شود: اگر pipeline تکرارپذیر نیست، پروژه ناتمام است']]],
        exercise:[['ol',['سه risk پروژه را با mitigation بنویس','اگر یک لایه حذف شود، پروژه چه می‌شود؟ تحلیل کن']]],
        quiz:[['quiz',[
          {q:'مهم‌ترین معیار قبولی پروژه؟',opts:['تعداد دستور','یکپارچگی سه لایه و دموی زنده','رنگ ترمینال','طول سند'],a:1,exp:'سیاست+امنیت+اتوماسیون که با هم کار کنند و قابل نمایش باشند.'},
          {q:'چرا evidence خودکار؟',opts:['زیباست','تکرارپذیر و قابل ممیزی است','چون دستی سخت است فقط','برای پر کردن گزارش'],a:1,exp:'هر ادعای مهندسی با شواهد ماشینی پشتیبانی می‌شود — قابل بازتولید.'},
        ]]],
        notes:[['ul',['پروژه را با تگ git tag و مستند README تحویل بده','بازخورد مربی را در دفترچه ثبت کن']]],
      },
    },
  ]
},
{
  id:'f4', num:'۴', title:'دانشکدهٔ چهارم — تخصص‌های پیشرفته', duration:'۱۸ ماه', tag:'DC / SP / Wireless',
  intro:'اینجا دیگر همه‌چیزدانی تمام می‌شود و تخصص شروع می‌شود: هشت مسیر مستقل — Enterprise، Security، Data Center، Service Provider، Wireless، Collaboration، Automation و Cybersecurity — هرکدام با دروس، آزمایشگاه، پروژه و مدارک هدف خودش. دانشجو یک یا چند مسیر را انتخاب می‌کند؛ همه الزامی نیستند.',
  lessons:[
    { id:'f4-dc1', title:'Leaf-Spine و VXLAN/EVPN در دیتاسنتر — راهنمای کامل', sub:'Data Center · جلسه ۱', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'چرا دیتاسنترهای امروز به جای سه‌طبقهٔ کلاسیک، به سراغ Leaf-Spine رفته‌اند؟ چون ترافیک امروز شرق‌به‌غرب است، نه شمال‌به‌جنوب. در این درس معماری Leaf-Spine را از ریشه می‌فهمی، با VXLAN/EVPN مقیاس می‌گیری، و می‌توانی آن را طراحی و عیب‌یابی کنی.',
      sec:{
        goal:[['p','در پایان این درس می‌توانی: محدودیت معماری سه‌طبقه را توضیح دهی، توپولوژی Leaf-Spine را طراحی کنی، نقش VXLAN و EVPN را در این معماری بگویی، و یک اتصال end-to-end بین دو Leaf را قدم‌به‌قدم ردیابی کنی.']],
        prereq:[['ul',['دانشکدهٔ CCNA و لایه ۲/۳ روان','VLAN/Trunk/STP را می‌دانی','IP و subnetting بدون فکر','مبانی BGP از ENCOR یا R&S']]],
        concept:[['h3','Leaf-Spine چیست؟'],['p','Leaf-Spine یک معماری (Topology) دو لایه‌ای برای دیتاسنتر است: روترهای لایهٔ ۲ (Leaf) به همهٔ روترهای لایهٔ ۱ (Spine) وصل‌اند — مثل خوشهٔ ستاره‌ای که هیچ Leaf‌ای به Leaf دیگر وصل نیست و همهٔ ترافیک داخلی از یک یا دو مسیر Spine عبور می‌کند. نتیجه: مسیر همیشه یک لینک است (بدون STP)، oversubscription کنترل‌شده، و گسترش با اضافه کردن Spine.'],['h3','چرا سه‌طبقهٔ کلاسیک جواب نمی‌دهد؟'],['p','در معماری کلاسیک Core–Distribution–Access ترافیک عمدتاً شمال‌به‌جنوب (کاربر به سرور) طراحی شده؛ اما امروز VM-to-VM، استوریج و East-West یعنی ترافیک بین سرورها در همان طبقهٔ Access می‌پیچد و Distribution و Core را اشباع می‌کند. راه‌حل: کوتاه‌ترین مسیر ممکن بین هر دو سرور — دقیقاً کاری که Leaf-Spine می‌کند.']],
        protocol:[['h3','اجزای اصلی'],['ul',['Leaf (ToR): به سرورها وصل است؛ در دیتاسنترهای مدرن معمولاً لایه ۲/۳ (EVPN-VXLAN) اجرا می‌کند','Spine: ستون فقرات؛ هر Leaf به همهٔ Spine‌ها وصل — هیچ Spine به Spine','بومی: لینک‌های ۴۰/۱۰۰G، ECMP چندمسیره، و عدم وابستگی به STP']],['h3','چگونه کار می‌کند — پنج گام'],['ol',['بسته از سرور روی پورت Leaf وارد می‌شود','Leaf بر اساس CMAP/VNI تصمیم می‌گیرد بسته کدام تونل (VXLAN) است','بسته با سربرگ VXLAN به یک Spine فوروارد می‌شود (ECMP روی چند Spine)','Spine فقط بر اساس Outer-IP آن را به Leaf مقصد می‌فرستد','Leaf مقصد VXLAN را unwrap می‌کند و به پورت سرور مقصد تحویل می‌دهد']],['h3','مقیاس‌پذیری با VXLAN/EVPN'],['p','VLAN به‌عنوان دامنهٔ پخش به ۴۰۹۴ محدود است؛ VXLAN با VNI تا ۱۶ میلیون دامنهٔ لایه ۲ می‌سازد و بسته را در UDP/IP (لایه ۳) تونل می‌کند — یعنی دو سایت می‌توانند یک VLAN را از روی روترهای عمومی/خودشان هم‌گام نگه دارند. EVPN کنترل‌پلن است: با BGP، MAC/IP های هر Leaf را اعلام می‌کند تا به جای flooding، کنترل‌شده یاد بگیریم (کنترل‌پلن BGP + دیتاپلن VXLAN).'],['h3','Leaf-Spine در یک جمله و رابطتش با VLAN و OSPF'],['p','لایه ۲ داخل تونل (VLAN/VNI) می‌ماند، لایه ۳ بین Leaf‌ها (Underlay با OSPF یا IS-IS ساده + ECMP) جریان دارد؛ EVPN بین Leaf‌ها با iBGP جفت می‌شود. اگر معماری سه‌طبقه را کلاسیک و کنترل‌شده می‌خواهی، همان‌جاست؛ اگر مقیاس و East-West می‌خواهی، Leaf-Spine.']],
        ios:[['cli','دستورهای کلیدی Leaf/Spine','! Underlay (روی هر Leaf و Spine)\nrouter ospf 1\n router-id 10.0.0.X\n network 10.0.0.0 0.0.0.255 area 0\n\n! VXLAN ساده روی Leaf\ninterface nve1\n source-address 10.10.10.1\n member vni 100100\n  ingress-replication protocol bgp\n\n! مشاهده\nshow nve peers\nshow nve vni\nshow bgp l2vpn evpn summary']],
        diagram:[['svg','leaf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — Topology ساده',steps:['دو Spine + دو Leaf + دو سرور در PT یا EVE','ping بین دو سرور و مسیر traceroute را ببین (دو مسیر ECMP)','یک لینک Spine را down کن: بدون قطعی، مسیر عوض شود']},
          {t:'آزمایشگاه ۲ — VLAN در VXLAN',steps:['دو Leaf با VNI یکسان و زیرشبکه یکسان','ARP فراگیر چطور در تونل جواب می‌دهد؟ با show nve peers و capture','دو VNI مجزا بساز و قطعی دامنه را ثابت کن']},
          {t:'آزمایشگاه ۳ — EVPN کنترل‌پلن',steps:['iBGP EVPN بین دو Leaf را بالا بیاور','MAC آدرس یادگرفته‌شده را در show bgp l2vpn evpn ببین','یک MAC جعلی نده و فیلتر رفتار را مشاهده کن']},
        ]]],
        trouble:[['ul',['پینگ بین Leaf قطع است: Underlay (OSPF FULL؟) را اول چک کن، بعد VXLAN','بسته flood می‌شود: EVPN up نیست یا ingress-replication اشتباه — show nve peers','MTU: VXLAN سربرگ ۵۰ بایت اضافه می‌کند — لینک‌ها باید MTU بالاتر (۱۵۵۰+) بدهند','ECMP نمی‌آید: OSPF همسایه‌ها را روی همهٔ Spine‌ها می‌بینی؟ cost یکسان؟']]],
        exercise:[['ol',['برای ۱۲ رک سرور، تعداد Leaf و Spine را با قاعدهٔ هر Leaf به همهٔ Spine‌ها محاسبه و رسم کن','مسیر بستهٔ یک VM روی Leaf1 تا VM روی Leaf2 را با هر hop بنویس','چرا بدون STP این معماری حلقه نمی‌سازد؟ توضیح بده']]],
        quiz:[['quiz',[
          {q:'چرا ترافیک East-West معماری سه‌طبقه را می‌شکند؟',opts:['چون کند است','چون در طبقه Access می‌پیچد و Distribution را اشباع می‌کند','چون VLAN ندارد','چون روتر ندارد'],a:1,exp:'سرور به سرور داخل Access جریان دارد؛ کلاسیک برای کاربر به سرور ساخته شده بود.'},
          {q:'در Leaf-Spine، Leaf‌ها به چه کسی وصل‌اند؟',opts:['به هم','فقط به همهٔ Spine‌ها','فقط به یک Spine','به Core خارجی'],a:1,exp:'ستارهٔ دو لایه: هر Leaf به همهٔ Spine‌ها؛ هیچ Leaf-Leaf و Spine-Spine نداریم.'},
          {q:'VXLAN چه محدودیتی را می‌شکند؟',opts:['MTU','۴۰۹۴ دامنهٔ VLAN','پهنای باند لینک','تعداد پورت سوئیچ'],a:1,exp:'VNI تا ۱۶M دامنهٔ لایه ۲ — جدای از VLAN ID.'},
          {q:'کنترل‌پلن یادگیری MAC در مدرن چیست؟',opts:[' flooding محض','EVPN روی BGP','STP','ARP استاتیک'],a:1,exp:'EVPN با BGP اعلام MAC/IP می‌کند تا دیتاپلن کنترل‌شده VXLAN باشد.'},
          {q:'نقش Spine در دیتاسنتر چیست؟',opts:['به سرور وصل است','ستون فقرات لایه ۳ بین همهٔ Leaf‌ها','فقط مدیریت','فقط استوریج'],a:1,exp:'Spine به همهٔ Leaf‌ها وصل است و مسیر یک‌پرشی بین هر جفت Leaf می‌سازد.'},
        ]]],
        notes:[['ul',['نمودار Leaf-Spine خودت را از حفظ رسم کن و مسیر یک بسته را فلش بزن','جداول VLAN 4094 و VXLAN 16M را مقایسه‌ای در دفترچه بنویس','خروجی show nve peers و show bgp l2vpn evpn را نگه دار']]],
      },
    },
    { id:'f4-dc2', title:'Data Center پیشرفته — vPC، Fabric و امنیت دیتاسنتر', sub:'Data Center · جلسه ۲', minutes:'۴ جلسه · ۸ ساعت',
      lead:'Leaf-Spine معماری است؛ vPC و Fabric ابزارهای اجرایی‌اند: اتصال دو سوئیچ به‌عنوان یک همسایه، بدون حلقه، با گذر از STP. این درس لایهٔ عملیاتی دیتاسنتر را می‌بندد.',
      sec:{
        goal:[['p','شامل: vPC (peer-link، keepalive، محدودیت‌ها)، OTV/ترکیب سایت مفهومی، امنیت دیتاسنتر (ACLهای شرق‌غرب، microsegmentation)، و استوریج/VM mobility مفهومی.']],
        prereq:[['ul',['Leaf-Spine تمام شده','STP و EtherChannel روان','مبانی BGP/EVPN']]],
        concept:[['h3','vPC در یک جمله'],['p','vPC یعنی دو سوئیچ (pair) برای دستگاه‌های مجاور مثل یک سوئیچ رفتار کنند: پورت‌های dual-homed شما به دو سوئیچ وصل‌اند اما یک LAG معتبر می‌بینند — بدون حلقه، بدون بلاک STP، با گذر از تمام پورت‌ها. شرط: peer-link بین دو سوئیچ + heartbeat (keepalive) برای تشخیص مرگ طرف مقابل.'],['h3','امنیت شرق‌غرب'],['p','داخل دیتاسنتر دیگر «داخل = امن» معنا ندارد: هر سرویس باید فقط پورت و مبدأ مجاز بگیرد. ابزارها: ACLهای اعمالی روی leaf (در مسیر VXLAN یا border)، و در مقیاس بالاتر microsegmentation با SGTag یا policy-based forwarding — دقیقاً همان چیزی که ISE/TrustSec یا SD-Access می‌سازد.']],
        protocol:[['cli','vPC پایه','feature vpc\nvpc domain 10\npeer-keepalive destination 10.10.10.2\npeer-link port-channel 10\n\ninterface port-channel10\n switchport mode trunk\n vpc peer-link\n\ninterface g1/1\n switchport mode trunk\n vpc 101\n\n! وضعیت\nshow vpc\nshow vpc brief']],
        ios:[['cli','وضعیت vPC و امنیت','show vpc\nshow vpc brief\nshow spanning-tree summary\nshow access-lists counters']],
        diagram:[['svg','leaf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — vPC ساده',steps:['دو سوئیچ pair + peer-link و keepalive','یک سرور dual-homed با LACP وصل و از هر دو مسیر ping کن','peer-link را قطع کن: رفتار failover را ببین']},
          {t:'آزمایشگاه ۲ — امنیت شرق‌غرب',steps:['ACL بین دو رک سرور: فقط 443 مجاز','یک ترافیک مسدود را capture کن و hit-counter را ببین','policy را با نام سرویس (نه IP) بازنویسی کن']},
        ]]],
        trouble:[['ul',['vPC دو طرف split-brain: keepalive ندارد یا مسدود است — قبل از همه show vpc','سرور LACP نمی‌گیرد: ترتیب LACP روی هر دو طرف؟ peer-link trunk allowed vlan؟','ACL نمی‌خورد: جهت in/out و مسیر سر بسته (post-VXLAN) را چک کن']]],
        exercise:[['ol',['سه شرط لازم vPC را با دلیل بنویس','چرا vPC بدون keepalive خطرناک است؟','یک policy امنیت شرق‌غرب برای سه سرویس (Web، DB، Backup) بنویس']]],
        quiz:[['quiz',[
          {q:'vPC چه چیزی را حذف می‌کند؟',opts:['نیاز به IP','بلاک شدن پورت‌ها توسط STP','نیاز به سرور','NAT'],a:1,exp:'دو سوئیچ یک همسایه‌اند؛ دستگاه‌ها LAG معتبر می‌بینند و حلقه STP نداریم.'},
          {q:'دو جزء حیاتی vPC؟',opts:['peer-link و keepalive','DNS و DHCP','VLAN و subnet','MTU و CDP'],a:0,exp:'peer-link ترافیک را می‌برد؛ keepalive مرگ طرف مقابل را تشخیص می‌دهد.'},
          {q:'امنیت شرق‌غرب یعنی چه؟',opts:['همه داخل امن‌اند','هر سرویس فقط دسترسی لازم را از مجاز‌ها بگیرد','فقط لبه فایروال دارد','بدون AAA'],a:1,exp:'داخل هم سطح‌بندی می‌شود؛ نفوذ به یک سرویس به سرویس دیگر نمی‌رسد.'},
        ]]],
        notes:[['ul',['وضعیت show vpc را برای حالت‌های normal/upstream-down حفظ کن','نمونه ACL شرق‌غرب سه سرویسی را در دفترچه نگه دار']]],
      },
    },
    { id:'f4-sp1', title:'Service Provider — MPLS، Segment Routing و BGP در مقیاس', sub:'Service Provider · جلسه ۱', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'اپراتورها جهان را به هم وصل می‌کنند: LDP برچسب می‌زند، Segment Routing برچسب را از سیاست می‌سازد، و BGP میلیون‌ها مسیر را حمل می‌کند. این درس زبان شبکه‌های هسته را یاد می‌دهد.',
      sec:{
        goal:[['p','شامل: عملکرد LDP، مفهوم Segment Routing (SR-MPLS با SID)، Traffic Engineering مقدماتی، BGP در مقیاس (route-server، filter-policy)، و نقش IXP مفهومی.']],
        prereq:[['ul',['MPLS L3VPN مفهومی از R&S','BGP کامل از ENCOR','Underlay OSPF/IS-IS روان']]],
        concept:[['h3','LDP چطور برچسب می‌زند؟'],['p','هر LSR با همسایه‌هایش LDP hello می‌دهد، جدول forwarding خودش را اعلام می‌کند و برچسب هر پیشوند را رد و بدل می‌کند؛ نتیجه: LSP (مسیر برچسب‌خورده) از ورودی تا خروجی. اما LDP کور است: مسیر را از IGP می‌گیرد، نمی‌توانی بگویی «این ترافیک از این لینک خاص برود».'],['h3','Segment Routing — برچسب از سیاست'],['p','SR به جای پروتکل پخش برچسب، SID را در هدر بسته (MPLS label یا IPv6 SRH) حمل می‌کند؛ مسیر با لیست SIDها (segment list) توسط مبدأ تعریف می‌شود. نتیجه: TE بدون LDP/PCE-پیچیده، fast reroute سریع، و مسیر «من می‌خواهم» به جای «بهترین IGP».']],
        protocol:[['cli','LDP و SR مفهی','! LDP\nmpls ldp router-id Loopback0 force\ninterface GigabitEthernet0/0\n mpls ip\n\n! SR-MPLS (معادل ساده)\nsegment-routing mpls\nsegment-routing\n sr-prefer-color 100\n\n! مشاهده\nshow mpls ldp bindings\nshow mpls forwarding-table\nshow segment-routing mpls prefix-sid map']],
        ios:[['cli','بررسی LDP/SR','show mpls ldp neighbor\nshow mpls forwarding-table\nshow ip cef 10.10.10.10 detail\nshow segment-routing mpls prefix-sid map']],
        diagram:[['svg','ospf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — LSP ساده',steps:['سه P/PE با LDP بالا','show mpls forwarding-table: برچسب‌ها را ردیابی کن','یک لینک را down کن: LSP چطور بازسازی می‌شود؟']},
          {t:'آزمایشگاه ۲ — SR-TE ساده',steps:['با SID مسیر مشخصی بین دو PE بساز','بسته را با capture یا مسیریابی ردیابی کن','مسیر IGP را عوض کن: ترافیک SR سر جایش می‌ماند؟']},
        ]]],
        trouble:[['ul',['LDP همسایه نمی‌شود: router-id، LDP enabled روی لینک، فیلتر TTL','SR prefix-SID تکراری: روی هر node فقط یک SID یکتا','TE tunnel up ولی ترافیک نمی‌رود: forwarder ورودی SID را می‌شناسد؟']]],
        exercise:[['ol',['تفاوت LDP و SR را در جدول چهار ستونه بنویس','مسیر SR با سه SID برای عبور از یک لینک خاص طراحی کن','چرا IXP ها معمولاً در لبهٔ شهر با ترافیک محلی زیاد‌اند؟']]],
        quiz:[['quiz',[
          {q:'LDP برچسب را از کجا می‌آورد؟',opts:['از BGP','از اعلام همسایگانش بر اساس پیشوند','از DHCP','از ARP'],a:1,exp:'LDP همسایه‌ها جدول‌هایشان را exchange می‌کنند و برچسب per-hop می‌سازند.'},
          {q:'مهم‌ترین فایدهٔ Segment Routing؟',opts:['کاهش MTU','کنترل مسیر توسط مبدأ با SID بدون پروتکل پخش برچسب','حذف BGP','افزایش VLAN'],a:1,exp:'segment list در هدر = سیاست مسیر در مبدأ؛ TE و FRR ساده‌تر می‌شود.'},
          {q:'در SR-MPLS، SID کجای بسته است؟',opts:['در سر TCP','در شاهین MPLS (label)','در payload','در MAC'],a:1,exp:'SID به‌صورت label در شاهین حمل می‌شود (یا در SRH برای SRv6).'},
          {q:'چرا P routerها به BGP نیاز ندارند؟',opts:['چون کندند','چون فقط برچسب swap می‌کنند و اطلاعات VPN ندارند','چون خاموش‌اند','چون OSPF دارند'],a:1,exp:'P فقط زیرساخت برچسب را جلو می‌برد؛ دانش VRF/مشتری نزد PE است.'},
        ]]],
        notes:[['ul',['مسیر یک بستهٔ L3VPN را با شمارهٔ labelهای هر hop بنویس','SID map را از show خروجی بگیر و رسم کن']]],
      },
    },
    { id:'f4-wl1', title:'Wireless — RF، طراحی AP و WLC', sub:'Wireless · جلسه ۱', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'وایرلس یعنی محیطی که کنترلش با هواست: سیگنال، کانال، تداخل. مهندس Wireless با dBm و channel plan شروع می‌کند، نه با کابل.',
      sec:{
        goal:[['p','شامل: مبانی RF (dBm، SNR، باندها)، channel plan و co-channel/adjacent interference، طراحی پوشش (site survey ساده)، معماری WLC (centralized/flexconnect) و امنیت WPA2/WPA3.']],
        prereq:[['ul',['دانشکدهٔ CCNA','لایه ۲ روان (VLAN/Trunk)','مفاهیم SSID و authentication را دیده‌ای']]],
        concept:[['h3','RF یک زبان است'],['p','قدرت سیگنال با dBm سنجیده می‌شود (مثلاً -67dBm برای VoIP مطمئن)، نویز را با SNR می‌سنجیم: سیگنال منهای نویز. هرچه SNR بالاتر، نرخ و پایداری بهتر. باند 2.4 نفوذ بیشتر/ازدحام بیشتر، 5GHz کانال بیشتر و سرعت بالاتر (و 6GHz در WiFi6E/7).'],['h3','کانال‌بندی بدون تداخل'],['p','APهای همسایه نباید کانال یکسان (co-channel) شان به هم بخورد چون CSMA/CA با هم رقابت می‌کنند؛ در 2.4 فقط سه کانال هم‌پوشان‌نشده 1/6/11؛ در 5GHz ده‌ها کانال. هدف طراحی: پوشش یکنواخت -67dBm و حداقل هم‌پوشانی کانال هم‌فاز.'],['h3','WLC چه می‌کند؟'],['p','کنترل‌پلن مرکزی: یادگیری AP، Roaming بین APها، سیاست‌های SSID، و بیمهٔ رفتار یکپارچه. حالت‌ها: centralized (ترافیک به WLC می‌آید)، flexconnect (ترافیک local خروج — سایت شاخه)، و در معماری‌های مدرن‌تر کنترل‌پلن ابری.']],
        protocol:[['cli','WLC و AP ساده','! SSID و VLAN روی WLC\nconfig wlan create 1 Employee-5G Employee\nconfig wlan security wpa akm dot1x enable 1\nconfig wlan interface create 1 Employee-5G vlan 20\n\n! روی AP: channel و power\nconfig 802.11a disable network\nconfig 802.11a channel 36\nconfig 802.11a power local 17\nconfig 802.11a enable network\n\n! وضعیت\nshow ap summary\nshow client summary']],
        ios:[['cli','وضعیت RF و کلاینت‌ها','show ap summary\nshow 802.11a summary\nshow client summary\nshow wireless channel']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — کانال و پوشش',steps:['سه AP با کانال 1/6/11 بچین و تداخل را شبیه‌سازی کن','با WiFi analyzer پوشش -67dBm را بررسی کن','قدرت را زیاد/کم کن و تأثیر روی SNR ببین']},
          {t:'آزمایشگاه ۲ — Roaming و WPA2',steps:['یک SSID روی دو AP با WPA2-Enterprise (یا شبیه‌ساز)','کلاینت را حرکت بده: لحظهٔ roam را با capture ببین','VLAN متفاوت برای Guest و Employee روی یک رادیو']},
        ]]],
        trouble:[['ul',['کلاینت وصل ولی اینترنت نیست: SSID به VLAN درست؟ DHCP و WLC tunnel؟','سرعت پایین: نویز و هم‌پوشانی کانال را چک کن، نه فقط سیگنال','روام نمی‌شود: همان AAA/RADIUS و کلید مشترک روی دو AP؟ fast-roaming (PMF/802.11r) فعال؟']]],
        exercise:[['ol',['برای سالن ۴۰×۲۰ متری، تعداد AP و کانال‌ها را طراحی کن','جدول dBm رایج: -30 عالی، -67 حد نصاب VoIP، -80 قابل استفاده — توضیح بده','چرا 2.4 فقط 1/6/11؟']]],
        quiz:[['quiz',[
          {q:'حد پوشش مطمئن برای VoIP معمولاً؟',opts:['-30dBm','حدود -67dBm','-90dBm','0dBm'],a:1,exp:'کمتر از حدود -67 کیفیت صدا می‌ریزد؛ SNR هم باید ≥25dB باشد.'},
          {q:'در 2.4GHz کانال‌های هم‌پوشان‌نشده؟',opts:['1/5/9','1/6/11','36/40/44','هر کانالی'],a:1,exp:'پهنای کانال 2.4 طوری است که فقط سه تا بدون هم‌پوشانی: 1، 6، 11.'},
          {q:'co-channel interference یعنی چه؟',opts:['دو AP همسایه کانال یکسان دارند و با هم رقابت می‌کنند','کانال خراب','نویز مایکروفر','SSID تکراری'],a:0,exp:'CSMA/CA بین APهای هم‌کانال مشترک است — ظرفیت افت می‌کند.'},
          {q:'WPA3 نسبت به WPA2 چه می‌افزاید؟',opts:['فقط سرعت','handshake مقاوم به brute-force و SAE','حذف رمز','پوشش بیشتر'],a:1,exp:'SAE جایگزین 4-way handshake سنتی می‌شود و حملات offline را سخت می‌کند.'},
        ]]],
        notes:[['ul',['نقشهٔ کانال سایت خودت را رنگی رسم کن','خروجی show ap summary و show client را تفسیر کن']]],
      },
    },
{ id:'f4-ent', title:'Enterprise Networking — زیرساخت سازمانی', sub:'تخصص‌ها · ۷.۱', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'دانشکدهٔ Enterprise عمیق‌ترین مسیر زیرساخت سازمانی است: کمپوس مدرن، SD-Access و SD-WAN، VXLAN/EVPN، و مانیتورینگ. خروجی: مهندسی که شبکهٔ ۱۰۰ شعبه‌ای را طراحی و نگهداری می‌کند.',
      sec:{
        goal:[['p','شامل ۱۵ درس محوری زیر. مدارک هدف: CCNP Enterprise و CCIE Enterprise Infrastructure. خروجی: طراحی و پیاده‌سازی شبکهٔ سازمانی با افزونگی، segmentation و assurance.']],
        prereq:[['ul',['CCNA و مهندسی R&S کامل','ENCOR را دیده‌ای','مبانی BGP و OSPF روان']]],
        concept:[['h3','چه چیزی یک مهندس Enterprise می‌داند؟'],['p','تفاوت این سطح با CCNA در عمق نیست، در «سیستم» است: کمپوس سه‌لایه با Layer-3 distribution، SD-Access برای segmentation سیاست‌محور، SD-WAN برای WAN منعطف، و VXLAN/EVPN برای مقیاس لایه ۲. هر فناوری پاسخ به یک قید است — نه لیستی برای حفظ.']],
        protocol:[['h3','دروس این مسیر'],['ul',['Advanced Campus Design','Cisco Catalyst Architecture','Advanced BGP و OSPF','IS-IS Fundamentals','SD-WAN Architecture','Cisco Catalyst Center','SD-Access','VXLAN و EVPN Fundamentals','VRF و Segmentation','QoS Advanced','Network Assurance','Telemetry','High Availability','Enterprise WAN','IPv6 Advanced']]],
        ios:[['cli','ابزارهای Enterprise','R1# show ip ospf neighbor\nR1# show ip bgp summary\nR1# show vrf\nR1# show sdwan validators   ! در دستگاه SD-WAN\nR1# show interface description\nR1# show platform software interface control-plane statistics']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'۱ — طراحی Campus سه‌لایه',steps:['Core/Distribution/Access با L3 distribution بساز','پینگ end-to-end و مسیرهای OSPF را بررسی کن']},
          {t:'۲ — OSPF چندناحیه',steps:['سه ناحیه + ABR + summarization','LSAها را با show ip ospf database بشمار']},
          {t:'۳ — BGP چند AS',steps:['دو AS با eBGP و policy محلی','local-preference را تغییر و مسیر را عوض کن']},
          {t:'۴ — طراحی SD-WAN',steps:['معماری vManage/vSmart/vEdge را رسم و شبیه‌سازی کن','یک policy مسیر بساز']},
          {t:'۵ — VRF',steps:['دو VRF با آدرس تکراری + import/export','جدول‌ها را جداگانه ببین']},
          {t:'۶ — QoS صدا/ویدیو',steps:['LLQ + EF marking برای RTP','تأخیر را قبل/بعد اندازه بگیر']},
          {t:'۷ — افزونگی کامل',steps:['دو مسیر برای هر لینک حیاتی + failover تست']},
          {t:'۸ — عیب‌یابی Routing پیچیده',steps:['سناریوی طراحی‌شده با سه خرابی هم‌زمان؛ فقط با show حل کن']},
        ]]],
        trouble:[['ul',['SD-Access policy اعمال نشد: SGT و policy set را چک کن','VXLAN پینگ ندارد: underlay اول، بعد overlay','SD-WAN control down: reachability کنسول تا vSmart را جدی بگیر']]],
        exercise:[['ol',['طرح ۱۰۰ شعبه + ۲ دیتاسنتر با فازبندی بنویس','سه تفاوت SD-Access با VLAN سنتی را با مثال بگو','یک capacity plan ساده برای uplink هسته بنویس']]],
        quiz:[['quiz',[
          {q:'در Campus مدرن، Distribution معمولاً لایهٔ چند است؟',opts:['فقط لایه ۲','لایه ۳ (-routing)','فقط فیزیکی','لایه ۷'],a:1,exp:'L3 distribution یعنی مرز VLAN در سوئیچ distribution است — STP کوچک و مسیر کوتاه‌تر.'},
          {q:'SD-Access چه چیزی را سیاست‌محور می‌کند؟',opts:['فقط سرعت','دسترسی بر اساس هویت/SGT نه فقط VLAN','فقط DNS','کابل‌کشی'],a:1,exp:'Segregation با برچسب سیاست (TrustSec/SGT) — کاربر جابه‌جا شد، سیاست همراهش می‌رود.'},
          {q:'Telemetry در Network Assurance چه می‌دهد؟',opts:['فقط ping','دادهٔ لحظه‌ای push توسط دستگاه','فقط لاگ روزانه','بدون مدل'],a:1,exp:'رویداد/وضعیت لحظه‌ای با مدل — پایهٔ داشبورد و هشدار هوشمند.'},
        ]]],
        notes:[['ul',['لیست ۱۵ درس را با وضعیت یادگیری علامت بزن','طرح ۱۰۰ شعبه را به‌صورت سند HLD ذخیره کن']]],
      },
    },
    { id:'f4-sec', title:'Security — تخصص امنیت شبکه', sub:'تخصص‌ها · ۷.۲', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'اینجا دیگر ACL کافی نیست: فایروال نسل جدید (FTD/FMC)، VPNهای سازمانی، NAC با ISE، و معماری Zero Trust. خروجی: زیرساخت امنیتی برای سازمان ۵۰ شعبه‌ای.',
      sec:{
        goal:[['p','شامل ۱۸ درس محوری. مدارک هدف: CCNP Security و CCIE Security. خروجی: طراحی و پیاده‌سازی firewall، VPN، NAC و معماری امنیتی با قابلیت عیب‌یابی.']],
        prereq:[['ul',['Security Fundamentals از CCNA','AAA و 802.1X را دیده‌ای','مبانی VPN و routing']]],
        concept:[['h3','لایه‌های امنیت مدرن'],['p','مرز (firewall با zone/policy)، ارتباط (IPsec site-to-site و remote access)، هویت (ISE/RADIUS/802.1X)، و مشاهده‌پذیری (IDS/IPS و monitoring). Zero Trust یعنی هیچ‌کس — حتی داخل شبکه — بدون احراز هویت و سیاست، دسترسی ندارد.']],
        protocol:[['h3','دروس این مسیر'],['ul',['Security Architecture','Cisco Secure Firewall','ASA و FTD','FMC','Firewall Policies','NAT و Security Zones','Site-to-Site IPsec VPN','Remote Access VPN','Cisco ISE','RADIUS و TACACS+','802.1X','NAC','TrustSec','Zero Trust','IPS و IDS','Secure Network Access','Security Monitoring','Security Troubleshooting']]],
        ios:[['cli','معماری فایروال و VPN','! ASA/FTD نمونه\nASA(config)# interface GigabitEthernet0/0\nASA(config-if)# nameif outside\nASA(config-if)# security-level 0\nASA(config)# object network INSIDE\nASA(config-network-object)# subnet 192.168.1.0 255.255.255.0\nASA(config)# nat (inside,outside) dynamic INSIDE\n\nASA# show vpn sessiondb anyconnect\nASA# show service-policy\nASA# show conn']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'۱ — راه‌اندازی Firewall',steps:['zones و policy پایه بساز','ترافیک مجاز/غیرمجاز را با hit-counter اثبات کن']},
          {t:'۲ — Zone-Based Security',steps:['three-zone: inside/outside/dmz','policy بین zoneها با تست نفوذ ساده']},
          {t:'۳ — Site-to-Site VPN',steps:['two IKE/IPsec tunnels + crypto map','SA را با show crypto isakmp sa ببین']},
          {t:'۴ — Remote Access',steps:['VPN client + split-tunnel','اتصال و مسیرها را بررسی کن']},
          {t:'۵ — ISE',steps:['policy set ساده + منبع AD','رخدادها را در ISE ببین']},
          {t:'۶ — 802.1X',steps:['پورت auto + کلاینت مجاز/غیرمجاز','no-access و access را مقایسه کن']},
          {t:'۷ — AAA مرکزی',steps:['TACACS+ نظارتی روی سوئیچ','لاگ دستورها']},
          {t:'۸ — تحلیل حملات',steps:[' ARP spoof / port scan در آزمایشگاه؛ علامت‌ها در لاگ']},
          {t:'۹ — Zero Trust ساده',steps:['هویت + دسترسی کمترین امتیاز را برای سه نقشه پیاده کن']},
        ]]],
        trouble:[['ul',['VPN up ولی ترافیک نمی‌رود: proxy-arp، NAT exemption یا ACL را چک کن','802.1X پورت را می‌بندد: سرور RADIUS و VLAN سوییچ','policy اعمال نشد: order قواعد و direction (in/out)']]],
        exercise:[['ol',['معماری امنیتی ۵۰ شعبه + ۲ دیتاسنتر را با نقشه بنویس','سه تفاوت ASA و FTD را در جدول بیاور','چرا Zero Trust بدون NAC شدنی نیست؟']]],
        quiz:[['quiz',[
          {q:'security-level در ASA بالاتر یعنی چه؟',opts:['سرعت بیشتر','اعتماد بیشتر به آن zone','پورت بیشتر','لایسنس گران‌تر'],a:1,exp:'ترافیک از high به low آزادتر است؛ برگشت نیاز به rule دارد.'},
          {q:'SITE-to-Site VPN دو طرف چه چیزی را پنهان می‌کند؟',opts:['MAC','ترافیک بین دو سایت را رمزنگاری می‌کند','نام دامنه','DNS'],a:1,exp:'IPsec روی WAN عمومی — محرمانگی و یکپارچگی بین سایت‌ها.'},
          {q:'در ISE، policy set چه می‌گوید؟',opts:['فقط رمز','کیست + چه دستگاهی + کجا = چه اتفاقی','فقط ساعت','فقط IP'],a:1,exp:'سیاست تصمیم بر اساس هویت/دستگاه/مکان — پایهٔ NAC و TrustSec.'},
        ]]],
        notes:[['ul',['چک‌لیست hardening فایروال و VPN را قالب‌بندی کن','یک design review امنیتی از طرح خودت بنویس']]],
      },
    },
    { id:'f4-col', title:'Collaboration و VoIP — ارتباطات سازمانی', sub:'تخصص‌ها · ۷.۶', minutes:'۴ جلسه · ۸ ساعت',
      lead:'صدا روی IP یعنی شبکه باید مثل یک مرکز تلفن رفتار کند: Dial Plan درست، QoS برای RTP، و عیب‌یابی Jitter/Loss. خروجی: سامانهٔ VoIP برای ۲۰ شعبه با مرکز تماس مرکزی.',
      sec:{
        goal:[['p','شامل ۱۷ درس محوری. مدارک هدف: CCNP Collaboration و CCIE Collaboration. خروجی: راه‌اندازی CUCM، Dial Plan، Voice Gateway/CUBE و QoS صدا.']],
        prereq:[['ul',['IP Services و QoS پایه','TCP/UDP و پورت‌ها روان','مفاهیم trunk و VLAN']]],
        concept:[['h3','مسیر یک تماس'],['p','گوشی SIP REGISTER می‌دهد → CUCM تماس را می‌پذیرد و با SDP/INVITE مقصد را می‌گوید → رسانه با RTP (پورت‌های داینامیک) جریان می‌یابد → QoS EF روی WAN تأخیر را کنترل می‌کند. Dial Plan (route pattern) تعیین می‌کند شماره ۰۲۱ کجا برود — قلب تنظیمات تلفنی.'],['h3','سه ستون عیب‌یابی صدا'],['p','Signaling (SIP/H.323 قطع است؟)، Media (RTP می‌آید؟ با چه کدکی؟)، و شبکه (Jitter، Loss، Queue). عیب‌یابی بدون تفکیک این سه، حدس زدن است.']],
        protocol:[['h3','دروس این مسیر'],['ul',['Voice Fundamentals','SIP','RTP و RTCP','SDP','Dial Plan','Cisco Unified CM','Unity Connection','Cisco Voice Gateway','Dial Peers','CUBE','Cisco Webex','Expressway','Call Routing','Voice Security','Video Conferencing','QoS for Voice','Troubleshooting Voice']]],
        ios:[['cli','Voice Gateway و QoS','! Dial Peer نمونه\nvoice-port 0/0/0\n dial-peer voice 100 voip\n  destination-pattern 911\n  session protocol sipv2\n  session target ipv4:10.10.10.20\n  codec g711ulaw\n\n! QoS صدا\npolicy-map WAN\n class VOICE\n  priority percent 10\n\nR1# show dial-peer voice summary\nR1# show voip rtp connections\nR1# show policy-map interface']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'۱ — ثبت IP Phone',steps:['DCHP Option 150 + ثبت گوشی در CUCM/شبیه‌ساز','وضعیت Registered را ببین']},
          {t:'۲ — Dial Plan',steps:['route pattern برای سه شعبه بساز','شماره‌گیری و مسیر تماس را تست کن']},
          {t:'۳ — Voice Gateway + SIP Trunk',steps:['اتصال PBX ساده با dial-peer','trace تماس را دنبال کن']},
          {t:'۴ — QoS صدا',steps:['EF marking + priority queue','با iperf تداخل را بساز و کیفیت را مقایسه کن']},
          {t:'۵ — عیب‌یابی RTP',steps:['Jitter/Loss عمداً بساز (پهنای باند)','show voip rtp و نتیجه را تفسیر کن']},
        ]]],
        trouble:[['ul',['گوشی ثبت نمی‌شود: Option 150؟ VLAN صدا؟ سرور CUCM؟','تماس برقرار می‌شود صدا نیست: RTP/UDP بلاک؟ کدک mismatch؟','کیفیت بد: queue درست؟ EF می‌خورد؟ پهنای باند کافی؟']]],
        exercise:[['ol',['Dial Plan سه شعبه‌ای با کد شهر بنویس','سه علت رایج قطعی صدا را با راه‌حل لیست کن','چرا RTP معمولاً UDP است نه TCP؟']]],
        quiz:[['quiz',[
          {q:'برای صدای بلادرنگ معمولاً از کدام پروتکل رسانه استفاده می‌شود؟',opts:['FTP','RTP روی UDP','SMTP','SSH'],a:1,exp:'RTP شماره‌گذاری و زمان‌بندی می‌دهد؛ UDP تأخیر کم — ترکیب استاندارد VoIP.'},
          {q:'Dial Plan چه می‌کند؟',opts:['رمزنگاری','تعیین مسیر شماره‌گیری به مقصد','تبدیل صدا به متن','ذخیره مخاطب'],a:1,exp:'route-pattern: از این شماره به این gateway/trunk برو — قلب مسیریابی تلفنی.'},
          {q:'اگر تماس برقرار شود ولی صدا نیاید، اول کجا؟',opts:['DNS','RTP و کدک/ACL مسیر رسانه','NTP','MAC'],a:1,exp:'Signaling سالم بوده؛ مشکل در Media path است — جدا کردن دو لایه اولین قدم است.'},
        ]]],
        notes:[['ul',['یک نقشهٔ Dial Plan برای سازمان خودت بکش','خروجی show voip و policy-map را تفسیر محور بنویس']]],
      },
    },
    { id:'f4-auto', title:'Automation — برنامه‌نویسی و اتوماسیون شبکه', sub:'تخصص‌ها · ۷.۷', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'این شاخه از CCNA شروع می‌شود و تا CCIE ادامه می‌یابد: Linux، Python، API، Ansible، IaC، CI/CD و در نهایت AI-Assisted Operations. خروجی: سامانهٔ مدیریت شبکهٔ ۵۰۰ شعبه‌ای.',
      sec:{
        goal:[['p','شامل ۲۰ درس ترتیبی. مدارک هدف: CCNA Automation، CCNP Automation و CCIE Automation (در کنار مسیر اصلی). خروجی: اسکریپت، playbook و pipeline واقعی برای شبکه.']],
        prereq:[['ul',['Python پایه (متغیر/حلقه/dict)','Git پایه','REST و JSON را دیده‌ای']]],
        concept:[['h3','چرا از همان CCNA؟'],['p','اتوماسیون یک دورهٔ جدا نیست، یک عادت است: از همان تغییر کوچک، فایل را در Git نگه دار؛ از همان show، یک اسکریپت گزارش بساز؛ از همان ACL، یک playbook. این تدریج، مهندس را بدون جهش بزرگ به سطح خودکار می‌رساند.'],['h3','ستون‌ها'],['p','زبان (Python)، قرارداد (REST/NETCONF/YANG)، ابزار (Ansible/Terraform)، و فرآیند (Git/CI-CD/Containers). هر ستون بدون بقیه فقط ابزار است؛ با هم سیستم می‌شوند.']],
        protocol:[['h3','دروس به ترتیب'],['table',['#','درس'],[
          ['1','Linux Fundamentals'],['2','Python Fundamentals'],['3','Python Advanced'],['4','Git و GitHub'],
          ['5','JSON و YAML'],['6','REST API'],['7','HTTP و HTTPS'],['8','NETCONF'],
          ['9','RESTCONF'],['10','YANG'],['11','Ansible'],['12','Terraform'],
          ['13','Cisco NSO'],['14','Cisco DevNet'],['15','Infrastructure as Code'],['16','CI/CD'],
          ['17','Containerization'],['18','Automated Testing'],['19','Network Telemetry'],['20','AI-Assisted Operations'],
        ]]],
        ios:[['cli','نمونهٔ اتصال اسکریپت به دستگاه','from netmiko import ConnectHandler\ndevice = ConnectHandler(device_type=cisco_ios, ip=10.0.0.1, username=admin, password=*** )\nprint(device.send_command(show ip interface brief))\n\n# Ansible ad-hoc\nansible switches -m ios_command -a commands=[show version]']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'۱ — Python + Router',steps:['اتصال SSH و گرفتن show version','خروجی را parse و CSV کن']},
          {t:'۲ — خواندن Configuration',steps:['running-config را بگیر و فیلدهای کلیدی را استخراج کن']},
          {t:'۳ — Configuration Generator',steps:['از YAML پیکربندی چند VLAN بساز و به فایل بنویس']},
          {t:'۴ — چند دستگاه هم‌زمان',steps:['دستور show را روی ۵ روتر موازی اجرا کن']},
          {t:'۵ — REST API',steps:['توکن بگیر، GET/POST بزن، JSON را parse کن']},
          {t:'۶ — Playbook',steps:['playbook hostname+banner+save با diff']},
          {t:'۷ — Git برای پیکربندی',steps:['change در شاخه، review، merge، rollback تمرینی']},
          {t:'۸ — تست دسترس‌پذیری',steps:['اسکریپت پینگ ۵۰ شعبه + گزارش خراب‌ها']},
          {t:'۹ — Backup و Audit',steps:['پشتیبان خودکار روزانه + مقایسه با نسخهٔ قبل']},
          {t:'۱۰ — CI ساده',steps:['lint+validate خودکار قبل از اعمال تغییر']},
        ]]],
        trouble:[['ul',['SSH وصل نمی‌شود: کلید/رمز، انگلیسی بودن خروجی، نسخهٔ دستگاه','playbook diff می‌دهد ولی اعمال نمی‌شود: mode و authorization دستگاه','API 401/404: توکن و مسیر را با مستندات چک کن']]],
        exercise:[['ol',['یک اسکریپت گزارش روزانه برای ۱۰ دستگاه بنویس','تفاوت NETCONF و REST را در جدول بیاور','۵۰۰ شعبه: چرا دستی جواب نمی‌دهد؟ با عدد توضیح بده']]],
        quiz:[['quiz',[
          {q:'YANG چه چیزی را توصیف می‌کند؟',opts:['لینک فیزیکی','مدل داده/state دستگاه','رمز','پورت فیزیکی'],a:1,exp:'شکل و قواعد داده — NETCONF/RESTCONF انتقال و تغییر آن را می‌کنند.'},
          {q:'در Git، rollback واقعی با چه؟',opts:['پاک کردن فایل','commit معکوس/ revert','reboot','logout'],a:1,exp:'تاریخچهٔ commit امکان بازگشت کنترل‌شده می‌دهد — هستهٔ GitOps.'},
          {q:'playbook Ansible اصلاً چیست؟',opts:['ویدیو','توصیف وضعیت مورد انتظار + وظایف','یک پروتکل','فایل لاگ'],a:1,exp:'ایده‌آل + وظایف — اجرا تکرارپذیر و diff-pذیر روی دستگاه‌ها.'},
        ]]],
        notes:[['ul',['مسیر ۲۰ درسی را با تاریخ واقعی در Git پیگیری کن','هر هفته یک اسکریپت کوچک به مخزن اضافه کن']]],
      },
    },
    { id:'f4-cyb', title:'Cybersecurity — عملیات امنیت سایبری (SOC)', sub:'تخصص‌ها · ۷.۸', minutes:'۵ جلسه · ۱۰ ساعت',
      lead:'اینجا دیگر جلوی نفوذ نمی‌ایستی؛ نفوذ را می‌بینی، می‌سنجی و پاسخ می‌دهی: SIEM، SOC، Incident Response و Threat Hunting. خروجی: یک مرکز عملیات امنیتی برای شبکهٔ سازمانی.',
      sec:{
        goal:[['p','شامل ۱۷ درس محوری. مدارک و مسیرها: CCNA/CCNP Cybersecurity و گواهینامه‌های مرتبط. خروجی: داشبورد SIEM، فرآیند IR، و تحلیل رخداد واقعی.']],
        prereq:[['ul',['Security Fundamentals و ACL','شبکه و پروتکل‌ها روان','مبانی Linux و لاگ‌خوانی']]],
        concept:[['h3','چرخهٔ عملیات'],['p','جمع‌آوری (لاگ/ترافیک) → تحلیل (SIEM قواعد و همبستگی) → شناسایی (رخداد → حادثه) → پاسخ (containment، eradication، recovery) → درس‌آموزی. SOC بدون فرآیند، فقط داشبورد است.'],['h3','لاگ چه می‌گوید؟'],['p','یک ورود ناموفق SSH تکراری از یک IP، یک تغییر ACL غیرمنتظره، یک پینگ از دامنهٔ مهمان به سرور — هرکدام یک جمله‌اند؛ مهندس امنیت آن‌ها را به یک داستان حادثه تبدیل می‌کند.']],
        protocol:[['h3','دروس این مسیر'],['ul',['Cybersecurity Fundamentals','TCP/IP Security','Network Threats','Threat Intelligence','SIEM','SOC Operations','Incident Response','Security Monitoring','Log Analysis','Threat Hunting','Network Forensics','Endpoint Security','Vulnerability Management','Malware Analysis Fundamentals','Security Automation','Cloud Security','OT Security Fundamentals']]],
        ios:[['cli','جمع‌آوری و تحلیل لاگ','! سمت دستگاه: ارسال لاگ به سرور\nR1(config)# logging host 10.10.10.50\nR1(config)# logging trap informational\nR1(config)# service timestamps log datetime msec\n\n! بررسی محلی\nR1# show logging | include %SEC\nR1# show ip access-lists counters\n\n! در سرور تحلیل (نمونه ELK/SIEM)\n# filter: source IP + failed ssh > 5 in 1min => alert']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'۱ — تحلیل لاگ فایروال',steps:['ده رخداد واقعی/شبیه‌سازی را دسته‌بندی کن','مبدأ/مقصد/زمان را در جدول بیاور']},
          {t:'۲ — ترافیک مشکوک',steps:['pcap را با Wireshark فیلتر کن','رفتار غیرعادی (beaconing ساده) را پیدا کن']},
          {t:'۳ — داشبورد SIEM',steps:['سه rule همبستگی برای brute-force بساز','رویداد تستی را به alert تبدیل کن']},
          {t:'۴ — بررسی رخداد',steps:['یک incident فرضی: timeline از اولین علامت تا اعلام']},
          {t:'۵ — شناسایی رفتار غیرعادی',steps:['baseline ساده از ترافیک عادی؛ انحراف را تعریف کن']},
          {t:'۶ — مدیریت آسیب‌پذیری',steps:['اسکن مجاز در آزمایشگاه + اولویت‌بندی CVSS-مانند']},
          {t:'۷ — Incident Response Simulation',steps:['بازی نقش: تشخیص، contain، report در ۴۵ دقیقه']},
          {t:'۸ — فرایند SOC',steps:['SLA، escalation و نقش‌ها را برای یک شبانه‌روز بنویس']},
        ]]],
        trouble:[['ul',['SIEM سیل می‌دهد: فیلتر منبع و حذف نویز را قبل از rule بگذار','رخداد غلط مثبت زیاد: قاعده را با دادهٔ واقعی kalibrate کن','لاگ نمی‌رسد: سرور، پورت، و trust بین دستگاه و سرور']]],
        exercise:[['ol',['timeline یک حادثهٔ فرضی را با ۶ نقطهٔ زمانی بنویس','سه rule SIEM با پاسخ توضیحی طراحی کن','فرق vulnerability و threat را با مثال بگو']]],
        quiz:[['quiz',[
          {q:'SIEM اصلی‌ترین نقشش؟',opts:['فایروال بودن','همبستگی و تحلیل لاگ از منابع مختلف','رمزنگاری','DNS'],a:1,exp:'جمع، همبستگی و هشدار — دیدن الگو در دریای رویدادها.'},
          {q:'اولین قدم Incident Response؟',opts:['پاک کردن همه','شناسایی و طبقه‌بندی رخداد','reboot سرور','انتشار عمومی'],a:1,exp:'بدون شناسایی درست، هر واکنشی شلخته است — بعد contain و ریشه‌کنی.'},
          {q:'Beaconing در ترافیک یعنی چه؟',opts:['پخش خبر','ارتباط منظم و تکراری مهاجم با C2','یک پروتکل استاندارد','خطای شبکه'],a:1,exp:'الگوی زمان‌بندی‌شدهٔ خروجی به سرور فرماندهی — نشانهٔ کلاسیک در فرآیند hunting.'},
        ]]],
        notes:[['ul',['یک play book سادهٔ IR برای سه نوع رخداد بنویس','لاگ‌های نمونه را با برچسب دقیق در دفترچه نگه دار']]],
      },
    },
    { id:'f4-labs', title:'آزمایشگاه‌های الزامی تخصص‌ها — ۲۰ سناریو', sub:'تخصص‌ها · کارگاه', minutes:'۳ جلسه · ۶ ساعت',
      lead:'بیست سناریوی تخصصی از سه مسیر (DC/SP/Wireless) — قبولی با گزارش و تحلیل معماری، نه فقط «بالا آمده».',
      sec:{
        goal:[['p','اجرای ۲۰ سناریوی تخصصی و تحویل گزارش معماری برای هرکدام.']],
        prereq:[['ul',['چهار درس تخصصی','دسترسی PT/PNETLab/EVE + WLC شبیه‌ساز','دفترچهٔ معماری']]],
        concept:[['p','تفاوت این سطح: سناریوها ترکیبی‌اند — مثلاً Leaf-Spine با ACL شرق‌غرب، یا LDP با BGP policy، یا WLC با VLAN و AAA. باید بتوانی مرز هر فناوری را در طرح تشخیص بدهی.']],
        protocol:[['table',['شماره','سناریو','مسیر'],[
          ['1','Leaf-Spine 4×2 با ECMP','DC'],
          ['2','VXLAN دو سایتی ساده','DC'],
          ['3','EVPN MAC learning','DC'],
          ['4','vPC با failover','DC'],
          ['5','ACL شرق‌غرب + counter','DC'],
          ['6','LDP end-to-end + label trace','SP'],
          ['7','SR-TE اجبار مسیر','SP'],
          ['8','BGP route-server ساده','SP'],
          ['9','MPLS VPN دو مشتری','SP'],
          ['10','Traffic Engineering با cost دستی','SP'],
          ['11','کانال‌پلن سه AP','WL'],
          ['12','WPA2-Enterprise ساده','WL'],
          ['13','Roaming بین دو AP','WL'],
          ['14','.flexconnect سایت شاخه','WL'],
          ['15','RF survey مصنوعی با ابزار','WL'],
          ['16','Leaf-Spine + QoS','DC'],
          ['17','SR + QoS class','SP'],
          ['18','WLC + AAA + VLAN','WL'],
          ['19','عیب‌یابی ترکیبی قطعی چندلایه','ترکیب'],
          ['20','طراحی معکوس از خروجی show','ترکیب'],
        ]]],
        ios:[['note','key','قالب گزارش: هدف ← معماری ← دستورها ← شواهد ← مرز فناوری‌ها ← آموزه.']],
        diagram:[['svg','leaf']],
        lab:[['labs',[{t:'استاندارد قبولی',steps:['اجرای واقعی','گزارش در Git','مرور دو سناریوی ترکیبی با مربی']}]]],
        trouble:[['ul',['گیر ترکیبی: اول لایهٔ فیزیک/underlay، بعد لایه ۲/۳، بعد policy','گیر wireless: اول VLAN/AAA سیمی را ثابت کن، بعد رادیو']]],
        exercise:[['ol',['دو سناریوی ترکیبی جدید طراحی کن','مرز DC/SP/Wireless در یک شرکت واقعی را ترسیم کن']]],
        quiz:[['quiz',[
          {q:'تفاوت کلیدی این سطح با CCNA؟',opts:['دستورهای بیشتر','ترکیب فناوری‌ها و تحلیل مرزها','سرعت بیشتر','پلتفرم دیگر'],a:1,exp:'مهندسی یعنی تشخیص مرز و هماهنگی فناوری‌ها، نه حفظ فرمان.'},
          {q:'در سناریوی Leaf-Spine + ACL، اول چه چیزی را ثابت می‌کنی؟',opts:['ACL','Underlay و ECMP','QoS','AAA'],a:1,exp:'بدون underlay سالم، سیاست معنا ندارد — لایه به لایه بالا بیا.'},
        ]]],
        notes:[['ul',['وضعیت ۲۰ سناریو را علامت بزن','بهترین گزارش را برای نمونهٔ مصاحبه نگه دار']]],
      },
    },
    { id:'f4-proj', title:'پروژهٔ پایان تخصص‌ها — طراحی یک سایت کامل', sub:'تخصص‌ها · پروژه', minutes:'۴ جلسه · ۸ ساعت',
      lead:'طراحی کامل یک سایت: دیتاسنتر کوچک Leaf-Spine، اتصال SP با L3VPN، و Wireless سالنی — با سند معماری، توپولوژی اجراشدنی و دمو.',
      sec:{
        goal:[['p','تحویل: سند معماری (فازبندی)، توپولوژی قابل اجرا، پیکربندی نمونه هر لایه، و دموی زنده با عیب‌یابی یک خرابی.']],
        prereq:[['ul',['۲۰ سناریوی تخصصی','طرح اولیهٔ سایت (تعداد رک، کاربر، سرویس)','Git و قالب گزارش']]],
        concept:[['h3','فازبندی واقعی'],['p','پروژه‌های واقعی یک‌باره اجرا نمی‌شوند: فاز ۱ زیرساخت (لینک/Underlay)، فاز ۲ سرویس (VLAN/VRF/Wireless)، فاز ۳ امنیت (ACL/AAA)، فاز ۴ اتوماسیون و مانیتورینگ. طرح تو باید همین فازها را داشته باشد.']],
        protocol:[['svg','leaf'],['p','مهم‌ترین بخش تحویل: نقشهٔ مسیر یک بستهٔ کاربر (Wireless) تا سرور (دیتاسنتر) و برگشت — با hopهای نام‌برده و مرز هر فناوری.']],
        ios:[['cli','قالب جمع‌آوری شواهد','# زیرساخت\nssh core1 "show ip ospf neighbor" > evidence/core.txt\nssh leaf1 "show nve peers" >> evidence/leaf.txt\nssh wlc "show ap summary" >> evidence/wl.txt\n\n# سپس اسکریپت بررسی: همه FULL؟ همه up؟ تعداد APها درست؟']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'چک‌لیست تحویل',steps:['سند معماری با فازبندی','توپولوژی + پیکربندی نمونه هر لایه','اسکریپت evidence','دمو + عیب‌یابی خرابی عمدی']}]]],
        trouble:[['ul',['پروژه پراکنده می‌شود: فازها را قفل کن و هر فاز را فقط با شواهد ببند','یک لایه جا می‌افتد: چک‌لیست مرور روزانه داشته باش']]],
        exercise:[['ol',['سه risk فاز ۲ را با mitigation بنویس','اگر Wireless فاز ۳ عقب بیفتد، اثر بر کل پروژه چیست؟']]],
        quiz:[['quiz',[
          {q:'چرا فازبندی در پروژه لازم است؟',opts:['برای زیبایی سند','کاهش ریسک و امکان بازگشت/تست مرحله‌ای','چون فروشنده می‌خواهد','به‌خاطر قانون'],a:1,exp:'هر فاز قابل تست و برگشت است؛ خرابی یک‌جا همه را نمی‌سوزاند.'},
          {q:'مرز فناوری در تحویل یعنی چه؟',opts:['کابل کشی','کجا Wireless تمام می‌شود و Underlay شروع — با نام لایه‌ها','رنگ‌بندی','نام سرور'],a:1,exp:'مهندسی یعنی بدانی هر فناوری کجا تمام می‌شود و با چه قراردادی به بعدی می‌دهد.'},
        ]]],
        notes:[['ul',['پروژه را با README و تگ نسخه تحویل بده','بازخورد را در دفترچه ثبت کن']]],
      },
    },
  ]
},
{
  id:'f5', num:'۵', title:'دانشکدهٔ پنجم — CCIE Enterprise Infrastructure', duration:'۱۲–۲۴ ماه', tag:'CCIE',
  gradStandard:'۱۰ سناریوی عملی + آزمون سخت‌گیرانه: سه قدم از یکدیگر جدا می‌شوند (CE — Candidate Engineer، PE — Provisional Engineer، RE — Routing Expert). هر قدم با گزارش مهندسی و defense شفاهی تأیید می‌شود.',
  intro:'اینجا دیگر مسیریابی یک مهارت نیست، یک «چشم» است: چشمی که به خروجی show نگاه می‌کند و مسیر، سیاست و خرابی را همان‌جا می‌بیند. این دانشکده شما را از سطح «درست پیکربندی می‌کنم» به سطح «درست فکر می‌کنم» می‌برد.',
  lessons:[
    { id:'f5-l1', title:'تحلیل مسیر و سیاست در سطح CCIE', sub:'CCIE · جلسه ۱', minutes:'۸ جلسه · ۱۶ ساعت',
      lead:'CCIE از شما نمی‌پرسد «دستور چیست»؛ می‌پرسد «اگر این پارامتر عوض شود، مسیر کجا می‌رود و چرا؟». این درس تحلیل مسیر و سیاست را تا سطح دفاع شفاهی تمرین می‌دهد.',
      sec:{
        goal:[['p','شامل: تحلیل FIB و RIB، برهم‌کنش AD/LPM/Metric در سناریوهای واقعی، policyهای چندمرحله‌ای (route-map، tag، communities)، و تمرین defense: توضیح شفاهی یک مسیر در دو دقیقه.']],
        prereq:[['ul',['ENCOR و ENARSI کامل','۲۰ سناریوی R&S با گزارش','خواندن show ip route و show ip bgp بدون کمک']]],
        concept:[['h3','سه جدول، سه پرسش'],['p','RIB جدول کنترلی است (چه چیزی یاد گرفته شده)، FIB جدول حمل (چه چیزی عملاً در سر بسته می‌رود)، و جدول سیاست (کدام مسیر با کدام علامت/اقدام). در لبهٔ حمل، ممکن است مسیر RIB «بهترین» باشد ولی FIB به خاطر policy یا CEF disable متفاوت عمل کند — CCIE دقیقاً همین شکاف را می‌سنجد.'],['h3','مدل دفاع'],['p','هر مسیر را باید بتوانی در سه جمله گفت: 1) از کجا آمد (پروتکل/منبع) 2) چرا برنده شد (معیار و رقیبان) 3) با تغییر کدام پارامتر می‌افتد. اگر جملهٔ سوم را نداری، هنوز CCIE فکر نکرده‌ای.']],
        protocol:[['cli','ابزارهای تحلیل','! چرا این مسیر؟\nR# show ip route 10.0.0.0 longer-prefixes\nR# show ip cef 10.0.0.5 detail\nR# show ip route <proto> backup\n\n! سیاست اعمال‌شده\nR# show route-map\nR# show ip bgp neighbors <nb> received-routes\nR# show ip bgp community exact-match\n\n! برهم‌کنش پروتکل‌ها\nR# show ip protocols\nR# show ip ospf border-routers']],
        ios:[['cli','ابزار دفاع زنده','R# show ip route | begin Gateway\nR# show ip bgp\nR# show ip ospf neighbor\nR# show route-map\nR# show running-config | section router']],
        diagram:[['svg','ospf']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — رقابت چهارمنبع',steps:['یک پیشوند را از OSPF، EIGRP، static و BGP اعلام کن','برنده را قبل از دیدن جدول پیش‌بینی کن، بعد show بگیر','AD یکی را دستی عوض کن و برنده را دوباره حدس بزن']},
          {t:'آزمایشگاه ۲ — سیاست چندلایه',steps:['route-map سه‌مرحله‌ای با match/set در لایه‌های مختلف','ردیابی: هر مسیر در کدام گام گیر کرد (trace با debug نرم)','خروجی show route-map را برای defense توضیح بده']},
          {t:'آزمایشگاه ۳ — FIB در عمل',steps:['با ip route و ip cef تفاوت RIB/FIB را ببین','یک مسیر null/route کن و رفتار FIB را ببین','مرور: مسیری که RIB دارد ولی FIB ندارد؟']},
        ]]],
        trouble:[['ul',['مسیر ناخواسته برنده شد: AD و LPM را قدم به قدم حساب کن — حدس نزن','policy اعمال نشد: مسیر از کجا آمد؟ route-map در جهت درست؟ شرط‌ها با همان منبع؟','FIB با RIB نمی‌خواند: route flap، disable cef، یا policy-based routing']]],
        exercise:[['ol',['سه‌جمله‌ای یک مسیر BGP را برای یک تازه‌کار بنویس (defense تمرینی)','یک سناریوی رقابت AD/Metric/LPM با جواب درست طراحی کن','تفاوت show ip route و show ip cef را با مثال بیان کن']]],
        quiz:[['quiz',[
          {q:'اگر دو مسیر با پیشوند متفاوت بیایند، اول چه چیزی تعیین‌کننده است؟',opts:['AD','LPM (بلندترین پیشوند)','سن مسیر','تعداد هاپ'],a:1,exp:'اول بلندترین پیشوند (LPM) برنده می‌شود؛ AD فقط بین مسیرهای هم‌پیشوند رقابت می‌کند.'},
          {q:'RIB و FIB چه فرقی دارند؟',opts:['هیچ','کنترل‌پلن در برابر جدول حمل واقعی','فقط نام','یکی IPv4 و دیگری v6'],a:1,exp:'RIB یادگیری است، FIB آن چیزی است که بسته را در لحظه جلو می‌برد.'},
          {q:'در defense، جملهٔ سوم هر مسیر؟',opts:['نام روتر','با تغییر کدام پارامتر مسیر می‌افتد','رنگ خروجی','تعداد خط'],a:1,exp:'پیش‌بینی رفتار با تغییر پارامتر = نشانهٔ تسلط، نه حفظ.'},
          {q:'community در BGP چیست؟',opts:['گروه کاربران','برچسب روی مسیر برای سیاست','پورت لایه ۴','نوع LSA'],a:1,exp:'برچسب عددی/رشته‌ای روی مسیر تا route-map بتواند بر اساس آن تصمیم بگیرد.'},
        ]]],
        notes:[['ul',['هر هفته یک «سه‌جمله‌ای مسیر» برای یک سناریو بنویس و تمرین شفاهی کن','خروجی‌های show تحلیلی را در دفترچهٔ CCIE نگه دار']]],
      },
    },
    { id:'f5-l2', title:'عیب‌یابی چندپروتکلی در سطح CCIE', sub:'CCIE · جلسه ۲', minutes:'۸ جلسه · ۱۶ ساعت',
      lead:'خرابی واقعی یک لایه نیست: یک کابل خراب می‌تواند OSPF را بشکند، سیاست BGP را بی‌اثر کند و AAA را قطع کند. این درس مدل عیب‌یابی چندپروتکلی را تا حد مصاحبهٔ عملی می‌رساند.',
      sec:{
        goal:[['p','شامل: مدل لایه‌ای عیب‌یابی، تکنیک‌های isolate (binary search روی شبکه)، عیب‌یابی route flap، مشکلات MTU/fragmentation در تونل‌ها، و عیب‌یابی همزمان چند پروتکل.']],
        prereq:[['ul',['درس اول CCIE تمام','۱۰ سناریوی عیب‌یابی پیشرفته','صبر و انضباط ثبت شواهد']]],
        concept:[['h3','مدل چهارلایه‌ای'],['p','1) شواهد جمع کن (بدون حدس) 2) مرز مشکل را تنگ کن (کدام لینک/کدام پروتکل/کدام سیاست) 3) فرضیهٔ واحد بساز و تست کن 4) رفع + راستی‌آزمایی + مستندسازی. نکتهٔ CCIE: هرگز دو چیز را هم‌زمان عوض نکن — وگرنه نمی‌دانی کدام درست کرد.'],['h3','شکست‌های زنجیره‌ای'],['p','MTU در تونل: پینگ کوچک می‌رود، بزرگ نه — کلاسیک OSPF over GRE/WXLAN. Route flap: لینک پایدار نیست و همسایه‌ها مدام می‌آیند/می‌روند — اول سمت فیزیکی/قدرت سیگنال، بعد timers، بعد سیاست. DNS/AAA: اگر control-plane امن دسترسی ندارد، همهٔ پروتکل‌ها «خراب» به نظر می‌رسند.']],
        protocol:[['cli','ابزار اثبات','! MTU و تونل\nR# ping 10.10.10.2 size 1472 df\nR# ping 10.10.10.2 size 1473 df\nR# show interface | include MTU|output queue\n\n! ثبات همسایه\nR# show ip ospf neighbor | begin NBR\nR# show logging | include OSPF-5-ADJCHG\n\n! لینک فیزیکی\nR# show interfaces counters errors\nR# show platform hardware capacity']],
        ios:[['cli','شواهد لینک و پایداری','R# show interfaces counters errors\nR# show ip ospf neighbor\nR# show logging | include ADJCHG\nR# show processes cpu | exclude CPU']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — MTU کلاسیک',steps:['تونل GRE بساز و پینگ با df را تست کن','مسیر MTU end-to-end را با trace و پینگ size sweep پیدا کن','رفع: ip tcp adjust-mtu یا MTU لینک — و راستی‌آزمایی']},
          {t:'آزمایشگاه ۲ — Route Flap',steps:['یک لینک را با noise پریودی قطع کن (یا loop مصنوعی)','موج‌های adjacency و SPF را در لاگ ببین','تعدیل timers/priority و مقایسهٔ ثبات']},
          {t:'آزمایشگاه ۳ — قطعی چندلایه',steps:['عمداً سه خرابی هم‌زمان بساز: ACL + DNS + MTU','با مدل چهارلایه‌ای فقط با شواهد حل کن','گزارش: کدام شواهد شما را به کدام لایه برد؟']},
        ]]],
        trouble:[['ul',['حل نشدن بعد از ۱۰ دقیقه: شواهد کم است — جمع‌آوری کن، نه بیشتر دست زدن','خرابی بعد از change: rollback کن، سپس یک‌یک تغییر بده','پینگ داخلی را راحت قبول نکن: تست از چند مبدأ و چند اندازه بگیر']]],
        exercise:[['ol',['چک‌لیست ۱۲تایی عیب‌یابی OSPF بنویس (از کابل تا LSA)','یک گزارش واقعی از خرابی سه‌لایه‌ای خودت بنویس','چرا «دو تغییر هم‌زمان» ممنوع است؟ با مثال توضیح بده']]],
        quiz:[['quiz',[
          {q:'پینگ کوچک می‌رود و 1500 نه، احتمال اول؟',opts:['DNS','MTU/fragmentation','AAA','STP'],a:1,exp:'کلاسیک: payload بزرگ‌تر از MTU مسیر و DF زده شده — با sweep اندازه اثبات کن.'},
          {q:'در مدل عیب‌یابی، قدم اول؟',opts:['reboot','جمع‌آوری شواهد','تعویض قطعه','تماس'],a:1,exp:'شواهد قبل از فرضیه؛ حدس بدون داده، زمان را می‌سوزاند.'},
          {q:'چرا دو تغییر هم‌زمان ممنوع است؟',opts:['چون سریع است','چون نمی‌توانی اثر هر کدام را جدا کنی','چون گران است','بهینه نیست'],a:1,exp:'تجزیهٔ علّی: فقط با تغییر واحد، نتیجه قابل انتساب است.'},
          {q:'route flap اول به کدام لایه شک می‌دهد؟',opts:['لایهٔ فیزیکی/پایداری لینک','سیاست BGP','DNS','NTP'],a:0,exp:'ناپایداری مکرر adjacency معمولاً ریشه در لینک/قدت/قدت سیگنال/timer دارد، نه در سیاست.'},
        ]]],
        notes:[['ul',['هر خرابی حل‌شده را در یک صفحه ثبت: شواهد، فرضیه، تغییر، اثبات','زمان تا ریشه (MTTR ذهنی) خودت را اندازه بگیر']]],
      },
    },
    { id:'f5-l3', title:'اتوماسیون سطح CCIE — CI/CD پیکربندی و Telemetry', sub:'CCIE · جلسه ۳', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'مهندس CCIE امروز باید بتواند پیکربندی را مثل کد نگه دارد: نسخه، تست، استقرار کنترل‌شده، و مانیتورینگ زنده. این درس pipeline واقعی را می‌سازد.',
      sec:{
        goal:[['p','شامل: GitOps برای شبکه، اعتبارسنجی YAML/JSON با تست (pytest/Ansible Molecule مفهومی)، staged deployment، Telemetry (gNMI/modeled) در برابر polling سنتی، و داشبورد عملیاتی.']],
        prereq:[['ul',['اتوماسیون ENCOR','Python و Git روان','دسترسی به دستگاه یا شبیه‌ساز قابل API']]],

        concept:[['h3','پیکربندی مثل کد'],['p','بدون Git هر تغییر یک قمار است: با Git تغییر diff دارد، review دارد، rollback دارد. مسیر: تغییر در شاخه → اعتبارسنجی خودکار (lint + تست ساختاری) → استقرار در staging → بررسی شواهد → production. هر مرحله بدون شواهد رد می‌شود.'],['h3','Telemetry در برابر Polling'],['p','Polling (SNMP) یعنی هر چند ثانیه بپرس «چه خبر؟» — دیر، پرهزینه و سطحی. Telemetry یعنی دستگاه خودش رویداد/وضعیت را push می‌کند (gNMI/gRPC، models YANG) — برای آنچه لحظه‌ای است (لینک flap، صف، خطا) حیاتی.']],
        protocol:[['cli','خط لولهٔ نمونه','# 1) تغییر در git\n$ git checkout -b change/dscp-voice\necho "dscp ef" >> changes/voice.yml\ngit commit -am "mark voice as EF"\n\n# 2) اعتبارسنجی\n$ yamllint changes/voice.yml\n$ ansible-playbook validate.yml --check\n\n# 3) استقرار پله‌ای با دروازهٔ شواهد\n$ ansible-playbook deploy.yml --limit leaf1\n$ ansible-playbook verify.yml   # اگر fail → rollback خودکار\n\n# 4) Telemetry\n$ python subscribe.py --target leaf1 --model /interfaces']],
        ios:[['cli','اجرای pipeline','ansible-playbook validate.yml --check\nansible-playbook deploy.yml --limit leaf1\nansible-playbook verify.yml\n\ngit log --oneline -5\ngit diff HEAD~1 -- changes/']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — GitOps ساده',steps:['مخزن پیکربندی + اعتبارسنجی lint','PR بساز و diff را review کن','استقرار روی یک دستگاه با rollback در صورت fail']},
          {t:'آزمایشگاه ۲ — Telemetry',steps:['اشتراک gNMI یا REST-event بگیر و رویداد لینک را لحظه‌ای ببین','داشبورد ساده (حتی CSV + اسکریپت) برای وضعیت لینک‌ها','مقایسه: کشف یک flap با telemetry در برابر poll 30 ثانیه‌ای']},
        ]]],
        trouble:[['ul',['استقرار نیمه‌کاره می‌ماند: دروازهٔ verify نداری — هر deploy باید evidence gate داشته باشد','اعتبارسنجی سبز بود ولی دستگاه خراب شد: تست ساختاری کافی نیست، تست رفتاری هم بگذار','telemetry سیل داده می‌دهد: فیلتر مدل/موضوع در اشتراک بگذار، نه در پس‌پردازش']]],
        exercise:[['ol',['یک pipeline پنج‌مرحله‌ای برای تغییر ACL بنویس (از PR تا verify)','چرا polling برای لینک flap کافی نیست؟ با عدد توضیح بده','شرط rollback خودکار چه باشد؟']]],
        quiz:[['quiz',[
          {q:'گیت بعد از استقرار staging چیست؟',opts:['review انسانی دوباره','verify خودکار شواهد، در غیر این صورت rollback','صبر یک روزه','تغییر مجدد'],a:1,exp:'بدون دروازهٔ شواهد، استقرار یعنی قمار؛ با آن، تغییر کنترل‌شده است.'},
          {q:'Telemetry چه تفاوتی با SNMP دارد؟',opts:['سریع‌تر و push توسط دستگاه','بدون مدل','فقط متن','رایگان‌تر'],a:0,exp:'push لحظه‌ای با مدل (YANG) در برابر poll سطحی و کند.'},
          {q:'در GitOps، منبع حقیقت کجاست؟',opts:['حافظهٔ مهندس','مخزن Git','فایل روی دستگاه','ایمیل'],a:1,exp:'مخزن = وضعیت مورد انتظار؛ دستگاه باید به آن برسد و تفاوت دیده شود.'},
        ]]],
        notes:[['ul',['یک مخزن پیکربندی با lint و validate راه‌اندازی کن','اولین اشتراک telemetry را در یک صفحه مستند کن']]],
      },
    },
    { id:'f5-labs', title:'آزمایشگاه‌های CCIE — ۷۰ سناریوی ترکیبی (بخشی از ۲۰۰ استاندارد)', sub:'CCIE · کارگاه', minutes:'۸ جلسه · ۱۶ ساعت',
      lead:'استاندارد نهایی: ۲۰۰ سناریوی ترکیبی. این دانشکده ۷۰ تای آن را به‌صورت الزامی می‌گذارد؛ ۱۳۰ تای دیگر مسیر آزاد تا پایان ۲۴ ماه است.',
      sec:{
        goal:[['p','اجرای ۷۰ سناریوی الزامی با گزارش کامل و defense شفاهی هر هفته.']],
        prereq:[['ul',['سه درس CCIE','زمان روزانهٔ ۲ ساعت پیوسته','دفترچهٔ دفاع']]]
        ,
        concept:[['p','تفاوت با سطوح پیشین: در CCIE، خرابی‌ها «طراحی‌شده»‌اند: چند گره، چند پروتکل، چند سیاست هم‌زمان. شما باید بتوانید بدون دست زدن، از روی شواهد نقشهٔ خرابی را بکشی.']],
        protocol:[['table',['حوزه','تعداد','نمونه'],[
          ['Routing/Policy','20','رقابت چهارمنبع، tag loop، BGP path manipulation'],
          ['Switching/L2','10','vPC، STP edge cases، LACP غلط'],
          ['Security','10','AAA، ACL پیچیده، hardening با تست'],
          ['Automation','10','API + pipeline + rollback'],
          ['Architecture','10','Leaf-Spine، SR، QoS end-to-end'],
          ['Trouble','10','خرابی‌های چندلایهٔ طراحی‌شده'],
        ]]],
        ios:[['note','key','گزارش هر سناریو با سه‌جملهٔ مسیر + شواهد + defense ثبت می‌شود.']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'استاندارد قبولی',steps:['۷۰ سناریوی الزامی','defense هفتگی دو سناریو','آرشیو شواهد در Git']}]]],
        trouble:[['ul',['گیر ذهنی: اول شواهد کامل، بعد نقشهٔ خرابی، بعد دست زدن','دفاع ناموفق: یعنی سه‌جملهٔ مسیر را نداری — درس را مرور کن']]],
        exercise:[['ol',['از ۷۰، ده موردی که دو بار خوردی را استخراج و تقویت کن','یک خرابی طراحی‌شدهٔ جدید بساز با جواب مستند']]],
        quiz:[['quiz',[
          {q:'استاندارد کلی CCIE در این طرح؟',opts:['۵۰ سناریو','۲۰۰ سناریوی ترکیبی','فقط آزمون کتبی','پروژه تنها'],a:1,exp:'۲۰۰ سناریو؛ ۷۰تای این دانشکده الزامی و بقیه مسیر آزاد ۲۴ ماهه.'},
          {q:'در defense، اگر جملهٔ سوم را نگویی؟',opts:['قبول می‌شوی','یعنی تسلط نداری و باید مرور کنی','فرقی ندارد','مربی کمک می‌کند'],a:1,exp:'پیش‌بینی رفتار با تغییر پارامتر، خط مرزی CE/PE/RE است.'},
        ]]],
        notes:[['ul',['تقویم ۷۰ سناریو را با تاریخ واقعی بچین','defenseهای ضعیف را علامت تکرار بزن']]],
      },
    },
    { id:'f5-proj', title:'پروژهٔ CCIE — طراحی و دفاع زنده', sub:'CCIE · پروژه', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'پروژهٔ نهایی: یک شبکهٔ چندناحیهٔ کامل با سیاست، امنیت و اتوماسیون — و مهم‌تر از خود شبکه، دفاع زندهٔ آن در برابر پرسش‌های بی‌امان مربی.',
      sec:{
        goal:[['p','طراحی، پیاده‌سازی و دفاع زنده: ۴۵ دقیقه ارائه + ۴۵ دقیقه پرسش‌وپاسخ فنی دربارهٔ هر تصمیم معماری.']],
        prereq:[['ul',['۷۰ سناریوی الزامی','طرح شبکه با دلیل هر تصمیم','تمرین شفاهی هفتگی']]],
        concept:[['h3','دفاع چیست؟'],['p','مربی به هر تصمیم طرح گیر می‌دهد: «چرا OSPF و نه IS-IS؟»، «اگر این لینک برود؟»، «این ACL چه چیزی را جا انداخته؟» — پاسخ باید از روی شواهد و tradeoff باشد، نه «بهتر بود».']],
        protocol:[['svg','topo'],['p','خروجی پروژه: سند معماری + مخزن پیکربندی + آرشیو شواهد + فایل دفاع (ویدیو یا متن).']],
        ios:[['cli','خلاصهٔ شواهد پروژه','# یک دستور برای هر ادعای سند\nfor c in "show ip ospf neighbor" "show ip bgp summary" "show route-map" "show access-lists counters"; do\n  echo "=== $c ===" >> evidence/final.txt\n  ssh core1 "$c" >> evidence/final.txt\ndone']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'چک‌لیست دفاع',steps:['سند ۸ صفحه‌ای با tradeoff هر تصمیم','پیکربندی اجراشده و تمیز','دفاع زنده و ثبت پرسش‌ها','نقشهٔ رشد: سه قدم بعدی تا RE']}]]],
        trouble:[['ul',['دفاع می‌شکند: به جای حفظ، شواهد را نشان بده — show کن زنده','پروژه ناقص می‌ماند: scope را کوچک و عمیق کن، نه وسیع و سطحی']]],
        exercise:[['ol',['۲۰ پرسش احتمالی مربی را خودت بنویس و پاسخ سه‌خطی بده','یک tradeoff واقعی پروژه را در یک صفحه تحلیل کن']]],
        quiz:[['quiz',[
          {q:'مهم‌ترین خروجی دفاع؟',opts:['طول سند','کیفیت استدلال با شواهد و tradeoff','سرعت جواب','لحن'],a:1,exp:'مهندس CCIE تصمیمش را با داده و مبادله (tradeoff) دفاع می‌کند، نه با ادعا.'},
          {q:'اگر مربی بگویید «این طراحی چرا؟» بهترین پاسخ؟',opts:['چون رایج است','چون شرط X را داشتیم و این گزینه آن را با قیمت Y پاسخ می‌دهد','چون کتاب گفته','چون قبلاً جواب داده'],a:1,exp:'شرط + گزینه + قیمت (tradeoff) = پاسخ مهندسی.'},
        ]]],
        notes:[['ul',['هر پرسش دفاع را با پاسخ خودت در دفترچه ثبت کن','سه قدم بعدی تا RE را با تاریخ بنویس']]],
      },
    },
  ]
},
{
  id:'f6', num:'۶', title:'دانشکدهٔ ششم — CCDE (طراحی)', duration:'۱۲–۱۸ ماه', tag:'DESIGN',
  gradStandard:'میزان قبولی: ۱۲۰ سناریوی طراحی با دفاع شفاهی. هر طرح باید tradeoff ثبت‌شده داشته باشد؛ طرح بدون «چرا نه گزینهٔ دیگر»، قبول نیست.',
  intro:'CCDE آخرین ایستگاه مسیر طراحی است: جایی که دیگر دستور مهم نیست، تصمیم مهم است. مهندس طراحی می‌تواند ده گزینه را ببیند، سه تا را رد کند، و دو تا را با هزینه/فایده انتخاب و بنویسد — طوری که تیم بتواند همان را بدون حضورش اجرا کند.',
  lessons:[
    { id:'f6-d1', title:'اصول طراحی — نیاز، قیدها و tradeoff', sub:'CCDE · جلسه ۱', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'طراحی با «چه چیزی بسازیم؟» شروع نمی‌شود؛ با «چه چیزی مهم است؟» شروع می‌شود: در دسترس بودن، مقیاس، امنیت، هزینه و زمان. این درس چارچوب تبدیل نیاز به طرح را می‌بندد.',
      sec:{
        goal:[['p','شامل: چارچوب نیازسنجی (RFP/RFS)، اولویت‌بندی قیدها، tradeoff-محوری، الگوهای طراحی رایج (hub-spine، dual-site، hybrid)، و اصول ساده‌سازی.']],
        prereq:[['ul',['هر دانشکدهٔ مسیریابی کامل','تجربهٔ پروژهٔ واقعی یا شبیه‌سازی‌شده','مهارت نوشتن سند فنی']]],
        concept:[['h3','طرح، پاسخ به قیدهاست'],['p','هیچ طرحی «بهترین» مطلق نیست؛ طرح، پاسخ به مجموعه‌ای از قیدهاست: بودجه، تیم، زمان، در دسترس بودن ۹۹.۹٪، امنیت خاص. مهندس طراحی اول قیدها را استخراج و اولویت‌بندی می‌کند، بعد گزینه می‌سازد.'],['h3','tradeoff زبان مشترک است'],['p','هر انتخاب هزینه‌ای دارد: active-active گران‌تر و پیچیده‌تر است؛ single-homing ارزان و شکننده؛ overlay منعطف ولی لایهٔ عیب‌یابی اضافه دارد. سند طراحی خوب، ستون «هزینهٔ این انتخاب» را دارد، نه فقط «مزایا».'],['h3','سادگی، اولین قاعده'],['p','هر فناوری که تیم نمی‌تواند بفهمد و عیب‌یابی کند، در بحران خطر است. طرح باید با «کمترین فناوری لازم برای پاسخ به قیدها» ساخته شود — نه با جدیدترین فناوری موجود.']],
        protocol:[['table',['عامل','اگر مهم‌تر شود','اگر ارزان‌تر شود'],[
          ['در دسترسی','مسیر/مکان/سایت دوم، active-active','سایت تکی و پذیرش ریسک'],
          ['مقیاس','Leaf-Spine، BGP، overlay','ساده‌ترین توپولوژی جواب‌ده'],
          ['امنیت','AAA، segmentation، لایه‌های چندگانه','کنترل لبه و hardening پایه'],
          ['زمان','استفاده از تکنولوژی آماده و تیم موجود','آموزش و پیاده‌سازی بلندمدت'],
          ['هزینه','پرداختنی برای قیدهای بالا','کاهش لایسنس/لینک/پیچیدگی'],
        ]]],
        ios:[['cli','الگوی مستندسازی تصمیم','# قالب یک صفحه‌ای هر تصمیم\nDECISION: (چه چیزی تصمیم گرفته شد)\nCONTEXT: (کدام قید این را ایجاب کرد)\nOPTIONS: (سه گزینه)\nCHOSEN: (گزینهٔ انتخابی + چرا)\nCOST: (هزینه/ریسک انتخاب)\nREVISIT: (چه زمانی دوباره بررسی شود)']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — نیازساقی سند',steps:['یک RFP کوچک (۱۰ خط) بنویس','قیدها را استخراج و اولویت‌بندی کن','سه گزینه با ستون tradeoff بساز']},
          {t:'آزمایشگاه ۲ — رد کردن گزینه',steps:['یک طرح «مدرن اما پیچیده» را برای تیم کوچک رد کن — با دلیل','طرح جایگزین ساده‌تر بنویس و قیدها را پاسخ دهی']},
        ]]],
        trouble:[['ul',['طرح شکست می‌خورد: قیدها ناقص‌اند — برگرد و دوباره بپرس','مشتری همه‌چیز می‌خواهد: tradeoff را جدول کن و اولویت بخواه','فناوری جدید فشار می‌آورد: «برای کدام قید لازم است؟» را بپرس']]],
        exercise:[['ol',['برای شرکت ۲۰۰نفره سه قید اصلی را بنویس','یک صفحهٔ decision record برای یک انتخاب واقعی بنویس','سه دلیل سادگی را با مثال شبکه بیان کن']]],
        quiz:[['quiz',[
          {q:'اولین قدم طراحی؟',opts:['لیست دستورها','استخراج و اولویت‌بندی قیدها','خرید لایسنس','نقشهٔ فیزیکی'],a:1,exp:'بدون قید، «بهترین» تعریف ندارد؛ طرح پاسخ به قیدهاست.'},
          {q:'tradeoff یعنی چه؟',opts:['فقط مزیت','انتخاب با هزینهٔ آشکار در ستون کناری','خطا','هزینهٔ کم'],a:1,exp:'هر انتخاب چیزی را می‌پردازد؛ سند خوب هزینه را پنهان نمی‌کند.'},
          {q:'چرا سادگی قاعدهٔ اول است؟',opts:['چون زیباست','چون در بحران فقط چیزی قابل عیب‌یابی است که تیم بفهمد','چون ارزان است همیشه','چون فروشنده می‌خواهد'],a:1,exp:'پیچیدگی در لحظهٔ خرابی تبدیل به ساعت قطعی می‌شود.'},
          {q:'اگر قید «۹۹.۹٪» باشد، کدام اول می‌آید؟',opts:['تک‌سایت ارزان','سایت دوم/افزونگی مسیر','WLAN','پروتکل جدید'],a:1,exp:'در دسترسی بالا افزونگی مکان/مسیر را ایجاب می‌کند — بقیه تابع آن‌اند.'},
        ]]],
        notes:[['ul',['قالب decision-record را برای ۱۰ تصمیگیری شبکه پر کن','هر طرح قدیمی را با ستون tradeoff بازنویسی کن']]],
      },
    },
    { id:'f6-d2', title:'طرح نهایی کشوری — از نیاز تا سند قابل اجرا', sub:'CCDE · جلسه ۲', minutes:'۸ جلسه · ۱۶ ساعت',
      lead:'پروژهٔ ملی: چند سایت در چند شهر، امنیت حساس، بودجهٔ محدود و زمان کوتاه. این درس همان چیزی است که آزمون CCDE از شما می‌خواهد: طراحی کامل با دفاع.',
      sec:{
        goal:[['p','شامل: معماری چندسایتی (WAN امن، افزونگی)، segmentation سازمانی، نقشهٔ مهاجرت فازبندی‌شده، و سند نهایی قابل تحویل به تیم اجرا.']],
        prereq:[['ul',['درس اول CCDE','دانش DC/SP/Enterprise','تجربهٔ نوشتن سند معماری']]],
        concept:[['h3','معماری چندسایتی'],['p','هسته: WAN امن (MPLS/SD-WAN یا hybrid) با دو اپراتور در لبهٔ حساس؛ افزونگی در هر لایه فقط جایی که قید می‌خواهد (بودجه همه‌جا active-active نیست). segmentation: سایت مرکزی/شعب/پیمانکار هرکدام دامنهٔ دسترسی خودش.'],['h3','مهاجرت، بخشی از طرح است'],['p','هیچ شبکه‌ای یک‌باره عوض نمی‌شود: فاز ۰ آزمایش، فاز ۱ زیرساخت، فاز ۲ سرویس، فاز ۳ حذف قدیمی. هر فاز معیار موفقیت و برنامهٔ بازگشت دارد — اگر ندارد، هنوز طرح نیست.'],['h3','سند تحویلی چه شکلی دارد؟'],['p','یک سند ۱۵–۲۰ صفحه‌ای: خلاصهٔ اجرایی، قیدها، معماری با نقشه، تصمیم‌ها با tradeoff، فازبندی، ریسک‌ها، و پیوست فنی (آدرس‌پلن، لیست فناوری، معیار پذیرش). تیم اجرا باید بدون حضور شما بتواند شروع کند.']],
        protocol:[['table',['فاز','محتوا','معیار موفقیت'],[
          ['0','آزمایشگاه و proof-of-concept','هر فناوری کلیدی یک بار اجرا شد'],
          ['1','زیرساخت (لینک، هسته، امنیت لبه)','پینگ end-to-end بین سایت‌ها'],
          ['2','سرویس‌ها و segmentation','ترافیک هر دامنه فقط در مرز خودش'],
          ['3','مهاجرت کاربران و حذف قدیمی','بدون قطعی برنامه‌ریزی‌شده'],
        ]]],
        ios:[['cli','قالب پیوست فنی','# آدرس‌پلن (نمونه)\n# HQ: 10.0.0.0/8\n#   - infra: 10.0.0.0/16\n#   - users: 10.10.0.0/16\n#   - servers: 10.20.0.0/16\n# Branches: 10.(100+i).0.0/16\n\n# معیار پذیرش (مثال)\n# ping HQ<->Branch RTT < 60ms, loss 0%\n# failover لینک اپراتور 2 < 30s']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱ — سند کامل',steps:['قیدها و اولویت‌ها','معماری + نقشه + آدرس‌پلن','جدول تصمیم‌ها با tradeoff','فازبندی و ریسک']},
          {t:'آزمایشگاه ۲ — دفاع زنده',steps:['۳۰ دقیقه ارائه','پرسش‌های بی‌امان دربارهٔ هر ستون','بازنویسی بخشی از طرح در لحظه بر اساس قید جدید']},
        ]]],
        trouble:[['ul',['طرح بیش از حد بزرگ می‌شود: scope را با قید بودجه/زمان قیچی کن','مهاجرت نادیده گرفته می‌شود: هر فاز rollback دارد؟ اگر نه، طرح ناقص است','دفاع می‌شکند: به «چرا نه گزینهٔ دیگر» جواب نداری — tradeoff را تمرین کن']]],
        exercise:[['ol',['فاز ۰ را با سه آزمایش مشخص بنویس','پنج ریسک پروژه را با احتمال/اثر و mitigation جدول کن','خلاصهٔ اجرایی ۱۰ خطی طرح را بنویس']]],
        quiz:[['quiz',[
          {q:'اگر فازبندی rollback نداشته باشد؟',opts:['پروژه قوی است','طرح ناقص است — هنوز قابل اجرا نیست','فایده ندارد','زمان کمتری می‌برد'],a:1,exp:'بدون برگشت پذیری، ریسک غیرقابل کنترل است — طراحی نیمه‌کاره است.'},
          {q:'خلاصهٔ اجرایی برای چه کسی است؟',opts:['فقط مهندس اجرا','تصمیم‌گیرندهٔ غیرفنی و تیم پروژه','فروشنده','هیچ‌کس'],a:1,exp:'کسی که بودجه و زمان را می‌دهد باید در یک صفحه بفهمد چه می‌شود و چرا.'},
          {q:'در مهاجرت، فاز ۰ چیست؟',opts:['حذف قدیمی','آزمایش و proof-of-concept','خرید','ارسال سند'],a:1,exp:'هر فناوری کلیدی اول در آزمایشگاه باید یک بار واقعاً اجرا شود.'},
        ]]],
        notes:[['ul',['یک سند ۱۵ صفحه‌ای واقعی بنویس — حتی برای شبکهٔ خیالی','هر تصمیم را با قالب decision-record ثبت کن']]],
      },
    },
    { id:'f6-proj', title:'پروژهٔ CCDE — طراحی کشوری با دفاع', sub:'CCDE · پروژه', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'طرح کامل یک سازمان کشوری با دفاع زندهٔ ۹۰ دقیقه‌ای — معیار پایان مسیر طراحی در این آکادمی.',
      sec:{
        goal:[['p','تحویل: سند طراحی کامل + پیوست فنی + دفاع زنده در برابر کمیتهٔ سه‌نفره (معمار، امنیت، عملیات).']],
        prereq:[['ul',['دو درس CCDE','طرح پیش‌نویس','تمرین هفتگی دفاع']]],
        concept:[['h3','کمیته سه‌گانه'],['p','هرکدام زاویهٔ خودش را می‌پرسد: معمار «چرا این معماری؟»، امنیت «کجا نفوذپذیر است؟»، عملیات «ساعت ۳ شب خرابی را چه کسی و چطور پیدا می‌کند؟». طرح خوب از هر سه سؤال عبور می‌کند.']],
        protocol:[['svg','topo'],['p','در دفاع: اگر کمیته قیدی را عوض کند (مثلاً بودجه نصف شود)، طرح را در لحظه تعدیل کن — نشانهٔ مهندس طراحی واقعی بودن.']],
        ios:[['cli','چک‌لیست تحویل نهایی','# هر بخش سند باید به یک پیوست وصل باشد\n# 1. قیدها          -> قیدنامه امضاشده\n# 2. معماری         -> نقشه + آدرس‌پلن\n# 3. تصمیم‌ها       -> جدول tradeoff\n# 4. فازبندی       -> جدول زمانی + معیار\n# 5. ریسک‌ها        -> احتمال/اثر/mitigation\n# 6. معیار پذیرش   -> تست قابل اجرا']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'دفاع نهایی',steps:['۴۵ دقیقه ارائه','۴۵ دقیقه پرسش سه‌نفره','بازنویسی یک بخش در لحظه با قید جدید','ثبت بازخورد و درس‌آموزی']}]]],
        trouble:[['ul',['دفاع به بحث تبدیل می‌شود: به قیدها برگرد، نه به فناوری','سند بلند و کم‌عمق می‌شود: هر صفحه باید یک تصمیم یا شاهد داشته باشد']]],
        exercise:[['ol',['پنج پرسش سخت احتمالی از هر زاویه بنویس و پاسخ بده','درس‌آموزی نهایی: سه اشتباه رایج طراحی خودت را بنویس']]],
        quiz:[['quiz',[
          {q:'اگر در دفاع قید بودجه عوض شد، چه می‌کنی؟',opts:['دفاع از طرح قبلی','تعدیل فوری طرح بر اساس قید جدید و توضیح اثرها','قطع ارائه','انکار'],a:1,exp:'طراحی یعنی پاسخ به قیدها؛ قید عوض شد = پاسخ باید عوض شود.'},
          {q:'سند طراحی خوب کدام است؟',opts:['بلندترین','با tradeoff و معیار پذیرش قابل اجرا','پر از اسکرین‌شات','بدون ریسک'],a:1,exp:'تصمیم + هزینه + معیار سنجش = سندی که تیم بدون شما می‌تواند اجرا کند.'},
        ]]],
        notes:[['ul',['پروژه را در Git با نسخه‌ها نگه دار','بازخورد کمیته را عیناً ثبت کن']]],
      },
    },
    { id:'f6-arch', title:'Principal Network Architect — جایگاه معمار ارشد شبکه', sub:'مسیر نهایی · مرحلهٔ ۸', minutes:'۶ جلسه · ۱۲ ساعت',
      lead:'مرحلهٔ هشتم نقشهٔ Master یک مدرک نیست: Principal Network Architect جایگاه شغلی معماری ارشد است — جایی که تصمیم فنی به زبان کسب‌وکار ترجمه می‌شود و چندین شاخهٔ تخصصی زیر یک چشم‌انداز معماری جمع می‌شوند.',
      sec:{
        goal:[['p','در پایان: می‌توانی یک سند معماری سطح CIO بنویسی، tradeoffهای چندملیتی را با زبان بودجه توضیح دهی، چرخهٔ حیات فناوری شبکه را مدیریت کنی، و تیم‌های تخصصی را زیر یک استاندارد معماری هماهنگ کنی.']],
        prereq:[['ul',['CCDE یا معادل تجربی','تجربهٔ چند پروژهٔ بزرگ end-to-end','توانایی نوشتن سند فنی و غیرفنی']]],
        concept:[['h3','این مرحله چه فرقی با CCDE دارد؟'],['p','CCDE طراحی را می‌آموزد؛ Principal Architect تصمیم را «مالک» می‌شود: بودجه، ریسک، زمان، افراد و فناوری را با هم می‌سنجد و پاسخ‌گوی نتیجه است. مدرک اینجا وجود ندارد — اعتبار با نمونه کار و تصمیم‌های درست ساخته می‌شود.'],['h3','دامنهٔ کاری'],['p','چهار سطح مکالمه: با CIO/مدیر — اثر کسب‌وکار و ریسک؛ با مدیر پروژه — زمان و وابستگی‌ها؛ با مهندسان — استاندارد و جزئیات؛ با فروشنده/اپراتور — قرارداد و SLA. معمار ارشد تنها کسی است که هر چهار زبان را هم‌زمان حرف می‌زند.']],
        protocol:[['h3','مسیر رشد تا این جایگاه'],['ol',['سال ۱ تا ۲: مبانی، CCNA، عملیات روزمره','سال ۳ تا ۴: تخصص + پروژه‌های سازمانی','سال ۵ تا ۶: CCIE/CCDE یا تجربه هم‌ارز + مالکیت طراحی','سال ۷ به بعد: معماری چندحوزه‌ای، راهبری فنی و تصمیم بودجه‌ای']],
          ['table',['سطح','تمرکز خروجی'],[
            ['طراح','سند HLD/LLD قابل اجرا'],
            ['معمار','tradeoff و چرخهٔ حیات فناوری'],
            ['معمار ارشد','چشم‌انداز، بودجه، ریسک و هماهنگی چند تیم'],
          ]],
        ],
        ios:[['cli','قالب سند معماری سطح بالا','# Executive Architecture Note (یک صفحه)\nCONTEXT:   business goal + constraint (budget/time/risk)\nCURRENT:   3-line state of network + top 3 gaps\nOPTIONS:   A/B/C with cost + risk + timeline\nRECOMMEND: chosen option + why-not-others\nROADMAP:   4 quarters, each with measurable outcome\nMETRICS:   availability, change-failure-rate, MTTR, cost/unit']],
        diagram:[['svg','topo']],
        lab:[['labs',[
          {t:'۱ — سند یک‌صفحه‌ای CIO',steps:['یک تصمیم واقعی (مهاجرت WAN) را در قالب بالا بنویس','بازخورد: آیا غیرفنی آن را می‌فهمد؟']},
          {t:'۲ — معماری چندتخصصی',steps:['Enterprise+Security+DC+Automation را در یک نقشه جمع کن','مرز مسئولیت هر تیم را مشخص کن']},
          {t:'۳ — چرخهٔ حیات',steps:['یک فناوری در حال end-of-life را با جایگزین و فاز مهاجرت بنویس']},
          {t:'۴ — جلسهٔ تصمیم',steps:['سناریو: بودجه نصف شد — طرح را در لحظه تعدیل و دفاع کن']},
        ]]],
        trouble:[['ul',['سند فنی می‌شود: مخاطب را عوض کن — اثر و ریسک اول، دستور آخر','تصمیم بدون tradeoff: هر گزینه باید هزینهٔ خودش را صریح بنویسد','همه‌چیز مهم می‌شود: اولویت‌بندی با بودجه واقعی، نه لیست آرزوها']]],
        exercise:[['ol',['یک Executive Architecture Note واقعی برای سازمان خودت بنویس','سه ریسک معماری سال آینده را با اثر/احتمال جدول کن','بنویس: چرا «Principal» بودن یعنی پاسخ‌گو بودن، نه فقط دانستن']]],
        quiz:[['quiz',[
          {q:'تفاوت CCDE و Principal Network Architect؟',opts:['هیچ','اولی مهارت طراحی، دومی مالکیت تصمیم و پاسخ‌گویی کسب‌وکار','دومی فقط مدرک','اولی عملی است'],a:1,exp:'جایگاه شغلی با دامنهٔ مسئولیت بیشتر — نه یک آزمون دیگر سیسکو.'},
          {q:'مهم‌ترین خروجی سند معماری برای CIO؟',opts:['لیست دستورها','گزینه‌ها با هزینه/ریسک و توصیهٔ روشن','نقشهٔ رنگی','نام تأمین‌کنندگان'],a:1,exp:'تصمیم‌گیرنده به گزینه، قیمت و ریسک نیاز دارد — نه جزئیات CLI.'},
          {q:'اگر بودجه نصف شد؟',opts:['رد کردن پروژه','تعدیل فوری طرح با اولویت‌بندی قیدها','ادامه با همان طرح','تغییر تیم'],a:1,exp:'معماری پاسخ به قیدهاست؛ قید عوض شد = پاسخ باید بازنویسی شود.'},
        ]]],
        notes:[['ul',['یک نمونهٔ Executive Note در پورتفولیو نگه دار','بازخورد یک غیرفنی را روی سندت جدی بگیر']]],
      },
    },
  ]
},
  ]
};
