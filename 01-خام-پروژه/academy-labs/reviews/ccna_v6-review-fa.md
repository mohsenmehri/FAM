# شواهد بازبینی معنایی `ccna_v6` — CCNA (مسیریابی): مسیریابی Dual-Stack IPv4 و IPv6، Longest Prefix Match، AD/Metric و OSPFv3

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/ccna_v6_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲A (2026-11-27)

- تصریح اینکه مقادیر AD (Static=1، EIGRP=90، OSPF=110) پیش‌فرض‌های فروشنده سیسکو هستند نه ثابت RFC.
- تفکیک OSPFv3 کلاسیک (RFC 5340) از OSPFv3 Address-Families (RFC 5838)، تصریح الزام اینترفیس خروجی برای `fe80::/10` و نیاز به `router-id` ۳۲بیتی روی روتر صرفاً-IPv6.
- تبدیل درس ۳بخشی/۳سؤالی قدیمی به بسته ۱۴بخشی/۱۵واژه‌ای/۱۲سؤالی همراه با `ccna_v6_lab.py` مبتنی بر `ipaddress` با `strict=True`.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc4291
- https://www.rfc-editor.org/rfc/rfc5340
- https://www.rfc-editor.org/rfc/rfc5838
- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_pi/configuration/xe-16/iri-xe-16-book/iri-ipv6-routing.html

### آزمون و پوشش
- تست مرتبط: `test_phase12a_transferred_ccna_core_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
