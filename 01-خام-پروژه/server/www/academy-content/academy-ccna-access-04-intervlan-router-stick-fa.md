# CCNA NA-04 — Inter-VLAN Routing با Router-on-a-Stick

**سطح:** CCNA. **پیش‌نیاز:** NA-01، NA-02 و IPv4. **هدف مرتبط:** `2.1.c` Configure and verify InterVLAN connectivity؛ این یک روش است، نه تمام روش‌های ممکن. **وضعیت:** توپولوژی، فرمان‌ها و خروجی‌ها طراحی‌شده و اجرا‌نشده‌اند؛ نسخهٔ Switch، Router و Client انتخاب نشده و کاربرگ به بازبینی عملی نیاز دارد.

## اهداف

توضیح دهید چرا بین VLANها Routing لازم است، Router-on-a-Stick را پیکربندی و بررسی کنید و خطاهای Trunk/Subinterface را عیب‌یابی کنید.

## ۱. چرا Routing؟

VLANهای جدا Broadcast Domainهای مستقلی دارند. اگر PC-A (`192.0.2.10/24`) مقصد `198.51.100.10` را ببیند، با Prefix خودش تشخیص می‌دهد مقصد دور است و Frame را به MAC Gateway `192.0.2.1` می‌دهد. Switch Frame ورودی Access را به VLAN 10 نسبت می‌دهد و هنگام عبور از Trunk، VLAN tag 10 می‌افزاید؛ R1 روی Subinterface متناظر Tag را می‌خواند، Route متصل VLAN 20 را انتخاب می‌کند و Frame جدید را با Tag 20 برمی‌گرداند. SW1 آن را روی Access Port VLAN 20 بدون Tag به PC-B تحویل می‌دهد. پاسخ نیز مسیر برگشت را طی می‌کند.

Router-on-a-Stick از یک لینک Trunk به Router و Subinterface جداگانه برای هر VLAN استفاده می‌کند. یک Switch لایهٔ ۳ با SVI روش دیگری است؛ در این درس پیکربندی SVI آموزش داده نمی‌شود. این طرح یک لینک فیزیکی مشترک و ظرفیت/نقطهٔ خرابی مشترک دارد؛ تعداد VLAN و کارایی را بدون سنجش/طراحی توسعه‌یافته مفروض نگیرید.

![نمودار قابل ویرایش کاربرگ؛ اجرا‌نشده](academy-images/na-04-intervlan.svg)

## ۲. توپولوژی و آدرس‌دهی — کاربرگ مستقل PNETLab

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده:** یک Switch لایهٔ ۲ پشتیبان Trunk، یک Router با Subinterface و 802.1Q، دو Client و سه لینک. نام تصویر، نسخه و دستور IP کلاینت‌ها باید پیش از اجرا انتخاب و ثبت شوند.

```text
PC-A ─ Gi0/1 [SW1] Gi0/24 ══ Trunk ══ Gi0/0 [R1]
PC-B ─ Gi0/2       VLAN 10,20             .10 / .20
```

| دستگاه | رابط | VLAN | آدرس | Gateway |
|---|---|---:|---|---|
| PC-A | به SW1 Gi0/1 | 10 | `192.0.2.10/24` | `192.0.2.1` |
| PC-B | به SW1 Gi0/2 | 20 | `198.51.100.10/24` | `198.51.100.1` |
| R1 | Gi0/0.10 | 10 | `192.0.2.1/24` | — |
| R1 | Gi0/0.20 | 20 | `198.51.100.1/24` | — |

آدرس‌ها مستنداتی‌اند. DHCP یا ACL در سناریو تنظیم نشده است. Client پیشنهادی VPCS است؛ نسخه و سینتکس در محیط هدف بررسی شوند. **فرمان‌های پیشنهادی، اجرا‌نشده:**

```text
PC-A> ip 192.0.2.10/24 192.0.2.1
PC-B> ip 198.51.100.10/24 198.51.100.1
```

## ۳. پیکربندی پیشنهادی

**فرمان‌ها اجرا‌نشده و وابسته به IOS هدف‌اند.** SW1:

```text
configure terminal
vlan 10
 name USERS
vlan 20
 name OTHER
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 no shutdown
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 20
 no shutdown
interface GigabitEthernet0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
end
```

دو VLAN ساخته می‌شوند، هر Client به VLAN خودش می‌رود و Trunk فقط VLANهای 10 و 20 را مجاز می‌کند. این دستور فهرست Allowed موجود را جایگزین می‌کند؛ فقط برای آزمایشگاه مستقل طراحی شده است. Native VLAN در این مثال برای ترافیک کاربر به کار نمی‌رود.

R1:

```text
configure terminal
interface GigabitEthernet0/0
 no shutdown
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.0.2.1 255.255.255.0
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 198.51.100.1 255.255.255.0
end
```

`no shutdown` رابط فیزیکی را اداری فعال می‌کند. `interface ... .10/.20` Subinterface را انتخاب می‌کند؛ `encapsulation dot1Q` VLAN تگ‌شده را مشخص می‌کند؛ `ip address` Gateway هر Subnet را می‌دهد. شمارهٔ Subinterface و VLAN را در این مثال یکسان انتخاب کرده‌ایم؛ آن‌ها دو مفهوم متفاوت‌اند.

## ۴. Verification

**فرمان‌های پیشنهادی و اجرا‌نشده:**

```text
SW1# show interfaces trunk
SW1# show interfaces GigabitEthernet0/24 switchport
SW1# show vlan brief
R1# show ip interface brief
R1# show interfaces GigabitEthernet0/0.10
R1# show interfaces GigabitEthernet0/0.20
R1# show ip route connected
R1# show ip arp
```

**خروجی آموزشی، نه نتیجهٔ واقعی:**

```text
R1# show ip interface brief
Interface              IP-Address       OK? Method Status  Protocol
GigabitEthernet0/0.10  192.0.2.1        YES manual up      up
GigabitEthernet0/0.20  198.51.100.1     YES manual up      up
```

هر خط آدرس و وضعیت یک Subinterface را نشان می‌دهد. `show interfaces trunk` VLANهای مجاز/فعال و وضعیت Trunk را طبق نسخه نشان می‌دهد؛ `show ... switchport` برای Mode و Native/Access state کمک می‌کند؛ `show ip route connected` مسیرهای متصل و `show ip arp` نگاشت‌های IPv4/Layer 2 را می‌سنجند. رابط `up/up` به‌تنهایی تحویل Tag، پاسخ Client یا سیاست امنیتی را اثبات نمی‌کند؛ آن‌ها را با ترافیک کنترل‌شده و چند شاهد تطبیق دهید.

پس از تنظیم آدرس‌ها، در محیط مجاز ابتدا هر PC، Gateway خود و سپس مقصد دیگر را Ping کند. انتظار آموزشی پاسخ است، اما فایروال Client، مسیر و وضعیت سرویس می‌توانند مؤثر باشند؛ هیچ نتیجه‌ای ثبت نشده است.

## ۵. عیب‌یابی

| نشانه | ترتیب بررسی | محدودیت نتیجه |
|---|---|---|
| PC به Gateway خودش نمی‌رسد | IP/Mask و ARP Client؛ Access VLAN/Port؛ VLAN موجود و active؛ Trunk مجاز و up؛ Parent Interface؛ encapsulation/Address Subinterface | Ping ناموفق به‌تنهایی کدام لایه را مقصر نمی‌کند |
| PC Gateway دارد ولی VLAN دیگر را نمی‌گیرد | Subinterface مقصد و Tag؛ Connected Route هر دو Subnet؛ PC/Gateway مقصد و مسیر برگشت؛ ACL/Firewall و Host Service | Gateway پاسخ‌گو بودن سرویس/Host مقصد را ثابت نمی‌کند |
| Subinterface `down/down` یا `up/down` است | Parent physical، کابل/پورت، وضعیت Line Protocol، Trunk و سازگاری Platform/Image | پیام و Status دقیق بین IOS/Emulator فرق دارد |
| فقط یک VLAN عبور می‌کند | `show interfaces trunk`، VLAN Allowed/Active، Access VLAN، تطابق `encapsulation dot1Q <id>` و Subnet Gateway | وجود VLAN در Database به معنی عبورش از Trunk نیست |
| PC-A و PC-B هر دو IP درست دارند اما همدیگر را نمی‌بینند | هر مقصد را جدا Ping کنید؛ ARP برای Gateway، RIB/Connected Route، ACL و Host Firewall را تطبیق دهید | ICMP ممکن است مسدود باشد؛ برنامهٔ کاربردی جدا Verify می‌شود |

### نقص کنترل‌شده، بازیابی و معیار موفقیت

**فقط در PNETLab ایزوله و پس از Snapshot؛ فرمان‌ها طراحی‌شده و اجرا‌نشده‌اند.** ابتدا از PC-B به Gateway `198.51.100.1` و از PC-A به Gateway `192.0.2.1`، سپس میان دو PC آزمون بگیرید و خروجی‌های پایه را ثبت کنید. یک متغیر را تغییر دهید: روی R1، Tag زیررابط VLAN 20 را موقتاً از 20 به 30 تغییر دهید:

```text
configure terminal
interface GigabitEthernet0/0.20
 encapsulation dot1Q 30
end
```

با `show running-config interface GigabitEthernet0/0.20` و `show interfaces trunk`، اختلاف Tag=30 با VLANهای مجاز 10,20 را پیدا کنید؛ از `up/up` بودن احتمالی رابط به‌تنهایی نتیجه نگیرید. Ping PC-B به Gateway/PC-A را دوباره بگیرید؛ در طرح، ترافیک VLAN 20 به زیررابط مورد انتظار نگاشت نمی‌شود. سپس فقط همان Tag را به `encapsulation dot1Q 20` بازگردانید، Gateway و ارتباط بین VLANها را دوباره آزمایش و بازیابی را ثبت کنید. هرگز این نقص را روی شبکهٔ عملیاتی وارد نکنید.

**معیار موفقیت/تحویل:** SW1 Trunk را در حالت عملیاتی با VLANهای 10 و 20 مجاز نشان دهد؛ هر دو Subinterface روی R1، Tag و آدرس درست داشته و Routeهای Connected متناظر دیده شوند؛ Clientها IP/Mask/Gateway مطابق جدول داشته باشند؛ Ping هر Client به Gateway و ارتباط بین VLANها آزمایش شود؛ نقص Tag با شاهد شناسایی، Restore و آزمون موفقِ پس از بازیابی ثبت شود. تحویل شامل Image/نسخه، نام Interface، `show interfaces trunk`, `show ip interface brief`, `show ip route connected`, پیکربندی Subinterface و نتایج Client در سه حالت پایه/نقص/بازیابی است. خروجی‌ها باید زمان‌دار و از راز/اطلاعات سازمانی پاک‌سازی شوند. هیچ خروجی واقعی در این سند وجود ندارد.

## ۶. سؤال‌های سناریویی

1. **چرا میان VLANها Routing لازم است؟** Broadcast Domain و Subnetهای مجزا به تصمیم لایهٔ ۳ نیاز دارند.
2. **Router-on-a-Stick چه می‌کند؟** چند Subinterface روی یک Trunk برای VLANهای جدا فراهم می‌کند.
3. **Gateway PC-A چیست؟** `192.0.2.1` در سناریوی طراحی‌شده.
4. **`encapsulation dot1Q 20` چیست؟** اتصال Subinterface به VLAN تگ‌شدهٔ 20 در IOS پشتیبان.
5. **شمارهٔ `.20` همیشه باید 20 باشد؟** خیر؛ شمارهٔ Subinterface و VLAN دو مفهوم جدا هستند.
6. **Trunk بدون VLAN 20 چه اثری دارد؟** ارتباط مربوط به VLAN 20 از آن لینک عبور مورد انتظار نخواهد داشت.
7. **Gateway پاسخ می‌دهد؛ PC-B حتماً پاسخ می‌دهد؟** خیر؛ مقصد، مسیر برگشت و فایروال هم مهم‌اند.
8. **آیا DHCP در این سناریو تنظیم شده؟** خیر؛ آدرس‌دهی Client باید جدا انجام شود.
9. **آیا SVI تنها روش Routing است؟** خیر؛ این مثال از Router Subinterface استفاده می‌کند.
10. **آیا خروجی نمونه واقعی است؟** خیر، طراحی و اجرا‌نشده است.
11. **`allowed vlan` چه خطری در محیط واقعی دارد؟** می‌تواند فهرست مجاز موجود را جایگزین کند.
12. **آیا VLAN به‌تنهایی ACL است؟** خیر؛ سیاست دسترسی جداست.

## واژه‌نامه و چک‌لیست

Inter-VLAN Routing: مسیریابی میان VLANها؛ Subinterface: رابط منطقی روی رابط فیزیکی؛ dot1Q: Encapsulation VLAN؛ Gateway: مقصد Next Hop برای شبکه‌های دیگر.

- [ ] دو Gateway و Tag را از جدول تشخیص می‌دهم.
- [ ] Trunk و مسیر برگشت را جداگانه بررسی می‌کنم.
- [ ] وابستگی دستور Client به نسخه و اجرا‌نشدن کاربرگ را ثبت می‌کنم.
