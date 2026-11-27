# صورت‌مسئله ادغام آکادمی — بازبینی ناتمام

این سند فهرست موجودی است، نه گواهی صحت محتوایی. منبع قدیمی: `5a7474902c8d729950288198953686702cfd85dc`، معماری جاری: `430b4212d1edd4a290c7da578c3372c604d983dd`. درس‌های قدیمی به نسخه جاری منتقل نشده‌اند و تطابق معنایی آنها با درس‌های جاری اثبات نشده است. ۱۱۴ عنوان قدیمی و ۱۳ عنوان فعال شمارش شده است؛ هیچ درس قدیمی بازبینی کامل و هیچ آزمایشگاهی اجرا نشده است.

## تفاوت معماری

- کاتالوگ فعلی به blueprintهای Curriculum 5.0 و engine مربوط به خود ارجاع می‌دهد؛ محتوا در داشبورد احراز هویت‌شده ارائه می‌شود. آفلاین مستقل و داده ۱۱۴ درسی قدیمی در این مبنا وجود ندارند.
- در نسخه قدیمی، داده‌ها در یک JSON با ساختار دیگر، داشبورد و simulator جداگانه و HTML مستقل جاسازی‌شده‌اند؛ کلیدهای پیشرفت با کد فعلی هم‌نام ولی ساختار state آنها متفاوت است. جایگزینی فایل‌ها یا بازنویسی کلید مشترک بدون مهاجرت داده خطر از دست رفتن پیشرفت و قابلیت‌های فعلی را دارد.
- برای ادغام باید شناسه‌های پایدار، وضعیت بازبینی هر مؤلفه، رندر و قرارداد محتوایی، داده پیشرفت مستقل یا مهاجرت بدون تخریب و روش build آفلاین مشخص و آزمون شوند. هم‌عنوان بودن به‌تنهایی اثبات هم‌ارزی درس نیست.

## یافته‌های محدود نمونه‌ای — نیازمند اصلاح در انتقال

- `auto_12`: متن قدیمی drift را در بخش‌هایی مغایرت state و کد تعریف می‌کند؛ این تعریف برای تغییر خارج از Terraform دقیق نیست. مطابق مستندات HashiCorp، drift به تغییر زیرساخت واقعی نسبت به پیکربندی مربوط است؛ refresh-only تغییرات پیشنهادی state نسبت به منابع مشاهده‌شده را نشان می‌دهد و apply آن منابع را به پیکربندی بازنمی‌گرداند. این درس باید با تمایز کد، state و واقعیت بازنویسی و تمرین Mock از Terraform واقعی جدا شود. [مستندات HashiCorp](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift).
- `spec_cyber`: هدف از «۷ مرحله NIST 800-61» می‌گوید، در متن ۶ مرحله آمده و کد آزمایشگاه از ۴ نام ترکیبی استفاده می‌کند. همچنین Rev. 3 در سال ۲۰۲۵ نهایی شده و Rev. 2 کنار گذاشته شده است؛ نباید این شمارش را بدون ذکر نسخه به استاندارد جاری نسبت داد. [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
- `s01`: توصیف تغییر Wi-Fi به Ethernet به‌عنوان تغییر صرفاً لایه‌های پایین مطلق است؛ تغییر رابط می‌تواند آدرس، gateway یا اتصال حمل را نیز تغییر دهد. عبارت «UDP سریع» نیز تضمین سرعت نسبت به TCP نیست. نیازمند اصلاح همراه با ارزیابی کامل کل درس و سؤال‌ها.

این سه مورد فقط نمونه هستند، نه بازبینی کامل این سه درس یا سایر درس‌ها.

## کاتالوگ فعال فعلی (۱۳ عنوان)

- `academy-stage-zero-06-client-server-fa` — Client، Server و سرویس
- `ccna-v11-1.1.a` — روتر: تصمیم‌گیرندهٔ بین شبکه‌ها
- `ccna-v11-1.1.b` — سوئیچ لایه ۲ و لایه ۳: مرز قاب و بسته
- `ccna-v11-1.1.c` — فایروال نسل جدید و IPS: عبور دادن یا متوقف کردن؟
- `ccna-v11-1.1.d` — Access Point: پل بین بی‌سیم و کابل
- `ccna-v11-1.1.e` — Controller: مغز مدیریت WLAN
- `ccna-v11-1.1.f` — Endpoint: نقطهٔ شروع و پایان شاهد
- `ccna-v11-1.1.g` — Server: سرویس‌هایی که شبکه را زنده نگه می‌دارند
- `ccna-v11-1.1.h` — PoE: وقتی کابل داده، برق هم می‌دهد
- `ccna-v11-1.2.a` — معماری two-tier: access و distribution
- `ccna-v11-1.2.b` — معماری three-tier: core جدا از distribution
- `ccna-v11-1.2.c` — spine-leaf: هر leaf به همهٔ spineها
- `ccna-v11-1.2.d` — WAN: وقتی فاصله و ISP وارد طراحی می‌شوند

## موجودی شناسه‌های قدیمی (۱۱۴ عنوان؛ انتقال و بازبینی نشده)

| شناسه | عنوان | وضعیت |
|---|---|---|
| `s01` | مدل OSI و TCP/IP چیست؟ سفر گام‌به‌گام یک پیام از مرورگر تا کابل | انتقال و بازبینی کامل نشده |
| `s02` | فریم Ethernet، آدرس MAC و عملکرد ARP چیست؟ | انتقال و بازبینی کامل نشده |
| `s04` | آدرس‌دهی IPv4، Subnetting و VLSM و CIDR چیست؟ | انتقال و بازبینی کامل نشده |
| `s10` | VLAN و Trunk 802.1Q چیست؟ جداسازی منطقی و ارتباط بین VLANها | انتقال و بازبینی کامل نشده |
| `s11` | معماری Leaf-Spine چیست؟ راهنمای کامل Clos، ECMP و VXLAN BGP EVPN | انتقال و بازبینی کامل نشده |
| `s12` | اتوماسیون شبکه با Python، REST API و NETCONF/YANG چیست؟ | انتقال و بازبینی کامل نشده |
| `s03` | سوئیچینگ، Collision Domain و تفاوت TCP و UDP چیست؟ | انتقال و بازبینی کامل نشده |
| `s05` | خلاصه‌سازی مسیر (CIDR Summarization) و طراحی IP Plan سازمانی | انتقال و بازبینی کامل نشده |
| `s06` | مبانی IPv6، ICMP و ICMPv6 و تحلیل Three-Way Handshake | انتقال و بازبینی کامل نشده |
| `s07` | سرویس‌های DNS، DHCP، NAT/PAT و تحلیل بسته با Wireshark | انتقال و بازبینی کامل نشده |
| `s08` | معماری Router و Switch و تسلط بر Cisco IOS CLI | انتقال و بازبینی کامل نشده |
| `s09` | مبانی Routing، عیب‌یابی لایه‌به‌لایه و پروژه ترم اول | انتقال و بازبینی کامل نشده |
| `ccna_01` | معماری شبکه، توپولوژی‌ها، کابل‌کشی و فیبر نوری (Network Fundamentals) | انتقال و بازبینی کامل نشده |
| `ccna_02` | پروتکل STP و RSTP، CDP/LLDP و تجمیع لینک EtherChannel (LACP) | انتقال و بازبینی کامل نشده |
| `ccna_03` | مسیریابی Static، Default، Floating Static و OSPF Single-Area | انتقال و بازبینی کامل نشده |
| `ccna_04` | سرویس‌های زیرساخت IP: HSRP، NTP، Syslog و SNMP | انتقال و بازبینی کامل نشده |
| `ccna_05` | امنیت شبکه سیسکو: ACL، Port Security، DHCP Snooping و DAI | انتقال و بازبینی کامل نشده |
| `ccna_06` | معماری SDN، Cisco Catalyst Center، REST API و اتوماسیون شبکه | انتقال و بازبینی کامل نشده |
| `adv_01` | Advanced Switching: MST، Guardهای STP، UDLD و StackWise | انتقال و بازبینی کامل نشده |
| `adv_02` | Advanced Routing: OSPF Multi-Area، انواع LSA و Stub / NSSA | انتقال و بازبینی کامل نشده |
| `adv_03` | سرویس‌های پیشرفته: VRF-Lite، IP SLA و پایش ترافیک با NetFlow | انتقال و بازبینی کامل نشده |
| `adv_04` | عیب‌یابی سیستماتیک پیشرفته: Control/Data Plane، MTU/MSS و Asymmetric Routing | انتقال و بازبینی کامل نشده |
| `ccnp_01` | 350-401 ENCOR: مجازی‌سازی (GRE/IPsec/LISP/VXLAN) و Assurance | انتقال و بازبینی کامل نشده |
| `ccnp_02` | 300-410 ENARSI: مسیریابی سیاستی (PBR)، DMVPN و MPLS L3VPN | انتقال و بازبینی کامل نشده |
| `spec_ent` | تخصص Enterprise: IS-IS، اتصال Campus (SD-Access) به SD-WAN و معماری ۱۰۰ شعبه‌ای | انتقال و بازبینی کامل نشده |
| `spec_sec` | تخصص امنیت: Cisco Secure Firewall (FTD)، ISE، 802.1X و معماری Zero Trust | انتقال و بازبینی کامل نشده |
| `spec_sp` | تخصص Service Provider: معماری P/PE/CE، MPLS L3VPN و مهندسی برچسب | انتقال و بازبینی کامل نشده |
| `spec_wl` | تخصص Wireless: فیزیک RF (dBm/SNR)، تحول Wi-Fi 6/6E/7 و معماری Catalyst 9800 | انتقال و بازبینی کامل نشده |
| `spec_collab` | تخصص Collaboration & VoIP: پروتکل SIP، RTP، CUCM و طراحی Dial Plan | انتقال و بازبینی کامل نشده |
| `spec_cyber` | تخصص Cybersecurity: راه‌اندازی SOC، SIEM، Incident Response و Threat Hunting | انتقال و بازبینی کامل نشده |
| `ccie_01` | CCIE Enterprise Infrastructure (350-401 ENCOR + Lab + ۲۰۰ سناریو) | انتقال و بازبینی کامل نشده |
| `ccde_01` | موضوع ۱ CCDE: Network Architecture Fundamentals و تفکر معماری کلان | انتقال و بازبینی کامل نشده |
| `ccna_v1` | مفاهیم Virtualization، Cloud و مقایسه On-Premises با ابری | انتقال و بازبینی کامل نشده |
| `ccna_02_vlan` | VLAN، پورت‌های Access و Trunk و Native VLAN: جداسازی یک سوئیچ به چند شبکه | انتقال و بازبینی کامل نشده |
| `ccna_wl` | مبانی Wireless LAN، معماری AP/WLC و پیکربندی WLAN پایه | انتقال و بازبینی کامل نشده |
| `ccna_v6` | مسیریابی IPv4 و IPv6، Longest Prefix Match و Metric/AD | انتقال و بازبینی کامل نشده |
| `ccna_dhcp` | سرویس‌های DHCP Server، DHCP Relay (ip helper-address) و DNS | انتقال و بازبینی کامل نشده |
| `ccna_nat` | پیاده‌سازی Static NAT، Dynamic NAT و PAT (NAT Overload) | انتقال و بازبینی کامل نشده |
| `ccna_qos_ssh` | مبانی QoS، مدیریت امن SSH و انتقال فایل (FTP/TFTP/SCP) | انتقال و بازبینی کامل نشده |
| `ccna_acl` | تهدیدات امنیتی، AAA (TACACS+ / RADIUS)، VPN مقدماتی و Hardening تجهیزات | انتقال و بازبینی کامل نشده |
| `adv_pvl` | Private VLAN، Voice VLAN و بهینه‌سازی VLAN Pruning | انتقال و بازبینی کامل نشده |
| `adv_ec` | Advanced EtherChannel، L3 Port-Channel و مقایسهٔ HSRP / VRRP / GLBP | انتقال و بازبینی کامل نشده |
| `adv_eigrp` | پروتکل EIGRP: Metric ترکیبی، الگوریتم DUAL و Stub | انتقال و بازبینی کامل نشده |
| `adv_redist` | Route Redistribution، Prefix-List، Route-Map و جلوگیری از Route Feedback | انتقال و بازبینی کامل نشده |
| `adv_bgp` | مبانی BGP، همسایگی eBGP/iBGP، Route Reflector و Path Selection | انتقال و بازبینی کامل نشده |
| `adv_qos` | کیفیت سرویس (QoS): MQC، PHB/DSCP، Token Bucket و WRED | انتقال و بازبینی کامل نشده |
| `adv_mcast` | مبانی Multicast: آدرس‌دهی گروهی، IGMP Snooping و PIM Sparse Mode | انتقال و بازبینی کامل نشده |
| `adv_bfd` | پروتکل BFD (کشف خرابی میلی‌ثانیه‌ای) و Flexible NetFlow | انتقال و بازبینی کامل نشده |
| `ccnp_enc_arch` | ENCOR حوزه ۱: معماری Enterprise، سخت‌افزار CEF/TCAM، SD-Access و SD-WAN | انتقال و بازبینی کامل نشده |
| `ccnp_enc_inf` | ENCOR حوزه ۳: زیرساخت L2/L3 (نوع شبکه OSPF، eBGP و Wireless Roaming) | انتقال و بازبینی کامل نشده |
| `ccnp_enc_sec` | ENCOR حوزه ۵: امنیت زیرساخت (CoPP با MQC، AAA/ACL و امنیت REST API) | انتقال و بازبینی کامل نشده |
| `ccnp_enc_auto` | ENCOR حوزه ۶: اتوماسیون در CCNP (JSON، YANG، NETCONF/RESTCONF، EEM و Python/Ansible) | انتقال و بازبینی کامل نشده |
| `ccnp_ensdwi` | تخصصی 300-415 ENSDWI: معماری Cisco Catalyst SD-WAN (OMP، TLOC و AAR) | انتقال و بازبینی کامل نشده |
| `ccnp_ensld` | تخصصی 300-420 ENSLD: طراحی شبکهٔ سازمانی (Oversubscription، مقیاس IGP/BGP و IPv6) | انتقال و بازبینی کامل نشده |
| `ccnp_enauto` | تخصصی 300-435 ENAUTO: مدل‌های YANG، NETCONF/RESTCONF و API پلتفرم‌های سیسکو | انتقال و بازبینی کامل نشده |
| `ccnp_encc` | تخصصی 300-440 ENCC: معماری اتصال امن و مقیاس‌پذیر به Cloud (AWS / Azure / Cloud OnRamp) | انتقال و بازبینی کامل نشده |
| `ccnp_enna` | تخصصی 300-445 ENNA: تضمین کیفیت شبکه با ThousandEyes و Catalyst Center Assurance | انتقال و بازبینی کامل نشده |
| `spec_ent_campus` | ۷.۱ Enterprise: طراحی Campus پیشرفته، StackWise Virtual (SVL) و پیشگیری از Split-Brain | انتقال و بازبینی کامل نشده |
| `spec_ent_sd` | ۷.۱ Enterprise: SD-WAN، Catalyst Center و معماری Zero-Touch برای ۱۰۰ شعبه | انتقال و بازبینی کامل نشده |
| `spec_sec_vpn` | ۷.۲ Security: Site-to-Site و Remote Access IPsec VPN با IKEv2 و VTI | انتقال و بازبینی کامل نشده |
| `spec_sec_ise` | ۷.۲ Security: معماری خوشه‌ای Cisco ISE، مدیریت دستگاه با TACACS+، Posture و pxGrid | انتقال و بازبینی کامل نشده |
| `spec_dc_nx` | ۷.۳ Data Center: سیستم‌عامل Cisco NX-OS، معماری Nexus و vPC (Virtual Port Channel) | انتقال و بازبینی کامل نشده |
| `spec_dc_aci` | ۷.۳ Data Center: معماری Cisco ACI، کنترلر APIC، مدل EPG/Contract و Multi-Site | انتقال و بازبینی کامل نشده |
| `spec_dc_stor` | ۷.۳ Data Center: شبکهٔ ذخیره‌سازی (SAN)، Fibre Channel، Zoning و FCoE | انتقال و بازبینی کامل نشده |
| `spec_sp_xr` | ۷.۴ Service Provider: معماری Cisco IOS XR، مدل Commit، زبان RPL و eBGP امن | انتقال و بازبینی کامل نشده |
| `spec_sp_sr` | ۷.۴ Service Provider: معماری Segment Routing (SR-MPLS و SRv6) و بازیابی TI-LFA | انتقال و بازبینی کامل نشده |
| `spec_wl_survey` | ۷.۵ Wireless: طراحی RF، سه فاز Site Survey و پروژهٔ Wi-Fi ساختمان ۱۰ طبقه | انتقال و بازبینی کامل نشده |
| `spec_collab_gw` | ۷.۶ Collaboration: CUBE، Expressway، Webex و پروژه VoIP بیست شعبه | انتقال و بازبینی کامل نشده |
| `auto_01` | ۷.۷ Automation (درس ۱ از ۲۰): Linux پیش‌نیاز مهندس شبکه | انتقال و بازبینی کامل نشده |
| `auto_02` | ۷.۷ Automation (درس ۲ از ۲۰): Python مقدماتی برای شبکه | انتقال و بازبینی کامل نشده |
| `auto_03` | ۷.۷ Automation (درس ۳ از ۲۰): Python پیشرفته (Netmiko، Paramiko، Nornir) | انتقال و بازبینی کامل نشده |
| `auto_04` | ۷.۷ Automation (درس ۴ از ۲۰): کنترل نسخه با Git و GitHub | انتقال و بازبینی کامل نشده |
| `auto_05` | ۷.۷ Automation (درس ۵ از ۲۰): ساختارهای داده JSON و YAML | انتقال و بازبینی کامل نشده |
| `auto_06` | ۷.۷ Automation (درس ۶ از ۲۰): مبانی REST API و Postman | انتقال و بازبینی کامل نشده |
| `auto_07` | ۷.۷ Automation (درس ۷ از ۲۰): پروتکل HTTP و HTTPS در برنامه‌نویسی شبکه | انتقال و بازبینی کامل نشده |
| `auto_08` | ۷.۷ Automation (درس ۸ از ۲۰): پروتکل NETCONF | انتقال و بازبینی کامل نشده |
| `auto_09` | ۷.۷ Automation (درس ۹ از ۲۰): پروتکل RESTCONF | انتقال و بازبینی کامل نشده |
| `auto_10` | ۷.۷ Automation (درس ۱۰ از ۲۰): زبان مدل‌سازی داده YANG | انتقال و بازبینی کامل نشده |
| `auto_11` | ۷.۷ Automation (درس ۱۱ از ۲۰): اتوماسیون با Ansible (Playbook & Inventory) | انتقال و بازبینی کامل نشده |
| `auto_12` | ۷.۷ Automation (درس ۱۲ از ۲۰): زیرساخت به عنوان کد با Terraform | انتقال و بازبینی کامل نشده |
| `auto_13` | ۷.۷ Automation (درس ۱۳ از ۲۰): Cisco NSO (Network Services Orchestrator) | انتقال و بازبینی کامل نشده |
| `auto_14` | ۷.۷ Automation (درس ۱۴ از ۲۰): اکوسیستم Cisco DevNet و SDKها | انتقال و بازبینی کامل نشده |
| `auto_15` | ۷.۷ Automation (درس ۱۵ از ۲۰): Infrastructure as Code (IaC) در شبکه | انتقال و بازبینی کامل نشده |
| `auto_16` | ۷.۷ Automation (درس ۱۶ از ۲۰): CI/CD Pipeline برای تغییرات شبکه | انتقال و بازبینی کامل نشده |
| `auto_17` | ۷.۷ Automation (درس ۱۷ از ۲۰): کانتینرها و Docker در سرویس‌های شبکه | انتقال و بازبینی کامل نشده |
| `auto_18` | ۷.۷ Automation (درس ۱۸ از ۲۰): تست خودکار شبکه (pyATS / Genie / Batfish) | انتقال و بازبینی کامل نشده |
| `auto_19` | ۷.۷ Automation (درس ۱۹ از ۲۰): Streaming Telemetry و Grafana / ELK | انتقال و بازبینی کامل نشده |
| `auto_20` | ۷.۷ Automation (درس ۲۰ از ۲۰): AIOps و پروژه مدیریت شبکه ۵۰۰ شعبه‌ای | انتقال و بازبینی کامل نشده |
| `spec_cyber_hunt` | ۷.۸ Cybersecurity: Network Forensics، Threat Hunting و امنیت OT/Cloud | انتقال و بازبینی کامل نشده |
| `ccie_sec` | CCIE Security (350-701 SCOR + Lab 8 ساعته) | انتقال و بازبینی کامل نشده |
| `ccie_dc` | CCIE Data Center (350-601 DCCOR + Lab 8 ساعته) | انتقال و بازبینی کامل نشده |
| `ccie_sp` | CCIE Service Provider (350-501 SPCOR + Lab 8 ساعته) | انتقال و بازبینی کامل نشده |
| `ccie_wl` | CCIE Wireless (350-101 WLCOR + Lab 8 ساعته) | انتقال و بازبینی کامل نشده |
| `ccie_collab` | CCIE Collaboration (350-801 CLCOR + Lab 8 ساعته) | انتقال و بازبینی کامل نشده |
| `ccie_auto` | CCIE Automation (350-901 AUTOCOR + Lab 8 ساعته) | انتقال و بازبینی کامل نشده |
| `ccde_02` | موضوع ۲ CCDE: Enterprise Architecture (طراحی Campus، هسته و شعب) | انتقال و بازبینی کامل نشده |
| `ccde_03` | موضوع ۳ CCDE: Service Provider Architecture (طراحی شبکه اپراتورها) | انتقال و بازبینی کامل نشده |
| `ccde_04` | موضوع ۴ CCDE: Large Scale Network Design (طراحی شبکه‌های فوق‌بزرگ و AI Fabric) | انتقال و بازبینی کامل نشده |
| `ccde_05` | موضوع ۵ CCDE: Data Center Architecture (مراکز داده Active/Active و Spine-Leaf) | انتقال و بازبینی کامل نشده |
| `ccde_06` | موضوع ۶ CCDE: WAN Architecture (مقایسه MPLS، SD-WAN و اینترنت سازمانی) | انتقال و بازبینی کامل نشده |
| `ccde_07` | موضوع ۷ CCDE: Cloud Connectivity (معماری اتصال به ابرهای عمومی و Hybrid Cloud) | انتقال و بازبینی کامل نشده |
| `ccde_08` | موضوع ۸ CCDE: Network Segmentation (جداسازی VRF، SGT، Micro-Segmentation) | انتقال و بازبینی کامل نشده |
| `ccde_09` | موضوع ۹ CCDE: Resiliency Architecture (تاب‌آوری، Failure Domain و Blast Radius) | انتقال و بازبینی کامل نشده |
| `ccde_10` | موضوع ۱۰ CCDE: High Availability (طراحی N+1 و 2N بدون Single Point of Failure) | انتقال و بازبینی کامل نشده |
| `ccde_11` | موضوع ۱۱ CCDE: Capacity Planning (برآورد رشد ترافیک، پورت و توان ۵ ساله) | انتقال و بازبینی کامل نشده |
| `ccde_12` | موضوع ۱۲ CCDE: Scalability (مقیاس‌پذیری افقی بدون تغییر معماری هسته) | انتقال و بازبینی کامل نشده |
| `ccde_13` | موضوع ۱۳ CCDE: Traffic Engineering (کنترل مهندسی مسیرها در WAN و هسته) | انتقال و بازبینی کامل نشده |
| `ccde_14` | موضوع ۱۴ CCDE: Network Security Architecture (دفاع در عمق و Zero Trust کلان) | انتقال و بازبینی کامل نشده |
| `ccde_15` | موضوع ۱۵ CCDE: Business Requirements Analysis (ترجمه RPO/RTO و SLA به طرح فنی) | انتقال و بازبینی کامل نشده |
| `ccde_16` | موضوع ۱۶ CCDE: استراتژی مهاجرت بدون قطعی (Migration Strategy، Coexistence و MoP) | انتقال و بازبینی کامل نشده |
| `ccde_17` | موضوع ۱۷ CCDE: تحلیل موازنه فناوری و بهینه‌سازی هزینه (Trade-offs، CapEx/OpEx و TCO) | انتقال و بازبینی کامل نشده |
| `ccde_18` | موضوع ۱۸ CCDE: سناریوی جامع ۱ — طراحی شبکه سازمانی چندسایتی جهانی (Global Enterprise) | انتقال و بازبینی کامل نشده |
| `ccde_19` | موضوع ۱۹ CCDE: سناریوی جامع ۲ — طراحی شبکه اپراتور مخابراتی و 5G (Service Provider) | انتقال و بازبینی کامل نشده |
| `ccde_20` | موضوع ۲۰ CCDE: مستندسازی HLD/LLD، دفاع از طرح معماری و تله‌های آزمون 400-007 | انتقال و بازبینی کامل نشده |

## حداقل شواهد لازم برای بستن هر سطر

بازبینی هدف و متن، منابع و محدودیت پلتفرم؛ سنجش معنایی سؤال‌ها و توضیح پاسخ؛ بازطراحی و تعیین وضعیت اجرای آزمایشگاه؛ تطبیق با شناسه و renderer نهایی؛ آزمون آزمون/پیشرفت و parity آفلاین. این فهرست صرفاً برنامه است و انجام آن را تأیید نمی‌کند.

## پیشرفت محدود بعدی

پیش‌نویس آزمایشگاه `auto_12` در `01-خام-پروژه/academy-labs/terraform-draft-fa.md` و یک Python Mock مستقل در همان پوشه افزوده شده است. Mock با تست Python اجرا شده؛ Terraform واقعی یا تجهیزات اجرا نشده‌اند. این پیش‌نویس هنوز به داده‌ها یا رابط درس متصل نیست و بازبینی کامل درس محسوب نمی‌شود.

در رابط فعلی، وقتی bridge حساب وجود دارد، علامت‌گذاری درس و بخش دیگر کلیدهای localStorage مشترک حالت مستقل را نمی‌خواند یا بازنویسی نمی‌کند. در حالت بدون bridge، ذخیره مستقل قبلی در همان کلیدها باقی می‌ماند. داده‌های مشترکی که نسخه‌های قبلی قبلاً نوشته‌اند پاک نشده یا به حساب معینی نسبت داده نشده‌اند؛ برای بازیابی امن آنها همچنان راهکار مهاجرت با تعیین مالک لازم است. تست Node این گذار را شبیه‌سازی می‌کند و جایگزین آزمون خروج واقعی در مرورگر نیست.
