# نقشهٔ تحویل تمرین‌های CCNA v1.1 — ۲۷ هدف عملی، ۴۲ بخش بدنه‌محور، ۵۹ درس

**تاریخ بازبینی:** ۲۰۲۶-۱۱-۲۰ · **شاخه:** `arena/0085ab04-fam` · **مبنای اهداف:** Cisco CCNA 200-301 v1.1.

این سند سه چیز را جدا می‌کند: (۱) درس مفهومی و فعالیت تحلیلی، (۲) کاربرگ طراحی‌شده برای هدف عملی و معیار قبولی همان Objective، (۳) Verification واقعی روی Image/نسخهٔ ثبت‌شده. برای هر ۲۷ هدف عملی، پیوندِ کاربرگ/مرحله و معیار قبولی مستقل مشخص شده و فعالیت‌های مشترک به معیارهای جدا شکسته شده‌اند. ۴۲ بخش خامی که در اسکن بدنه‌محور پیدا شدند نیز ردیف‌به‌ردیف طبقه‌بندی شده‌اند؛ این ۴۲ مورد معادل ۴۲ کاربرگ مستقل نیستند.

## وضعیت ادعاها

- **۲۷/۲۷ هدف عملی** به یک کاربرگ موجود و معیار قبولی Objectiveمحور نگاشت شده‌اند؛ بسیاری از فایل‌ها یک کاربرگ مشترک برای چند Objective دارند و جدول اول دقیقاً می‌گوید هر هدف کدام مرحله و آزمون را جداگانه باید بگذراند.
- کاربرگ‌های Cisco/PNETLab در این مخزن **طراحی‌شده‌اند، نه روی IOS/PNETLab اجراشده**؛ مدل/نسخه/Feature set برای اکثر Imageها موجود نیست. «معیار قبولی طراحی‌شده» را با تأیید پلتفرمی یکی نگیرید.
- آزمون محلی جدید این نوبت برای AUT-03 فقط Underlay مبتنی بر Linux network namespace را اجرا کرد: دوطرفه `2/2` Ping؛ Kernel VXLAN را با `Error: Unknown device type.` نپذیرفت. پس هیچ Overlay/Fabric/Controller تأیید نشده است. وضعیت جزئی در [کاربرگ AUT-03](academy-ccna-automation-03-sdn-fabric-lab-fa.md) ثبت شده.
- در IS-07 یک کاربرگ QoS مستقل شامل توپولوژی، IP، Marking، صف/Shape، Verification، Fault و معیار شاهد تهیه شد؛ IOS XE/PNETLab/`iperf3` برای آن **اجرا نشده‌اند**: [کاربرگ IS-07](academy-ccna-services-07-qos-lab-fa.md).
- هیچ IOS/WLC/PNETLab/Controller/API/AAA Server واقعی در دسترس یا آزمایش‌شده نیست. آزمایش Linux Underlay تنها اجرای واقعی ثبت‌شده در این بسته است.

## ۱. نگاشت Objective به کاربرگ و معیار قبولی مستقل

| Objective رسمی | کاربرگ/درس (پیوند) | مرحله/آزمون ویژهٔ همان Objective | معیار قبولی مستقل |
|---|---|---|---|
| **1.6** IPv4 addressing/subnetting — Configure and verify | [NF-10](academy-ccna-fundamentals-10-ipv4-subnet-lab-fa.md) | Parent `/26` را به دو `/27` تقسیم؛ آدرس Router/Clientها و دو LAN را جدا تنظیم؛ Subnet fault کنترل‌شده را روی Client آزمایشی وارد و برگردانید. | هر چهار آدرس Host/Gateway در Subnet درست باشند؛ هر دو Connected Route و Mask/Prefix با طرح تطبیق کنند؛ Pingهای Gateway و بین دو LAN ثبت شوند؛ خطای Prefix کشف و بازیابی شود. IOS واقعی هنوز تأیید نشده است. |
| **1.8** IPv6 addressing/prefix — Configure and verify | [NF-12](academy-ccna-fundamentals-12-ipv6-interface-lab-fa.md) | دو Router و لینک `/64` مستنداتی؛ آدرس Global/Link-Local و Route متصل را بررسی؛ Prefix نامنطبق را فقط روی یک سمت وارد و اصلاح کنید. | Global Prefix دو سمت دقیقاً برابر و Route/Ping دوطرفهٔ Global پس از تنظیم درست باشد؛ Link-Local با Global اشتباه نشود؛ نقص Prefix و بازگردانی با شاهد ثبت شود. |
| **1.10** Client IP parameters — Verify | [NF-13](academy-ccna-fundamentals-13-client-ip-parameters-fa.md) | روی Windows، macOS و Linux، OS/نسخه و رابط واقعی را جداگانه شناسایی؛ آدرس/Prefix، مسیر Default و Resolver را بخوانید؛ Gateway غلط را فقط در Client ایزوله بیازمایید. | برای هر سه OS، فرمان و خروجی پاک‌سازی‌شده ثبت شود؛ IP/Mask/Gateway/DNS با طرح مقایسه و پس از Fault/Restore دوباره Verify شوند. VPCS جایگزین این سه OS نیست؛ این Sandbox فقط Linux دارد. |
| **2.1.a** Data/Voice VLAN access | [NA-01](academy-ccna-access-01-vlan-fa.md) + [NA-03](academy-ccna-access-03-voice-vlan-fa.md) | NA-01: Access Port داده و VLAN آن؛ NA-03: Voice VLAN روی پورت تلفن+PC، فقط با Switch/Phone سازگار. دو مسیر جدا هستند. | در آزمون داده، Access VLAN/Client درست باشد؛ در آزمون Voice، Data/Voice VLAN و رفتار LLDP/CDP/Phone فقط در صورت وجود دستگاه واقعی بررسی شود. نبود PoE/Phone/Image به‌عنوان «اجرای Voice» گزارش نشود. |
| **2.1.b** Default VLAN — Configure and verify | [NA-01](academy-ccna-access-01-vlan-fa.md) | Switch را در حالت پایه بررسی کنید؛ عضویت پورت Default VLAN را **بدون** تنظیم صریح Access VLAN ثبت کنید. | `show vlan brief` و وضعیت Switchport نشان دهند رابط آزمایشی عضو Default VLAN مورد انتظار همان Image است؛ Config نباید دستور ساختگی/صریحی را به‌عنوان «Default بودن» جا بزند. |
| **2.1.c** Inter-VLAN connectivity | [NA-04](academy-ccna-access-04-intervlan-router-stick-fa.md) | دو VLAN، Trunk و Router-on-a-Stick؛ Gateway هر Subnet و ارتباط بین Clientها را Verify؛ Tag زیررابط را موقتاً خراب و Restore کنید. | VLANها/Trunk/زیررابط‌ها مطابق طرح باشند؛ هر Client Gateway و سپس Client دیگر را ببیند؛ Fault 802.1Q محل‌یابی و پس از اصلاح دوباره آزموده شود. |
| **2.2.a** Trunk ports | [NA-02](academy-ccna-access-02-trunk-8021q-fa.md) | Trunk دو سمت را صریحاً تنظیم؛ هر دو سر و VLANهای مجاز/فعال را بررسی کنید. | دو پورت Operational Trunk و Allowed/Active VLANها مطابق فهرست باشند؛ عبور هر VLAN با Client/Traffic Test جدا از فقط `show` ثابت شود. |
| **2.2.b** 802.1Q | [NA-02](academy-ccna-access-02-trunk-8021q-fa.md) | Encapsulation/Tagging را برای Image هدف بررسی؛ ارتباط VLAN روی Trunk را با Switchport و تست End-to-End بسنجید. | دو سمت 802.1Q سازگار داشته باشند و Clientهای VLANهای برنامه‌ریزی‌شده از لینک عبور کنند؛ دستور Encapsulation اختیاری/ناموجود روی مدل‌های فقط-dot1q تحمیل نشود. |
| **2.2.c** Native VLAN | [NA-02](academy-ccna-access-02-trunk-8021q-fa.md) | Native VLAN `999` را دوطرفه تنظیم؛ Mismatch کنترل‌شده را فقط در Lab ایجاد و سپس Restore کنید. | Native VLAN دو سر یکسان/تعریف‌شده باشد؛ فرمان‌های Trunk/Log/Packet behaviorِ Image ثبت شود؛ Mismatch و بازیابی مستند شوند. |
| **2.3** CDP and LLDP | [NA-05](academy-ccna-access-05-cdp-lldp-fa.md) | دو Switch، یک لینک؛ CDP و LLDP را جداگانه فعال/غیرفعال و Neighbor سمت هر دو دستگاه را ببینید؛ آزمون Receive یک‌طرفه انجام دهید. | هر پروتکل جدا در هر دو جهت Neighbor صحیح نشان دهد؛ Fault یک‌طرفه با تفاوت Receive/Transmit تشخیص و Restore شود؛ به IP نیاز نیست. |
| **2.4** L2/L3 EtherChannel with LACP | [NA-06](academy-ccna-access-06-lacp-etherchannel-fa.md) | کاربرگ A: دو عضو Trunk/L2؛ کاربرگ B: دو Routed member/L3؛ `active/passive` را از `passive/passive` جدا بیازمایید. | LACP/عضوهای Bundled و Port-channel را روی دو سمت Verify؛ ترافیک VLAN یا Ping لایهٔ ۳ را پس از تشکیل بسنجید؛ خرابی عضو/عدم تشکیل و بازیابی ثبت شود. ادغام L2/L3 در یک توپولوژی واحد منظور نیست. |
| **3.3.a** IPv4/IPv6 static default route | [IC-02](academy-ccna-connectivity-02-static-routing-fa.md) | در توپولوژی دو/سه‌Router، Default Route هر دو Family را جدا نصب و مسیر واقعیِ Next Hop/برگشت را بررسی کنید. | `show ip route` و `show ipv6 route` مسیر Default نصب‌شده/Resolve‌شده را نشان دهند و مقصدهای خارج از Subnet از مسیر مورد انتظار برسند؛ صرف وجود خط در Config کافی نیست. |
| **3.3.b** IPv4/IPv6 static network route | [IC-02](academy-ccna-connectivity-02-static-routing-fa.md) | Route شبکهٔ Remote را برای IPv4 و IPv6 نصب؛ مسیر برگشت و Longest Prefix را بررسی کنید. | Prefix/Next Hop/Interface، Route نصب‌شده و دسترسی مقصد Remote در هر دو Family با جدول آدرس هم‌خوان باشد. |
| **3.3.c** IPv4/IPv6 static host route | [IC-02](academy-ccna-connectivity-02-static-routing-fa.md) | Host Route را جدا بسازید: IPv4 `/32` و IPv6 `/128`؛ مسیر عمومی‌تر را با مقصد مشخص مقایسه کنید. | جدول مسیریابی Route دقیق Host را نشان دهد و Packet به همان Host از Next Hop مورد انتظار برود؛ Host Prefix با Network Route اشتباه نشود. |
| **3.3.d** IPv4/IPv6 floating static route | [IC-02](academy-ccna-connectivity-02-static-routing-fa.md) | مسیر Primary و مسیر دومِ واقعاً قابل‌دسترسی را با AD متفاوت نصب؛ Primary را در Lab Down و سپس برگردانید. | مسیر Backup فقط هنگام ناموجود/غیرقابل‌استفاده‌شدن Primary طبق طراحی نصب/انتخاب شود؛ مسیر برگشت، AD، Recovery و محدودیت تشخیص خرابی Next Hop جدا ثبت شود. |
| **3.4.a** Single-area OSPFv2 adjacencies | [IC-03](academy-ccna-connectivity-03-ospf-architecture-fa.md) | دو Router هم‌Subnet/Area؛ Hello تا FULL را با Neighbor، Interface و Route بررسی؛ یک پارامتر کنترل‌شده را مختل و اصلاح کنید. | Neighbor مورد انتظار به FULL برسد (با توجه به نوع لینک)، Prefixهای لازم در RIB ظاهر شوند و علت/بازیابی Fault با خروجی زمان‌دار ثبت شود. |
| **3.4.b** OSPFv2 point-to-point | [IC-03](academy-ccna-connectivity-03-ospf-architecture-fa.md) | لینک `/30` مستقیم و Network Type نقطه‌به‌نقطه؛ وضعیت Neighbor و نبود انتخابات DR/BDR را بررسی کنید. | هر دو سمت Network Type/Area/Hello/Dead و همسایگی را مطابق پلتفرم نشان دهند؛ DR/BDR به این لینک نسبت داده نشود. |
| **3.4.c** OSPFv2 broadcast, DR/BDR | [IC-04](academy-ccna-connectivity-04-ospf-dr-cost-fa.md) | سه Router روی Broadcast segment؛ Priority/Router ID را قبل از Election تنظیم؛ یک Election مجدد کنترل‌شده انجام دهید. | DR/BDR در Neighbor table مطابق Priority/Router ID و Election جدید باشد؛ non-preemption و زمان/effect پس از تغییر Priority درست توضیح داده شود. |
| **3.4.d** OSPF Router ID | [IC-03](academy-ccna-connectivity-03-ospf-architecture-fa.md) | Router ID یکتا را پیش از شروع Process تنظیم؛ اگر بعداً تغییر کرد، روش مجاز restart/clear را فقط در Lab انجام دهید. | `show ip ospf`/Neighbor خروجی Router IDهای یکتا را نشان دهد و پس از تغییر، تأثیر نیاز به شروع مجدد Process به‌درستی ثبت شود. |
| **4.1** Inside-source NAT (static and pools) | [IS-01](academy-ccna-services-01-nat-fa.md) | Inside/Outside، Static و Dynamic Pool/PAT را مطابق Address Plan تنظیم؛ ACL انتخاب‌گر NAT را از ACL فیلتر تفکیک کنید. | Translation/Hit/Inside-Global با آزمون مبدا-مقصد مطابق Policy دیده شود؛ Pool/ACL/route و پاسخ برگشت بررسی شوند؛ `deny` در selector به‌تنهایی Packet filtering نیست. |
| **4.2** NTP client and server mode | [IS-02](academy-ccna-services-02-ntp-time-fa.md) | دو Router/منبع ایزوله؛ Server و Client را تنظیم؛ Association, Sync, Stratum و دسترس‌پذیری را دنبال کنید. | Client واقعاً Source/Association را انتخاب و Sync کند؛ `show ntp status/associations` و Clock پس از همگرایی ثبت شوند؛ `ntp master` فقط مرجع Lab است، نه ساعت معتبر اینترنتی. |
| **4.6** DHCP client and relay | [IS-06](academy-ccna-services-06-dhcp-config-fa.md) | یک Interface Router به‌عنوان DHCP Client، Interface دیگر به‌عنوان Relay به Server در Subnet مجزا؛ Lease و DHCP Discover/Offer را تفکیک کنید. | R1 روی Interface Client Lease درست بگیرد؛ Host در LAN از Server دوردست Lease/Option 3 بگیرد؛ `giaddr`/Log/Capture، مسیر برگشت و Fault حذف Helper/Restore ثبت شوند. |
| **4.8** SSH remote access — Configure | [IS-08](academy-ccna-services-08-ssh-fa.md) | Hostname/Domain/Key و Local User/SSHv2؛ همهٔ VTY rangeهای همان Image را بیابید؛ SSH را قبل از منع Telnet بیازمایید. | نشست SSH موفق و در `show users`/`show ssh` دیده شود؛ هر VTY فقط SSH بپذیرد و Telnet رد شود؛ Console راه بازیابی در تمام تمرین بماند. |
| **5.3** Local password access control | [SEC-03](academy-ccna-security-03-local-passwords-fa.md) | Console، VTY/local user و Enable Secret را جدا پیکربندی/آزمون؛ VTY را فقط پس از آماده‌شدن SSH محدود کنید. | احراز هویت هر Line مطابق Policy؛ کاربر عادی Privilege کمینه و Enable جدا باشد؛ Secret/Hash/Private key در خروجی تحویلی افشا نشود. |
| **5.6** ACL | [SEC-06](academy-ccna-security-06-acl-fa.md) | Named Extended ACL با HTTP/HTTPS و DNS روی UDP/TCP، SSH فقط برای PC-B، Deny به Server و Permit مقصدهای دیگر؛ روی Interface/جهت مشخص اعمال کنید. | آزمون مجاز و ممنوع انتهابه‌انتها، DNS و شمارنده‌ها با Policy تطبیق؛ `show ip interface` اعمال/جهت درست؛ مسیر مدیریتی/بازگشت محفوظ و Fault اصلاح شده باشد. |
| **5.7** L2 security (DHCP Snooping, DAI, Port Security) | [SEC-07](academy-ccna-security-07-layer2-security-fa.md) | VLAN/Portها و DHCP Server؛ ترتیب Snooping→Trust→Binding/DAI→Port Security؛ Rogue DHCP/ARP/MAC فقط در Lab. | Trusted port محدود به مسیر Server؛ Binding معتبر برای DAI؛ نقض Port Security و Counter/Log دیده شود؛ Client مجاز پس از Fault و Recovery کار کند؛ Feature/Model ثبت شود. |
| **5.10** WLAN GUI with WPA2 PSK | [SEC-10](academy-ccna-security-10-wlan-gui-wpa2-fa.md) | در GUI واقعی WLAN/SSID، WPA2-Personal/PSK و AES-CCMP؛ AP Join، Policy/VLAN mapping، Client و DHCP. | WLAN روی AP درست فعال و در Client با PSK درست Join شود؛ WPA2-CCMP و IP/Gateway آزمایش شوند؛ PSK غلط رد و سپس Rollback/شواهد بی‌Secret ثبت شود. GUI مفهومی/اسکرین‌شات طراحی‌شده، Verification واقعی نیست. |

**نکتهٔ اشتراک:** جدول بالا از ۲۷ معیار قبولی مجزا استفاده می‌کند، اما پیاده‌سازی‌ها در فایل‌های NF-10/12/13، NA-01/02/03/04/05/06، IC-02/03/04، IS-01/02/06/08 و SEC-03/06/07/10 گروه شده‌اند. در تمرین مشترک، موفقیت یک Objective را به دیگری تعمیم ندهید؛ هر ردیف شاهد خودش را می‌خواهد.

## ۲. ارزیابی ۴۲ بخش بدنه‌محورِ اضافه

این فهرست از ۴۲ بخش نامزدِ inventory پیشین بازساخته شد. نتیجهٔ هر ردیف می‌گوید بخش چه نوع تمرینی است و شاهد/محدودیت آن چیست؛ `subpart` یا عنوان متفاوت به معنی Worksheet مستقل جدید نیست.

| ID | فایل/بخش (پیوند) | نوع و Objective مرتبط | ارزیابی محتوا و حد Verification |
|---|---|---|---|
| B01 | [NA-01 §۳ — توپولوژی کاربرگ](academy-ccna-access-01-vlan-fa.md) | زیر‌بخش عملی؛ 2.1.a/b، 2.2 | توپولوژی/VLAN/Port بخشی از WS مشترک است؛ نام Image/Interface واقعی نیازمند تطبیق و IOS اجرا‌نشده. |
| B02 | [NA-01 §۴ — پیکربندی به ترتیب اجرا](academy-ccna-access-01-vlan-fa.md) | زیر‌بخش پیکربندی؛ 2.1.a/b | دستورات مرحله‌ای موجود؛ Default VLAN باید با حالت پایه و بدون تنظیم صریح ثابت شود؛ نسخه/سوییچ نامشخص. |
| B03 | [NA-03 §۲ — جدول سناریو](academy-ccna-access-03-voice-vlan-fa.md) | طراحی سناریو؛ 2.1.a Voice | Phone+PC و Data/Voice VLAN را به هم متصل می‌کند؛ Voice/PoE/CDP-LLDP به Feature واقعی وابسته است، تماس/PoE اثبات نشده. |
| B04 | [NA-03 §۶ — سؤال‌های سناریویی](academy-ccna-access-03-voice-vlan-fa.md) | تحلیلی/پاسخ‌نامه؛ 2.1.a | برای درک نقش Data/Voice مناسب است؛ نه گام اجرایی یا شاهد Configure/Verify جداگانه. |
| B05 | [NA-06 §۲ — کاربرگ A، EtherChannel L2](academy-ccna-access-06-lacp-etherchannel-fa.md) | نیمهٔ Worksheet؛ 2.4 | دستور LACP/Trunk، Verification و Failure-mode طراحی شده‌اند؛ مدل/IOS و خروجی واقعی هنوز لازم‌اند. |
| B06 | [NA-07 §۵ — توپولوژی کاربرگ](academy-ccna-access-07-rapid-pvst-fa.md) | سناریوی تفسیری | مثلث سه-Switch، VLAN و نقش Root را برای Interpret نشان می‌دهد؛ پیکربندی نمونه/لاب اجرا نشده و Objective این بخش تفسیری است. |
| B07 | [NA-08 §۴ — کاربرگ و Troubleshooting](academy-ccna-access-08-wireless-architecture-fa.md) | تحلیل معماری WLAN؛ 2.6/2.7 | مقایسهٔ AP mode، اتصال WLC، access/trunk و LAG؛ برای شرح/تحلیل کفایت دارد، اما WLC واقعی/GUI در آن نیست. |
| B08 | [NA-09 §۶ — تحلیل دسترسی و WLAN GUI](academy-ccna-access-09-management-gui-fa.md) | تحلیل GUI/روش مدیریت؛ 2.8/2.9 | فرم مفهومی و مقایسهٔ امنیت/فیلدها؛ نام منو و حالت عملی به نسخهٔ WLC وابسته و GUI واقعی مشاهده نشده. |
| B09 | [NA-09 بخش B — تمرین اختیاری IOS Management](academy-ccna-access-09-management-gui-fa.md) | تمرین عملی اختیاری؛ پیوند به 4.8/5.3، نه Objective مستقل 2.8 | SSH/روش مدیریت را عمیق‌تر می‌کند؛ از کاربرگ رسمی SSH/Local Password لینک شده، VTY/IOS واقعی اجرا نشده. |
| B10 | [AUT-02 §۸ — کاربرگ تحلیلی](academy-ccna-automation-02-traditional-vs-controller-fa.md) | مقایسهٔ طراحی؛ 6.2 | Traditional vs Controller-Based و Fail Mode؛ پاسخ تحلیلی است، نه پیکربندی Controller/API. |
| B11 | [AUT-04 §۶ — کاربرگ تحلیلی](academy-ccna-automation-04-control-data-plane-fa.md) | تحلیل Control/Data Plane؛ 6.3.a | جداسازی نقش و Fail Mode؛ Controller واقعی/رفتار محصول آزموده نشده. |
| B12 | [AUT-05 §۶ — کاربرگ API](academy-ccna-automation-05-apis-fa.md) | تحلیل North/Southbound؛ 6.3.b | جهت API و YANG/NETCONF/RESTCONF؛ Endpoint/Capability واقعی برای یک محصول انتخاب نشده. |
| B13 | [AUT-05 تمرین اختیاری Endpoint](academy-ccna-automation-05-apis-fa.md) | اختیاری/Endpoint؛ 6.3.b | فقط در صورت داشتن Endpoint سازگار قابل اجرا؛ API/اعتبارنامه در این Sandbox موجود نبود و پاسخ واقعی ثبت نشده. |
| B14 | [AUT-08 §۵ — سناریوی Ansible/Terraform](academy-ccna-automation-08-config-management-fa.md) | تحلیل ابزار/Resource ownership؛ 6.6 | مفاهیم State/Plan/Module و Risk؛ ابزارها نصب یا اجرا نشده‌اند. |
| B15 | [AUT-08 §۶ — تشخیص قابلیت‌ها](academy-ccna-automation-08-config-management-fa.md) | Worksheet تحلیلی؛ 6.6 | انتخاب ابزار بر اساس Task/Provider/Collection؛ به‌درستی عملیاتی اعلام نمی‌شود؛ نسخهٔ Module/Provider هنوز نمونه‌ای است. |
| B16 | [IC-02 §۳ — توپولوژی کاربرگ](academy-ccna-connectivity-02-static-routing-fa.md) | زیر‌بخش لاب مشترک؛ 3.3.a–d | توپولوژی پایه و افزونهٔ مسیر شناور را تفکیک می‌کند؛ آدرس/Next Hop در طراحی، IOS اجرا‌نشده. |
| B17 | [IC-03 §۶ — توپولوژی کاربرگ](academy-ccna-connectivity-03-ospf-architecture-fa.md) | زیر‌بخش OSPF؛ 3.4.a/b/d | Point-to-point و LANها/Router ID به Worksheet متصل‌اند؛ Interface/Image و Adjacency واقعی لازم است. |
| B18 | [NF-01 §۵ — کاربرگ تحلیلی](academy-ccna-fundamentals-01-components-fa.md) | تحلیلی اجزای شبکه؛ 1.1 | نقش اجزای Router/Switch/Endpoint را از سناریو می‌سنجد؛ نیاز به IOS/PNETLab ندارد. |
| B19 | [NF-02 §۸ — کاربرگ PoE](academy-ccna-fundamentals-02-poe-fa.md) | محاسبه/تحلیل بودجه؛ 1.1.h | PSE/PD، توان و Margin را تحلیل می‌کند؛ PNETLab توان الکتریکی/PoE واقعی را ثابت نمی‌کند. |
| B20 | [NF-03 §۴ — کاربرگ Wireless Controller](academy-ccna-fundamentals-03-wireless-controller-fa.md) | تحلیل AP/WLC/CAPWAP؛ 1.1.d/e | مسیر Control/Data و Central/Local را آموزشی وصل می‌کند؛ WLC/AP Join واقعی ندارد. |
| B21 | [NF-04 §۳ — کاربرگ NGFW/IPS](academy-ccna-fundamentals-04-ngfw-ips-fa.md) | تحلیل امنیت؛ 1.1.c | نقش Firewall/IDS/IPS/Inline را می‌سنجد؛ هیچ حمله، Scan یا IPS واقعی اجرا نشده. |
| B22 | [NF-05 §۶ — کاربرگ معماری شبکه](academy-ccna-fundamentals-05-network-architectures-fa.md) | تحلیل Design؛ 1.2.a–f | Campus/WAN/Spine-Leaf/Cloud را بر اساس سناریو می‌سنجد؛ Drawing مفهومی است نه Survey. |
| B23 | [NF-06 §۵ — کاربرگ رسانه و Verification](academy-ccna-fundamentals-06-ethernet-media-fa.md) | تحلیلی/مشاهده‌ای؛ 1.3 | رسانه، Link و Domain را از سناریو تفکیک می‌کند؛ کابل/Transceiver واقعی آزموده نشده. |
| B24 | [NF-07 §۳ — سناریو و توپولوژی](academy-ccna-fundamentals-07-interface-troubleshooting-fa.md) | طراحی عیب‌یابی؛ 1.4 | دو سر لینک را لازم می‌داند؛ Duplex/Counter خروجی‌ها نمونه و سخت‌افزار واقعی در دسترس نیست. |
| B25 | [NF-07 §۴ — کاربرگ CLI](academy-ccna-fundamentals-07-interface-troubleshooting-fa.md) | Worksheet مشاهده‌ای؛ 1.4 | فرمان/برداشت/دو نمونهٔ زمان‌دار مشخص؛ اجرای IOS/کابل و شمارنده واقعی ثبت نشده. |
| B26 | [NF-08 §۵ — کاربرگ TCP/UDP](academy-ccna-fundamentals-08-tcp-udp-fa.md) | تحلیل/Packet reasoning؛ 1.5 | پاسخ‌های سناریویی دارد؛ Packet Capture واقعی اختیاری است و انجام نشده. |
| B27 | [NF-10 §۶ — سؤال‌های سناریویی](academy-ccna-fundamentals-10-ipv4-subnet-lab-fa.md) | ارزیابی دانش؛ 1.6 | بخشی از Worksheet NF-10 است، نه لاب دوم؛ معیار عملی همان جدول Objective 1.6 است. |
| B28 | [NF-12 §۱ — سناریو و آدرس‌ها](academy-ccna-fundamentals-12-ipv6-interface-lab-fa.md) | Setup/Address plan؛ 1.8 | پایهٔ Worksheet IPv6 است؛ آدرس مستنداتی و IOS واقعی اجرا نشده. |
| B29 | [NF-13 §۵ — Client OS](academy-ccna-fundamentals-13-client-ip-parameters-fa.md) | Verify عملی سیستم‌عامل؛ 1.10 | Windows/macOS/Linux از هم جدا هستند؛ فرمان‌ها OS-specific؛ این Sandbox فقط Linux داشته و دو OS دیگر Verify نشده‌اند. |
| B30 | [NF-14 §۴ — سناریوی RF](academy-ccna-fundamentals-14-wireless-rf-fa.md) | طراحی/تحلیل RF؛ 1.11 | کانال 1/6/11 با قید 2.4GHz/20MHz/مقررات؛ Survey و اندازه‌گیری RF واقعی نیست. |
| B31 | [SEC-06 §۵ — توپولوژی ACL](academy-ccna-security-06-acl-fa.md) | Setup Worksheet؛ 5.6 | Source/Destination و Interface/Policy در توپولوژی است؛ IOS/Server و تست واقعی اجرا نشده. |
| B32 | [SEC-07 §۳ — توپولوژی امنیت L2](academy-ccna-security-07-layer2-security-fa.md) | Setup Worksheet؛ 5.7 | VLAN/Trusted ports/Hosts آمادهٔ تمرین است؛ Feature و Hardware Switch انتخاب/اجرا نشده. |
| B33 | [IS-01 §۲ — سناریوی NAT مرزی](academy-ccna-services-01-nat-fa.md) | تحلیل مرز NAT/ACL؛ 4.1 | نقش selector ACL از packet-filtering جدا می‌شود؛ NAT واقعی/Translation Table وجود ندارد. |
| B34 | [IS-02 — اجرای NTP و Verification](academy-ccna-services-02-ntp-time-fa.md) | Worksheet پیکربندی؛ 4.2 | Client/Server/Association و زمان همگرایی در طراحی است؛ منبع NTP واقعی و IOS اجرا نشده. |
| B35 | [IS-03 §۵ — DHCP/DNS](academy-ccna-services-03-dhcp-dns-fa.md) | توضیح با فعالیت تحلیلی/اختیاری؛ 4.3 | سناریو و Error isolation دارند، اما فعل رسمی Explain است؛ Server و Packet Capture اجرا نشده. |
| B36 | [IS-04 §۴ — سناریوی SNMP](academy-ccna-services-04-snmp-fa.md) | Setup طرح لاب؛ 4.4 | Agent/NMS/UDP/IP و v2c محدودشده به Lab؛ نمونهٔ Community ناامن است و روی دستگاه واقعی به‌کار نرود. |
| B37 | [IS-04 §۵ — Worksheet SNMP](academy-ccna-services-04-snmp-fa.md) | کاربرگ فنی/تست؛ 4.4 | Poll/Trap، ACL و Fault/Recovery طراحی شده؛ NMS/IOS موجود نبود و Poll/Trap واقعی نداریم. |
| B38 | [IS-04 «گام‌ها و شواهد»](academy-ccna-services-04-snmp-fa.md) | زیرعنوانِ داخل Worksheet B37 | سرفصل مراحل و شواهد همان کاربرگ است، نه تمرین مستقل سوم؛ شمارش جداگانهٔ آن یک raw-section است. |
| B39 | [IS-06 §۲ — توپولوژی و IP](academy-ccna-services-06-dhcp-config-fa.md) | Setup/Address plan؛ 4.6 | DHCP Client و Relay را در Subnet جدا می‌چیند؛ Server/Image و Lease واقعی موجود نیست. |
| B40 | [IS-06 §۵ — Worksheet DHCP Relay](academy-ccna-services-06-dhcp-config-fa.md) | کاربرگ Configure/Verify؛ 4.6 | Scope/Helper/Lease/Fault/Restore و معیار تحویل دارد؛ هیچ IOS/DHCP Server اجرا نشده. |
| B41 | [IS-09 §۴ — File Transfer](academy-ccna-services-09-tftp-ftp-fa.md) | فعالیت/عیب‌یابی انتقال فایل؛ 4.9 | Active/Passive/Transfer/Integrity را سناریویی تفکیک می‌کند؛ FTP/TFTP Server/IOS اجرا نشده. |
| B42 | [IS-09 «Topology, equipment, address plan»](academy-ccna-services-09-tftp-ftp-fa.md) | Setup زیر‌بخش؛ 4.9 | آدرس/Node/Server بخشی از Worksheet B41 است، نه کاربرگ مستقل؛ Version و Transfer واقعی باز است. |

## ۳. پیوند تمرین به همهٔ ۵۹ درس CCNA

در ستون «فعالیت پیوندی»، نوع کار به‌صراحت تعیین شده است: `عملی طراحی‌شده` یعنی مراحل/فرمان پیشنهادی هستند ولی Platform اجرا نشده؛ `تحلیلی` یعنی فعالیت متناسب با فعل Objective بدون ادعای CLI؛ `مفهومی` یعنی درس را با Case/پاسخ/نمودار می‌بندد. این نگاشت نمی‌گوید همهٔ Objectiveها کاربرگ عملی لازم دارند؛ فعل رسمی و Platform boundary حفظ می‌شود.

| کد | درس | فعالیت پیوندی و ماهیت |
|---|---|---|
| NF-01 | [اجزای شبکه](academy-ccna-fundamentals-01-components-fa.md) | §۵ کاربرگ تحلیلی: تشخیص نقش Router/Switch/AP/Server؛ مفهومی. |
| NF-02 | [PoE](academy-ccna-fundamentals-02-poe-fa.md) | §۸ بودجهٔ توان: محاسبهٔ PSE/PD/Margin؛ تحلیلی، نه آزمون PoE واقعی. |
| NF-03 | [Wireless Controller](academy-ccna-fundamentals-03-wireless-controller-fa.md) | §۴ مسیر CAPWAP و Central/Local؛ تحلیل معماری، بدون WLC. |
| NF-04 | [NGFW و IPS](academy-ccna-fundamentals-04-ngfw-ips-fa.md) | §۳ Threat/Policy case؛ تحلیلی، بدون Scan/IPS. |
| NF-05 | [Network Architectures](academy-ccna-fundamentals-05-network-architectures-fa.md) | §۶ انتخاب معماری برای سناریوی سازمانی؛ تحلیلی. |
| NF-06 | [Ethernet و رسانه](academy-ccna-fundamentals-06-ethernet-media-fa.md) | §۵ مقایسهٔ Link/Media/Domain؛ مفهومی/مشاهده‌ای، کابل واقعی اجرا نشده. |
| NF-07 | [Interface Troubleshooting](academy-ccna-fundamentals-07-interface-troubleshooting-fa.md) | §۴ مشاهدهٔ دو سمت/Counter با زمان‌بندی؛ IOS/سخت‌افزار اجرا نشده. |
| NF-08 | [TCP/UDP](academy-ccna-fundamentals-08-tcp-udp-fa.md) | §۵ تحلیل Flow/Port/Transport؛ Packet Capture واقعی اختیاری و اجرا نشده. |
| NF-09 | [IPv4 مبانی](academy-ccna-fundamentals-09-ipv4-basics-fa.md) | §۴ تمرین Prefix/Address؛ برای Configure/Verify عملی، خروجی کار به NF-10 می‌رود. |
| NF-10 | [IPv4 Subnet Lab](academy-ccna-fundamentals-10-ipv4-subnet-lab-fa.md) | §۲/۳/۴ Worksheet هدف `1.6`؛ طراحی‌شده، IOS اجرا نشده. |
| NF-11 | [IPv6 Addressing](academy-ccna-fundamentals-11-ipv6-addressing-fa.md) | §۵ کاربرگ ULA/GUA/Link-Local/Prefix؛ تحلیلی، به NF-12 برای اعمال عملی پیوند دارد. |
| NF-12 | [IPv6 Interface Lab](academy-ccna-fundamentals-12-ipv6-interface-lab-fa.md) | §۵ Worksheet هدف `1.8`؛ طراحی‌شده، IOS اجرا نشده. |
| NF-13 | [Client IP parameters](academy-ccna-fundamentals-13-client-ip-parameters-fa.md) | §۵ آزمون سه OS برای هدف `1.10`; فقط سیستم‌عامل واقعی می‌تواند Verification را ثابت کند. |
| NF-14 | [Wireless RF](academy-ccna-fundamentals-14-wireless-rf-fa.md) | §۴ طرح کانال/سناریو؛ تحلیلی، Site Survey واقعی لازم است. |
| NF-15 | [MAC Learning](academy-ccna-fundamentals-15-switching-mac-fa.md) | §۴ MAC table/aging؛ مشاهدهٔ Switch طراحی‌شده، Device اجرا نشده؛ به NA-01 برای VLAN پیکربندی پیوند دارد. |
| NF-16 | [Virtualization/Containers/VRF](academy-ccna-fundamentals-16-virtualization-container-vrf-fa.md) | §۴ مرزبندی VM/Container/VRF؛ تحلیل، نه lab جداسازی واقعی. |
| NA-01 | [VLAN Access و Default VLAN](academy-ccna-access-01-vlan-fa.md) | §۷ Worksheet اهداف `2.1.a`, `2.1.b`; IOS طراحی‌شده. |
| NA-02 | [Trunk/802.1Q/Native](academy-ccna-access-02-trunk-8021q-fa.md) | §۳ Worksheet اهداف `2.2.a–c`; هر هدف معیار جدا در جدول ۱ دارد. |
| NA-03 | [Voice VLAN](academy-ccna-access-03-voice-vlan-fa.md) | §۵ تلفن/PC؛ اجراپذیری وابسته به Phone/PoE/Feature واقعی. |
| NA-04 | [Inter-VLAN Routing](academy-ccna-access-04-intervlan-router-stick-fa.md) | §۲–۵ و Worksheet هدف `2.1.c`; IOS/Client اجرا نشده. |
| NA-05 | [CDP/LLDP](academy-ccna-access-05-cdp-lldp-fa.md) | §۵ Worksheet هدف `2.3`; دو Switch، Lab طراحی‌شده. |
| NA-06 | [LACP/EtherChannel](academy-ccna-access-06-lacp-etherchannel-fa.md) | §۲ L2 و §۳ L3، دو زیرکاربرگ هدف `2.4`; اجرا نشده. |
| NA-07 | [Rapid PVST+](academy-ccna-access-07-rapid-pvst-fa.md) | §۱۰ تفسیر/تحلیل Role, State, Guards؛ خروجی نمونه، IOS اجرا نشده. |
| NA-08 | [Wireless Architecture](academy-ccna-access-08-wireless-architecture-fa.md) | §۴ AP/WLC physical/logical design؛ مفهومی و نسخه‌وابسته. |
| NA-09 | [Management و WLAN GUI](academy-ccna-access-09-management-gui-fa.md) | §۶ Security/GUI case + بخش B SSH اختیاری؛ GUI واقعی نیست و SSH عملی به IS-08 لینک دارد. |
| IC-01 | [Routing Table](academy-ccna-connectivity-01-routing-table-fa.md) | §۹ مشاهدهٔ Route اختیاری + تمرین تحلیلی AD/Metric؛ IOS اجرا نشده. |
| IC-02 | [Static Routing](academy-ccna-connectivity-02-static-routing-fa.md) | §۷ Worksheet اهداف `3.3.a–d`; چهار معیار مجزا در جدول ۱. |
| IC-03 | [OSPF Architecture](academy-ccna-connectivity-03-ospf-architecture-fa.md) | §۱۰ Worksheet اهداف `3.4.a/b/d`; Adjacency/P2P/Router-ID جدا ارزیابی می‌شوند. |
| IC-04 | [OSPF DR/BDR](academy-ccna-connectivity-04-ospf-dr-cost-fa.md) | §۵ Worksheet هدف `3.4.c`; Broadcast Election؛ اجرا نشده. |
| IC-05 | [OSPF Area/LSA](academy-ccna-connectivity-05-ospf-area-lsa-fa.md) | §۶ Lab تحلیلی/مشاهده‌ای؛ IOS اجرا نشده و هدف عملی مستقل در v1.1 نیست. |
| IC-06 | [FHRP](academy-ccna-connectivity-06-fhrp-fa.md) | §۵ HSRP/Tracking/Failover؛ هدف رسمی `3.5` مفهومی، Failover اجرا نشده. |
| IS-01 | [NAT](academy-ccna-services-01-nat-fa.md) | §۵ Worksheet هدف `4.1`; ترجمه/ACL/route باید واقعی Verify شوند. |
| IS-02 | [NTP](academy-ccna-services-02-ntp-time-fa.md) | §۵ Worksheet هدف `4.2`; IOS/Clock source اجرا نشده. |
| IS-03 | [DHCP/DNS Roles](academy-ccna-services-03-dhcp-dns-fa.md) | §۵ توضیح DORA/Resolver و خطای کنترل‌شده؛ سرور واقعی اختیاری و اجرا نشده. |
| IS-04 | [SNMP](academy-ccna-services-04-snmp-fa.md) | §۵ Poll/Trap/ACL؛ Community فقط Lab و NMS/IOS اجرا نشده. |
| IS-05 | [Syslog](academy-ccna-services-05-syslog-fa.md) | §۵ Severity/Collector investigation؛ Collector/IOS واقعی اجرا نشده. |
| IS-06 | [DHCP Client/Relay](academy-ccna-services-06-dhcp-config-fa.md) | §۵ Worksheet هدف `4.6`; Lease/Relay/Scope اجرا نشده. |
| IS-07 | [QoS](academy-ccna-services-07-qos-fa.md) + [کاربرگ مستقل](academy-ccna-services-07-qos-lab-fa.md) | طبقه‌بندی نظری به همراه Lab کامل طراحی‌شده؛ IOS XE/Traffic/Queue هنوز اجرا نشده. |
| IS-08 | [SSH](academy-ccna-services-08-ssh-fa.md) | §۵ Worksheet هدف `4.8`; SSH/Telnet/VTY آزموده نشده. |
| IS-09 | [TFTP/FTP](academy-ccna-services-09-tftp-ftp-fa.md) | §۴ انتقال/Passive-vs-Active؛ Server/IOS اجرا نشده. |
| SEC-01 | [Threats/Vulnerabilities](academy-ccna-security-01-threats-fa.md) | §۵ Threat vs evidence case؛ تحلیلی و بدون Scan/Exploit. |
| SEC-02 | [Awareness/Physical](academy-ccna-security-02-awareness-physical-fa.md) | §۵ policy/training case؛ تحلیلی، بدون تمرین نفوذ/ورود واقعی. |
| SEC-03 | [Local Passwords](academy-ccna-security-03-local-passwords-fa.md) | §۵ Worksheet هدف `5.3`; Secrets placeholder، IOS اجرا نشده. |
| SEC-04 | [Password/MFA](academy-ccna-security-04-password-management-mfa-fa.md) | §۶ انتخاب کنترل/عامل MFA؛ تحلیل، سامانهٔ MFA اجرا نشده. |
| SEC-05 | [IPsec VPN](academy-ccna-security-05-ipsec-vpn-fa.md) | §۵ VPN topologies/verification reasoning؛ Tunnel واقعی برقرار نشده. |
| SEC-06 | [ACL](academy-ccna-security-06-acl-fa.md) | §۱۰ Worksheet هدف `5.6`; Allowed/Deny/DNS/Counter طراحی‌شده، IOS اجرا نشده. |
| SEC-07 | [Layer-2 Security](academy-ccna-security-07-layer2-security-fa.md) | §۷ Worksheet هدف `5.7`; Binding/DAI/Snooping/Port Security اجرا نشده. |
| SEC-08 | [AAA](academy-ccna-security-08-aaa-fa.md) | §۹ Authentication/Authorization/Accounting Lab؛ Server و IOS اجرا نشده؛ رسمی `5.8` Compare است. |
| SEC-09 | [Wireless Security](academy-ccna-security-09-wireless-security-fa.md) | §۴ WPA/WPA2/WPA3 case; AP/Client واقعی آزموده نشده. |
| SEC-10 | [WLAN WPA2-PSK GUI](academy-ccna-security-10-wlan-gui-wpa2-fa.md) | §۵ Worksheet هدف `5.10`; Controller/GUI/AP Join اجرا نشده. |
| AUT-01 | [Automation Impact](academy-ccna-automation-01-automation-impact-fa.md) | §۶ Change-risk/Pre-Post-check case؛ تحلیل، نه اجرای ابزار. |
| AUT-02 | [Traditional vs Controller](academy-ccna-automation-02-traditional-vs-controller-fa.md) | §۸ comparison/Fail-mode؛ Controller واقعی اجرا نشده. |
| AUT-03 | [SDN Fabric](academy-ccna-automation-03-sdn-fabric-fa.md) + [کاربرگ محدود](academy-ccna-automation-03-sdn-fabric-lab-fa.md) | Controller architecture مفهومی؛ Linux underlay فقط بخش اجراشده، VXLAN unsupported در Sandbox. |
| AUT-04 | [Control/Data Plane](academy-ccna-automation-04-control-data-plane-fa.md) | §۶ fail-mode map؛ تحلیلی، هیچ Controller وصل نشده. |
| AUT-05 | [North/Southbound APIs](academy-ccna-automation-05-apis-fa.md) | §۶ API-direction/Endpoint exercise؛ API واقعی فراخوانی نشده. |
| AUT-06 | [AI/ML](academy-ccna-automation-06-ai-ml-fa.md) | §۸ تحلیل داده/مدل و معیار؛ مدل/دادهٔ عملیاتی اجرا نشده. |
| AUT-07 | [REST API](academy-ccna-automation-07-rest-api-fa.md) | §۷ Request/Auth/CRUD Worksheet؛ Mock/unit test جداگانه، API واقعی در دسترس نیست. |
| AUT-08 | [Ansible/Terraform](academy-ccna-automation-08-config-management-fa.md) | §۶ State/Plan/Ownership analysis; ابزارها نصب/اجرا نشده‌اند. |
| AUT-09 | [JSON](academy-ccna-automation-09-json-fa.md) | §۶ تمرین محلی JSON؛ PNETLab لازم نیست؛ Parser/dialect این درس در آزمون تحویل اجرا نشده و کفایت کاربرگ فقط متنی ارزیابی شده است. |

## ۴. روش نهاییِ ثبت وضعیت

برای هر اجرای آینده، یک ردیف شاهد با این فیلدها اضافه شود: `Objective ID`, worksheet, hostname/Image/model/version, `show version`/OS version, date, exact command/tool version, topology/address plan, sanitized before/after output, failure injected, recovery, acceptance decision and reviewer. رمز، PSK، token، private key و اطلاعات سازمانی در Git یا گزارش قرار نگیرد.

**نتیجهٔ این بازبینی:** همهٔ ۲۷ هدف عملی، ۴۲ بخش خام نامزد و ۵۹ درس دارای محل فعالیت/پیوند و حد/نوع Verification مشخص‌اند. این نتیجه، ممیزی فنی کاملِ همهٔ ۵۹ درس یا اجرای ۲۷ هدف نیست. وضعیت واقعی ۰/۲۷ IOS/PNETLab/GUI/API objective lab اجراشده است؛ فقط Underlay Linux در کاربرگ AUT-03 به‌طور محدود آزموده شد.
