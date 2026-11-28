# شواهد بازبینی معنایی `auto_11` — اتوماسیون با Ansible (Playbook & Inventory)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- عبارات شکسته نسخه قدیمی اصلاح و کل محتوا به ۱۴ بخش، ۱۵ واژه و ۱۲ پرسش ارتقا یافت.
- فایل `01-خام-پروژه/academy-labs/agent3/auto_11_lab.py` به‌صورت Local Mock در Python 3 اجرا و تست شد؛ هیچ باینری Ansible یا روتر واقعی متصل نشده است.

## بازبینی فنی فاز ۸C-2 (2026-11-27)
- **ایراد:** نبود `_require_bool` روی `check_mode` (`check_mode="False"` مانع اعمال تغییر می‌شد) و عدم تفکیک `handler_actually_executed` در حالت `--check`.
- **منبع معتبر:** Ansible `--check` mode & Handlers Semantics و Python Data Model.
- **اصلاح انجام‌شده:** اعمال `_require_bool`، اعتبارسنجی `hosts_pattern`/`parents`/`lines` و افزودن `handler_actually_executed`.
- **تست مرتبط:** `test_phase8c2_remaining_automation_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی بدون Ansible/SSH؛ بازبینی نویسنده (نه مستقل).

## به‌روزرسانی فاز ۱۳ (ممیزی پیشگیرانه پیش از intake)
- افزودن `build_initial_device_state()` و پارامتر اختیاری `device_state` برای ایزوله‌سازی وضعیت میان اجراها و اعتبارسنجی نوع رشته‌ای تک‌تک اعضای `parents` و `lines`.
- **وضعیت بازبینی:** همچنان خودبازبینی نویسنده (`author-agent-self-review-not-independent`).
