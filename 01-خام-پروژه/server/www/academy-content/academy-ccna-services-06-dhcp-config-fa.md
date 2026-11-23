# CCNA IS-06 — DHCP Client و Relay

**سطح:** CCNA. **پیش‌نیاز:** IS-03. **هدف رسمی:** `4.6` پیکربندی و Verification DHCP Client و Relay. **وضعیت:** بازبینی محتوایی این نوبت؛ طرح پیکربندی و شواهد طراحی شدند، اما اجرای IOS/Server و سازگاری Syntax با Image واقعی هنوز تأیید نشده‌اند.

## اهداف

روی یک رابط روتر DHCP Client فعال کنید، روی رابط رو به Clientها DHCP Relay پیکربندی کنید، Lease سمت WAN و دریافت Lease سمت LAN را با شواهد جداگانه بررسی کنید.

## ۱. دو نقش مستقل DHCP روی روتر

یک رابط روتر می‌تواند **DHCP Client** باشد و از Server بالادست IPv4 بگیرد؛ رابط دیگری می‌تواند **Relay** باشد و درخواست Clientهای Subnet خود را به DHCP Server در Subnet دیگر برساند.

- **Client:** `ip address dhcp` روی Interface، درخواست آدرس برای خود روتر می‌فرستد.
- **Relay:** `ip helper-address <server-ip>` روی رابط رو به Client، DHCP Broadcast را به Server مشخص‌شده Unicast می‌کند. Relay با استفاده از آدرس رابط Client-facing، به Server کمک می‌کند Scope مناسب را انتخاب کند.

Router معمولاً DHCP Broadcast را بین Subnetها Route نمی‌کند؛ برای همین به Relay نیاز است. `ip helper-address` در بعضی IOSها می‌تواند علاوه بر DHCP، Broadcast سرویس‌های UDP دیگری را نیز Forward کند؛ اثر پیش‌فرض‌ها و محدودسازی را در راهنمای نسخهٔ هدف بررسی کنید. اگر چند DHCP Server مقصد داشته باشند، Router درخواست را به مقصدهای پیکربندی‌شده Forward می‌کند؛ Client از Offer معتبر یکی را برمی‌گزیند و نباید فرض کرد «اولین پاسخ از نظر زمان» همیشه انتخاب می‌شود.

## ۲. توپولوژی و آدرس‌دهی پیشنهادی

**طرح PNETLab ایزوله، طراحی‌شده و اجرا‌نشده:** R1 یک رابط DHCP Client به یک DHCP Server آزمایشی و مجزا دارد؛ رابط دوم Gateway کلاینت‌هاست و Relay را به DHCP Server در Subnet سوم می‌فرستد. DHCP Server راه دور و پاسخ‌دهی‌اش باید در محیط واقعی تنظیم شود. به اینترنت یا ISP واقعی وصل نشوید.

![نمودار قابل ویرایش DHCP Client و Relay؛ اجرا‌نشده](academy-images/is-06-dhcp-relay.svg)

| گره/Interface | IPv4 نمونه | نقش/پارامتر |
|---|---|---|
| DHCP-ISP | `198.51.100.1/24` | سرویس DHCP آزمایشی؛ Pool نمونه `198.51.100.25–40` فقط برای رابط WAN |
| R1 `Gi0/1` | DHCP Client؛ Lease نمونه `198.51.100.25/24` | دریافت خودکار IPv4؛ آدرس واقعی تابع Offer است |
| R1 `Gi0/0` | `10.10.0.1/24` | Gateway و Relay روی LAN کلاینت |
| PC-A | Scope `10.10.0.100–149/24` | Client DHCP؛ Gateway Option 3 برابر `10.10.0.1` |
| R1 `Gi0/2` | `10.20.0.1/24` | رابط شبکهٔ Server راه دور |
| DHCP-REMOTE | `10.20.0.200/24` | Scope برای `10.10.0.0/24`؛ Default Gateway خود Server برابر `10.20.0.1`؛ Gateway واگذارشده به Client برابر `10.10.0.1` |

نام Interfaceها و پشتیبانی هم‌زمان از سه پورت در Image انتخابی تأیید نشده‌اند. اگر مدل تصویر پورت کافی ندارد، توپولوژی را با زیررابط/VLAN یا Image سازگار بازطراحی کنید و تغییر را ثبت کنید؛ آدرس‌دهی یا سیم‌کشی را بی‌مدرک فرض نکنید. آدرس‌های `198.51.100.0/24` و `192.0.2.0/24` مستنداتی‌اند؛ در این تمرین فقط بلوک `198.51.100.0/24` روی لاب ایزوله استفاده می‌شود.

## ۳. پیکربندی پیشنهادی R1

DHCP-REMOTE باید Scopeای برای Subnet **کلاینت‌ها** داشته باشد، نه فقط Subnet مستقیم خودش: `10.10.0.0/24`، بازهٔ Lease انتخابی، Exclusion/Reservation، Gateway `10.10.0.1` و Options لازم. تنظیم Server به OS/Image وابسته است و فرمان آن در این سند جعل نشده است.

**فرمان‌های R1 طراحی‌شده و اجرا‌نشده؛ نام/نحو را با IOS انتخابی تطبیق دهید:**

```text
configure terminal
interface GigabitEthernet0/1
 ip address dhcp
 no shutdown
interface GigabitEthernet0/0
 ip address 10.10.0.1 255.255.255.0
 ip helper-address 10.20.0.200
 no shutdown
interface GigabitEthernet0/2
 ip address 10.20.0.1 255.255.255.0
 no shutdown
end
```

`ip helper-address` روی `Gi0/0` است، چون همان رابط، Broadcast Domain کلاینت‌هاست. R1 به هر دو Subnet `10.10.0.0/24` و `10.20.0.0/24` مسیر Connected دارد؛ DHCP-REMOTE نیز باید پاسخ را از مسیر Gateway خود به Relay برگرداند. این تمرین NAT یا دسترسی اینترنت را تنظیم نمی‌کند.

## ۴. Verification

**خروجی‌های زیر نمونهٔ آموزشیِ ساختگی‌اند، نه Capture واقعی؛ Syntax و قالب خروجی وابسته به IOS است.**

```text
R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0      10.10.0.1       YES manual up                    up
GigabitEthernet0/1      198.51.100.25   YES DHCP   up                    up
GigabitEthernet0/2      10.20.0.1       YES manual up                    up
```

```text
R1# show dhcp lease
Temp IP addr: 198.51.100.25 for peer on Interface: GigabitEthernet0/1
DHCP Lease server: 198.51.100.1, state: 3 Bound
Lease: 86400 secs, Renewal: 43200 secs, Rebind: 75600 secs
```

`show dhcp lease` وضعیت Client روی R1 را بررسی می‌کند؛ این فرمان ثابت نمی‌کند PC-A از Relay Lease گرفته است. برای سمت LAN، Client باید آدرس رنج `10.10.0.100–149` و Gateway `10.10.0.1` داشته باشد؛ DHCP-REMOTE باید Lease/Log درخواست Relayed را ثبت کند. ابزار/فرمان Client، Server Log، Lease Time و نمایش `giaddr` به سیستم‌عامل/محصول بستگی دارد.

## ۵. کاربرگ مستقل و Troubleshooting

**پیوند رسمی:** `4.6 Configure and verify DHCP client and relay`. این سناریو دو شاهد جدا می‌خواهد: DHCP Client روی R1 و DHCP Relay برای PC-A. هیچ‌یک روی IOS یا سرور واقعی اجرا نشده‌اند.

**تجهیزات/نسخه:** یک Router IOS با سه رابط آزمایشگاهی، دو DHCP service مجزا (شبیه‌ساز ISP و DHCP-REMOTE)، یک VPCS یا Client با DHCP، سه L2 segment/switch/bridge، Console و دسترسی مدیریتی. مدل/نسخهٔ Router، نوع/نسخهٔ Serverها، نسخهٔ PNETLab و فرمان‌های Client را قبل از کار ثبت کنید. هر سه Segment باید ایزوله باشند؛ به شبکهٔ واقعی/اینترنت اتصال ندهید.

### مراحل اجرا

1. توپولوژی §۲ را مطابق Interfaceهای واقعاً موجود بسازید. نام پورت‌ها، VLAN/Bridge و نسخهٔ هر Image را ثبت کنید.
2. DHCP-ISP را روی Segment WAN به‌صورت آزمایشی تنظیم کنید تا Leaseای از Pool غیرهم‌پوشان `198.51.100.25–40/24` به R1 بدهد. این DHCP server به ISP واقعی وصل نیست.
3. DHCP-REMOTE را روی `10.20.0.200/24` تنظیم کنید: Scope برای `10.10.0.0/24`، رنج Client، Exclusion آدرس‌های رزروشده و Option 3 برابر `10.10.0.1`. Default Gateway خود Server را `10.20.0.1` قرار دهید. نسخه/تنظیم واقعی را مستند کنید.
4. Client را به DHCP روی LAN `10.10.0.0/24` بگذارید. R1 را طبق §۳ پیکربندی کنید و Interfaceهای هر سه Subnet را بالا بیاورید.
5. روی R1، `show ip interface brief` و در صورت پشتیبانی `show dhcp lease` را ثبت کنید؛ جداگانه ثابت کنید `Gi0/1` از DHCP-ISP Lease گرفته است.
6. روی PC-A یک درخواست تازه بسازید؛ VPCS/Windows/Linux فرمان Renew متفاوت دارند. آدرس، Mask و Gateway را از Client بگیرید و Lease/Log را در DHCP-REMOTE بررسی کنید. اگر ابزار دارد، مبدأ Relay/`giaddr` را هم ثبت کنید.
7. Client را با Gateway `10.10.0.1` تست کنید و مسیر پاسخ Server را بررسی کنید. Ping فقط دسترسی IP را می‌سنجد، نه همهٔ تراکنش‌های DHCP.
8. **نقص کنترل‌شده:** فقط در پروژهٔ دورریختنی، `ip helper-address 10.20.0.200` را از رابط LAN بردارید؛ Lease Client را Release/Renew کنید و ببینید درخواست تازه به سرور راه دور نمی‌رسد، درحالی‌که DHCP Client روی `Gi0/1` مستقل است. Helper را بازگردانید و Lease موفق تازه ثبت کنید. به Lease قدیمی به‌عنوان شاهد درخواست جدید تکیه نکنید.
9. پس از ثبت شواهد، پروژه را به Snapshot پایه برگردانید؛ روی روتر/سرور عملیاتی هیچ تغییری ندهید.

### شاهد مورد انتظار

| بخش آزمون | نتیجهٔ مورد انتظار | چه چیزی را به‌تنهایی ثابت نمی‌کند؟ |
|---|---|---|
| DHCP Client روی `Gi0/1` | آدرس Leaseشده، Server و وضعیت Bound در شاهد پلتفرم | موفقیت DHCP Relay به PC-A |
| DHCP Relay روی `Gi0/0` | PC-A Lease از Scope `10.10.0.0/24` با Gateway `10.10.0.1` می‌گیرد؛ Server Log/Lease درخواست Relayed را نشان می‌دهد | دسترسی برنامه یا اینترنت |
| برداشتن موقت Helper | درخواست تازه از Client به Scope راه‌دور نمی‌رسد؛ پس از بازگردانی Lease تازه موفق می‌شود | خرابی خود DHCP Client روی `Gi0/1` |
| مسیر پاسخ | Server به `10.20.0.1` و Relay به Client دسترسی دارد | صحت همهٔ Optionهای Scope |

### Troubleshooting

| نشانه | بررسی مرحله‌ای |
|---|---|
| `Gi0/1` Lease نمی‌گیرد | رابط/کابل و Segment WAN، DHCP-ISP، Pool آزاد، VLAN و Firewall |
| WAN Lease دارد ولی PC-A ندارد | Broadcast Domain و Client؛ `ip helper-address` روی رابط Client-facing؛ Server address/Scope؛ UDP/ACL؛ Server Log |
| PC-A آدرس دارد ولی Gateway غلط است | DHCP Option 3، Scope/Reservation و Lease قدیمی |
| Server درخواست را می‌بیند ولی پاسخی نمی‌رسد | `giaddr`/Scope انتخابی، مسیر برگشت به Relay، Default Gateway Server و ACL |
| چند Server/Helper هست | مقصدهای Forwardشده، هر Offer و انتخاب Client را در Log/Capture تفکیک کنید؛ انتخاب «اولین پاسخ» را فرض نکنید |

**معیار موفقیت/تحویل:** (۱) Imageها و رابط‌های واقعی ثبت شده؛ (۲) R1 روی `Gi0/1` Lease می‌گیرد؛ (۳) PC-A از Server راه‌دور Lease و Gateway درست می‌گیرد؛ (۴) Log/Capture درخواست Relay را از DHCP Client خود R1 متمایز می‌کند؛ (۵) نقص Helper و بازیابی با Lease تازه مستند است؛ (۶) محدودیت Syntax، Scope و نبود اتصال به ISP واقعی توضیح داده شده است. تا اجرا، همهٔ فرمان‌ها و خروجی‌ها طراحی‌شده‌اند.

## ۶. سؤال‌ها و پاسخ

1. **DHCP Client روی روتر چه می‌کند؟** برای خود Interface Lease درخواست می‌کند.
2. **`ip address dhcp` کجا قرار می‌گیرد؟** در پیکربندی رابط DHCP Client.
3. **Relay چه می‌کند؟** DHCP Broadcast را به Server در Subnet دیگر می‌رساند و آدرس Relay را برای انتخاب Scope فراهم می‌کند.
4. **`ip helper-address` کجا تنظیم می‌شود؟** روی رابط رو به Clientهای Broadcast Domain مربوط.
5. **چرا در این توپولوژی Relay لازم است؟** DHCP-REMOTE در Subnet دیگری است و Broadcast روتر را عبور نمی‌کند.
6. **`Bound` چه معنایی دارد؟** Client روی آن Interface یک Lease دریافت/برقرار کرده؛ قالب دقیق خروجی پلتفرم‌محور است.
7. **آیا `show dhcp lease` روی R1، Lease کلاینت PC-A را ثابت می‌کند؟** خیر؛ آن، DHCP Client خود R1 را بررسی می‌کند.
8. **چند Helper/Server پیکربندی شود، اولین پاسخ حتماً برنده است؟** خیر؛ Client از Offerهای معتبر انتخاب می‌کند؛ ترتیب/رفتار را با شواهد همان Client بسنجید.
9. **آیا DHCP Client و Relay روی یک روتر ممکن‌اند؟** بله؛ روی Interfaceهای متفاوت با نقش‌های مستقل.
10. **آیا این سناریو اجرا شده است؟** خیر.

## واژه‌نامه و چک‌لیست

DHCP Client: دریافت‌کنندهٔ Lease؛ Relay: رساندن درخواست بین Subnetها؛ Scope: محدوده و Optionهای تخصیص؛ Lease: تخصیص زمان‌دار؛ `giaddr`: آدرس رابط Relay که در انتخاب Scope کاربرد دارد.

- [ ] Interface Client و Interface Relay را از هم تشخیص می‌دهم.
- [ ] DHCP Server راه‌دور Scope مربوط به Subnet کلاینت را دارد.
- [ ] Lease سمت R1 را از Lease PC جداگانه Verification می‌کنم.
- [ ] مسیر رفت/برگشت و Gateway Server را بررسی می‌کنم.

## منابع فنی

- [RFC 2131 — Dynamic Host Configuration Protocol](https://www.rfc-editor.org/rfc/rfc2131.html)
- [RFC 2132 — DHCP Options and BOOTP Vendor Extensions](https://www.rfc-editor.org/rfc/rfc2132.html)

Syntax و خروجی `ip helper-address`, `show dhcp lease` و DHCP Client را با Command Reference نسخهٔ واقعی تطبیق دهید.
