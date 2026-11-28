# شواهد بازبینی معنایی `adv_04` — عیب‌یابی پیشرفته (Advanced Troubleshooting): تفکیک Control/Data Plane (CEF)، تله MTU/MSS و Asymmetric Routing

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/adv_04_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲C (2026-11-27)

- افزودن تفکیک عملیاتی اندازه پینگ DF بین Cisco IOS (`size 1500` کل بسته) و Linux/Windows (`-s/-l 1472` فقط Payload)، تصریح `ICMP Type 3 Code 4` / `ICMPv6 Type 2` و تفکیک uRPF Strict و Loose.
- گسترش از ۳ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `adv_04_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc1191
- https://www.rfc-editor.org/rfc/rfc2784
- https://www.cisco.com/c/en/us/support/docs/ip/generic-routing-encapsulation-gre/25885-pmtud-ipfrag.html

### آزمون و پوشش
- تست مرتبط: `test_phase12c_transferred_advanced_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
