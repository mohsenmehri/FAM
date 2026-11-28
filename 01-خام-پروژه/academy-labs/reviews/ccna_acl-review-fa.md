# شواهد بازبینی معنایی `ccna_acl` — CCNA (امنیت شبکه): چشم‌انداز تهدیدات، AAA (TACACS+ و RADIUS)، VPN مقدماتی و Hardening تجهیزات

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (Agent 3، پس از انتقال از سهم سابق ایجنت اول در `641d02ee73e0fa86b0972dc1f85474e84abef288`)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، نمودار SVG و کد `01-خام-پروژه/academy-labs/agent3/ccna_acl_lab.py` تدوین، بازبینی و اجرا شدند.
- هیچ تجهیز واقعی سیسکو (سوئیچ/روتر/هایپروایزر/سرور زنده) در این محیط اجرا نشده است؛ آزمایشگاه یک شبیه‌ساز محلی درون‌حافظه‌ای Python 3 و بخش دوم سناریوی مرجع اجرا نشده است.

## یافته‌ها و اصلاحات بازبینی فنی فاز ۱۲B (2026-11-27)

- تصریح رفتار دقیق `local` fallback (صرفاً هنگام عدم دسترسی سرور AAA، نه هنگام REJECT رمز اشتباه).
- تکمیل مقایسه TACACS+ (RFC 8907) و RADIUS (UDP 1812/1813 + RadSec)، ممیزی Type 0/7/5/8/9 و جزئیات IKEv2/ESP/AH.
- گسترش از ۳ بخش/۳ سؤال قدیمی به ۱۴ بخش/۱۵ واژه/۱۲ پرسش همراه با `ccna_acl_lab.py` بدون import پرچم‌دار.

### منابع معتبر بررسی‌شده
- https://www.rfc-editor.org/rfc/rfc8907
- https://www.rfc-editor.org/rfc/rfc2865
- https://www.rfc-editor.org/rfc/rfc7296
- https://www.cisco.com/c/en/us/support/docs/security-vpn/terminal-access-controller-access-control-system-tacacs-/10384-security.html

### آزمون و پوشش
- تست مرتبط: `test_phase12b_transferred_ccna_services_security_batch` و تست‌های پایه در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** خودبازبینی نویسنده (نه بازبینی مستقل انسانی) و منتظر بازبینی/ادغام انتخابی توسط Agent 2.
