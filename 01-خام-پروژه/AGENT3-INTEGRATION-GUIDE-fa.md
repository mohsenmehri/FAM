# راهنمای ادغام محتوای ایجنت ۳ (Agent 3 Integration Guide — ۸۱ درس: ۶۴ اصلی + ۱۷ انتقالی کامل دسته‌های ۱۲A/۱۲B/۱۲C)

تاریخ تولید و اعتبارسنجی: **۲۰۲۶-۱۱-۲۷** | شاخه کاری: `arena/941b9e62-fam` | مبنای مقایسه قدیمی: `5a7474902c8d729950288198953686702cfd85dc` (و منبع خام ایجنت ۱ @ `641d02ee`)

## ۱. خلاصه دامنه و سیاست بدون تعارض (Zero-Conflict Scope)

- **تعداد دقیق درس‌های تحویلی ایجنت ۳ (تکمیل ۱۰۰٪):** **۸۱ درس** شامل ۶۴ درس اصلی (۶ Specialist پایه، ۱۲ Specialist عمیق، ۱۹ Automation به‌جز `auto_12`، ۷ CCIE و ۲۰ CCDE) + **تمام ۱۷ درس انتقالی سابق ایجنت ۱** (دسته ۱۲A: ۵ درس هسته CCNA + دسته ۱۲B: ۷ درس سرویس‌ها/امنیت/بی‌سیم/SDN CCNA + دسته ۱۲C: ۵ درس پیشرفته `adv_*`).
- **بدون دست‌کاری فایل‌های مشترک هسته:** فایل‌های مشترک `curriculum-catalog.json`، `lesson-engine.js`، `server/app.py` و `tests/test_academy_content.py` دست‌نخورده باقی مانده‌اند (`SHARED_FILES_TOUCHED=0`) و نسخه‌های محلی ادغام‌شده توسط Agent 2 روی `arena/ab96c97c-fam` بازنویسی نمی‌شوند.
- **استاندارد فنی هر ۶۴ درس:** قالب رسمی `fam-app-blueprint-v1`، حداقل **۱۴ بخش آموزشی فارسی** (با حداقل ۱ نمودار SVG معتبر XML دارای `viewBox`)، حداقل **۱۵ واژه تخصصی**، دقیقاً **۱۲ پرسش چهارگزینه‌ای با گزینه‌های یکتا و پاسخ تشریحی**، **اسکریپت آزمایشگاه مستقل Python 3 (stdlib-only)** به‌صورت Verbatim HTML-Escaped در `stages.lab.html` و فایل ثبت بازبینی معنایی اختصاصی.

## ۲. شفافیت وضعیت اجرا (تفکیک دقیق ۶۴ آزمایشگاه) و وضعیت بازبینی

- **مرز مشترک اجرا (`evidence: "Designed — Not Run"`):** تمام ۶۴ اسکریپت آزمایشگاهی موجود در `01-خام-پروژه/academy-labs/agent3/*_lab.py` به‌صورت محلی با Python 3 اجرا و آزمون شده‌اند (`exit code 0` و خروجی/Assert معتبر)، و **هیچ‌یک به روتر، سوئیچ، فایروال، کنترلر SDN، مخزن Remote تولیدی یا زیرساخت ابری واقعی متصل نمی‌شوند**. اما **همه ۶۴ آزمایشگاه صرفاً Mock درون‌حافظه‌ای نیستند**؛ وضعیت واقعی اجرای هر ۶۴ آزمایشگاه در ۴ دسته دقیق زیر تفکیک شده است (جزئیات هر فایل نیز در `stages.lab.executionStatus` و جدول کامل در `AGENT3-TECHNICAL-AUDIT-LOG-fa.md` ثبت است):
  1. **اجرای باینری خارجی واقعی در پوشه موقت ایزوله (۱ آزمایشگاه):** `auto_04_lab.py` (اجرای واقعی دستور `git` با `subprocess.run` شامل `init`، `config`، `add`، `commit`، `status`، `switch`، `revert` و `log` درون `tempfile.TemporaryDirectory` بدون دستکاری مخزن اصلی یا ریموت).
  2. **اجرای واقعی سرور/کلاینت HTTP روی Loopback `127.0.0.1` (۳ آزمایشگاه):** `auto_06_lab.py` (CRUD کامل REST)، `auto_09_lab.py` (شبیه‌ساز RESTCONF RFC 8040 روی HTTP واقعی محلی با `NoRedirectHandler`) و `auto_14_lab.py` (شبیه‌ساز API کنترلر با Pagination و `429 Retry-After` روی HTTP واقعی محلی).
  3. **اجرای واقعی عملیات سیستم‌عامل/فایل‌سیستم، رمزنگاری stdlib یا پارسر/اعتبارسنج واقعی روی داده نمونه (۷ آزمایشگاه):** `auto_01_lab.py` (ایجاد فایل و `os.chmod(0o600)`/`stat` در پوشه موقت + پارس لاگ)، `auto_02_lab.py` (نوشتن/خواندن واقعی JSON در پوشه موقت + پارس CLI)، `auto_05_lab.py` (پارسر واقعی `json` سخت‌گیرانه RFC 8259 با `parse_constant` و `object_pairs_hook` + پارسر واقعی XML با `ElementTree` + مدل تله YAML 1.1)، `auto_07_lab.py` (امضا و راستی‌آزمایی واقعی HMAC-SHA256 JWT با قفل `alg=HS256` و `exp` + تطبیق SAN)، `auto_10_lab.py` (اعتبارسنج محلی واقعی Regex/Schema برای زیرمجموعه YANG RFC 7950)، `auto_15_lab.py` (بررسی واقعی هم‌پوشانی ساب‌نت با `ipaddress.ip_network` + شبیه‌ساز IaC State/Drift) و `auto_19_lab.py` (بسته‌بندی باینری واقعی `struct.pack` در برابر JSON + شبیه‌ساز Hysteresis/MDT).
  4. **شبیه‌ساز / مدل‌ساز درون‌حافظه‌ای محلی / Local Mock در Python 3 stdlib (۵۳ آزمایشگاه):** شامل `auto_03` (با `ThreadPoolExecutor` واقعی روی Mock)، `auto_08`، `auto_11`، `auto_13`، `auto_16` (با `re` واقعی روی متن نمونه)، `auto_17`، `auto_18`، `auto_20`؛ تمام ۱۸ آزمایشگاه `spec_*` (شامل استفاده از `hashlib` در `spec_sec_vpn` و `statistics` در `spec_cyber`/`spec_cyber_hunt`)؛ تمام ۷ آزمایشگاه `ccie_*`؛ و تمام ۲۰ آزمایشگاه `ccde_*` (شامل استفاده از `ipaddress` در `ccde_02` و `ccde_07`).
- **وضعیت بازبینی معنایی:** همه ۶۴ درس توسط نویسنده (ایجنت) بازبینی معنایی و ممیزی در برابر نسخه قدیمی و استانداردها شده‌اند (`reviewer: "author-agent-self-review-not-independent"`) و گزارش آن در `01-خام-پروژه/academy-labs/reviews/<id>-review-fa.md` ثبت شده است. **بازبینی مستقل انسانی (Independent Human SME Review) هنوز انجام نشده است** و پیش از انتشار نهایی عمومی پیشنهاد می‌شود.

## ۳. فهرست کامل ۶۴ درس تحویلی ایجنت ۳ و نگاشت ادغام

### مسیر Specialist پایه (۶ درس)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `spec_ent` | تخصص Enterprise: IS-IS، اتصال Campus (SD-Access) به SD-WAN و معماری ۱۰۰ شعبه‌ای | `fam-specializations` / `spec-enterprise` | `/academy-assets/v5/blueprints/spec_ent.json` | `academy-labs/agent3/spec_ent_lab.py` | `academy-labs/reviews/spec_ent-review-fa.md` |
| `spec_sec` | تخصص امنیت: Cisco Secure Firewall (FTD)، ISE، 802.1X و معماری Zero Trust | `fam-specializations` / `spec-security` | `/academy-assets/v5/blueprints/spec_sec.json` | `academy-labs/agent3/spec_sec_lab.py` | `academy-labs/reviews/spec_sec-review-fa.md` |
| `spec_sp` | تخصص Service Provider: معماری P/PE/CE، MPLS L3VPN و مهندسی برچسب | `fam-specializations` / `spec-sp` | `/academy-assets/v5/blueprints/spec_sp.json` | `academy-labs/agent3/spec_sp_lab.py` | `academy-labs/reviews/spec_sp-review-fa.md` |
| `spec_wl` | تخصص Wireless: فیزیک RF (dBm/SNR)، تحول Wi-Fi 6/6E/7 و معماری Catalyst 9800 | `fam-specializations` / `spec-wireless` | `/academy-assets/v5/blueprints/spec_wl.json` | `academy-labs/agent3/spec_wl_lab.py` | `academy-labs/reviews/spec_wl-review-fa.md` |
| `spec_collab` | تخصص Collaboration & VoIP: پروتکل SIP، RTP، CUCM و طراحی Dial Plan | `fam-specializations` / `spec-collaboration` | `/academy-assets/v5/blueprints/spec_collab.json` | `academy-labs/agent3/spec_collab_lab.py` | `academy-labs/reviews/spec_collab-review-fa.md` |
| `spec_cyber` | تخصص Cybersecurity: راه‌اندازی SOC، SIEM، Incident Response و Threat Hunting | `fam-specializations` / `spec-cybersecurity` | `/academy-assets/v5/blueprints/spec_cyber.json` | `academy-labs/agent3/spec_cyber_lab.py` | `academy-labs/reviews/spec_cyber-review-fa.md` |

### مسیر Specialist عمیق (۱۲ درس)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `spec_ent_campus` | ۷.۱ Enterprise: طراحی Campus پیشرفته، StackWise Virtual (SVL) و پیشگیری از Split-Brain | `fam-specializations` / `spec-enterprise` | `/academy-assets/v5/blueprints/spec_ent_campus.json` | `academy-labs/agent3/spec_ent_campus_lab.py` | `academy-labs/reviews/spec_ent_campus-review-fa.md` |
| `spec_ent_sd` | ۷.۱ Enterprise: SD-WAN، Catalyst Center و معماری Zero-Touch برای ۱۰۰ شعبه | `fam-specializations` / `spec-enterprise` | `/academy-assets/v5/blueprints/spec_ent_sd.json` | `academy-labs/agent3/spec_ent_sd_lab.py` | `academy-labs/reviews/spec_ent_sd-review-fa.md` |
| `spec_sec_vpn` | ۷.۲ Security: Site-to-Site و Remote Access IPsec VPN با IKEv2 و VTI | `fam-specializations` / `spec-security` | `/academy-assets/v5/blueprints/spec_sec_vpn.json` | `academy-labs/agent3/spec_sec_vpn_lab.py` | `academy-labs/reviews/spec_sec_vpn-review-fa.md` |
| `spec_sec_ise` | ۷.۲ Security: معماری خوشه‌ای Cisco ISE، مدیریت دستگاه با TACACS+، Posture و pxGrid | `fam-specializations` / `spec-security` | `/academy-assets/v5/blueprints/spec_sec_ise.json` | `academy-labs/agent3/spec_sec_ise_lab.py` | `academy-labs/reviews/spec_sec_ise-review-fa.md` |
| `spec_dc_nx` | ۷.۳ Data Center: سیستم‌عامل Cisco NX-OS، معماری Nexus و vPC (Virtual Port Channel) | `fam-specializations` / `spec-datacenter` | `/academy-assets/v5/blueprints/spec_dc_nx.json` | `academy-labs/agent3/spec_dc_nx_lab.py` | `academy-labs/reviews/spec_dc_nx-review-fa.md` |
| `spec_dc_aci` | ۷.۳ Data Center: معماری Cisco ACI، کنترلر APIC، مدل EPG/Contract و Multi-Site | `fam-specializations` / `spec-datacenter` | `/academy-assets/v5/blueprints/spec_dc_aci.json` | `academy-labs/agent3/spec_dc_aci_lab.py` | `academy-labs/reviews/spec_dc_aci-review-fa.md` |
| `spec_dc_stor` | ۷.۳ Data Center: شبکه ذخیره‌سازی (SAN)، Fibre Channel، VSAN/Zoning، NPIV و FCoE | `fam-specializations` / `spec-datacenter` | `/academy-assets/v5/blueprints/spec_dc_stor.json` | `academy-labs/agent3/spec_dc_stor_lab.py` | `academy-labs/reviews/spec_dc_stor-review-fa.md` |
| `spec_sp_xr` | ۷.۴ Service Provider: سیستم‌عامل Cisco IOS-XR، مدل Two-Stage Commit و زبان RPL | `fam-specializations` / `spec-sp` | `/academy-assets/v5/blueprints/spec_sp_xr.json` | `academy-labs/agent3/spec_sp_xr_lab.py` | `academy-labs/reviews/spec_sp_xr-review-fa.md` |
| `spec_sp_sr` | ۷.۴ Service Provider: معماری Segment Routing (SR-MPLS / SRv6)، SR-TE و TI-LFA | `fam-specializations` / `spec-sp` | `/academy-assets/v5/blueprints/spec_sp_sr.json` | `academy-labs/agent3/spec_sp_sr_lab.py` | `academy-labs/reviews/spec_sp_sr-review-fa.md` |
| `spec_wl_survey` | ۷.۵ Wireless: مهندسی Site Survey بی‌سیم، بودجه لینک RF، طراحی کانال و تحلیل طیف | `fam-specializations` / `spec-wireless` | `/academy-assets/v5/blueprints/spec_wl_survey.json` | `academy-labs/agent3/spec_wl_survey_lab.py` | `academy-labs/reviews/spec_wl_survey-review-fa.md` |
| `spec_collab_gw` | ۷.۶ Collaboration: دروازه‌های صوتی (Voice Gateways)، Cisco CUBE (SBC)، Dial-Peer و SRST | `fam-specializations` / `spec-collab` | `/academy-assets/v5/blueprints/spec_collab_gw.json` | `academy-labs/agent3/spec_collab_gw_lab.py` | `academy-labs/reviews/spec_collab_gw-review-fa.md` |
| `spec_cyber_hunt` | ۷.۷ CyberOps: شکار پیش‌فعال تهدید (Threat Hunting)، ماتریس MITRE ATT&CK، تله‌متری و شکار LOLBins | `fam-specializations` / `spec-cyberops` | `/academy-assets/v5/blueprints/spec_cyber_hunt.json` | `academy-labs/agent3/spec_cyber_hunt_lab.py` | `academy-labs/reviews/spec_cyber_hunt-review-fa.md` |

### مسیر Automation و DevNet به جز auto_12 (۱۹ درس)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `auto_01` | ۷.۷ Automation (درس ۱ از ۲۰): Linux پیش‌نیاز مهندس شبکه | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_01.json` | `academy-labs/agent3/auto_01_lab.py` | `academy-labs/reviews/auto_01-review-fa.md` |
| `auto_02` | ۷.۷ Automation (درس ۲ از ۲۰): Python مقدماتی برای شبکه | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_02.json` | `academy-labs/agent3/auto_02_lab.py` | `academy-labs/reviews/auto_02-review-fa.md` |
| `auto_03` | ۷.۷ Automation (درس ۳ از ۲۰): Python پیشرفته (Netmiko، Paramiko، Nornir) | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_03.json` | `academy-labs/agent3/auto_03_lab.py` | `academy-labs/reviews/auto_03-review-fa.md` |
| `auto_04` | ۷.۷ Automation (درس ۴ از ۲۰): کنترل نسخه با Git و GitHub | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_04.json` | `academy-labs/agent3/auto_04_lab.py` | `academy-labs/reviews/auto_04-review-fa.md` |
| `auto_05` | ۷.۷ Automation (درس ۵ از ۲۰): ساختارهای داده JSON و YAML | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_05.json` | `academy-labs/agent3/auto_05_lab.py` | `academy-labs/reviews/auto_05-review-fa.md` |
| `auto_06` | ۷.۷ Automation (درس ۶ از ۲۰): مبانی REST API و Postman | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_06.json` | `academy-labs/agent3/auto_06_lab.py` | `academy-labs/reviews/auto_06-review-fa.md` |
| `auto_07` | ۷.۷ Automation (درس ۷ از ۲۰): پروتکل HTTP و HTTPS در برنامه‌نویسی شبکه | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_07.json` | `academy-labs/agent3/auto_07_lab.py` | `academy-labs/reviews/auto_07-review-fa.md` |
| `auto_08` | ۷.۷ Automation (درس ۸ از ۲۰): پروتکل NETCONF | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_08.json` | `academy-labs/agent3/auto_08_lab.py` | `academy-labs/reviews/auto_08-review-fa.md` |
| `auto_09` | ۷.۷ Automation (درس ۹ از ۲۰): پروتکل RESTCONF | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_09.json` | `academy-labs/agent3/auto_09_lab.py` | `academy-labs/reviews/auto_09-review-fa.md` |
| `auto_10` | ۷.۷ Automation (درس ۱۰ از ۲۰): زبان مدل‌سازی داده YANG | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_10.json` | `academy-labs/agent3/auto_10_lab.py` | `academy-labs/reviews/auto_10-review-fa.md` |
| `auto_11` | ۷.۷ Automation (درس ۱۱ از ۲۰): اتوماسیون با Ansible (Playbook & Inventory) | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_11.json` | `academy-labs/agent3/auto_11_lab.py` | `academy-labs/reviews/auto_11-review-fa.md` |
| `auto_13` | ۷.۷ Automation (درس ۱۳ از ۲۰): Cisco NSO (Network Services Orchestrator) | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_13.json` | `academy-labs/agent3/auto_13_lab.py` | `academy-labs/reviews/auto_13-review-fa.md` |
| `auto_14` | ۷.۷ Automation (درس ۱۴ از ۲۰): اکوسیستم Cisco DevNet و SDKها | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_14.json` | `academy-labs/agent3/auto_14_lab.py` | `academy-labs/reviews/auto_14-review-fa.md` |
| `auto_15` | ۷.۷ Automation (درس ۱۵ از ۲۰): Infrastructure as Code (IaC) در شبکه | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_15.json` | `academy-labs/agent3/auto_15_lab.py` | `academy-labs/reviews/auto_15-review-fa.md` |
| `auto_16` | ۷.۷ Automation (درس ۱۶ از ۲۰): CI/CD Pipeline برای تغییرات شبکه | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_16.json` | `academy-labs/agent3/auto_16_lab.py` | `academy-labs/reviews/auto_16-review-fa.md` |
| `auto_17` | ۷.۷ Automation (درس ۱۷ از ۲۰): کانتینرها و Docker در سرویس‌های شبکه | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_17.json` | `academy-labs/agent3/auto_17_lab.py` | `academy-labs/reviews/auto_17-review-fa.md` |
| `auto_18` | ۷.۷ Automation (درس ۱۸ از ۲۰): تست خودکار شبکه (pyATS / Genie / Batfish) | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_18.json` | `academy-labs/agent3/auto_18_lab.py` | `academy-labs/reviews/auto_18-review-fa.md` |
| `auto_19` | ۷.۷ Automation (درس ۱۹ از ۲۰): Streaming Telemetry و Grafana / ELK | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_19.json` | `academy-labs/agent3/auto_19_lab.py` | `academy-labs/reviews/auto_19-review-fa.md` |
| `auto_20` | ۷.۷ Automation (درس ۲۰ از ۲۰): AIOps و پروژه مدیریت شبکه ۵۰۰ شعبه‌ای | `fam-automation` / `automation-foundations` | `/academy-assets/v5/blueprints/auto_20.json` | `academy-labs/agent3/auto_20_lab.py` | `academy-labs/reviews/auto_20-review-fa.md` |

### مسیر CCIE (۷ درس)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `ccie_01` | ۸.۱ CCIE Enterprise Infrastructure: کالبدشکافی لب ۸ساعته v1.1، تله‌های فنی و نقشه ۲۰۰ سناریو | `fam-ccie` / `ccie-ei` | `/academy-assets/v5/blueprints/ccie_01.json` | `academy-labs/agent3/ccie_01_lab.py` | `academy-labs/reviews/ccie_01-review-fa.md` |
| `ccie_sec` | ۸.۲ CCIE Security: معماری دفاع لایه‌دار (v6.1)، هم‌افزایی ISE/FTD/PKI و روش دیباگ لب ۸ساعته | `fam-ccie` / `ccie-security` | `/academy-assets/v5/blueprints/ccie_sec.json` | `academy-labs/agent3/ccie_sec_lab.py` | `academy-labs/reviews/ccie_sec-review-fa.md` |
| `ccie_dc` | ۸.۳ CCIE Data Center: پنج ستون لب ۸ساعته v3.1 (ACI، VXLAN EVPN، MDS SAN، UCS و اتوماسیون) | `fam-ccie` / `ccie-dc` | `/academy-assets/v5/blueprints/ccie_dc.json` | `academy-labs/agent3/ccie_dc_lab.py` | `academy-labs/reviews/ccie_dc-review-fa.md` |
| `ccie_sp` | ۸.۴ CCIE Service Provider: مقیاس‌پذیری هسته، Inter-AS VPN، EVPN و دیباگ لایه‌به‌لایه IOS-XR | `fam-ccie` / `ccie-sp` | `/academy-assets/v5/blueprints/ccie_sp.json` | `academy-labs/agent3/ccie_sp_lab.py` | `academy-labs/reviews/ccie_sp-review-fa.md` |
| `ccie_wl` | ۸.۵ CCIE Enterprise Wireless: معماری ۳تگی Catalyst 9800، RadioActive Tracing و QoS بی‌سیم | `fam-ccie` / `ccie-wireless` | `/academy-assets/v5/blueprints/ccie_wl.json` | `academy-labs/agent3/ccie_wl_lab.py` | `academy-labs/reviews/ccie_wl-review-fa.md` |
| `ccie_collab` | ۸.۶ CCIE Collaboration: معماری یکپارچه CUCM/CUBE/Expressway (v3.1) و جراحی پیام‌های SIP | `fam-ccie` / `ccie-collab` | `/academy-assets/v5/blueprints/ccie_collab.json` | `academy-labs/agent3/ccie_collab_lab.py` | `academy-labs/reviews/ccie_collab-review-fa.md` |
| `ccie_auto` | ۸.۷ CCIE Automation (DevNet Expert): تحویل Idempotent و Atomic با Cisco NSO، GitOps، YANG و pyATS | `fam-ccie` / `ccie-auto` | `/academy-assets/v5/blueprints/ccie_auto.json` | `academy-labs/agent3/ccie_auto_lab.py` | `academy-labs/reviews/ccie_auto-review-fa.md` |

### مسیر CCDE (۲۰ درس)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `ccde_01` | ۹.۱ CCDE — مبانی معماری شبکه و تفکر کلان معمار (400-007) | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_01.json` | `academy-labs/agent3/ccde_01_lab.py` | `academy-labs/reviews/ccde_01-review-fa.md` |
| `ccde_02` | ۹.۲ CCDE — معماری سازمانی (Enterprise Composite): طراحی Campus، هسته و پروفایل شعب | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_02.json` | `academy-labs/agent3/ccde_02_lab.py` | `academy-labs/reviews/ccde_02-review-fa.md` |
| `ccde_03` | ۹.۳ CCDE — معماری شبکه‌های اپراتوری (Service Provider): اقتصاد Peering/Transit و هسته مقیاس‌پذیر | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_03.json` | `academy-labs/agent3/ccde_03_lab.py` | `academy-labs/reviews/ccde_03-review-fa.md` |
| `ccde_04` | ۹.۴ CCDE — طراحی شبکه‌های فوق‌بزرگ (Large Scale)، ۵-Stage Clos و AI/ML Fabric (RoCEv2) | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_04.json` | `academy-labs/agent3/ccde_04_lab.py` | `academy-labs/reviews/ccde_04-review-fa.md` |
| `ccde_05` | ۹.۵ CCDE — معماری دیتاسنتر و DCI: Active/Active در برابر DR، فیزیک فیبر و معمای کشش لایه ۲ | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_05.json` | `academy-labs/agent3/ccde_05_lab.py` | `academy-labs/reviews/ccde_05-review-fa.md` |
| `ccde_06` | ۹.۶ CCDE — معماری شبکه‌های گسترده (WAN): MPLS، اینترنت، Hybrid SD-WAN و SASE | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_06.json` | `academy-labs/agent3/ccde_06_lab.py` | `academy-labs/reviews/ccde_06-review-fa.md` |
| `ccde_07` | ۹.۷ CCDE — معماری اتصال ابری و چندابری (Cloud Connectivity): Colo Hub، Direct Connect و ۳ تله کلاسیک | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_07.json` | `academy-labs/agent3/ccde_07_lab.py` | `academy-labs/reviews/ccde_07-review-fa.md` |
| `ccde_08` | ۹.۸ CCDE — معماری سگمنتاسیون شبکه: کلان‌جداسازی (VRF)، ریزجداسازی (SGT/EPG) و تله Over-Segmentation | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_08.json` | `academy-labs/agent3/ccde_08_lab.py` | `academy-labs/reviews/ccde_08-review-fa.md` |
| `ccde_09` | ۹.۹ CCDE — معماری تاب‌آوری (Resiliency): ۵ لایه آسیب‌پذیری، شعاع انفجار و موازنه همگرایی سریع در برابر پایداری | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_09.json` | `academy-labs/agent3/ccde_09_lab.py` | `academy-labs/reviews/ccde_09-review-fa.md` |
| `ccde_10` | ۹.۱۰ CCDE — معماری دسترس‌پذیری بالا (High Availability): ریاضی سری/موازی، N+1 در برابر 2N و Multi-Box HA | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_10.json` | `academy-labs/agent3/ccde_10_lab.py` | `academy-labs/reviews/ccde_10-review-fa.md` |
| `ccde_11` | ۹.۱۱ CCDE — برنامه‌ریزی ظرفیت (Capacity Planning): ۵ بُعد پنهان فراتر از Gbps و فرمول رشد مرکب ۵ساله | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_11.json` | `academy-labs/agent3/ccde_11_lab.py` | `academy-labs/reviews/ccde_11-review-fa.md` |
| `ccde_12` | ۹.۱۲ CCDE — معماری مقیاس‌پذیری (Scalability): ۴ دیوار مقیاس، Scale-Out افقی و سلسله‌مراتب | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_12.json` | `academy-labs/agent3/ccde_12_lab.py` | `academy-labs/reviews/ccde_12-review-fa.md` |
| `ccde_13` | ۹.۱۳ CCDE — مهندسی ترافیک (Traffic Engineering): ۴ سطح TE، SR-TE/Flex-Algo و تله ناپایداری پس از خرابی | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_13.json` | `academy-labs/agent3/ccde_13_lab.py` | `academy-labs/reviews/ccde_13-review-fa.md` |
| `ccde_14` | ۹.۱۴ CCDE — معماری امنیت شبکه: دفاع در عمق، Zero Trust و مهار گلوگاه فایروال شرق-غرب | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_14.json` | `academy-labs/agent3/ccde_14_lab.py` | `academy-labs/reviews/ccde_14-review-fa.md` |
| `ccde_15` | ۹.۱۵ CCDE — تحلیل نیازمندی‌های تجاری (Business Requirements): RPO/RTO، محدودیت‌ها و Compliance | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_15.json` | `academy-labs/agent3/ccde_15_lab.py` | `academy-labs/reviews/ccde_15-review-fa.md` |
| `ccde_16` | ۹.۱۶ CCDE — راهبرد مهاجرت بدون قطعی (Migration Strategy): هم‌زیستی، Ships-in-the-Night و MoP چهارستونه | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_16.json` | `academy-labs/agent3/ccde_16_lab.py` | `academy-labs/reviews/ccde_16-review-fa.md` |
| `ccde_17` | ۹.۱۷ CCDE — موازنه فناوری‌ها و بهینه‌سازی هزینه (Technology Trade-Offs &amp; 5-Year TCO) | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_17.json` | `academy-labs/agent3/ccde_17_lab.py` | `academy-labs/reviews/ccde_17-review-fa.md` |
| `ccde_18` | ۹.۱۸ CCDE — مطالعه موردی جامع ۱: معماری سازمان جهانی چندسایتی (شرکت Pars-Global) | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_18.json` | `academy-labs/agent3/ccde_18_lab.py` | `academy-labs/reviews/ccde_18-review-fa.md` |
| `ccde_19` | ۹.۱۹ CCDE — مطالعه موردی جامع ۲: نوسازی اپراتور مخابراتی و ۵G (شرکت Aria-Telecom) | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_19.json` | `academy-labs/agent3/ccde_19_lab.py` | `academy-labs/reviews/ccde_19-review-fa.md` |
| `ccde_20` | ۹.۲۰ CCDE — مستندسازی HLD/LLD، دفاع از معماری، تله‌های آزمون 400-007 و جمع‌بندی نهایی آکادمی فام | `fam-ccde` / `ccde-design` | `/academy-assets/v5/blueprints/ccde_20.json` | `academy-labs/agent3/ccde_20_lab.py` | `academy-labs/reviews/ccde_20-review-fa.md` |

### مسیر CCNA v1.1 انتقالی (دسته ۱۲A — ۵ درس از ۱۷ درس سابق ایجنت ۱)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `ccna_02_vlan` | CCNA (سوئیچینگ): VLANها، Trunk 802.1Q، Voice VLAN و Native VLAN (بازبینی و رفع تناقض) | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_02_vlan.json` | `academy-labs/agent3/ccna_02_vlan_lab.py` | `academy-labs/reviews/ccna_02_vlan-review-fa.md` |
| `ccna_v1` | CCNA (معماری): مجازی‌سازی سرور، Hypervisor (Type 1/2)، کانتینرها و سوئیچ‌های مجازی | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_v1.json` | `academy-labs/agent3/ccna_v1_lab.py` | `academy-labs/reviews/ccna_v1-review-fa.md` |
| `ccna_v6` | CCNA (مسیریابی): مسیریابی Dual-Stack IPv4 و IPv6، Longest Prefix Match، AD/Metric و OSPFv3 | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_v6.json` | `academy-labs/agent3/ccna_v6_lab.py` | `academy-labs/reviews/ccna_v6-review-fa.md` |
| `ccna_03` | CCNA (مسیریابی): Static، Default، Floating Static و OSPF Single-Area (Area 0) | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_03.json` | `academy-labs/agent3/ccna_03_lab.py` | `academy-labs/reviews/ccna_03-review-fa.md` |
| `ccna_04` | CCNA (سرویس‌های IP): افزونگی دروازه HSRP، همگام‌سازی NTP، ثبت وقایع Syslog و پایش SNMPv3 | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_04.json` | `academy-labs/agent3/ccna_04_lab.py` | `academy-labs/reviews/ccna_04-review-fa.md` |

### مسیر CCNA v1.1 انتقالی (دسته ۱۲B — ۷ درس سرویس‌ها، امنیت، بی‌سیم و SDN)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `ccna_dhcp` | CCNA (سرویس‌های IP): سرور DHCP، عامل بازپخش DHCP Relay (giaddr)، APIPA و DNS | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_dhcp.json` | `academy-labs/agent3/ccna_dhcp_lab.py` | `academy-labs/reviews/ccna_dhcp-review-fa.md` |
| `ccna_nat` | CCNA (سرویس‌های IP): Static NAT، Dynamic NAT، PAT (NAT Overload) و ترتیب پردازش بسته | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_nat.json` | `academy-labs/agent3/ccna_nat_lab.py` | `academy-labs/reviews/ccna_nat-review-fa.md` |
| `ccna_05` | CCNA (امنیت شبکه): فهرست‌های دسترسی ACL، Port Security، DHCP Snooping، DAI و STP Guards | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_05.json` | `academy-labs/agent3/ccna_05_lab.py` | `academy-labs/reviews/ccna_05-review-fa.md` |
| `ccna_acl` | CCNA (امنیت شبکه): چشم‌انداز تهدیدات، AAA (TACACS+ و RADIUS)، VPN مقدماتی و Hardening تجهیزات | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_acl.json` | `academy-labs/agent3/ccna_acl_lab.py` | `academy-labs/reviews/ccna_acl-review-fa.md` |
| `ccna_qos_ssh` | CCNA (سرویس‌های IP و مدیریت): مبانی QoS (DiffServ/DSCP/LLQ)، مدیریت امن SSHv2 و انتقال فایل (TFTP/FTP/SCP) | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_qos_ssh.json` | `academy-labs/agent3/ccna_qos_ssh_lab.py` | `academy-labs/reviews/ccna_qos_ssh-review-fa.md` |
| `ccna_wl` | CCNA (شبکه‌های بی‌سیم): مبانی Wi-Fi، کانال‌های RF، معماری AP/WLC (CAPWAP) و امنیت WPA2/WPA3 | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_wl.json` | `academy-labs/agent3/ccna_wl_lab.py` | `academy-labs/reviews/ccna_wl-review-fa.md` |
| `ccna_06` | CCNA (اتوماسیون و برنامه‌پذیری): معماری SDN، Cisco Catalyst Center، REST API و ابزارهای Ansible/Puppet/Chef | `fam-c5` / `c5-ccna-v11-transfer` | `/academy-assets/v5/blueprints/ccna_06.json` | `academy-labs/agent3/ccna_06_lab.py` | `academy-labs/reviews/ccna_06-review-fa.md` |

### مسیر پیشرفته انتقالی (دسته ۱۲C — ۵ درس `adv_*` سابق ایجنت ۱)

| شناسه | عنوان فارسی | مسیر / دوره پیشنهادی | Blueprint | Lab Script | گزارش بازبینی |
|---|---|---|---|---|---|
| `adv_01` | سوئیچینگ پیشرفته (Advanced Switching): MST (802.1s)، مکانیزم‌های Guard، تله BPDU Filter، UDLD و StackWise/SVL | `fam-advanced` / `adv-switching-routing` | `/academy-assets/v5/blueprints/adv_01.json` | `academy-labs/agent3/adv_01_lab.py` | `academy-labs/reviews/adv_01-review-fa.md` |
| `adv_02` | مسیریابی پیشرفته (Advanced Routing): OSPF Multi-Area، انواع LSA (۱ تا ۷)، نواحی Stub/NSSA و خلاصه‌سازی | `fam-advanced` / `adv-switching-routing` | `/academy-assets/v5/blueprints/adv_02.json` | `academy-labs/agent3/adv_02_lab.py` | `academy-labs/reviews/adv_02-review-fa.md` |
| `adv_03` | سرویس‌های پیشرفته (Advanced Services): جداسازی لایه ۳ با VRF-Lite، پایش فعال IP SLA + Track و NetFlow | `fam-advanced` / `adv-switching-routing` | `/academy-assets/v5/blueprints/adv_03.json` | `academy-labs/agent3/adv_03_lab.py` | `academy-labs/reviews/adv_03-review-fa.md` |
| `adv_04` | عیب‌یابی پیشرفته (Advanced Troubleshooting): تفکیک Control/Data Plane (CEF)، تله MTU/MSS و Asymmetric Routing | `fam-advanced` / `adv-switching-routing` | `/academy-assets/v5/blueprints/adv_04.json` | `academy-labs/agent3/adv_04_lab.py` | `academy-labs/reviews/adv_04-review-fa.md` |
| `adv_bfd` | همگرایی میلی‌ثانیه‌ای و تله‌متری پیشرفته: پروتکل BFD (RFC 5880) و Flexible NetFlow (v9 / IPFIX) | `fam-advanced` / `adv-switching-routing` | `/academy-assets/v5/blueprints/adv_bfd.json` | `academy-labs/agent3/adv_bfd_lab.py` | `academy-labs/reviews/adv_bfd-review-fa.md` |

**جمع کل درس‌های احصاشده و تاییدشده:** `81` درس (`64` اصلی + `17` انتقالی کامل دسته‌های ۱۲A، ۱۲B و ۱۲C).

## ۴. خلاصه مهم‌ترین اصلاحات ممیزی نسخه قدیمی (Legacy Audit Fixes)

در بازنویسی ۶۴ درس نسبت به فایل قدیمی `academy-data.json` (کمیت `5a747490`)، علاوه بر ارتقای عمیق محتوا (از ۱–۳ پرسش و چند پاراگراف کوتاه به ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش، SVG و آزمایشگاه اجرایی Python)، تمام خطاهای علمی و نگارشی شناسایی‌شده پاکسازی و در `meta.legacyAuditFixes` هر درس ثبت شدند؛ از جمله:

- **`spec_cyber`:** اصلاح ناهماهنگی شمارش مراحل NIST 800-61 در نسخه قدیمی و به‌روزرسانی دقیق به **NIST SP 800-61 Rev. 3 (۲۰۲۵)** هم‌راستا با CSF 2.0 (Govern, Identify, Protect, Detect, Respond, Recover).
- **`spec_cyber_hunt`:** اصلاح عبارات غلط تایپی نسخه قدیمی (`تلgern`، `شوائع`).
- **`auto_01` تا `auto_20` (به‌جز `auto_12`):** پاکسازی خطاهای نگارشی (`politicaها`، `استخراجدرس`، `چهخروجیی`، `عمولاتی`)، تفکیک شفاف شبیه‌ساز محلی از تجهیزات/پلتفرم‌های واقعی و افزودن استانداردهای روز (RESTCONF، gNMI/YANG، pyATS/Batfish، CI/CD GitOps، NetBox Source of Truth).
- **`ccde_02`، `ccde_04`، `ccde_05`، `ccde_08`، `ccde_10`، `ccde_13`، `ccde_17`:** پاکسازی تمام واژگان درهم‌ریخته و غلط تایپی نسخه قدیمی (`مرزهای camino`، `کابل‌های فیبرpath`، `سبین-لیف`، `سه تاقا یکسان هستند`، `هماً یک الشيء هستند`، `مسیریابی مبتنی بر یتیک`، `n preservation`) و تکمیل هر ۲۰ درس CCDE همراه با دو مطالعه موردی کامل **Pars-Global (`ccde_18`)** و **Aria-Telecom (`ccde_19`)**.

## ۵. گام‌های ادغام نهایی در `curriculum-catalog.json` پس از Merge هر ۳ ایجنت

برای فعال‌سازی هر ۶۴ درس در کاتالوگ رابط کاربری پس از ادغام شاخه‌های ایجنت ۱، ۲ و ۳:

1. در `01-خام-پروژه/server/www/academy-assets/v5/curriculum-catalog.json`، مسیرهای زیر را (در صورت نبود) تعریف یا تکمیل کنید:
   - `fam-specialist` (شامل دوره‌های `spec-core` و `spec-deep`)
   - `fam-automation` (شامل دوره `net-auto` همراه با `auto_12` از ایجنت ۲)
   - `fam-ccie` (شامل دوره `ccie-mastery`)
   - `fam-ccde` (شامل دوره `ccde-design`)
2. برای هر شناسه در جدول بخش ۳، آبجکت متناظر با `blueprint: "/academy-assets/v5/blueprints/<id>.json"` را به کاتالوگ اضافه کنید (نمونه ساختار زیر):

```json
{
  "id": "spec_ent",
  "title": "تخصص Enterprise: IS-IS، اتصال Campus (SD-Access) به SD-WAN و معماری ۱۰۰ شعبه‌ای",
  "path": "fam-specializations",
  "course": "spec-enterprise",
  "blueprint": "/academy-assets/v5/blueprints/spec_ent.json",
  "estimatedMinutes": 55
}
```

3. **حفظ داده‌های پیشرفت کاربران:** شناسه‌های جدید (`spec_*`، `auto_*`، `ccie_*`، `ccde_*`) هیچ هم‌پوشانی با ۱۳ شناسه فعال پایه (`academy-stage-zero-*` و `ccna-v11-*`) ندارند، بنابراین پیشرفت کاربران فعلی بدون تخریب حفظ می‌شود.

## ۶. دستورات اعتبارسنجی خودکار و گزارش ممیزی فنی مراحل ۲ و ۳ (Verification & Technical Audit)

- گزارش کامل ممیزی فنی و معنایی مراحل ۲ و ۳ (شامل جدول تفکیک وضعیت واقعی اجرای تک‌تک ۶۴ آزمایشگاه، اصلاحات عمیق فنی و معنایی روی ۲۶ درس متمایز، ارتقای ۱۱ آزمایشگاه متمایز و مستندسازی منابع رسمی و آزمون‌های واحد/رگرسیون برای هر اصلاح) در فایل [`AGENT3-TECHNICAL-AUDIT-LOG-fa.md`](AGENT3-TECHNICAL-AUDIT-LOG-fa.md) ثبت شده است.

```bash
# ۱. اعتبارسنجی کاتالوگ فعلی main (بدون شکستن هیچ آزمون موجود)
python3 -m unittest 01-خام-پروژه/tests/test_academy_content.py -v

# ۲. اعتبارسنجی جامع تمام ۶۴ blueprint، نمودارهای SVG، آزمون‌ها، گزارش‌های بازبینی و اجرای زنده تمام ۶۴ آزمایشگاه Python ایجنت ۳
python3 -m unittest 01-خام-پروژه/tests/test_agent3_content.py -v
```
