# ممیزی پوشش اهداف CCNA 200-301 v1.1 — ماتریس جامع ۹۸ ردیف

**تاریخ:** ۲۰۲۶-۱۱-۲۰. **مبنا:** [Cisco CCNA 200-301 v1.1 Exam Topics](https://learningcontent.cisco.com/documents/marketing/exam-topics/200-301-CCNA-v1.1.pdf). **شاخه:** `arena/0085ab04-fam`.

## ۱. این سند چه چیزی را اثبات می‌کند و چه چیزی را نه

این سند **فهرست کامل اهداف رسمی** (۱ + ۵ حوزه، ۹۸ ردیف) و **ارجاع هر ردیف به یک درس و بخش مشخص** را یک‌جا جمع می‌کند. ستون «شاهد» فقط می‌گوید کجا دربارهٔ آن هدف نوشته شده است.

این سند **اثبات نمی‌کند** که:

- همهٔ محتوا از نظر فنی درست یا به‌روز است: بازبینی هدفمند/کاملِ محتوایی برای بخشی از درس‌ها انجام شده، اما همهٔ ۹۸ هدف/۶۹ درس ممیزی نشده‌اند؛ بازبینی جاری به معنی تأیید نسخه‌ای یا پلتفرمی نیست.
- همهٔ هدف‌ها «پوشش داده‌شده» هستند: ۷۱ هدف غیرعملی در سطح متن کافی ارزیابی شده‌اند؛ ۲۷ هدف عملی نهایی‌نشده‌اند و هیچ‌کدام اجرا و تأیید نشده‌اند. این تفکیک متن مفهومی از Verification عملی را حفظ می‌کند.
- فرمان‌ها روی IOS واقعی اجرا شده‌اند (**هیچ فرمان IOS اجرا نشده**؛ مدل/Image/نسخهٔ IOS یا WLC برای اجرا انتخاب نشده). آزمون Linux namespace برای Underlay در کاربرگ AUT-03 جداگانه انجام شد؛ VXLAN پشتیبانی نشد.
- سناریوها در PNETLab اجرا شده‌اند (**هیچ لبی اجرا نشده**؛ هیچ خروجی ثبت‌شده و واقعی وجود ندارد).
- درس‌ها در اپلیکیشن/کاتالوگ Academy ثبت شده‌اند (هیچ UI یا کاتالوگی تغییر نکرده).
- کیفیت آموزشی، سطح دشواری، یا آمادگی آزمون تأیید شده است (هیچ آزمون واقعی یا ارزیابی دانشجو انجام نشده).

در ممیزی پیشین فقط درس ۰.۱ تأیید محتوایی انسانی داشت. اکنون **۷۱ هدف غیرعملی از ۹۸ ردیف** در سطح متن کافی ارزیابی شده‌اند: `1.1.a–h`، `1.2.a–f`، `1.3.a–b`، `1.4`، `1.5`، `1.7`، `1.9.a–d`، `1.11.a–d`، `1.12`، `1.13.a–d`، `2.5.a–d`، `2.6–2.9`، `3.1.a–g`، `3.2.a–c`، `3.5`، `4.3–4.5`، `4.7`، `4.9`، `5.1`، `5.2`، `5.4`، `5.5`، `5.8`، `5.9`، `6.1`، `6.2`، `6.3`، `6.3.a–b`، `6.4`، `6.5`، `6.6` و `6.7`. این جمع شامل پنج هدف IP Services پیشین، ۱۵ هدف از بازبینی پیشین، ۲۶ هدف Network Fundamentals، ۲۰ هدف در IC-01/SEC/AUT و پنج هدف این ادامه در NA-07/IC-06 است. ۲۷ هدف عملی همچنان نهایی‌نشده و **۰/۲۷ اجرا و Verification** شده‌اند. ارزیابی متنی، آزمون دانشجو یا تأیید نسخه/پلتفرم نیست.

## ۲. آمار تولید

| گروه | شناسه‌ها | تعداد درس | نمودار SVG | وضعیت |
|---|---|---|---|---|
| مرحلهٔ صفر | ۰.۱–۰.۱۰ | ۱۰ | ۱ | ۰.۱ تأیید محتوایی؛ بقیه پیش‌نویس |
| Network Fundamentals (حوزهٔ ۱) | NF-01–NF-16 | ۱۶ | ۹ | پیش‌نویس |
| Network Access (حوزهٔ ۲) | NA-01–NA-09 | ۹ | ۸ | پیش‌نویس |
| IP Connectivity (حوزهٔ ۳) | IC-01–IC-06 | ۶ | ۶ | پیش‌نویس |
| IP Services (حوزهٔ ۴) | IS-01–IS-09 | ۹ | ۹ | پیش‌نویس |
| Security Fundamentals (حوزهٔ ۵) | SEC-01–SEC-10 | ۱۰ | ۱۰ | پیش‌نویس |
| Automation and Programmability (حوزهٔ ۶) | AUT-01–AUT-09 | ۹ | ۹ | پیش‌نویس |
| **جمع** | — | **۶۹** | **۵۲** | **همه اجرا‌نشده** |

**یادداشت شمارش تصویر:** وجود SVG با «داشتن تصویر در درس» یکی نیست. در وضعیت فعلی ۵۲ فایل SVG در `docs/academy-images/` هست و هر ۵۲ فایل از یک درس ارجاع داده می‌شوند (۰ فایل بی‌استفاده، ۰ ارجاع مفقود در سطح درس‌ها). اما ۱۷ درس هیچ تصویری ندارند: در حوزهٔ CCNA، NA-03 و NF-01، NF-05، NF-09، NF-11، NF-13، NF-14، NF-16؛ و در مرحلهٔ صفر، ۰.۱ تا ۰.۷ و ۰.۹ و ۰.۱۰ (۰.۸ تصویر دارد). بنابراین ادعای «همهٔ درس‌ها تصویر دارند» درست نیست؛ ادعای درست این است که هر SVG موجود، استفاده می‌شود.

## ۲.۱ وضعیت کفایت به تفکیک نوع هدف

ماتریس ۹۸ ردیفی پیش‌تر وضعیت «باز / اجرا نشده» را به‌جای تفکیک نوع ارزیابی به‌کار می‌برد. شمارش قبلی ۶۱/۳۷ از افعال رسمی قابل‌بازتولید نبود: ۳۵ ردیف حوزهٔ ۱ دسته‌بندی ردیفی نداشتند و عملاً در شمار عملی آمده بودند؛ در حوزه‌های ۲–۶ نیز 2.1.b با وجود فعل `Configure and verify` تحلیلی برچسب خورده بود و سه هدف مفهومیِ دارای کاربرگ (2.8، 4.7 و 5.8) به‌اشتباه عملی شمرده شده بودند. بازشماری زیر فقط بر اساس فعل رسمی هر ردیف است؛ ستون پایانی ماتریس جداگانه حضور طرح تمرین و اجرای واقعی را نشان می‌دهد.

| وضعیت | تعریف | تعداد | نمونه |
|---|---|---|---|
| **کافی در سطح Objective توضیحی/توصیفی** | کفایت متن با بازبینی ردیفی تأیید شده؛ برای فعل‌های عملی، اجرای واقعی و Verification همچنان لازم است | **۷۱** | 1.1.a–h، 1.2.a–f، 1.3.a–b، 1.4، 1.5، 1.7، 1.9.a–d، 1.11.a–d، 1.12، 1.13.a–d، 2.5.a–d، 2.6–2.9، 3.1.a–g، 3.2.a–c، 3.5، 4.3–4.5، 4.7، 4.9، 5.1، 5.2، 5.4، 5.5، 5.8، 5.9، 6.1–6.7 (شامل 6.3.a–b؛ همه با فعل غیرعملی) |
| **نیازمند اعتبارسنجی عملی** | فعل رسمی `Configure and verify`، `Configure` یا `Verify` است؛ هیچ اجرای واقعی ثبت نشده | **۲۷** | 1.6، 1.8، 2.1.a–c، 5.6 |
| **نیازمند بازبینی محتوایی/تحلیلی** | سایر فعل‌های رسمی؛ اجرای IOS/PNETLab شرط ذاتی این فعل‌ها نیست؛ همه در سطح متن کافی ارزیابی شده‌اند | **۷۱** | شامل 2.5.a–d و 3.5 که در آخرین ممیزی کامل بررسی شدند |
| **جمع هدف‌ها** | — | **۹۸** | — |
| **کفایت ناکافی / صرفاً اشاره‌شده / فاقد شاهد** | شمارش مستقلِ کفایت برای هر ردیف کامل نشده؛ مقدار **نامعلوم** است و نباید صفر تعبیر شود | — | ارزیابی ردیف‌به‌ردیف هنوز لازم است |

**این اعداد نوع ارزیابی لازم را از کفایت جدا می‌کنند.** ۲۷ هدف عملی از ۲۵ فعل `Configure and verify`، یک `Configure` و یک `Verify` تشکیل شده‌اند؛ هیچ‌کدام اجرا و تأیید نشده‌اند. هر ۷۱ هدف با فعل‌های دیگر اکنون در سطح متن کافی ارزیابی شده‌اند؛ هیچ‌کدام از این برچسب‌ها به هدف عملی یا آزمون دانشجو تعمیم داده نمی‌شود.

**۲۷ هدف از ۹۸ هنوز نهایی نشده‌اند؛ هر ۲۷ مورد عملی‌اند و به اجرای واقعی و Verification نیاز دارند.** ارجاع به درس یا نمونهٔ طراحی‌شده به‌تنهایی شاهد اجرای هدف نیست؛ هیچ اجرای IOS/PNETLab برای این اهداف ثبت نشده است. بازشماری کدهای ردیف (۹۸ کد یکتا) وضعیت ۷۱/۲۷ را تأیید می‌کند. جست‌وجوی لفظیِ زیررشتهٔ `باز /` در ستون وضعیت ۲۶ ردیف را می‌یابد؛ `4.6` با عبارت «کفایت عملی باز** /» از این تطبیق جا می‌افتد. ردیف `5.6` نیز با پیشوند «متن/طرح بازبینی شد» آغاز می‌شود، اما عبارت «هدف عملی باز /» را در خود دارد و در ۲۶ ردیف لفظاً شمرده می‌شود. هر دو، بر اساس فعل رسمی، در ۲۷ هدف عملی باز منظورند.

### ۲.۱.۱. وضعیت کفایت ردیفی — ممیزی هدفمندِ این نوبت

**معیار:** «کافی» یعنی محتوای درس، همهٔ اجزای فعل/موضوع همان Objective را به‌درستی توضیح می‌دهد و شاهد آموزشی/مرزهای لازم را دارد؛ «ناکافی» یعنی بخش الزامی جاافتاده یا خطای مؤثر دارد؛ «جزئی» یعنی تنها بخشی از Objective پوشش دارد؛ «باز» یعنی ارزیابی مستقل هنوز انجام نشده است. برای اهداف Configure/Verify، کفایت متنِ آموزش و اجرای واقعی دو ستون جدا هستند؛ تأیید نهاییِ اجرای آن‌ها به Image/نسخه و شواهد واقعی نیاز دارد.

| وضعیت ارزیابی محتوا | تعداد هدف | ردیف‌ها/توضیح |
|---|---:|---|
| **کافی در سطح متنِ Objectiveهای غیرعملی** | **۷۱** | پنج هدف IP Services، ۱۵ هدف از بازبینی قبلی، ۲۶ هدف Network Fundamentals، ۲۰ هدف IC-01/SEC/AUT و پنج هدف NA-07/IC-06؛ فهرست دقیق در ماتریس. برای هدف‌های Configure/Verify این برچسب جای اجرای واقعی را نمی‌گیرد. |
| **باز — اجرای نهایی هنوز انجام نشده** | **۲۷** | همهٔ ۲۷ هدف عملی هنوز اجرا/Verification نشده‌اند. متن طراحی‌شده به معنی تأیید هدف عملی نیست. |
| **کفایت طراحیِ هدف‌های عملی** | **۲۷/۲۷ نگاشت و بازبینی ۱۱جزئی؛ ۰/۲۷ اجراشده** | ۲۵۶✓+۳۶△+۰—+۵ N/A در ۲۹۷ خانهٔ متنی؛ △های باقیمانده عمدتاً Image/نسخه/Feature تأییدنشده‌اند. نگاشت/معیار قبولی هر Objective در [نقشهٔ تحویل](academy-ccna-practical-delivery-map-fa.md) است؛ طراحی متنی جای اجرای عملی نیست. |
| **اجرای واقعی IOS/PNETLab برای Objectiveهای عملی** | **۰ از ۲۷** | هیچ Objective عملی روی IOS/PNETLab اجرا/تأیید نشده است. در AUT-03 فقط Underlay محلی Linux آزموده شد؛ این هدف/Fabric Controller-based را Verify نمی‌کند. |

**پنج Objective که پیش‌تر در ممیزی IP Services در سطح متن کافی ارزیابی شدند:** `4.3`، `4.4`، `4.5`، `4.7` و `4.9`. برای آن‌ها نیز اجرا/تأیید پلتفرم ادعا نمی‌شود؛ جزئیات هر ردیف در ماتریس حوزهٔ ۴ آمده است.

### بازبینی محتوایی پیشین — ۱۵ Objective غیرعملی

در بازبینی پیشین ۱۲ درس `NF-03`، `NF-04`، `NF-06`، `NF-09`، `NA-08`، `NA-09`، `SEC-06`، `AUT-02`، `AUT-04`، `AUT-05`، `AUT-08` و `AUT-09` از ابتدا تا انتها بررسی شد. از آن بازبینی ۱۵ هدف غیرعملی به «کافی در سطح متن» ارتقا یافتند: `1.1.c–e`، `1.3.a–b`، `1.7`، `2.6–2.9` و `6.2`، `6.3.a–b`، `6.6`، `6.7`. Objective `5.6` در SEC-06 نیز از نظر متن/طرح بازبینی شد، اما چون فعل آن `Configure and verify` است، وضعیت کلی آن عملی/باز می‌ماند تا روی Image/نسخهٔ مشخص اجرا و Verify شود. هیچ GUI، WLC، IOS، کنترلر، API، PNETLab یا ابزار Automation در آن بازبینی اجرا نشد.

### بازبینی پیشین — ۲۶ Objective غیرعملی در Network Fundamentals

متن کامل ۱۲ درس `NF-01`، `NF-02`، `NF-05`، `NF-07`، `NF-08`، `NF-10`، `NF-11`، `NF-12`، `NF-13`، `NF-14`، `NF-15` و `NF-16` از ابتدا تا انتها از نظر ارتباط با هدف، درستی مفهومی، caveatهای نسخه/محصول و تمایز نمونه از اجرای واقعی بررسی شد. در نتیجه `1.1.a–b`، `1.1.f–h`، `1.2.a–f`، `1.4`، `1.5`، `1.9.a–d`، `1.11.a–d`، `1.12` و `1.13.a–d` (۲۶ ردیف غیرعملی) در سطح متن کافی ارزیابی شدند. طرح و متن آموزشی `1.6`، `1.8` و `1.10` نیز بازخوانی شدند، اما چون هدف‌ها عملی‌اند همچنان به اجرای واقعی و Verification نیاز دارند؛ هیچ IOS، Client OS، PNETLab، RF survey یا سخت‌افزاری در این ادامه اجرا/آزمایش نشد. در درس NF-07 برای صراحتِ تشخیص mismatch سرعت، توضیح و پرسش تکمیلی افزوده شد.

### ممیزی هدفمند پیشین — IC-01، Security و Automation — ۲۰۲۶-۱۱-۲۰

متن کامل IC-01 و بخش‌های مرتبط در شش درس SEC-01/02/04/05/08/09 و چهار درس AUT-01/03/06/07 از ابتدا تا انتها برای تطبیق هدف مربوط بررسی شد. ده Objective `3.1.a–g` و `3.2.a–c` در IC-01، شش Objective غیرعملی `5.1`، `5.2`، `5.4`، `5.5`، `5.8`، `5.9` و چهار Objective `6.1`، `6.3`، `6.4`، `6.5` در سطح متن کافی ارزیابی شدند. برای `6.3`، شاهد AUT-02 (مدل Controller-Based) در کنار AUT-03 (Underlay/Overlay/Fabric) در ماتریس آمده است. خروجی‌های IC-01، APIها، ابزارها و سناریوهای شبکه اجرا نشده‌اند. این ممیزی هدف‌محور را ممیزی جامع همهٔ ادعاهای هر درس به‌شمار نمی‌آوریم؛ در ادامهٔ بعدی NA-07 و IC-06 نیز از ابتدا تا انتها بازبینی شدند و هر پنج Objective مفهومیِ پیشین را در سطح متن کافی کردند.

### تکمیل ممیزی پنج Objective مفهومیِ باز — NA-07 و IC-06 — ۲۰۲۶-۱۱-۲۰

محتوای دو درس از ابتدا تا انتها با پنج عبارت هدف‌محور سرفصل v1.1 تطبیق داده شد. `2.5.a`: Bridge ID و انتخاب Root، Primary/Secondary به‌عنوان طرح Priority، و Root/Designated/Alternate/Backup با خروجی نمونه؛ `2.5.b`: نقش‌ها و سه State در Rapid PVST+/RSTP، شامل تفاوت Discarding با Listening/Blocking کلاسیک؛ `2.5.c`: PortFast روی Edge، اثر DHCP/گذار سریع و خطر لینک Switch-to-Switch؛ `2.5.d`: Root Guard، Loop Guard، BPDU Guard و دو رفتار BPDU Filter، Trigger/حالت حفاظتی و مسیر عیب‌یابی؛ `3.5`: هدف افزونگی First Hop، Virtual IP/MAC، HSRP Active/Standby، GLBP AVG/AVF و توازن بار، VRRP و محدودیت Tracking/Preempt/مسیر بالادست. هر پنج مورد در سطح متن کافی ارزیابی شدند؛ نمودارها/خروجی‌ها و کاربرگ‌های دو درس نمونهٔ طراحی‌اند و روی Switch/Router یا PNETLab اجرا نشده‌اند. جمع مفهومی اکنون **۷۱/۷۱ کافی متنی** و هدف‌های نهایی‌نشده **۲۷/۹۸ عملی، ۰/۲۷ اجرا/Verification** است.

## ۳. ماتریس جامع — حوزهٔ ۱

| کد | هدف رسمی | درس، بخش و شاهد | کفایت / نوع ارزیابی / اجرا |
|---|---|---|---|
| 1.1.a | Explain — routers | NF-01 §۲: نقش Router و مسیریابی بین شبکه‌های IP، با قید وابستگی مسیر به جدول/سیاست | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / Router واقعی اجرا نشده |
| 1.1.b | Explain — layer 2 and layer 3 switches | NF-01 §۲: تمایز Switching لایهٔ ۲ از قابلیت Routing لایهٔ ۳ و وابستگی به مدل/پیکربندی | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / تجهیز واقعی اجرا نشده |
| 1.1.c | Explain — next-generation firewalls and IPS | NF-04 §۱–۲: تفاوت Firewall/NGFW/IDS/IPS، حالت Inline/Monitor، Detection/Prevention و خطای مثبت/منفی | **کافی در سطح Objective توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / محصول واقعی اجرا نشده |
| 1.1.d | Explain — access points | NF-03 §۱–۳: Radio/Beacon، Client، Bridge/Tunnel و تمایز SSID/اتصال/سرویس | **کافی در سطح Objective توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / AP واقعی اجرا نشده |
| 1.1.e | Explain — controllers | NF-03 §۱–۳: مدیریت/Policy گروهی، CAPWAP و وابستگی مسیر داده و Fail Mode به معماری | **کافی در سطح Objective توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / WLC واقعی اجرا نشده |
| 1.1.f | Explain — endpoints | NF-01 §۲ و §۶: Endpoint، Client و امکان ارائهٔ سرویس توسط دستگاه انتهایی | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / Client واقعی آزموده نشده |
| 1.1.g | Explain — servers | NF-01 §۲ و §۶: Server به‌عنوان نرم‌افزار/میزبان سرویس؛ روشن‌بودن میزبان تضمین‌کنندهٔ پاسخ سرویس نیست | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / سرویس واقعی آزموده نشده |
| 1.1.h | Explain — PoE | NF-02 §۱–۶: PSE/PD، Detection، Physical Classification در برابر LLDP/CDP، استاندارد/کلاس و بودجهٔ توان؛ تمایز برق از داده | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / اندازه‌گیری PoE روی سخت‌افزار انجام نشده |
| 1.2.a | Describe — two-tier | NF-05 §۲: ادغام نقش Core و Distribution در مدل Collapsed Core و تفکیک نقش منطقی از تعداد دستگاه | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.2.b | Describe — three-tier | NF-05 §۲: نقش‌های Access، Distribution و Core و این‌که لایه‌ها الزاماً سه دستگاه منفرد نیستند | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.2.c | Describe — spine-leaf | NF-05 §۳: نقش Leaf/Spine، اتصال میزبان و مسیرهای افزونه با caveat ظرفیت و Routing | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.2.d | Describe — WAN | NF-05 §۴–۵: نقش WAN در اتصال جغرافیایی سایت‌ها و وابستگی دسترسی به طراحی/افزونگی | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.2.e | Describe — SOHO | NF-05 §۴: شبکهٔ دفتر کوچک/خانه و امکان ترکیب چند نقش در یک تجهیز؛ اندازه خطر را حذف نمی‌کند | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.2.f | Describe — on-premises and cloud | NF-05 §۴–۵: محل استقرار، مدل مسئولیت و وابستگی به سرویس/قرارداد | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.3.a | Compare — single-mode fiber, multimode fiber, copper | NF-06 §۱–۲: نوع سیگنال/Mode، کاربردهای نسبی و قیود کابل/ترنسیور/فاصله و سرعت | **کافی در سطح Objective توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / سنجش فیزیکی انجام نشده |
| 1.3.b | Compare — Ethernet shared media and point-to-point | NF-06 §۳ و §۷: رسانهٔ مشترک/Hub و برخورد در Half-duplex در برابر لینک سوئیچی P2P/Full-duplex | **کافی در سطح Objective توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / آزمایش فیزیکی انجام نشده |
| 1.4 | Identify — collisions, errors, mismatch duplex and/or speed | NF-07 §۱–۵: Collision/CRC/errors، تغییر شمارنده در زمان، و مقایسهٔ عملیاتی Speed/Duplex دو سمت | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / سخت‌افزار واقعی آزموده نشده |
| 1.5 | Compare — TCP and UDP | NF-08 §۲–۴: اتصال/بدون اتصال، ترتیب و قابلیت اتکا، کنترل جریان/ازدحام و نقش پروتکل کاربردی | **کافی در سطح متن مقایسه‌ای (بازبینی ۲۰۲۶-۱۱-۲۰)** / Packet Capture انجام نشده |
| 1.6 | Configure and verify — IPv4 addressing and subnetting | NF-09 §۱–۳ و NF-10 §۱–۵: محاسبهٔ Prefix، تنظیم دو رابط، Verification، آزمون و عیب‌یابی؛ طرح متنی بازبینی شد | باز / نیازمند IOS/Image و اجرای عملی با Verification / اجرا نشده |
| 1.7 | Describe — private IPv4 addressing | NF-09 §۳: سه بازهٔ RFC 1918، تمایز خصوصی/مستنداتی و نبود امنیت خودکار | **کافی در سطح Objective توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.8 | Configure and verify — IPv6 addressing and prefix | NF-11 §۱–۶ و NF-12 §۱–۶: نوع/Prefix، پیکربندی رابط، Link-Local، Route و Verification؛ طرح متنی بازبینی شد | باز / نیازمند IOS/Image و اجرای عملی با Verification / اجرا نشده |
| 1.9.a | Describe — unicast: global, unique local, link local | NF-11 §۲–۳: دامنه و مثال‌های Global Unicast، ULA و Link-Local؛ Prefix مستنداتی و محدودیت Route | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.9.b | Describe — anycast | NF-11 §۲: آدرس Unicast مشترک بین Interfaceها و انتخاب بر پایهٔ Routing/Policy، نه فاصلهٔ فیزیکی قطعی | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.9.c | Describe — multicast | NF-11 §۲–۳: بازهٔ `ff00::/8`، مثال‌های scope و تمایز از Broadcast IPv4 | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.9.d | Describe — modified EUI-64 | NF-11 §۴: درج `ff:fe` و معکوس‌کردن بیت U/L با محاسبهٔ نمونه؛ اشاره به روش‌های دیگر | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.10 | Verify — IP parameters for Windows, Mac OS, Linux | NF-13 §۱–۷: فرمان‌های Windows/macOS/Linux، Route و DNS؛ طرح مقایسهٔ سه Client بازبینی شد | باز / نیازمند اجرای Verify روی هر سه سیستم‌عامل واقعی / اجرا نشده |
| 1.11.a | Describe — nonoverlapping Wi-Fi channels | NF-14 §۲: مثال 1/6/11 فقط برای 2.4 GHz/20 MHz و با قید منطقه؛ هم‌کانالی در برابر تداخل مجاور | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** / RF واقعی اندازه‌گیری نشده |
| 1.11.b | Describe — SSID | NF-14 §۳: SSID به‌عنوان نام شبکه و عدم اثبات اتصال/اعتبار سرویس با دیدن آن | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.11.c | Describe — RF | NF-14 §۱–۲: تأثیر محیط، باند/کانال، RSSI/SNR و محدودیت سنجش کیفیت | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** / RF واقعی اندازه‌گیری نشده |
| 1.11.d | Describe — encryption | NF-14 §۳: نقش رمزنگاری WLAN و تمایز آن از احراز هویت، مجازسازی و حفاظت انتهابه‌انتها | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.12 | Explain — server virtualization, containers, VRFs | NF-16 §۱–۵: Hypervisor/VM، Container و Kernel مشترک، VRF و جدول‌های مسیر مجزا، محدودیت امنیت/منابع | **کافی در سطح متن توضیحی (بازبینی ۲۰۲۶-۱۱-۲۰)** / پلتفرم مجازی‌سازی اجرا نشده |
| 1.13.a | Describe — MAC learning and aging | NF-15 §۱–۲: یادگیری MAC مبدأ به‌ازای VLAN/پورت و Aging پویا با قید پلتفرم | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.13.b | Describe — frame switching | NF-15 §۱–۳: جست‌وجوی MAC مقصد در همان VLAN و هدایت Frame به پورت واجد شرایط | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.13.c | Describe — frame flooding | NF-15 §۲–۳: Unknown Unicast/Broadcast در VLAN مربوط، به‌جز ورودی و با caveat سیاست/پورت | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** |
| 1.13.d | Describe — MAC address table | NF-15 §۱ و §۴: MAC، VLAN، نوع مدخل و پورت؛ جداسازی از ARP و Routing Table | **کافی در سطح متن توصیفی (بازبینی ۲۰۲۶-۱۱-۲۰)** / خروجی واقعی Switch وجود ندارد |

## ۴. ماتریس جامع — حوزه‌های ۲ تا ۶


### ۴.1 — Network Access

| کد | فعل | هدف رسمی | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 2.1.a | Configure and verify | VLAN access ports (data and voice) | NA-01 §۱–۵: VLAN، Access Port، Trunk و Verification (داده)؛ NA-03 §۳–۵ صوت | باز / نیازمند اعتبارسنجی عملی / کاربرگ دو‌سوئیچی NA-01 / اجرا نشده |
| 2.1.b | Configure and verify | default VLAN | NA-01 §۳–۵: عضویت Gi0/3 بدون پیکربندی صریح در VLAN 1 و فرمان‌های Verification طراحی‌شده | باز / نیازمند اعتبارسنجی عملی / اجرا نشده |
| 2.1.c | Configure and verify | interVLAN connectivity | NA-04 §۲–۵: Router-on-a-Stick و Gateway | باز / نیازمند اعتبارسنجی عملی / کاربرگ VPCS و دو تجهیز پیشنهادی / اجرا نشده |
| 2.2.a | Configure and verify | trunk ports | NA-01 §۲–۵: Trunk در همان کاربرگ VLAN چندسوئیچی | باز / نیازمند اعتبارسنجی عملی / کاربرگ دو‌سوئیچی / اجرا نشده |
| 2.2.b | Configure and verify | 802.1Q | NA-01 §۲ و ۴: ساختار Tag و `encapsulation dot1q`؛ NA-02 تفصیل | باز / نیازمند اعتبارسنجی عملی / کاربرگ / اجرا نشده |
| 2.2.c | Configure and verify | native VLAN | NA-01 §۲، ۴–۵: Native VLAN 999 و خطای Mismatch؛ NA-02 تفصیل | باز / نیازمند اعتبارسنجی عملی / کاربرگ / اجرا نشده |
| 2.3 | Configure and verify | Layer 2 discovery protocols: Cisco Discovery Protocol and LLDP | NA-05 §۳–۵: فعال‌سازی و Neighbor CDP/LLDP | باز / نیازمند اعتبارسنجی عملی / کاربرگ دو سوئیچ پیشنهادی / اجرا نشده |
| 2.4 | Configure and verify | Layer 2/Layer 3 EtherChannel (LACP) | NA-06 §۲–۴: LACP لایهٔ ۲ و ۳ و وضعیت گروه | باز / نیازمند اعتبارسنجی عملی / دو سناریوی مستقل پیشنهادی / اجرا نشده |
| 2.5.a | Interpret | Rapid PVST+: root port, root bridge (primary/secondary), and other port names | NA-07 §۲–۳، §۶–۷: Bridge ID، انتخاب Root، Primary/Secondary به‌عنوان نقش طراحی، Root/Designated/Alternate/Backup و تفسیر خروجی نمونه | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / خروجی و لاب نمونه‌اند، اجرا نشده |
| 2.5.b | Interpret | Rapid PVST+: port states and roles | NA-07 §۳–۴، §۷: نقش‌های Root/Designated/Alternate/Backup و حالت‌های RSTPِ Discarding/Learning/Forwarding، تطبیق با خروجی | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / خروجی نمونه، اجرا نشده |
| 2.5.c | Interpret | Rapid PVST+: PortFast | NA-07 §۴، §۸–۹ و §۱۱: Edge Port، کاربرد روی Endpoint، خطر لینک Switch-to-Switch، BPDU و تفاوت با STP-off | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / پیکربندی/رفتار اجرا نشده |
| 2.5.d | Interpret | Rapid PVST+: root guard, loop guard, BPDU filter, BPDU guard | NA-07 §۸–۹ و §۱۱: Trigger، حالت Root/Loop-Inconsistent یا Err-Disable، دامنه/ریسک BPDU Filter و عیب‌یابی چهار محافظت | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / پیکربندی/رفتار اجرا نشده |
| 2.6 | Describe | Cisco Wireless Architectures and AP modes | NA-08 §۱: Autonomous/Cloud/Split-MAC و نقش/محدودیت Local، FlexConnect، Monitor، Sniffer، Rogue Detector، Bridge/Mesh و SE-Connect | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / WLC/AP واقعی اجرا نشده |
| 2.7 | Describe | physical infrastructure connections of WLAN components (AP, WLC, access/trunk ports, and LAG) | NA-08 §۲–۳: AP/WLC و Access/Trunk، Local/Central Switching، VLAN Mapping، LAG و وابستگی به مدل/نسخه | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / اتصال واقعی آزمایش نشده |
| 2.8 | Describe | network device management access (Telnet, SSH, HTTP, HTTPS, console, TACACS+/RADIUS, cloud managed) | NA-09 §۱–۴ و §۸: امنیت/Transport، پیش‌نیاز و محدودسازی SSH، Console، AAA و Cloud Managed | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / IOS/Cloud واقعی اجرا نشده |
| 2.9 | Interpret | wireless LAN GUI configuration: WLAN creation, security settings, QoS profiles, advanced settings | NA-09 §۵–۶: Profile/SSID، امنیت، VLAN Mapping، QoS، Advanced و فرم مفهومی تحلیلی؛ فیلدها نسخه‌وابسته‌اند | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / GUI واقعی باز نشده |

### ۴.2 — IP Connectivity

| کد | فعل | هدف رسمی | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 3.1.a | Interpret | routing protocol code | IC-01 §۱–۲ و §۷: کدهای `L`/`C`/`S`/`O`/`D`/`B`/`R` و تفسیر منبع Route در نمونهٔ جدول | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / خروجی‌ها نمونه‌اند؛ IOS اجرا نشده |
| 3.1.b | Interpret | prefix | IC-01 §۲ و §۷: Prefix شبکه در برابر طول/Mask، با نمونهٔ `/16` و `/24` | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.c | Interpret | network mask | IC-01 §۲ و §۷: Network Mask و Prefix Length و اثر آن بر محدودهٔ شبکه | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.d | Interpret | next hop | IC-01 §۲، §۷–۸: Next Hop، Interface خروجی و Resolve بازگشتی؛ فرمان‌های بررسی مسیر/Next Hop | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / فرمان‌ها نمونه، IOS اجرا نشده |
| 3.1.e | Interpret | administrative distance | IC-01 §۳، §۵A، §۷ و §۱۰: جدول AD و مقایسهٔ آن میان Routeهای کاندیدِ همان Prefix | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.f | Interpret | metric | IC-01 §۴–۵A و §۱۰: معنای Metric در OSPF/EIGRP/RIP و مقایسه فقط درون همان Protocol و Prefix | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.g | Interpret | gateway of last resort | IC-01 §۶–۷: Default Route، Gateway of Last Resort و وابستگی نمایش به نصب/Resolve مسیر | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / خروجی نمونه، اجرا نشده |
| 3.2.a | Determine | longest prefix match | IC-01 §۵B، §۷ و §۱۰: LPM میان Routeهای نصب‌شده؛ مثال `/24` از RIP در برابر `/16` از OSPF | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.2.b | Determine | administrative distance | IC-01 §۳، §۵A و §۱۰: AD میان منابع مسیر با Prefix یکسان؛ از LPM میان Prefixهای متفاوت جدا شده | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.2.c | Determine | routing protocol metric | IC-01 §۴–۵A و §۱۰: Metric کمتر درون یک Protocol برای Prefix یکسان؛ Metric پروتکل‌های مختلف قابل قیاس نیست | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.3.a | Configure and verify | IPv4 and IPv6 static default route | IC-02 بخش ۴، گام‌های ۳ و ۵: Default؛ بالادست فقط فرضی و اجرا‌نشده | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.3.b | Configure and verify | IPv4 and IPv6 static network route | IC-02 بخش ۴، گام‌های ۲ و ۵: Network Route و مسیر برگشت | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.3.c | Configure and verify | IPv4 and IPv6 static host route | IC-02 بخش ۴، گام‌های ۴ و ۵: Host Route؛ IPv6 خروجی نمونه نیز تکمیل شد | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.3.d | Configure and verify | IPv4 and IPv6 floating static route | IC-02 بخش ۴، گام ۶: Next Hop واقعی در توپولوژی افزوده‌شده، مسیر برگشت و AD مشروط | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.4.a | Configure and verify | single-area OSPFv2 neighbor adjacencies | IC-03 §۱–۵: تفکیک آدرس‌دهی از `network`، ۸ حالت Neighbor | باز / نیازمند اعتبارسنجی عملی / کاربرگ ۱۰ مرحله‌ای / اجرا نشده |
| 3.4.b | Configure and verify | single-area OSPFv2 point-to-point | IC-03 §۳ و ۵: لینک `/30` و نبود DR/BDR | باز / نیازمند اعتبارسنجی عملی / کاربرگ / اجرا نشده |
| 3.4.c | Configure and verify | single-area OSPFv2 broadcast (DR/BDR selection) | IC-04 §۱–۳: Priority، انتخابات و `FULL/DR` | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.4.d | Configure and verify | single-area OSPFv2 router ID | IC-03 §۴: ترتیب انتخاب Router ID و `router-id` دستی | باز / نیازمند اعتبارسنجی عملی / کاربرگ / اجرا نشده |
| 3.5 | Describe | purpose, functions and concepts of first hop redundancy protocols | IC-06 §۱–۴ و §۶: هدف FHRP، Virtual Gateway، HSRP Active/Standby، GLBP AVG/AVF و Load Balancing، VRRP و مرزهای Tracking/Preempt/Failover | **کافی در سطح متن توصیفی (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / فرمان‌ها و Failover نمونه‌اند؛ اجرا نشده |

### ۴.3 — IP Services

| کد | فعل | هدف رسمی | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 4.1 | Configure and verify | inside source NAT using static and pools | IS-01 §۱–۵: Static، Pool و PAT؛ در ACL انتخاب‌گر NAT، `deny` ترجمه را رد می‌کند نه خود Packet را؛ `show ip nat translations` | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 4.2 | Configure and verify | NTP operating in client and server mode | IS-02 §۱–۴: `ntp master`، `ntp server` و Stratum | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 4.3 | Explain | role of DHCP and DNS within the network | IS-03 §۱–۶ (بازبینی این نوبت): DORA/Lease/Options، Relay، Resolver/Cache/TTL، A/AAAA/CNAME/MX/PTR، تفکیک خطای DHCP/DNS/برنامه؛ RFC 2131/2132/1034/1035 | **کافی در سطح Objective توضیحی (۲۰۲۶-۱۱-۲۰)** / IOS و Server واقعی اجرا نشده |
| 4.4 | Explain | function of SNMP in network operations | IS-04 §۱–۵ (بازنویسی این نوبت): Manager/Agent/MIB/OID، عملیات، Poll/Trap/Inform، نسخه/امنیت، پورت‌ها، کاربرگ و Troubleshooting؛ منابع RFC 3411/3414/3416 | **کافی در سطح Objective توضیحی (ممیزی هدفمند ۲۰۲۶-۱۱-۲۰)** / IOS/NMS واقعی اجرا نشده؛ فرمان‌های نمونه نسخه‌محورند |
| 4.5 | Describe | syslog features, including facilities and severity levels | IS-05 §۱–۵ (بازنویسی این نوبت): Facility/PRI در برابر Severity، سطوح 0–7، Threshold، مقصدها/Buffer/Collector، Timestamp/NTP و محدودیت UDP؛ RFC 5424/5426 | **کافی در سطح Objective توضیحی (ممیزی هدفمند ۲۰۲۶-۱۱-۲۰)** / IOS/Collector واقعی اجرا نشده؛ فرمان‌های نمونه نسخه‌محورند |
| 4.6 | Configure and verify | DHCP client and relay | IS-06 §۱–۵ (بازبینی این نوبت): Gi0/1 Client و Gi0/0 Relay به Server در Subnet جدا؛ Scope/giaddr، مسیر برگشت، Verification جدا برای R1 و PC؛ نقص Helper و آزمون بازیابی | طرح متنی بازبینی شد؛ **کفایت عملی باز** / نیازمند اعتبارسنجی عملی با IOS/Server واقعی و اجرای لاب |
| 4.7 | Explain | QoS forwarding per-hop behavior: classification, marking, queuing, congestion, policing and shaping | IS-07 §۱–۹ + [کاربرگ QoS مستقل](academy-ccna-services-07-qos-lab-fa.md): PHB/Marking/Queue، Topology/IP، IOS XE MQC، LLQ/CBWFQ/Shaping، Verification/Fault | **کافی در سطح متن Objective توضیحی؛ طرح عملی کامل است؛ IOS XE/PNETLab/Traffic اجرا نشده** |
| 4.8 | Configure | network devices for remote access using SSH | IS-08 §۱–۴ (بازبینی هدفمند طرح پیکربندی/Verification این نوبت): RSA، کاربر محلی و `transport input ssh` | باز / نیازمند اعتبارسنجی عملی روی IOS واقعی / کاربرگ پیشنهادی / اجرا نشده |
| 4.9 | Describe | capabilities and functions of TFTP/FTP | IS-09 §۱–۶ (بازبینی این نوبت): TFTP/UDP 69 و TID، FTP Control/Data Active/Passive، احراز/رمزنگاری، FTPS/SCP/SFTP، Backup/Hash/خطر Merge؛ RFC 1350/959/2577/4217 | **کافی در سطح Objective توصیفی (۲۰۲۶-۱۱-۲۰)** / سناریوی فایل/IOS اجرا نشده |

### ۴.4 — Security Fundamentals

| کد | فعل | هدف رسمی | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 5.1 | Define | threats, vulnerabilities, exploits, mitigation techniques | SEC-01 §۱–۲، §۴ و §۷: تفکیک چهار مفهوم، مثال‌های تهدید/کاهش و جداسازی وجود ضعف از اثبات Exploit | **کافی در سطح متن تعریفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اسکن یا حملهٔ واقعی انجام نشده |
| 5.2 | Describe | user awareness, training, physical access control | SEC-02 §۱–۲، §۴ و §۷: اجزای برنامهٔ Awareness/آموزش و سنجش؛ کنترل‌های مانع/ورود/نظارت و حدود آن‌ها | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 5.3 | Configure and verify | device access control using local passwords | SEC-03 §۱–۴: Console، VTY و `enable secret` | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 5.4 | Describe | password management, complexity, alternatives: multifactor authentication, certificates, biometrics | SEC-04 §۱–۴ و §۶–۷: سیاست/طول/پیچیدگی، عوامل و MFA، گواهی و بیومتریک با مزایا و محدودیت‌ها | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / سرویس واقعی نصب نشده |
| 5.5 | Describe | IPsec remote access and site-to-site VPNs | SEC-05 §۱–۲ و §۵–۶: مقایسهٔ دو کاربرد IPsec، AH/ESP، IKE/SA، Modeها، Split/Full Tunnel و مرزهای Verification | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / تونل واقعی برقرار نشده |
| 5.6 | Configure and verify | access control lists | SEC-06 §۱–۱۱: Standard/Extended، Wildcard، ترتیب/جهت، DNS، شمارنده و ویرایش Named/Numbered؛ دامنهٔ سیاست روشن شد | متن/طرح بازبینی شد؛ **هدف عملی باز / نیازمند IOS واقعی و Verification** / کاربرگ طراحی‌شده، اجرا نشده |
| 5.7 | Configure and verify | Layer 2 security: DHCP snooping, dynamic ARP inspection, port security | SEC-07 §۲–۶: مکانیزم سه حمله، ترتیب راه‌اندازی، وابستگی DAI به Binding | باز / نیازمند اعتبارسنجی عملی / کاربرگ ۷ مرحله‌ای / اجرا نشده |
| 5.8 | Compare | authentication, authorization, accounting concepts | SEC-08 §۱–۵ و §۱۰: تمایز سه A، AAA محلی/متمرکز، RADIUS/TACACS+ و رفتار Method List/Fallback | **کافی در سطح متن مقایسه‌ای (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / AAA Server اجرا نشده |
| 5.9 | Describe | wireless security protocols WPA, WPA2, WPA3 | SEC-09 §۱، §۳ و §۵: WPA/WPA2/WPA3 Personal/Enterprise، TKIP/CCMP/SAE/PMF و محدودیت‌های WPS/SSID پنهان | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / AP/WLC اجرا نشده |
| 5.10 | Configure and verify | WLAN within GUI using WPA2 PSK | SEC-10 §۱–۵: مراحل GUI و PSK | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |

### ۴.5 — Automation and Programmability

| کد | فعل | هدف رسمی | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 6.1 | Explain | automation impacts on network management | AUT-01 §۱–۴ و §۶–۷: مقیاس/تکرارپذیری و Drift، نقش Source of Truth/Template/Orchestration، Idempotency، Pre/Post-check و Blast Radius؛ اعداد صرفاً فرض آموزشی‌اند | **کافی در سطح متن توضیحی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / ابزار اجرا یا اندازه‌گیری نشده |
| 6.2 | Compare | traditional networks with controller-based networking | AUT-02 §۱–۵ و §۸–۹: مدل توزیع‌شده/Controller، Abstraction، Effect of Programming و Fail Mode؛ مزایا با محدودیت | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / Controller واقعی اجرا نشده |
| 6.3 | Describe | controller-based, software defined architecture: overlay, underlay, fabric | AUT-02 §۱–۵ و §۸–۹؛ AUT-03 §۱–۸ و [کاربرگ تفصیلی](academy-ccna-automation-03-sdn-fabric-lab-fa.md): Controller/Control/Data Plane، Underlay/Overlay, VNI/VXLAN/MTU و حد واقعی Lab | **کافی در سطح متن؛ Underlay Linux در namespace آزموده شد؛ VXLAN با `Unknown device type` رد شد؛ Controller/Fabric اجرا نشده** |
| 6.3.a | Describe | separation of control plane and data plane | AUT-04 §۱–۶: نقش‌ها، تفکیک درون‌دستگاهی، State/Fail Mode و مرزهای محصول؛ In-band تعریف شده است | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / Controller/IOS اجرا نشده |
| 6.3.b | Describe | northbound and southbound APIs | AUT-05 §۱–۶: جهت از دید Controller، REST/NETCONF/RESTCONF/YANG و Endpoint/Capabilityهای نسخه‌وابسته | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / API واقعی فراخوانی نشده |
| 6.4 | Explain | AI (generative and predictive) and machine learning in network operations | AUT-06 §۱–۷ و §۹: AI/ML، Generative/Predictive، الگوهای یادگیری، کاربرد شبکه، کیفیت/Drift داده، معیارها و Explainability | **کافی در سطح متن توضیحی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / مدل یا دادهٔ واقعی استفاده نشده |
| 6.5 | Describe | REST-based API characteristics: authentication types, CRUD, HTTP verbs, data encoding | AUT-07 §۱–۵ و §۸: قیود REST، Auth Basic/Bearer/API Key/OAuth، CRUD و semantics افعال HTTP، Status Codes و JSON/XML/YAML/URL encoding | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / API واقعی فراخوانی نشده |
| 6.6 | Recognize | capabilities of configuration management mechanisms such as Ansible and Terraform | AUT-08 §۱–۷: Ansible Module/Idempotency در برابر Terraform State/Plan/Drift؛ امکان ترکیب و مالکیت Resource؛ نسخه‌وابستگی روشن | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / هیچ ابزار اجرا نشده |
| 6.7 | Recognize | components of JSON-encoded data | AUT-09 §۱–۷: شش نوع مقدار، Object/Array تودرتو، JSONPath، `null` در برابر کلید غایب/`""`/`0`/`false` و Parsing دفاعی | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)** / API واقعی Parse نشده |

## ۵. کار باقی‌مانده (به ترتیب اولویت)

| اولویت | کار | معیار پایان |
|---|---|---|
| ۱ | بازبینی تخصصی محتوای ۶۹ درس | هر درس توسط یک بازبین فنی تأیید یا اصلاح شود |
| ۲ | انتخاب و تثبیت نسخهٔ IOS، ایمیج PNETLab و نسخهٔ WLC | نسخه‌ها در سند نسخه‌بندی ثبت شوند |
| ۳ | اجرای مرحله‌ای کاربرگ‌ها در PNETLab / سخت‌افزار | خروجی واقعی و ثبت خطاها برای هر درس |
| ۴ | تکمیل اجرای ۲۷ هدف عملی | برای هر هدف، انتخاب Image/نسخهٔ مناسب، اجرای واقعی و Verification؛ هر ۷۱ هدف غیرعملی در سطح متن کافی ارزیابی شده‌اند |
| ۵ | یکسان‌سازی ساختار و عمق درس‌ها | اختلاف عمق فعلی (۴۶۸ تا ۲٬۴۱۵ واژه) کاهش یابد |
| ۶ | ورود درس‌ها به کاتالوگ و UI Academy | فقط پس از تأیید مراحل ۱–۵ |

## ۶. محدودیت‌های ثبت‌شده

- نمودارها با XML Parser و رندر محلی PDF/PNG بررسی شدند؛ Chromium سندباکس اجرا نشد و صحت بصری در همهٔ مرورگرها تأیید نشده است.
- هیچ PNETLab، IOS، WLC، سرور AAA، RADIUS، Controller/API، Ansible، Terraform یا مدل هوش مصنوعی اجرا نشده است. تنها آزمون شبکه‌ای این نوبت Linux namespace Underlay بود: `iproute2 6.1.0`، Kernel `6.1.158+`، Ping دوطرفه موفق `2/2`؛ ساخت VXLAN با `Error: Unknown device type.` شکست خورد.
- درس‌های اصلی AUT در این ادامه به کاربرگ مستقل AUT-03 پیوند خوردند؛ تعمیق/بازبینی جامع همهٔ ۹ درس AUT همچنان ادعا نمی‌شود.
- چند درس NF از ساختار سؤال‌محور یکسان پیروی نمی‌کنند (NF-02 تا NF-04 و NF-06 تا NF-09 و NF-11 و NF-15 و NF-16).
- درس ۰.۱ از بستهٔ پیشین تأیید محتوایی داشت؛ IS-03–IS-05 برای Objectiveهای 4.3–4.5 از ابتدا تا انتها بازبینی شدند؛ IS-07 و IS-09 برای کفایت 4.7 و 4.9 بازبینی هدفمند شدند. Objectiveهای 4.6/4.8 عملی‌اند و همچنان اجرا‌نشده‌اند. این ارزیابی‌های متنی، اجرای IOS/Server/NMS/Collector یا تأیید پلتفرم را ثابت نمی‌کنند.


## تکمیل نگاشت کاربرگ و ممیزی بخش‌های بدنه‌محور — ۲۰۲۶-۱۱-۲۰

- [نقشهٔ تحویل عملی CCNA](academy-ccna-practical-delivery-map-fa.md) اکنون هر ۲۷ Objective عملی را به Worksheet و معیار قبولی مستقل وصل می‌کند؛ برای کاربرگ‌های مشترک، معیار هر هدف جدا آمده است. همان سند ۴۲ بخش بدنه‌محورِ شناسایی‌شده را ردیف‌به‌ردیف طبقه‌بندی و به فعالیت مرتبط می‌کند و برای همهٔ ۵۹ درس CCNA یک فعالیت پیوندی/نوع Verification ثبت می‌کند.
- AUT-03 به [کاربرگ Linux Underlay/VXLAN](academy-ccna-automation-03-sdn-fabric-lab-fa.md) پیوند دارد: فقط Underlay اجرا شد؛ VXLAN Kernel حاضر را نپذیرفت و Controller وجود نداشت. IS-07 به [کاربرگ QoS IOS XE](academy-ccna-services-07-qos-lab-fa.md) پیوند دارد؛ طرح IOS XE هدفمند است اما Image، Traffic generator و QoS اجرا نشده‌اند.
- ارزیابی ۱۱جزئی به‌روز AUT-03 و IS-07 هرکدام **۱۰✓+۱△** است؛ جمع ۲۷ عنوان: **۲۵۶✓+۳۶△+۰—+۵ N/A**. این امتیاز فقط وجود/کفایت طراحی را می‌سنجد. ۲۷ هدف عملی همچنان **۰/۲۷** اجرای IOS/PNETLab دارند؛ ۷۱ هدف دیگر در سطح متن کافی‌اند.

## اعتبارسنجی محلیِ همگام‌سازی نهایی — ۲۰۲۶-۱۱-۲۰

- آزمون تحویل `test_academy_delivery.py`: **۶/۶ موفق**؛ شامل آزمون‌های ساختار ۲۷ Objective، ۴۲ بخش بدنه‌محور و ۵۹ درس یکتا، و مرز اجرای AUT-03/IS-07.
- اسکن پیوندهای Markdown در ده سند تحویل/ممیزی هیچ مقصد محلی مفقودی نیافت؛ `git diff --check` و `py_compile` موفق شدند.
- این اعتبارسنجی محلی است، نه CI یا اجرای پلتفرم. CI موفق `44813470272` برای Commit پیشین `6728bf5` بود و تغییرهای جاری را شامل نمی‌شود؛ همچنان **۰/۲۷** هدف عملی IOS/PNETLab تأیید شده است.
