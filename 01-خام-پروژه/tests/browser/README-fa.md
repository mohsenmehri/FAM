# آزمون Chromium واقعی

این آزمون با دیتابیس موقت و Flask در حالت TESTING، HTTP محلی و cookie بدون Secure اجرا می‌شود؛ جای آزمون production با nginx و HTTPS نیست. دو asset ورود که nginx در production ارائه می‌دهد توسط harness ارائه می‌شوند. Chromium سازگار و کتابخانه‌های سیستم آن باید از قبل نصب باشند. در محیط مجاز با اینترنت، برای فراهم کردن وابستگی Node خارج از پروژه:

```bash
mkdir -p /tmp/fam-browser-deps
npm install --prefix /tmp/fam-browser-deps puppeteer-core@24.15.0
export NODE_PATH=/tmp/fam-browser-deps/node_modules
export FAM_CHROMIUM_PATH="$(command -v chromium)"
.venv/bin/python '01-خام-پروژه/tests/browser/run_browser_test.py'
```

ممکن است نام مرورگر شما `chromium-browser` یا `google-chrome` باشد؛ مسیر واقعی را قرار دهید. بدون Chromium یا کتابخانه‌های آن، این تست اجرا نمی‌شود. مجوزهای مرورگر، CSP و محدودیت‌های file:// ممکن است در سیستم‌های دیگر فرق کنند. خروجی آفلاین شامل هر ۱۲۷ درس فعال و شبیه‌ساز آموزشی CLI است و همگام‌سازی سرور ندارد.
