# CCNA IC-05 — Area، LSA، LSDB و Troubleshooting در OSPF

**سطح:** CCNA. **پیش‌نیاز:** IC-03 و IC-04. **اهداف رسمی:** تکمیل `3.4` در سطح مفهومی و عیب‌یابی؛ Area، LSA و LSDB. **وضعیت:** پیش‌نویس محتوایی؛ فرمان‌ها و خروجی‌ها طراحی‌شده و **اجرا نشده‌اند**. مدل و نسخهٔ IOS انتخاب نشده است.

## اهداف

1. نقش Area و تفاوت ABR با ASBR را توضیح دهید.
2. انواع LSA را با **شماره** بشناسید و بدانید هر کدام چه چیزی را توصیف می‌کند.
3. بفهمید Adjacency و همگام‌سازی LSDB چه رابطه‌ای دارند — و **ترتیب** آن را.
4. یک عیب OSPF را گام‌به‌گام ریشه‌یابی کنید.

## ۱. Area — چرا OSPF شبکه را تقسیم می‌کند؟

**مسئله:** OSPF یک پروتکل **Link-State** است و هر روتر برای هر Area، LSDB و محاسبهٔ توپولوژی خودش را نگه می‌دارد. بزرگ‌شدن Area می‌تواند حافظه، تعداد LSA و هزینهٔ محاسبهٔ مسیر را بالا ببرد؛ اثر واقعی به توپولوژی، نرخ تغییر، سخت‌افزار، نسخه و رفتار SPF وابسته است.

| مفهوم | توضیح دقیق |
|---|---|
| LSDB / Flooding | LSAهای هم‌دامنهٔ انتشار میان روترهای Area توزیع می‌شوند؛ ACK، زمان‌بندی و کنترل سیلینگ هم وجود دارد |
| SPF | روتر وقتی LSAهای مؤثر بر توپولوژی تغییر کنند، محاسبهٔ خود را به‌روزرسانی می‌کند؛ هر LSA یا هر Packet الزاماً SPF کامل در همهٔ روترها ایجاد نمی‌کند |
| بین Areaها | ABR اطلاعات مسیر را به‌صورت LSAهای Summary/مسیر قابل‌دسترس تبلیغ می‌کند؛ بعضی تغییرها می‌توانند به Areaهای دیگر هم برسند |
| مقیاس | چند Area می‌تواند دامنهٔ جزئیات توپولوژی/محاسبه را محدود کند، اما طراحی و نگهداری را پیچیده‌تر می‌کند |

**نتیجه:** Area‌بندی ابزار کنترل مقیاس است، نه تضمین همگرایی سریع‌تر برای هر شبکه. تغییر توپولوژی داخل یک Area معمولاً جزئیات LSA و محاسبهٔ همان Area را درگیر می‌کند؛ اثر مسیر بین‌Area می‌تواند از ABR عبور کند. طراحی باید تعداد روتر، LSA، نرخ رخداد و نیاز عملیاتی را درنظر بگیرد.

### قواعد Area

1. **Area 0 ستون فقرات منطقی OSPF است.** در طراحی معمول، هر Area غیرستون‌فقرات باید از طریق ABR به Backbone متصل شود؛ Virtual Link راهکار استثنایی/موقت در توپولوژی‌های خاص است، نه جایگزین طراحی پایه.
2. روترهای یک Area پس از همگرایی، مجموعهٔ LSAهای **هم‌دامنه و هم‌نوع** را همگام می‌کنند؛ Area/Scope را هنگام مقایسهٔ LSDB رعایت کنید.
3. ABR مسیرهای بین‌Area را در LSAهای مناسب (مانند Type 3/4) تبلیغ می‌کند؛ جزئیات داخلی Area دیگر لزوماً به شکل نقشهٔ لینک کامل منتقل نمی‌شود. خلاصه‌سازی Prefix قابلیت طراحی/پیکربندی است و خودکار بودن آن را فرض نکنید.

### ABR در برابر ASBR — تفاوت مهم

| نقش | مرز بین چه چیزی | مثال |
|---|---|---|
| **ABR** (Area Border Router) | چند Area در یک Router؛ در طراحی معمول یکی از آن‌ها Area 0 است | روتری با `Gi0/0` در Area 0 و `Gi0/1` در Area 1؛ می‌تواند Areaهای بیشتری داشته باشد |
| **ASBR** (Autonomous System Boundary Router) | OSPF و یک منبع مسیر خارجی (پروتکل دیگر یا Connected/Static طبق طراحی) | روتری که با Redistribution مسیرهای Static یا EIGRP را وارد OSPF می‌کند |

**خطای رایج:** این دو را یکی گرفتن. یک روتر می‌تواند **هم** ABR باشد **هم** ASBR. تفاوت در **نوع مرز** است، نه در دستگاه.

![نمودار قابل ویرایش Area، ABR و LSDB؛ اجرا‌نشده](academy-images/ic-05-lsa-area.svg)

## ۲. LSA — شش نوع با کاربرد

**LSA** (Link-State Advertisement) ساختار اطلاعاتی است که بخشی از State/Reachability را توصیف می‌کند؛ در OSPF در پیام‌های Link-State Update حمل می‌شود، پس خود LSA را با Packet/LSU یکی نگیرید. **LSDB** مجموعهٔ LSAهای با Scope مربوط در پایگاه دادهٔ روتر است؛ برخی LSAها Area-scoped و برخی OSPF-domain-scoped هستند.

| نوع | نام | چه چیزی را توصیف می‌کند | تولیدکننده | گسترهٔ انتشار |
|---|---|---|---|---|
| **Type 1** | Router LSA | لینک‌های مستقیم یک روتر و وضعیت آن‌ها | هر روتر | **داخل Area** |
| **Type 2** | Network LSA | شبکهٔ Broadcast و فهرست روترهای متصل به آن (DR) | **DR** | داخل Area |
| **Type 3** | Summary LSA | یک شبکه در Area دیگر (خلاصه) | **ABR** | به Areaهای دیگر |
| **Type 4** | ASBR Summary LSA | مسیر رسیدن به ASBR | **ABR** | به Areaهای دیگر |
| **Type 5** | External LSA | مسیر خارج از OSPF (Static، EIGRP، ...) | **ASBR** | **کل دامنه** (بجز Stub) |
| Type 7 | NSSA External | مسیر خارجی داخل NSSA | ASBR در NSSA | داخل NSSA؛ ABR منتخب معمولاً آن را هنگام خروج به Type 5 ترجمه می‌کند، طبق سیاست/پیکربندی |

**آن‌چه برای CCNA باید حفظ شود: ۱، ۲، ۳، ۵؛** Type 4 برای رسیدن به ASBR و Type 7 در NSSA را نیز از نظر نام/محدوده بشناسید.
- **۱** = روتر و لینک‌هایش
- **۲** = شبکهٔ Broadcast و DR
- **۳** = شبکه در Area دیگر (از ABR)
- **۵** = مسیر خارجی (از ASBR)

**نکتهٔ ظریف:** روی Interfaceای که **OSPF Network Type آن Point-to-Point** است، **Type 2 وجود ندارد** چون DR/BDR انتخاب نمی‌شود. Prefix `/30` یا کابل مستقیم به‌تنهایی OSPF را P2P نمی‌کند؛ روی Ethernet، Network Type پیش‌فرض معمولاً Broadcast است مگر تنظیم شود. اگر نوع Interface واقعاً P2P است و برای همان لینک Type 2 نمی‌بینید، این **طبیعی** است، نه خطا.

## ۳. Adjacency و همگام‌سازی LSDB — رابطهٔ درست

**این نکته در بسیاری از منابع غلط گفته می‌شود.** رابطهٔ درست:

```text
DOWN → INIT → 2-WAY → EXSTART → EXCHANGE → LOADING → FULL
                          ↑          ↑         ↑
                    Master/Slave   تبادل DBD   درخواست LSAهای غایب
                     تعیین می‌شود
```

پس از توافق اولیه، خلاصهٔ LSDB در `EXCHANGE` مقایسه می‌شود؛ LSAهای لازم در `LOADING` درخواست/دریافت می‌شوند. **`FULL` یعنی Adjacency کامل و همگام‌سازی LSAهای مربوط به آن Adjacency تمام شده است.**

پس این جمله **برعکس** است: «اگر LSDB دو روتر متفاوت باشد، Adjacency کامل نمی‌شود.» واقعیت:

- دو روتر با LSDB **متفاوت** می‌توانند Adjacency بسازند — خلاصهٔ Database Description تفاوت‌ها را آشکار می‌کند و LSAهای لازم تبادل می‌شوند.
- در حالت `FULL`، LSDBهای هم‌Area و هم‌Scope باید پس از همگرایی سازگار باشند؛ مقایسهٔ Areaهای متفاوت، LSAهای Type 5/7، زمان‌های متفاوت یا رکوردهای درحال‌تازه‌سازی می‌تواند ظاهراً فرق کند. اختلاف پایدار را با Area/Scope، Seq/Checksum/Age و نسخه/فیلتر مجاز بررسی کنید؛ Timer mismatch یا MTU معمولاً مانع رسیدن به FULL می‌شوند، نه توضیح عمومی برای تفاوت پایدار بعد از FULL.

| حالت | معنا | آیا LSDB همگام است؟ |
|---|---|---|
| `2-WAY` | روی Broadcast، دو DROther با یکدیگر در این حالت می‌مانند؛ هرکدام با DR/BDR همسایهٔ کامل می‌شوند | همگام‌سازی کامل نشده است |
| `EXSTART` | تعیین Master/Slave، تبادل اولیه | نه |
| `EXCHANGE` | تبادل DBD (فهرست LSAها) | در حال انجام |
| `LOADING` | درخواست LSAهای غایب با LSR | در حال انجام |
| `FULL` | همسایگی کامل | **بله** |

`2-WAY` روی دو **DROther** در یک شبکهٔ Broadcast **طبیعی** است: آن‌ها با هم Adjacency کامل نمی‌سازند، چون هر دو با DR/BDR کامل می‌شوند، نه با یکدیگر. روی P2P معمولاً همسایه باید به FULL برسد؛ Network Type را از تنظیم Interface بخوانید، نه از Prefix یا کابل به‌تنهایی.

## ۴. عیب‌یابی گام‌به‌گام

ترتیب بررسی، از لایهٔ پایین به بالا:

| گام | چه چیزی | فرمان | علامت خطا |
|---|---|---|---|
| ۱ | Interface up و آدرس درست | `show ip interface brief` | `down/down` یا آدرس اشتباه |
| ۲ | همان Subnet و Area | `show ip ospf interface` | Area متفاوت |
| ۳ | Router ID یکتا | `show ip ospf` | Router ID تکراری |
| ۴ | Timer و نوع شبکه | `show ip ospf interface` | Hello/Dead ناسازگار |
| ۵ | MTU | `show interfaces` | `EXSTART` گیر می‌کند |
| ۶ | Neighbor و وضعیت | `show ip ospf neighbor` | `INIT`، `2-WAY`، `EXSTART` |
| ۷ | LSDB | `show ip ospf database` | LSA غایب |
| ۸ | جدول Routing | `show ip route ospf` | مسیر نصب نمی‌شود |

**MTU و `EXSTART`/`EXCHANGE`:** در مذاکرهٔ DBD، OSPF رابط/MTU را دربرابر حد قابل‌پذیرش بررسی می‌کند؛ ناهماهنگی می‌تواند باعث رد DBD و ناتمام‌ماندن Adjacency شود. این یک فرضیهٔ رایج است، نه تنها علت. نخست MTU و پشتیبانی دو سمت را بررسی کنید. یکسان‌سازی MTU معمولاً راه‌حل اصلی است. `ip ospf mtu-ignore` در IOSهای پشتیبان، بررسی MTU را دور می‌زند و ممکن است Adjacency را بالا بیاورد، اما MTU واقعی مسیر را اصلاح نمی‌کند و می‌تواند Packetهای بزرگ را بعداً Black-hole کند؛ فقط در Lab/با توجیه و Verification انتهابه‌انتها به‌کار ببرید.

## ۵. Verification و تفسیر خروجی

**نمونهٔ طراحی‌شده، اجرا‌نشده.**

```text
R1# show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/DR         00:00:38    192.0.2.2       GigabitEthernet0/0
3.3.3.3           1   FULL/BDR        00:00:35    192.0.2.3       GigabitEthernet0/0
4.4.4.4           0   FULL/  -        00:00:37    192.0.2.4       GigabitEthernet0/1
```

**خط‌به‌خط — این خروجی سه چیز متفاوت را نشان می‌دهد:**

- `Neighbor ID 2.2.2.2` — Router ID همسایه. اگر این عدد با `show ip ospf` روی خودِ همسایه یکی نباشد، Router ID اشتباه است.
- `Pri 1` — Priority همسایه. ستون سوم نقش را تعیین می‌کند.
- `State: FULL/DR` — همسایگی کامل است و این همسایه **DR** همان شبکه است.
- `State: FULL/BDR` — همسایهٔ دوم **Backup DR**.
- **`State: FULL/  -` (خط چهارم)** — خط تیره یعنی همسایه نقش DR/BDR ندارد؛ در این مثال، فقط اگر `Gi0/1` با Network Type صریح Point-to-Point پیکربندی شده باشد، این انتظار طبیعی است. Prefix `/30` به‌تنهایی Network Type را تعیین نمی‌کند؛ `show ip ospf interface Gi0/1` را برای نوع شبکه ببینید. `Pri 0` به‌تنهایی نیز اثبات P2P نیست. **این خروجی، طرح آموزشی است.**
- `Dead Time` — شمارش معکوس تا انقضای Neighbor، که Hello معتبر آن را تازه می‌کند. اگر زمان منقضی شود، Neighbor حذف و بعداً ممکن است دوباره ساخته شود؛ نوسان را با Timestamp/Log، Packet loss، CPU و Link بررسی کنید.

```text
R1# show ip ospf database

            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum Link count
1.1.1.1         1.1.1.1         342         0x80000004 0x00A1B2 2
2.2.2.2         2.2.2.2         344         0x80000003 0x00C3D4 2

                Net Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum
192.0.2.2       2.2.2.2         344         0x80000001 0x00E5F6
```

- `OSPF Router with ID (1.1.1.1)` — این روتر خودش. پروسه `1`.
- `Router Link States` = **Type 1**. این نمونه کوتاه‌شده است؛ چند ردیف نمونه نشان داده شده و سایر LSAها حذف شده‌اند. `ADV Router` = Router ID تولیدکنندهٔ LSA.
- `Link count 2` — در این LSA دو Link Description شمرده شده، نه لزوماً دو رابط فیزیکی. Router LSA می‌تواند Transit Network، Stub Network، لینک روتر، Loopback و نوع‌های دیگر را با ساختارهای متفاوت توصیف کند؛ اگر تعداد با انتظار توپولوژی نمی‌خواند، Type/Link ID هر ورودی و تنظیم OSPF هر Interface را بررسی کنید، نه این‌که فقط از عدد نتیجه بگیرید رابطی ثبت نشده است.
- `Age` — سن LSA به ثانیه. در OSPFv2، MaxAge برابر 3600 ثانیه است؛ LSA با MaxAge برای Flush منتشر و سپس از LSDB حذف می‌شود. LSAها می‌توانند پیش از آن طبق زمان Refresh دوباره Originate شوند؛ عدد Age به‌تنهایی خرابی نیست.
- `Seq#` — شمارهٔ ترتیب. هر تبلیغ جدید یک واحد بالا می‌رود (`0x80000004`). این مکانیزم، نسخهٔ تازه‌تر را تشخیص می‌دهد.
- `Net Link States` = **Type 2**. فقط **یک** ردیف، با `ADV Router 2.2.2.2` (که DR است). حتی اگر ۳ روتر در همان شبکه باشند، باز هم یک Type 2 وجود دارد، چون فقط DR آن را تولید می‌کند.

## ۶. کاربرگ مستقل PNETLab — Area و انواع LSA

**طراحی‌شده و اجرا‌نشده.** سه Router IOSv/IOL سازگار، یک Switch لایهٔ ۲ برای Area 0، یک لینک مجزای R1–R3 برای Area 1، Console و Image/Version ثبت‌شده لازم‌اند. هیچ اتصال بیرونی ندارد. قبل از اجرا Snapshot بگیرید؛ نام Interface و پشتیبانی `Null0`/فرمان‌ها را در Image بررسی کنید.

```text
Area 0 broadcast: R1 Gi0/0 192.0.2.1/24 ─┐
                                         ├─ SW-LAB
                   R2 Gi0/0 192.0.2.2/24 ─┘
Area 1 P2P:       R1 Gi0/2 203.0.113.1/30 ── R3 Gi0/0 203.0.113.2/30
R2 Lo0 10.2.2.2/32 (Area 0) · R3 Lo0 10.3.3.3/32 (Area 1)
R2 exports only static 172.31.100.0/24 via Null0 as an example external route.
```

**Address/Role Plan**

| Router | Interface | Address | Area/Role |
|---|---|---|---|
| R1, RID `1.1.1.1` | Gi0/0 | `192.0.2.1/24` | Area 0 Broadcast; ABR |
| R1 | Gi0/2 | `203.0.113.1/30` | Area 1, explicit OSPF Point-to-Point |
| R2, RID `2.2.2.2` | Gi0/0 | `192.0.2.2/24` | Area 0 Broadcast; Priority 200; ASBR |
| R2 | Lo0 | `10.2.2.2/32` | Area 0 internal prefix |
| R2 | Static to `Null0` | `172.31.100.0/24` | One controlled external prefix |
| R3, RID `3.3.3.3` | Gi0/0 | `203.0.113.2/30` | Area 1, explicit OSPF Point-to-Point |
| R3 | Lo0 | `10.3.3.3/32` | Area 1 internal prefix |

Ethernet `/30` does not automatically mean OSPF P2P. To observe that LSA distinction, configure Point-to-Point network type on **both ends** of the R1–R3 link. The Area 0 Ethernet remains Broadcast; if OSPF is brought up with R2 Priority 200 before the first election, expect R2 DR and R1 BDR (subject to already-established election state).

### پیکربندی نمونهٔ مستقل (فرمان‌ها اجرا‌نشده)

R1:

```text
enable
configure terminal
interface GigabitEthernet0/0
 ip address 192.0.2.1 255.255.255.0
 no shutdown
exit
interface GigabitEthernet0/2
 ip address 203.0.113.1 255.255.255.252
 ip ospf network point-to-point
 no shutdown
exit
router ospf 1
 router-id 1.1.1.1
 network 192.0.2.0 0.0.0.255 area 0
 network 203.0.113.0 0.0.0.3 area 1
end
```

R2:

```text
enable
configure terminal
interface GigabitEthernet0/0
 ip address 192.0.2.2 255.255.255.0
 ip ospf priority 200
 no shutdown
exit
interface Loopback0
 ip address 10.2.2.2 255.255.255.255
exit
ip route 172.31.100.0 255.255.255.0 Null0
router ospf 1
 router-id 2.2.2.2
 network 192.0.2.0 0.0.0.255 area 0
 network 10.2.2.2 0.0.0.0 area 0
 redistribute static subnets
end
```

R3:

```text
enable
configure terminal
interface GigabitEthernet0/0
 ip address 203.0.113.2 255.255.255.252
 ip ospf network point-to-point
 no shutdown
exit
interface Loopback0
 ip address 10.3.3.3 255.255.255.255
exit
router ospf 1
 router-id 3.3.3.3
 network 203.0.113.0 0.0.0.3 area 1
 network 10.3.3.3 0.0.0.0 area 1
end
```

`redistribute static subnets` اینجا فقط Static آزمایشی `172.31.100.0/24` را وارد OSPF می‌کند؛ Default Route نداریم. فرمان‌های Redistribution روی شبکهٔ عملیاتی خطرناک‌اند. Syntax و LSA/metric دقیق را با IOS هدف تطبیق دهید.

### Verification و آزمون‌ها

1. روی هر Router `show ip ospf neighbor`, `show ip ospf interface` و `show ip ospf database` بگیرید. در Area 0 انتظار Type 1 و Type 2 از DR (R2)؛ در لینک Area 1 با Network Type P2P، Type 1 اما نه Type 2 برای همان لینک را بررسی کنید.
2. در Area 1، Type 3 مربوط به مسیر داخلی Area 0 (مثل `10.2.2.2/32`) و Type 4 برای دسترسی به ASBR `2.2.2.2` را بررسی کنید؛ R1 به‌عنوان ABR آنها را تبلیغ می‌کند.
3. R2 باید برای `172.31.100.0/24`، Type 5 بسازد؛ R3 در Area 1 باید External route را ببیند. وجود Route را در `show ip route ospf` و نوع LSA را در `show ip ospf database` با جزئیات همان نسخه تطبیق دهید.
4. `show ip ospf database` را بین روترها فقط برای Area/Scope و زمان Snapshot یکسان مقایسه کنید؛ Router LSA برای هر Area جداگانه است و همهٔ Areaها یک LSDB واحد ندارند.
5. **Area Mismatch:** در R3 زیر `router ospf 1` ابتدا `no network 203.0.113.0 0.0.0.3 area 1` و سپس `network 203.0.113.0 0.0.0.3 area 0` را موقتاً تنظیم کنید؛ R1–R3 روی آن Interface Area mismatch دارند و Adjacency نباید Full شود. بازیابی: `no network 203.0.113.0 0.0.0.3 area 0`, سپس `network 203.0.113.0 0.0.0.3 area 1`; Neighbor و Routeهای Area1 را Verify کنید.
6. **MTU:** فقط در لاب، یک سر لینک R1–R3 را موقتاً با `ip mtu 1400` تغییر دهید و State دو طرف را ببینید. رفتار `EXSTART/EXCHANGE` نسخه‌محور است. MTU را به مقدار اولیه بازگردانید؛ `ip ospf mtu-ignore` را به‌عنوان راه‌حل دائمی به‌کار نبرید. اگر برای مقایسهٔ آموزشی موقتاً آن را آزمودید، مقدار واقعی MTU و اندازهٔ Packet را نیز Verify و سپس Ignore را حذف کنید.
7. **Router ID تکراری:** در لاب Snapshotدار RID یکی از Routerها را موقتاً تکرار کنید؛ پیام/اثر را در هر دو سمت ثبت کنید؛ رفتار دقیق نسخه‌ها فرق می‌کند. سپس RID یکتا را برگردانید و با Console/`show ip ospf` وضعیت را دوباره Verify کنید.
8. خروجی‌های حقیقی، Timestamp، Image/Version و نتیجهٔ هر نقص را ثبت کنید؛ همهٔ مقادیر و Routeها را به Snapshot اولیه برگردانید. هیچ‌یک از این مراحل در این سند اجرا نشده است.

**معیار موفقیت:** Area/Scope هر Interface درست؛ همسایگی‌ها متناسب با Broadcast/P2P؛ Type 1/2/3/4/5 با تولیدکننده/Scope مورد انتظار مشاهده شوند؛ تفاوت RIB و LSDB تشخیص داده شود؛ Area/MTU/RID fault به‌شکل ایزوله بازیابی شوند و خروجی واقعی ثبت شود. در غیر این صورت، علت نامعلوم را باز نگه دارید—نمودار یا خروجی نمونه شاهد اجرا نیست.

## ۷. سؤال‌ها و پاسخ

1. **Area چیست؟** تقسیم شبکه برای کوچک نگه داشتن LSDB و سریع نگه داشتن SPF.

2. **Area 0 چیست؟** ستون فقرات OSPF. همهٔ Areaهای دیگر باید به آن متصل باشند.

3. **ABR چیست؟** روتری با Interface در دو یا چند Area؛ در طراحی معمول، حداقل یکی Area 0 است.

4. **ASBR چیست؟** روتری که Routeهای منبع خارجی (پروتکل دیگر، Static یا Connected طبق Policy) را وارد OSPF می‌کند.

5. **آیا یک روتر می‌تواند هم ABR هم ASBR باشد؟** بله. تفاوت در نوع مرز است، نه دستگاه.

6. **LSA چیست؟** بسته‌ای که اطلاعات یک بخش از توپولوژی را توصیف می‌کند.

7. **LSDB چیست؟** مجموعهٔ LSAهای قابل‌دسترسی در Scope/Area مربوط؛ روترهای یک Area پس از همگرایی، LSAهای هم‌نوع/هم‌دامنه را همگام دارند.

8. **Type 1 چه چیزی را توصیف می‌کند؟** روتر و لینک‌های مستقیمش.

9. **Type 2 چه چیزی را توصیف می‌کند؟** شبکهٔ Broadcast و فهرست روترهای متصل، تولیدشده توسط DR.

10. **چرا روی Interface با OSPF Network Type=Point-to-Point Type 2 نداریم؟** چون در این نوع شبکه DR/BDR انتخاب نمی‌شود. یک Prefix مثل `/30` به‌تنهایی P2P بودن OSPF را ثابت نمی‌کند.

11. **Type 3 از چه کسی می‌آید؟** از ABR، برای توصیف شبکه‌های Area دیگر.

12. **Type 5 از چه کسی می‌آید؟** از ASBR، برای مسیرهای خارج از OSPF.

13. **آیا LSDB متفاوت باعث می‌شود Adjacency کامل نشود؟** **نه** — برعکس. Adjacency برای همگام‌سازی LSDB ساخته می‌شود. LSDB در مرحلهٔ EXCHANGE/LOADING مبادله می‌شود و FULL یعنی همگام‌سازی تمام شده.

14. **اگر بعد از FULL، LSDB دو طرف متفاوت به‌نظر برسد، چه می‌کنیم؟** Area و Scope، زمان Snapshot، نوع LSA، Sequence/Checksum و همگرایی را در دو طرف مقایسه می‌کنیم؛ فقط اختلاف پایدارِ هم‌Scope نشانهٔ نیازمند بررسی است. MTU/Timer معمولاً Adjacency را از FULL بازمی‌دارند.

15. **MTU mismatch همیشه `EXSTART` می‌سازد؟** خیر، رفتار به پلتفرم و مقدار/مسیر بستگی دارد؛ DBD/Interface MTU را در هر دو سمت بررسی کنید. `mtu-ignore` کنترل را دور می‌زند و اندازهٔ واقعی مسیر را حل نمی‌کند.

16. **`2-WAY` همیشه خطا است؟** نه. روی دو DROther در شبکهٔ Broadcast طبیعی است.

17. **`Age 3600` یعنی چه؟** LSA به MaxAge رسیده و برای Flush/حذف منتشر می‌شود؛ تازه‌سازی و حذف را با Sequence/نوع LSA و وضعیت همسایه‌ها تفسیر کنید.

18. **آیا این درس اجرا شده است؟** خیر.

## واژه‌نامه و چک‌لیست

**Area**: تقسیم شبکه؛ **LSA**: اطلاعات لینک؛ **LSDB**: پایگاه دادهٔ حالت لینک؛ **ABR**: روتر مرزی Area؛ **ASBR**: روتر مرزی AS؛ **DR/BDR**: روتر طراحی‌شده؛ **DROther**: روتر غیر DR/BDR؛ **MaxAge**: سن ۳۶۰۰ ثانیهٔ انقضای LSA.

- [ ] می‌دانم Adjacency **قبل** از همگام‌سازی LSDB ساخته می‌شود، نه بعد از آن.
- [ ] Type 1/2/3/5 را با کاربرد می‌شناسم.
- [ ] می‌دانم در P2P هیچ Type 2 و هیچ نقش DR وجود ندارد.
- [ ] MTU را به‌عنوان علت گیر کردن در EXSTART می‌شناسم.
- [ ] `2-WAY` بین DROtherها را طبیعی می‌دانم.
- [ ] هیچ خروجی فرضی را واقعی اعلام نمی‌کنم.
