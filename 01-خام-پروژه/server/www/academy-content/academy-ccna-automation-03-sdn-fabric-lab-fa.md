# AUT-03 — کاربرگ مستقلِ Underlay و VXLAN: طراحی کنترل‌گر در برابر Data Plane

**پیوند رسمی:** CCNA v1.1 `6.3` — Describe controller-based / software-defined architecture, overlay, underlay, fabric. **وضعیت:** سناریو و مراحل طراحی شده‌اند؛ این سند عمداً اجرای یک Controller واقعی یا SD-Access را ادعا نمی‌کند. در محیط جاری، Underlay مبتنی بر Linux network namespace واقعاً آزموده شد؛ ساخت Interface VXLAN شکست خورد (`Error: Unknown device type.`)، بنابراین Overlay و ارتباط End-to-End اجرا/تأیید نشده‌اند. هیچ IOS، PNETLab، Catalyst Center، API یا Controller در دسترس نبود.

## مرز این کاربرگ

این آزمایش دو بخش با سطح اطمینان متفاوت دارد:

1. **Underlay قابل‌اجرا با iproute2:** دو namespace به‌وسیلهٔ یک جفت veth و شبکهٔ `/30` وصل می‌شوند؛ دسترسی IP دوطرفه را می‌توان مستقل آزمود. در این Sandbox، همین بخش موفق شد.
2. **Overlay داده‌صفحه‌ای VXLAN روی Linux:** دو VTEP، دو Bridge و دو Endpoint، با VNI 100 و UDP/4789 طراحی شده‌اند. اجرای آن به پشتیبانی VXLAN در Kernel نیاز دارد؛ این Kernel نوع دستگاه VXLAN را نمی‌پذیرد و گام ساخت VXLAN اجرا نشد.

این طرح **Controller-based fabric کامل نیست**: هیچ کنترل‌گر، پروتکل جنوب‌سو، توزیع پویا/EVPN، نقشهٔ Endpoint، Policy مرکزی، HA یا Border به شبکهٔ بیرونی پیاده‌سازی نمی‌شود. فرمان‌های Linux زیر تنظیم مستقیم Data Plane و Underlay در میزبان آزمایش هستند؛ آن‌ها را فرمان Catalyst Center، OpenFlow یا IOS جا نزنید. بخش Controller در این تمرین، معماریِ مورد تحلیل است، نه برنامه‌ای که در محیط حاضر اجرا شده باشد.

## ۱. سناریو و توپولوژی

دو Edge/VTEP فرضی می‌خواهند دو Endpoint را در یک Segment منطقی قرار دهند. Underlay فقط بین آدرس‌های VTEP اتصال IP فراهم می‌کند؛ Overlay قرار است Ethernet داخلی را در VXLAN حمل کند.

```text
        Endpoint-A                                  Endpoint-B
      192.0.2.10/24                               192.0.2.20/24
          | pa/ha                                      | pb/hb
   +------+-------+                             +------+-------+
   | VTEP-A       |==== Underlay IPv4 /30 =====| VTEP-B       |
   | 198.51.100.1 |       UDP/4789, VNI 100     | 198.51.100.2 |
   | br10 + vx100 |                             | vx100 + br10 |
   +--------------+                             +--------------+
       یک Broadcast Domain منطقی، در صورت ساخت موفق VXLAN
```

| گره/لایه | Interface | آدرس یا پارامتر | نقش |
|---|---|---|---|
| VTEP-A / Underlay | `ua` | `198.51.100.1/30` | آدرس محلی VTEP و مسیر IP به VTEP-B |
| VTEP-B / Underlay | `ub` | `198.51.100.2/30` | آدرس محلی VTEP و مسیر برگشت |
| VXLAN سمت A و B | `vx100` | VNI `100`, UDP destination `4789` | کپسوله‌سازی Ethernet؛ remote VTEP به‌صورت Static Unicast |
| Bridge سمت A و B | `br10` | بدون IP مدیریتی در این مثال | اتصال Endpoint محلی به VXLAN |
| Endpoint-A | `ha` | `192.0.2.10/24` | گرهٔ آزمایش‌شده در Segment منطقی |
| Endpoint-B | `hb` | `192.0.2.20/24` | گرهٔ آزمایش‌شده در همان Prefix منطقی |

همهٔ آدرس‌ها از بلوک‌های مستنداتی‌اند و فقط در محیط ایزوله به‌کار روند. این توپولوژی جای Routing/Border واقعی را نمی‌گیرد.

## ۲. تفکیک Controller، Control Plane و Data Plane

| جزء | نقش در یک Fabric واقعی | در این تمرین |
|---|---|---|
| **Management / Controller** | دریافت Intent/Policy، نگاشت Endpoint/VNI، ترجمهٔ Intent به پیکربندی و هماهنگی چند Node | **وجود ندارد.** هیچ API یا Controller اجرا نمی‌شود؛ نقشهٔ این سند فقط Intent آموزشی است. |
| **Control Plane** | یادگیری/توزیع اطلاعات Endpoint و Reachability، انتخاب/نصب مسیر یا Tunnel؛ سازوکار تابع معماری (مثلاً EVPN در برخی پیاده‌سازی‌ها) | **پویا نیست.** مقصد Remote به‌صورت Static در هر VTEP تعریف می‌شود؛ هیچ EVPN/LISP یا پروتکل کنترلی اجرا نمی‌شود. |
| **Underlay** | رساندن IP بیرونی بین VTEPها؛ باید مسیر و MTU مناسب داشته باشد | دو IP در `/30` روی veth؛ Route مستقیم Connected، بدون OSPF و بدون مسیر فیزیکی. |
| **Data Plane** | کپسوله‌سازی/Decapsulation، Bridge و Forward کردن Frame | در صورت پشتیبانی Kernel: Linux VXLAN و Bridge؛ در Sandbox ساخته نشد و ترافیک عبور نکرد. |
| **Fabric** | ترکیب Underlay، Overlay، Control Plane، Edge/Border و Policy مطابق محصول | این سند تنها یک **مدل آموزشی کوچک Underlay/Overlay** است، نه Fabric سازمانی یا Cisco SD-Access. |

در معماری Controller-based واقعی، Controller عموماً Policy/State را محاسبه می‌کند و از APIهای پشتیبانی‌شده به Nodeها می‌رساند؛ Packet کاربران معمولاً در Data Plane تجهیزات Forward می‌شود، نه از خود Dashboard. نوع Controller، southbound protocol، Control Plane و fail mode را باید در محصول/نسخهٔ واقعی جداگانه مشخص کرد؛ این کاربرگ دربارهٔ آن‌ها Command ساختگی نمی‌دهد.


## ۲.۱ تمرین تحلیلی: کدام Plane در این رویداد درگیر است؟

برای Endpoint-A به Endpoint-B مسیر را با چهار گام توضیح دهید: Ethernet داخلی به `br10` می‌رسد؛ در صورت ساخت موفق، `vx100` آن را با VNI 100 در UDP/IP بیرونی می‌پیچد؛ Underlay بستهٔ بیرونی را به VTEP مقصد می‌رساند؛ VTEP مقصد آن را باز می‌کند و Bridge به Endpoint محلی می‌دهد. در همین کاربرگ، `remote` به‌صورت ثابت در هر دو Linux VTEP نوشته می‌شود؛ Controller، EVPN/LISP و توزیع پویای Endpoint وجود ندارد.

| رویداد | جزء/Plane محتمل | چه چیزی را در همین کاربرگ می‌توان سنجید؟ | محدودیت نتیجه |
|---|---|---|---|
| `ua` در VTEP-A پایین می‌آید | Underlay و در پی آن Data Plane تونل | Route و Ping دو VTEP؛ در صورت ساخت VXLAN، ترافیک Endpoint | لینک تک‌مسیره است؛ failover یا Controller آزموده نمی‌شود |
| پیکربندی Static `vx100` اشتباه است | تنظیم محلی/Overlay Data Plane | local/remote/VNI/Bridge و Counter/FDB در Kernel پشتیبان | این خطا شاهد نقص Controller نیست؛ Controller در Lab وجود ندارد |
| API/Controller یک Fabric واقعی قطع می‌شود | Management/Control Planeِ محصول | در این Lab قابل‌اجرا نیست؛ در محصول واقعی باید API/cluster health و رفتار forwarding را جدا سنجید | ادامهٔ Forwarding موجود/تغییرات جدید وابسته به پلتفرم، نسخه، cache/state و fail mode است؛ از نام «Controller» به‌تنهایی نتیجه نگیرید |
| `ip link ... type vxlan` با `Unknown device type` رد می‌شود | پیش‌نیاز Feature در Kernel/محیط | خطای ساخت و نسخهٔ ابزار/Kernel را ثبت کنید | Underlay موفق نه VXLAN را می‌سازد و نه Control Plane/Fabric را تأیید می‌کند |

**تحویل تحلیلی:** برای یک Fabric مورد مطالعه، نام محصول/نسخه و سند مرجع را ثبت کنید؛ سپس Controller/Management، Control Plane، Underlay و Data Plane را در چهار ستون جدا قرار دهید و برای قطع Controller و قطع Underlay دو پیش‌بینی متفاوت بنویسید. پاسخ قابل قبول باید وابستگی Fail Mode به محصول را ذکر کند و هیچ رفتار مشاهده‌نشده‌ای را «واقعی» ننامد.

**اگر VXLAN در Kernel در دسترس نبود:** این مرحله را به‌عنوان Feature unsupported متوقف کنید؛ Underlay و تحلیل جدول بالا همچنان قابل تحویل‌اند. وضعیت Overlay/Controller را «اجرا نشده» ثبت کنید، نه موفق و نه شکست رفتاری Fabric.


## ۳. پیش‌نیاز، ایمنی و نسخه

- میزبان Linux با `iproute2`، فرمان `ip` و `bridge`، `ping` و مجوز `CAP_NET_ADMIN`/`sudo`؛ چهار namespace موقت ساخته می‌شود.
- برای Overlay علاوه بر iproute2، **Kernel باید VXLAN netdevice را پشتیبانی کند**. `ip link help vxlan` فقط Syntax ابزار کاربر را نشان می‌دهد؛ وجود Feature را ثابت نمی‌کند. آزمون واقعی Feature همان ساخت `type vxlan` در گام ۵ است.
- آدرس‌ها فقط روی namespaceهای آزمایش و در محیط بدون اتصال به شبکهٔ سازمانی/اینترنت استفاده شوند. دستورها را روی NIC یا Namespace میزبان عملیاتی اجرا نکنید. هیچ `flush` سراسری یا تغییر مسیر میزبان لازم نیست.
- نسخهٔ محیط ثبت‌شده در Sandbox این سند: `iproute2 6.1.0`. Kernel VXLAN قابل استفاده نبود؛ نسخه/Feature Kernel در این محیط به‌عنوان پشتیبانی تأیید نمی‌شود.

## ۴. ساخت و Verification مستقل Underlay

در Terminal یک میزبان Linux ایزوله اجرا کنید. اگر Terminal از قبل با دسترسی Root باز است، پیشوند `sudo` را بردارید. نام namespace و interfaceها در این مثال رزرو و موقت‌اند؛ پیش از اجرا مطمئن شوید تکراری نیستند.

```sh
sudo ip netns add vtepa
sudo ip netns add vtepb
sudo ip netns add hosta
sudo ip netns add hostb

sudo ip link add ua type veth peer name ub
sudo ip link set ua netns vtepa
sudo ip link set ub netns vtepb
sudo ip -n vtepa addr add 198.51.100.1/30 dev ua
sudo ip -n vtepb addr add 198.51.100.2/30 dev ub
sudo ip -n vtepa link set lo up
sudo ip -n vtepb link set lo up
sudo ip -n vtepa link set ua up
sudo ip -n vtepb link set ub up
```

ابتدا فقط Underlay را بیازمایید؛ پیش از موفقیت این مرحله به VXLAN نروید:

```sh
sudo ip -n vtepa route get 198.51.100.2
sudo ip -n vtepb route get 198.51.100.1
sudo ip netns exec vtepa ping -c 2 -W 1 -n 198.51.100.2
sudo ip netns exec vtepb ping -c 2 -W 1 -n 198.51.100.1
```

**انتظار:** هر دو Route از Interface مستقیم خود بیرون بروند و دو Ping، در صورت اجرای موفق، `2 received, 0% packet loss` داشته باشند. این فقط Underlay را می‌آزماید؛ نه VXLAN، نه Bridge و نه دسترسی Endpointها را.

## ۵. ساخت Endpointها و Overlay — فقط اگر Kernel پشتیبانی می‌کند

لینک‌های Endpoint را بسازید و آدرس‌دهی کنید:

```sh
sudo ip link add pa type veth peer name ha
sudo ip link set pa netns vtepa
sudo ip link set ha netns hosta
sudo ip link add pb type veth peer name hb
sudo ip link set pb netns vtepb
sudo ip link set hb netns hostb
sudo ip -n hosta addr add 192.0.2.10/24 dev ha
sudo ip -n hostb addr add 192.0.2.20/24 dev hb
sudo ip -n hosta link set lo up
sudo ip -n hostb link set lo up
sudo ip -n vtepa link set pa up
sudo ip -n vtepb link set pb up
sudo ip -n hosta link set ha up
sudo ip -n hostb link set hb up
```

Bridgeهای خالی را ایجاد کنید؛ سپس گام VXLAN را آزمایش کنید:

```sh
sudo ip -n vtepa link add br10 type bridge
sudo ip -n vtepb link add br10 type bridge
sudo ip -n vtepa link set br10 up
sudo ip -n vtepb link set br10 up

sudo ip -n vtepa link add vx100 type vxlan id 100 local 198.51.100.1 remote 198.51.100.2 dev ua dstport 4789
sudo ip -n vtepb link add vx100 type vxlan id 100 local 198.51.100.2 remote 198.51.100.1 dev ub dstport 4789
```

اگر هر فرمان `type vxlan` خطا داد، همان‌جا متوقف شوید، پیام/Kernel و نسخه را ثبت کنید و نتیجه را **«Overlay با این Kernel قابل اجرا نبود»** بنویسید؛ به‌جای آن فرمان دیگری را حدس نزنید. در صورت ساخت موفق هر دو Tunnel:

```sh
sudo ip -n vtepa link set pa master br10
sudo ip -n vtepb link set pb master br10
sudo ip -n vtepa link set vx100 master br10
sudo ip -n vtepb link set vx100 master br10
sudo ip -n vtepa link set vx100 up
sudo ip -n vtepb link set vx100 up
sudo ip netns exec hosta ping -c 3 -W 1 -n 192.0.2.20
sudo ip netns exec hostb ping -c 3 -W 1 -n 192.0.2.10
sudo ip -n vtepa -d link show vx100
sudo ip -n vtepb -d link show vx100
sudo ip netns exec vtepa bridge fdb show
```

**انتظار طراحی‌شده، نه نتیجهٔ این Sandbox:** هر دو Interface VXLAN باید VNI `100`، آدرس local/remote صحیح و پورت مقصد `4789` را گزارش کنند؛ اگر مسیر، MTU و Firewall اجازه دهند، Hostها در یک Prefix منطقی به Ping پاسخ دهند و Bridge/FDB دربارهٔ MACها مدخل یادگرفته‌شده نشان دهد. شکل دقیق خروجی Kernel-محور است. Ping کوچک MTU برای inner packet برابر 1500 را ثابت نمی‌کند؛ در این مثال برای inner IP MTU=1500، سربار IPv4/UDP/VXLAN و Ethernet داخلی در محاسبهٔ رایج حدود 50 بایت است و MTU تمام مسیر باید جدا بررسی شود.

## ۶. نقص کنترل‌شده، عیب‌یابی و بازیابی

فقط پس از موفق‌شدن کامل Overlay و Snapshot/ثبت حالت پایه اجرا شود:

1. از `hosta` به `192.0.2.20` سه Ping بگیرید و خروجی/زمان را ثبت کنید.
2. فقط Underlay سمت A را خاموش کنید: `sudo ip -n vtepa link set ua down`.
3. Ping را دوباره اجرا و شکست/افت را ثبت کنید. `ip -n vtepa route get 198.51.100.2`، `ip -n vtepa -s link show ua` و `ip -n vtepa -d link show vx100` را بررسی کنید.
4. Underlay را برگردانید: `sudo ip -n vtepa link set ua up`; ابتدا Ping دو VTEP و سپس Ping دو Endpoint را دوباره بگیرید.
5. اگر Overlay خودکار بازیابی نشد، Interfaceها را حذف نکنید؛ `link`, VNI, local/remote, route و FDB دو سمت را ثبت، علت را مرحله‌ای پیدا و در پایان فقط namespaceهای همین Lab را پاک کنید.

| نشانه | ترتیب بررسی مستقل |
|---|---|
| VTEP-A و VTEP-B Ping ندارند | Interface/آدرس `/30`، Link state، Route lookup و سمت Peer؛ هنوز VXLAN را عیب‌یابی نکنید |
| Underlay سالم است ولی VXLAN ساخته نمی‌شود | قابلیت Kernel، نوع خطای `type vxlan` و Syntax iproute2؛ ساخت موفق یک سمت کافی نیست |
| VXLAN ساخته شده، Hostها Ping ندارند | `master br10` و Link state دو سمت، VNI/local/remote/UDP، آدرس/Prefix Endpoint، route برگشت و Firewall UDP/4789 |
| بستهٔ کوچک رد می‌شود ولی بزرگ نه | MTU تمام Underlay، سربار واقعی، PMTUD/ICMP و MTU VXLAN/Bridge؛ MSS فقط TCP را محدود می‌کند |
| VTEP Link up ولی MAC/FDB خالی است | ترافیک واقعاً ارسال شده؟ Bridge portها Up/Master هستند؟ learning/FDB و خطاهای RX/TX را بررسی کنید |

### پاک‌سازی ایمن

پس از ذخیرهٔ شواهد فقط namespaceهای ساخته‌شده در همین تمرین را حذف کنید:

```sh
sudo ip netns del hosta
sudo ip netns del hostb
sudo ip netns del vtepa
sudo ip netns del vtepb
```

Namespace deletion، رابط‌های درون آن را نیز حذف می‌کند. از `ip link delete` روی رابط‌های میزبان اصلی یا `ip netns`های متعلق به کاربر دیگر استفاده نکنید.

## ۷. شواهد و معیار پذیرش

| بخش | شاهد قابل تحویل | معیار موفقیت |
|---|---|---|
| Underlay | نسخهٔ `iproute2`/Kernel، `ip route get` و Ping زمان‌دار هر دو جهت | هر دو VTEP به آدرس مقابل می‌رسند؛ اگر نه، ادامهٔ Overlay متوقف می‌شود |
| Overlay/Control state | `ip -d link show vx100` در هر دو سمت، VNI و local/remote و `bridge fdb show` | هر دو VTEP پارامتر سازگار دارند، MACهای Endpoint یادگرفته می‌شوند و Ping Endpoint برقرار است؛ این شرط فقط در Kernel پشتیبان قابل سنجش است |
| Controlled fault | خروجی پیش/حین/پس از Down/Up لینک Underlay | قطع مسیر باعث از دست‌رفتن ارتباط وابسته شود و پس از Restore ارتباط بازگردد؛ رفتار/زمان دقیق ثبت شود |
| معماری | برچسب نقش Controller/Control Plane/Underlay/Data Plane و محدودیت‌ها | دانشجو نبود Controller/EVPN در این Lab را صریح می‌گوید و آن را SD-Access یا Fabric کامل نمی‌نامد |
| واقعیت اجرا | وضعیت جداگانهٔ هر بخش: اجرا شد / به‌علت Feature اجرا نشد / طراحی‌شده | موفقیت Underlay به‌تنهایی به‌عنوان موفقیت VXLAN یا Fabric گزارش نمی‌شود |

## ۸. اجرای واقعی انجام‌شده در Sandbox حاضر

در `2026-11-20` با `iproute2-6.1.0`، دو namespace و veth جفت‌شده با `198.51.100.1/30` و `.2/30` ساخته شدند؛ Ping هر دو جهت **۲/۲ و ۰% loss** بود. سپس با همین IPها تلاش شد `type vxlan id 100 ... dstport 4789` ایجاد شود؛ Kernel پاسخ `Error: Unknown device type.` داد. Namespaceهای آزمایش با `trap` پاک شدند. `ip link help vxlan` در iproute2 Syntax گزینه‌ها را نشان می‌دهد، ولی پشتیبانی Kernel را ثابت نمی‌کند.

**نتیجه:** Underlay مینی‌آزمایش واقعاً اجرا و تأیید شد؛ Overlay، Endpoint-to-Endpoint، نقص تونل و Controller **آزموده نشدند**. این محدودیت به محیط Sandbox مربوط است و دربارهٔ هر Image PNETLab یا سخت‌افزار دیگر نتیجه نمی‌دهد.

## واژه‌نامه و چک‌لیست

VTEP: نقطهٔ پایانی تونل؛ VNI: شناسهٔ شبکهٔ VXLAN؛ Underlay: شبکهٔ IP حامل؛ Overlay: شبکهٔ منطقی روی حامل؛ Control Plane: محاسبه/توزیع state مسیر؛ Data Plane: Forwarding بسته؛ Controller: سامانهٔ مدیریت/برنامه‌ریزی، نه مسیر عبور Packet.

- [ ] Underlay را مستقل از VXLAN بررسی می‌کنم.
- [ ] Controller و Control Plane را با Data Plane یکی نمی‌گیرم.
- [ ] فرمان‌های Linux را به IOS/Controller نسبت نمی‌دهم.
- [ ] نتیجهٔ Unsupported Kernel یا طراحی را اجرای موفق تلقی نمی‌کنم.
