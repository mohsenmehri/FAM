# شواهد بازبینی معنایی `spec_ent_sd` — SD-WAN، Catalyst Center و Zero-Touch برای ۱۰۰ شعبه

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/spec_ent_sd_lab.py` بررسی و اجرا شدند.
- هیچ کنترلر یا روتر واقعی متصل نشده است.

## بازبینی فنی فاز ۷ (2026-11-27 — اعتبارسنجی سخت‌گیرانه نوع `bool` و مرزهای ورودی)
- **ایراد:** بررسی truthiness روی `sudi_valid` و `tloc_ext_enabled` باعث می‌شد `sudi_valid="False"` روتر غیرمجاز را بپذیرد؛ `parse_pnp_option43` نیز اعتبار IP/پورت/کد انتقال را چک نمی‌کرد.
- **منبع معتبر:** Cisco Plug and Play (DHCP Option 43) و Cisco SD-WAN ZTP Hardware SUDI Authentication.
- **اصلاح انجام‌شده:** اعمال `_require_bool` روی `sudi_valid`/`tloc_ext_enabled` و اعتبارسنجی `ipaddress.ip_address`، بازه پورت `1..65535` و کد `K4/K1` در `parse_pnp_option43`.
- **تست مرتبط:** `test_phase7_strict_boolean_typing_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی بدون Catalyst Center یا vManage؛ بازبینی نویسنده (نه مستقل).
