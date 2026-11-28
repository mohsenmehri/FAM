# شواهد بازبینی معنایی `ccna_05` — CCNA (امنیت شبکه): فهرست‌های دسترسی ACL، Port Security، DHCP Snooping، DAI و STP Guards

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/ccna_05_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲B (2026-11-27)

- افزودن تله عملیاتی Option 82 در DHCP Snooping لایه ۲، الزام ARP ACL برای میزبان‌های Static IP در DAI، تفکیک دقیق shutdown/restrict/protect و ذخیره Sticky MAC.
- گسترش از ۳ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `ccna_05_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/16-12/configuration_guide/sec/b_1612_sec_9300_cg/configuring_port_security.html
- https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/16-12/configuration_guide/sec/b_1612_sec_9300_cg/configuring_dhcp_snooping.html
- https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/16-12/configuration_guide/sec/b_1612_sec_9300_cg/configuring_dynamic_arp_inspection.html

### آزمون و پوشش
- تست مرتبط: `test_phase12b_transferred_ccna_services_security_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
