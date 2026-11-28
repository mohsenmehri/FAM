# s08 — بازبینی نویسنده: حالت‌های IOS و حافظه

۲۰۲۶-۱۱-۲۷، توسط نویسنده و بدون بازبینی مستقل انسانی. ۱۴ بخش، واژه‌نامه، ۱۲ سؤال و همه گزینه‌ها، سناریو، مثال و آزمایشگاه بررسی شدند؛ رفتارها وابسته به محصول و مجوزند.

- [مستند فرمان‌های IOS](https://www.cisco.com/c/en/us/td/docs/wireless/access_point/15-3-3-JB/command/reference/cr-book/cr-chap1.html) نمونه حالت user/privileged، enable، configure، interface، exit و end را توضیح می‌دهد؛ نام و قابلیت interface الزاماً در همه دستگاه‌ها یکسان نیست. [راهنمای IOS](https://www.cisco.com/en/US/docs/ios/12_3/vvf_r/vrgusing_ps1839_TSD_Products_Command_Reference_Chapter.html) نمونه running-config، startup-config و ذخیره را برای نسخه خود شرح می‌دهد.
- [مستند configuration register](https://www.cisco.com/c/en/us/support/docs/routers/10000-series-routers/50421-config-register-use.html) نقش آن در boot و ignore configuration را شرح می‌دهد؛ تغییر روی دستگاه تولیدی بدون مجوز، نسخه پشتیبان و طرح بازیابی توصیه نشده است.
- پاسخ‌ها به ترتیب running-config، فرار بودن تغییر ذخیره‌نشده، startup-config، وابستگی ذخیره به پلتفرم، prompt، enable، exit، end، اثر register، خطر تغییر، contextual help و محدودیت مدل بازبینی شد.
- آزمایشگاه `ios_modes_mock.py` یک ماشین حالت محلی محدود در حافظه است. آزمون‌ها در `tests/test_foundations_models.py` مسیرهای مجاز و ورودی غیرمجاز را می‌سنجند. برنامه IOS، boot، مجوز، تنظیمات، تجهیزات و شبکه واقعی را اجرا نمی‌کند؛ تمرین آن شاهد اجرای تجهیزات نیست.
