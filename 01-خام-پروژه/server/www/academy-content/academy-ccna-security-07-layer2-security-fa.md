# CCNA SEC-07 — امنیت لایهٔ ۲: DHCP Snooping، DAI و Port Security

**سطح:** CCNA. **پیش‌نیاز:** NA-01، NA-02 و SEC-06. **هدف رسمی:** `5.7` پیکربندی و بررسی امنیت لایهٔ ۲ شامل DHCP Snooping، Dynamic ARP Inspection و Port Security. **وضعیت:** پیش‌نویس محتوایی؛ طراحی عملی انجام شده و **اجرا نشده**. مدل Switch و نسخهٔ IOS انتخاب نشده. همهٔ خروجی‌ها نمونهٔ طراحی‌شده‌اند.

## اهداف

1. سه حملهٔ لایهٔ ۲ را با مکانیزم دقیقشان توضیح دهید.
2. Trusted و Untrusted را در جای درست تعیین کنید و بفهمید چرا اشتباه در آن، شبکه را قطع می‌کند.
3. هر سه کنترل را پیکربندی کنید و بفهمید هر کدام به دادهٔ کدام کنترل وابسته است.
4. ترتیب راه‌اندازی را بدانید — ترتیب اشتباه باعث قطع کاربران می‌شود.

## ۱. چرا لایهٔ ۲ آسیب‌پذیر است؟

در Switching لایهٔ ۲ِ پایه، فریم‌ها **به‌طور پیش‌فرض احراز هویت نمی‌شوند**؛ کنترل‌هایی مثل 802.1X باید جداگانه طراحی و فعال شوند. روی پورتی که چنین کنترلی ندارد، هر متصل‌شونده می‌تواند:

- ادعا کند سرور DHCP است.
- ادعا کند Gateway است (با ARP).
- MACهای جعلی بفرستد تا جدول MAC پر شود.

هیچ‌کدام از این‌ها «حمله به سوییچ» نیست؛ سوییچ دارد کار عادی خودش را می‌کند. دفاع باید روی **پورت‌ها** و **ترتیب یادگیری** اعمال شود.

## ۲. سه حمله، با مکانیزم دقیق

### حملهٔ ۱ — Rogue DHCP

**مکانیزم:** کلاینت DHCP پیام `Discover` را به‌صورت Broadcast در VLAN می‌فرستد. سرور جعلی (لپ‌تاپ مهاجم با نرم‌افزار DHCP) سریع‌تر از سرور واقعی پاسخ `Offer` می‌دهد. کلاینت این Offer را می‌پذیرد و Gateway و DNS را از مهاجم می‌گیرد.

**نتیجهٔ محتمل:** کلاینتی که Offer جعلی را بپذیرد ممکن است Gateway یا DNS مهاجم را تنظیم کند و ترافیکِ مسیریابی‌شده‌اش از او عبور کند (**On-Path**).

**کاهش — DHCP Snooping** با سه سازوکار:

1. **جداسازی Trusted/Untrusted** — پیام‌های Server→Client (`Offer`، `Ack`، `Nak`) از پورت Untrusted دور ریخته می‌شوند.
2. **جدول Binding** — برای هر تخصیص موفق، MacAddress + IP + Lease + VLAN + Interface ثبت می‌شود.
3. **Rate Limiting** — تعداد پیام DHCP در ثانیهٔ هر پورت محدود می‌شود تا طوفان DHCP جلوی منابع را نگیرد.

نکتهٔ عملی مهم: DHCP Snooping پیام `Discover` را از Untrusted **مسدود نمی‌کند**، چون کلاینت‌ها باید بتوانند درخواست بدهند. تنها پاسخ سمت سرور مسدود می‌شود.

### حملهٔ ۲ — ARP Spoofing

**مکانیزم:** ARP هیچ احراز هویتی ندارد. مهاجم یک ARP Reply جعلی می‌فرستد: «آدرس `10.10.0.1` (Gateway) در MAC من است». کلاینت‌ها جدول ARP خود را به‌روز می‌کنند و ترافیک Gateway را به مهاجم می‌فرستند.

**نتیجه:** On-Path شدن، شنود و دستکاری داده.

**کاهش — Dynamic ARP Inspection (DAI)**:

1. هر بستهٔ ARP روی پورت Untrusted بررسی می‌شود.
2. DAI دنبال جفت **MAC/IP** می‌گردد و آن را با **جدول Binding** مقایسه می‌کند.
3. اگر جفت در جدول نباشد، بسته دور ریخته می‌شود.
4. پورت‌های Trusted بدون بررسی عبور می‌کنند.

**وابستگی مهم:** در الگوی معمول DHCP، DAI صحت جفت IP/MAC را با Bindingهای DHCP Snooping می‌سنجد. اگر Binding معتبر وجود نداشته باشد، ARP پورت‌های Untrusted ممکن است Drop شود؛ ترافیک روی پورت Trusted بررسی نمی‌شود. میزبان‌های دارای IP ایستا را باید با ARP ACL/روش Binding پشتیبانی‌شده پوشش داد. پیش از فعال‌سازی `ip arp inspection vlan 10`، منابع اعتبارسنجی و Trust هر پورت را کامل کنید؛ خالی بودن Bindingها برای کلاینت‌های DHCP می‌تواند آن‌ها را از شبکه جدا کند.

### حملهٔ ۳ — MAC Flooding / CAM Table Overflow

**مکانیزم:** مهاجم فریم‌های زیادی با MAC مبدأهای تصادفی می‌فرستد تا ظرفیت یادگیری MAC مصرف شود. برای مقصد ناشناخته، سوییچ ممکن است فریم Unicast را در همان VLAN Flood کند (**Unknown-Unicast Flooding**). این به معنی دیده‌شدن همهٔ ترافیک نیست: Unicast شناخته‌شده همچنان به پورت مقصد می‌رود؛ پیامد به رفتار و ظرفیت پلتفرم بستگی دارد.

**کاهش — Port Security**:

1. تعداد MAC امن مجاز روی هر پورت محدود می‌شود.
2. MACها را می‌توان دستی یا با یادگیری `sticky` تثبیت کرد.
3. در صورت تخلف، رفتار مشخصی اعمال می‌شود.

این کنترل، MAC Flooding را کاهش می‌دهد اما به‌تنهایی محرمانگی ترافیک را تضمین نمی‌کند؛ Unknown-Unicast Flooding وابسته به رفتار و ظرفیت سوییچ است و مهاجمِ دارای دسترسی ممکن است با روش‌های دیگری ترافیک را شنود کند.

سه حالت تخلف (**Violation Mode**):

| حالت | بستهٔ متخلف | شمارنده | پورت | Log |
|---|---|---|---|---|
| **Protect** | دور ریخته می‌شود | ثبت **نمی‌شود** | باز می‌ماند | خیر |
| **Restrict** | دور ریخته می‌شود | ثبت **می‌شود** | باز می‌ماند | بله |
| **Shutdown** | دور ریخته می‌شود | ثبت می‌شود | **Err-Disable** می‌شود | بله |

تفاوت Protect و Restrict در گزارش‌دهی است: Protect بسته‌های متخلف را Drop می‌کند، ولی معمولاً شمارنده/Log/SNMP trap ندارد؛ Restrict آن‌ها را Drop کرده و شمارنده را افزایش می‌دهد و در پیاده‌سازی‌های متداول پیام/Trap هم می‌فرستد. جزئیات وابسته به پلتفرم است. Shutdown پورت را Err-Disable می‌کند؛ بازیابی دستی با `shutdown` سپس `no shutdown` یا سازوکار `errdisable recovery` (در صورت پشتیبانی و پیکربندی) ممکن است. زمان بازیابی خودکار را طراحی کنید؛ فرض نکنید حتماً به Restart نیاز دارد.

## ۳. توپولوژی کاربرگ

**PNETLab مستقل — طراحی‌شده و اجرا‌نشده.**

```text
                DHCP Server 10.10.0.1 / DNS 10.10.0.1
                          |
                    [Gi0/1] (Trusted)
                          |
                    ┌──── SW1 ────┐  VLAN 10 · 10.10.0.0/24
                    |             |
              [Gi0/10]          [Gi0/20]
                    |             |
                 PC-A           PC-B
              10.10.0.50     10.10.0.51
              (Untrusted)    (Untrusted)
```

| مورد | مقدار | نقش |
|---|---|---|
| VLAN | 10 | تنها VLAN فعال |
| Pool | `10.10.0.50 – 10.10.0.200` | محدودهٔ DHCP؛ آدرس‌های `.50` و `.51` در خروجی نمونه داخل Pool فرض شده‌اند |
| Gi0/1 | Trusted | مسیر سرور DHCP و Gateway |
| Gi0/10–20 | Untrusted | کاربران |
| Switch Port Mode | `access` | همهٔ پورت‌های کاربر |

![نمودار قابل ویرایش کنترل‌های امنیت لایهٔ ۲؛ اجرا‌نشده](academy-images/sec-07-layer2.svg)

## ۴. پیکربندی به ترتیب اجرا

**همهٔ فرمان‌ها اجرا‌نشده‌اند.** ترتیب مهم است؛ اگر جابه‌جا شود، کاربران قطع می‌شوند.

### گام ۱ — پیش‌نیاز: VLAN و پورت Access

```text
enable
configure terminal
vlan 10
 name USERS
 exit
interface range GigabitEthernet0/10 - 20
 switchport mode access
 switchport access vlan 10
 exit
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 exit
```

بدون این پیش‌نیاز، DHCP Snooping روی هیچ پورتی اثر نمی‌گذارد. `ip dhcp snooping` روی سوییچی بدون VLAN فعال، جدول Binding خالی می‌سازد.

### گام ۲ — فعال کردن DHCP Snooping

```text
configure terminal
ip dhcp snooping
ip dhcp snooping vlan 10
```

- `ip dhcp snooping` — ویژگی را در کل سوییچ فعال می‌کند.
- `ip dhcp snooping vlan 10` — می‌گوید در کدام VLANها اعمال شود. بدون این خط، Snooping فعال است ولی روی هیچ VLANی کار نمی‌کند — یکی از رایج‌ترین دلایل «جدول Binding خالی است».

### گام ۳ — تعیین پورت Trusted

```text
interface GigabitEthernet0/1
 ip dhcp snooping trust
 exit
```

**تنها** پورتی که سرور واقعی به آن وصل است. اگر این را فراموش کنید، پاسخ سرور هم دور ریخته می‌شود و هیچ کلاینتی آدرس نمی‌گیرد. اگر اشتباهاً روی پورت کاربر بگذارید، مهاجم می‌تواند از همان پورت پاسخ بدهد.

### گام ۴ — Rate Limit روی پورت‌های کاربر

```text
interface range GigabitEthernet0/10 - 20
 ip dhcp snooping limit rate 10
 exit
```

مقدار ۱۰ پیام در ثانیه یک انتخاب طراحی است، نه توصیهٔ عمومی. کلاینت عادی چند پیام در ثانیه می‌فرستد؛ مقدار کم (مثلاً ۳) ممکن است کلاینت واقعی را هم قطع کند. اگر مقدار را خیلی بالا بگذارید، هیچ محافظتی نمی‌کند. مقدار مناسب به تعداد کلاینت‌های پشت پورت (مثلاً یک تلفن IP + یک PC = دو MAC) بستگی دارد.

### گام ۵ — فعال کردن DAI (فقط بعد از گام ۲ و ۳)

```text
configure terminal
ip arp inspection vlan 10
interface GigabitEthernet0/1
 ip arp inspection trust
 exit
```

- `ip arp inspection vlan 10` — بازرسی ARP را در VLAN 10 فعال می‌کند. روی پورت Untrusted، بسته باید با DHCP Snooping Binding یا ARP ACL/روش پشتیبانی‌شدهٔ دیگری اعتبارسنجی شود؛ وگرنه ممکن است Drop شود. پورت Trusted از این بررسی عبور می‌کند.
- `ip arp inspection trust` روی Gi0/1 در این طرح یعنی **تمام ARP ورودی از آن لینک** از DAI عبورِ بدون بازرسی دارد. فقط چون یک دستگاه «Gateway» است آن را Trusted نکنید؛ Trust گسترده، جعل ARP از همان لینک را هم عبور می‌دهد. برای میزبان ایستا ARP ACL را در نظر بگیرید.

اگر Gateway روی SVI خود Switch است، به‌خاطر Gateway بودن، پورت Uplink به روتر را خودکار Trusted نکنید؛ Trust را بر مبنای مسیر DHCP/ARP و ریسک هر VLAN تعیین کنید.

### گام ۶ — Port Security روی پورت‌های کاربر

```text
interface range GigabitEthernet0/10 - 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 exit
```

- `switchport port-security` — ویژگی را فعال می‌کند. این مثال از پورت Access ثابت استفاده می‌کند؛ برخی پلتفرم‌ها Port Security را روی Trunk هم با محدودیت‌های MAC/VLAN پشتیبانی می‌کنند، درحالی‌که پورت dynamic-access ممکن است مجاز نباشد. رابط Routed (`no switchport`) پورت لایهٔ ۲ برای این کنترل نیست. سازگاری و نحو را با Image هدف بررسی کنید.
- `maximum 2` — حداکثر دو MAC روی پورت. عدد ۲ انتخاب طراحی است: یک PC + یک تلفن IP. اگر فقط PC دارید، ۱ کافی است.
- `violation restrict` — بستهٔ متخلف دور ریخته و شمارنده/Log ثبت می‌شود. گزینهٔ امن‌تر از `protect` (که ردی نمی‌گذارد).
- `mac-address sticky` — MACهای یادگرفته‌شده به **Running Configuration** افزوده می‌شوند. برای ماندگاری پس از Reload باید Configuration را پس از یادگیری/تأیید MACها به Startup Configuration ذخیره کنید؛ این مرحله عمداً در مثال اجرا‌نشده است. جابه‌جایی تجهیز ممکن است تخلف بسازد؛ MACها را با رویهٔ تغییر کنترل‌شده پاک/به‌روزرسانی کنید.

## ۵. Verification و تفسیر خروجی

**نمونهٔ طراحی‌شده، اجرا‌نشده.**

```text
SW1# show ip dhcp snooping
Switch DHCP snooping is enabled
DHCP snooping is configured on following VLANs:
10
Insertion of option 82 is enabled
Interface                  Trusted    Rate limit (pps)
GigabitEthernet0/1         yes        unlimited
GigabitEthernet0/10        no         10
GigabitEthernet0/20        no         10
```

خط‌به‌خط:

- `Switch DHCP snooping is enabled` — ویژگی کلی روشن است.
- `VLANs: 10` — دستور `vlan 10` اعمال شده. اگر این‌جا خالی بود، گام ۲ ناقص است.
- `Insertion of option 82 is enabled` — سوییچ اطلاعات پورت و VLAN را در پیام DHCP تزریق می‌کند (**Option 82**). بعضی سرورهای DHCP نسبت به این گزینه حساس‌اند و باید بررسی شوند.
- `Trusted yes` روی Gi0/1 و `no` روی بقیه — همان چیزی که می‌خواستیم.

```text
SW1# show ip dhcp snooping binding
MacAddress          IpAddress        Lease(sec)  Type           VLAN  Interface
00:11:22:33:44:55   10.10.0.50       86000       dhcp-snooping  10    GigabitEthernet0/10
00:11:22:33:44:56   10.10.0.51       86000       dhcp-snooping  10    GigabitEthernet0/20
```

- `Type dhcp-snooping` — این رکورد از DHCP Snooping آمده، نه از Static Binding.
- جدول خالی یعنی یکی از این‌ها: Snooping روی VLAN فعال نیست، پورت Trusted اشتباه است، یا کلاینتی آدرس نگرفته.

```text
SW1# show ip arp inspection vlan 10
Source Mac Validation      : Disabled
Destination Mac Validation : Disabled
IP Address Validation      : Disabled

 Vlan     Configuration    Operation   ACL Match          Static ACL
 ----     -------------    ---------   ---------          -----------
   10     Enabled          Active      dhcp-snooping      No

 Vlan     ACL Logging      DHCP Logging
 ----     -----------      ------------
   10     Deny             Deny
```

- `ACL Match: dhcp-snooping` — DAI دارد از جدول DHCP Snooping استفاده می‌کند (نه از ACL دستی). این ستون ثابت می‌کند که وابستگی درست برقرار است.
- سه `Validation` خاموش — به‌طور پیش‌فرض DAI فقط MAC/IP را با Binding مقایسه می‌کند. فعال‌سازی Validation اضافی (مثلاً بررسی MAC مبدأ در ARP با Ethernet header) بررسی سخت‌گیرانه‌تر است و در شبکه‌های خاص می‌تواند ترافیک مشروع را هم دور بریزد. مقدار پیش‌فرض معمولاً کافی است.

```text
SW1# show ip arp inspection statistics
 Vlan      Forwarded        Dropped     DHCP Drops      ACL Drops
 ----      ---------        -------     ----------      ---------
   10             124             18             18              0
```

- `DHCP Drops 18` — ۱۸ بسته به‌دلیل عدم تطبیق با DHCP Snooping Bindingها Drop شده‌اند؛ این عدد به‌تنهایی جعلی‌بودن همهٔ بسته‌ها را ثابت نمی‌کند و می‌تواند Binding ناقص/منقضی یا ترافیک مشروعِ ناسازگار را هم نشان دهد. `ACL Drops 0` یعنی در این خروجی بسته‌ای با علت ACL Drop نشده است.

```text
SW1# show port-security interface GigabitEthernet0/10
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Restrict
Aging Time                 : 0 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 2
Total MAC Addresses        : 1
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 1
Last Source Address:Vlan   : 0011.2233.4455:10
Security Violation Count   : 0
```

- `Secure-up` — وضعیت سالم. مقادیر ممکن: `Secure-up`، `Secure-shutdown`، `Secure-down`.
- `Sticky MAC Addresses 1` — یک MAC به‌صورت خودکار به Running Configuration افزوده شده؛ برای ماندگاری پس از Reload باید Startup Configuration ذخیره شود.
- `Security Violation Count 0` — هنوز تخلفی رخ نداده. اگر دستگاه دیگری وصل شود، این عدد بالا می‌رود و پورت `Secure-up` می‌ماند (چون Restrict است).
- `Configured MAC Addresses 0` — ما MAC دستی تنظیم نکردیم؛ همه از Sticky آمده.

```text
SW1# show port-security
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
                (Count)       (Count)          (Count)
---------------------------------------------------------------------------
      Gi0/10              2            1                  0           Restrict
      Gi0/20              2            1                  0           Restrict
```

## ۶. عیب‌یابی

| نشانه | علت محتمل | بررسی | اصلاح |
|---|---|---|---|
| هیچ کلاینتی IP نمی‌گیرد | پورت سرور Trusted نیست | `show ip dhcp snooping` | `ip dhcp snooping trust` |
| جدول Binding خالی است | Snooping روی VLAN فعال نیست | ستون VLAN در `show ip dhcp snooping` | `ip dhcp snooping vlan 10` |
| جدول Binding خالی است | کلاینت Lease نگرفته، VLAN/پورت جا افتاده یا مسیر DHCP ناقص است | `show ip dhcp snooping` و `show ip dhcp snooping binding` | مسیر را پیدا کنید؛ فقط Uplink کنترل‌شده را در صورت نیاز Trusted کنید |
| بعد از فعال‌سازی DAI، ARP مشروع Drop می‌شود | Binding ناموجود/ناسازگار یا ARP ACL/Trust نادرست | `show ip arp inspection statistics` و Bindingها | ابتدا DHCP/Binding را اصلاح کنید؛ برای IP ثابت ARP ACL مناسب بسازید؛ Trust را کورکورانه گسترش ندهید |
| پورت با کابل سالم Down است | Port Security با Shutdown | `show interface status err-disabled` | `shutdown`/`no shutdown` |
| Port Security خطا می‌دهد | پورت Dynamic، رابط Routed یا ناسازگاری پلتفرم/Interface | `show interface switchport` و راهنمای مدل | فقط اگر پورت کاربر است آن را Access ثابت کنید؛ سازگاری Trunk را جدا بررسی کنید |
| IP می‌گیرد ولی DNS اشتباه است | سرور جعلی روی پورت Untrusted | بررسی Binding و پورت | Snooping را بررسی کنید |
| Option 82 مشکل ایجاد می‌کند | سرور DHCP به Option 82 حساس است | Log سرور | تنظیم سرور یا `no ip dhcp snooping information option` |

**سناریوی نقص طراحی‌شده (اجرا نشده):** یک لپ‌تاپ مهاجم روی `Gi0/15` (Untrusted) یک DHCP Server راه می‌اندازد و سعی می‌کند Gateway جعلی بدهد. سه رفتار را طراحی کرده‌ایم:

1. Snooping فعال است ولی Trusted درست تنظیم نشده → پاسخ مهاجم از Untrusted دور ریخته می‌شود، ولی پاسخ سرور واقعی هم دور ریخته می‌شود → قطع کامل.
2. Snooping و Trusted درست هستند → پاسخ مهاجم دور ریخته می‌شود؛ شبکه سالم می‌ماند.
3. Snooping فعال نیست و ARP ACL/Binding جایگزین هم تعریف نشده، ولی DAI فعال است → ARP بدون تطبیق روی پورت‌های Untrusted Drop می‌شود؛ رابط‌های Trusted از بازرسی عبور می‌کنند. اثر واقعی به پورت و VLAN وابسته است.

هیچ‌کدام اجرا نشده و زمان یا رفتار واقعی ثبت نشده است.

## ۷. کاربرگ مستقل PNETLab

1. سوییچ و کلاینتی را در VLAN 10 راه بیندازید و بدون هیچ کنترل، از DHCP آدرس بگیرید. جدول Binding را خالی نشان دهید.
2. `ip dhcp snooping` و `ip dhcp snooping vlan 10` را اجرا کنید. جدول Binding را ثبت کنید — هنوز خالی است.
3. پورت سرور را Trusted کنید و کاربر را `shutdown`/`no shutdown` کنید (یا Lease را تجدید کنید). جدول Binding را ثبت کنید.
4. پس از ایجاد Binding معتبر برای کلاینت DHCP، DAI را فعال کنید و عبور ARP مشروع را بررسی کنید. سپس در آزمایشگاه ایزوله یک میزبان IP ثابتِ بدون Binding را بررسی کنید؛ ARP ممکن است Drop شود. برای آن ARP ACL متناسب با پلتفرم طراحی کنید یا در صورت انتخاب Trust، فقط اثر و ریسک آن را روی لینک کنترل‌شده ثبت کنید—پورت کاربر را در شبکهٔ واقعی Trusted نکنید.
5. Port Security را فعال و MAC دوم را روی یک پورت وصل کنید. `Security Violation Count` را ثبت کنید.
6. یک لپ‌تاپ (مهاجم) روی پورت Untrusted برای DHCP جعلی تنظیم کنید و سه رفتار بخش ۶ را امتحان کنید.
7. `show ip arp inspection statistics` را قبل و بعد ثبت کنید.

**نکتهٔ مهم:** برای مرحلهٔ ۳ و ۵، **timing** مهم است: DHCP Lease را با `ipconfig /release` و `ipconfig /renew` (یا معادل لینوکسی) تجدید کنید تا جدول واقعاً پر شود. کابل را قطع و وصل کردن هم کار می‌کند.

هیچ‌کدام از این مراحل اجرا نشده است.

## ۸. سؤال‌ها و پاسخ

1. **اگر DHCP Snooping Binding موجود نباشد، DAI چه می‌کند؟** روی پورت Untrusted، ARP باید با Binding معتبر یا ARP ACL/روش پشتیبانی‌شدهٔ دیگر تطبیق کند؛ در غیر این صورت ممکن است Drop شود. پورت Trusted از این بررسی عبور می‌کند، بنابراین Trust جایگزین امنی برای Binding نیست و باید محدود باشد.

2. **آیا DHCP Snooping پیام Discover را از پورت Untrusted مسدود می‌کند؟** خیر؛ فقط پیام‌های سمت سرور. کلاینت باید بتواند درخواست بدهد.

3. **اگر Trusted را فراموش کنیم ولی Snooping فعال باشد، چه می‌شود؟** پاسخ سرور از پورت Untrusted دور ریخته می‌شود، هیچ کلاینتی آدرس نمی‌گیرد.

4. **آیا Port Security روی پورت Trunk کار می‌کند؟** روی بعضی Catalystها بله، با محدودیت‌ها و تنظیمات وابسته به مدل/نسخه؛ این مثال فقط Access Port است. پیش از استفاده روی Trunk، راهنمای پلتفرم و محدودیت‌های MAC/VLAN را بررسی کنید.

5. **تفاوت Protect و Restrict در Port Security چیست؟** هر دو بستهٔ متخلف را Drop می‌کنند؛ در پیاده‌سازی‌های معمول، Restrict شمارنده را افزایش و پیام/Trap می‌فرستد، درحالی‌که Protect گزارش‌دهی کمتری دارد. جزئیات را با پلتفرم هدف تطبیق دهید.

6. **Sticky چه مزیت و چه خطری دارد؟** MAC یادگرفته‌شده را به Running Configuration می‌افزاید؛ برای ماندگاری پس از Reload باید Configuration را ذخیره کنید و این رفتار را روی Image هدف بررسی کنید. جابه‌جایی دستگاه ممکن است نقض امنیتی بسازد؛ پاک‌سازی باید کنترل‌شده باشد.

7. **چرا Rate Limit پایین ممکن است کلاینت واقعی را قطع کند؟** پشت یک پورت ممکن است چند دستگاه باشد یا در Burst راه‌اندازی/تجدید Lease پیام‌های زیادی برسد؛ حد دقیق به پلتفرم و الگوی ترافیک وابسته است. آستانه را در محیط هدف بررسی کنید، نه با یک عدد عمومی.

8. **Option 82 چیست؟** سوییچ اطلاعات پورت و VLAN را در پیام DHCP تزریق می‌کند تا سرور بداند کلاینت از کجا آمده. بعضی سرورها این گزینه را نمی‌پذیرند و باید تنظیم شوند.

9. **MAC Flooding چطور بررسی می‌شود؟** با شمارش/رشد غیرعادی MACها و Violation/Logهای Port Security در صورت فعال‌بودن؛ فرمان و شمارنده به مدل وابسته است. MAC Flapping می‌تواند جابه‌جایی یا جعل را نشان دهد، اما به‌تنهایی اثبات MAC Flooding نیست.

10. **اگر Gateway روترِ Router-on-a-Stick باشد چه کنیم؟** DHCP Snooping و DAI روی سوییچ اعمال می‌شوند. پورت Trunk را خودکار Trusted نکنید: بسته‌های DHCP/ARP مشروع و نیاز به Binding را در توپولوژی بررسی کنید؛ Trust روی Trunk، ARP همهٔ VLANهای مجاز را از بازرسی عبور می‌دهد. فقط بر اساس طراحی و راهنمای پلتفرم، Trust یا ARP ACL را انتخاب کنید.

11. **بعد از Shutdown شدن پورت، خودش برمی‌گردد؟** ممکن است با Recovery پیکربندی‌شده خودکار برگردد؛ در غیر این صورت معمولاً `shutdown`/`no shutdown` لازم است. پشتیبانی و Timer را بررسی کنید.

12. **آیا این درس امنیت کامل شبکه را تأمین می‌کند؟** نه. این‌ها لایه‌ای محافظتی در لایهٔ ۲ هستند و روی لایه‌های بالاتر (ACL، Authentication، Port Isolation) باید تکمیل شوند.

## واژه‌نامه و چک‌لیست

DHCP Snooping: پایش ترافیک DHCP؛ **Trusted Port**: پورت مجاز؛ Untrusted: پورت کاربر؛ Binding Table: نگاشت MAC، IP، VLAN و پورت؛ **DAI**: بازرسی بسته‌های ARP؛ **Port Security**: محدودسازی MAC؛ **Err-Disable**: خاموشی محافظتی پورت.

- [ ] ترتیب راه‌اندازی را می‌دانم: VLAN → Snooping → Trusted → DAI → Port Security.
- [ ] می‌دانم DAI روی Untrusted ARP فاقد Binding/ARP ACL معتبر را Drop می‌کند.
- [ ] تفاوت گزارش‌دهی Protect و Restrict را با درنظرگرفتن Platform می‌دانم.
- [ ] Trust را محدود به لینک‌های کنترل‌شده و نیاز واقعی می‌کنم؛ صرفاً به‌خاطر Uplink بودن Trust نمی‌گذارم.
- [ ] می‌دانم Option 82 می‌تواند با سرور DHCP ناسازگار باشد.
