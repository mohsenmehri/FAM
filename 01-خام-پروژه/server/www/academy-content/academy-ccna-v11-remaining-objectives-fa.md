# ماتریس اهداف رسمی CCNA v1.1 — حوزه‌های ۲ تا ۶

**مبنا:** [سند رسمی Cisco CCNA 200-301 v1.1](https://learningcontent.cisco.com/documents/marketing/exam-topics/200-301-CCNA-v1.1.pdf)، بازبینی ۲۰۲۶-۱۱-۲۰. سند یک راهنمای عمومی است و امکان تغییر دارد. این فهرست تلخیص هدف‌ها است، نه متن کامل یا ممیزی نهایی. حوزهٔ ۱ در `academy-ccna-v11-network-fundamentals-plan-fa.md` ثبت شده است.

**وضعیت ردیف‌ها (به‌روزرسانی ۲۰۲۶-۱۱-۲۰):** هر ۶۳ ردیف این فایل به درس و بخش مشخص ارجاع دارند. هر ۳۹ هدف غیرعملی در سطح متن کافی ارزیابی شده‌اند: `2.5.a–d`، `2.6–2.9`، `3.1.a–g`، `3.2.a–c`، `3.5`، `4.3–4.5`، `4.7`، `4.9`، `5.1`، `5.2`، `5.4`، `5.5`، `5.8`، `5.9`، `6.1`، `6.2`، `6.3`، `6.3.a–b`، `6.4`، `6.5`، `6.6` و `6.7`. ۲۴ ردیف نهایی‌نشده در این فایل (و ۲۷ در کل حوزه‌های ۱–۶) همگی هدف عملی‌اند و هنوز روی IOS/PNETLab اجرا و تأیید نشده‌اند. برای هر ۲۷، کاربرگ/معیار قبولی مستقل و پیوند به فعالیت‌های ۴۲ بخش بدنه‌محور در [نقشهٔ تحویل](academy-ccna-practical-delivery-map-fa.md) آمده است؛ این سند نقشهٔ محتواست، نه تأیید پلتفرم یا اجرای دانشجو.

**تفکیک نوع ارزیابی بر اساس فعل رسمی (جدا از کفایت):** کل ماتریس ۹۸ ردیفی ۲۷ هدف نیازمند اعتبارسنجی عملی دارد (۲۵ `Configure and verify`، یک `Configure` و یک `Verify`) و ۷۱ هدف دیگر نیازمند بازبینی محتوایی/تحلیلی است. این سند حوزه‌های ۲ تا ۶ را در بر می‌گیرد: ۶۳ ردیف یکتا، شامل ۲۴ عملی و ۳۹ با فعل‌های دیگر؛ هر ۳۹ هدف غیرعملی در سطح متن کافی ارزیابی شده‌اند. هدف `2.1.b` نیز عملی است؛ هیچ هدف عملی از این دسته اجرا و تأیید نشده است. جست‌وجوی لفظیِ عبارت `باز /` در ستون وضعیت ۲۳ مورد را می‌یابد؛ ردیف `5.6` با عبارت «نیازمند اعتبارسنجی عملی» این زیررشته را ندارد، اما بر اساس فعل رسمی یک هدف عملیِ باز است و در شمار ۲۴ منظور می‌شود.


> **یادداشت نام‌گذاری (پس از ممیزی ۱۴۰۵/۰۸/۲۹):** نام فایل NA-01 از `academy-ccna-access-01-vlan-access-fa.md` به `academy-ccna-access-01-vlan-fa.md` تغییر کرد و نسخهٔ قدیمی (تک‌سوئیچی، بدون Trunk) حذف شد. هر ارجاع به نام قدیمی در این سند تاریخی است.

## 2 — Network Access

| کد | فعل رسمی | موضوع (تلخیص) | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 2.1.a | Configure and verify | VLAN access ports (data and voice) | NA-01 §۴–۶ داده؛ NA-03 §۳–۵ صوت | باز / نیازمند اعتبارسنجی عملی / کاربرگ‌های طراحی‌شده؛ تصویر Voice تعیین نشده / اجرا نشده |
| 2.1.b | Configure and verify | default VLAN | NA-01 §۳–۵: عضویت پورت Gi0/3 در VLAN پیش‌فرض 1 و Verification طراحی‌شده، بدون تنظیم صریح VLAN | باز / نیازمند اعتبارسنجی عملی / اجرا نشده |
| 2.1.c | Configure and verify | interVLAN connectivity | NA-04 §۲–۵: Router-on-a-Stick و Gateway | باز / نیازمند اعتبارسنجی عملی / کاربرگ VPCS و دو تجهیز پیشنهادی / اجرا نشده |
| 2.2.a | Configure and verify | trunk ports | NA-02 §۳–۶: Trunk دو سوئیچ و Verification | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 2.2.b | Configure and verify | 802.1Q | NA-02 §۲–۵: 802.1Q و VLANهای مجاز | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 2.2.c | Configure and verify | native VLAN | NA-02 §۲ و ۴–۶: Native VLAN 999 در دو سمت | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 2.3 | Configure and verify | Layer 2 discovery protocols: Cisco Discovery Protocol and LLDP | NA-05 §۳–۵: فعال‌سازی و Neighbor CDP/LLDP | باز / نیازمند اعتبارسنجی عملی / کاربرگ دو سوئیچ پیشنهادی / اجرا نشده |
| 2.4 | Configure and verify | Layer 2/Layer 3 EtherChannel (LACP) | NA-06 §۲–۴: LACP لایهٔ ۲ و ۳ و وضعیت گروه | باز / نیازمند اعتبارسنجی عملی / دو سناریوی مستقل پیشنهادی / اجرا نشده |
| 2.5.a | Interpret | Rapid PVST+: root port, root bridge (primary/secondary), and other port names | NA-07 §۲–۳، §۶–۷: Bridge ID، انتخاب Root، Primary/Secondary به‌عنوان نقش طراحی، Root/Designated/Alternate/Backup و تفسیر خروجی نمونه | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / خروجی و لاب نمونه‌اند، اجرا نشده |
| 2.5.b | Interpret | Rapid PVST+: port states and roles | NA-07 §۳–۴، §۷: نقش‌های Root/Designated/Alternate/Backup و حالت‌های RSTPِ Discarding/Learning/Forwarding، تطبیق با خروجی | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / خروجی نمونه، اجرا نشده |
| 2.5.c | Interpret | Rapid PVST+: PortFast | NA-07 §۴، §۸–۹ و §۱۱: Edge Port، کاربرد روی Endpoint، خطر لینک Switch-to-Switch، BPDU و تفاوت با STP-off | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / پیکربندی/رفتار اجرا نشده |
| 2.5.d | Interpret | Rapid PVST+: root guard, loop guard, BPDU filter, BPDU guard | NA-07 §۸–۹ و §۱۱: Trigger، حالت Root/Loop-Inconsistent یا Err-Disable، دامنه/ریسک BPDU Filter و عیب‌یابی چهار محافظت | **کافی در سطح متن تفسیری (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / پیکربندی/رفتار اجرا نشده |
| 2.6 | Describe | Cisco Wireless Architectures and AP modes | NA-08 §۱: Autonomous/Cloud/Split-MAC و نقش/مرز Local، FlexConnect، Monitor، Sniffer، Rogue Detector، Bridge/Mesh و SE-Connect | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ WLC/AP اجرا نشده |
| 2.7 | Describe | physical infrastructure connections of WLAN components (AP, WLC, access/trunk ports, and LAG) | NA-08 §۲–۳: AP/WLC، Access/Trunk، Central/Local Switching، VLAN Mapping و LAG؛ محدودیت مدل/نسخه | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ اتصال واقعی آزمایش نشده |
| 2.8 | Describe | network device management access (Telnet, SSH, HTTP, HTTPS, console, TACACS+/RADIUS, cloud managed) | NA-09 §۱–۴ و §۸: Transport، رمزنگاری، پیش‌نیاز SSH، Console، AAA و Cloud Managed | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ IOS/Cloud اجرا نشده |
| 2.9 | Interpret | wireless LAN GUI configuration: WLAN creation, security settings, QoS profiles, advanced settings | NA-09 §۵–۶: Profile/SSID، Security، VLAN Mapping، QoS و Advanced؛ فرم صرفاً مفهومی و فیلدها نسخه‌وابسته‌اند | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ GUI واقعی آزمایش نشده |

## 3 — IP Connectivity

| کد | فعل رسمی | موضوع (تلخیص) | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 3.1.a | Interpret | routing protocol code | IC-01 §۱–۲ و §۷: کدهای `L`/`C`/`S`/`O`/`D`/`B`/`R` و تفسیر منبع Route در نمونهٔ جدول | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / خروجی‌ها نمونه‌اند؛ IOS اجرا نشده |
| 3.1.b | Interpret | prefix | IC-01 §۲ و §۷: Prefix شبکه در برابر طول/Mask، با نمونهٔ `/16` و `/24` | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.c | Interpret | network mask | IC-01 §۲ و §۷: Network Mask و Prefix Length و اثر آن بر محدودهٔ شبکه | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.d | Interpret | next hop | IC-01 §۲، §۷–۸: Next Hop، Interface خروجی و Resolve بازگشتی؛ فرمان‌های بررسی مسیر/Next Hop | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / فرمان‌ها نمونه، IOS اجرا نشده |
| 3.1.e | Interpret | administrative distance | IC-01 §۳، §۵A، §۷ و §۱۰: جدول AD و مقایسهٔ آن میان Routeهای کاندیدِ همان Prefix | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.f | Interpret | metric | IC-01 §۴–۵A و §۱۰: معنای Metric در OSPF/EIGRP/RIP و مقایسه فقط درون همان Protocol و Prefix | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.1.g | Interpret | gateway of last resort | IC-01 §۶–۷: Default Route، Gateway of Last Resort و وابستگی نمایش به نصب/Resolve مسیر | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / خروجی نمونه، اجرا نشده |
| 3.2.a | Determine | longest prefix match | IC-01 §۵B، §۷ و §۱۰: LPM میان Routeهای نصب‌شده؛ مثال `/24` از RIP در برابر `/16` از OSPF | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.2.b | Determine | administrative distance | IC-01 §۳، §۵A و §۱۰: AD میان منابع مسیر با Prefix یکسان؛ از LPM میان Prefixهای متفاوت جدا شده | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.2.c | Determine | routing protocol metric | IC-01 §۴–۵A و §۱۰: Metric کمتر درون یک Protocol برای Prefix یکسان؛ Metric پروتکل‌های مختلف قابل قیاس نیست | **کافی در سطح متن (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 3.3.a | Configure and verify | IPv4 and IPv6 static default route | IC-02 بخش ۴، گام‌های ۳ و ۵: Default؛ بالادست فقط فرضی و اجرا‌نشده | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.3.b | Configure and verify | IPv4 and IPv6 static network route | IC-02 بخش ۴، گام‌های ۲ و ۵: Network Route و مسیر برگشت | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.3.c | Configure and verify | IPv4 and IPv6 static host route | IC-02 بخش ۴، گام‌های ۴ و ۵: Host Route؛ IPv6 خروجی نمونه نیز تکمیل شد | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.3.d | Configure and verify | IPv4 and IPv6 floating static route | IC-02 بخش ۴، گام ۶: Next Hop واقعی در توپولوژی افزوده‌شده، مسیر برگشت و AD مشروط | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.4.a | Configure and verify | single-area OSPFv2 neighbor adjacencies | IC-03 §۱–۴: Hello تا Adjacency و `show ip ospf neighbor` | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.4.b | Configure and verify | single-area OSPFv2 point-to-point | IC-03 §۲–۴: لینک `/30` بدون DR/BDR | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.4.c | Configure and verify | single-area OSPFv2 broadcast (DR/BDR selection) | IC-04 §۱–۳: Priority، انتخابات و `FULL/DR` | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.4.d | Configure and verify | single-area OSPFv2 router ID | IC-03 §۱ و IC-04 §۲: Router ID دستی و یکتا | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 3.5 | Describe | purpose, functions and concepts of first hop redundancy protocols | IC-06 §۱–۴ و §۶: هدف FHRP، Virtual Gateway، HSRP Active/Standby، GLBP AVG/AVF و Load Balancing، VRRP و مرزهای Tracking/Preempt/Failover | **کافی در سطح متن توصیفی (ممیزی جامع ۲۰۲۶-۱۱-۲۰)** / فرمان‌ها و Failover نمونه‌اند؛ اجرا نشده |

## 4 — IP Services

| کد | فعل رسمی | موضوع (تلخیص) | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 4.1 | Configure and verify | inside source NAT using static and pools | IS-01 §۱–۵: Static، Pool و PAT؛ ACL انتخاب‌گر NAT در §۳ از ACL فیلتر روی Interface تفکیک شد؛ `deny` به‌خودی‌خود Packet را Drop نمی‌کند | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 4.2 | Configure and verify | NTP operating in client and server mode | IS-02 §۱–۴: `ntp master`، `ntp server` و Stratum | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 4.3 | Explain | role of DHCP and DNS within the network | IS-03 §۱–۶: DORA/Lease/Options، Relay، Resolver/Cache/TTL، A/AAAA/CNAME/MX/PTR و تفکیک خطا؛ RFC 2131/2132/1034/1035 | **کافی در سطح Objective توضیحی (۲۰۲۶-۱۱-۲۰)** / DHCP/DNS واقعی اجرا نشده |
| 4.4 | Explain | function of SNMP in network operations | IS-04 §۱–۵: Manager/Agent/MIB/OID، GET/GETNEXT/GETBULK/SET/Response، Poll/Trap/Inform، نسخه/امنیت، پورت‌ها؛ RFC 3411/3414/3416 | **کافی در سطح Objective توضیحی (۲۰۲۶-۱۱-۲۰)** / IOS/NMS واقعی اجرا نشده |
| 4.5 | Describe | syslog features, including facilities and severity levels | IS-05 §۱–۵: Facility/PRI و Severity، سطوح 0–7، Threshold، مقصد/Buffer/Collector/زمان و محدودیت UDP؛ RFC 5424/5426 | **کافی در سطح Objective توصیفی (۲۰۲۶-۱۱-۲۰)** / IOS/Collector واقعی اجرا نشده |
| 4.6 | Configure and verify | DHCP client and relay | IS-06 §۱–۴: `ip address dhcp`، `ip helper-address` و Lease | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 4.7 | Explain | QoS forwarding per-hop behavior: classification, marking, queuing, congestion, policing and shaping | IS-07 §۱–۹ + [کاربرگ QoS](academy-ccna-services-07-qos-lab-fa.md): PHB، Classification/Marking، QoS Policy، Verification/Fault؛ RFC 2474/2475/3246 | **کافی در سطح متن؛ طرح عملی مستقل کامل؛ IOS XE/Traffic اجرا نشده** |
| 4.8 | Configure | network devices for remote access using SSH | IS-08 §۱–۴ (بازبینی هدفمند طرح پیکربندی/Verification این نوبت): RSA، کاربر محلی و `transport input ssh` | باز / نیازمند اعتبارسنجی عملی روی IOS واقعی / کاربرگ پیشنهادی / اجرا نشده |
| 4.9 | Describe | capabilities and functions of TFTP/FTP | IS-09 §۱–۶: TFTP/UDP 69 و TID، FTP Control/Data Active/Passive، احراز/رمزنگاری، FTPS/SCP/SFTP، Backup/Hash/خطر Merge؛ RFC 1350/959/2577/4217 | **کافی در سطح Objective توصیفی (۲۰۲۶-۱۱-۲۰)** / Server/IOS و انتقال لاب اجرا نشده |

## 5 — Security Fundamentals

| کد | فعل رسمی | موضوع (تلخیص) | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 5.1 | Define | threats, vulnerabilities, exploits, mitigation techniques | SEC-01 §۱–۲، §۴ و §۷: تفکیک چهار مفهوم، مثال‌های تهدید/کاهش و جداسازی وجود ضعف از اثبات Exploit | **کافی در سطح متن تعریفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اسکن یا حملهٔ واقعی انجام نشده |
| 5.2 | Describe | user awareness, training, physical access control | SEC-02 §۱–۲، §۴ و §۷: اجزای برنامهٔ Awareness/آموزش و سنجش؛ کنترل‌های مانع/ورود/نظارت و حدود آن‌ها | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / اجرا نشده |
| 5.3 | Configure and verify | device access control using local passwords | SEC-03 §۱–۴: Console، VTY و `enable secret` | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 5.4 | Describe | password management, complexity, alternatives: multifactor authentication, certificates, biometrics | SEC-04 §۱–۴ و §۶–۷: سیاست/طول/پیچیدگی، عوامل و MFA، گواهی و بیومتریک با مزایا و محدودیت‌ها | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / سرویس واقعی نصب نشده |
| 5.5 | Describe | IPsec remote access and site-to-site VPNs | SEC-05 §۱–۲ و §۵–۶: مقایسهٔ دو کاربرد IPsec، AH/ESP، IKE/SA، Modeها، Split/Full Tunnel و مرزهای Verification | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / تونل واقعی برقرار نشده |
| 5.6 | Configure and verify | access control lists | SEC-06 §۱–۱۱: Standard/Extended، Wildcard، ترتیب/جهت، DNS، Counter و ویرایش ACL | متن/طرح بازبینی شد؛ **نیازمند اعتبارسنجی عملی** / IOS اجرا نشده |
| 5.7 | Configure and verify | Layer 2 security: DHCP snooping, dynamic ARP inspection, port security | SEC-07 §۱–۴: Trusted/Untrusted، Binding و Violation Mode | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |
| 5.8 | Compare | authentication, authorization, accounting concepts | SEC-08 §۱–۵ و §۱۰: تمایز سه A، AAA محلی/متمرکز، RADIUS/TACACS+ و رفتار Method List/Fallback | **کافی در سطح متن مقایسه‌ای (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / AAA Server اجرا نشده |
| 5.9 | Describe | wireless security protocols WPA, WPA2, WPA3 | SEC-09 §۱، §۳ و §۵: WPA/WPA2/WPA3 Personal/Enterprise، TKIP/CCMP/SAE/PMF و محدودیت‌های WPS/SSID پنهان | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / AP/WLC اجرا نشده |
| 5.10 | Configure and verify | WLAN within GUI using WPA2 PSK | SEC-10 §۱–۵: مراحل GUI و PSK | باز / نیازمند اعتبارسنجی عملی / کاربرگ پیشنهادی / اجرا نشده |

## 6 — Automation and Programmability

| کد | فعل رسمی | موضوع (تلخیص) | درس، بخش و شاهد | کفایت / نوع ارزیابی / کاربرگ / اجرا |
|---|---|---|---|---|
| 6.1 | Explain | automation impacts on network management | AUT-01 §۱–۴ و §۶–۷: مقیاس/تکرارپذیری و Drift، نقش Source of Truth/Template/Orchestration، Idempotency، Pre/Post-check و Blast Radius؛ اعداد صرفاً فرض آموزشی‌اند | **کافی در سطح متن توضیحی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / ابزار اجرا یا اندازه‌گیری نشده |
| 6.2 | Compare | traditional networks with controller-based networking | AUT-02 §۱–۵ و §۸–۹: مقایسه، Abstraction/Effect of Programming و Fail Mode؛ اثر دامنه و محدودیت‌ها | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ Controller اجرا نشده |
| 6.3 | Describe | controller-based, software defined architecture: overlay, underlay, fabric | AUT-02 §۱–۵ و §۸–۹ + [کاربرگ AUT-03](academy-ccna-automation-03-sdn-fabric-lab-fa.md): Controller/Control/Data Plane، Underlay/Overlay/VXLAN/MTU | **کافی در سطح متن؛ Underlay Linux آزموده شد، VXLAN Kernel unsupported و Controller/Fabric اجرا نشده** |
| 6.3.a | Describe | separation of control plane and data plane | AUT-04 §۱–۶: نقش‌ها، تفکیک درون‌دستگاهی، Fail Mode، In-band و محدودیت‌های محصول | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ IOS/Controller اجرا نشده |
| 6.3.b | Describe | northbound and southbound APIs | AUT-05 §۱–۶: جهت از دید Controller، REST/NETCONF/RESTCONF/YANG، Endpoint و Capability وابسته به محصول | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ API واقعی فراخوانی نشده |
| 6.4 | Explain | AI (generative and predictive) and machine learning in network operations | AUT-06 §۱–۷ و §۹: AI/ML، Generative/Predictive، الگوهای یادگیری، کاربرد شبکه، کیفیت/Drift داده، معیارها و Explainability | **کافی در سطح متن توضیحی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / مدل یا دادهٔ واقعی استفاده نشده |
| 6.5 | Describe | REST-based API characteristics: authentication types, CRUD, HTTP verbs, data encoding | AUT-07 §۱–۵ و §۸: قیود REST، Auth Basic/Bearer/API Key/OAuth، CRUD و semantics افعال HTTP، Status Codes و JSON/XML/YAML/URL encoding | **کافی در سطح متن توصیفی (بازبینی هدفمند ۲۰۲۶-۱۱-۲۰)** / API واقعی فراخوانی نشده |
| 6.6 | Recognize | capabilities of configuration management mechanisms such as Ansible and Terraform | AUT-08 §۱–۷: Ansible Module/Idempotency، Terraform State/Plan/Drift و مالکیت Resource در ترکیب ابزارها | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ هیچ ابزاری اجرا نشده |
| 6.7 | Recognize | components of JSON-encoded data | AUT-09 §۱–۷: شش نوع مقدار JSON، JSONPath، `null`/کلید غایب و Parsing دفاعی | **کافی در سطح متن (بازبینی ۲۰۲۶-۱۱-۲۰)**؛ API اجرا/Parse نشده |

**کلید فایل‌ها:** NA-01 `academy-ccna-access-01-vlan-access-fa.md`؛ NA-02 `academy-ccna-access-02-trunk-8021q-fa.md`؛ NA-03 `academy-ccna-access-03-voice-vlan-fa.md`؛ NA-04 `academy-ccna-access-04-intervlan-router-stick-fa.md`. این شاهدها به معنی پوشش کامل یا تأیید کیفیت نیستند.

**کلید تکمیلی:** NA-05 `academy-ccna-access-05-cdp-lldp-fa.md`؛ NA-06 `academy-ccna-access-06-lacp-etherchannel-fa.md`. اجرای واقعی و کفایت نهایی هنوز بررسی نشده است.

**کلید تکمیلی:** NA-07 `academy-ccna-access-07-rapid-pvst-fa.md`؛ NA-08 `academy-ccna-access-08-wireless-architecture-fa.md`؛ NA-09 `academy-ccna-access-09-management-gui-fa.md`. همه پیش‌نویس و اجرا‌نشده‌اند.

**کلید تکمیلی:** IC-01 `academy-ccna-connectivity-01-routing-table-fa.md`؛ IC-02 `academy-ccna-connectivity-02-static-routing-fa.md`. همه پیش‌نویس و اجرا‌نشده‌اند.

**کلید تکمیلی:** SEC-01 `academy-ccna-security-01-threats-fa.md`؛ SEC-02 `academy-ccna-security-02-awareness-physical-fa.md`؛ SEC-03 `academy-ccna-security-03-local-passwords-fa.md`؛ SEC-04 `academy-ccna-security-04-password-management-mfa-fa.md`؛ SEC-05 `academy-ccna-security-05-ipsec-vpn-fa.md`؛ SEC-06 `academy-ccna-security-06-acl-fa.md`؛ SEC-07 `academy-ccna-security-07-layer2-security-fa.md`؛ SEC-08 `academy-ccna-security-08-aaa-fa.md`؛ SEC-09 `academy-ccna-security-09-wireless-security-fa.md`؛ SEC-10 `academy-ccna-security-10-wlan-gui-wpa2-fa.md`. همه پیش‌نویس و اجرا‌نشده‌اند.

**کلید تکمیلی:** AUT-01 `academy-ccna-automation-01-automation-impact-fa.md`؛ AUT-02 `academy-ccna-automation-02-traditional-vs-controller-fa.md`؛ AUT-03 `academy-ccna-automation-03-sdn-fabric-fa.md`؛ AUT-04 `academy-ccna-automation-04-control-data-plane-fa.md`؛ AUT-05 `academy-ccna-automation-05-apis-fa.md`؛ AUT-06 `academy-ccna-automation-06-ai-ml-fa.md`؛ AUT-07 `academy-ccna-automation-07-rest-api-fa.md`؛ AUT-08 `academy-ccna-automation-08-config-management-fa.md`؛ AUT-09 `academy-ccna-automation-09-json-fa.md`. همه پیش‌نویس و اجرا‌نشده‌اند.
