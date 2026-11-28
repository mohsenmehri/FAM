# شواهد بازبینی معنایی `auto_07` — پروتکل HTTP و HTTPS در برنامه‌نویسی شبکه

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و کد `01-خام-پروژه/academy-labs/agent3/auto_07_lab.py` بررسی و اجرا شدند.
- استانداردهای RFC 8446 (TLS 1.3)، RFC 9113/9114 (HTTP/2 & HTTP/3)، RFC 7519 (JWT)، RFC 6749 (OAuth 2.0) و RFC 9525 (SAN) تطبیق داده شدند. هیچ سرور TLS/OAuth زنده متصل نشده است.

## ممیزی فنی و معنایی مرحله ۳ (۲۰۲۶-۱۱-۲۷)

- **هم‌راستاسازی `verify_hs256_jwt` و `verify_san_match` با RFC 8725 و متن درس:** قفل صریح `alg == 'HS256'` (رد حمله `alg: 'none'`)، بررسی انقضای `exp` و رفع باگ برچسب خالی `.netops.example` در `auto_07_lab.py` اعمال و با تست‌های منفی خودکار تأیید شد.
- **وضعیت بازبینی:** خودبازبینی نویسنده (`author-agent-self-review-not-independent`)؛ بازبینی مستقل انجام نشده است.

## به‌روزرسانی فاز ۱۰E — خودبازبینی نویسنده (reviewed.9؛ بدون بازبینی مستقل انسانی)
- **تغییرات:** رفع تله `isinstance(True, int)` در `exp` و `now_ts` توکن JWT، مدیریت امن خطاهای Base64/JSON خراب به خروجی `malformed_jwt` و اعتبارسنجی ورودی‌های `verify_san_match`.
- **وضعیت اجرا:** اجرای محلی Python بدون تجهیز شبکه یا سرویس بیرونی زنده؛ تطابق دقیق بایتی کد HTML با `auto_07_lab.py` تأیید شد.

## به‌روزرسانی فاز ۱۳ (رفع کامل ایرادهای `batch-auto-07-09-intake-fa.md` @ `9cdaf84b4e`)
- رفع باگ `TypeError` روی امضای غیر-ASCII (`☃`) با اعتبارسنجی سخت‌گیرانه ASCII Base64URL و مقایسه بایتی `hmac.compare_digest(bytes, bytes)`.
- حذف نام گمراه‌کننده `verify_hs256_jwt` و کلید بدون‌مرز `valid` و جایگزینی با `evaluate_hs256_jwt_demo` همراه کلیدهای صریح `demo_checks_passed`، `educational_demo_only`، `not_production_jwt_verifier`، `checks_performed` و `checks_not_implemented`.
- افزودن بررسی `nbf` و اختیاری `iss`/`aud`/`typ`، رد کلید تکراری JSON و رد Wildcard روی IP literal در SAN.
- اصلاح بخش‌های ۶، ۱۰ و ۱۴ و آزمون برای تصریح وابستگی بررسی ابطال گواهینامه (CRL/OCSP) به کلاینت/سیاست، ارجاع صریح به RFC 8725 و مرز غیرتولیدی آزمایشگاه.
- **وضعیت بازبینی:** همچنان خودبازبینی نویسنده (`author-agent-self-review-not-independent`) — آماده بازبینی مجدد یکپارچه‌ساز/انسان مستقل.
