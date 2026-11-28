# شواهد بازبینی معنایی `ccna_02_vlan` — CCNA (تکمیلی لایه ۲): VLAN، پورت‌های Access، Voice، 802.1Q Trunk، Native VLAN و DTP

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/ccna_02_vlan_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲A (2026-11-27)

- رفع کامل اختلاف نسخه `agent1_rewrites/ccna_02_vlan.json` (`allowed vlan 10,20`) با `academy-data.json` (`10,20,999` با خروجی نمونه `10,20`): همسان‌سازی دو سر ترانک SW1/SW2 روی `10,20,50,999` با ساخت VLAN 50 (Voice) و Native VLAN 999 در هر دو سوئیچ و تصریح `switchport mode trunk`.
- رفع تمام یافته‌های `ccna_02_vlan-intake-fa.md`: تفکیک `switchport mode access` از `switchport nonegotiate`، تعدیل untagged بودن Native VLAN به رفتار پیش‌فرض (ذکر `vlan dot1q tag native`)، ذکر وابستگی پلتفرمی `encapsulation dot1q` و `nonegotiate`، محدود کردن `show vlan brief` به نمایش Catalyst، تکمیل عیب‌یابی (VLAN active، STP، لینک، L3 و فیلترینگ) و حذف ادعای خروجی «زنده».

### منابع معتبر بررسی‌شده
- https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9600/software/release/16-11/configuration_guide/vlan/b_1611_vlan_9600_cg/b_1611_vlan_9600_cg_chapter_010.html
- https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9500/software/release/16-6/command_reference/b_166_9500_cr/b_166_9500_cr_chapter_0111.html
- https://www.cisco.com/c/en/us/support/docs/lan-switching/8021q/17056-741-4.html

### آزمون و پوشش
- تست مرتبط: `test_phase12a_transferred_ccna_core_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.

## به‌روزرسانی فاز ۱۴ (همگام‌سازی نکات `ccna_02_vlan-integration-review-fa.md` @ `ffd6a320ca`)
- رفع تایپوی «تگ ۴بیتی» به «تگ ۴بایتی»، تصریح اینکه VLAN جایگزین ACL نیست، کنترل وجود Native VLAN در پایگاه داده هر سمت و اعتبارسنجی `isinstance(..., str)` برای حالت پورت.
