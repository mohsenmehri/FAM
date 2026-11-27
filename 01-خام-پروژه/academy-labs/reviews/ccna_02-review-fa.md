# ccna_02 — بازبینی نویسنده STP و EtherChannel

۲۰۲۶-۱۱-۲۷. نویسنده ۱۴ بخش، واژه‌نامه، مثال، ۱۲ پرسش و همه گزینه‌ها و مدل را بررسی کرد. این بازبینی مستقل انسانی نیست. پاسخ‌ها به‌ترتیب حلقه لایه ۲، کمترین bridge ID، تساوی MAC، معیار root port، BPDU، زمان RSTP، edge، همسایه، تجمیع لینک، hash، LACP و مرز مدل‌اند. این شناسه با `ccna_02_vlan` تاریخی متفاوت است و سؤال چهارم درس VLAN در نامزد آن حفظ شده است.

[راهنمای Cisco درباره STP](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10556-16.html) و [EtherChannel](https://www.cisco.com/c/en/us/support/docs/lan-switching/etherchannel/12023-4.html) مبنای بررسی‌اند؛ پورت و نسخه و VLAN و هزینه مسیر در انتخاب نقش مهم‌اند. یک جریان منفرد الزاماً از مجموع ظرفیت استفاده نمی‌کند و اطلاعات CDP/LLDP به‌تنهایی اعتبار هویت همسایه را اثبات نمی‌کند.

کد `stp_root_mock.py` صرفاً مقایسه فیلد ۱۶ بیتی bridge ID و MAC را انجام می‌دهد. پیش‌تر به علت زیرنوع بودن bool در Python، `True` به عنوان priority پذیرفته می‌شد؛ اکنون رد و تست شده است. مدل انتخاب root port، BPDU، topology یا LACP و هیچ تجهیز واقعی را اجرا نمی‌کند. مهاجرت پیشرفت تاریخی انجام نشده است.
