# CCNA NA-01 — VLAN، Broadcast Domain و VLAN چندسوئیچی

**سطح:** CCNA. **پیش‌نیاز:** NF-15 و IPv4 مقدماتی. **اهداف رسمی:** `2.1.a` پیکربندی و Verification دسترسی داده، `2.1.b` عضویت Default VLAN، `2.2.a–c` Trunk/802.1Q/Native VLAN. این هدف‌ها در طرح آموزشی شرح داده می‌شوند؛ تمرین اجرا نشده است. **وضعیت:** پیش‌نویس محتوایی؛ همهٔ فرمان‌ها، خروجی‌ها و کاربرگ طراحی‌شده و **اجرا‌نشده** هستند. مدل Switch، ایمیج و نسخهٔ IOS تعیین نشده‌اند.

## اهداف

1. توضیح دهید چرا VLAN ساخته می‌شود و Broadcast Domain چیست.
2. VLAN را روی **یک** سوییچ بسازید و Access Port را درست تخصیص دهید.
3. همان VLAN را روی **دو** سوییچ بسازید و با **Trunk** به هم وصل کنید.
4. تفاوت Access Port و Trunk را از نظر **Tag** بفهمید.
5. در `show vlan brief` و `show interfaces switchport` ببینید چه چیزی تأیید می‌شود و چه چیزی تأیید **نمی‌شود**.

## ۱. VLAN چه مسئله‌ای را حل می‌کند؟

در یک سوییچ لایهٔ ۲، پورت‌های عضو یک VLAN در همان Broadcast Domain هستند. جدول MAC بر اساس VLAN نگهداری می‌شود؛ یک VLAN می‌تواند چند Subnet داشته باشد، هرچند در طراحی مقدماتی معمولاً برای هر VLAN یک Subnet مستقل در نظر می‌گیریم. مرز لایهٔ ۲ را با طرح آدرس‌دهی IP یکی نگیرید.

مشکل: در یک سازمان، بخش مالی و بخش مهندسی نباید ترافیک لایهٔ ۲ یکدیگر را ببینند. اگر یک سوییچ فیزیکی داشته باشید، نمی‌توانید با کابل‌کشی دو شبکهٔ منطقی جدا بسازید بدون خرید دو سوییچ.

**راه‌حل:** VLAN — تقسیم **منطقی** یک سوییچ به چند Broadcast Domain مستقل.

| بدون VLAN | با VLAN |
|---|---|
| یک Broadcast Domain | چند Broadcast Domain |
| دامنهٔ یادگیری MAC همان VLAN | مدخل‌های MAC وابسته به VLAN؛ یک MAC می‌تواند در VLANهای متفاوت مدخل جدا داشته باشد |
| Subnet به طراحی IP بستگی دارد | معمولاً برای هر VLAN یک Subnet IP جدا برنامه‌ریزی می‌شود؛ خود VLAN آن را ایجاد نمی‌کند |
| سوییچ فیزیکی جدا لازم است | یک سوییچ، چند شبکهٔ منطقی |

**تشبیه و محدودیتش:** VLAN مثل تقسیم یک ساختمان اداری به طبقات با دسترسی مستقل است. کابل‌کشی (سوییچ) مشترک است ولی هر طبقه آسانسور (Broadcast Domain) خودش را دارد.

**محدودیت تشبیه:** در ساختمان، دیوار فیزیکی جلوی عبور را می‌گیرد. در VLAN، جداسازی **منطقی** است و در برابر خطای پیکربندی یا حملهٔ VLAN Hopping مقاومت ذاتی ندارد. VLAN به‌تنهایی **امنیت کامل** نیست؛ برای کنترل واقعی به ACL و طراحی لایهٔ ۳ نیاز دارید.

## ۲. Access Port و Trunk

دو نقش برای پورت سوییچ وجود دارد و تفاوتشان **در Tag** است:

| ویژگی | **Access Port** | **Trunk Port** |
|---|---|---|
| متصل به | کلاینت، سرور، چاپگر | سوییچ دیگر یا روتر |
| فریم ورودی | **بدون Tag**؛ Tag داخلی به VLAN پورت نسبت داده می‌شود | **با Tag**؛ VLAN از Tag خوانده می‌شود |
| فریم خروجی | **بدون Tag** | **با Tag** |
| تعداد VLAN | ۱ | چند VLAN |
| پروتکل استاندارد | — | **802.1Q** |

**نکتهٔ کلیدی:** فریم روی کابل Access **هیچ Tag ندارد**. سوییچ آن را به‌صورت داخلی به VLAN پورت اختصاص می‌دهد. فریم روی Trunk **Tag دارد** تا سوییچ مقابل بداند به کدام VLAN تعلق دارد.

### ساختار Tag در 802.1Q

سوییچ یک فیلد ۴ بایتی به فریم اضافه می‌کند:

| فیلد | طول | معنا |
|---|---|---|
| TPID | ۲ بایت | `0x8100` (نشانهٔ 802.1Q) |
| Priority (PCP) | ۳ بیت | CoS برای QoS |
| **DEI** | ۱ بیت | Drop Eligible |
| **VLAN ID** | ۱۲ بیت | فضای کدگذاری ۰–۴۰۹۵؛ مقدار ۰ برای Priority Tag و ۴۰۹۵ رزرو است؛ شناسه‌های قابل تخصیص معمولاً ۱–۴۰۹۴، با محدودیت پلتفرم |

۱۲ بیت ۴۰۹۶ مقدار کدگذاری می‌کند؛ این به معنی ۴۰۹۶ VLAN قابل تخصیص نیست: VID صفر برای Priority Tag و ۴۰۹۵ رزرو است. در بسیاری از IOSهای Catalyst، محدودهٔ معمول ۱–۱۰۰۵ و Extended برابر ۱۰۰۶–۴۰۹۴ است؛ پشتیبانی، VLANهای رزروشده و امکان ذخیره‌سازی به مدل و نسخه وابسته‌اند.

### Native VLAN — مفهوم مهم برای درک درست

در Trunkهای 802.1Q سیسکو، فریم بی‌برچسب معمولاً به Native VLAN نسبت داده می‌شود؛ جزئیات Tagging و تنظیم پیش‌فرض به پلتفرم وابسته است. مقدار پیش‌فرض در بسیاری از Catalystها VLAN 1 است.

**مغایرت Native VLAN:** اگر دو سر Trunk Native متفاوت داشته باشند، ترافیک بی‌برچسب می‌تواند در دو سمت به VLANهای متفاوت نسبت داده شود؛ این ناهم‌خوانی و ریسک نشت/اختلال است، اما به‌تنهایی اثبات وقوع حملهٔ VLAN Hopping نیست. روش‌های VLAN Hopping از جمله سوءاستفاده از مذاکرهٔ Trunk یا Double-tagging، مسئلهٔ جداگانه‌اند. مطابق طرح سازمانی، Native یکسان و در صورت پشتیبانی و سیاست محل، VLAN بلااستفاده/غیرپیش‌فرض انتخاب کنید؛ این اقدام جای محدودسازی Trunk و کنترل‌های امنیتی را نمی‌گیرد.

**هشدار:** Default VLAN (VLAN 1) و Native VLAN **مفهوم یکسانی نیستند**، حتی اگر پیش‌فرض یکی باشند. Default VLAN، VLAN پورت‌های تنظیم‌نشده است؛ Native VLAN، VLAN فریم‌های بدون Tag روی Trunk.

## ۳. توپولوژی کاربرگ

**PNETLab مستقل — طراحی‌شده و اجرا‌نشده.** دو سوییچ، دو VLAN، یک Trunk.

```text
   PC-A                    SW1                 SW2                    PC-B
192.0.2.10  ─ Gi0/1    [Gi0/1 · VLAN 10]  [Gi0/1 · VLAN 10]  ─ 192.0.2.11
               (access)                      (access)
                          Gi0/24 ═════════ Gi0/24
                            802.1Q trunk (10, 20, 999)
                          (trunk)         (trunk)
                                                                     PC-C
                                                              ─ 198.51.100.10
                                                                (VLAN 20, Gi0/2)
```

| دستگاه | Interface | نقش | VLAN | IPv4 | Gateway |
|---|---|---|---|---|---|
| PC-A | eth0 | Access | 10 | `192.0.2.10/24` | لازم نیست |
| PC-B | eth0 | Access | 10 | `192.0.2.11/24` | لازم نیست |
| PC-C | eth0 | Access | 20 | `198.51.100.10/24` | لازم نیست |
| SW1 | Gi0/1 | Access | 10 | — | — |
| SW1 | Gi0/3 | پیش‌فرضِ بدون تغییر (بررسی VLAN 1) | 1 | — | — |
| SW1 | Gi0/24 | Trunk | 10, 20, 999 | — | — |
| SW2 | Gi0/1 | Access | 10 | — | — |
| SW2 | Gi0/2 | Access | 20 | — | — |
| SW2 | Gi0/24 | Trunk | 10, 20, 999 | — | — |

**چه چیزی اثبات می‌شود:**

- PC-A → PC-B: **باید** کار کند (هم VLAN، هم Subnet، از Trunk عبور می‌کند).
- PC-A → PC-C: **نباید** کار کند (VLAN متفاوت، Subnet متفاوت، روتری وجود ندارد).

اگر PC-A → PC-B کار **نکند**، Trunk یکی از فرضیه‌هاست؛ VLAN/پورت، آدرس‌دهی، لینک، STP و فایروال Client هم باید بررسی شوند. اگر PC-A → PC-C کار **کند**، مسیر لایهٔ ۳ یا اتصال دیگری برخلاف توپولوژی وجود دارد؛ آن را با فرضیهٔ «همه در یک VLAN افتاده‌اند» یکی نگیرید و مسیر واقعی را بررسی کنید.

![نمودار قابل ویرایش VLAN و Trunk دو سوییچ؛ اجرا‌نشده](academy-images/na-01-vlan.svg)

**نکتهٔ مهم دربارهٔ شماره‌گذاری پورت:** این طرح نام‌های Gi0/1، Gi0/2 و Gi0/24 را فرض می‌کند؛ نام واقعی در ایمیج/مدل می‌تواند متفاوت باشد. پیش از اجرا، فرمان فهرست رابط‌های پشتیبانی‌شده را از راهنمای همان Image انتخاب کنید (برای نمونه `show interfaces status` یا در برخی پلتفرم‌ها `show ip interface brief`) و جدول اتصال را با آن تطبیق دهید؛ یک فرمان واحد برای همهٔ Images تضمین‌شده نیست.

## ۴. پیکربندی به ترتیب اجرا

**همهٔ فرمان‌ها اجرا‌نشده‌اند.**

### گام ۱ — ساخت VLAN روی هر دو سوییچ

```text
SW1> enable
SW1# configure terminal
SW1(config)# vlan 10
SW1(config-vlan)# name USERS
SW1(config-vlan)# exit
SW1(config)# vlan 20
SW1(config-vlan)# name SERVERS
SW1(config-vlan)# exit
SW1(config)# vlan 999
SW1(config-vlan)# name NATIVE-UNUSED
SW1(config-vlan)# exit
```

| فرمان | معنا |
|---|---|
| `vlan 10` | VLAN را **می‌سازد** (اگر نباشد) یا ویرایش می‌کند (اگر باشد) |
| `name USERS` | برچسب توضیحی؛ **روی Forwarding اثر ندارد** ولی خواندن Configuration را آسان می‌کند |

**دام مهم:** اگر `switchport access vlan 30` بزنید و VLAN 30 **وجود نداشته باشد**، سوییچ خطا نمی‌دهد ولی پورت **غیرفعال** می‌شود (`inactive`). در `show vlan brief` می‌بینید که پورت زیر هیچ VLAN نیست. این یکی از رایج‌ترین خطاهای مبتدی است.

همین سه VLAN را روی SW2 هم بسازید. `Gi0/3` روی SW1 در این لاب برای بررسی عضویت پیش‌فرض VLAN 1 **بدون اتصال Client و بدون پیکربندی صریح VLAN** باقی می‌ماند؛ روی Switch تازه‌تنظیم‌شده یا پس از بازنشانی کنترل‌شدهٔ رابط، فرمان `switchport access vlan 1` نزنید تا حالت پیش‌فرض را با تنظیم صریح اشتباه نگیرید. در محیط ایزوله، اگر رابط قبلاً پیکربندی شده است، فقط پس از بررسی اثر `default interface GigabitEthernet0/3` را به‌کار ببرید.

در نسخهٔ هدف عضویت را با `show vlan brief` و حالت پورت را با `show interfaces GigabitEthernet0/3 switchport` بررسی کنید؛ در بسیاری از Catalystها انتظار می‌رود Gi0/3 زیر VLAN 1 دیده شود و `Access Mode VLAN` مقدار پیش‌فرض 1 را نشان دهد. جزئیات حالت عملیاتی به مدل/نسخه وابسته است. VLAN 1 در این لاب حذف نمی‌شود؛ برای کاربران واقعی فقط مطابق طرح و سیاست از آن استفاده کنید. بدون ساخت VLANهای لازم روی هر دو Switch، عبور ترافیک آن‌ها مطابق انتظار نیست.

### گام ۲ — تنظیم Access Portها

```text
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# no shutdown
SW1(config-if)# exit
```

| فرمان | معنا |
|---|---|
| `switchport mode access` | پورت را صراحتاً Access می‌کند. `dynamic auto` در پلتفرم‌های پشتیبان مذاکره را آغاز نمی‌کند؛ دو سمت auto معمولاً Trunk نمی‌شوند، اما مذاکره با همسایهٔ `dynamic desirable`/Trunk می‌تواند رفتار را تغییر دهد |
| `switchport access vlan 10` | VLAN داده را تعیین می‌کند |
| `no shutdown` | پورت را از حالت Administratively Down خارج می‌کند |

**چرا `switchport mode access` صریح لازم است؟** حالت پیش‌فرض و پشتیبانی DTP به مدل/نسخه وابسته است؛ در بسیاری از Catalystهای IOS، `dynamic auto` درخواست مذاکره را آغاز نمی‌کند و دو پورت auto به‌تنهایی Trunk نمی‌شوند، ولی مذاکره با پورت `dynamic desirable` می‌تواند Trunk بسازد. برای پورت Endpoint آن را صریحاً Access کنید و هر روش غیرفعال‌کردن مذاکره را فقط طبق قابلیت و راهنمای نسخه به‌کار ببرید. این کار ریسک مذاکرهٔ ناخواسته را کم می‌کند؛ به‌تنهایی تضمین امنیت یا دسترسی به همهٔ VLANها نیست.

روی SW1، Gi0/1 به PC-A و VLAN 10 تعلق دارد؛ روی SW2، Gi0/1 به PC-B و VLAN 10 و Gi0/2 به PC-C و VLAN 20 تعلق دارند. تنظیم نمونهٔ SW2:

```text
SW2(config)# interface GigabitEthernet0/1
SW2(config-if)# switchport mode access
SW2(config-if)# switchport access vlan 10
SW2(config-if)# no shutdown
SW2(config-if)# exit
SW2(config)# interface GigabitEthernet0/2
SW2(config-if)# switchport mode access
SW2(config-if)# switchport access vlan 20
SW2(config-if)# no shutdown
```

در SW1 نیز Gi0/1 را به‌صورت Access در VLAN 10 تنظیم کنید؛ از تکرار بی‌دلیل پیکربندی پورت خودداری کنید.

### گام ۳ — تنظیم Trunk بین دو سوییچ

```text
SW1(config)# interface GigabitEthernet0/24
SW1(config-if)# switchport trunk encapsulation dot1q
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk native vlan 999
SW1(config-if)# no shutdown
SW1(config-if)# exit
```

| فرمان | معنا |
|---|---|
| `switchport trunk encapsulation dot1q` | فقط در پلتفرم‌هایی که چند Encapsulation پشتیبانی می‌کنند ممکن است لازم باشد. فرمان در دستگاه‌های 802.1Q-only وجود ندارد؛ نبود آن را خطا تلقی نکنید و دستورالعمل همان مدل را بررسی کنید. |
| `switchport mode trunk` | پورت را صراحتاً Trunk می‌کند |
| `switchport trunk native vlan 999` | Native VLAN را از 1 تغییر می‌دهد |

**نکتهٔ نسخه/مدل:** بعضی پلتفرم‌های چند-Encapsulation لازم دارند ابتدا 802.1Q صریح انتخاب شود؛ برخی پلتفرم‌های جدید فقط 802.1Q دارند و دستور `switchport trunk encapsulation` را نمی‌شناسند. نحو، خطا و پیش‌فرض را با مستندات و راهنمای Image مشخص‌شده بررسی کنید؛ از متن خطای نمونه به‌تنهایی نسخه را استنتاج نکنید.

همین را روی SW2 برای Gi0/24 تکرار کنید. **Native VLAN باید در دو طرف یکسان باشد.**

### گام ۴ — تعیین VLANهای مجاز روی Trunk

```text
SW1(config)# interface GigabitEthernet0/24
SW1(config-if)# switchport trunk allowed vlan 10,20,999
SW1(config-if)# end
```

همین allow-list را روی SW2 Gi0/24 نیز تنظیم و پس از آن روی هر دو سمت Verification کنید.

`switchport trunk allowed vlan 10,20,999` — فقط این VLANها مجازند. Native بودن به‌تنهایی VLAN را از محدودیت Allowed VLAN مستثنا نمی‌کند؛ VLAN 999 را هم در allow-list نگه دارید اگر باید روی این لینک فعال باشد.

**چرا محدود کردن مهم است؟** به‌طور پیش‌فرض **همه** VLANها روی Trunk مجاز هستند. اگر بعداً یک VLAN جدید بسازید که نباید به آن سوییچ برود، به‌طور خودکار می‌رود. محدودسازی صریح، سطح حمله را کم می‌کند.

**هشدار عملیاتی:** اگر `switchport trunk allowed vlan` را با لیست جدید بزنید (بدون `add`)، لیست قبلی **جایگزین** می‌شود. برای اضافه کردن: `switchport trunk allowed vlan add 30`. این تفاوت، منبع قطعی‌های واقعی است.

### گام ۵ — تنظیم IP کلاینت‌ها

```text
PC-A> ip 192.0.2.10/24
PC-B> ip 192.0.2.11/24
PC-C> ip 198.51.100.10/24
```

سینتکس VPCS است و باید با نسخهٔ PNETLab و نوع کلاینت تطبیق داده شود. در کلاینت‌های گرافیکی، از پنل تنظیمات IP استفاده کنید.

## ۵. Verification و تفسیر خروجی

**نمونهٔ طراحی‌شده، اجرا‌نشده.**

```text
SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/3
10   USERS                            active    Gi0/1
20   SERVERS                          active
999  NATIVE-UNUSED                    active
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
```

**خط‌به‌خط — این خروجی کمتر از آن‌چه فکر می‌کنید اثبات می‌کند:**

- `10 USERS active Gi0/1` — VLAN وجود دارد، فعال است و Gi0/1 **عضو** آن است. این تأیید می‌کند `switchport access vlan 10` اعمال شده.
- `20 SERVERS active` — VLAN وجود دارد ولی **هیچ پورتی** در آن نیست. این درست است: Trunk پورت Access نیست، پس در این لیست نمی‌آید.
- `999 NATIVE-UNUSED active` — وجود Native VLAN.
- **مهم:** Gi0/24 (Trunk) در **هیچ‌کدام** از این خطوط نمی‌آید، چون Access نیست. **نباید** انتظار داشته باشید Trunk را اینجا ببینید.
- `1002–1005 act/unsup` — VLANهای قدیمی FDDI/Token Ring. `unsup` یعنی پشتیبانی نمی‌شوند. این طبیعی است و خطا نیست.

**چه چیزی این خروجی اثبات نمی‌کند:** آیا Trunk کار می‌کند؟ آیا VLAN 20 از Trunk عبور می‌کند؟ برای این‌ها باید Trunk را جداگانه بررسی کنید.

```text
SW1# show interfaces GigabitEthernet0/1 switchport
Name: Gi0/1
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: Off
Access Mode VLAN: 10 (USERS)
Trunking Native Mode VLAN: 1 (default)
Voice VLAN: none
```

- `Administrative Mode: static access` — ما گفتیم Access. ✅
- `Operational Mode: static access` — در عمل هم Access است. ✅
- `Negotiation of Trunking: Off` — طرف مقابل نمی‌تواند پورت را Trunk کند. این اثر مستقیم `switchport mode access` است.
- `Access Mode VLAN: 10 (USERS)` — VLAN داده درست است.
- `Trunking Native Mode VLAN: 1 (default)` — روی Access Port معیار عملی Trunk نیست؛ این فیلد در خروجی بعضی نسخه‌ها مقدار پیش‌فرض را نشان می‌دهد. Native VLAN واقعی را روی پورت Trunk بررسی کنید.

```text
SW1# show interfaces GigabitEthernet0/24 switchport
Name: Gi0/24
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Negotiation of Trunking: On
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 999 (NATIVE-UNUSED)
Trunking VLANs Enabled: 10,20,999
```

- `Administrative Mode: trunk` و `Operational Mode: trunk` — **هر دو** باید `trunk` باشند. اگر وضعیت Operational مطابق طرح نیست، همسایه، لینک، VLANها و قابلیت/تنظیم پلتفرم را بررسی کنید؛ از این دو مقدار به‌تنهایی کابل را علت قطعی ندانید.
- `Trunking Native Mode VLAN: 999` — این سر Trunk مقدار 999 را گزارش می‌کند؛ مقدار سر مقابل را نیز جداگانه بررسی کنید. یکسان‌بودن دو سر شرط سازگاری طرح است.
- `Trunking VLANs Enabled: 10,20,999` — VLANهای مجاز. ✅

```text
SW1# show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/24      on               802.1q         trunking      999

Port        Vlans allowed on trunk
Gi0/24      10,20,999

Port        Vlans allowed and active in management domain
Gi0/24      10,20,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/24      10,20,999
```

**این خروجی سه ستون مهم دارد و باید هر سه تفاوت داده شوند:**

| ستون | معنا | چه زمانی خالی است |
|---|---|---|
| `Vlans allowed on trunk` | VLANهایی که **مجاز** هستند (`switchport trunk allowed vlan`) | اگر محدود نشده، `1-4094` |
| `Vlans allowed and active` | مجاز **و موجود** (`vlan` روی سوییچ ساخته شده) | اگر VLAN ساخته نشده باشد |
| `Vlans in forwarding state` | در حالت Forwarding در STP | اگر VLAN در STP Blocked باشد |

**یک خطای ممکن:** VLAN در ستون اول مجاز است ولی در ستون دوم فعال نیست؛ VLAN ممکن است روی آن سوییچ تعریف نشده یا در وضعیت قابل‌استفاده نباشد. اگر VLAN 20 روی SW2 ساخته نشده باشد، پورت PC-C و عبور ترافیک آن مطابق انتظار کار نمی‌کنند؛ وضعیت پورت و نسخه را جداگانه بررسی کنید.

**تست نهایی، انتظار طراحی:** از PC-A به PC-B ارتباط IP محلی باید ممکن باشد؛ پاسخ Ping واقعی به وضعیت Client، Firewall و پورت‌ها وابسته است. اگر شکست خورد:

1. `show interfaces trunk` را روی **هر دو** سوییچ بزنید و ستون دوم را مقایسه کنید.
2. مطمئن شوید Native VLAN دو طرف یکسان است.
3. مطمئن شوید Access Portها در VLAN درست هستند.

## ۶. عیب‌یابی

| نشانه | علت محتمل | بررسی | اصلاح |
|---|---|---|---|
| PC-A و PC-B ارتباط ندارند | Trunk در حالت `down` یا `static access` | `show interfaces trunk` روی هر دو | `switchport mode trunk` در دو طرف |
| PC-A و PC-B ارتباط ندارند | VLAN روی یک سوییچ ساخته نشده | ستون ۲ در `show interfaces trunk` | `vlan 10` روی هر دو |
| PC-A و PC-B ارتباط ندارند | Native VLAN متفاوت | `show interfaces switchport` | `switchport trunk native vlan` یکسان |
| PC-A و PC-B ارتباط ندارند | VLAN از Trunk مجاز نیست | ستون ۱ | `switchport trunk allowed vlan add 10` |
| پورت در `show vlan brief` نیست | پورت Trunk است | `show interfaces switchport` | طبیعی است |
| پورت `inactive` است | VLAN تخصیص‌یافته وجود ندارد | `show vlan brief` | `vlan ...` بسازید |
| PC-A → PC-C کار می‌کند | مسیر لایهٔ ۳، عضویت/VLAN اشتباه یا اتصال خارج از طرح | VLAN، IP/Gateway، Route و کابل‌کشی را بررسی کنید | مسیر واقعی را بیابید و تنظیم ناخواسته را اصلاح کنید |
| PC-A → PC-C کار نمی‌کند | VLAN و Subnet متفاوت، بدون Router | — | این رفتار **درست** است |
| CDP/LLDP همسایه را نمی‌بیند | کابل یا پورت اشتباه | `show cdp neighbors` | سیم‌کشی و پورت را بررسی کنید |
| مشکل پورت‌های متفاوت در PNETLab | نام Interface فرق دارد | فرمان فهرست رابط‌های پشتیبانی‌شده در Image هدف | شماره‌گذاری را تطبیق دهید |

**سناریوی نقص طراحی‌شده (اجرا نشده):** اگر VLAN 20 روی SW2 تعریف نشده باشد، پورت Gi0/2 تخصیص‌یافته به آن ممکن است در برخی IOSها `inactive` گزارش شود؛ این رفتار را برای همهٔ Imageها تضمین نکنید. PC-B در VLAN 10 ممکن است همچنان از Trunk کار کند، اما PC-C نه. تعریف VLAN و وضعیت واقعی پورت را با فرمان‌های نسخهٔ هدف بررسی کنید؛ اصلاح پیشنهادی در محیط آزمایش، تعریف VLAN 20 روی SW2 است.

## ۷. کاربرگ مستقل PNETLab

1. دو سوییچ لایهٔ ۲ و سه کلاینت بسازید و کابل‌کشی بخش ۳ را انجام دهید.
2. پیش از پیکربندی، روی هر سوییچ با فرمان فهرست رابط‌های پشتیبانی‌شده (برای نمونه `show interfaces status` یا در برخی پلتفرم‌ها `show ip interface brief`) شماره‌گذاری واقعی را ثبت کنید؛ سپس `show vlan brief` را بررسی کنید.
3. VLAN 10، 20 و 999 را روی هر دو سوییچ بسازید؛ `Gi0/3` روی SW1 را بدون پیکربندی VLAN نگه دارید.
4. پیش از تنظیم آن، `show vlan brief` و `show interfaces GigabitEthernet0/3 switchport` را ثبت کنید؛ در Image تازه‌تنظیم‌شده عضویت پیش‌فرض VLAN 1 را بررسی کنید. اگر رابط پیکربندی قبلی دارد، فقط در لاب ایزوله و پس از بررسی اثر آن را Reset کنید.
5. Access Portهای متصل به کلاینت‌ها را تنظیم کنید.
6. **بدون** Trunk، از PC-A به PC-B پینگ بزنید. باید شکست بخورد. این حالت پایه است.
7. روی هر دو سوییچ Trunk را با `switchport mode trunk` و `switchport trunk native vlan 999` تنظیم کنید؛ سپس روی هر دو `switchport trunk allowed vlan 10,20,999` را اعمال کنید.
8. از PC-A به PC-B پینگ بزنید. در طراحی، ارتباط باید برقرار شود؛ نتیجهٔ واقعی را ثبت کنید.
9. از PC-A به PC-C پینگ بزنید. باید شکست بخورد.
10. VLAN 20 را روی SW2 حذف کنید (`no vlan 20`) و ببینید PC-C قطع می‌شود. سپس بازگردانید.
11. در محیط آزمایشی، Native VLAN را در یک طرف متفاوت تنظیم کنید. دو خروجی و Logهای دو سوییچ را ثبت کنید؛ هشدار mismatch فقط در صورت پشتیبانی و فعال بودن مکانیزم گزارش‌دهی (برای نمونه CDP) انتظار می‌رود، نه در هر Image.
12. در لاب، allow-list را موقتاً به `10` محدود کنید و در صورت مجاز بودن اثر را بر PC-C مشاهده کنید.
13. allow-list را به `10,20,999` بازگردانید و Verification هر دو سمت را ثبت کنید؛ این تغییر در شبکهٔ عملیاتی انجام نمی‌شود.

### معیار موفقیت و بستهٔ شواهد

کاربرگ فقط وقتی از نظر طراحی موفق است که در همان Image/نسخهٔ ثبت‌شده: (الف) SW1 Gi0/3 بدون پیکربندی صریح همچنان عضو پیش‌فرض VLAN 1 گزارش شود؛ (ب) Access Portها و VLANهای 10/20 روی هر دو سوییچ مطابق جدول باشند؛ (پ) هر دو Trunk در دو سمت Operational/802.1Q با Native 999 و VLANهای 10,20,999 مجاز و فعال باشند؛ (ت) PC-A↔PC-B ارتباط مورد انتظار VLAN 10 را داشته باشد و PC-A↔PC-C بدون Router یا مسیر لایهٔ ۳ ارتباط نگیرد؛ و (ث) هر نقصِ انتخاب‌شده جداگانه ایجاد، با خروجی تشخیص و سپس اصلاح شده باشد. برای تحویل، Image/Release و نگاشت پورت واقعی، خروجی قبل/بعد `show vlan brief`, `show interfaces trunk`, `show ... switchport` و پیکربندی IP و آزمون‌های Client را با زمان اجرا ثبت کنید. شکست Ping به‌تنهایی علت را اثبات نمی‌کند؛ Host Firewall و وضعیت Client نیز در شاهد ذکر شوند.

هیچ‌کدام از این مراحل اجرا نشده و هیچ خروجی واقعی ثبت نشده است.

## ۸. سؤال‌ها و پاسخ

1. **VLAN چه چیزی را جدا می‌کند؟** Broadcast Domain در لایهٔ ۲. هر VLAN یک جدول MAC و یک محدودهٔ Broadcast مستقل دارد.

2. **برخلاف تصور رایج، VLAN امنیت کامل است؟** نه. VLAN جداسازی منطقی است و در برابر خطای پیکربندی یا VLAN Hopping مقاومت ندارد. برای کنترل نیاز به ACL و طراحی لایهٔ ۳ دارید.

3. **تفاوت Access و Trunk در Tag چیست؟** Access فریم بدون Tag می‌گیرد و می‌فرستد؛ Trunk فریم با Tag. تنها استثنا Native VLAN است که روی Trunk بدون Tag می‌رود.

4. **Native VLAN چیست؟** در رفتار معمول 802.1Q سیسکو، VLAN فریم‌های untagged روی Trunk است. تفاوت دو طرف می‌تواند فریم را در VLAN متفاوت قرار دهد و اختلال/ریسک بسازد، اما به‌تنهایی اثبات حملهٔ VLAN Hopping نیست.

5. **Default VLAN و Native VLAN یکی هستند؟** نه. Default VLAN (معمولاً 1) VLAN پورت‌های تنظیم‌نشده است؛ Native VLAN مفهوم Trunk است. پیش‌فرض یکی است ولی مفهومشان متفاوت است.

6. **`switchport mode access` چرا صریح لازم است؟** حالت پیش‌فرض به پلتفرم وابسته است؛ در بسیاری از Catalystها auto به‌تنهایی مذاکره را شروع نمی‌کند، اما با همسایهٔ desirable ممکن است Trunk بسازد. پورت Endpoint را صریحاً Access کنید.

7. **اگر `switchport access vlan 30` بزنید و VLAN 30 وجود نداشته باشد چه می‌شود؟** سوییچ خطا نمی‌دهد، ولی پورت `inactive` می‌شود و در `show vlan brief` دیده نمی‌شود.

8. **Trunk را در `show vlan brief` می‌بینید؟** نه. Trunk پورت Access نیست. برای دیدن آن `show interfaces trunk` بزنید.

9. **تفاوت «allowed» و «allowed and active» چیست؟** اولی VLANهای مجاز را نشان می‌دهد (تنظیم `allowed vlan`)؛ دومی آن‌هایی که هم مجاز و هم روی سوییچ **ساخته شده**اند. اگر VLAN ساخته نشود، در اولی هست ولی در دومی نیست.

10. **اگر `switchport trunk allowed vlan` را بدون `add` بزنید چه می‌شود؟** لیست قبلی **جایگزین** می‌شود، نه اضافه. برای اضافه کردن باید `add` بکار ببرید.

11. **PC-A و PC-C در VLANهای متفاوت‌اند. برای ارتباط چه لازم است؟** یک دستگاه لایهٔ ۳ (روتر یا SVI) با یک IP در هر VLAN. بدون آن، ارتباط ممکن نیست.

12. **چرا در PNETLab بعضی پورت‌ها وجود ندارند؟** نام Interface به ایمیج و مدل بستگی دارد. با `show ip interface brief` نام واقعی را پیدا کنید و پیکربندی را تطبیق دهید.

## واژه‌نامه و چک‌لیست

**VLAN**: تقسیم منطقی لایهٔ ۲؛ **Broadcast Domain**: محدودهٔ انتشار Broadcast؛ **Access Port**: پورت تک‌VLAN بدون Tag؛ **Trunk Port**: پورت چند‌VLAN با Tag؛ **802.1Q**: استاندارد Tag؛ **Native VLAN**: VLAN فریم بدون Tag روی Trunk؛ **Default VLAN**: VLAN پورت تنظیم‌نشده؛ **PVID**: VLAN پیش‌فرض پورت.

- [ ] `switchport mode access` را صریح تنظیم می‌کنم.
- [ ] Native VLAN را در دو طرف یکسان و غیر از 1 می‌گذارم.
- [ ] VLANها را روی **هر دو** سوییچ می‌سازم.
- [ ] Trunk را در `show interfaces trunk` بررسی می‌کنم، نه در `show vlan brief`.
- [ ] ارتباط بین VLANها را بدون L3 فرض نمی‌کنم.
- [ ] شماره‌گذاری پورت را قبل از پیکربندی با `show ip interface brief` تطبیق می‌دهم.
- [ ] کاربرگ و خروجی پیشنهادی را اجراشده نمی‌نامم.
