# شواهد بازبینی معنایی `spec_sec_ise` — معماری خوشه‌ای Cisco ISE، TACACS+، Posture و pxGrid

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/spec_sec_ise_lab.py` بررسی و اجرا شدند.
- هیچ سرور Cisco ISE یا فایروال واقعی متصل نشده است.

## بازبینی فنی و معنایی مرحله ۲ (۲۰۲۶-۱۱-۲۷)

- وضعیت بازبینی: همچنان **بازبینی نویسنده (author-agent-self-review-not-independent)** است و **بازبینی مستقل انسانی انجام نشده است**.
- مسئله: ذکر حداکثر ۵ دقیقه اختلاف ساعت Kerberos در پرسش ۱۱ بدون تصریح اینکه مقدار پیش‌فرض سیاست Active Directory (`MaxClockSkew`) است.
- منبع: Microsoft Active Directory Kerberos Policy (`Maximum tolerance for computer clock synchronization`) و Cisco ISE 3.3 Admin Guide.
- آزمون مرتبط: `test_agent3_content.py` (`test_technical_audit_regressions`).

## بازبینی فنی فاز ۸B (2026-11-27)
- **ایراد:** نبود `_require_bool` روی `av_updated`/`os_patched` (`av_updated="False"` وضعیت Compliant می‌داد) و آسیب‌پذیری فاصله ابتدایی (`" reload"`) در `tacacs_authorize_command`.
- **منبع معتبر:** Cisco ISE Posture/CoA/pxGrid و TACACS+ Command Authorization.
- **اصلاح انجام‌شده:** اعمال `_require_bool` و نرمال‌سازی `.strip().lower()` در `tacacs_authorize_command`.
- **تست مرتبط:** `test_phase8b_ccie_and_remaining_specialist_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون ISE زنده؛ بازبینی نویسنده (نه مستقل).
