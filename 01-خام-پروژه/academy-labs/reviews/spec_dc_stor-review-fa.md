# شواهد بازبینی معنایی `spec_dc_stor` — شبکه ذخیره‌سازی SAN، Fibre Channel، VSAN/Zoning و FCoE

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/spec_dc_stor_lab.py` بررسی و اجرا شدند.
- هیچ سوئیچ Cisco MDS یا آرایه SAN واقعی متصل نشده است.

## بازبینی فنی فاز ۵ (2026-11-27 — ممیزی موضوعی درس‌ها و آزمایشگاه‌های باقی‌مانده با آزمون‌های منفی)
- **ایراد:** شمارش Initiator در `evaluate_fc_access` به پیشوند سخت‌کد `20:00:00:11` وابسته بود و HBAهای با OUI دیگر را نادیده می‌گرفت.
- **منبع معتبر:** Cisco MDS 9000 Fibre Channel Zoning Guide (Single-Initiator Zoning Best Practice)
- **اصلاح انجام‌شده:** جایگزینی با رجیستری صریح `known_initiator_wwpns` و افزودن تست منفی Zone چند-Initiator (QLogic `21:00:00:24:...`).
- **تست مرتبط:** `test_phase5_remaining_tracks_labs_and_regressions` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون سوئیچ MDS یا آرایه ذخیره‌سازی؛ بازبینی مستقل انجام نشده است.
