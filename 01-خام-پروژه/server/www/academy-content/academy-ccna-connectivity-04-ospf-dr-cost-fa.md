# CCNA IC-04 — OSPF در شبکهٔ Broadcast، DR/BDR و Cost

**سطح:** CCNA. **پیش‌نیاز:** IC-03. **اهداف رسمی:** `3.4.c` لینک Broadcast در Single-Area و انتخاب DR/BDR؛ تکمیل مفهوم Cost در انتخاب مسیر. **وضعیت:** پیش‌نویس؛ فرمان‌ها و خروجی‌ها طراحی‌شده و اجرا‌نشده‌اند؛ مدل و نسخهٔ IOS انتخاب نشده است.

## اهداف

در شبکهٔ Broadcast، نقش DR و BDR را تفسیر کنید، انتخابات را با Priority و Router ID توضیح دهید و Cost را در انتخاب مسیر اعمال کنید.

## ۱. چرا DR/BDR؟

در شبکهٔ Broadcast با چند روتر، اگر همه با هم Adjacency کامل بسازند، تعداد همسایگی‌ها زیاد می‌شود. برای کاهش تبادل، یک روتر به‌عنوان **DR** و یکی به‌عنوان **BDR** انتخاب می‌شوند؛ DROtherها با DR/BDR به حالت `FULL` می‌رسند و معمولاً میان خودشان در `2-WAY` می‌مانند. انتخابات با **Interface Priority** (بالاتر بهتر؛ صفر یعنی عدم شرکت) و سپس Router ID بزرگ‌تر انجام می‌شود؛ مقدار پیش‌فرض Priority در IOSهای رایج 1 است.

انتخاب در شکل‌گیری رابطهٔ همسایگی انجام می‌شود و معمولاً **preemptive نیست**: اگر DR فعلی زنده بماند، بالا بردن Priority روتر دیگری به‌تنهایی انتخابات را عوض نمی‌کند. برای آزمون انتخاب تازه، در لاب ایزوله همسایگی/فرایند را با روش پشتیبانی‌شده بازآغاز کنید. در لینک Point-to-Point، DR/BDR وجود ندارد. در Multiaccess، `2-WAY` میان دو DROther معمول است؛ اگر هیچ همسایه‌ای با نقش DR/BDR به `FULL` نمی‌رسد، وضعیت Interface، نوع شبکه و Neighborها را بررسی کنید. با از دست رفتن DR، BDR ارتقا می‌یابد و انتخابات برای BDR تازه صورت می‌گیرد.

## ۲. سناریوی سه روتر

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده:** سه روتر R1، R2 و R3 روی یک LAN با شبکهٔ `192.0.2.0/24`، Area 0. Router IDها به‌ترتیب `1.1.1.1`، `2.2.2.2` و `3.3.3.3` هستند. نام تصویر و نسخه تأیید نشده‌اند.

| روتر | Router ID | آدرس LAN |
|---|---|---|
| R1 | `1.1.1.1` | `192.0.2.1/24` |
| R2 | `2.2.2.2` | `192.0.2.2/24` |
| R3 | `3.3.3.3` | `192.0.2.3/24` |

![نمودار قابل ویرایش DR و BDR در OSPF؛ اجرا‌نشده](academy-images/ic-04-dr-bdr.svg)

## ۳. پیکربندی پیشنهادی

**فرمان‌ها اجرا‌نشده‌اند.** روی هر سه روتر:

```text
configure terminal
router ospf 1
 router-id <Router ID یکتا>
 network 192.0.2.0 0.0.0.255 area 0
end
```

روی R3 برای افزایش شانس DR:

```text
interface GigabitEthernet0/0
 ip ospf priority 200
 no shutdown
end
```

`ip ospf priority` شانس DR شدن را تعیین می‌کند؛ پیش‌فرض معمولاً 1 است و 0 یعنی عدم شرکت در انتخابات. انتظار طراحی، DR شدن R3 و BDR شدن R2 است؛ نتیجهٔ واقعی فقط با خروجی تأیید می‌شود.

## ۴. Cost و انتخاب مسیر

هر رابط OSPF یک **Cost** دارد که معمولاً از Reference Bandwidth و Bandwidth رابط محاسبه می‌شود؛ الگوریتم مسیر، Cost رابط‌های مسیر را جمع می‌کند و کم‌هزینه‌ترین مسیر را ترجیح می‌دهد. Bandwidth اسمی بیشتر معمولاً Cost همان Interface را کم می‌کند، اما اگر Reference Bandwidth پایین باشد چند سرعت مختلف ممکن است همگی Cost برابر بگیرند.

```text
Cost = Reference Bandwidth / Interface Bandwidth
Reference Bandwidth پیش‌فرض = 100 Mbps = 100,000 kbps
```

### محاسبه با عدد واقعی

| Interface | Bandwidth | محاسبه | Cost |
|---|---|---|---|
| Serial 1544 kbps | 1.544 Mbps | 100,000 / 1,544 | **64** |
| FastEthernet | 100 Mbps | 100,000 / 100,000 | **1** |
| GigabitEthernet | 1000 Mbps | 100,000 / 1,000,000 | **1** |
| 10 GigabitEthernet | 10,000 Mbps | 100,000 / 10,000,000 | **1** |

**نکتهٔ بحرانی و پرتکرار:** هزینهٔ GigabitEthernet و 10G و 100G همه **۱** می‌شوند، چون همه سریع‌تر از Reference Bandwidth هستند. یعنی OSPF **تفاوت بین ۱G و ۱۰G را نمی‌بیند** و ممکن است مسیر ۱G را انتخاب کند در حالی که ۱۰G بهتر بود.

**راه‌حل:** `auto-cost reference-bandwidth` را بالا ببرید:

```text
router ospf 1
 auto-cost reference-bandwidth 100000
```

در نسخه‌های رایج IOS/IOS-XE، مقدار `100000` با واحد Mbps معادل مرجع 100 Gbps است؛ بازه و سقف مجاز را در Command Reference همان Image بررسی کنید. **مقدار Reference Bandwidth باید روی روترهای Area یکسان باشد.** اگر متفاوت باشد، هر روتر ممکن است Cost و مسیر بهینهٔ متفاوتی حساب کند؛ این ناسازگاری می‌تواند مسیرهای نامطلوب/نامتقارن بسازد، اما به‌تنهایی وقوع حلقه را تضمین نمی‌کند.

با `ip ospf cost` می‌توان Cost Interface را دستی تعیین کرد؛ این مقدار در آن رابط بر محاسبهٔ خودکار اولویت دارد. `show ip ospf interface` و `show ip route ospf` را کنار توپولوژی بخوانید و تغییر مرجع را هم‌زمان و هماهنگ روی همهٔ روترها اعمال کنید. سقف مقدار، واحد، رفتار Auto-Cost و نحو CLI به نسخه/پلتفرم وابسته‌اند؛ این مثال‌ها در IOS اجرا نشده‌اند.

**خروجی آموزشی، اجرا‌نشده:**

```text
R1# show ip ospf neighbor
Neighbor ID     Pri   State            Dead Time   Address   Interface
3.3.3.3         200   FULL/DR          40s         192.0.2.3 Gi0/0
2.2.2.2         1     FULL/BDR         40s         192.0.2.2 Gi0/0
```

`FULL/DR` یعنی همسایه DR است؛ `FULL/BDR` یعنی BDR. روترهای دیگر در حالت `2-WAY` با هم می‌مانند. فرمان‌های `show ip ospf interface` و `show ip route` برای Cost و مسیر مفیدند.

## ۵. کاربرگ مستقل PNETLab — DR/BDR در Broadcast

**Objective عملی `3.4.c`:** پیکربندی و Verification همسایگی OSPFv2 در شبکهٔ Broadcast و انتخاب DR/BDR. **طراحی شده؛ اجرا نشده است.** سه روتر IOSv/IOL به یک Ethernet switch داخلی وصل کنید؛ هیچ اتصال بیرونی لازم نیست.

```text
R1 Gi0/0 192.0.2.1/24 ─┐
R2 Gi0/0 192.0.2.2/24 ─┼── SW-LAB (یک Broadcast LAN؛ Area 0)
R3 Gi0/0 192.0.2.3/24 ─┘
Router-ID: R1 1.1.1.1 · R2 2.2.2.2 · R3 3.3.3.3
```

پیش از اجرا Image، نسخه، نام Interface، پشتیبانی OSPF و Link Type را ثبت کنید. Snapshot بگیرید؛ هر سه روتر باید در یک Subnet/Area باشند. نمونهٔ پیکربندی اجرا‌نشده روی هر Router:

```text
interface GigabitEthernet0/0
 ip address 192.0.2.X 255.255.255.0
 no shutdown
router ospf 1
 router-id X.X.X.X
 network 192.0.2.0 0.0.0.255 area 0
```

در R3، پیش از برقراری همسایگی یا پس از پاک‌سازی کنترل‌شدهٔ فرایند، روی همان Interface `ip ospf priority 200` بگذارید؛ R1/R2 را روی Priority پیش‌فرض 1 نگه دارید. سپس `show ip ospf interface Gi0/0` و `show ip ospf neighbor` را روی هر سه Router ثبت کنید. انتظار: R3، DR؛ R2، BDR (در تساوی Priority، Router ID بزرگ‌تر میان R1/R2)؛ R1، DROther. R3 با هر دو `FULL` می‌شود؛ R1 و R2 با هم معمولاً `2-WAY/DROTHER` می‌مانند.

**نقص کنترل‌شده:** در R3، Priority را به صفر تغییر دهید. چون انتخابات معمولاً preemptive نیست، ابتدا ممکن است نقش DR فعلی تغییر نکند؛ در لاب Snapshotدار، OSPF process/adjacency را با فرمان پشتیبانی‌شدهٔ Image بازآغاز کنید، سپس انتظار R2 به‌عنوان DR و R1 به‌عنوان BDR را بسنجید. بعد R3 را به 200 برگردانید و همان بازآغاز کنترل‌شده را تکرار کنید. `clear ip ospf process` می‌تواند همهٔ همسایگی‌ها را قطع کند؛ فقط در لاب ایزوله و با دسترسی Console به‌کار ببرید.

| مسئله | بررسی و تفسیر |
|---|---|
| R3 DR نشده | Interface Priority، Router ID، زمان انتخاب، Network Type و آیا فرایند پس از تغییر دوباره Election کرده را بررسی کنید |
| فقط R1/R2 در 2-WAY | برای دو DROther طبیعی است؛ `show ip ospf interface` را ببینید تا DR و BDR منتخب و همسایگی FULL با آن‌ها روشن باشد |
| Neighbor نمی‌شود | IP/Mask/Area، Hello/Dead، MTU/Authentication (اگر تنظیم شده)، وضعیت Interface و Subnet را تطبیق دهید |
| Cost مسیر متفاوت است | مجموع Costهای هر مسیر و Reference Bandwidth یکسان در همهٔ روترها را بررسی کنید؛ DR بودن Cost را تعیین نمی‌کند |

**معیار تحویل:** جدول نقش و Priority هر سه روتر، خروجی `show ip ospf interface` و `show ip ospf neighbor` برای هر طرف، پیش‌بینی درست نقش‌ها پس از نقص/بازیابی، و توضیح تفاوت Election DR از انتخاب مسیر بر مبنای Cost. هیچ خروجی واقعی در این درس ثبت نشده است.

## ۶. سؤال‌ها و پاسخ

1. **DR چیست؟** روتر منتخب برای Adjacency با بقیه در Broadcast.
2. **BDR چیست؟** پشتیبان DR.
3. **انتخابات بر چه اساسی است؟** Priority و سپس Router ID.
4. **Priority 0 یعنی چه؟** عدم شرکت در انتخابات.
5. **2-WAY بین دو روتر غیر DR/BDR طبیعی است؟** بله.
6. **Cost بر چه اساسی است؟** Bandwidth رابط.
7. **Bandwidth بیشتر چه Costی دارد؟** کمتر.
8. **Reference Bandwidth چیست؟** مبنای محاسبهٔ Cost.
9. **`ip ospf cost` چه می‌کند؟** Cost رابط را دستی تغییر می‌دهد.
10. **در Point-to-Point DR هست؟** خیر.
11. **اگر DR از کار بیفتد چه می‌شود؟** BDR به‌عنوان DR انتخاب می‌شود.
12. **آیا این سناریو اجرا شده است؟** خیر.

## واژه‌نامه و چک‌لیست

DR: روتر منتخب؛ BDR: پشتیبان؛ Priority: شانس انتخابات؛ Cost: هزینهٔ رابط؛ Reference Bandwidth: مبنای Cost.

- [ ] DR/BDR را فقط در Broadcast می‌بینم.
- [ ] Priority و Router ID را با هم بررسی می‌کنم.
- [ ] Cost را با Bandwidth هماهنگ می‌کنم.
