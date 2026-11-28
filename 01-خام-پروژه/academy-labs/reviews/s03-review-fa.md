# شواهد بازبینی معنایی s03 — سوئیچینگ و TCP/UDP

تاریخ ۲۰۲۶-۱۱-۲۷. بازبینی توسط نویسنده است، نه کارشناس مستقل انسانی. ۱۴ بخش، واژه‌نامه، ۱۲ پرسش و همه گزینه‌ها، مثال و آزمایشگاه بررسی شده‌اند.

- [راهنمای جدول MAC سیسکو](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/cdp-lldp-mac-udld/cdp-lldp-mac-udld-configuration-guide/c-configure-mac.html) یادگیری مبدأ و نگاشت VLAN/پورت، aging و ارسال بر اساس مقصد را شرح می‌دهد. flooding به پورت واجد شرایط و VLAN و استثناهای سیاستی محدود است. [RFC 4541](https://www.rfc-editor.org/rfc/rfc4541) تأثیر IGMP/MLD snooping بر multicast را شرح می‌دهد؛ این RFC اطلاعاتی است، نه گواهی رفتار همه پلتفرم‌ها.
- [راهنمای duplex سیسکو](https://www.cisco.com/c/en/us/support/docs/lan-switching/ethernet/10561-3.html) و منطق Ethernet در حالت full duplex، تفکیک half/full و احتمال mismatch را پشتیبانی می‌کنند. mismatch از یک علامت به تنهایی نتیجه قطعی نیست.
- [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293) مبنای TCP و [RFC 768](https://www.rfc-editor.org/rfc/rfc768) مبنای UDP است. UDP تضمین تحویل، ترتیب یا سرعت بالاتر ندارد؛ برنامه می‌تواند سازوکار خود را بسازد و TCP به‌تنهایی رمزنگاری نیست.
- ۱۲ پاسخ و تمام گزینه‌ها به ترتیب مبدأ، flooding مقصد ناشناخته، فیلتر پورت ورودی، snooping، full duplex، VLAN، مرز روتر، جریان مرتب TCP، عدم تضمین UDP، STP، علل جابه‌جایی و محدودیت مدل بررسی شدند.
- مدل `switch_learning_mock.py` سه پورت و یک VLAN فرضی دارد؛ خروجی شناخته/ناشناخته، filter و broadcast و ورودی نامعتبر در `tests/test_foundations_models.py` آزمون شده است. STP، multicast snooping، aging، همه سیاست‌های سوئیچ و دستگاه واقعی در این مدل نیست.

این بررسی ادعای capture، اجرای فریم یا آزمون تجهیزات و بازبینی مستقل انسانی ندارد.
