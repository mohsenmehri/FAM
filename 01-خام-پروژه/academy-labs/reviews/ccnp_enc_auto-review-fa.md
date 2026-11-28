# گزارش خودبازبینی فنی درس `ccnp_enc_auto` — اتوماسیون در CCNP ENCOR: JSON/YAML/XML، مدل YANG، NETCONF در برابر RESTCONF، EEM و Guest Shell

- **وضعیت بازبینی:** خودبازبینی فنی نویسنده انجام شده؛ **بازبینی مستقل انسانی انجام نشده است**.
- **منابع مقایسه‌شده:** داده تاریخی `5a7474902c8d729950288198953686702cfd85dc` و پیش‌نویس ایجنت اول `641d02ee73e0fa86b0972dc1f85474e84abef288`.
- **وضعیت آزمایشگاه:** `01-خام-پروژه/academy-labs/agent3/ccnp_enc_auto_lab.py` — **شبیه‌سازی محلی Python 3 (Mock)** اجرا و با آزمون خودکار تأیید شده؛ هیچ تجهیز زنده یا شبکه تولیدی متصل نشده است.

## اصلاحات فنی کلیدی
- تفکیک دقیق NETCONF (RFC 6241، SSH 830، XML، Candidate Datastore و تایید تراکنشی) از RESTCONF (RFC 8040، HTTPS 443، JSON/XML، بدون Candidate Datastore استاندارد).
- تبیین دقیق نقش YANG (RFC 7950) به‌عنوان زبان مدل‌سازی داده و تفاوت OpenConfig، IETF و Native Models.
- ساخت آزمایشگاه محلی ccnp_enc_auto_lab.py برای شبیه‌سازی چرخه Candidate->Commit/Discard در NETCONF، متدهای RESTCONF و سیاست EEM.

## پوشش ساختاری
- ۱۴ بخش آموزشی + نمودار SVG اختصاصی + ۱۵ واژه کلیدی + ۱۲ پرسش چندگزینه‌ای با پاسخ تشریحی + همگام‌سازی byte-for-byte کد آزمایشگاه.
