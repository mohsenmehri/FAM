# IS-07 — کاربرگ مستقل QoS: Classification، Marking، Shaping و صف خروجی

**پیوند رسمی:** CCNA v1.1 `4.7` — Explain QoS forwarding per-hop behavior. **این کاربرگ آزمایش طراحی‌شده است، نه خروجی اجراشده.** پلتفرم منتخب برای Syntax این طرح `Cisco C8000V / IOS XE 17.9.4` با IOS XE MQC است؛ Image هدف در Sandbox موجود نیست و پشتیبانی H-QoS/LLQ در آن Verify نشده است. چنین Image/Router در Sandbox حاضر نیست و Syntax، محدودیت رزرو Scheduler، H-QoS و نام Interface روی آن تأیید نشده‌اند. اگر Image واقعی فرمان‌های مشخص‌شده را نپذیرفت، متوقف شوید و آن را گزارش کنید؛ دستور جایگزین حدسی وارد نکنید.

## ۱. هدف و مرز آزمایش

این Lab نشان می‌دهد یک روتر مرزی چگونه ترافیک آزمایشی را در ورودی شناسایی/علامت‌گذاری می‌کند و در خروجیِ گلوگاه، Shaping و Per-Hop Queueing به‌کار می‌گیرد. اندازه‌گیری QoS فقط روی همان گره و جهت خروجی معتبر است؛ این تمرین کیفیت انتهابه‌انتها یا تجربهٔ واقعی تماس VoIP را ثابت نمی‌کند.

- **Classification/Marking:** Ruleها روی R1 بر اساس جریان‌های مشخص‌شدهٔ Source/Destination/UDP Port؛ علامت‌های آزمایش EF، AF21، AF41، AF11 و CS1.
- **Queueing/Scheduling:** Policy فرزند روی خروجی R1؛ LLQ برای کلاس Voice و CBWFQ برای کلاس‌های دیگر.
- **Shaping:** Policy والد خروجی را به نرخ طراحی‌شدهٔ `10 Mbps` محدود می‌کند تا رقابت در صف همان R1 قابل مشاهده باشد.
- **Policing:** در این سناریو پیکربندی نمی‌شود؛ اثر آن در IS-07 مفهومی جداگانه توضیح داده شده است. Policing را با Shaping یا با LLQ یکی نگیرید.
- **جریان‌های تست:** `iperf3` فقط UDP/TCP آزمایشی می‌فرستد؛ این Packetها RTP، SIP یا Web واقعی نیستند.

## ۲. توپولوژی و جدول آدرس‌دهی

```text
Linux GEN ─── R1 Gi0/0 ── R1 Gi0/1 ===== R2 Gi0/0 ── R2 Gi0/1 ─── Linux SVC
192.0.2.10/24   .1/24       198.51.100.1/30  .2/30         .1/24      203.0.113.10/24
                   LAN-MARK input       WAN-SHAPE output
```

| Node | Interface | IPv4/Prefix | Gateway/Neighbor | نقش و محدودیت |
|---|---|---|---|---|
| GEN | `eth0` | `192.0.2.10/24` | `192.0.2.1` | Linux generator؛ همهٔ جریان‌ها از این آدرس می‌آیند |
| R1 | `Gi0/0` | `192.0.2.1/24` | — | LAN؛ محل `service-policy input LAN-MARK` |
| R1 | `Gi0/1` | `198.51.100.1/30` | R2 `198.51.100.2` | لینک آزمایشی؛ محل `service-policy output WAN-SHAPE` |
| R2 | `Gi0/0` | `198.51.100.2/30` | R1 `198.51.100.1` | مسیر بازگشت به LAN |
| R2 | `Gi0/1` | `203.0.113.1/24` | — | LAN سرور |
| SVC | `eth0` | `203.0.113.10/24` | `203.0.113.1` | Linux `iperf3` server روی چند پورت آزمایش |

آدرس‌ها از Prefixهای مستنداتی هستند؛ فقط در پروژهٔ ایزوله استفاده شوند. اگر Interface Image واقعی `Gi0/0`/`Gi0/1` نیست، `show ip interface brief` را بخوانید و در کاربرگ نام واقعی را ثبت کنید؛ بلوک زیر را کورکورانه Paste نکنید.

## ۳. آماده‌سازی Image و شبکه، پیش از QoS

1. پروژهٔ دورریختنی/ایزوله بسازید؛ نسخهٔ دقیق IOS XE، مدل/Feature set، نسخهٔ PNETLab، Image سیستم‌عامل GEN/SVC، نسخهٔ `iperf3` و Interface mapping را در برگهٔ شواهد بنویسید. از اتصال واقعی ISP، شبکهٔ سازمان یا اینترنت استفاده نکنید.
2. روی Routerها با Console، فرمان‌های مشاهده‌ایِ پشتیبانی‌شدهٔ Image را اجرا و Interfaceهای واقعی را تطبیق دهید. مطمئن شوید R1 از **Hierarchical QoS، `shape average`، Child `service-policy` و LLQ percent** روی Interface هدف پشتیبانی می‌کند. پشتیبانی Syntax به‌تنهایی، ظرفیت آزمایش را ثابت نمی‌کند.
3. R1، R2 و Linux Nodeها را مطابق جدول آدرس‌دهی کنید. نمونهٔ پایه برای Routerها، برای Image دارای Interfaceهای متناظر:

**R1 — فرمان طراحی‌شده، اجرا‌نشده:**

```text
configure terminal
interface GigabitEthernet0/0
 ip address 192.0.2.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 198.51.100.1 255.255.255.252
 no shutdown
ip route 203.0.113.0 255.255.255.0 198.51.100.2
end
```

**R2 — فرمان طراحی‌شده، اجرا‌نشده:**

```text
configure terminal
interface GigabitEthernet0/0
 ip address 198.51.100.2 255.255.255.252
 no shutdown
interface GigabitEthernet0/1
 ip address 203.0.113.1 255.255.255.0
 no shutdown
ip route 192.0.2.0 255.255.255.0 198.51.100.1
end
```

در Linux Nodeها، نام Interface را از `ip -br link` بیابید؛ فقط در صورت واقعی‌بودن `eth0` و در محیط ایزوله:

```sh
# GEN
sudo ip link set dev eth0 up
sudo ip address replace 192.0.2.10/24 dev eth0
sudo ip route replace default via 192.0.2.1

# SVC
sudo ip link set dev eth0 up
sudo ip address replace 203.0.113.10/24 dev eth0
sudo ip route replace default via 203.0.113.1
```

پس از تنظیم، روی هر Host `ip -br address show dev eth0` و `ip route get <آدرس مقصد>` را بررسی کنید. اگر Interface نام دیگری دارد، فقط همان نام واقعی را جایگزین کنید؛ این فرمان‌ها را روی NIC میزبان/شبکهٔ کاری اجرا نکنید.

4. پیش از اعمال Policy، روی Routerها `show ip interface brief`, `show ip route` و Ping دوطرفهٔ مجاز را بگیرید؛ از GEN به `203.0.113.10` و از SVC به `192.0.2.10`. هر دو Static Route، Default Gateway دو Host و مسیر برگشت باید درست باشند. اگر IP پایه کار نمی‌کند، QoS را عیب‌یابی نکنید.
5. روی SVC پنج Listener آزمایشی اجرا کنید (هر کدام در Terminal/فرآیند جدا یا به شکل Background). نسخهٔ `iperf3` باید روی دو Host سازگار باشد:

```sh
iperf3 -s -p 5004
iperf3 -s -p 5060
iperf3 -s -p 5005
iperf3 -s -p 5201
iperf3 -s -p 5202
```

## ۴. Classification و Marking در مرز اعتماد

در این طرح GEN قابل‌اعتماد فرض نشده است. R1 بر اساس ACLهای مشخص، Mark را اعمال می‌کند؛ کلاس نامنطبق به DSCP پیش‌فرض برمی‌گردد. این سیاست نمونه برای ترافیک آزمایشی است، نه توصیهٔ کپی‌کردن در شبکهٔ عملیاتی.

| ACL / Class | شرط آزمایشی | DSCP خروجی R1 | معنای علامت در سناریو |
|---|---|---|---|
| `QOS-VOICE` / `FLOW-VOICE` | UDP از `192.0.2.10` به `203.0.113.10:5004` | EF `46` | کلاس اولویت‌دار؛ جریان تست، نه RTP |
| `QOS-SIGNAL` / `FLOW-SIGNAL` | UDP به پورت `5060` | AF21 `18` | فقط نام/علامت آموزشی؛ SIP واقعی نیست |
| `QOS-VIDEO` / `FLOW-VIDEO` | UDP به پورت `5005` | AF41 `34` | فقط UDP آزمایشی؛ Video واقعی نیست |
| `QOS-BUSINESS` / `FLOW-BUSINESS` | UDP به پورت `5201` | AF11 `10` | جریان عادیِ نمونه |
| `QOS-BACKUP` / `FLOW-BACKUP` | UDP به پورت `5202` | CS1 `8` | جریان کم‌اولویتِ نمونه |

**پیکربندی نمونهٔ IOS XE MQC — طراحی‌شده، اجرا‌نشده:**

```text
configure terminal
ip access-list extended QOS-VOICE
 permit udp host 192.0.2.10 host 203.0.113.10 eq 5004
ip access-list extended QOS-SIGNAL
 permit udp host 192.0.2.10 host 203.0.113.10 eq 5060
ip access-list extended QOS-VIDEO
 permit udp host 192.0.2.10 host 203.0.113.10 eq 5005
ip access-list extended QOS-BUSINESS
 permit udp host 192.0.2.10 host 203.0.113.10 eq 5201
ip access-list extended QOS-BACKUP
 permit udp host 192.0.2.10 host 203.0.113.10 eq 5202

class-map match-any FLOW-VOICE
 match access-group name QOS-VOICE
class-map match-any FLOW-SIGNAL
 match access-group name QOS-SIGNAL
class-map match-any FLOW-VIDEO
 match access-group name QOS-VIDEO
class-map match-any FLOW-BUSINESS
 match access-group name QOS-BUSINESS
class-map match-any FLOW-BACKUP
 match access-group name QOS-BACKUP

policy-map LAN-MARK
 class FLOW-VOICE
  set dscp ef
 class FLOW-SIGNAL
  set dscp af21
 class FLOW-VIDEO
  set dscp af41
 class FLOW-BUSINESS
  set dscp af11
 class FLOW-BACKUP
  set dscp cs1
 class class-default
  set dscp default

interface GigabitEthernet0/0
 service-policy input LAN-MARK
end
```

اگر IOS XE هدف `set dscp` یا Policy ورودی را در Interface/Feature انتخابی نپذیرفت، این مرحله را ناموفق/ناسازگار ثبت کنید؛ Image یا دستور را بی‌ثبت عوض نکنید. DSCP Marking از کلاس‌بندی جداست: ACL/Class hit را با Counter بررسی کنید و در صورت امکان DS Field را روی لینک R1–R2 با Capture مجاز مشاهده کنید.

## ۵. Egress Queuing، Shaping و اعمال Policy

صف‌ها روی R1 و جهت `Gi0/1` اعمال می‌شوند؛ در این جهت R1 خروجی WAN را محدود می‌کند. در جدول زیر ارقام عددی ۷۵٪ می‌شوند (با احتساب سقف LLQ) تا از تکرار نمونهٔ ۹۹٪ پرریسک در یک درس جلوگیری شود؛ **این جمع به معنی سازگاری یا Reserve مجاز در C8000V نیست** و باید با همان Image/نسخه بررسی شود. اعداد طراحی آموزشی‌اند: `priority percent` سقف صف LLQ است، ولی `bandwidth percent` حداقل نسبی CBWFQ در Congestion است؛ هیچ‌یک سهم دائمیِ انحصاری نیستند.

| Class | Match در خروجی | فرمان/سهم طراحی | برداشت |
|---|---|---|---|
| `DSCP-VOICE` | `ef` | `priority percent 20` | LLQ؛ سقف طراحی ۲۰٪ از نرخ والد 10 Mbps، حدود 2 Mbps |
| `DSCP-SIGNAL` | `af21` | `bandwidth percent 5` | حداقل تضمین در Congestion |
| `DSCP-VIDEO` | `af41` | `bandwidth percent 10` | حداقل تضمین در Congestion |
| `DSCP-BUSINESS` | `af11` | `bandwidth percent 15` | حداقل تضمین در Congestion |
| `DSCP-BACKUP` | `cs1` | `bandwidth percent 5` | حداقل تضمین در Congestion |
| `class-default` | سایر ترافیک | `bandwidth percent 20` | Best Effort؛ حداقل طراحی‌شده |

**پیکربندی Policy و اعمال — IOS XE MQC، طراحی‌شده و اجرا‌نشده:**

```text
configure terminal
class-map match-any DSCP-VOICE
 match dscp ef
class-map match-any DSCP-SIGNAL
 match dscp af21
class-map match-any DSCP-VIDEO
 match dscp af41
class-map match-any DSCP-BUSINESS
 match dscp af11
class-map match-any DSCP-BACKUP
 match dscp cs1

policy-map WAN-EDGE
 class DSCP-VOICE
  priority percent 20
 class DSCP-SIGNAL
  bandwidth percent 5
 class DSCP-VIDEO
  bandwidth percent 10
 class DSCP-BUSINESS
  bandwidth percent 15
 class DSCP-BACKUP
  bandwidth percent 5
 class class-default
  bandwidth percent 20

policy-map WAN-SHAPE
 class class-default
  shape average 10000000
  service-policy WAN-EDGE

interface GigabitEthernet0/1
 service-policy output WAN-SHAPE
end
```

`bandwidth 10000` به‌تنهایی رابط را به 10 Mbps محدود نمی‌کند؛ Shaper در Policy والد این نقش را دارد. Policy والد/فرزند، درصدهای Scheduler، نحوهٔ reserve، H-QoS و محل/جهت اعمال باید با **دقیقاً همان Image/نسخه** مستند شوند. اگر IOS فرمان `service-policy WAN-EDGE` زیر کلاس والد، `shape average` یا `priority percent` را رد کرد، Policy را اعمال نکنید؛ آن نسخه/Feature با طرح حاضر سازگار نیست تا زمانی که با مستند معتبر همان نسخه اصلاح شود.

## ۶. آزمون پایه و تولید بار کنترل‌شده

1. ابتدا بدون `service-policy output WAN-SHAPE`، هر پنج جریان را جداگانه اجرا و اتصال/دریافت را بررسی کنید؛ سپس Policy را طبق §۵ فعال کنید. خروجی پایه را با خروجی Policy فعال اشتباه نگیرید.
2. روی GEN، جریان‌ها را **هم‌زمان** اجرا کنید؛ هدف‌های `iperf3 -b` مجموعاً `13.5 Mbit/s` نرخ دادهٔ UDP هستند و از CIR طراحی‌شدهٔ 10 Mbps بیشترند. سربار IP/UDP/L2 و روش حساب‌کردن نرخ در Shaper باعث می‌شود نرخ روی سیم/مقدار مؤثر دقیقاً برابر این جمع نباشد. اگر CPU یا Emulator نتواند نرخ‌ها را بسازد، `offered rate` واقعی را ثبت کنید؛ شکل‌دهی/Drop را صرفاً از نرخ درخواستی نتیجه نگیرید.

```sh
iperf3 -c 203.0.113.10 -u -p 5004 -b 1M   -t 30 -i 1 > /tmp/voice.log &
iperf3 -c 203.0.113.10 -u -p 5060 -b 0.5M -t 30 -i 1 > /tmp/signal.log &
iperf3 -c 203.0.113.10 -u -p 5005 -b 3M   -t 30 -i 1 > /tmp/video.log &
iperf3 -c 203.0.113.10 -u -p 5201 -b 4M   -t 30 -i 1 > /tmp/business.log &
iperf3 -c 203.0.113.10 -u -p 5202 -b 5M   -t 30 -i 1 > /tmp/backup.log &
wait
```

**محاسبهٔ پیش از اجرا:** `1 + 0.5 + 3 + 4 + 5 = 13.5 Mbit/s` بارِ دادهٔ درخواستی در برابر سقف طراحی‌شدهٔ 10 Mbps است. اگر Offered واقعی به روتر برسد و Shaper روی همان مسیر واقعاً فعال باشد، خروجیِ پایدار نمی‌تواند از نرخ مؤثر Shaper بیشتر شود؛ مازاد ممکن است موقتاً در صف بماند و با پرشدن Buffer Drop شود. از `bandwidth percent`ها نرخ خروجی دقیق هر کلاس را پیش‌بینی نکنید. Voice با هدف اسمی 1 Mbps پایین‌تر از سقف طراحی 20٪ (حدود 2 Mbps از 10 Mbps) است؛ این محاسبه فقط فرض آموزشی است و نه اندازه‌گیری، تضمین Latency یا تجربهٔ تماس.

این UDPهای ساختگی، SIP/RTP/Video یا رفتار یک WAN واقعی را شبیه‌سازی کامل نمی‌کنند. `iperf3` روی همان Host ممکن است برای هر پورت Listener جدا بخواهد؛ پیش از ارسال جریان، Serverها را آماده کنید. اگر فرمان/نسخه از `-b` یا چند Instance پشتیبانی نمی‌کند، نسخه و نرخ واقعی را ثبت و آزمون را متوقف/بازطراحی کنید.

## ۷. Verification و تفسیر نتیجه

روی R1، پیش از بار و پس از بار، خروجی‌های زمان‌دار و نام Image را ثبت کنید:

```text
show policy-map
show policy-map interface GigabitEthernet0/0 input
show policy-map interface GigabitEthernet0/1
show access-lists QOS-VOICE
show access-lists QOS-SIGNAL
show access-lists QOS-VIDEO
show access-lists QOS-BUSINESS
show access-lists QOS-BACKUP
show running-config interface GigabitEthernet0/0
show running-config interface GigabitEthernet0/1
show interfaces GigabitEthernet0/1
```

| شاهد | نتیجهٔ مورد انتظار در صورت پشتیبانی/ترافیک واقعی | چه چیزی را **ثابت نمی‌کند** |
|---|---|---|
| R1 ورودی | Counter هر `FLOW-*`/ACL برای جریان مربوط افزایش یابد؛ کلاس `class-default` سایر جریان‌ها را بگیرد | Hit ACL به‌تنهایی DSCP روی لینک یا کیفیت خروجی را ثابت نمی‌کند |
| Capture اختیاری روی R1–R2 | DSCP در IP Header پس از R1 با جدول Marking برابر باشد | یک Capture بدون سنجش بار/Counter، عملکرد صف را ثابت نمی‌کند |
| R1 خروجی | والد `WAN-SHAPE` و نرخ طراحی‌شدهٔ CIR=10,000,000 bps دیده شود؛ Policy فرزند به رابط وصل باشد | عدد پیکربندی‌شده به‌تنهایی نرخ فیزیکی یا throughput واقعی را ثابت نمی‌کند |
| کلاس Voice | Match روی DSCP EF و عبارت Priority/LLQ دیده شود؛ Counterها هنگام آزمون افزایش یابند | Priority را با تضمین تأخیر انتهابه‌انتها یا تلفن واقعی یکی نمی‌کند |
| کلاس‌های دیگر | Match مناسب و `bandwidth percent` متناظر نمایش داده شود؛ Drop/Queue Counter در Congestion بررسی شود | `bandwidth percent` سقف مصرف کلاس نیست |
| نرخ‌ها و Dropها | `offered rate`, `drop rate`, `queue depth`, `pkts output` قبل/بعد مقایسه شود؛ شکل/واحد خروجی نسخه‌محور است | صفر بودن Drop در ترافیک کم/بدون Congestion موفقیت آزمون ازدحام نیست |

**شکل شماتیکِ مورد انتظار، نه خروجی واقعی یا متن تضمین‌شدهٔ IOS XE:**

```text
Service-policy output: WAN-SHAPE
  Class-map: class-default
    Average Rate Traffic Shaping
      cir 10000000 (bps)
    Service-policy: WAN-EDGE
      Class-map: DSCP-VOICE
        Match: dscp ef (46)
        Priority: 20% ...
      Class-map: DSCP-BUSINESS
        Match: dscp af11 (10)
        bandwidth 15% ...
```

اگر `Match` صفر است، ابتدا ACL/کلاس ورودی و مسیر ترافیک را بررسی کنید. اگر کلاس Voice Match دارد اما `Priority`/LLQ در Output نیست، صف اولویت‌دار روی آن Policy تأیید نشده است. اگر Shaper روی Interface خروجی دیده نمی‌شود، صرف وجود Policy در Running Config به معنی Apply شدن نیست. مقدار/قالب واقعی و Labelهای Platform را عیناً از Capture همان IOS XE ثبت کنید، نه از بلوک شماتیک بالا.

## ۸. نقص کنترل‌شده، عیب‌یابی و Rollback

### نقص کنترل‌شدهٔ Marking

فقط در لاب ایزوله، درحالی‌که ترافیک GEN به‌طور پیش‌فرض DSCP 0 دارد:

1. از R1 روی `Gi0/0`، ورودی `service-policy input LAN-MARK` را موقتاً بردارید: `no service-policy input LAN-MARK`.
2. همان پنج جریان را دوباره اجرا کنید و `show policy-map interface Gi0/0 input` و `show policy-map interface Gi0/1` را ثبت کنید. Policy ورودی دیگر نباید اعمال شود؛ DSCP پیش‌فرض باید در Policy خروجی به Best Effort برود و Voice/کلاس‌های DSCP شمارندهٔ Match مورد انتظار نداشته باشند. اگر GEN خودش DSCP را علامت می‌زند، پیش‌فرض‌بودن آن را پیش از این آزمون Capture کنید یا Fault را اجرا نکنید.
3. Policy را برگردانید: `service-policy input LAN-MARK` روی همان Interface. ترافیک را دوباره بفرستید؛ ACL/کلاس‌های ورودی و Match خروجی را با Counterهای تازه/تفاضلی بررسی کنید.
4. اگر خروجی غیرمنتظره است، فقط همان متغیر را تغییر دهید؛ `clear counters` یا تغییرات متعدد هم‌زمان، شواهد علت را از بین می‌برد.

### مسیر Troubleshooting مستقل

1. **Link و IP:** `show ip interface brief`, `show interfaces`, Route دو طرف، Gatewayهای Host، Ping پایه.
2. **ترافیک آزمون:** Listener/Client `iperf3`، مقصد/پورت واقعی، نرخ Offered و خطای Socket.
3. **Classification ورودی:** `show access-lists` و `show policy-map interface Gi0/0 input`; ACL، جهت `input` و `service-policy` باید با Topology سازگار باشند.
4. **Marking و Trust:** کلاس ورودی و DSCP پس از R1 را با Capture مجاز بررسی کنید؛ ترافیک کلاینت نامنطبق باید سیاست مشخص داشته باشد.
5. **خروجی و Scheduler:** روی Interface رو به WAN، Policy والد/فرزند، shaping rate، کلاس/DSCP Match، LLQ/CBWFQ، شمارندهٔ Queue و Drop را مقایسه کنید.
6. **Congestion واقعی:** مجموع Offered Rate از CIR بیشتر است؟ اگر نه، صفر بودن Drop یا تغییر تأخیر آزمون صف نیست. بار CPU/Emulator و نرخ واقعاً منتقل‌شده را لحاظ کنید.
7. **Rollback در همین Lab ایزوله:** پس از ثبت شواهد، ابتدا از Interfaceهای آزمایشی Policy را بردارید؛ فرمان‌های زیر فقط برای همان R1 و نام Interfaceهای همین طرح‌اند:

   ```text
   configure terminal
   interface GigabitEthernet0/0
    no service-policy input LAN-MARK
   interface GigabitEthernet0/1
    no service-policy output WAN-SHAPE
   end
   ```

   اگر نام Image متفاوت است، تطبیق دهید یا Snapshot همان پروژه را Restore کنید. روی WAN، شبکهٔ سازمانی یا میزبان اصلی هیچ Policy/Route را تغییر ندهید.

| نشانه | علت محتمل | شاهد و گام بعد |
|---|---|---|
| جریان IP ندارد | آدرس، Interface، Route، Gateway یا Listener | ابتدا Ping و `iperf3` بدون QoS |
| ACL hit ندارد | Source/Destination/Port یا جهت اشتباه | تطبیق Packet Capture و Named ACL؛ Counter را با زمان/بار مقایسه کنید |
| ورودی کلاس می‌خورد ولی خروجی Voice نمی‌خورد | Mark اعمال نشده، DSCP تغییر کرده، یا خروجی روی جهت/Interface دیگری است | Policy ورودی، Capture بعد از R1، DSCP match و Interface واقعی |
| Policy در Config هست ولی اثر/Counter ندارد | روی Interface درست Apply نشده یا بار از مسیر دیگری عبور می‌کند | `show policy-map interface` و Routing/Topology |
| LLQ نشان داده نمی‌شود | کلاس/Policy یا نسخهٔ H-QoS ناسازگار؛ استفاده از `bandwidth` به‌جای Priority نیز ممکن است | Output نسخه را با Policy و مستند Image مقایسه کنید؛ ادعای LLQ نکنید |
| Shape یا Percentage رد می‌شود | محدودیت Feature set، Hierarchical QoS یا سقف Reserve | خطا/نسخه را ثبت کنید؛ بر اساس مستند همان IOS XE بازطراحی، نه با Syntax حدسی |
| Drop بالا در همهٔ کلاس‌ها | CIR بیش‌ازحد پایین، Offered rate، MTU/CPU/Queue | Queue/dropها و نرخ روی دو سمت را تفکیک کنید |
| QoS هیچ تغییر قابل‌اندازه‌گیری ندارد | Congestion شکل نگرفته، Capture/Counter اشتباه یا گلوگاه جای دیگری است | offered rate و محل Congestion را اثبات کنید؛ Label شدن را موفقیت کیفیت ننامید |

## ۹. معیار قبولی و بستهٔ شواهد

کاربرگ در سطح **طراحی/آمادگی** زمانی کامل است که Address plan، نگاشت Interface، Image/version، ACL/Class، Marking، Parent/Child QoS، مراحل، خطای کنترل‌شده، مسیر Troubleshooting و معیار زیر همگی ثبت باشند. اجرای عملی فقط پس از دسترسی و ثبت Image معتبر ادعا می‌شود.

1. `show version`، نام Interfaceهای واقعی، Feature Support و نسخه/ابزار Linux ثبت شود؛ Secret یا Token وارد شواهد نشود.
2. مسیر پایه و دو Static Route، Ping دوطرفه و `iperf3` بدون QoS موفق و ثبت شده باشد.
3. پنج جریان UDP با پورت‌های مشخص تولید شوند؛ ACL/Class Counter ورودی مربوط افزایش یابد و Mark DSCP با Capture مجاز هم‌خوان باشد.
4. Policy والد روی خروجی R1 اعمال شود؛ Shaper/CIR و Child Policy در خروجی تأیید شود؛ کلاس Voice واقعاً Priority/LLQ داشته باشد و چهار کلاس دیگر با Match/سهم طراحی‌شده دیده شوند.
5. مجموع نرخ‌ها از CIR بیشتر باشد یا صریحاً ثبت شود چرا Congestion در محیط ایجاد نشد؛ offered/drop/queue/output counterها و نتایج Client/SVC زمان‌دار مقایسه شوند.
6. با برداشتن فقط Policy ورودی، طبقه‌بندی/Marking مورد انتظار از دست برود؛ پس از Restore، شمارنده‌ها/DSCP مورد انتظار برگردند.
7. همهٔ خروجی‌ها یا Captureهای شواهد صریحاً `واقعی`، `شماتیک` یا `طراحی‌شده` علامت بخورند. **در مخزن فعلی هیچ‌یک از مراحل IOS XE/PNETLab/iperf3 این Lab اجرا نشده است؛ پس این معیار هنوز عملی تأیید نشده است.**

## واژه‌نامهٔ کوتاه

Classification: دسته‌بندی جریان؛ Marking: نوشتن DSCP؛ PHB: رفتار هر گره؛ LLQ: صف اولویت‌دار محدود؛ CBWFQ: صف‌بندی وزن‌دار؛ Shaping: Buffer/تنظیم نرخ خروجی؛ Policing: عبور/Mark/Drop بر مبنای نرخ؛ CIR: نرخ طراحی‌شده/قراردادی.
