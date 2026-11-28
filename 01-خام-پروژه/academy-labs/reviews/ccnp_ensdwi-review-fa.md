# گزارش خودبازبینی فنی درس `ccnp_ensdwi` — تخصص CCNP ENSDWI (Cisco SD-WAN): چهار صفحه معماری، پروتکل OMP، TLOC و مسیریابی آگاه از برنامه (AAR)

- **وضعیت بازبینی:** خودبازبینی فنی نویسنده انجام شده؛ **بازبینی مستقل انسانی انجام نشده است**.
- **منابع مقایسه‌شده:** داده تاریخی `5a7474902c8d729950288198953686702cfd85dc` و پیش‌نویس ایجنت اول `641d02ee73e0fa86b0972dc1f85474e84abef288`.
- **وضعیت آزمایشگاه:** `01-خام-پروژه/academy-labs/agent3/ccnp_ensdwi_lab.py` — **شبیه‌سازی محلی Python 3 (Mock)** اجرا و با آزمون خودکار تأیید شده؛ هیچ تجهیز زنده یا شبکه تولیدی متصل نشده است.

## اصلاحات فنی کلیدی
- تفکیک دقیق چهار صفحه Management (vManage)، Orchestration (vBond)، Control (vSmart/OMP) و Data (WAN Edge/IPsec) و جداسازی VPN 0، VPN 512 و Service VPN.
- تبیین دقیق سه مؤلفه TLOC (System IP، Color، Encapsulation)، سه نوع مسیر OMP (OMP/TLOC/Service) و معیارهای BFD برای AAR (Latency/Loss/Jitter).
- ساخت آزمایشگاه محلی ccnp_ensdwi_lab.py برای شبیه‌سازی انتخاب TLOC، سیاست SLA در AAR و منطق مسیردهی OMP.

## پوشش ساختاری
- ۱۴ بخش آموزشی + نمودار SVG اختصاصی + ۱۵ واژه کلیدی + ۱۲ پرسش چندگزینه‌ای با پاسخ تشریحی + همگام‌سازی byte-for-byte کد آزمایشگاه.
