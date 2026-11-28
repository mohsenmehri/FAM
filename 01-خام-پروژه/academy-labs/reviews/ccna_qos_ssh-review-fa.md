# شواهد بازبینی معنایی `ccna_qos_ssh` — CCNA (سرویس‌های IP و مدیریت): مبانی QoS (DiffServ/DSCP/LLQ)، مدیریت امن SSHv2 و انتقال فایل (TFTP/FTP/SCP)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/ccna_qos_ssh_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲B (2026-11-27)

- تصریح ماهیت مهندسی اهداف VoIP SLA (G.114/SRND)، Policer داخلی LLQ، مرز اعتماد (Trust Boundary)، تفاوت CoS/DSCP و Policing/Shaping.
- گسترش از ۳ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `ccna_qos_ssh_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc2474
- https://www.rfc-editor.org/rfc/rfc3246
- https://www.rfc-editor.org/rfc/rfc4251
- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_conmgt/configuration/xe-16/qos-conmgt-xe-16-book.html

### آزمون و پوشش
- تست مرتبط: `test_phase12b_transferred_ccna_services_security_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
