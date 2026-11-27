# شواهد بازبینی معنایی `auto_20` — AIOps و پروژه مدیریت شبکه ۵۰۰ شعبه‌ای

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- غلط تایپی نسخه قدیمی اصلاح و پروژه کلان ۵۰۰ شعبه‌ای همراه با AIOps، RCA، Wave Rollout، Circuit Breaker و Guardrails در ۱۴ بخش و ۱۲ پرسش تدوین شد.
- فایل `01-خام-پروژه/academy-labs/agent3/auto_20_lab.py` به‌صورت Local Mock در Python 3 اجرا و تست شد؛ هیچ شبکه تولیدی متصل نشده است.

## بازبینی فنی فاز ۷ (2026-11-27 — اعتبارسنجی سخت‌گیرانه نوع `bool` و مرزهای ورودی)
- **ایراد:** در `remediation_decision` مقدار `human_approved="False"` به‌دلیل truthiness باعث اجرای خودکار Failover روی ۱۲۵ شعبه بدون تأیید انسانی می‌شد؛ همچنین `z_score` روی baseline خالی/ثابت دچار خطا یا عدد مصنوعی می‌شد.
- **منبع معتبر:** Python Data Model، آمار پایه (انحراف معیار/Z-score) و کنترل ایمنی Human-in-the-Loop در AIOps.
- **اصلاح انجام‌شده:** اعمال `_require_bool` روی `human_approved`، اعتبارسنجی بازه `confidence in [0,1]` و `impacted_branches >= 0`، و نگهبان `len(baseline) >= 2` / واریانس صفر در `z_score`.
- **تست مرتبط:** `test_phase7_strict_boolean_typing_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی ۵۰۰ شعبه بدون کنترلر یا کلاستر ML زنده؛ بازبینی نویسنده (نه مستقل).
