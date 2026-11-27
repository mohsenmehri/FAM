# شواهد بازبینی معنایی `ccie_auto` — CCIE Automation (DevNet Expert)

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و شبیه‌ساز `01-خام-پروژه/academy-labs/agent3/ccie_auto_lab.py` بررسی و اجرا شدند.
- واژه نامرتبط نسخه قدیمی کامل اصلاح و در `legacyAuditFixes` ثبت شد.
- هیچ سرور واقعی Cisco NSO یا GitLab/Kubernetes متصل نشده است.

## بازبینی فنی و معنایی مرحله ۲ (۲۰۲۶-۱۱-۲۷)

- وضعیت بازبینی: همچنان **بازبینی نویسنده (author-agent-self-review-not-independent)** است و **بازبینی مستقل انسانی انجام نشده است**.
- مسئله ۱: نقل‌قول واژه اسپانیایی `diferencia` در متن دانشجویی بخش ۱۲.
- مسئله ۲: هم‌راستاسازی دقیق عنوان آزمون با تغییر رسمی سیسکو از ۳ فوریه ۲۰۲۶ (`350-901 v2.0 AUTOCOR` / `CCIE Automation`). منبع: Cisco Learning Network.
- آزمون مرتبط: `test_agent3_content.py` (`FORBIDDEN_LEGACY_TYPOS` + `test_technical_audit_regressions`).

## بازبینی فنی فاز ۸B (2026-11-27)
- **ایراد:** نبود `_require_bool` روی `dry_run` (`dry_run="False"` مانع commit می‌شد)، باگ `fastmap_clean` در سناریوی چندسرویسه و «تضمین می‌کند» در Q5.
- **منبع معتبر:** Cisco NSO FASTMAP Service Lifecycle و Python Data Model.
- **اصلاح انجام‌شده:** اعمال `_require_bool`، اصلاح `fastmap_clean` به‌ازای VRF همان سرویس + assertها و تعدیل Q5.
- **تست مرتبط:** `test_phase8b_ccie_and_remaining_specialist_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** مدل محلی بدون NSO/pyATS زنده؛ بازبینی نویسنده (نه مستقل).
