# شواهد بازبینی معنایی `auto_13` — Cisco NSO (Network Services Orchestrator)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- عبارات نیمه‌انگلیسی نسخه قدیمی به فارسی مهندسی استاندارد بازنویسی و محتوا به ۱۴ بخش، ۱۵ واژه و ۱۲ پرسش ارتقا یافت.
- فایل `01-خام-پروژه/academy-labs/agent3/auto_13_lab.py` به‌صورت Local Mock در Python 3 اجرا و تست شد؛ هیچ سرور واقعی Cisco NSO متصل نشده است.

## بازبینی فنی فاز ۸C-2 (2026-11-27)
- **ایراد:** عدم اعتبارسنجی `vrf_name`/`rd` خالی و پرتاب `KeyError` خام روی نام تجهیز ناشناخته در `check_sync`.
- **منبع معتبر:** Cisco NSO CDB/NED/FASTMAP Two-Phase Commit.
- **اصلاح انجام‌شده:** افزودن `_require_non_empty_str` و بررسی وجود تجهیز در `commit_service`/`check_sync`.
- **تست مرتبط:** `test_phase8c2_remaining_automation_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی بدون NSO زنده؛ بازبینی نویسنده (نه مستقل).
