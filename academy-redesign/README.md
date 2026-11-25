# FAM Academy — بازطراحی کامل (Live Topology)

نسخهٔ مستقل و آمادهٔ اجرا: **سایت عمومی + داشبورد دانشجو**، تماماً فارسی RTL، بدون هیچ فریمورک یا مرحلهٔ build.

## اجرا

کافی است `index.html` را در مرورگر باز کنید — یا یک سرور محلی بگیرید:

```bash
python3 -m http.server 8080
# سپس http://localhost:8080/index.html
```

## فایل‌ها

| فایل | نقش |
|---|---|
| `index.html` | سایت عمومی: هیرو تولوژی زنده، مسیر یادگیری، آزمایشگاه، CTA |
| `dashboard.html` | داشبورد دانشجو: خانه / دوره‌ها / آزمایشگاه / پیشرفت |
| `styles.css` | کل سیستم طراحی (تم تاریک + ریسپانسیو + RTL) |
| `app.js` | تعاملات: منو، انیمیشن ورود، شمارنده‌ها، تایپ ترمینال، سوییچ ویوها |
| `lessons.html` | کلاس‌های درسی: درخت ۷ دانشکده + نمایش درس با ۱۱ بخش استاندارد |
| `lesson.css` | سیستم طراحی صفحهٔ درس (کارت‌ها، CLI، جدول، آزمون، نمودار) |
| `lessons.js` | رندر درخت/درس/آزمون + پیشرفت در localStorage (`fam-lessons-v1`) |
| `curriculum.js` | دادهٔ کامل دروس: ۷ دانشکده، ۳۸ درس، ۱۱۸ سؤال، ۷۸ آزمایشگاه، ۶ نمودار SVG |

## دروس (curriculum)

مسیر کامل از **ارزیابی و مبانی (f0)** تا **CCDE (f6)** طبق طرح جامع آکادمی:

**Cisco Master Roadmap (نقشهٔ نهایی، ۸ مرحله):**
Networking Fundamentals → Cisco Entry/CCST → CCNA → CCNP Specialization → Advanced Technologies → CCIE → CCDE → Principal Network Architect

| # | دانشکده | عنوان | درس |
|---|---|---|---|
| ۰ | f0 | ارزیابی و مبانی | ۴ |
| ۱ | fnd | Network Engineering Foundations | ۴ |
| ۲ | ccst | Cisco Entry / CCST | ۳ |
| ۳ | f1 | CCNA 200-301 | ۸ |
| ۴ | f2 | مسیریابی/سوئیچینگ پیشرفته | ۶ |
| ۵ | f3 | Enterprise (ENCOR) | ۶ |
| ۶ | f4 | هشت مسیر تخصصی (Enterprise·Security·DC·SP·Wireless·Collaboration·Automation·Cyber) | ۱۱ |
| ۷ | f5 | CCIE | ۵ |
| ۸ | f6 | CCDE + Principal Network Architect | ۴ |

جمع: **۵۱ درس · ۱۶۴ سؤال · ۱۴۰ آزمایشگاه**

هر درس: هدف ← پیش‌نیاز ← مفهوم ← پروتکل ← دستورات ← نمودار ← آزمایشگاه ← عیب‌یابی ← تمرین ← آزمون ← یادداشت (+سوالات متداول).

## نکته

- فونت‌ها از Google Fonts لود می‌شوند (Vazirmatn + JetBrains Mono)؛ بدون اینترنت هم کار می‌کند با فونت سیستم.
- صفحهٔ درس `lessons.html` را با `#/l/<id>` (مثل `lessons.html#/l/f0-w1`) مستقیم باز کنید.
