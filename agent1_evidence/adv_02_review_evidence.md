# شواهد مراجعة عمیق — adv_02 (Advanced Routing: OSPF Multi-Area, LSA Types, Stub/NSSA)

## تاریخ مراجعة
2026-11-23 — ایجنت ۱

## خلاصه استنباط
**بدون ایراد فنی** — محتوایدرس فنی صحیح، کاربردی و کامل است. هیچ تغییر محتوایی لازم نیست.

## فایل‌های مرتبط
- منبع: `academy-data.json` (lesson `adv_02`)
- کپیReview: `agent1_evidence/adv_02_full_review.json`
- بازنویسی: `agent1_rewrites/adv_02.json` (فقط `labType: "Reference"` اضافه شده)

---

## ۱. ادعاها و دستورات مهم

| # | ادعا / دستور | وضعیت | توضیح |
|---|-------------|--------|-------|
| ۱ | همه Areaهای غیرصفر باید مستقیماً به Area 0 وصل باشند (یا Virtual-Link در اضطرار) | ✅ صیح | قانون ضدلوپ OSPF Multi-Area. |
| ۲ | ABR करता خلاصه‌سازی بین‌ناحیه‌ای با `area range` | ✅ صیح | فقط روی ABR، نه روترهای داخلی. |
| ۳ | ASBR مسیرهای بیرونی را با Redistribution وارد OSPF می‌کند | ✅ صیح | Autonomous System Boundary Router. |
| ۴ | LSA Type 1 (Router): هر روتر برای خودش، هرگز خارج از Area نمی‌رود | ✅ صیح | کد `O` در جدول مسیریابی. |
| ۵ | LSA Type 2 (Network): توسط DR روی لینک‌های Broadcast، نه P2P | ✅ صیح | در همان Area باقی می‌ماند. |
| ۶ | LSA Type 3 (Summary): توسط ABR، کد `O IA` در جدول | ✅ صیح | بهترین محل خلاصه‌سازی. |
| ۷ | LSA Type 4 (ASBR Summary): توسط ABR، آدرس ASBR را اعلام می‌کند | ✅ صیح | فقط در ناحیاتی که ASBR داخلشان نیست. |
| ۸ | LSA Type 5 (External): توسط ASBR، در کل OSPF پخش می‌شود | ✅ صیح | E2 پیش‌فرض (فقط Seed Metric). |
| ۹ | LSA Type 7 (NSSA External): فقط در NSSA، ABR تبدیل به Type 5 می‌کند | ✅ صیح | Type 5 در Stub/NSSA ممنوع است. |
| ۱۰ | مسیر `O E1`: Cost داخلی + Seed Metric، بر `E2` اولویت دارد | ✅ صیح | E2 فقط Seed Metric را نگه می‌دارد. |
| ۱۱ | اولویت مسیرها: `O > O IA > E1 > E2` (قبل از مقایسه Metric) | ✅ صیح | مطابق RFC 2328. |
| ۱۲ | Stub Area: مسدود Type 4/5، ABR مسیر پیش‌فرض Type 3 می‌فرستد | ✅ صیح | فقط `O` و `O IA` می‌مانند. |
| ۱۳ | Totally Stubby: zusätzlich مسدود Type 3، فقط `0.0.0.0/0` | ✅ صیح | `no-summary` فقط روی ABR. |
| ۱۴ | NSSA: مسدود Type 4/5، مجاز Type 7 از ASBR محلی | ✅ صیح | ABR Type 7→Type 5 مترجم می‌کند. |
| ۱۵ | Totally NSSA: مسدود Type 3/4/5، مجاز Type 7 | ✅ صیح | `nssa no-summary` روی ABR. |
| ۱۶ | NSSA Translator: ABR با بالاترین Router-ID (RFC 3101) | ✅ صیح | فقط یک ABR ترجمه می‌کند. |
| ۱۷ | NSSA پیش‌فرض مسیر `0.0.0.0/0` نمی‌فرستد (برخلاف Stub) | ✅ صیح | نیاز به `default-information-originate`. |
| ۱۸ | Virtual-Link برای backbone قطع‌شده (Disconnected Backbone) | ✅ صیح | شرایط اضطراری موقت. |
| ۱۹ | Area 0 نمی‌تواند Stub یا NSSA باشد | ✅ صیح | سیسکو اجازه نمی‌دهد. |
| ۲۰ | E-bit در Helloهای OSPF باید در همه روترهای یک Area یکسان باشد | ✅ صیح | شرط همسایگی. |

### دستورات IOS (iosCommands)
| دستور | executable | توضیح |
|-------|-----------|-------|
| `show ip ospf neighbor` | false | sim داخلی خروجی نمونهٔ ثابت می‌دهد |
| `show ip route` | false | sim داخلی خروجی نمونهٔ ثابت می‌دهد |
| `show ip interface brief` | true | زنده در sim داخلی |

## ۲. پاسخ‌های کوییز (۳ سوال)

| # | سوال | پاسخ | توضیح | وضعیت |
|---|------|-------|-------|--------|
| Q0 | خلاصه‌سازی ۴ زیرشبکه Area 1 به Area 0 | [1] فقط روی ABR با `area 1 range` | خلاصه‌سازی درون‌ناحیه‌ای روی ABR است | ✅ صیح |
| Q1 | نوع ناحیه‌ای که Type 3/4/5 مسدود می‌کند + اجازه Type 7 | [2] Totally NSSA | `nssa no-summary` روی ABR | ✅ صیح |
| Q2 | تفاوت O E1 و O E2 | [3] E1 جمع می‌کند Cost داخلی، E2 فقط Seed | E1 بر E2 اولویت دارد | ✅ صیح |

## ۳. راه‌حل تمرین‌ها (۳ تمرین)

| # | سطح | المهمة | راه‌حل | وضعیت |
|---|------|--------|--------|--------|
| Ex0 | ساده | معادل LSA برای کدهای O, O IA, O E2, O N1 | Type 1/2 → O; Type 3 → O IA; Type 5 → O E2; Type 7 → O N1 | ✅ صیح |
| Ex1 | متوسط | دستورات Totally Stubby Area 10 + خلاصه‌سازی | ABR: `area 10 stub no-summary`, `area 10 range`; Branch: `area 10 stub` | ✅ صیح |
| Ex2 | چالشی | NSSA Translator انتخاب +default-information |ABR-B (2.2.2.2)Tr레이تر؛ `default-information-originate` برای پیش‌فرض | ✅ صیح |

## ۴. آزمایشگاه (Lab)

| ویژگی | وضعیت | توضیح |
|-------|--------|-------|
| نوع آزمایشگاه | Reference | صادقانه: sim داخلی `router ospf`، `area stub/nssa`، `show ip ospf database` را اجرا نمی‌کند |
| مراحل | ۴ مرحله | مناسب |
| verifyCmds | ۴ دستور | enable, show ip interface brief, show ip ospf neighbor, show running-config |

## ۵. Depanarishing (Troubleshooting)

| فیلد | محتوا | وضعیت |
|-------|--------|--------|
| Fault | Area 1 متصل به Area 2 (نه Area 0)، مسیرهای O IA دریافت نمی‌شوند | سناریوی realistic |
| Analysis | Disconnected Backbone — ABR نمی‌تواند Type 3 بدون حضور در Area 0 عبور دهد | ✅ فنی صحیح |
| Fix | Virtual-link یا تغییر توپولوژی برای اتصال مستقیم به Area 0 | ✅ صحیح |

## ۶. اشتباهات متداول

| # | myth | reality | وضعیت |
|---|------|---------|--------|
| 0 | `no-summary` روی همه روترهای Area برای Totally Stubby | فقط روی ABR، روترهای داخلی فقط `area stub` | ✅ صحیح |
| 1 | `O E1` با Metric پایین‌تر بر `O IA` برتری دارد | `O IA` همیشه بر `O E1` برتری دارد (پیش از Metric) | ✅ صحیح |

## ۷. سایر مؤلفه‌ها
- Analogy: ✅ vorhanden (شرکت هلدینگ با ستاد مرکزی Area 0)
- Summary: ✅ vorhanden (LSDB کاهش می‌دهد، SPF محدود می‌شود)
- CiscoRef: ✅ "Cisco CCNP ENCOR 350-401 Official Cert Guide — Ch 7–8 / RFC 2328 & 3101"
- ProtocolAnalysis: ✅ E1 vs E2، Stub Area Flag در Hello
- Bridge: ✅ nextId: adv_eigrp

## ۸. ایرادات یافت شده
**هیچ ایرادی یافت نشد.**

## ۹. تغییرات اعمال شده
**هیچ تغییر محتوایی لازم نیست.**

---
**نتیجه Review adv_02:** ⟨کامل و فنی صحیح، بدون اصلاح⟩