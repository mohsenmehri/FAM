# شواهد مراجعة عمیق — ccnp_enauto (تخصصی 300-435 ENAUTO: مدل‌های YANG، NETCONF/RESTCONF و API پلتفرم‌های سیسکو)

## تاریخ مراجعة
2026-11-23 — ایجنت ۱ (بررسی محتوایی واقعی، نه چک‌لیست ساختاری)

## خلاصه استنباط
**بدون ایراد فنی یافت شده** — محتوایدرس فنی صحیح، کاربردی و کامل است.

## فایل‌های مرتبط
- منبع: `academy-data.json` (lesson `ccnp_enauto`)
- کپیReview: `agent1_evidence/ccnp_enauto_full_review.json`
- بازنویسی: `agent1_rewrites/ccnp_enauto.json`

---

## ۱. بررسی عمیق پاسخ‌های کوییز

### Q0: در کار با **RESTCONF** برای تغییر فقط `description` یک اینترفیس بدون پاک کردن آدرس IP موجود (در برابر `PUT` ناقص)، کدام توضیح دقیق‌تر است؟
- **پاسخ انتخاب [0]:** استفاده از `PATCH` (با بررسی schema و نتیجهٔ واقعی؛ زیرا طبق RFC 5789 متد `PATCH` ذاتاً Idempotent نیست) یا ارسال کل بدنهٔ کامل در `PUT`
- **توضیح:** `PUT` کل منبع را جایگزین می‌کند؛ `PATCH` تغییر جزئی می‌دهد ولی طبق RFC 5789 به نوع عملیات و schema وابسته است و پس از اجرا باید وضعیت واقعی را راستی‌آزمایی کرد.
- **وضعیت:** ✅ فنی صحیح

### Q1: هنگام ارسال درخواست تغییرات به یک endpoint ناهمگام در **Cisco Catalyst Center REST API** که پاسخ **`202 Accepted`** برمی‌گرداند، گام الزامی بعدی چیست؟
- **پاسخ انتخاب [1]:** استخراج `taskId` و فراخوانی دوره‌ای (Polling) `/dna/intent/api/v1/task/{taskId}` تا رسیدن به `endTime`
- **توضیح:** عملیات تغییردهنده در Catalyst Center ناهمگام (Asynchronous) هستند و نتیجهٔ واقعی فقط از طریق Polling روی `taskId` مشخص می‌شود.
- **وضعیت:** ✅ فنی صحیح

### Q2: اگر اسکریپت شما هنگام فراخوانی **Meraki Dashboard API** با کد خطای **`HTTP 429`** روبه‌رو شود، علت چیست و پاسخ استاندارد کد باید چه باشد؟
- **پاسخ انتخاب [2]:** عبور از سقف نرخ مجاز درخواست در ثانیه؛ خواندن هدر `Retry-After` و مکث به همان میزان پیش از ارسال مجدد
- **توضیح:** کد `429 Too Many Requests` نشانهٔ Rate Limiting است و هدر `Retry-After` زمان دقیق انتظار پیش از تلاش بعدی را اعلام می‌کند.
- **وضعیت:** ✅ فنی صحیح

## ۲. بررسی عمیق راه‌حل تمرین‌ها

### Ex0 (ساده)
- **مهمته:** در مدل‌های YANG، اگر بخواهیم یک اسکریپت واحد بتواند وضعیت اینترفیس و BGP را هم از روتر Cisco IOS-XE و هم از سوئیچ Arista بخواند، از کدام خانواده YANG استفاده می‌کنیم (`IETF`, `OpenConfig`, `Cisco Native`)؟ و اگر بخواهیم تنظیمات خاص `EIGRP` سیسکو را عوض کنیم چطور؟
- **راه‌حل:** برای خواندن مشترک روی چند برند: **`OpenConfig`** (یا `IETF` برای بخش‌های پایه)؛ برای تنظیمات خاص و اختصاصی سیسکو مثل EIGRP: **`Cisco Native`** (`Cisco-IOS-XE-native`).
- **وضعیت:** ✅ موجود و فنی صحیح

### Ex1 (متوسط)
- **مهمته:** قطعه کد پایتون با کتابخانهٔ `ncclient` را بنویسید که به پورت `830` روتر `192.0.2.10` وصل شود و تنها بخش `interfaces` را با یک `<filter type="subtree">` از `running` بخواند و در خروجی چاپ کند.
- **راه‌حل:** `from ncclient import manager`
`filt = """<filter><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/></filter>"""`
`with manager.connect(host="192.0.2.10", port=830, username="netops", password="Pass123", hostkey_verify=False) as m:`
`    res = m.get_config(source="running", filter=filt)`
`    print(res.xml)`
- **وضعیت:** ✅ موجود و فنی صحیح

### Ex2 (چالشی)
- **مهمته:** توابع کامل پایتون بخش `exercise` بالا را بنویسید: تابع ۱) `meraki_get(url, api_key)` با مدیریت هوشمند `429 Retry-After`؛ تابع ۲) `wait_dnac_task(base_url, token, task_id)` با Polling ایمن و سقف `max_tries`.
- **راه‌حل:** `import time, requests`
`def meraki_get(url, api_key):`
`    headers = {"X-Cisco-Meraki-API-Key": api_key}`
`    for _ in range(5):`
`        r = requests.get(url, headers=headers, timeout=10)`
`        if r.status_code == 429:`
`            time.sleep(int(r.headers.get("Retry-After", 2)))`
`            continue`
`        r.raise_for_status()`
`        return r.json()`
`    raise RuntimeError("Rate limit persisted")`

`def wait_dnac_task(base_url, token, task_id, max_tries=15):`
`    headers = {"X-Auth-Token": token}`
`    for _ in range(max_tries):`
`        r = requests.get(f"{base_url}/dna/intent/api/v1/task/{task_id}", headers=headers, timeout=10)`
`        r.raise_for_status()`
`        t = r.json()["response"]`
`        if "endTime" in t:`
`            if t.get("isError"): raise RuntimeError(t.get("failureReason"))`
`            return t`
`        time.sleep(2)`
`    raise TimeoutError("Task polling timed out")`
- **وضعیت:** ✅ موجود و فنی صحیح

## ۳. بررسی عمیق آزمایشگاه
- **عنوان:** آزمایشگاه شبیه‌سازی تفاوت `PUT` (جایگزینی کامل) در برابر `PATCH` (اصلاح جزئی) در وضعیت پورت‌ها
- **تعداد مراحل:** 5
- **دستورات تایید:** 4
- **نوع آزمایشگاه:** Reference (اجرای_real_ تأیید نشده)

  مرحله 1: ۱. مرز شبیه‌ساز: شبیه‌ساز سبک داخلی سرویس‌دهندهٔ واقعی NETCONF/RESTCONF یا کنترلرهای Catalyst Center/Meraki را ندارد (برای کدنویسی زنده از Cisco DevNet Sandbox استفاده کنید). اما اینجا اثر منطقی عملیا...
  مرحله 2: ۲. با `enable` وارد شوید و با `show interfaces trunk` و `show running-config` ببینید روی ترانک `Gi0/1` VLANهای `1,10,20` مجاز هستند....
  مرحله 3: ۳. شبیه‌سازی **`PATCH`** (افزودن جزئی بدون حذف قبلی‌ها): روی `Gi0/1` دستور `configure terminal` -> `interface Gi0/1` -> `switchport trunk allowed vlan add 75` -> `end` و سپس `show interfaces trunk` را...
  مرحله 4: ۴. با `show interfaces trunk` و `show running-config` بررسی کنید در شبیه‌ساز ساده تفاوت جایگزینی لیست ترانک (شبیه خطرِ `PUT` ناقص) با افزودن افزایشی (`add`) روی `Gi0/1` قابل مشاهده است (پروتکل‌های واق...
  مرحله 5: ۵. **سناریوی مرجع غیرشبیه‌سازی‌شده (Catalyst Center Async `202` Polling و RESTCONF `PATCH` — RFC 8040/8072):** **نمونهٔ کد پایتون:** `r = requests.post(url, headers={'X-Auth-Token': tok}, json=payload...

## ۴. عیب‌یابی
- **خطا:** اسکریپت پایتونی با متد **`PUT`** به RESTCONF برای تغییر فقط `description` روی اینترفیس `Gi0/0` ارسال شده؛ درخواست با کد `204 No Content` موفق می‌شود، اما لحظه‌ای بعد ارتباط مدیریتی با روتر روی `Gi0/0`...
- **تحلیل:** در RESTCONF، متد **`PUT`** به معنی **جایگزینی کامل منبع (Full Replacement)** است؛ یعنی اگر شما در بدنهٔ JSON تنها `"name": "Gi0/0"` و `"description": "NEW"` را فرستاده و آدرس IP اینترفیس را داخل JSON ...
- **اصلاح:** در این سناریو برای ویرایش صرفاً `description` بدون بازنویسی IP، استفاده از **`PATCH` (plain RESTCONF merge با بررسی schema و خواندن نتیجه پس از تغییر)** مناسب‌تر از `PUT` ناقص است؛ اگر از `PUT` استفاد...

## ۵. اشتباهات متداول

### myth 0: در Catalyst Center API اگر درخواست `POST` ما کد موفقیت `202 Accepted` برگرداند، یعنی عملیات تغییر روی تمام سوئیچ‌ها با موفقیت کامل پایان یافته است....
- **واقعیت:** `202 Accepted` صرفاً یعنی درخواست وارد صف اجرا شده و یک `taskId` گرفته است؛ شکست واقعی (مثل قطع بودن سوئیچ یا خطای CLI) تنها پس از Polling آدرس `/task/{taskId}` در فیلد `isError: true` معلوم می‌شود....
- **تشخیص:** همیشه در پاسخ `POST` به دنبال فیلد `response.taskId` بگردید و وضعیتش را تا اتمام (`endTime` و `isError`) پایش کنید....

### myth 1: در پایتون و کار با RESTCONF، فرقی بین `PUT` و `PATCH` وجود ندارد و `PATCH` همیشه به خودی خود Idempotent و امن است....
- **واقعیت:** `PUT` منبع هدف را جایگزین کامل می‌کند و فیلدهای نیامده را پاک می‌سازد؛ `PATCH` تغییر جزئی می‌فرستد، ولی طبق **RFC 5789** ذاتاً Idempotent نیست (مثلاً در YANG Patch عملیات `create`/`insert` می‌توانند د...
- **تشخیص:** بررسی دقیق نوع Patch (Plain RESTCONF `merge` vs YANG Patch RFC 8072) و اجرای `GET` راستی‌آزمایی پس از تغییر....

## ۶. سایر مؤلفه‌ها
- **導師 (lead):** 490 کاراکتر
- **هدف (goal):** 291 کاراکتر
- **پیش‌نیاز (prereq):** 78 کاراکتر
- **تشبیه (analogy):** 725 کاراکتر
- **جمع‌بندی (summary):** 513 کاراکتر
- **ارجاع سیسکو:** Cisco Automating and Programming Cisco Enterprise Solutions (300-435 ENAUTO) Official Cert Guide — Ch 2–8 (YANG, NETCONF/RESTCONF, Catalyst Center, SD-WAN & Meraki APIs)
- **تحلیل پروتکل:** 2 مورد
- **دستورات IOS:** 2 مورد
- **پل به درس بعدی:** ccnp_encc

---

## ۷.}Eیرات یافت شده
**هیچ ایرادی یافت نشد.**

## ۸. تغییرات اعمال شده
**هیچ تغییر محتوایی لازم نیست.**

**نتیجه Review:** ⟨کامل و فنی صحیح، بدون اصلاح⟩