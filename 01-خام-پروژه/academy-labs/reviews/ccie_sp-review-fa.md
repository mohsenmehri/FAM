# شواهد بازبینی معنایی `ccie_sp` — CCIE Service Provider v5.1

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/ccie_sp_lab.py` بررسی و اجرا شدند.
- عبارات نامفهوم و معیوب نسخه قدیمی کامل اصلاح و ثبت شدند.
- هیچ روتر واقعی IOS-XR یا هسته MPLS متصل نشده است.

## بازبینی فنی فاز ۸B (2026-11-27)
- **ایراد:** نبود `_require_bool` روی پرچم‌های IGP و IOS-XR eBGP RPL (مقدار `"False"` عبور می‌کرد)، نبود اعتبارسنجی `prefix_sid_index` و عبارت مطلق «بدون خطای دستی» در بخش ۹.
- **منبع معتبر:** RFC 8212 (Default EBGP Route Propagation Behavior)، RFC 8660 (SR-MPLS) و Python Data Model.
- **اصلاح انجام‌شده:** اعمال `_require_bool`/`_require_prefix_sid`، افزودن assertها و تعدیل بخش ۹.
- **تست مرتبط:** `test_phase8b_ccie_and_remaining_specialist_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی بدون IOS-XR/MPLS زنده؛ بازبینی نویسنده (نه مستقل).
