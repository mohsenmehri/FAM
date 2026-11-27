# شواهد بازبینی معنایی `ccie_sec` — CCIE Security v6.1

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/ccie_sec_lab.py` بررسی و اجرا شدند.
- هیچ دستگاه ISE یا FTD/FMC واقعی متصل نشده است.

## بازبینی فنی فاز ۵ (2026-11-27 — ممیزی موضوعی درس‌ها و آزمایشگاه‌های باقی‌مانده با آزمون‌های منفی)
- **ایراد:** ۱) `audit_ntp_dns_preflight` اختلاف >30s را شکست Kerberos اعلام می‌کرد (سقف پیش‌فرض RFC 4120 / AD برابر 300s است)؛ ۲) `ftd_packet_tracer` روی پورت 443 بدون مدل‌سازی TLS-DECRYPT بررسی Snort انجام می‌داد.
- **منبع معتبر:** RFC 4120 §3.1.1 / Active Directory Kerberos MaxClockSkew=300s و معماری Cisco FTD TLS Decryption + Snort 3
- **اصلاح انجام‌شده:** تفکیک هشدار عملیاتی (>30s) از شکست Kerberos (>300s) و افزودن فاز `TLS-DECRYPT` با تست منفی عبور کور ترافیک رمزنگاری‌شده بدون Decrypt.
- **تست مرتبط:** `test_phase5_remaining_tracks_labs_and_regressions` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون ISE/FMC/FTD زنده؛ بازبینی مستقل انجام نشده است.

## بازبینی فنی فاز ۷ (2026-11-27 — اعتبارسنجی سخت‌گیرانه نوع `bool` و مرزهای ورودی)
- **ایراد:** تبدیل `bool(flow.get('tls_decrypted', True))` باعث می‌شد `tls_decrypted="False"` به اشتباه `True` تلقی شده و بازگشایی TLS فرض شود.
- **منبع معتبر:** Python Data Model و ترتیب ارزیابی Cisco FTD TLS Decryption -> Snort 3.
- **اصلاح انجام‌شده:** اعمال `_require_bool` سخت‌گیرانه روی `tls_decrypted`، `route_exists`، `contains_exploit_sig` و `dns_forward_reverse_ok` در `ccie_sec_lab.py`.
- **تست مرتبط:** `test_phase7_strict_boolean_typing_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون ISE/FMC/FTD واقعی؛ بازبینی نویسنده (نه مستقل).

## به‌روزرسانی فاز ۱۰B — خودبازبینی نویسنده (reviewed.9؛ بدون بازبینی مستقل انسانی)
- **تغییرات:** افزودن `_require_finite_num` به `audit_ntp_dns_preflight` برای رد `NaN`/`Inf`/`10**500` و `bool` در `clock_skew_sec` و آستانه‌های زمانی.
- **وضعیت اجرا:** آزمایشگاه محلی/Mock Python بدون تجهیز شبکه یا سرویس زنده؛ تطابق دقیق بایتی کد HTML با `ccie_sec_lab.py` تأیید شد.
