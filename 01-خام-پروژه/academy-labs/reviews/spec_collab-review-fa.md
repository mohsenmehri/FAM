# شواهد بازبینی معنایی `spec_collab` — تخصص Collaboration & VoIP (SIP، RTP، CUCM و Dial Plan)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت) انجام شده؛ **بازبینی مستقل انسانی انجام نشده است.**

## یافته‌های ممیزی نسخه قدیمی (`5a747490`) و اصلاحات
- نسخه قدیمی ۳ بخش و ۳ پرسش داشت؛ محاسبات عددی G.711 (87.2 / 88.8 kbps) و G.729 (31.2 / 32.8 kbps) در نسخه قدیمی دقیق بود و در نسخه جدید با افزودن L3، Wire Rate (+20 B Preamble/SFD/IFG) و اثر SRTP/IPsec کامل‌تر و با کد Python راستی‌آزمایی شد.
- منطق دقیق ترکیب `Line CSS` قبل از `Device CSS`، قاعده Longest Match، ریسک Partition `<None>` و بقای شعبه با SRST اضافه شدند.

## راستی‌آزمایی آزمایشگاه
- فایل `01-خام-پروژه/academy-labs/agent3/spec_collab_lab.py` یک **Python Mock محلی** برای محاسبه پهنای باند VoIP و شبیه‌سازی Dial Plan است که اجرا و آزمون شده است. هیچ خوشه CUCM یا تلفن واقعی اجرا نشده است.

## بازبینی فنی فاز ۸A (2026-11-27)
- **ایراد:** نبود `_require_bool` روی `dot1q` و `include_wire_preamble_ifg` (`dot1q='False'` تگ ۴ بایتی اضافه می‌کرد)، `ZeroDivisionError` در `packetization_ms=0` و پذیرش سربار منفی.
- **منبع معتبر:** ITU-T G.711/G.729، RFC 3550 (RTP) و Cisco CUCM Partition/CSS Evaluation Order.
- **اصلاح انجام‌شده:** اعمال `_require_bool`، `packetization_ms > 0`، سربار غیرمنفی و بررسی `dialed_number` غیرخالی + assertها.
- **تست مرتبط:** `test_phase8a_ccde18_dynamic_vrf_and_specialist_core_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون CUCM/CUBE/تلفن واقعی؛ بازبینی نویسنده (نه مستقل).
