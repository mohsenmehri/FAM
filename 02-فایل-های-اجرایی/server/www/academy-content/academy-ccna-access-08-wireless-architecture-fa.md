# CCNA NA-08 — معماری Wireless سیسکو و زیرساخت فیزیکی WLAN

**سطح:** CCNA. **پیش‌نیاز:** NF-03، NF-14 و NA-02. **اهداف رسمی:** `2.6` معماری‌های Wireless سیسکو و حالت‌های AP؛ `2.7` اتصالات فیزیکی اجزای WLAN شامل AP، WLC، پورت‌های Access/Trunk و LAG. **وضعیت:** پیش‌نویس؛ هیچ AP، WLC یا اتصال واقعی آزمایش نشده است. مدل‌ها و نسخه‌ها انتخاب نشده‌اند.

## اهداف

معماری Autonomous، Cloud-based و Split-MAC را مقایسه کنید، حالت‌های AP و نقش WLC را توضیح دهید و اتصال فیزیکی AP به Access/Trunk و WLC به شبکه را در سناریوی طراحی‌شده تفسیر کنید.

## ۱. سه معماری

**Autonomous:** هر AP مستقل پیکربندی و مدیریت می‌شود و تنظیمات روی خود AP است؛ برای شبکه‌های کوچک مناسب است ولی مدیریت مرکزی و مقیاس‌پذیری ندارد.

**Cloud-based:** مدیریت AP از طریق سرویس ابری انجام می‌شود؛ مدیر از داشبورد مرکزی سیاست را اعمال می‌کند. APها برای مدیریت باید به Endpointهای سرویس‌دهنده برسند (اغلب از طریق اینترنت، اما مسیر و نیاز به Internet را معماری/مستند محصول تعیین می‌کند). مسیر User Data می‌تواند Local باشد؛ Cloud Management به این معنی نیست که تمام دادهٔ کاربر از Cloud عبور می‌کند. وابستگی، دسترس‌پذیری سرویس ابری، مجوز و قفل‌شدن به ارائه‌دهنده را در طراحی بسنجید.

**Split-MAC (Controller-based/Centralized):** بخشی از وظایف MAC/مدیریت روی WLC و بخشی از عملیات زمان‌واقعی در AP است. AP کنترلری با **CAPWAP** به WLC می‌پیوندد؛ در Central Switching دادهٔ WLAN نیز می‌تواند در CAPWAP به WLC تونل شود. این معماری امکان مدیریت مرکزی می‌دهد، ولی مسیر Data و تحمل قطع WLC تابع حالت AP/سیاست و نسخه است.

| AP Mode | نقش معمول | اثر/مرز |
|---|---|---|
| **Local** | سرویس‌دهی Client و در معماری معمول Controller-based، Central Switching | Client Data منتخب به WLC تونل می‌شود؛ حالت و پلتفرم را بررسی کنید |
| **FlexConnect** | AP شعبه با مدیریت WLC؛ Central یا Local Switching طبق تنظیم WLAN | Local Switching به VLAN/Trunk محلی و Policy درست نیاز دارد؛ عملکرد در قطع WAN/WLC تضمین ذاتی نیست |
| **Monitor** | پایش RF/شبکه یا Rogue بدون سرویس‌دهی Client به همان شکل AP عادی | رفتار و قابلیت Radio وابسته به Product/Version |
| **Sniffer** | دریافت/ارسال فریم منتخب برای Capture/تحلیل | AP معمولاً Client را سرویس نمی‌دهد؛ Capture ممکن است دادهٔ حساس داشته باشد |
| **Rogue Detector** | کمک به تشخیص Rogue از طریق همکاری/مشاهدات شبکه | یک AP منفرد الزاماً مکان‌یابی قطعی نمی‌کند |
| **Bridge/Mesh** | اتصال بی‌سیم میان نقطه‌ها یا Segmentها | نیازمند طرح Backhaul/Root/Child سازگار؛ فاصله و RF واقعی مهم است |
| **SE-Connect / Spectrum Expert** | مشاهده/تحلیل Spectrum در مدل‌های پشتیبان | نقش تخصصی و نسخه‌محور؛ Client Service هدف این حالت نیست |

نام AP Mode و قابلیت‌ها بین خانواده‌های WLC/Software فرق دارد؛ در شبکهٔ واقعی Command/GUI Guide همان نسخه را بخوانید. انتخاب حالت به محل AP، VLAN، Data Path، ظرفیت و سیاست ترافیک بستگی دارد.

![نمودار قابل ویرایش معماری Wireless؛ اجرا‌نشده](academy-images/na-08-wireless.svg)

## ۲. سناریوی طراحی‌شده

**طرح مستقل، اجرا‌نشده:** یک WLC، دو AP Local در دو طبقه و یک Access Switch در هر طبقه. AP به پورت Access یا Trunk متصل است؛ WLC به پورت Trunk با VLAN مدیریت و VLANهای کلاینت متصل است. هیچ کابل‌کشی واقعی انجام نشده است.

```text
[WLC] ── Trunk ── [Core/Distribution Switch]
                     │
              ┌──────┴──────┐
         [Access SW1]  [Access SW2]
              │              │
            [AP1]            [AP2]
         Access/Trunk    Access/Trunk
```

## ۳. اتصالات فیزیکی

**AP به Switch:** در Central Switching، AP معمولاً برای Management به Access Port متصل می‌شود؛ Client VLANهای انتخاب‌شده داخل CAPWAP حمل می‌شوند. در FlexConnect Local Switching، AP ممکن است برای Management و یک/چند Client VLAN به Trunk نیاز داشته باشد. این قاعدهٔ عمومی جایگزین طراحی/Vendor Guide نیست؛ Native VLAN، Tagging و اجازهٔ VLANها باید با حالت AP هماهنگ شوند. PoE نیز به توان/کلاس/بودجهٔ دو سمت وابسته است.

**WLC به Switch:** پورت فیزیکی ممکن است Access یا Trunk باشد؛ اگر چند VLAN/Interface روی همان لینک لازم باشد، Trunk در طراحی‌های پشتیبان به‌کار می‌رود. نوع WLC، نوع Interface (Management/Client/Service)، شیوهٔ VLAN mapping و نسخه مشخص می‌کنند. جملهٔ «هر WLC همیشه Trunk است» دقیق نیست.

**LAG** چند لینک فیزیکی را به یک گروه منطقی WLC–Switch تبدیل می‌کند و در صورت طراحی درست، ظرفیت و تاب‌آوری را افزایش می‌دهد؛ یک جریان منفرد الزاماً کل ظرفیت را نمی‌گیرد. پشتیبانی LAG، تعداد لینک، الزام Switch-side Port-channel و پروتکل (LACP یا روش پلتفرم) مدل‌محور است؛ EtherChannel را قبل از تطبیق راهنمای دو سر پیکربندی نکنید.

CAPWAP Control معمولاً از UDP/5246 و Data از UDP/5247 استفاده می‌کند؛ مسیر/ACL میان AP و WLC باید عبور لازم را مجاز کند. AP ممکن است WLC را از L2 Discovery، تنظیم دستی، DHCP Option 43 یا DNS به روش محصول کشف کند؛ برای مثال نام DNS رایج در برخی Cisco APها `CISCO-CAPWAP-CONTROLLER.<domain>` است، اما روش دقیق و ترتیب Discovery را با مدل/نسخه بررسی کنید. دریافت IP توسط AP به‌تنهایی Join موفق WLC را ثابت نمی‌کند.

در Centralized Switching دادهٔ Client منتخب در CAPWAP به WLC می‌رود؛ در Local Switching داده در AP به VLAN محلی Forward می‌شود. این تفکیک را با NF-03 تکمیل کنید.

## ۴. کاربرگ و Troubleshooting

1. یک WLAN مرکزی با Central Switching و یک WLAN شعبه با FlexConnect Local Switching رسم کنید؛ برای AP هر کدام Access/Trunk، Management VLAN و Client VLANهای لازم را روی نقشه ثبت کنید. توضیح دهید چرا مسیر User Data در دو حالت فرق می‌کند.
2. برای WLC، نوع Physical Interface/Port، VLAN mapping و نیاز یا عدم نیاز Trunk را از فرض‌های خود جدا و به مستندات همان مدل وابسته علامت بزنید. اگر چند لینک LAG است، روش سازگاری دو سمت را هم ثبت کنید.
3. سناریوی نقص طراحی‌شده: AP IP گرفته اما WLC Join نمی‌شود. شبکهٔ Management، روش/پاسخ Discovery (DHCP Option 43، DNS، Static یا L2 طبق طرح)، مسیر/ACL UDP/5246–5247، زمان/گواهی در صورت استفاده و لاگ مجاز را مرحله‌ای بررسی کنید؛ هیچ علت واحدی از IP داشتن قطعی نیست.
4. اگر Client به WLAN وصل شد ولی IP نگرفت، حالت Central/Local، VLAN mapping در WLC و Access/Trunk مسیر Client، DHCP و مسیر برگشت را جدا بررسی کنید.
5. برای هر AP Mode یکی از Local، FlexConnect، Monitor، Sniffer، Rogue Detector، Bridge/Mesh یا SE-Connect را انتخاب و نقش، اثر بر Client service و محدودیت مدل را بنویسید.
6. PNETLab به‌تنهایی Radio/RF واقعی یا Join یک AP فیزیکی را شبیه‌سازی و اثبات نمی‌کند؛ اگر تجهیزات واقعی در دسترس نیست، نتیجه را طراحی/تحلیل ثبت کنید، نه اجرا.

| نشانه | بررسی |
|---|---|
| AP بالا نمی‌آید | PoE، VLAN مدیریت، DHCP و CAPWAP |
| کلاینت IP ندارد | VLAN کلاینت روی Trunk و WLC |
| ترافیک به WLC برمی‌گردد | حالت Centralized در برابر Local Switching |

## ۵. سؤال‌ها و پاسخ

1. **Autonomous یعنی چه؟** هر AP مستقل مدیریت می‌شود.
2. **Centralized چه مزیتی دارد؟** مدیریت مرکزی از طریق WLC.
3. **CAPWAP چه می‌کند؟** تونل کنترل و مدیریت AP و WLC.
4. **Local AP چه می‌کند؟** ترافیک را به WLC تونل می‌کند.
5. **FlexConnect چه تفاوتی دارد؟** AP زیر مدیریت WLC است ولی برای هر WLAN می‌توان Central یا Local Switching را طبق قابلیت/پیکربندی انتخاب کرد؛ فقط در Local Switching، Data منتخب در AP به VLAN محلی می‌رود.
6. **Mesh برای چیست؟** اتصال بی‌سیم بین نقاط دور.
7. **AP به چه پورتی وصل می‌شود؟** Access یا Trunk طبق Data Path و VLANهای موردنیاز؛ برای Central Switching معمولاً Access مدیریت کافی است، ولی Trunk در Local Switching ممکن است لازم شود.
8. **WLC به چه پورتی وصل می‌شود؟** نوع پورت به WLC/Interface/VLAN mapping بستگی دارد؛ Trunk زمانی که چند VLAN حمل می‌شود، نه یک الزام همیشگی.
9. **LAG چیست؟** تجمیع منطقی چند لینک؛ پروتکل و تنظیم دو سمت مدل‌محور است و یک جریان لزوماً تمام ظرفیت را نمی‌گیرد.
10. **Centralized Switching یعنی چه؟** دادهٔ WLAN منتخب از AP به WLC تونل می‌شود.
11. **Local Switching یعنی چه؟** AP دادهٔ Client را به VLAN محلی Forward می‌کند؛ تنظیم و جداسازی VLAN باید درست باشد.
12. **SE-Connect چه نقشی دارد؟** در مدل‌های پشتیبان برای تحلیل Spectrum است؛ نام/قابلیت دقیق Version-dependent است.
13. **CAPWAP چه پورت‌هایی دارد؟** معمولاً Control روی UDP/5246 و Data روی UDP/5247؛ ACL/نسخه بررسی شود.
14. **AP IP گرفته؛ یعنی Join شده است؟** خیر؛ Discovery، مسیر، کنترل CAPWAP، پیکربندی و شواهد WLC جدا بررسی شوند.
15. **آیا این سناریو اجرا شده است؟** خیر، طرح آموزشی است.

## واژه‌نامه و چک‌لیست

AP: نقطهٔ دسترسی؛ WLC: کنترلر WLAN؛ CAPWAP: تونل ارتباطی AP؛ LAG: تجمیع لینک؛ FlexConnect: AP تحت مدیریت WLC با Central یا Local Switching، طبق WLAN/قابلیت نسخه.

- [ ] معماری‌ها را با هم قاطی نمی‌کنم.
- [ ] Access/Trunk و VLAN را در طراحی مشخص می‌کنم.
- [ ] Centralized و Local Switching را جدا می‌دانم.
