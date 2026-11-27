# شواهد بازبینی معنایی `spec_wl` — تخصص Wireless (فیزیک RF، Wi-Fi 6/6E/7 و Catalyst 9800)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت) انجام شده؛ **بازبینی مستقل انسانی انجام نشده است.**

## یافته‌های ممیزی نسخه قدیمی (`5a747490`) و اصلاحات
- نسخه قدیمی ۳ بخش و ۳ پرسش داشت و آزمایشگاه آن فقط VLAN 180/190 را در شبیه‌ساز ذخیره می‌کرد.
- محاسبات عددی `dBm <-> mW`، EIRP (`14 - 1 + 4 = 17 dBm ≈ 50.12 mW`)، اثر +3 dB کف نویز به ازای هر دو برابر شدن عرض کانال (افت SNR از 26 dB در 20 MHz به 20 dB در 80 MHz) با Python راستی‌آزمایی شدند.
- قوانین امنیتی باند 6 GHz (ممنوعیت WPA2/Open کلاسیک؛ الزام WPA3 یا OWE به همراه Mandatory PMF) و ترکیب دقیق Catalyst 9800 FlexConnect Local Switching بررسی و ثبت شدند.

## راستی‌آزمایی آزمایشگاه
- فایل `01-خام-پروژه/academy-labs/agent3/spec_wl_lab.py` یک **Python Mock محلی** است که اجرا و تست شده است. هیچ WLC یا AP واقعی اجرا نشده است.

## بازبینی فنی فاز ۸A (2026-11-27)
- **ایراد:** عدم اعتبارسنجی بولی روی ۵ پرچم `resolve_c9800_ap_behavior` (`wlan_no_shut='False'` SSID را فعال نشان می‌داد) و عدم رد `cable_loss_db < 0` یا مقادیر غیرمتناهی/bool در `compute_rf_link`.
- **منبع معتبر:** IEEE 802.11ax/be (6 GHz WPA3/OWE + Mandatory PMF) و Cisco Catalyst 9800 Configuration Model.
- **اصلاح انجام‌شده:** اعمال `_require_bool` روی ۵ پرچم C9800، `_require_finite_num` و `cable_loss_db >= 0` + assertها.
- **تست مرتبط:** `test_phase8a_ccde18_dynamic_vrf_and_specialist_core_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون WLC 9800 یا رادیو واقعی؛ بازبینی نویسنده (نه مستقل).

## به‌روزرسانی فاز ۱۰B — خودبازبینی نویسنده (reviewed.9؛ بدون بازبینی مستقل انسانی)
- **تغییرات:** محافظت `_require_finite_num` و `dbm_to_mw` در برابر `OverflowError` (`10**500` و `dbm=10000`) و تبدیل به `ValueError`.
- **وضعیت اجرا:** آزمایشگاه محلی/Mock Python بدون تجهیز شبکه یا سرویس زنده؛ تطابق دقیق بایتی کد HTML با `spec_wl_lab.py` تأیید شد.
