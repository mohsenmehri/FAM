# CCNA NA-09 — دسترسی مدیریتی و پیکربندی GUI در WLAN

**سطح:** CCNA. **پیش‌نیاز:** NF-03، NF-13، NA-08 و SEC-03. **اهداف رسمی:** `2.8` مقایسهٔ دسترسی مدیریت شامل Telnet، SSH، HTTP، HTTPS، Console، TACACS+/RADIUS و Cloud Managed؛ `2.9` تفسیر پیکربندی GUI در WLAN شامل ساخت WLAN، امنیت، QoS و تنظیمات پیشرفته. **وضعیت:** پیش‌نویس محتوایی؛ طراحی عملی انجام شده و **اجرا نشده**. هیچ دستگاه، GUI یا کنترلر واقعی آزمایش نشده و مدل/نسخه انتخاب نشده‌اند.

## اهداف

1. هر روش دسترسی را از نظر **رمزنگاری**، **احراز هویت** و **پیامد نبود آن** ارزیابی کنید.
2. پیش‌نیازهای معمول IOS برای ساخت Host Key و فعال‌کردن SSH را بشناسید؛ دستورها و Keyهای موجود را با نسخهٔ هدف تطبیق دهید.
3. `transport input ssh` را از روش احراز هویت جدا کنید؛ `login local` فقط وقتی لازم است که VTY قرار است از Username محلی استفاده کند.
4. فیلدهای ساخت WLAN را تفسیر کنید و بدانید کدام فیلد باعث «وصل نمی‌شود» می‌شود.
5. بدانید چرا Cloud Managed یک مدل بنیاداً متفاوت است، نه یک روش دیگر.

## ۱. روش‌های دسترسی — نگاه از منظر ریسک

| سازوکار | ماهیت/رمزنگاری | احراز هویت یا کاربرد | پورت/رابط رایج | ریسک/وابستگی |
|---|---|---|---|---|
| **Console** | مدیریت محلی خارج از IP؛ سریال/USB ذاتاً شبکه‌ای رمزنگاری‌شده نیست | Console Line/AAA، بسته به پیکربندی | پورت فیزیکی، نه TCP | دسترسی فیزیکی/کنترل اتاق و کابل |
| **Telnet** | TCP متن ساده؛ **بدون رمزنگاری** | Line Password، Local یا AAA | TCP/23 پیش‌فرض | Credential و Session قابل شنود |
| **SSH** | کانال رمزنگاری‌شده؛ الگوریتم‌ها/Host Key بر اساس نسخه | Local User، Key یا AAA | TCP/22 پیش‌فرض | Key/Algorithm/AAA و مجوز منبع |
| **HTTP** | **بدون TLS** | Basic/Local/AAA بر اساس Web Server | TCP/80 پیش‌فرض | رمز و داده در مسیر قابل خواندن |
| **HTTPS** | HTTP داخل TLS | Local/AAA/Client Certificate، طبق محصول | TCP/443 معمولاً | اعتبارسنجی Certificate، Version، Cipher و Credential |
| **SNMPv3** | پروتکل مدیریت/پایش؛ Auth/Privacy وابسته به Security Level | GET/SET/Notification، نه CLI Login | UDP/161؛ Trap اغلب 162 | Scope/ACL/USM و نوع Security Level را بررسی کنید |
| **TACACS+ / RADIUS** | **پروتکل AAA، نه Transport کاربر به CLI/GUI**؛ حفاظت و قابلیت‌ها متفاوت‌اند | Authentication/Authorization/Accounting از طریق Server | TACACS+ TCP/49؛ RADIUS UDP/1812/1813 معمولاً | Secret، دسترس‌پذیری، Method List و Fallback |
| **Cloud Managed** | Console/CLI محلی نیست؛ Control/Management Service بر بستر TLS و پروتکل Vendor | حساب/Role/SSO/MFA و Policy ابری | اتصال خروجی/مقصدها و Portها Vendor-specific؛ HTTPS رایج است | اینترنت/DNS/Cloud/مجوز و کنترل دسترسی حساب |

### Console — دسترسی محلی Out-of-Band

Console به IP/Route دستگاه وابسته نیست و در برخی خرابی‌های Management Network برای Recovery مفید است؛ اما **تنها راه ممکن یا الزام مطلق برای هر طراحی نیست**. خود پورت Console معمولاً کانال رمزنگاری‌شده نیست، پس کابل و اتاق تجهیزات را فیزیکی کنترل کنید. اگر Console Line با رمز/AAA محافظت می‌شود، تنظیم و آزمون آن را با Recovery مجاز انجام دهید؛ `exec-timeout` جلسهٔ رهاشده را می‌بندد و `logging synchronous` از قطع‌شدن خط تایپ با پیام Log جلوگیری می‌کند.

### Telnet — چرا باید از آن اجتناب کرد

Telnet همه‌چیز را **بدون رمزنگاری** می‌فرستد: نام کاربری، گذرواژه و هر فرمان. هر کسی که در مسیر باشد (Switch، Router، یا ابزار شنود) می‌تواند گذرواژه را بخواند. حتی اگر در شبکهٔ «امن» داخلی باشید، رویکرد «شبکهٔ داخلی قابل اعتماد است» در برابر مهاجم داخلی یا دستگاه آلوده شکست می‌خورد.

### SSH — ساخت Host Key در IOS

برای **ساخت Host Key RSA روی بسیاری از IOS/IOS XEها**، معمولاً ابتدا `hostname` مناسب و `ip domain-name` تنظیم می‌شوند تا نام کامل موردنیاز CLI در دسترس باشد؛ اگر Domain تنظیم نشده باشد، نمونهٔ خطای رایج چنین است:

```text
% Please define a domain-name first.
```

`Router` به‌عنوان Hostname پیش‌فرض لزوماً Syntax نامعتبر نیست، اما نام سازمانی مناسب نیست. اگر Host Key از قبل موجود باشد یا Platform/Algorithm دیگری به‌کار رود، پیش‌نیاز و فرمان می‌تواند فرق کند؛ دستور `show ip ssh`, وضعیت Key و مستند همان IOS را بررسی کنید. پس SSH را به یک جفت فرمان مطلق برای همهٔ سیستم‌عامل‌ها تقلیل ندهید.

### HTTP در برابر HTTPS

HTTP گذرواژه را با **Basic Authentication** می‌فرستد که Base64 است — یعنی **رمزنگاری نیست**، فقط کدگذاری است. با یک ابزار ساده قابل خواندن است. HTTPS همان را در TLS می‌پیچد.

**رویهٔ امن:** اگر Web Management لازم نیست، Service وب را غیرفعال نگه دارید. اگر به GUI نیاز دارید، HTTP ساده را (`no ip http server`) خاموش کنید و HTTPS را فقط با TLS/Certificate، Authentication، ACL و نیاز معتبر فعال کنید؛ Syntax/Status در نسخه‌ها فرق می‌کند.

### Cloud Managed — مدل متفاوت، نه روش دیگر

در Cloud-Managed Networking، Device یا Gateway با سرویس مدیریت Cloud ارتباط برقرار می‌کند و مدیر Policy/Configuration را از Dashboard/API ابری تعریف می‌کند. این **سطح مدیریت** در Cloud است؛ Packetهای کاربران عموماً همچنان در Access Point/Switch/Router محلی Forward می‌شوند، نه اینکه لزوماً از Dashboard عبور کنند. مقصدهای Cloud، پروتکل، DNS و Portهای خروجی را از مستند محصول بگیرید؛ «فقط TCP/443» را برای همهٔ Vendorها فرض نکنید.

**پیامدها:**

| مزیت | محدودیت/شرط |
|---|---|
| مدیریت گروهی و Policy مرکزی | وابستگی به اینترنت/Cloud برای برخی کارهای مدیریت؛ قابلیت محلی متفاوت است |
| گزارش/Telemetry تجمیع‌شده | دید به اتصال، مجوز، بازهٔ نگهداری و ارسال Telemetry وابسته است |
| پیکربندی از راه دور | مجوز/Subscription، امنیت حساب و MFA/Role مهم‌اند |

اگر Cloud یا مسیر اینترنت قطع شود، Device ممکن است State محلیِ قبلی را برای بخشی از Forwarding ادامه دهد، اما این **تضمین همگانی نیست**؛ Update، Auth، Client جدید، Policy پویا و Telemetry می‌توانند متفاوت رفتار کنند. مستند نسخه و Fail Mode واقعی را بررسی کنید؛ «Cloud Managed» به معنی این نیست که همهٔ Data در Cloud می‌گذرد یا Device حتماً کار می‌کند.

![نمودار قابل ویرایش روش‌های دسترسی مدیریتی؛ اجرا‌نشده](academy-images/na-09-management.svg)

## ۲. جدول کامل پیکربندی دسترسی

نمونهٔ طراحی‌شده، **اجرا‌نشده**:

```text
enable
configure terminal
hostname R1
ip domain-name lab.example
username netadmin privilege 15 secret <strong-secret>
enable secret <enable-secret>
service password-encryption

! Build/test SSH prerequisites before restricting VTY transports.
crypto key generate rsa modulus 2048
ip ssh version 2

line console 0
 password <console-secret>
 login
 exec-timeout 10 0
 logging synchronous
 exit

! Example range only: verify and configure every VTY range on this image.
line vty 0 4
 login local
 exec-timeout 10 0
 exit

! Optional: enable HTTPS only if GUI management is required and protected.
ip http secure-server
ip http authentication local
no ip http server
end
```

**مرحلهٔ محدودسازی جداگانه:** از Client مجاز یک Session SSH تازه بسازید و Authentication/Recovery را Verify کنید؛ سپس در Console، پس از تطبیق VTY Range واقعی، Transport را محدود کنید. این بخش را زودتر از تست اجرا نکنید:

```text
configure terminal
line vty 0 4
 transport input ssh
end
```

| فرمان | چرا |
|---|---|
| `hostname R1` | Hostname معنادار؛ در بسیاری از IOSها برای ساخت Host Key همراه Domain Name مصرف می‌شود |
| `ip domain-name` | در IOSهای متداول به ساخت FQDN برای RSA Key کمک می‌کند؛ نیاز دقیق وابسته به Platform/Key موجود است |
| `username ... privilege 15 secret` | Local Username/Secret؛ نوع Hash و مقاومت آن به IOS/Secret Type وابسته است، پس نوع پشتیبانی‌شدهٔ قوی را از مستند نسخه انتخاب کنید |
| `service password-encryption` | گذرواژه‌های خط را با **Type 7** رمز می‌کند — این **رمزنگاری ضعیف و برگشت‌پذیر** است. فقط برای جلوگیری از نگاه سرانگشتی، نه امنیت |
| `line console 0` + `login` | گذرواژهٔ Console را اعمال می‌کند |
| `line vty ...` + `login local` | VTY را برای Local User می‌سازد؛ اگر AAA Method List/روش دیگری تنظیم شود، دستور احراز متفاوت است |
| `transport input ssh` | VTY را به SSH محدود می‌کند؛ فقط روی **تمام VTY lineها** که IOS دارد اعمال/Verify کنید |
| `crypto key generate rsa modulus 2048` | نمونهٔ syntax برای ساخت RSA Host Key؛ اندازه، Algorithm و Syntax را با استاندارد سازمان و IOS تطبیق دهید |
| `ip ssh version 2` | SSHv1 آسیب‌پذیر است؛ فقط نسخهٔ ۲ |
| `no ip http server` | HTTP را خاموش می‌کند |

**دو تنظیم را با هم اشتباه نگیرید:** `transport input ssh` نوع Transport مجاز روی VTY را محدود می‌کند؛ احراز هویت را پیکربندی نمی‌کند. `login local` روش Local Username است؛ اگر AAA Method List یا روش مجاز دیگری استفاده می‌شود، همان را به Line وصل کنید.

**ترتیب امن تغییر:** از Console/Out-of-Band یا Session مدیریتِ محافظت‌شده آماده باشید؛ تنظیم Hostname/Domain و User/AAA، ساخت/بررسی Host Key، تنظیم SSHv2، تنظیم و آزمون احراز SSH را انجام دهید؛ پس از موفقیت، `transport input ssh` را روی تمام VTY lineهای موجود اعمال و از Session تازه Verify کنید. نمونهٔ `line vty 0 4` همهٔ مدل‌ها را پوشش نمی‌دهد؛ تعداد Range را روی IOS هدف بررسی کنید تا VTY دیگری با Telnet باز نماند.

## ۳. محدود کردن دسترسی مدیریت از شبکه

فقط رمزنگاری کافی نیست؛ باید **از کجا** هم محدود شود:

```text
ip access-list standard MGMT-ALLOWED
 permit 10.10.0.0 0.0.0.255
 deny any log
 exit
line vty 0 4
 access-class MGMT-ALLOWED in
```

- `access-class` (نه `access-group`) برای VTY به‌کار می‌رود. این یکی از تفاوت‌های ظریف و پرتکرار در آزمون است.
- `in` یعنی از دید روتر، ترافیک **ورودی** به جلسهٔ VTY.
- بدون این، هر IPی که مسیر شبکه‌ای داشته باشد می‌تواند تلاش ورود کند.

**روی Interface فیزیکی** از `ip access-group` استفاده می‌شود؛ روی VTY از `access-class`. این تفاوت را با هم اشتباه نگیرید.

## ۴. AAA در دسترسی مدیریت

| روش/Backend | نقش | نکتهٔ مقایسه |
|---|---|---|
| `login` + Line Password | احراز روی Console/VTY با Secret مشترک | ساده اما کم‌قابلیت حسابرسی/تفویض؛ دسترسی فیزیکی یا VTY همچنان کنترل می‌شود |
| `login local` | Local Username/Secret دستگاه | `username` محلی لازم است؛ دستگاه‌به‌دستگاه مدیریت می‌شود |
| AAA با **TACACS+** | دستگاه درخواست AuthN/AuthZ/Accounting را به Server می‌فرستد | معمولاً TCP/49؛ کاربردهای مدیریت Device و Authorize فرمان‌ها وابسته به پشتیبانی/Policy |
| AAA با **RADIUS** | Backend مرکزی برای احراز/سیاست و Accounting | معمولاً UDP/1812 و Accounting/UDP/1813؛ در WLAN/802.1X و نیز مدیریت Device قابل استفاده است |

TACACS+/RADIUS **جای SSH/HTTPS/Console را نمی‌گیرند**: مدیر همچنان از یک Transport وارد می‌شود و Device برای AAA با Server صحبت می‌کند. رمزنگاری و حفاظت Payload تفاوت دارند؛ از آن‌ها نتیجه نگیرید که Secret یا تمام پیام‌ها در همهٔ نسخه‌ها یکسان حفاظت می‌شود. AAA Method List/Fallback باید صریح و آزموده شود؛ شرح دقیق‌تر در SEC-08 است. `login local` فقط برای Local Username لازم است؛ با AAA List ممکن است روش دیگری متصل شود.

## ۵. GUI در WLAN — تفسیر فیلدها

در کنترلر WLAN، ساخت یک WLAN چند فیلد کلیدی دارد. **نام منوها بین نسخه‌ها متفاوت است** — آن‌چه ثابت است، **مفهوم** فیلدهاست. این درس مفهوم را می‌آموزد، نه مسیر منو را.

### فیلدهای مرحلهٔ ۱ — Profile و SSID

| فیلد | معنا | خطای رایج |
|---|---|---|
| **Profile Name** | نام داخلی پروفایل (در Broadcast دیده نمی‌شود) | اشتباه گرفتن با SSID |
| **SSID** | نامی که کلاینت می‌بیند | فاصله یا کاراکتر غیرمجاز |
| **Status / Admin State** | فعال/غیرفعال بودن | روشن نشدن پس از ساخت |
| **Broadcast SSID** | نمایش یا پنهان کردن SSID | «پنهان کردن امنیت است» — **افسانه**؛ ابزار کشف شبکه SSID پنهان را پیدا می‌کند |

### فیلدهای مرحلهٔ ۲ — امنیت (مهم‌ترین بخش)

| گزینه | معنا | مناسب برای |
|---|---|---|
| **Open** | احراز/رمزنگاری لینک Wi-Fi ندارد | فقط اگر Guest/Captive Portal با Segmentation و ریسک آگاهانه طراحی شده باشد؛ Portal به‌تنهایی RF را رمز نمی‌کند |
| **WPA2-Personal/PSK** | راز مشترک؛ از AES-CCMP و تنظیم سازگار استفاده شود، نه TKIP | شبکهٔ کوچک؛ اشتراک/چرخش راز و دسترسی کاربر را مدیریت کنید |
| **WPA2-Enterprise (802.1X)** | 802.1X/EAP و AAA/RADIUS یا سامانهٔ سازگار | سازمان با Identity مرکزی و تنظیم Server/Certificate/EAP |
| **WPA3-Personal (SAE)** | احراز مبتنی بر SAE؛ در برابر حملات حدس Offline مقاوم‌تر از PSK سنتی طراحی شده | Client/AP سازگار و Security Policy مناسب |
| **WPA3-Enterprise** | 802.1X/EAP با Suite/Policyهای WPA3؛ قابلیت دقیق به Mode/نسخه وابسته | سازمان با Client/AP و AAA سازگار |

**نکتهٔ سازگاری:** Clientهای قدیمی ممکن است WPA3 را پشتیبانی نکنند. Transition Mode بعضی ترکیب‌های WPA2/WPA3 را می‌پذیرد؛ Clientها ممکن است با روش‌های متفاوت متصل شوند و ریسک سازگاری/Fallback باقی بماند. آن را راه‌حل همگانی یا تضمین سطح امنیت یکسان برای همهٔ Clientها ندانید؛ Client/AP/Controller و Policy را Verify کنید.

**دام مهم:** در طراحی Enterprise متکی به RADIUS، انتخاب WPA2-Enterprise بدون AAA/EAP Server درست و قابل‌دسترسی باعث شکست Authentication می‌شود؛ ممکن است Client پیام Failure/Timeout بدهد یا Retry کند. محلی‌بودن بعضی EAP/AAA در محصول خاص را از مستندش بررسی کنید. SSID قابل‌مشاهده به معنی موفقیت 802.1X نیست؛ Server Certificate، EAP Method، Identity/Secret و Reachability را جدا عیب‌یابی کنید.

### فیلدهای مرحلهٔ ۳ — Interface / VLAN Mapping

| فیلد | معنا |
|---|---|
| **Interface / VLAN / Policy** | کدام Data Interface/Policy و VLAN یا Segment به WLAN نگاشت شود؛ نام و رفتار وابسته به Controller است |
| **Dynamic Interface** | در بعضی WLCها Interface منطقی با VLAN/Port مشخص؛ در محصول دیگر ممکن است معادل دیگری داشته باشد |

**خطای طراحی نمونه:** WLAN مهمان به Interface مدیریت نگاشت شود؛ اگر این Policy واقعاً روی Client Data اعمال شود، کاربران می‌توانند در Segment مدیریت قرار گیرند. Mapping باید با Trunk/Access VLAN، Scope AP، روش Central/Local Switching، DHCP/Relay، Routing و ACL سازگار باشد. این نتیجه را از نام Interface به‌تنهایی حدس نزنید؛ در GUI/Policy و Data Path مقصد Verify کنید.

### فیلدهای مرحلهٔ ۴ — QoS Profile

| پروفایلِ رایج در بعضی Cisco WLCها | کاربردِ هدف در GUI | چه چیزی باید جدا Verify شود |
|---|---|---|
| **Platinum** | Voice/ترافیک حساس به تأخیر | WMM/User Priority، DSCP mapping و حدود/Policy در همان Controller |
| **Gold** | Video | Mapping و Classifier؛ نام پروفایل به‌تنهایی DSCP معین نمی‌کند |
| **Silver** | Best-effort data | Trust Boundary و علامت‌گذاری در سمت سیمی |
| **Bronze** | Background/ترافیک کم‌اهمیت | Queue/Policing و رفتار نسخهٔ هدف |

نام‌ها و رفتار این Profileها محصول‌محورند؛ از `Platinum`/`Gold` نمی‌توان DSCP ثابت (مثلاً EF/AF41) نتیجه گرفت. Mapping واقعی WMM/UP/DSCP، Trust Boundary و QoS لایهٔ سیمی را طبق Config و مستند Controller بررسی کنید. اگر فقط WLAN اولویت بدهد و Switch/Router علامت را حفظ یا عمل نکند، سیاست انتهابه‌انتها تضمین نمی‌شود.

### فیلدهای مرحلهٔ ۵ — Advanced

| فیلد | معنا | چرا اهمیت دارد |
|---|---|---|
| **Band Select** | بعضی Controllerها با Steering/Response به Clientهای چندباندی، 5 GHz را ترجیح می‌دهند | رفتار Client/Driver و Policy را تست کنید؛ تضمین نمی‌کند همه به 5 GHz بروند |
| **Client Limit** | حد Association/Client در Scope تعیین‌شده (WLAN/AP/Radio، بسته به محصول) | واحد Scope و رفتار Reject/Load Balance را از GUI/نسخه بخوانید |
| **Session Timeout** | عمر Session/reauthentication طبق WLAN/AAA Policy | اثر بر Client و Session را با Security/AAA طراحی کنید؛ مقدار زیاد/کم به‌تنهایی امنیت را تعیین نمی‌کند |
| **Aironet IE** | Information Element اختصاصی Cisco در Beacon/Frame، اگر پشتیبانی شود | Vendor/Client compatibility؛ نیاز و پشتیبانی را بررسی کنید |
| **Management Frame Protection (MFP/802.11w)** | حفاظت از برخی Robust Management Frames، از جمله Deauth/Disassociation در پیکربندی پشتیبانی‌شده | Client/AP compatibility و Required/Capable mode؛ تمام حملات WLAN را متوقف نمی‌کند |
| **DHCP/Address Assignment** | تنظیم Proxy/Relay/Server یا نحوهٔ عبور DHCP، بسته به GUI | مسیر DHCP و VLAN را بررسی کنید؛ این گزینه را با Static IP کلاینت یکی نگیرید |

## ۶. کاربرگ مستقلِ تحلیل دسترسی و WLAN GUI

Objectiveهای 2.8 و 2.9 فعل‌های Compare/Interpret دارند؛ این تمرین را می‌توان از روی دادهٔ زیر حل کرد و برای آن به WLC یا PNETLab وابسته نیست. فیلدهای GUI فرضی‌اند، نه Screenshot یا Output واقعی.

### بخش A — خواندن فرم WLAN فرضی

| فیلد در فرم مفهومی | مقدار فرضی |
|---|---|
| Profile / SSID | `STAFF-01` / `Staff` |
| Admin State / Broadcast | Enabled / Visible |
| Security | WPA2-Enterprise (802.1X/EAP) |
| AAA/RADIUS Profile | **Not selected**؛ طراحی سازمان فرضاً به Remote RADIUS متکی است |
| Interface / VLAN | `management` / VLAN 99 |
| QoS Profile | `Silver` |
| Band Select | Enabled |
| MFP | Capable (not Required) |
| DHCP/Addressing | DHCP Relay/Server مسیرش جداگانه بررسی نشده |

سناریو: کاربران SSID را می‌بینند، اما احراز هویت ناموفق/Timeout است. اگر اتصال برقرار شود، کاربران ممکن است به VLAN مدیریت وارد شوند؛ این رفتار باید با Data Path و Interface Mapping همان WLC تأیید شود.

1. کدام فیلد محتمل‌ترین ناسازگاری با طرح Enterprise است؟ **پاسخ:** AAA/RADIUS Profile انتخاب نشده، درحالی‌که سناریو به Remote RADIUS متکی است؛ Server، EAP، Certificate، Secret و Reachability را با Log/Policy بررسی کنید.
2. چرا دیدن SSID اثبات احراز هویت یا IP گرفتن نیست؟ Broadcast/Beacon، Association، 802.1X، VLAN/Mapping، DHCP، Routing و Service مراحل جدا هستند.
3. چرا VLAN 99 نیازمند بازبینی امنیتی است؟ اگر این Mapping واقعاً Client Data را به Management Segment بفرستد، دسترسی/جداسازی خطرناک است؛ Trunk، AP Mode، Central/Local Switching و Policy را بررسی کنید.
4. آیا `Silver` به‌تنهایی DSCP خاصی را ثابت می‌کند؟ خیر؛ QoS profile و DSCP/WMM mapping محصول/نسخه‌محورند. اگر WLAN برای Voice است، Class، Trust Boundary و QoS سیمی را مستند کنید.
5. آیا Band Select اتصال Client را به 5 GHz تضمین می‌کند؟ خیر؛ رفتار وابسته به Client/Driver، باند پشتیبانی‌شده و Policy است.
6. MFP روی Capable به‌تنهایی از همهٔ Deauth/DoS جلوگیری می‌کند؟ خیر؛ 802.11w و Mode پشتیبانی‌شده فقط بعضی Frameهای مدیریتی را محافظت می‌کند.

**راهنمای عیب‌یابی:** ابتدا وضعیت/زمان و Client Impact؛ سپس Authentication/AAA و Event Log؛ پس از Auth، Interface/VLAN و مسیر DHCP؛ بعد Routing/ACL و Service. SSID را بدون مجوز باز یا امنیت WLAN را ضعیف نکنید. هیچکدام از فیلدهای این Case واقعی یا اجراشده نیستند.

### بخش B — تمرین اختیاری IOS Management (برای اجرای آینده، نه Capture)

**پیش‌نیاز:** IOS/IOS XE-compatible Image با Console و یک Client ترمینالی که SSH/Telnet را پشتیبانی کند؛ VPCS لزوماً Client مدیریتی ندارد. نسخه، VTY Range، Syntax و Snapshot را ثبت کنید. این پیکربندی را روی Device عملیاتی اجرا نکنید.

1. در Snapshot دورریختنی، Hostname و Domain Name را جداگانه بررسی کنید؛ اگر `crypto key generate rsa` بدون Domain شکست خورد، متن واقعی را ثبت کنید. خروجی خطا را روی همهٔ IOSها تعمیم ندهید.
2. Hostname/Domain مناسب، Local User یا AAA Method List و Host Key را طبق Syntax نسخه تنظیم کنید؛ `show ip ssh` و فرمان کلید سازگار را بخوانید.
3. از Client مجاز یک Session SSH تازه آزمایش کنید؛ تا پیش از موفقیت، Transportهای موجود را نبندید. `transport input ssh` فقط بعد از بررسی احراز و Recovery، روی **همهٔ VTY Rangeهای موجود** اعمال شود.
4. Telnet را فقط از Lab مجاز و پس از Restrict کردن Transport آزمایش کنید؛ منبع غیرمجاز را با `access-class` محدود کنید و ACL/Source IP را از Console Verify کنید.
5. HTTPS/HTTP را فقط اگر Web Server تصویر پشتیبانی کند و Certificate/AAA قابل بررسی باشد آزمایش کنید؛ در غیر این صورت «قابل آزمون نبود» ثبت کنید.

**وضعیت:** این Case و تمرین طراحی شده‌اند؛ هیچ IOS، PNETLab، GUI، Authentication یا Client واقعی در این سند آزمایش نشده است.

## ۷. عیب‌یابی

| نشانه | فرضیه‌ها/ترتیب بررسی | محدودیت |
|---|---|---|
| ساخت Host Key RSA شکست می‌خورد | Domain/Hostname، Host Key موجود، Syntax و پشتیبانی Algorithm/Modulus در نسخه را بررسی کنید | پیش‌فرض `Router` به‌تنهایی اثبات علت نیست؛ پیام IOS را ثبت کنید |
| SSH وصل نمی‌شود | `show ip ssh` و Host Key؛ User/AAA Method؛ VTY Transport/ACL؛ IP/Route/Reachability و Clock/Certificate در صورت نیاز | یک خطا علت واحد ندارد؛ از Console و Log مجاز کمک بگیرید |
| SSH وصل است ولی Telnet هم جواب می‌دهد | تمام VTY Rangeها و `transport input` را بررسی کنید؛ Range 0–4 ممکن است همهٔ Lineها را پوشش ندهد | در لاب تغییر دهید، سپس از Session تازه Verify کنید |
| AAA Login ناموفق است | Method List متصل به Line، Server/Key/Reachability، Policy و Fallback؛ TACACS/RADIUS Log | خاموش‌کردن AAA بدون Backup می‌تواند Lockout بسازد |
| HTTPS/GUI در دسترس نیست | Secure Server فعال؟ Port/ACL/Route؟ Certificate/Trust؟ AAA/Role؟ | دستور Status و قابلیت Web وابسته به نسخه است |
| SSID دیده می‌شود ولی Auth شکست می‌خورد | WPA/EAP/AAA Profile، RADIUS Reachability، Certificate/Identity و Client Log | Beacon/SSID به معنی Auth یا IP نیست |
| Client احراز شده ولی IP ندارد | Mapping VLAN/Interface، Central/Local Switching، Trunk، DHCP/Relay/Scope و مسیر برگشت | DHCP را از Auth جدا بررسی کنید |
| Guest/Staff وارد Segment مدیریت می‌شود | Policy/Interface/VLAN و مسیر Data را بررسی و دسترسی را تا رفع نقص محدود کنید | صرف نام `management` ثابت نمی‌کند Data در آن VLAN است؛ Flow را Verify کنید |
| Voice/Video کیفیت ندارد | WLAN QoS Profile، WMM/UP/DSCP map، Trust Boundary، Queue/Policing و مسیر سیمی | نام Platinum/Gold به‌تنهایی DSCP/عملکرد را ثابت نمی‌کند |
| Cloud Device از Dashboard Offline است | Internet/DNS/Time/Firewall outbound destination/ports طبق Vendor، Cloud Account/License | قطع Dashboard الزاماً معنی قطع Data Plane نیست و تداوم هم تضمین نیست |

**سناریوی خطر طراحی‌شده (اجرا نشده):** مدیر `transport input ssh` را روی تمام VTYها اعمال می‌کند، اما Host Key یا روش Authentication قابل‌استفاده ندارد. SSH Login شکست می‌خورد و Telnet هم مجاز نیست؛ اگر مسیر Out-of-Band دیگری آماده نباشد، Console ممکن است تنها Recovery باشد. پیش از محدودسازی، Credential/AAA، Key، Session تازه و برنامهٔ بازگشت را Verify کنید.

## ۸. سؤال‌ها و پاسخ

1. **Console چه ارزشی دارد؟** مسیر Out-of-Band است و در اختلال IP/Route ممکن است Recovery بدهد؛ پورت فیزیکی/کابل هم باید محافظت شود و Console تنها روش اجباری همهٔ شبکه‌ها نیست.

2. **چرا برای مدیریت معمولاً از Telnet اجتناب می‌کنیم؟** گذرواژه و فرمان‌ها بدون رمزنگاری منتقل می‌شوند؛ فقط استثنای Legacy باید جداگانه ایزوله، مجاز و کنترل شود.

3. **برای ساخت RSA Host Key در IOS متداول چه تنظیمی لازم می‌شود؟** معمولاً Hostname مناسب و `ip domain-name`؛ Key موجود، Platform و Syntax می‌توانند تفاوت ایجاد کنند. نبود Domain در بسیاری از IOSها خطای CLI می‌دهد.

4. **`service password-encryption` گذرواژه را امن می‌کند؟** نه. رمزنگاری **Type 7** ضعیف و برگشت‌پذیر است. برای گذرواژه از `secret` استفاده کنید.

5. **`secret` در برابر `password` چه تفاوتی دارد؟** `secret` معمولاً به‌صورت Hash ذخیره می‌شود؛ Algorithm/Type و مقاومت به IOS/دستور وابسته است. `password` ممکن است متن ساده یا Type 7 ضعیف باشد؛ نوع را بررسی و قوی‌ترین روش پشتیبانی‌شده را انتخاب کنید.

6. **`transport input ssh` چه می‌کند؟** Transportهای مجاز VTY را به SSH محدود می‌کند؛ Username/AAA و Authentication را تعریف نمی‌کند و باید روی همهٔ VTY lineهای هدف اعمال شود.

7. **`access-class` با `access-group` چه تفاوتی دارد؟** `access-class` روی VTY، `access-group` روی Interface فیزیکی.

8. **HTTP چرا ناامن است؟** گذرواژه را با Basic Auth (Base64) می‌فرستد که رمزنگاری نیست.

9. **Cloud-Managed چه تفاوتی دارد؟** Management/Policy از سرویس ابری انجام می‌شود؛ Data معمولاً روی Device محلی می‌گذرد. نبود اینترنت می‌تواند Update/Telemetry را مختل کند؛ اثر دقیق بر Session/Forwarding به محصول و Fail Mode بستگی دارد.

10. **WPA2-Enterprise متکی به Remote RADIUS بدون AAA/EAP Server قابل‌دسترسی چه می‌شود؟** Authentication معمولاً Fail/Timeout می‌شود؛ Log، EAP/Certificate، Server Profile و Reachability را بررسی کنید. پیاده‌سازی محلی/سازگارِ محصول خاص را جدا Verify کنید.

11. **QoS Profile کنترلر با QoS سیمی چه ربطی دارد؟** Policy باید در مسیر End-to-End سازگار باشد؛ WMM/UP/DSCP Mapping و Trust Boundary را بررسی کنید. نام Profile به‌تنهایی Marking/Queue یا اولویت واقعی را ثابت نمی‌کند.

12. **TACACS+ و RADIUS روش‌های Transport ورود مدیرند؟** خیر؛ آن‌ها AAA Protocolهای بین Device و Server هستند. مدیر از Console/SSH/HTTPS وارد می‌شود؛ Device می‌تواند AAA را به Server واگذار کند.

13. **SNMPv3 جای SSH است؟** خیر؛ SNMPv3 برای Monitoring/Management API و Notification است، نه Interactive CLI. Security Level `authPriv` احراز و محرمانگی را فراهم می‌کند، اگر درست پیکربندی شود.

14. **آیا GUI واقعی آزمایش شده است؟** خیر. این درس مفهوم فیلدها را می‌آموزد و نام منوها بین نسخه‌ها (AireOS، IOS XE، Cloud) متفاوت است.

## واژه‌نامه و چک‌لیست

**Console**: دسترسی سریال Out-of-Band؛ **VTY**: خط مجازی دسترسی IP؛ **SSHv2**: نسخهٔ دوم SSH (امنیت وابسته به Cipher/Key/Policy)؛ **FQDN**: نام کامل دامنه؛ **Basic Auth**: Scheme احراز، Base64 رمزنگاری نیست؛ **AAA**: احراز/مجوز/حسابرسی؛ **SSID**: نام شبکهٔ بی‌سیم؛ **MFP/802.11w**: حفاظت از بعضی Frameهای مدیریتی؛ **Cloud Managed**: Management از سرویس ابری.

- [ ] SSH Transport را از Host Key، User/AAA و IP Reachability جدا بررسی می‌کنم.
- [ ] دسترسی VTY را فقط پس از Test Session/Recovery و روی تمام Line Rangeها محدود می‌کنم.
- [ ] `access-class` را از `access-group` تفکیک می‌کنم.
- [ ] می‌دانم Type 7/`service password-encryption` رمزگذاری امنیتی قوی نیست.
- [ ] HTTP را غیرفعال می‌کنم و HTTPS را فقط با Certificate/AAA و نیاز معتبر در معرض دسترسی می‌گذارم.
- [ ] TACACS+/RADIUS را Backend AAA و SNMPv3 را Monitoring می‌شناسم، نه Transport ورود.
- [ ] فیلدهای WLAN، Authentication، VLAN/Data Path، QoS و Advanced را از روی مفهوم تفسیر می‌کنم.
- [ ] SSID دیده‌شدن را از Authentication، IP، Routing و Service جدا می‌کنم.
- [ ] هیچ GUI یا کنترلر واقعی را آزمایش‌شده اعلام نمی‌کنم.
