# شواهد مراجعة عمیق — ccnp_enc_auto (ENCOR حوزه ۶: اتوماسیون در CCNP (JSON، YANG، NETCONF/RESTCONF، EEM و Python/Ansible))

## تاریخ مراجعة
2026-11-23 — ایجنت ۱

## خلاصه استنباط
**بدون ایراد فنی** — محتوایدرس فنی صحیح، کاربردی و کامل است. هیچ تغییر محتوایی لازم نیست.

## فایل‌های مرتبط
- منبع: `academy-data.json` (lesson `ccnp_enc_auto`)
- کپیReview: `agent1_evidence/ccnp_enc_auto_full_review.json`
- بازنویسی: `agent1_rewrites/ccnp_enc_auto.json` (فقط `labType: "Reference"` اضافه شده)

---

## ۱. بررسی عمیق پاسخ‌های کوییز

### Q0: پروتکل **NETCONF** به‌صورت استاندارد از کدام لایهٔ انتقال، پورت و فرمت داده استفاده می‌کند؟

- **پاسخ انتخاب [0]:** SSH پورت TCP 830 با فرمت XML
- **توضیح:** پورت استاندارد NETCONF برابر `TCP 830` روی بستر امن SSH است و پیام‌هایش در ساختار XML بر پایهٔ مدل YANG ردوبدل می‌شوند.
- **وضعیت:** ✅ فنی صحیح

### Q1: مزیت اصلی **Ansible** در مقایسه با **Puppet** و **Chef** در اتوماسیون سوئیچ‌ها و روترهای سیسکو چیست؟

- **پاسخ انتخاب [1]:** Ansible هیچ Agentای روی روتر/سوئیچ نصب نمی‌کند (Agentless) و مستقیم از طریق SSH/NETCONF/HTTP کار می‌کند
- **توضیح:** از آنجا که بسیاری از تجهیزات شبکهٔ قدیمی یا بسته اجازهٔ نصب Agent ندارند، مدل Agentless و Push در Ansible محبوب‌ترین گزینه در شبکه است.
- **وضعیت:** ✅ فنی صحیح

### Q2: اگر در یک اسکریپت EEM در ماشهٔ `syslog` الگوی بسیار کلی مثل `"%LINK"` بگذاریم و در `action` وضعیت پورت را تغییر دهیم، چه خطری پیش می‌آید؟

- **پاسخ انتخاب [2]:** خطر حلقهٔ مکرر اجرای EEM (در صورت تولید مکرر پیام تغییر وضعیت / Flap) و مصرف شدید CPU روتر
- **توضیح:** در صورتی که تغییر پورت یا Flap باعث تولید مکرر پیام منطبق با `%LINK` شود، EEM پی‌درپی تحریک شده و می‌تواند CPU روتر را تحت فشار شدید یا قفل بگذارد.
- **وضعیت:** ✅ فنی صحیح

## ۲. بررسی عمیق راه‌حل تمرین‌ها

### Ex0 (ساده)
- **مهمته:** در پاسخ JSON زیر از RESTCONF، مقدار عددی `mtu` اولین اینترفیس را با یک عبارت تک‌خطی پایتون از دیکشنری `res` استخراج کنید:
`res = {"ietf-interfaces:interfaces": {"interface": [{"name": "Gi0/0", "mtu": 1500}]}}`
- **راه‌حل:** `res["ietf-interfaces:interfaces"]["interface"][0]["mtu"]` (که مقدار `1500` را برمی‌گرداند).
- **وضعیت:** ✅ موجود و فنی صحیح

### Ex1 (متوسط)
- **مهمته:** کد تمیز پایتون با کتابخانهٔ `requests` بنویسید که با احراز هویت Basic و هدرهای استاندارد **RESTCONF**، وضعیت اینترفیس‌های روتر `192.0.2.10` را در فرمت JSON بخواند و در صورت موفقیت (`status_code == 200`) نام تک‌تک آن‌ها را چاپ کند.
- **راه‌حل:** `import requests`
`url = "https://192.0.2.10/restconf/data/ietf-interfaces:interfaces"`
`headers = {"Accept": "application/yang-data+json"}`
`resp = requests.get(url, auth=("admin", "Pass123"), headers=headers, verify="/etc/ssl/corp-ca.pem", timeout=10)`
`if resp.status_code == 200:`
`    for iface in resp.json()["ietf-interfaces:interfaces"]["interface"]:`
`        print(iface["name"])`
- **وضعیت:** ✅ موجود و فنی صحیح

### Ex2 (چالشی)
- **مهمته:** نمونهٔ **آزمایشگاهی** EEM Applet در بخش `exercise` بالا را بنویسید (ثبت هشدار و بررسی شرط) و **دو دلیل عملی** ذکر کنید که چرا در شبکهٔ تولیدی باز کردن خودکار یک پورت `administratively down` با `no shutdown` خطرناک است و نقش دقیق `maxrun` در EEM چیست.
- **راه‌حل:** `event manager session cli username automation`
`event manager applet LAB_WATCH_INT`
` event syslog pattern "Interface GigabitEthernet0/0, changed state to administratively down" maxrun 30`
` action 1.0 syslog priority alerts msg "EEM-ALERT: Gi0/0 was administratively shut down; manual NOC approval required before no shut!"`
` action 2.0 cli command "enable"`
` action 3.0 cli command "show interfaces Gi0/0 | append bootflash:eem_audit.txt"`

**چرا `no shutdown` خودکار در تولید خطرناک است:** ۱) ممکن است تیم امنیت یا NOC عمداً پورت را برای مهار یک حمله، حلقه یا عملیات نگهداری کابل `shutdown` کرده باشد و EEM کار آن‌ها را خنثی کند؛ ۲) با تریگر اشتباه می‌تواند حلقهٔ اجرا بسازد. در آزمایشگاه هم اگر دستوری اجرایی بنویسید باید محدوده، شرط تایید و مکانیسم توقف اضطراری (`no event manager applet ...`) لحاظ شود. نکته: **`maxrun 30`** فقط حداکثر مدت اجرای یک نوبت Applet (۳۰ ثانیه) را تعیین می‌کند و جلوی تکرار تریگر یا اجرای هم‌زمان را نمی‌گیرد.
- **وضعیت:** ✅ موجود و فنی صحیح

## ۳. بررسی عمیق آزمایشگاه
- **عنوان:** آزمایشگاه تطابق تنظیمات پورت با الگوی JSON/Playbook و بررسی Idempotency
- **تعداد مراحل:** 5
- **دستورات تایید:** 4
- **نوع آزمایشگاه:** Reference (اجرای_real_ تأیید نشده)
- **محدودیت پلتفرم:** sim داخلی دستورات پیشرفته را اجرا نمی‌کند

  مرحله 1: ۱. مرز شبیه‌ساز: شبیه‌ساز سبک داخلی سرویس‌های واقعی `netconf-yang`، `restconf` و `EEM` ندارد (برای تست با Python `requests`/`ncclient` از Cisco DevNet Sandbox یا CML استفاده کنید). اما اینجا رفتار واق...
  مرحله 2: ۲. با `enable` و `show interfaces status` و `show vlan brief` وضعیت اولیه (`Current State`) را بررسی کنید....
  مرحله 3: ۳. فرض کنید یک اسکریپت اتوماسیون باید `VLAN 65 (AUTO_ENFORCE)` را بسازد و پورت `Gi0/7` را با `description ENCOR-NETCONF-PORT` به آن متصل کند: `configure terminal` -> `vlan 65` -> `name AUTO_ENFORCE` -...
  مرحله 4: ۴. با `show running-config` خروجی اولیه را ثبت کنید (Post-Check). سپس برای **تست Idempotency** در شبیه‌ساز، عیناً مرحلهٔ ۳ را برای بار دوم تکرار کنید و بررسی نمایید خروجی `show running-config` تغییری ...
  مرحله 5: ۵. **سناریوی مرجع غیرشبیه‌سازی‌شده (RESTCONF RFC 8040 و EEM — پلتفرم مرجع: Cisco IOS-XE 17.x):** **فرمان‌ها و درخواست نمونه:** فعال‌سازی روی روتر (`ip http secure-server`, `restconf`) و درخواست پایتون...

## ۴. عیب‌یابی
- **خطا:** اسکریپت پایتون با کتابخانهٔ `requests` درخواست `GET` به روتر `IOS-XE` از طریق `RESTCONF` می‌فرستد تا اطلاعات اینترفیس `Gi0/0` را بگیرد؛ آدرس `https://192.0.2.10/restconf/data/ietf-interfaces:interface...
- **تحلیل:** ۱) خطای **`406 Not Acceptable`** مطابق **RFC 8040** زمانی رخ می‌دهد که کلاینت در هدر `Accept` قالب(هایی) را درخواست کرده باشد که سرور در آن endpoint پشتیبانی نمی‌کند (مثلاً ارسال `Accept: text/plain` ...
- **اصلاح:** روی روتر `ip http secure-server` و `restconf` را فعال کنید و در کد پایتون هدرهای `Accept` و `Content-Type` را دقیقاً به قالب پشتیبانی‌شده یعنی **`application/yang-data+json`** (یا `application/yang-da...

## ۵. اشتباهات متداول

### myth 0: YANG یک پروتکل شبکهٔ جایگزین برای SNMP و SSH است که روی پورت خاصی ارسال می‌شود....
- **واقعیت:** **YANG یک زبان مدل‌سازی داده (Data Modeling Language)** است که فقط ساختار داده‌ها را تعریف می‌کند؛ پروتکل‌هایی که این داده را حمل می‌کنند **NETCONF** (`SSH 830`) و **RESTCONF** (`HTTPS 443`) هستند....
- **تشخیص:** برای YANG هیچ پورت TCP/UDP وجود ندارد؛ پورت `830` متعلق به NETCONF و `443` متعلق به RESTCONF است....

### myth 1: در کتابخانهٔ `requests` پایتون برای راحتی کار در شبکهٔ عملیاتی همیشه باید `verify=False` گذاشت....
- **واقعیت:** گذاشتن `verify=False` بررسی گواهی TLS سرور را غیرفعال می‌کند و راه را برای حملهٔ **Man-in-the-Middle** باز می‌گذارد؛ در آزمایشگاه موقتاً کاربرد دارد اما در محیط تولیدی باید مسیر CA سازمان را به `verif...
- **تشخیص:** بررسی کدهای CI/CD و جستجوی عبارت `verify=False` در مخازن عملیاتی....

## ۶. سایر مؤلفه‌ها
- **導師 (lead):** 455 کاراکتر
- **هدف (goal):** 278 کاراکتر
- **پیش‌نیاز (prereq):** 77 کاراکتر
- **تشبیه (analogy):** 723 کاراکتر
- **جمع‌بندی (summary):** 371 کاراکتر
- **ارجاع سیسکو:** Cisco CCNP ENCOR 350-401 Official Cert Guide — Ch 25–28 (Network Programmability, YANG/NETCONF/RESTCONF, EEM, Ansible/Puppet/Chef)
- **تحلیل پروتکل:** 2 مورد
- **دستورات IOS:** 2 مورد
- **پل به درس بعدی:** ccnp_02

---

## ۷.}Eیرات یافت شده
**هیچ ایرادی یافت نشد.**

## ۸. تغییرات اعمال شده
**هیچ تغییر محتوایی لازم نیست.**

**نتیجه Review:** ⟨کامل و فنی صحیح، بدون اصلاح⟩