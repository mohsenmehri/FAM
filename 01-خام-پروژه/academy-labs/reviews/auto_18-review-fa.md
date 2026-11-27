# شواهد بازبینی معنایی `auto_18` — تست خودکار شبکه (pyATS / Genie / Batfish)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- اشکالات نگارشی نسخه قدیمی اصلاح و مباحث pyATS، Genie، AEtest، Dq و Batfish در ۱۴ بخش و ۱۲ پرسش تدوین شدند.
- فایل `01-خام-پروژه/academy-labs/agent3/auto_18_lab.py` به‌صورت Local Mock در Python 3 اجرا و تست شد؛ هیچ سرویس واقعی Batfish یا روتر زنده متصل نشده است.

## بازبینی فنی فاز ۸C-2 (2026-11-27)
- **ایراد:** نبود اعتبارسنجی نوع ورودی در `dq_filter_down_bgp_peers` و `batfish_style_trace` (کرش `AttributeError` روی ورودی نامعتبر).
- **منبع معتبر:** Cisco pyATS/Genie Dq و Batfish Static Control-Plane Verification.
- **اصلاح انجام‌شده:** افزودن بررسی نوع `dict`/`str` با `ValueError` صریح.
- **تست مرتبط:** `test_phase8c2_remaining_automation_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی بدون pyATS/Batfish؛ بازبینی نویسنده (نه مستقل).
