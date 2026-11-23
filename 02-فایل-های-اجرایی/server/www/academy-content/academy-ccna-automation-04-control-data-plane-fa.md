# CCNA AUT-04 — تفکیک Control Plane و Data Plane

**سطح:** CCNA. **پیش‌نیاز:** AUT-03. **هدف رسمی:** `6.3.a` توصیف تفکیک Control Plane و Data Plane. **وضعیت:** پیش‌نویس محتوایی؛ طراحی عملی انجام شده و **اجرا نشده**؛ هیچ کنترلر واقعی در دسترس نبوده است.

## اهداف

1. برای هر وظیفهٔ شبکه، تشخیص دهید در کدام Plane است — با استدلال، نه حفظ.
2. بفهمید تفکیک SDN، تفکیک **درون دستگاه** را به **بیرون** می‌برد.
3. **Fail Mode** را در سه سناریوی مشخص تحلیل کنید.
4. بدانید چرا این تفکیک هم مزیت می‌آورد و هم عیب‌یابی را سخت‌تر می‌کند.

## ۱. دو Plane اصلی — با مکانیزم دقیق

| ویژگی | **Control Plane** | **Data Plane** |
|---|---|---|
| کار | محاسبه/انتخاب Route، Topology و Adjacency؛ ساخت State لازم | اعمال Lookup/Policy و Forward کردن Packet/Frame |
| زمان‌بندی | رویدادمحور یا دوره‌ای؛ با همسایه/وضعیت تعامل دارد | هنگام ورود Packet/Frame یا Flow عمل می‌کند |
| محل پیاده‌سازی معمول | CPU/Route Processor یا Control process؛ جزئیات محصول‌محور | ASIC/NPU یا Software Forwarding Engine؛ سخت‌افزار/نرم‌افزار وابسته به دستگاه |
| State/خروجی | RIB، همسایگی و پروتکل‌ها؛ سپس اطلاعات لازم برای Forwarding نصب/اعلان می‌شود | FIB/Forwarding Table و Lookup، ACL/Queue/NAT حسب دستگاه |
| خطای نمونه | Route/Adjacency/Policy اشتباه یا نصب‌نشدن State | Drop، Loop یا Forwarding اشتباه |

### مثال‌های مشخص

| وظیفه | Plane | چرا |
|---|---|---|
| OSPF Hello و LSA | Control | همسایه و مسیر را محاسبه می‌کند |
| STP BPDU | Control | توپولوژی لایهٔ ۲ را تعیین می‌کند |
| Neighbor Resolution مثل ARP | در تحلیل مفهومی معمولاً Control/Adjacency | فرایند پاسخ و محل پردازش به سیستم‌عامل/پلتفرم وابسته است؛ نتیجهٔ همسایه برای Forwarding مصرف می‌شود |
| MAC Learning و جدول MAC/FDB | اغلب Data/Forwarding در Switchهای Ethernet | Source MAC/VLAN/Port برای تصمیم Frame استفاده می‌شود؛ پیاده‌سازی و punt behavior می‌تواند فرق کند |
| **RIB در برابر FIB** | RIB: نتیجهٔ Route Selection در Control | FIB/Hardware Forwarding Table: Lookup عملی Packet |
| **ACL روی بسته** | Data | در حین عبور بسته اعمال می‌شود |
| **Queue و QoS** | Data | ترتیب ارسال بسته |
| **NAT** | Data | تغییر آدرس در حین عبور |
| SSH به روتر | Management | پیکربندی، نه تصمیم مسیر |
| SNMP Monitoring | Management | پایش وضعیت |

**RIB/FIB را یکی نگیرید:** `show ip route` معمولاً RIB/مسیرهای منتخب را نشان می‌دهد؛ FIB/adjacency ساختاری است که Data Plane برای Forwarding مصرف می‌کند. جزئیات Verification و دسترسی به سخت‌افزار به مدل وابسته‌اند. Route در RIB به‌تنهایی اثبات نمی‌کند هر Packet در هر نقطه طبق انتظار Forward شده است.

**نکتهٔ ظریف ۱ — ARP/Neighbor Resolution:** پروتکل همسایه اطلاعات IP–MAC/Link-Layer را فراهم می‌کند و نتیجه در Adjacency/Forwarding مصرف می‌شود. محل دقیق پاسخ‌گویی یا Offload به سیستم‌عامل و دستگاه بستگی دارد؛ همهٔ ARP Frameها را در هر محصول بی‌قیدوشرط به یک Plane نسبت ندهید.

**نکتهٔ ظریف ۲ — ACL:** ACL یک **سیاست** است که مدیر تعریف می‌کند (Management)، در جدول نصب می‌شود (Control)، و روی بسته اعمال می‌شود (Data). اگر سؤال بپرسد «ACL در کدام Plane است؟»، پاسخ معمول **Data** است چون **اعمال** روی بسته در Data رخ می‌دهد. این را با تعریف مدیریتش اشتباه نگیرید.

**نکتهٔ ظریف ۳ — Routing Protocol:** OSPF و تبادل Hello/LSA در Control Plane هستند؛ Packetهای پروتکل روی رابط شبکه منتقل و در Router همسایه به Control/Protocol Process تحویل می‌شوند، نه اینکه مانند ترافیک کاربر صرفاً به مقصد بعدی Forward شوند. می‌توان گفت Control از همان رسانه/مسیر مدیریت‌شده (In-band) برای تبادل استفاده می‌کند، اما این را با «OSPF Packet در FIB مثل User Data Forward می‌شود» یکی نگیرید. اگر adjacency یا مسیر مدیریت Control قطع شود، محاسبه/توزیع Route می‌تواند مختل شود.

## ۲. تفکیک در دستگاه سنتی — این را همه فراموش می‌کنند

تفکیک Control/Data **اختراع SDN نیست.** در همان روتر سنتی:

```text
┌─────────────────────────────────────┐
│ Route Processor (CPU)               │ ← Control Plane
│  OSPF، BGP، STP، ARP                │
│  جدول مسیر را می‌سازد               │
└──────────────┬──────────────────────┘
               │ (دانلود جدول به ASIC)
┌──────────────▼──────────────────────┐
│ ASIC / Forwarding Engine            │ ← Data Plane
│  Lookup، Queue، ACL، Forwarding     │
└─────────────────────────────────────┘
```

**یعنی:** Control/Data دو **نقش منطقی**‌اند و در بسیاری از Router/Switchها Control process روی CPU/Route Processor و Forwarding در ASIC/NPU یا Engine نرم‌افزاری انجام می‌شود. این جداسازی الزاماً دو قطعهٔ فیزیکی یا دو مکان متفاوت نیست؛ جزئیات سخت‌افزار و Offload به مدل وابسته است.

در بعضی معماری‌های SDN، بخشی از منطق/Policy در یک Control Plane منطقیِ بیرون از Device متمرکز می‌شود و Data Plane همچنان Packetها را در تجهیزات می‌فرستد. این توصیف یک الگوی رایج است، نه حکم همهٔ سامانه‌ها: Control محلی می‌تواند باقی بماند و Controller هم می‌تواند توزیع‌شده/HA باشد.

پس SDN مرز جداسازی و برنامه‌پذیری را تغییر/آشکار می‌کند؛ مفهوم Control/Data از قبل در شبکه‌های سنتی نیز وجود داشت.

## ۳. SDN — مزایا با هزینه

### مزایا

| مزیت | چرا |
|---|---|
| **سیاست یکنواخت‌تر** | Policy می‌تواند در سطح منطقی تعریف و روی گروه‌های پشتیبانی‌شده اعمال شود؛ نتیجه نیازمند Verification است |
| **مدیریت تغییر** | API/Workflow می‌تواند مراحل تکراری را خودکار کند؛ صرف Controller بودن زمان یا موفقیت را تضمین نمی‌کند |
| **مشاهدهٔ تجمیعی** | Controller دادهٔ دستگاه‌های Onboard/Reachable را ترکیب می‌کند؛ دید ممکن است ناقص یا قدیمی باشد |
| **برنامه‌پذیری** | API، Script و Infrastructure as Code را ممکن می‌کند؛ باید اعتبارسنجی/کنترل دسترسی داشت |
| **تفکیک نقش** | می‌تواند Interface برنامه‌ای برای مصرف‌کننده فراهم کند؛ مسئولیت تیم‌ها وابسته به سازمان است |

### هزینه‌ها

| هزینه | پیامد |
|---|---|
| **وابستگی به Controller/API** | قطع Controller ممکن است تغییر مرکزی/Telemetry را مختل کند؛ تغییر محلی یا پروتکل‌های باقی‌مانده رفتار جدا دارند |
| **وابستگی به مسیر مدیریت** | اختلال مسیر/AAA/DNS/Firewall می‌تواند کنترل را محدود کند؛ VLAN جدا به‌تنهایی مسیر را تضمین نمی‌کند |
| **پیچیدگی عیب‌یابی** | خطا می‌تواند در Underlay، Overlay یا کنترلر باشد |
| **هزینهٔ زیرساخت** | کنترلر، مجوز و آموزش |
| **مسئلهٔ Fail Mode** | رفتار دستگاه در قطع کنترلر باید صریح تعیین شود |

## ۴. Fail Mode — سه سناریوی متفاوت

**Fail Mode** رفتار شبکه در قطع ارتباط با کنترلر است. **سه سناریو، سه رفتار، سه تصمیم:**

### سناریوی ۱ — ترافیک موجود

فرض کنید قبل از اختلال، FIB/Policy موردنیاز روی SWها نصب شده و User Packet مستقیماً از Data Plane عبور می‌کند. با قطع Controller، **ممکن است** این Flow موجود ادامه یابد؛ اما Flowهای دارای Timeout، Policy پویا، Tunnel/Session وابسته یا Failure Mode متفاوت می‌توانند متأثر شوند. از برچسب «Data Plane محلی است» به‌تنهایی استمرار را نتیجه نگیرید.

### سناریوی ۲ — تغییر جدید

اگر مدیر بخواهد VLAN 30 را **از Controller/API** تعریف کند و Controller/Management Path در دسترس نباشد، درخواست ممکن است اعمال نشود یا به تعویق بیفتد. امکان تغییر از CLI محلی به Policy Product و اختیار مدیر وابسته است؛ تغییر مستقیم می‌تواند با منبع حقیقت Controller تعارض کند یا در Reconciliation بازنویسی شود. مجوز و Workflow را بررسی کنید.

### سناریوی ۳ — اتصال کلاینت جدید (Wi-Fi)

| وضعیت | چه چیزی باید بررسی شود |
|---|---|
| WLAN کنترلری در Central Switching | تونل/کنترل AP–WLC، Session موجود، احراز هویت و روش Failover؛ قطع WLC می‌تواند مسیر/کلاینت را متأثر کند |
| FlexConnect با Local Switching | Data محلی ممکن است ادامه یابد، اما Control، Auth، Policy و Client جدید همچنان وابسته به تنظیم/Cache/نسخه‌اند |
| Standalone/Autonomous | AP ممکن است مستقل عمل کند؛ این Mode و Featureها محصول‌محورند و با Controller-Based برابر نیستند |

این تفاوت‌ها **طراحی‌محور و نسخه‌وابسته** است. برای هر سرویس، موجود/جدید بودن Session و مسیر Authentication/Data را جداگانه بنویسید؛ نام AP Mode به‌تنهایی ضمانت نیست.

## ۵. سناریوی طراحی‌شده

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده:** یک کنترلر فرضی و سه سوییچ. Control Plane روی کنترلر و Data Plane روی سوییچ‌ها **فرض** می‌شود؛ هیچ اتصال یا اجرای واقعی انجام نشده است.

```text
              ┌───────────────┐
              │  Controller   │  Control Plane (فرضی)
              │  10.10.0.10   │
              └───────┬───────┘
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
     [SW1]         [SW2]         [SW3]
    Data Plane   Data Plane   Data Plane
    + Control    + Control    + Control
    Plane (fallback) (fallback) (fallback)
```

**نکتهٔ طراحی:** توپولوژی فرض می‌کند سوئیچ‌ها توانایی Forwarding محلی و پروتکل‌های لازم را دارند؛ این ویژگی را از Image/مدل بررسی کنید. بعضی معماری‌های Controller از Switchهای سازگار با Control محلی استفاده می‌کنند، بعضی رفتارهای دیگری دارند. قطع Controller نه به‌طور خودکار همه‌چیز را می‌خواباند و نه تداوم را تضمین می‌کند.

![نمودار قابل ویرایش تفکیک Plane‌ها؛ اجرا‌نشده](academy-images/aut-04-planes.svg)

## ۶. کاربرگ تحلیلی مستقل

**Objective 6.3.a فعل Describe دارد؛ این تمرین تحلیلی است و PNETLab/Controller لازم ندارد.** ردیف‌های جدول سناریوی ساخته‌شده‌اند، نه Capture:

| رویداد فرضی | Plane اصلی در مدل مفهومی | چه چیزی را نشان می‌دهد؟ |
|---|---|---|
| R1 دریافت OSPF Hello و به‌روزرسانی Neighbor State | Control | ساخت/نگهداری Adjacency؛ نه User Data Forwarding |
| OSPF بهترین مسیر را انتخاب می‌کند و RIB را به‌روز می‌کند | Control | تصمیم Route Selection |
| Route منتخب به FIB/Forwarding Engine نصب می‌شود | انتقال State از Control به Data | آمادگیِ Lookup، نه اثبات عبور یک Packet |
| Frame با Source MAC جدید روی SW وارد می‌شود | معمولاً Data/L2 Learning | MAC/VLAN/Port در FDB به‌روزرسانی می‌شود؛ Offload/punt وابسته به پیاده‌سازی است |
| Router روی Packet ورودی ACL را اعمال و Drop می‌کند | Data (در لحظهٔ اجرا) | تصمیم Per-Packet/Flow؛ تعریف ACL از Management آمده است |
| مدیر با SSH Config را تغییر می‌دهد | Management | کانال مدیریت؛ Device پس از تغییر ممکن است آن را به Stateهای Control/Data اعمال کند |
| Controller یک Policy را به Switch می‌فرستد | Management/Control API (بسته به سامانه) | توزیع Policy؛ اجرای Policy روی Switch در مسیر Data رخ می‌دهد |

### پرسش و راهنمای پاسخ

1. **`show ip route` چه چیزی را نمایش می‌دهد؟** معمولاً RIB و Routeهای منتخب؛ به‌تنهایی FIB/ASIC یا عبور موفق Packet را ثابت نمی‌کند.
2. **`show ip cef` یا معادل آن چه کمکی می‌کند؟** در تصویر/نسخهٔ پشتیبان، نمایش Forwarding/Adjacency را فراهم می‌کند؛ نام، محتوا و سطح Hardware به محصول وابسته است.
3. **قطع OSPF همسایگی فوراً همهٔ ترافیک را Drop می‌کند؟** نه لزوماً؛ RIB/FIB، Timer، Route جایگزین و رفتار Device دخیل‌اند. با دادهٔ داده‌شده علت/نتیجهٔ قطعی نمی‌گیریم.
4. **ACL در کدام Plane است؟** Policy را Management تنظیم می‌کند؛ Sync/Installation در Control/Management انجام می‌شود؛ Match/Permit/Drop روی Packet در Data رخ می‌دهد.
5. **قطع Controller چه اثری دارد؟** از روی معماری فرضی کافی نیست؛ State نصب‌شده، Timeout، Fail Mode و مسیر کنترل را باید دانست.

**اختیاری برای Image IOS مجاز:** خروجی‌های مشاهده‌ای `show ip ospf neighbor`، `show ip route`, فرمان FIB سازگار، `show mac address-table` و ACL counter را کنار هم ثبت کنید. Syntax، دسترسی و معنای Counter را برای Image هدف بررسی کنید؛ از `debug` در محیط واقعی استفاده نکنید. این سند و همهٔ داده‌های جدول طراحی‌شده‌اند؛ هیچ اجرا یا خروجی واقعی ثبت نشده است.

## ۷. سؤال‌ها و پاسخ

1. **Control Plane چیست؟** State و تصمیم Route/Topology را محاسبه یا مدیریت می‌کند؛ نمونه‌ها OSPF، BGP و STP هستند. Neighbor Resolution مانند ARP در تشخیص مفهومی به دستگاه وابسته است و نتیجه‌اش در Forwarding استفاده می‌شود.

2. **Data Plane چیست؟** بخشی که بسته را واقعاً می‌فرستد: جدول Forwarding، Queue، ACL، NAT.

3. **Management Plane چیست؟** دسترسی و پیکربندی: SSH، SNMP، NETCONF.

4. **OSPF در کدام Plane است؟** Control.

5. **ACL در کدام Plane است؟** Data — چون روی بسته در حال عبور اعمال می‌شود. (تعریف سیاست در Management است، ولی اجرا در Data.)

6. **STP در کدام Plane است؟** Control.

7. **جدول Forwarding در کدام Plane است؟** Data.

8. **آیا در شبکهٔ سنتی تفکیک وجود دارد؟** بله، Control/Data نقش‌های منطقی‌اند؛ در بسیاری از Deviceها Control process روی CPU و Forwarding در ASIC/NPU یا Engine نرم‌افزاری است. SDN بعضی Control/Policy را در معماری بیرونی/متمرکزتر سازمان می‌دهد، نه اینکه همهٔ سامانه‌ها یکسان باشند.

9. **مزیت احتمالی تفکیک SDN چیست؟** در سامانهٔ پشتیبان می‌تواند تعریف/توزیع Policy و دید تجمیعی را ساده کند و API برنامه‌پذیر فراهم آورد؛ دامنه و صحت آن به محصول، پشتیبانی و Verification بستگی دارد.

10. **ریسک اصلی؟** وابستگی به کنترلر و مسیر مدیریت.

11. **Fail Mode چیست؟** رفتار شبکه در قطع ارتباط با کنترلر. سه سناریو: ترافیک موجود، تغییر جدید، اتصال کلاینت جدید.

12. **اگر Controller قطع شود شبکه کاملاً می‌خوابد؟** نه لزوماً، اما ادامهٔ Data هم تضمین نیست. State نصب‌شده، Timeout، Fail Mode، مسیر مدیریت و وابستگی سرویس را بررسی کنید؛ تغییر از Controller ممکن است متوقف شود ولی Control محلی می‌تواند باقی بماند.

13. **چرا عیب‌یابی سخت‌تر می‌شود؟** چون خطا می‌تواند در سه لایه باشد: Underlay، Overlay و کنترلر.

## واژه‌نامه و چک‌لیست

**Control Plane**: تصمیم؛ **Data Plane**: ارسال؛ **Management Plane**: پیکربندی؛ **Route Processor**: CPU تصمیم؛ **ASIC**: سخت‌افزار Forwarding؛ **Fail Mode**: رفتار در قطع کنترلر؛ **In-band**: تبادل Control روی همان زیرساخت/شبکهٔ اصلی، نه لزوماً مسیر فیزیکی جدا؛ **Reconciliation**: بازنویسی پیکربندی محلی توسط کنترلر.

- [ ] سه Plane را با مثال موقعیتی می‌شناسم، نه فقط تعریف.
- [ ] می‌دانم تفکیک در دستگاه سنتی هم وجود دارد.
- [ ] مزایا و هزینه‌ها را با هم می‌دانم.
- [ ] سه سناریوی Fail Mode را جدا تحلیل می‌کنم.
- [ ] برای هر دستگاه جملهٔ Fail Mode دارم.
- [ ] هیچ کنترلری را اجراشده اعلام نمی‌کنم.
