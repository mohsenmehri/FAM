# شواهد بازبینی معنایی `auto_17` — کانتینرها و Docker در سرویس‌های شبکه

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- غلط‌های تایپی نسخه قدیمی اصلاح و مباحث Docker Networking، Volumes، Compose و Hardening در ۱۴ بخش و ۱۲ پرسش تدوین شدند.
- فایل `01-خام-پروژه/academy-labs/agent3/auto_17_lab.py` به‌صورت Local Mock در Python 3 اجرا و تست شد؛ هیچ دیمون واقعی Docker درگیر نشده است.

## بازبینی فنی فاز ۵ (2026-11-27 — ممیزی موضوعی درس‌ها و آزمایشگاه‌های باقی‌مانده با آزمون‌های منفی)
- **ایراد:** در `audit_dockerfile`: ۱) `USER 0` تشخیص داده نمی‌شد؛ ۲) وجود `USER appuser` قبل از `USER root/0` با `any(...)` دور زده می‌شد؛ ۳) کلیدهای `TOKEN=`/`API_KEY=` در `ENV` بررسی نمی‌شدند.
- **منبع معتبر:** Docker Dockerfile Best Practices و CIS Docker Benchmark 4.1
- **اصلاح انجام‌شده:** بررسی آخرین دستور مؤثر `USER` و رد `root`/`0`، گسترش تشخیص اسرار `ENV` و افزودن تست منفی escalation به `USER 0`.
- **تست مرتبط:** `test_phase5_remaining_tracks_labs_and_regressions` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** لینتر آموزشی محلی بدون Docker Daemon؛ بازبینی مستقل انجام نشده است.
