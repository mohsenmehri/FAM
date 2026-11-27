# شواهد بازبینی معنایی `ccde_04` — طراحی شبکه‌های فوق‌بزرگ و AI/ML Fabric

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و مدل‌ساز `01-خام-پروژه/academy-labs/agent3/ccde_04_lab.py` بررسی و اجرا شدند.
- خطای تایپی نسخه قدیمی اصلاح و ثبت شد؛ هیچ کلاستر GPU واقعی متصل نیست.

## بازبینی فنی فاز ۶ (2026-11-27 — رفع کامل یافته‌های `agent-intake-837fad64-fa.md` روی `ccde_18` و ممیزی مرزی درس‌های باقی‌مانده)
- **ایراد:** نبود اعتبارسنجی `switch_radix`، `oversubscription <= 0`، سقف `pods <= switch_radix` در ۵-Stage Clos، و پذیرش بی‌صدا مقادیر نامعتبر `load_balancing` در `audit_ai_ml_fabric`.
- **منبع معتبر:** معماری Clos Fabric (3-Stage/5-Stage Radix Math) و طراحی RoCEv2 AI/ML Ethernet Fabric (ECN/PFC + Adaptive Load Balancing).
- **اصلاح انجام‌شده:** افزودن اعتبارسنجی کامل مرزی و لیست مجاز صریح `ADAPTIVE_AI_LB_MODES` در `ccde_04_lab.py` همراه با assertها و تست‌های منفی.
- **تست مرتبط:** `test_phase6_ccde_18_remediation_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل‌ساز ریاضی محلی بدون فابریک سوئیچ یا کلاستر GPU واقعی؛ بازبینی نویسنده (نه مستقل).
