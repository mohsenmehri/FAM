# FAM Academy v2 — گزارش نهایی نسخه قابل ارائه

تولید: `2026-11-24T19:23:49+00:00`
وضعیت کلی: **PASS / قابل ارائه برای دموی فردا**
شاخه / HEAD: `arena/5473d411-fam` / `430b4212d1edd4a290c7da578c3372c604d983dd`
`main` / `origin/main`: `430b4212d1edd4a290c7da578c3372c604d983dd` / `430b4212d1edd4a290c7da578c3372c604d983dd` — بدون تغییر
بروزرسانی: نسخه v2 در **قالب موجود آکادمی FAM** ادغام، روی شاخه فعال Commit/Push و دستورات استقرار VM در `reports/academy-v2-deployment-fa.md` اضافه شد. شاخه remote ساخته شد؛ `main` همچنان بدون تغییر است.

## ۱. خلاصه اجرایی

آکادمی قدیمی بازسازی نشده و ۱۴۳ فایل حذفشده قبلی بازگردانده نشدند. یک Vertical Slice کامل و نسخهدار v1 از صفر ساخته شد و سپس داخل پوسته قالب موجود FAM (`academy-reference-ui.css`، sidebar/topbar/section-head، پل تم و لینک بازگشت به FAM) قرار گرفت: داشبورد RTL، ۲۳ مسیر، ۵ دوره متصل و قابل ارائه، ۱۰ درس کامل ۱۶بخشی، ۳ شبیهساز واقعی با منطق قابل تست، ۲ لاب شبیهسازیشده، آزمون/نتیجه، پیشرفت، API نسخهدار، Validator و تستهای خودکار. محتوای ۱۸ دوره دیگر صادقانه بهعنوان نقشه راه P1 علامتگذاری شده تا درس ضعیف/تکراری تولید نشود.

مانیفست مستقل v1: `37` فایل محتوایی + خود `manifest.json` = ۳۸ فایل روی دیسک؛ `aggregateSha256=2bf847e997730d831c9bc14f042d6afd5470a5b85b642d08eb9ddbbdf75f2594`.
مانیفست ریشه بدون تغییر: SHA-256 `4e6e209a453aa48b1d5390151d3b8ed4654605977c43f66dd5cd0556c04365d3`؛ ۲۱۳ ورودی / ۱۴۳ missing مربوط به حذفهای حفظشده / ۴ mismatch مربوط به فایلهای tracked تغییرکرده / ۰ خطای ساختاری.

## ۲. معماری جدید

| لایه | مسیر | نقش |
|---|---|---|
| محتوای نسخهدار | `server/www/academy-content/v1/` | کاتالوگ، ۱۰ درس، ۳ شبیهساز، ۲ لاب، تمرینها، منابع، ۴ Schema، ۱۵ SVG و مانیفست مستقل |
| تولید محتوا | `tools/build_academy_v2_content.py` | Builder قطعی و بدون وابستگی؛ بازتولید کامل v1 |
| اعتبارسنجی | `tools/validate_academy_v2.py` | ساختار، لینکها، IDها، ترتیب مسیرها، Quiz، لابها، هشها، RTL/Responsive، CJK/Secret |
| موتور خالص | `server/www/academy-assets/academy-engine.js` | `arpResolve`, `vlanForward`, `ospfAdjacency`, quiz, lab state؛ بدون DOM/شبکه/دستگاه |
| رابط کاربری | `server/www/academy-assets/academy-v2.{css,js}` + `server/private_ui/academy.html` | SPA vanilla RTL، مسیرها، درس مرحلهای، شبیهساز، لاب، آزمون، پیشرفت |
| قالب FAM | `server/www/academy-assets/academy-reference-ui.css` + لایه سازگاری v2 | حفظ پوسته آکادمی FAM، sidebar/topbar/section-head، منوی جمعشو، تم روشن/تیره، لینکهای بازگشت به بخشهای FAM |
| Runtime تولیدی | `server/app.py` | کلید ایزوله `famAcademyV2.progress.v1` و ۸ endpoint `/api/academy/v2/*` روی درخت v1 |
| Preview امن | `server/academy_preview_server.py` | سرور stdlib بدون Flask برای ارائه و تست HTTP؛ بدون ذخیرهسازی progress و بدون اتصال تجهیز |
| تستها | `tests/test_academy_content.py`, `tests/test_academy_v2_api.py`, `tests/test_academy_v2_engine.test.mjs`, `tests/test_academy_v2_ui.test.mjs` | محتوا/API/موتور/جریان end-to-end UI |
| اجرای تست | `tools/run_academy_v2_tests.py` | اجرای کامل Validator + Python + Node + UI برروی API واقعی |

## ۳. قابلیتهای آماده

- داشبورد حرفهای RTL/تاریک/Responsive با ۳ breakpoint (`1100px`, `820px`, `480px`)، ۱۴ قانون grid و جداسازی LTR برای کد/ترمینال.
- ادغام با قالب موجود آکادمی FAM: CSS مرجع قدیمی حفظ شد؛ `academy-v2.js` پوسته `.app-shell`، sidebar، topbar، section-head، breadcrumb، ناوبری موبایل، دکمه تم و لینک `/app` را میسازد، بدون اجرای `academy-reference-shell.js` قدیمی.
- ۲۳ مسیر با ترتیب ۱..۲۳، پیشنیاز/مسیر بعدی معتبر، اهداف و سطح؛ ۲۳ دوره شامل ۵ دوره live و ۱۸ دوره P1 شفاف.
- ۱۰ درس واقعی هرکدام ۱۶ بخش: مفهوم، عمیق، دیاگرام، مثال، سناریو، دستورات، تشریح خطبهخط، خروجی Sample/Simulated، اشتباهات، عیبیابی، نکات، تفاوت نسخه/استاندارد، خلاصه، منابع، آزمون، گام بعد.
- ۳ شبیهساز تعاملی: ARP/MAC discovery (`arpResolve`)، VLAN/802.1Q Trunk (`vlanForward`)، OSPF adjacency (`ospfAdjacency`)؛ پارامترها تصمیم و جدول بستهها را تغییر میدهند.
- ۲ لاب داخلی VLAN/Trunk و OSPF Single-Area با توپولوژی، جدول آدرسدهی، مراحل، دستورات، خروجی برچسبخورده، سناریوی خرابی، عیبیابی و معیار موفقیت؛ آداپتورهای آینده `enabled=false`.
- آزمون سناریومحور، نمره، پاسخ تشریحی، ذخیره پیشرفت تحت کلید جدید؛ کلیدهای قدیمی کاربران حفظ شدند.
- پیشرفت: localStorage در Preview، و در Runtime تولیدی همگامسازی با `/api/academy/progress` و همان سیاست CSRF/Origin.
- API تولیدی و Preview: `health`, `catalog`, `exercises`, `references`, `lesson/{id}`, `simulation/{id}`, `lab/{id}`, `quiz/{lessonId}`؛ مسیریابی امن داخل `v1`.
- خروجیهای دستورات و لابها صریحاً `Sample / Simulated — Internal Simulator` هستند؛ هیچ خروجی بهعنوان دستگاه Cisco واقعی معرفی نشده است.

## ۴. محدودیتها و کارهای ناتمام صادقانه

- **۱۸ دوره P1**: فقط ساختار/نقشهراه دارند؛ محتوای ضعیف یا کپیشده تولید نشد.
- **شبیهسازها**: ۳ مورد P0 پیادهسازی شده؛ فهرست بلند درخواستی (STP/EtherChannel/BGP/NAT/DHCP/DNS/TCP/… ) در این نسخه پیادهسازی نشد.
- **لابها**: فقط Safe Internal Simulator؛ اجرا روی تجهیز واقعی، PNETLab، EVE-NG، SSH/Telnet، Docker یا شبکه عملیاتی انجام نشد و آداپتورها غیرفعالاند.
- **تست بصری مرورگر**: Chromium/Playwright/Selenium نصب نیست؛ عکسبرداری/پیکسلتست/کلیک واقعی مرورگر انجام نشد. بهجای آن `academy-v2.js` واقعی در DOM-shim اجرا و مسیر کامل تست شد.
- **Runtime Flask**: بسته Flask در محیط موجود نیست؛ ۱۲ تست وابسته به Flask بهصورت `skipped` گزارش شدند. قرارداد `app.py` بهصورت استاتیک/AST تست شد و معادل API readonly/quiz روی Preview واقعی HTTP اجرا شد.
- **Preview stateless**: در سرور Preview پیشرفت فقط در localStorage مرورگر ذخیره میشود و عمداً روی دیسک/DB نوشته نمیشود.
- Commit/Push فقط روی شاخه فعال `arena/5473d411-fam` انجام شد؛ شاخه remote ساخته شد. هیچ PR، Merge، تغییر شاخه، تغییر `main`، بازنویسی `MANIFEST.sha256` ریشه، اجرای عملیاتی Nginx/VM/Docker توسط Arena یا اتصال به تجهیز انجام نشد. دستورات استقرار در `reports/academy-v2-deployment-fa.md` ارائه شدهاند.

## ۵. نتایج واقعی تستها

| تست | نتیجه واقعی |
|---|---|
| `python3 -B tools/validate_academy_v2.py` | **PASS**؛ ۱۵ دسته بررسی، ۰ خطا |
| `python3 -B -m unittest discover -s tests -p "test_*.py" -v` | **Ran 49 tests … OK (skipped=12)** |
| `node --test tests/test_academy_v2_engine.test.mjs` | **8 pass / 0 fail** |
| `node --check academy-engine.js` و `node --check academy-v2.js` | **هر دو exit 0** |
| `node --test tests/test_academy_v2_ui.test.mjs` (file fixtures) | **1 pass / 0 fail** |
| همان تست با `ACADEMY_V2_API_BASE` روی Preview HTTP | **1 pass / 0 fail** |
| همان تست علیه Preview زنده پورت ۸۰۰۰ | **1 pass / 0 fail** |
| `python3 -B tools/run_academy_v2_tests.py` | **Overall PASS**؛ ۷ فرمان همگی exit 0 |
| پایداری `unittest` (۳ بار متوالی) | **۳ × Ran 49 tests … OK (skipped=12)** |
| بررسی CJK/لغات سرگردان روی ۵۵ فایل جدید/تغییرکرده | **۰ مورد** |
| بررسی RTL/Responsive | HTML `lang=fa dir=rtl viewport`؛ CSS شامل `direction: rtl`، ۳ media query و ۱۴ grid rule |

گزارش ماشینی و لاگ کامل: `reports/academy-v2-verification.md` و `reports/academy-v2-test-logs.txt`.

## ۶. روش اجرا و ارائه

### Preview زنده (پیشنهادی برای دمو)

```bash
cd /home/user/FAM/01-خام-پروژه
python3 -B server/academy_preview_server.py --host 0.0.0.0 --port 8000
# سپس /academy را باز کنید
```

در همین نشست، یک Preview زنده روی پورت ۸۰۰۰ نیز آغاز شده است؛ لینک آن در پیام نهایی/UI نمایش داده میشود.
تست جریان کامل SPA و بررسی نبود `X-Frame-Options`/`frame-ancestors` روی همان Preview زنده نیز با موفقیت اجرا شد.

### مسیر دموی پیشنهادی

1. داشبورد → کارت «شروع یادگیری» / «همه مسیرها».
2. مسیرها → «مشاهده ساختار» یک دوره live.
3. دوره → «مطالعه» درس `l01-osi-tcpip-encapsulation`.
4. درس → مراحل ۱ تا ۵، سپس «آزمون».
5. «اجرای شبیهساز» ARP → تغییر `targetIp` به `203.0.113.10` → «اجرا» و مشاهده `Remote delivery via gateway`.
6. «ورود به لاب» VLAN/Trunk → اجرای مرحله اول و مشاهده ترمینال Sample/Simulated.
7. آزمون → پاسخها → نمره/تشریح → «پیشرفت من».

### Runtime تولیدی

`server/app.py` صفحه `/academy` را همانند قبل با session/CSRF/nonce سرو میکند و endpointهای v2 را اضافه کرده است. برای اجرای واقعی آن به محیطی با Flask و پیکربندی FAM نیاز است؛ در این sandbox فقط قرارداد استاتیک و Preview تست شد.

### بازتولید و تست

```bash
cd /home/user/FAM/01-خام-پروژه
python3 -B tools/build_academy_v2_content.py
python3 -B tools/validate_academy_v2.py
python3 -B tools/run_academy_v2_tests.py
```

## ۷. فایلها

- **حذفشده حفظشده**: `143` فایل قدیمی (دقیقاً همان ۱۴۳ مورد مأموریت قبل). فهرست کامل در `reports/academy-v2-baseline.md` و پیوست زیر.
- **فایلهای tracked تغییرکرده**: `4` مورد:
  - `01-خام-پروژه/server/app.py`
  - `01-خام-پروژه/server/private_ui/academy.html`
  - `01-خام-پروژه/tests/test_academy_content.py`
  - `01-خام-پروژه/tests/test_app_api.py`
- **فایلهای جدید اضافهشده به شاخه**: `53` مورد (پس از Commit دیگر untracked نیستند):

  - `01-خام-پروژه/server/academy_preview_server.py`
  - `01-خام-پروژه/server/www/academy-assets/academy-engine.js`
  - `01-خام-پروژه/server/www/academy-assets/academy-v2.css`
  - `01-خام-پروژه/server/www/academy-assets/academy-v2.js`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l01-osi-tcpip-encapsulation.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l02-ethernet-arp.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l03-vlan-access-ports.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l04-trunk-8021q.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l05-ipv4-subnetting.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l06-ipv6-addressing.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l07-static-routing.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l08-ospf-neighbor-formation.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l09-ospf-spf-cost.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/l10-acl-filtering.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/lab-ospf-single-area.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/lab-vlan-trunk.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/sim-arp-discovery.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/sim-ospf-neighbor.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/assets/diagrams/sim-vlan-trunk.svg`
  - `01-خام-پروژه/server/www/academy-content/v1/catalog.json`
  - `01-خام-پروژه/server/www/academy-content/v1/exercises.json`
  - `01-خام-پروژه/server/www/academy-content/v1/labs/lab-ospf-single-area.json`
  - `01-خام-پروژه/server/www/academy-content/v1/labs/lab-vlan-trunk.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l01-osi-tcpip-encapsulation.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l02-ethernet-arp.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l03-vlan-access-ports.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l04-trunk-8021q.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l05-ipv4-subnetting.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l06-ipv6-addressing.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l07-static-routing.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l08-ospf-neighbor-formation.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l09-ospf-spf-cost.json`
  - `01-خام-پروژه/server/www/academy-content/v1/lessons/l10-acl-filtering.json`
  - `01-خام-پروژه/server/www/academy-content/v1/manifest.json`
  - `01-خام-پروژه/server/www/academy-content/v1/references.json`
  - `01-خام-پروژه/server/www/academy-content/v1/schemas/catalog.schema.json`
  - `01-خام-پروژه/server/www/academy-content/v1/schemas/lab.schema.json`
  - `01-خام-پروژه/server/www/academy-content/v1/schemas/lesson.schema.json`
  - `01-خام-پروژه/server/www/academy-content/v1/schemas/simulation.schema.json`
  - `01-خام-پروژه/server/www/academy-content/v1/simulations/sim-arp-discovery.json`
  - `01-خام-پروژه/server/www/academy-content/v1/simulations/sim-ospf-neighbor.json`
  - `01-خام-پروژه/server/www/academy-content/v1/simulations/sim-vlan-trunk.json`
  - `01-خام-پروژه/tests/test_academy_v2_api.py`
  - `01-خام-پروژه/tests/test_academy_v2_engine.test.mjs`
  - `01-خام-پروژه/tests/test_academy_v2_ui.test.mjs`
  - `01-خام-پروژه/tools/build_academy_v2_content.py`
  - `01-خام-پروژه/tools/run_academy_v2_tests.py`
  - `01-خام-پروژه/tools/validate_academy_v2.py`
  - `reports/academy-v2-baseline.md`
  - `reports/academy-v2-deployment-fa.md`
  - `reports/academy-v2-presentation.md`
  - `reports/academy-v2-test-logs.txt`
  - `reports/academy-v2-verification.md`

### پیوست: ۱۴۳ مسیر حذفشده حفظشده

<details>
<summary>نمایش فهرست کامل</summary>

```text
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/curriculum-catalog.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/academy-stage-zero-06-client-server-fa.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.a.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.b.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.c.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.d.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.e.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.f.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.g.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.1.h.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.2.a.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.2.b.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.2.c.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-assets/v5/blueprints/ccna-v11-1.2.d.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-01-vlan-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-02-trunk-8021q-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-03-voice-vlan-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-04-intervlan-router-stick-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-05-cdp-lldp-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-06-lacp-etherchannel-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-07-rapid-pvst-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-08-wireless-architecture-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-access-09-management-gui-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-01-automation-impact-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-02-traditional-vs-controller-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-03-sdn-fabric-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-03-sdn-fabric-lab-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-04-control-data-plane-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-05-apis-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-06-ai-ml-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-07-rest-api-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-08-config-management-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-automation-09-json-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-connectivity-01-routing-table-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-connectivity-02-static-routing-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-connectivity-03-ospf-architecture-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-connectivity-04-ospf-dr-cost-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-connectivity-05-ospf-area-lsa-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-connectivity-06-fhrp-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-01-components-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-02-poe-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-03-wireless-controller-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-04-ngfw-ips-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-05-network-architectures-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-06-ethernet-media-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-07-interface-troubleshooting-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-08-tcp-udp-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-09-ipv4-basics-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-10-ipv4-subnet-lab-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-11-ipv6-addressing-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-12-ipv6-interface-lab-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-13-client-ip-parameters-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-14-wireless-rf-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-15-switching-mac-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-fundamentals-16-virtualization-container-vrf-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-practical-delivery-map-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-01-threats-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-02-awareness-physical-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-03-local-passwords-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-04-password-management-mfa-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-05-ipsec-vpn-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-06-acl-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-07-layer2-security-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-08-aaa-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-09-wireless-security-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-security-10-wlan-gui-wpa2-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-01-nat-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-02-ntp-time-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-03-dhcp-dns-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-04-snmp-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-05-syslog-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-06-dhcp-config-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-07-qos-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-07-qos-lab-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-08-ssh-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-services-09-tftp-ftp-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-v11-coverage-audit-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-v11-network-fundamentals-plan-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-v11-remaining-objectives-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-ccna-worksheet-inventory-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-01-computer-server-os-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-02-cpu-memory-storage-nic-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-03-files-users-permissions-processes-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-04-linux-cli-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-05-windows-cli-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-06-client-server-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-07-virtualization-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-08-vm-connectivity-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-09-backup-restore-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/academy-stage-zero-10-troubleshooting-project-fa.md"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/catalog.json"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-01-automation.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-02-controller.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-03-fabric.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-04-planes.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-05-apis.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-06-ai.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-07-rest.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-08-config.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/aut-09-json.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/ic-01-routing-table.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/ic-02-static.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/ic-03-ospf-p2p.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/ic-04-dr-bdr.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/ic-05-lsa-area.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/ic-06-fhrp.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-01-nat.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-02-ntp.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-03-dhcp-dns.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-04-snmp.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-05-syslog.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-06-dhcp-relay.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-07-qos.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-08-ssh.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/is-09-tftp.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-01-vlan.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-02-trunk.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-04-intervlan.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-05-discovery.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-06-lacp.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-07-stp.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-08-wireless.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/na-09-management.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-02-poe.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-03-wireless.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-04-ngfw-ips.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-06-media.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-07-interface.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-08-tcp-handshake.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-10-ipv4-lab.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-12-ipv6-lab.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/nf-15-mac-table.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-01-threats.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-02-physical.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-03-passwords.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-04-mfa.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-05-ipsec.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-06-acl.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-07-layer2.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-08-aaa.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-09-wireless.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/sec-10-wlan-gui.svg"
"01-\330\256\330\247\331\205-\331\276\330\261\331\210\332\230\331\207/server/www/academy-content/images/stage-zero-08-host-only.svg"
```

</details>

## ۸. وضعیت Git

- `git status --porcelain=v1 -uall`: `143` حذف، `4` تغییر tracked، `52` فایل جدید.
- `git diff --shortstat`: `147 files changed, 464 insertions(+), 21823 deletions(-)`.
- تغییرات روی همان شاخه فعال باقیمانده و قابل تفکیک از حذفهای قبلی هستند.
- ریشه `MANIFEST.sha256` تغییر نکرده؛ mismatchهای گزارششده Validator مربوط به ۴ فایل tracked ویرایششده است، نه خرابی مانیفست.
