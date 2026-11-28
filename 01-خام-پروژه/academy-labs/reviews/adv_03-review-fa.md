# شواهد بازبینی معنایی `adv_03` — سرویس‌های پیشرفته (Advanced Services): جداسازی لایه ۳ با VRF-Lite، پایش فعال IP SLA + Track و NetFlow

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/adv_03_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲C (2026-11-27)

- تکمیل جزئیات VRF-Lite (جداسازی RIB/CEF/ARP و تله حذف IP)، IP SLA (Responder برای udp-jitter، track delay ضد-Flap، track list ضد False Failover) و IPFIX RFC 7011 / Sampled NetFlow.
- گسترش از ۳ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `adv_03_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc7011
- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_pi/configuration/xe-16/iri-xe-16-book/iri-vrf-lite.html
- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipsla/configuration/xe-16/sla-xe-16-book.html

### آزمون و پوشش
- تست مرتبط: `test_phase12c_transferred_advanced_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
