# گزارش خودبازبینی فنی درس `ccnp_enc_arch` — معماری سازمانی در CCNP ENCOR: طراحی Three-Tier/Collapsed Core، SD-Access، SD-WAN و CEF/NSF-SSO

- **وضعیت بازبینی:** خودبازبینی فنی نویسنده انجام شده؛ **بازبینی مستقل انسانی انجام نشده است**.
- **منابع مقایسه‌شده:** داده تاریخی `5a7474902c8d729950288198953686702cfd85dc` و پیش‌نویس ایجنت اول `641d02ee73e0fa86b0972dc1f85474e84abef288`.
- **وضعیت آزمایشگاه:** `01-خام-پروژه/academy-labs/agent3/ccnp_enc_arch_lab.py` — **شبیه‌سازی محلی Python 3 (Mock)** اجرا و با آزمون خودکار تأیید شده؛ هیچ تجهیز زنده یا شبکه تولیدی متصل نشده است.

## اصلاحات فنی کلیدی
- تفکیک دقیق معیار انتخاب Two-Tier (Collapsed Core) از Three-Tier و مزایای Routed Access.
- تصریح دقیق سه صفحه Control/Data/Policy در SD-Access (LISP، VXLAN، SGT/TrustSec) و چهار مؤلفه کلیدی SD-WAN (vBond، vSmart، vManage، WAN Edge).
- ساخت آزمایشگاه محلی ccnp_enc_arch_lab.py برای شبیه‌سازی CEF (FIB + Adjacency Table)، NSF/SSO و پیشنهاد معماری Campus.

## پوشش ساختاری
- ۱۴ بخش آموزشی + نمودار SVG اختصاصی + ۱۵ واژه کلیدی + ۱۲ پرسش چندگزینه‌ای با پاسخ تشریحی + همگام‌سازی byte-for-byte کد آزمایشگاه.
