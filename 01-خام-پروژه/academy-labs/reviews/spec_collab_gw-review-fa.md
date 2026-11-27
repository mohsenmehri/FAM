# شواهد بازبینی معنایی `spec_collab_gw` — دروازه‌های صوتی، Cisco CUBE (SBC)، Dial-Peer و SRST

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/spec_collab_gw_lab.py` بررسی و اجرا شدند.
- هیچ روتر Cisco CUBE یا خوشه CUCM واقعی متصل نشده است.

## بازبینی فنی و معنایی مرحله ۲ (۲۰۲۶-۱۱-۲۷)

- وضعیت بازبینی: همچنان **بازبینی نویسنده (author-agent-self-review-not-independent)** است و **بازبینی مستقل انسانی انجام نشده است**.
- مسئله: عبارت مطلق «همیشه باید» در توضیح پرسش ۵.
- منبع: Cisco Unified Border Element (CUBE) Configuration Guide.
- آزمون مرتبط: `test_agent3_content.py` (`test_technical_audit_regressions`).

## بازبینی فنی فاز ۸B (2026-11-27)
- **ایراد:** نبود `_require_bool` روی `primary_trunk_up`، `wan_to_cucm_up` و `srst_configured` و عدم رد `dialed_number` خالی.
- **منبع معتبر:** Cisco CUBE Dial-Peer Longest Match و SRST Survivability.
- **اصلاح انجام‌شده:** اعمال `_require_bool`، اعتبارسنجی `dialed_number` و افزودن assertها.
- **تست مرتبط:** `test_phase8b_ccie_and_remaining_specialist_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون CUBE/CUCM زنده؛ بازبینی نویسنده (نه مستقل).
