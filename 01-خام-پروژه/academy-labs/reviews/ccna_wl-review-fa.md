# شواهد بازبینی معنایی `ccna_wl` — CCNA (شبکه‌های بی‌سیم): مبانی Wi-Fi، کانال‌های RF، معماری AP/WLC (CAPWAP) و امنیت WPA2/WPA3

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/ccna_wl_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲B (2026-11-27)

- کشف و اصلاح خطای بحرانی آزمون نسخه خام ایجنت ۱ (`ccna_wl.json` Q2 داشت `ans=2` یعنی معکوس AP=Trunk و WLC=Access برای Local Mode!).
- تصریح تفاوت DTLS پیش‌فرض در CAPWAP Control (UDP 5246) و Data (UDP 5247)، تفکیک Local Mode و FlexConnect و تکمیل مباحث WPA3 SAE + PMF + 6GHz.
- گسترش از ۴ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `ccna_wl_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc5415
- https://www.wi-fi.org/discover-wi-fi/security
- https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/17-9/config-guide/b_wl_17_9_cg.html

### آزمون و پوشش
- تست مرتبط: `test_phase12b_transferred_ccna_services_security_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
