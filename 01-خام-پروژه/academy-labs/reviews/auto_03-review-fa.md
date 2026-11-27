# شواهد بازبینی معنایی `auto_03` — Python پیشرفته (Netmiko، Paramiko، Nornir)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و کد `01-خام-پروژه/academy-labs/agent3/auto_03_lab.py` بررسی و اجرا شدند.
- هیچ اتصال SSH واقعی، Netmiko یا Nornir به تجهیزات شبکه اجرا نشده است؛ آزمایشگاه یک Python Mock محلی است که الگوهای ایمنی را می‌آزماید.

## بازبینی فنی فاز ۸C-1 (2026-11-27)
- **ایراد:** نبود `_require_bool` روی `use_textfsm` و `dry_run` (`dry_run="False"` مانع اعمال تغییر می‌شد) و نبود نگهبان `max_workers <= 0`؛ عبارت «تضمین می‌کند» در Q2.
- **منبع معتبر:** Python Data Model و Context Manager Protocol (`with`).
- **اصلاح انجام‌شده:** اعمال `_require_bool`، اعتبارسنجی `max_workers > 0` + assertها و تعدیل Q2.
- **تست مرتبط:** `test_phase8c1_automation_core_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** شبیه‌ساز محلی بدون Netmiko/Nornir/SSH واقعی؛ بازبینی نویسنده (نه مستقل).

## بازبینی فنی فاز ۱۱ (2026-11-27 — پاسخ به `AGENT-HANDOFF-fa.md` @ `f3a809393e`؛ `reviewed.9`)
- **ایرادها:** (۱) نسبت دادن غیرمشروط `dry_run` به فریم‌ورک Nornir و مدل‌سازی گمراه‌کننده `dry_run` داخل `MockNetmikoConnection.send_config_set()`؛ در واقعیت Nornir فقط پرچم `task.is_dry_run()` را منتشر می‌کند و ایمنی/Diff واقعی به پلاگین یا کد وظیفه وابسته است (`nornir_napalm` / `napalm_configure` پشتیبانی بومی دارد، اما `nornir_netmiko` / `netmiko_send_config` پشتیبانی بومی ندارد)؛ (۲) نبود تصریح تطابق `nr.filter(role="pilot")` با کلید `data.role` در `SimpleInventory` (در برابر عضویت گروهی `F(groups__contains="pilot")`)؛ (۳) ادعاهای زمانی قطعی موازی‌سازی («زیر ۱ دقیقه»، «ظرف ۵ ثانیه کل ۵۰۰ دستگاه») بدون قید سربار SSH/AAA/RTT/CPU؛ (۴) تعمیم `save_config()` به همه پلتفرم‌ها (برخلاف سیستم‌های Commit-based مانند IOS-XR/JunOS)؛ (۵) تفکیک‌نکردن لایه‌های تایم‌اوت Netmiko (`conn_timeout`, `auth_timeout`, `banner_timeout`, `read_timeout`, `read_timeout_override`).
- **منابع معتبر:** `AGENT-HANDOFF-fa.md` (`arena/ab96c97c-fam` @ `f3a809393e`)، [مستندات رسمی Nornir](https://nornir.readthedocs.io/) و [مستندات API `netmiko.base_connection`](https://ktbyers.github.io/netmiko/docs/netmiko/base_connection.html).
- **اصلاح انجام‌شده:** بازنویسی `auto_03_lab.py` با حذف `dry_run` از `MockNetmikoConnection.send_config_set`، پیاده‌سازی نگهبان صریح `task_honors_dry_run` (رد fail-closed هنگام نبود پشتیبانی `dry_run`)، مدل‌سازی اسکیمای `SimpleInventory` (`data.role`) و مرز پلتفرمی `save_config()` (IOS-XE در برابر `NotImplementedError` در IOS-XR)؛ به‌روزرسانی کامل بخش‌های ۲، ۵، ۶ (SVG)، ۸، ۹، ۱۰، ۱۱، ۱۲، ۱۳، ۱۴، واژه‌نامه، پرسش‌های ۳، ۶، ۷ و ۱۱ و نمونه مرجع Nornir در `auto_03.json` همراه با تطابق دقیق بایتی ۶۴/۶۴ HTML.
- **تست مرتبط:** `test_phase11_handoff_f3a80939_ccde18_and_auto03_remediation` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی)؛ آزمایشگاه شبیه‌ساز محلی بدون Netmiko/Nornir/SSH واقعی است و برای بازبینی مستقل Agent 2 آماده است.

