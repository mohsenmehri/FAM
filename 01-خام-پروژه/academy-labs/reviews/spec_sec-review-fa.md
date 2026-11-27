# شواهد بازبینی معنایی `spec_sec` — تخصص امنیت (FTD، ISE، 802.1X و Zero Trust)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت) انجام شده؛ **بازبینی مستقل انسانی انجام نشده است.**

## یافته‌های ممیزی نسخه قدیمی (`5a747490`) و اصلاحات
- نسخه قدیمی فقط ۳ بخش و ۳ سؤال داشت و آزمایشگاه آن صرفاً جداسازی VLAN در شبیه‌ساز ساده بود بدون مدل‌سازی سیاست TLS یا 802.1X.
- در نسخه بازطراحی‌شده، معماری دوگانه FTD (Lina + Snort 3)، محدودیت‌های واقعی TLS Decrypt-Resign (Certificate Pinning، Compliance، ظرفیت)، مراحل IBNS 2.0 (Monitor/Low-Impact/Closed)، تفکیک دقیق پورت RADIUS CoA (UDP 1700 در سیسکو در برابر UDP 3799 در RFC 5176) و چارچوب NIST SP 800-207 به دقت تشریح شدند.

## راستی‌آزمایی فنی و آزمایشگاه
- فایل `01-خام-پروژه/academy-labs/agent3/spec_sec_lab.py` یک **Python Mock محلی** است که منطق Decrypt-Resign/Bypass/Snort و Host-Modeهای 802.1X را مدل‌سازی و آزمون می‌کند. هیچ FTD، FMC، Cisco ISE یا سوئیچ واقعی اجرا نشده است.

## بازبینی فنی فاز ۷ (2026-11-27 — اعتبارسنجی سخت‌گیرانه نوع `bool` و مرزهای ورودی)
- **ایراد:** تبدیل `bool(sess['authenticated'])` باعث می‌شد مقدار رشته‌ای `"False"` به `True` تبدیل شده و کلاینت احرازنشده 802.1X مجاز شود.
- **منبع معتبر:** Python Data Model و معماری کنترل دسترسی IEEE 802.1X / Cisco FTD TLS Decryption.
- **اصلاح انجام‌شده:** اعمال `_require_bool` سخت‌گیرانه روی `authenticated`، `decrypt_enabled`، `cert_pinned` و `snort_signature_match` و اعتبارسنجی `host_mode`/`port_mode` همراه با assertها.
- **تست مرتبط:** `test_phase7_strict_boolean_typing_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون FTD/ISE زنده؛ بازبینی نویسنده (نه مستقل).
