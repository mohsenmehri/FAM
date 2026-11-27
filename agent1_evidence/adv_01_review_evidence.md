# شواهد مراجعة عمیق — adv_01 (Advanced Switching: MST, STP Guards, UDLD, StackWise)

## تاریخ مراجعة
2026-11-23 — ایجنت ۱ (scope: ccna_* sauf ccna_01/02، adv_*、ccnp_*)

## خلاصه استنباط
**بدون ایراد فنی** — محتوایدرس فنی صحیح، کاربردی و کامل است. هیچ تغییر محتوایی لازم نیست.

## فایل‌های مرتبط
- منبع: `01-خام-پروژه/server/www/academy-assets/academy-data.json` (lesson `adv_01`)
- کپیReview: `agent1_evidence/adv_01_full_review.json`
- بازنویسی: `agent1_rewrites/adv_01.json` (فقط فیلد `labType: "Reference"` اضافه شده)

---

## ۱. ادعاها و دستورات مهم (دقت فنی)

| # | ادعا / دستور | وضعیت | توضیح |
|---|-------------|--------|-----------|
| ۱ | MST Region 멤버 شرایط: Region Name + Revision Number + VLAN-to-Instance mapping باید عیناً یکسان باشند | ✅ صیح | مطابق IEEE 802.1s. تغییر یک VLAN در نگاشت Digest را عوض می‌کند. |
| ۲ | Configuration Digest (MD5 ۱۶ بایتی) از جدول نگاشت در BPDU مقایسه می‌شود | ✅ صیح | این مستقیماً مستندات سیسکو و استاندارد 802.1s است. |
| ۳ | BPDU Guard روی پورت PortFast کاربر: دریافت BPDU → err-disabled | ✅ صیح | رفتار استاندارد سیسکو. |
| ۴ | Root Guard روی پورت‌های Designated رو به دسترسی: دریافت BPDU برتر → root-inconsistent (موقت) | ✅ صیح | به محض قطع BPDU مهاجم، خودکار بازمی‌گردد. |
| ۵ | Loop Guard روی پورت‌های Root/Alternate: ناپدید شدن BPDU → loop-inconsistent | ✅ صیح | Prevents loops after unidirectional link failure or CPU exhaustion. |
| ۶ | `bpdufilter enable` در سطح اینترفیس: BPDUهای ورودی و خروجی نادیده گرفته می‌شوند (STP غیرفعال روی آن پورت) | ✅ صیح | خطرناک‌تر از BPDU Guard، می‌تواند حلقه لایه ۲ ایجاد کند. |
| ۷ | UDLD Aggressive: پس از ۸ تلاش ناموفق Echo → err-disabled | ✅ صیح | UDLD Normal فقط لاگ می‌دهد. |
| ۸ | Root Guard و Loop Guard نمی‌توانند هم‌زمان روی یک پورت فعال باشند | ✅ صیح | فعال کردن یکی، دیگری را غیرفعال می‌کند. |
| ۹ | StackWise Split-Brain (Dual-Active): دو تکه پشته فکر می‌کنند خودشان Master هستند | ✅ صیح | نیاز به Dual-Active Detection (Enhanced PAgP یا BFD). |
| ۱۰ | MST Instance 0 (IST) همیشه وجود دارد و با Regionها ارتباط برقرار می‌کند | ✅ صیح | مطابق استاندارد. |

### دستورات IOS (iosCommands)
| دستور | executable | توضیح |
|-------|-----------|-------|
| `show spanning-tree` | false | خروجی نمونهٔ مرجع، sim داخلی MST را پشتیبانی نمی‌کند |
| `show interfaces trunk` | true | زنده در sim داخلی |
| `show interfaces Gi0/3 switchport` | true | زنده در sim داخلی |

## ۲. پاسخ‌های کوییز (۳ سوال)

| # | سوال | پاسخ انتخاب شده | توضیح | وضعیت |
|---|------|-----------------|-------|--------|
| Q0 | سه پارامتر MST Region | [0] Region Name + Revision + VLAN mapping | تغییر یک VLAN Digest را عوض می‌کند | ✅ صیح |
| Q1 | bpdufilter بجای BPDU Guard روی پورت کاربر | [1] سTP غیرفعال → حلقه لایه ۲ | فعال کردن bpdufilter در سطح اینترفیس STP را خاموش می‌کند | ✅ صیح |
| Q2 | ابزار پیشگیری از لینک فیبر یک‌طرفه | [2] UDLD Aggressive | پیام Echo لایه ۲، ۸ تلاش ناموفق → err-disabled | ✅ صیح |

## ۳. راه‌حل تمرین‌ها (۳ تمرین)

| # | سطح | المهمة | راه‌حل | وضعیت |
|---|------|--------|--------|--------|
| Ex0 | ساده | انتخاب محافظ STP برای ۳ سناریو پورت | ۱) BPDU Guard، ۲) Loop Guard + UDLD Aggressive، ۳) Root Guard | ✅ صیح و کامل |
| Ex1 | متوسط | دستورات کامل MST Region CAMPUS revision 1 | spanning-tree mode mst → configuration → name → revision → instance → root primary/secondary | ✅ صیح و کامل |
| Ex2 | چالشی | Root Guard + سوئیچ جدید priority 0 | root-inconsistent موقت، خودکار بازمی‌گردد، shut/no shut لازم نیست | ✅ صیح و کامل |

## ۴. آزمایشگاه (Lab)

| ویژگی | وضعیت | توضیح |
|-------|--------|-----------|
| تعداد مراحل | ۴ مرحله | مناسب |
| صدق simulate | **Reference** | صادقانه می‌گوید sim داخلی MST/Guard/UDLD را اجرا نمی‌کند، نیازمند CML/EVE-NG یا Catalyst واقعی |
| دستورات مرحله ۲-۴ | show interfaces trunk/status/switchport, show running-config | 모두 executable در sim داخلی |
| verifyCmds | ۴ دستور | enable, show interfaces trunk, show interfaces Gi0/3 switchport, show running-config |
| نوع آزمایشگاه | Reference | ✅ مناسب — اجرا_real_ تأیید نشده، نه Mock |

## ۵. Depanarishing (Troubleshooting)

| فیلد | محتوا | وضعیت |
|-------|--------|--------|
| Fault | Migration PVST+ → MST، Boundary状، Instance 2 توزیع نمی‌شود | واقع‌판센ار |
| Analysis | Region mismatch → Hash متفاوت → همه به IST سقوط می‌کنند | ✅ فنی صحیح |
| Fix | `show spanning-tree mst configuration` روی هر دو، تطابق Name/Revision/instance lines | ✅ صحیح |

## ۶. اشتباهات متداول (Misconceptions)

| # | myth | reality | howToSpot | وضعیت |
|---|------|---------|-----------|--------|
| 0 | Region Name + Revision یکسان = نگاشت VLAN خودکار همگام | MST نگاشت را منتشر نمی‌کند (مگر VTPv3)، باید دستی یکسان بنویسید | show spanning-tree mst configuration Digest | ✅ صحیح |
| 1 | bpdufilter امنیت بیشتر از bpduguard | برعکس! bpdufilter در سطح اینترفیس STP را غیرفعال می‌کند | show running-config دنبال bpduguard نباشد bpdufilter | ✅ صحیح |

## ۷. سایر مؤلفه‌ها

| مؤلفه | وضعیت | شرح |
|-----------|--------|------|
| Analogy (تشبیه) | ✅ vorhanden | PVST+ vs MST = ۴۰۰ راهنمای جداگانه vs ۲ اتوبوس؛ StackWise = چسباندن کمد کشویی |
| Summary (جمع‌بندی) | ✅ vorhanden | MST کاهش CPU/BPDU، Guardها، UDLD Aggressive، StackWise |
| CiscoRef | ✅ vorhanden | "Cisco CCNP/CCIE Enterprise Design & IEEE 802.1s (MST), Cisco Catalyst STP Toolkit" |
| ProtocolAnalysis | ✅ vorhanden (۲ مورد) | Configuration Digest MD5، StackWise Active election |
| Bridge | ✅ vorhanden | nextId: adv_pvl |

## ۸.}Eیرات یافت شده
**هیچ ایرادی یافت نشد.**

## ۹. تغییرات اعمال شده
**هیچ تغییر محتوایی لازم نیست.**
فایل `agent1_rewrites/adv_01.json` فقط شامل اضافه کردن `labType: "Reference"` به laboratoire است (بدون تغییر محتوای الدرس).

## ۱۰. منبع تأیید
دستورات و مفاهیم مطابق مستندات سیسکو CCNP/CCIE Enterprise و استاندارد IEEE 802.1s.

---
**نتیجه Review adv_01:** ⟨کامل و فنی صحیح، بدون اصلاح⟩