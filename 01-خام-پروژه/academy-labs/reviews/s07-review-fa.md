# بازبینی s07: DHCP، DNS، NAT و مشاهده بسته‌ها

۲۰۲۶-۱۱-۲۷ — توسط نویسنده؛ بازبینی مستقل انسانی نیست. ۱۴ بخش، همه گزینه‌های ۱۲ پرسش، مثال PAT، واژه‌نامه و کد آزمایشگاه جداگانه بررسی شد. گزینه اول سؤال ۱۰ طوری اصلاح شد که «وجود ترجمه پیکربندی‌شده» را تضمین NAT تلقی نکند.

- [RFC 2131](https://www.rfc-editor.org/rfc/rfc2131) برای DHCP، DORA نمونه موفق تخصیص اولیه و متفاوت بودن renewal و وضعیت‌های دیگر؛ relay به پیکربندی و رسیدن پیام وابسته است. دریافت IP اثبات صحت مسیر نیست.
- [RFC 1034](https://www.rfc-editor.org/rfc/rfc1034) سلسله‌مراتب و cache، [RFC 3596](https://www.rfc-editor.org/rfc/rfc3596) رکورد AAAA و [RFC 7766](https://www.rfc-editor.org/rfc/rfc7766) انتقال TCP برای DNS؛ cache و نوع انتقال در عیب‌یابی اهمیت دارند.
- [RFC 3022](https://www.rfc-editor.org/rfc/rfc3022) تفاوت Basic NAT و NAPT (سند informational است)؛ [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737) محدوده مستندسازی 198.51.100.0/24؛ تخصیص پورت مدل یک انتخاب آموزشی است نه پیش‌بینی سیستم واقعی.
- [Wireshark display filter](https://www.wireshark.org/docs/man-pages/wireshark-filter.html) نمایش را از capture جدا می‌کند؛ ضبط فقط با مجوز و روی رابط مناسب.
- پاسخ‌های ۱۲ سؤال به ترتیب DORA اولیه، تمدید، relay، علت‌یابی، A، AAAA، cache، انتقال، PAT، عدم تضمین امنیت، display filter و ماهیت مدل بررسی شدند؛ گزینه‌های نادرست نیز مقایسه شدند.
- `services_mock.py` تنها فهرست پیام‌های نمونه و نگاشت فرضی می‌سازد؛ `tests/test_foundations_models.py` رفتار موفق، ورودی نادرست و تخصیص را می‌سنجد. این مدل DHCP/DNS/NAT واقعی، packet capture، timeout، تمدید، فیلتر یا انقضای NAT را اجرا نمی‌کند. آزمون روی شبکه واقعی و مرورگرهای دیگر انجام نشده است.
