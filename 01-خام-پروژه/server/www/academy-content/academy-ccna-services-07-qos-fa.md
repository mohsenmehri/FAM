# CCNA IS-07 — QoS و Per-Hop Behavior

**سطح:** CCNA. **پیش‌نیاز:** NF-15. **هدف رسمی:** `4.7` توضیح QoS Forwarding Per-Hop Behavior شامل Classification، Marking، Queuing، Congestion، Policing و Shaping. **وضعیت:** بازبینی هدفمند محتوای Objective 4.7؛ متن برای این هدف توضیحی کافی ارزیابی شد، نه ممیزی جامع کل درس. پیکربندی/خروجی‌ها طراحی‌شده و اجرا‌نشده‌اند. کاربرگ مستقل [IS-07](academy-ccna-services-07-qos-lab-fa.md) توپولوژی و آزمون را برای هدف طراحی `Cisco C8000V / IOS XE 17.9.4` مشخص می‌کند؛ Image در Sandbox موجود نیست و نسخه/Featureها، QoS و Traffic هنوز Verify نشده‌اند.

## اهداف

1. بفهمید Queueing/Scheduling چه زمانی روی جریان اثر می‌گذارد و Marking چه کاربردی دارد حتی وقتی لینک محلی شلوغ نیست.
2. زنجیرهٔ Classification → Marking → Queuing → Scheduling را توضیح دهید.
3. تفاوت **Policing** و **Shaping** را با پیامد عملی‌شان بیان کنید.
4. نقش **Trust Boundary** را تشخیص دهید و بدانید چرا اشتباه در آن، کل طراحی را خنثی می‌کند.
5. محدودیت‌های **Priority Queuing** را بفهمید و بدانید کی نباید از آن استفاده کرد.

## ۱. QoS چه مسئله‌ای را حل می‌کند؟

**نکتهٔ کلیدی:** زمان‌بندی صف، اولویت‌دهی و Drop/Mark ناشی از صف زمانی اثر مستقیم دارند که چند جریان برای ظرفیت خروجی رقابت کنند و Congestion شکل بگیرد. اگر روی همان لینک هیچ صف/رقابتی نباشد، Scheduler چیزی برای اولویت‌بندی ندارد؛ بااین‌حال Classification/Marking هنوز می‌تواند برای Policy یا هاپ بعدی اهمیت داشته باشد. QoS پهنای باند تازه نمی‌سازد و علامت‌گذاری به‌تنهایی تأخیر را کم نمی‌کند.

سناریوی واقعی: لینک WAN بین دفتر و دیتاسنتر `10 Mbps` است. در ساعات کاری:

- Backup شبانه (که به بعد از ساعت کاری منتقل نشده) حدود `6 Mbps` می‌گیرد.
- کاربران وب و ایمیل حدود `3 Mbps`.
- تماس VoIP حدود `1 Mbps`.

مجموع دقیقاً به سقف می‌رسد. وقتی یک تماس دوم شروع می‌شود، بسته‌های صدا در صف انتظار می‌مانند. صف، **تأخیر (Delay)** و **Jitter** می‌سازد. اگر صف پر شود، بسته‌های صدا **Drop** می‌شوند. نتیجه: صدا قطع و وصل می‌شود.

QoS کاری که می‌کند این است: به بسته‌های صدا **اولویت** می‌دهد تا قبل از بقیه از صف خارج شوند.

### پیامدهای Congestion و محدودیت ظرفیت

| اثر | معنا | تأثیر بر صدا و ویدیو |
|---|---|---|
| **Delay** (تأخیر) | زمان رسیدن بسته از مبدأ تا مقصد؛ صف یکی از عوامل آن است | ۱۵۰ ms یک‌طرفه یک معیار برنامه‌ریزی رایج است، نه مرز ادراکی قطعی؛ مسیر/برنامه هم اثر دارند |
| **Jitter** | تغییر تأخیر بین بسته‌ها | صدا رباتیک می‌شود |
| **Packet Loss** | دور ریختن بسته در صف پر | صدا قطع می‌شود |
| **ظرفیت/Throughput موجود** | منبع محدودی که جریان‌ها برایش رقابت می‌کنند | کمبود ظرفیت می‌تواند Congestion بسازد؛ مقدار ظرفیت به‌تنهایی پیامد نیست |

زمان‌بندی و مدیریت صف می‌توانند Delay/Jitter/Drop را در گلوگاه کنترل کنند؛ **ظرفیت لینک را نمی‌سازند.** اگر تقاضا از ظرفیت بیشتر است، QoS بخشی از ترافیک را ترجیح می‌دهد و بخشی ممکن است بیشتر منتظر بماند یا Drop شود.

## ۲. زنجیرهٔ QoS — Per-Hop Behavior

**Per-Hop Behavior (PHB)** یعنی هر روتر در مسیر، به‌طور مستقل تصمیم می‌گیرد با هر کلاس ترافیک چه کند. این تصمیم‌ها **در هر هاپ** تکرار می‌شوند، نه یک‌بار برای کل مسیر.

```text
Traffic → Classify → Mark → Queue → Schedule → Transmit
              ↑                        ↑
         Trust Boundary          Congestion Management
```

### گام ۱ — Classification

روتر باید بفهمد بستهٔ ورودی از چه نوعی است. روش‌ها:

| روش | دقت | پیچیدگی | نمونه |
|---|---|---|---|
| **ACL** | متوسط | کم | `match access-group 101` |
| **DSCP** | بالا (اگر قابل‌اعتماد باشد) | کم | `match dscp ef` |
| **NBAR** | وابسته به نسخه/پروتکل و دیدپذیری ترافیک؛ رمزنگاری می‌تواند تشخیص را محدود کند | زیاد | نمونهٔ دستور و پروتکل‌های پشتیبانی‌شده را با IOS/IOS-XE هدف بررسی کنید |
| Interface ورودی | کم | بسیار کم | `match input-interface Gi0/0` |
| CoS (802.1Q) | متوسط | کم | `match cos 5` |

### گام ۲ — Marking

علامت‌گذاری در سرآیند بسته. اگر دامنهٔ مدیریتی بعدی به آن مقدار اعتماد کند، Mark می‌تواند ورودیِ Policy/Queuing بعدی باشد و از Classification تکراریِ گران‌قیمت بکاهد؛ این صرفه‌جویی تضمین‌شده نیست و فقط در صورت هماهنگی Trust Boundary معنا دارد. مقدار علامت‌گذاری‌شده همراه بسته می‌ماند تا جایی که بازنویسی/Encapsulation آن را تغییر دهد.

| فیلد | لایه | محدوده | کاربرد |
|---|---|---|---|
| **DSCP** (6 بیت) | IP | 0–63 | استاندارد اصلی در L3 |
| **IP Precedence** (3 بیت) | IP | 0–7 | قدیمی، زیرمجموعهٔ DSCP |
| **CoS / PCP** (۳ بیت) | برچسب VLAN در فریم Ethernetِ 802.1Q | 0–7 | در فریم‌های Tagged؛ فقط به Trunk بین سوئیچ‌ها محدود نیست |
| **MPLS TC (نام قدیمی EXP)** | MPLS | 0–7 | کلاس سرویس در MPLS |

**DSCP** جایگزین IP Precedence شده است چون فضای بیشتری دارد. DSCPهای معروف:

| نام | مقدار | کلاس |
|---|---|---|
| **EF** (Expedited Forwarding) | 46 | صدا |
| **AF41** | 34 | ویدیو تعاملی |
| **AF31** | 26 | ویدیو Streaming |
| **AF21** | 18 | سیگنالینگ تماس |
| **CS1** | 8 | Scavenger (ترافیک کم‌اهمیت) |
| **BE** (Best Effort) | 0 | پیش‌فرض |

جدول کامل DSCP ۶۴ مقدار دارد؛ فقط تعداد کمی در عمل استفاده می‌شود.

### گام ۳ — Queuing و Scheduling

**Queuing** یعنی بسته در صف کلاس خودش قرار می‌گیرد. **Scheduling** یعنی کدام صف اول خارج شود.

| الگوریتم | نحوهٔ کار | مناسب برای |
|---|---|---|
| **FIFO** | یک صف، به ترتیب ورود | شبکهٔ ساده |
| **WFQ** | تقسیم پهنای باند بر اساس وزن | ترافیک متنوع |
| **CBWFQ** | صف جدا برای هر کلاس با پهنای باند تضمینی | استاندارد اصلی |
| **LLQ** | CBWFQ همراه یک یا چند کلاس Priority با رفتار Strict/Low-Latency و سقف/Policing وابسته به پلتفرم | ترافیک حساس به تأخیر، با بودجه و کنترل نرخ |

**LLQ (Low Latency Queuing)** الگوی رایج IOS برای ترکیب CBWFQ با کلاس Priority است، نه تضمین سراسری کیفیت: کلاس Priority در گلوگاهِ دارای رقابت نسبت به صف‌های عادی سرویس با تأخیر کمتر/Strict Priority می‌گیرد؛ سقف یا Policing پیکربندی‌شده و رفتار همان پلتفرم آن را محدود می‌کند. «اولویت» را با رزرو دائمی پهنای‌باند یا تضمین تأخیر انتهابه‌انتها یکی نگیرید.

**محدودیت مهم LLQ:** اگر صف Priority را **محدود نکنید**، ترافیک آن کلاس می‌تواند همهٔ پهنای باند را بگیرد و بقیهٔ کلاس‌ها گرسنه بمانند (**Starving**). پس باید **سقف (Bandwidth Percent)** برای صف Priority تعیین کنید. اینجا همان عدد `percent 20` معنا پیدا می‌کند.

### گام ۴ — Congestion Management

وقتی صف پر می‌شود، تصمیم در مورد اینکه کدام بسته دور ریخته شود:

- **Tail Drop** — بستهٔ رسیده به صف پر Drop می‌شود. ساده است و در بعضی شرایط، به‌ویژه میان جریان‌های TCP هم‌زمان، می‌تواند به **Global Synchronization** کمک کند؛ این پیامد همیشگی/قطعی نیست.
- **WRED** — با افزایش میانگین طول صف، احتمال Drop زودهنگام را بالا می‌برد؛ اگر آستانه‌ها بر اساس Precedence/DSCP تنظیم شده باشند، می‌تواند ترافیک کم‌اولویت را زودتر Drop کند.
- **ECN** — برای بسته‌های IPِ ECN-capable، به‌جای Drop علامت ازدحام می‌گذارد. واکنش فرستنده به پشتیبانی Transport/Application وابسته است؛ UDP یا RTP عمومی به‌خودی‌خود نرخ را کم نمی‌کند، اما ECN ذاتاً به TCP محدود نیست.

## ۳. Policing در برابر Shaping

بیشتر اشتباه‌ها در همین تمایز رخ می‌دهند.

| ویژگی | **Policing** | **Shaping** |
|---|---|---|
| چه می‌کند | بستهٔ اضافه را **دور می‌ریزد** یا علامت می‌زند | بستهٔ اضافه را **نگه می‌دارد** و بعد می‌فرستد |
| Buffer | معمولاً ندارد | **دارد** (صف) |
| اثر | **Drop** | **Delay** |
| محل کاربرد | **ورودی** یا خروجی | خروجی |
| مناسب برای | محدودسازی مشتری به نرخ قرارداد | جلوگیری از Drop در لینک کند |

**تشبیه و محدودیتش:** Policing مثل دریافت‌کننده‌ای در ورودی سالن است که هر کس بلیت اضافه دارد را برمی‌گرداند. Shaping مثل ناظری است که بازدیدکنندگان اضافه را در راهرو نگه می‌دارد و یکی‌یکی وارد می‌کند. محدودیت تشبیه: Shaping تأخیر می‌سازد و اگر صفش پر شود، بالاخره Drop می‌کند؛ در مقیاس بزرگ، اثر Shaping روی تأخیر خودش مشکل می‌شود.

**قاعدهٔ عملی:**

- اگر روی خروجی به ISP نرخ قراردادی `10 Mbps` دارید، **Shaping روی خروجی** معمولاً ترافیک را پیش از policer بالادست صف‌بندی می‌کند؛ Policing برای Drop/Mark کردن ترافیک خارج از نرخ مناسب است.
- اگر لینک شما به‌هر دلیل کندتر از روتر است و می‌خواهید Drop را به Delay تبدیل کنید → **Shaping** روی Interface خروجی. روی ورودی، ترافیک از قبل دریافت شده و Policing نمی‌تواند آن را پیش از لینک صف‌بندی کند.

## ۴. Trust Boundary

**Trust Boundary** نقطه‌ای است که شبکه تصمیم می‌گیرد به علامت‌های DSCP/CoS ورودی **اعتماد** کند یا نه.

اگر در Trust Boundary به DSCP کاربر بدون محدودیت اعتماد شود و Policy خروجی همان DSCP را به کلاس Priority نگاشت کند، کاربر می‌تواند ترافیک غیرصوتی را نیز وارد آن کلاس کند؛ این کار ممکن است سهم صف‌های دیگر را کاهش دهد و کیفیت صدا را بدتر کند. Marking به‌تنهایی صف یا اولویت ایجاد نمی‌کند؛ نگاشت و Scheduler همان گره نیز باید آن را اعمال کنند. به همین دلیل:

1. در لبهٔ شبکه، علامت‌های کاربر **بازنویسی** می‌شوند (معمولاً به `BE`).
2. تلفن IP یا AP مجاز است علامت بزند → روی پورت متصل به تلفن، Trust فعال می‌شود.
3. این اعتماد فقط در همان Interface/Policy برقرار است؛ هر هاپ بعدی باید جداگانه تصمیم بگیرد Mark را بپذیرد، بازنویسی کند یا نادیده بگیرد.

```text
interface GigabitEthernet0/10
 mls qos trust device cisco-phone
 mls qos trust dscp
```

- `trust device cisco-phone` — یک نمونهٔ وابسته به قابلیت/نحو Catalyst است؛ در پلتفرم‌های پشتیبان، شرطِ شناسایی تلفن را در لایهٔ دسترسی به‌کار می‌گیرد. نتیجه برای PC پشت Phone، حالت Pass-through و CDP/LLDP به مدل/نسخه و طراحی پورت وابسته است؛ بدون آزمایش، نادیده‌گرفته‌شدن همهٔ Markهای PC را تضمین نکنید.
- `trust dscp` — نمونهٔ IOS/Catalyst برای اعتماد به DSCP ورودی؛ فقط بعد از تعیین مرز اعتماد و Policy بازنویسی/محدودسازی در لبه استفاده شود. نحو و سخت‌افزار هدف باید بررسی شود.

**Trust Boundary نادرست یکی از ریسک‌های رایج طراحی QoS است:** ممکن است ترافیک نامعتبر وارد کلاس اولویت‌دار شود یا Mark معتبر پیش از رسیدن به گلوگاه بازنویسی شود. برای یافتن علت، مرز اعتماد، Policy هر هاپ و شمارندهٔ کلاس را جدا بررسی کنید؛ بدون داده، فراوانی یک علت را رتبه‌بندی نکنید.

## ۵. سناریوی طراحی‌شده

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده.** لینک WAN با ظرفیت `10 Mbps` (فرض طراحی، نه اندازه‌گیری‌شده).

| کلاس | ترافیک | DSCP | درصد پیکربندی‌شده (سقف یا حداقل) | الگوریتم |
|---|---|---|---|---|
| Voice | RTP صدا | EF (46) | ۲۰٪ سقف صف Priority | LLQ |
| Signaling | SIP | AF21 (18) | ۵٪ حداقل تضمین‌شده | CBWFQ |
| Video | ویدیو تعاملی | AF41 (34) | ۱۰٪ حداقل تضمین‌شده | CBWFQ |
| Business | ایمیل، HTTPS | AF11 (10) | ۱۵٪ حداقل تضمین‌شده | CBWFQ |
| Scavenger | Backup، دانلود | CS1 (8) | ۵٪ حداقل تضمین‌شده | CBWFQ |
| Best Effort (`class-default`) | بقیهٔ ترافیک | DSCP 0 (BE) و هر ترافیکِ نامنطبق با کلاس‌های دیگر | ۲۰٪ حداقل تضمین‌شده | CBWFQ |

**توجه:** ارقام این سناریو با کاربرگ مستقل IS-07 همسان شده‌اند و جمع عددی آن‌ها ۷۵٪ است: سقف طراحی‌شدهٔ ۲۰٪ برای Priority و حداقل‌های طراحی‌شدهٔ ۵٪+۱۰٪+۱۵٪+۵٪+۲۰٪ برای CBWFQ. این جمع، سهم دائمی یا نرخ خروجی تضمین‌شدهٔ هر کلاس نیست؛ حد مجاز و مبنای محاسبهٔ درصدها به H-QoS، نسخه و پلتفرم وابسته است و ۲۵٪ باقی‌مانده را نیز نمی‌توان بدون مستندات به یک کلاس نسبت داد. این مثال اجرا نشده است؛ قبل از پیکربندی، محدودیت reserve و Syntax را در مستند همان Image بررسی کنید.

![نمودار قابل ویرایش QoS؛ اجرا‌نشده](academy-images/is-07-qos.svg)

### پیکربندی متناظر با جدول

**اجرا‌نشده.** این پیکربندی، تک‌تک ردیف‌های جدول بالا را پیاده می‌کند؛ هر خط به یک ردیف برمی‌گردد:

```text
class-map match-any VOICE
 match dscp ef
class-map match-any SIGNALING
 match dscp af21
class-map match-any VIDEO
 match dscp af41
class-map match-any BUSINESS
 match dscp af11
class-map match-any SCAVENGER
 match dscp cs1
exit

policy-map WAN-EDGE
 class VOICE
  priority percent 20
 class SIGNALING
  bandwidth percent 5
 class VIDEO
  bandwidth percent 10
 class BUSINESS
  bandwidth percent 15
 class SCAVENGER
  bandwidth percent 5
 class class-default
  bandwidth percent 20
 exit
exit

! Parent shaper: limits aggregate egress to the assumed 10-Mbps CIR
policy-map WAN-SHAPE
 class class-default
  shape average 10000000
  service-policy WAN-EDGE
 exit
exit

interface GigabitEthernet0/1
 description WAN uplink — ISP contract 10 Mbps
 bandwidth 10000
 service-policy output WAN-SHAPE
```

| خط | چرا |
|---|---|
| `class-map match-any VOICE` + `match dscp ef` | کلاس صدا بر اساس DSCP، مطابق ستون دوم جدول |
| `priority percent 20` | **LLQ** — صف Priority با سقف ۲۰٪. `priority` (بدون `percent`) سقف ندارد و Starvation می‌سازد |
| `bandwidth percent 5`، `10`، `15` یا `20` (کلاس‌های دیگر) | **CBWFQ** — حداقل نسبی در Congestion، نه سقف مصرف و نه اولویت مطلق |
| `class class-default` | ترافیک طبقه‌بندی‌نشده؛ در جدول ردیف Best Effort |
| `bandwidth 10000` روی Interface | مقدار اطلاعاتی/مرجع را بر حسب kbps تنظیم می‌کند و ممکن است بر محاسبهٔ درصدها اثر بگذارد؛ **پهنای باند فیزیکی را محدود نمی‌کند**. محدودیت 10 Mbps در این طرح با `shape average 10000000` اعمال می‌شود. |

در این ساختار، `WAN-SHAPE` سقف مجموع ترافیک خروجی را به 10 Mbps می‌رساند و `WAN-EDGE` زمان‌بندی کلاس‌ها را درون آن نرخ انجام می‌دهد. پشتیبانی از H-QoS و جزئیات درصدها وابسته به IOS/IOS-XE و مدل است؛ پیکربندی نمونه را پیش از اجرا در مستندات Image هدف بررسی کنید.

**نکتهٔ کلیدی که باید حفظ شود:** `priority` و `bandwidth` دو الگوریتم متفاوت‌اند و در خروجی هم متفاوت دیده می‌شوند:

| فرمان در policy | الگوریتم | در خروجی `show policy-map interface` |
|---|---|---|
| `priority percent 20` | **LLQ** | `Strict Priority` + `Priority: 20% (2000 kbps)` |
| `bandwidth percent 5` | **CBWFQ** | `bandwidth 5% (500 kbps)` |

اگر در خروجی، کلاس صدا `bandwidth` نشان دهد، یعنی `priority` اعمال نشده و صدا **صف Priority ندارد**. این یکی از ساده‌ترین راه‌های تشخیص خطای پیکربندی است.

### خروجی Verification

**گزیدهٔ شماتیک، اجرا‌نشده؛ شکل دقیق خروجی والد/فرزند به پلتفرم وابسته است و کلاس‌های Video، Business و Scavenger در این گزیده حذف شده‌اند.**

```text
R1# show policy-map interface GigabitEthernet0/1
 GigabitEthernet0/1

  Service-policy output: WAN-SHAPE
    Class-map: class-default (match-any)
      Average Rate Traffic Shaping
        cir 10000000 (bps)
      Service-policy: WAN-EDGE

        Class-map: VOICE (match-any)
          0 packets, 0 bytes
          5 minute offered rate 0 bps, drop rate 0 bps
          Match: dscp ef (46)
          Priority: 20% (2000 kbps), burst bytes 50000, b/w exceed drops: 0

        Class-map: SIGNALING (match-any)
          0 packets, 0 bytes
          5 minute offered rate 0 bps, drop rate 0 bps
          Match: dscp af21 (18)
          Queueing
          queue limit 64 packets
          (queue depth/total drops/no-buffer drops) 0/0/0
          (pkts output/bytes output) 0/0
          bandwidth 5% (500 kbps)

        Class-map: class-default (match-any)
          0 packets, 0 bytes
          5 minute offered rate 0 bps, drop rate 0 bps
          Match: any
          Queueing
          queue limit 64 packets
          (queue depth/total drops/no-buffer drops) 0/0/0
          (pkts output/bytes output) 0/0
          bandwidth 20% (2000 kbps)
```

خط‌به‌خط:

- `Service-policy output: WAN-SHAPE` — policy والد روی خروجی `Gi0/1` اعمال شده و نرخ خروجی را شکل می‌دهد؛ سیاست فرزند زیر آن زمان‌بندی کلاس‌ها را انجام می‌دهد.
- `Average Rate Traffic Shaping / cir 10000000` — نرخ شکل‌دهی فرضی 10 Mbps است؛ این مقدار حد مجموع ترافیک خروجی را نشان می‌دهد.
- `Service-policy: WAN-EDGE` — policy فرزند برای Classification و زمان‌بندی کلاس‌ها.
- `Match: dscp ef (46)` — این کلاس ترافیک صدا را با DSCP = 46 تشخیص می‌دهد (**Classification** روی مقدار علامت‌گذاری‌شده).
- `Priority: 20% (2000 kbps)` — **این خط، LLQ را اثبات می‌کند.** عبارت `Priority:` (و نه `bandwidth:`) نشان می‌دهد کلاس صف Priority دارد؛ این صف با اولویت نسبت به صف‌های دیگر سرویس می‌گیرد، اما سقف ۲۰٪ آن را محدود می‌کند. ۲۰٪ از نرخ شکل‌دهی 10 Mbps برابر 2 Mbps است. `b/w exceed drops: 0` یعنی در بازهٔ شمارندهٔ جاری Drop ناشی از عبور از سقف ثبت نشده است.
- `burst bytes 50000` — مقدار Burst برای Token Bucket. اگر بسته‌ها به‌صورت انفجاری برسند، تا این حجم مجاز است.
- `bandwidth 5% (500 kbps)` در کلاس SIGNALING — **این حداقل تضمین CBWFQ تحت Congestion است، نه سقف مصرف و نه LLQ.** معنای دقیق Percent را با مستندات پلتفرم هدف تأیید کنید.
- `Match: any` در `class-default` — ترافیک طبقه‌بندی‌نشده.
- `0 packets, 0 bytes` در کلاس‌های نشان‌داده‌شده — این نمونه هیچ ترافیک/آمار واقعی ثبت نمی‌کند؛ کلاس‌های حذف‌شده از گزیده را هم از روی آن نتیجه‌گیری نکنید.
- `5 minute offered rate 0 bps, drop rate 0 bps` — نرخ مشاهده‌شده و Drop در بازهٔ گزارش. برای تشخیص Congestion مفید است: اگر `offered rate` کلاس صدا به سقف 2000 kbps برسد، ممکن است Drop یا Mark ناشی از محدودیت ثبت شود.

**نکتهٔ مهم دربارهٔ لینک WAN:** روی Interface فیزیکی `100 Mbps` با CIR برابر `10 Mbps`، دستور `bandwidth 10000` به‌تنهایی نرخ را محدود نمی‌کند؛ فقط مقدار مرجع/اطلاعاتی را تنظیم می‌کند. برای شکل‌دادن ترافیک در سمت خودتان از Shaper خروجی (مانند `shape average 10000000` در policy والد) استفاده کنید؛ وگرنه ازدحام ممکن است نزد policer شرکت بالادست رخ دهد و بسته‌ها پیش از صف‌بندی شما Drop شوند.

## ۶. محدودیت‌های Priority و هشدارهای طراحی

1. **مجموع درصدهای Priority و bandwidth را با محدودیت نسخه تطبیق دهید** — LLQ و ضمانت‌های CBWFQ هم‌معنی نیستند؛ سقف مجموع و نحوهٔ باقیماندهٔ پهنای باند در پلتفرم‌ها تفاوت دارد.
2. **صف Priority را همیشه محدود کنید** — بدون سقف، Starvation.
3. **اثر QoS به Congestion و قابلیت Scheduler وابسته است** — سرعت زیاد Congestion را ناممکن نمی‌کند؛ Burst یا Oversubscription هم می‌تواند صف بسازد و offload/بار CPU به پلتفرم بستگی دارد.
4. **QoS روی لینک اشتراکی (اینترنت) محدود است** — شما فقط خروجی خودتان را کنترل می‌کنید، نه مسیر میانی.
5. **Encryption با IPsec سرآیند را تغییر می‌دهد** — پس از Encapsulation امکان Classification/Marking روی DSCP داخلی به نحوهٔ Copy کردن فیلدها، زمان اعمال Policy و پشتیبانی `qos pre-classify` وابسته است؛ دسترسی به سرآیند داخلی را فرض نکنید.
6. **پلتفرم تفاوت دارد** — بعضی مدل‌های Switch فقط QoS سخت‌افزاری دارند و بعضی دستورات Router را پشتیبانی نمی‌کنند. قبل از طراحی، **مستند پلتفرم** الزامی است.

## ۷. عیب‌یابی

| نشانه | علت محتمل | بررسی |
|---|---|---|
| صدا قطع و وصل می‌شود | Congestion واقعی یا نبود LLQ | `show policy-map interface` و `drop rate` |
| تأخیر بالا در همه | Shaping بسیار سخت‌گیرانه | `shape` و صف |
| Drop زیاد | Policing سخت‌گیرانه یا صف کوچک | `drop rate` و `queue limit` |
| QoS اعمال شده ولی اثر ندارد | Trust Boundary اشتباه | `show mls qos interface` |
| علامت‌ها نادیده گرفته می‌شوند | کاربر DSCP را روی PC تنظیم کرده | `trust device` |
| Congestion در جای غلط | Shaper نرخ سرویس را محدود نکرده یا نرخ CIR اشتباه است | `show policy-map interface`، نرخ Shape و Dropهای WAN |
| تعدادی کلاس بی‌صدا مانده‌اند | شرط Classification/DSCP یا درصدهای مجاز اشتباه است | شمارندهٔ Match و `show policy-map` |

**سناریوی نقص طراحی‌شده (اجرا نشده):** اگر ترافیک Voice به سقف `priority percent 50` روی لینک 10 Mbps برسد، تا حدود 5 Mbps به صف Priority اختصاص می‌یابد و می‌تواند ظرفیت قابل‌استفادهٔ کلاس‌های دیگر را کاهش دهد؛ اثر واقعی به سیاست والد و رفتار Scheduler وابسته است. بررسی: `show policy-map interface` و نسبت `offered rate` کلاس‌های مختلف.

## ۸. کاربرگ مستقل و تمرین تحلیلی

**کاربرگ مستقل:** [IS-07 — QoS IOS XE](academy-ccna-services-07-qos-lab-fa.md). تمرین، Classification/Marking ورودی و Shaping/LLQ/CBWFQ خروجی را روی یک روتر مرزیِ آزمایشگاهی به هم وصل می‌کند. توپولوژی آن **تلفن IP، AP/WLC یا Catalyst Access Switch ندارد**؛ بنابراین رفتار `trust device cisco-phone`، CoS ورودیِ تلفن و تجربهٔ واقعی تماس را نمی‌آزماید. Policing نیز در Lab پیکربندی نمی‌شود. هیچ‌یک از این قابلیت‌ها را از خروجی IOS XE در آن کاربرگ نتیجه نگیرید.

پس از تکمیل کاربرگ یا خواندن خروجی‌های طراحی‌شده، به پرسش‌ها با استناد به شاهد پاسخ دهید:

1. در آزمون UDP، چرا باید نرخ Offered و شمارنده‌های Policy را هم‌زمان ثبت کرد؟ نرخ درخواستی `iperf3` به‌تنهایی ثابت نمی‌کند همان بار به روتر رسیده است.
2. اگر بار واقعی از نرخ مؤثر Shaper بیشتر باشد، کدام شاهدها وجود گلوگاه/صف را نشان می‌دهند؟ چه خروجی‌هایی هنوز تأخیر انتهابه‌انتها یا کیفیت تماس واقعی را ثابت نمی‌کنند؟
3. اگر ACL ورودی Match دارد ولی کلاس DSCP خروجی Match ندارد، سه فرضیهٔ قابل‌آزمون پیشنهاد کنید و هرکدام را با کدام Counter/Capture تفکیک می‌کنید.
4. در یک طرح جداگانه با Catalyst و تلفن سازگار، برای ارزیابی Trust Boundary چه مدل/Release، تنظیم پورت، رفتار Phone/PC پشت آن، Packet Marking قبل/بعد از Switch و سند Feature را لازم دارید؟ **این آزمایش اختیاری و خارج از کاربرگ C8000V است**؛ تا اجرای واقعی، پاسخ را «طرح آزمون» بنویسید.
5. در یک مقایسهٔ جدا، تفاوت Policing و Shaping را از نظر محل اعمال، Buffer/Delay و Drop/Mark توضیح دهید؛ از روی کاربرگ حاضر ادعا نکنید Policing اجرا شده است.

**کلید خودسنجی کوتاه:** نرخ ارسال در Generator ممکن است با بار عبوری فرق کند؛ Congestion را با Offered/Output/Queue/Drop و Policy روی Interface واقعی بسنجید؛ ACL hit فقط Classification ورودی را ثابت می‌کند؛ برای Phone Trust، IOS XE Router این Lab شاهد کافی نیست؛ و Policing در این سناریو اصلاً فعال نشده است.


## ۹. سؤال‌ها و پاسخ

1. **زمان‌بندی صف چه زمانی اثر مستقیم بر تأخیر/Drop دارد؟** هنگامی که جریان‌ها برای ظرفیت خروجی رقابت می‌کنند؛ Classification/Marking ممکن است حتی پیش از Congestion برای Policy یا هاپ بعدی اهمیت داشته باشد.

2. **PHB یعنی چه؟** Per-Hop Behavior — هر روتر تصمیم مستقل می‌گیرد با هر کلاس چه کند. QoS یک تصمیم سراسری نیست؛ تصمیم‌های محلی هماهنگ است.

3. **DSCP چند بیت است؟** ۶ بیت، مقادیر ۰ تا ۶۳.

4. **EF چه کلاسی است؟** Expedited Forwarding با مقدار 46، برای صدا.

5. **تفاوت Policing و Shaping چیست؟** Policing Drop می‌کند (یا Mark)، Shaping Buffer (Delay) می‌کند.

6. **چرا صف Priority باید محدود شود؟** بدون سقف، ترافیک آن کلاس می‌تواند تمام پهنای باند را بگیرد و بقیه را گرسنه کند.

7. **Trust Boundary چیست؟** نقطه‌ای که شبکه به DSCP/CoS ورودی اعتماد می‌کند. اگر اشتباه تنظیم شود، کاربران می‌توانند خودشان Priority بگیرند.

8. **`trust device cisco-phone` چه می‌کند؟** در بعضی Catalystها، Trust را به شناسایی تلفن/Policy پورت وابسته می‌کند. این فرمان پلتفرم‌محور است؛ بدون آزمون روی مدل و Release هدف، رفتار PC پشت Phone یا رد همهٔ Markهای PC را تضمین نکنید.

9. **آیا `bandwidth` روی Interface سرعت را محدود می‌کند؟** خیر؛ این فرمان مقدار مرجع/اطلاعاتی است. برای محدودکردن CIR روی رابط سریع‌تر از سرویس، Shaper خروجی (مثل policy والد با `shape average`) لازم است.

10. **درصدهای Priority و bandwidth چه تفاوتی دارند؟** در این نمونه `priority percent` سقف صف LLQ است؛ `bandwidth percent` حداقل تضمین CBWFQ زیر Congestion است. این‌ها سهم ثابت و یکسان‌معنا نیستند.

11. **اگر جمع درصدها ۱۲۰٪ باشد چه می‌شود؟** از یک قانون ثابت برای همهٔ IOSها نتیجه نگیرید؛ ممکن است پیکربندی رد، بیش‌اشتراک یا به‌شکل پلتفرم‌ویژه محاسبه شود. حد مجاز را در مستند همان پلتفرم بررسی و از آن تجاوز نکنید.

12. **آیا یک Policy محلی تضمین QoS انتهابه‌انتهاست؟** خیر. هر گلوگاه/دامنهٔ مدیریتی باید رفتار کلاس‌ها و Trust را طبق نیاز هماهنگ کند؛ روترِ بدون Congestion الزاماً به صف‌بندی ویژه نیاز ندارد، اما DSCP/Policy آن و گلوگاه بعدی باید با انتظار سازگار باشند. نتیجهٔ End-to-End را فقط با سنجش مسیر و سرویس می‌توان ارزیابی کرد.

## واژه‌نامه و چک‌لیست

QoS: کیفیت سرویس؛ PHB: رفتار هر گره؛ DSCP: علامت ۶ بیتی IP؛ CoS: علامت ۳ بیتی 802.1Q؛ LLQ: صف Priority؛ CBWFQ: صف با تضمین پهنای باند؛ Policing: Drop اضافه؛ Shaping: Buffer اضافه؛ Trust Boundary: مرز اعتماد به علامت‌ها؛ Starvation: گرسنه ماندن کلاس دیگر.

- [ ] اثر Queueing/Scheduling را از Classification/Marking جدا می‌کنم.
- [ ] DSCP را از CoS و IP Precedence جدا می‌کنم.
- [ ] Policing را از Shaping در اثر عملی تفکیک می‌کنم.
- [ ] صف Priority را همیشه محدود می‌کنم.
- [ ] Trust Boundary را در لبهٔ درست تنظیم می‌کنم.
- [ ] می‌دانم پیکربندی QoS به پلتفرم وابسته است و مستند لازم دارد.

## منابع فنی

- [RFC 2474 — Definition of the Differentiated Services Field (DS Field)](https://www.rfc-editor.org/rfc/rfc2474.html)
- [RFC 2475 — An Architecture for Differentiated Services](https://www.rfc-editor.org/rfc/rfc2475.html)
- [RFC 3246 — An Expedited Forwarding PHB](https://www.rfc-editor.org/rfc/rfc3246.html)

نحو `class-map`/`policy-map`، سقف درصدها، H-QoS و رفتار Queue/Hardware را فقط از مستند IOS/IOS-XE مدل/نسخهٔ انتخابی بگیرید؛ مثال‌های بالا اجرا نشده‌اند.
