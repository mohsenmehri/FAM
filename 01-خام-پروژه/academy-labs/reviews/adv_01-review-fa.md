# شواهد بازبینی معنایی `adv_01` — سوئیچینگ پیشرفته (Advanced Switching): MST (802.1s)، مکانیزم‌های Guard، تله BPDU Filter، UDLD و StackWise/SVL

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/adv_01_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲C (2026-11-27)

- تفکیک دقیق Global BPDU Filter از تله Interface-level BPDU Filter، تصریح ناسازگاری هم‌زمان Root/Loop Guard و مرزبندی سخت‌افزاری StackWise (C9200/C9300) از SVL (C9400/C9500/C9600 Network Advantage + DAD).
- گسترش از ۳ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `adv_01_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc5171
- https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-9000/nb-06-cat-9k-stack-wp-cte-en.html
- https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_mstp.html

### آزمون و پوشش
- تست مرتبط: `test_phase12c_transferred_advanced_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
