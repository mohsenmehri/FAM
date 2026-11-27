# Agent 1 Lesson Transfer Manifest

**SHA:** c31fc9e54c0cce21e6e4f45b9f7c1b30919ea763
**Branch:** arena/96a73266-fam
**Total lessons:** 35
**Date:** 2026-11-23

## Review Summary
- **Lessons reviewed (deep technical):** 35/35
- **Lessons modified (content):** 0 (all technically correct)
- **Errors found:** 0
- **labType assigned:** All 35 = 'Reference'

## Evidence Files
- Directory: `agent1_evidence/`
- Format: `{id}_full_review.json` + `{id}_review_evidence.md` per lesson
- Test file: `01-خام-پروژه/tests/test_agent1_rewrites.py` (8 tests)

## Transfer Groups

### Group A - adv_* (Advanced Switching/Routing)
- **Count:** 12
- **Lesson IDs:** adv_01, adv_02, adv_03, adv_04, adv_bfd, adv_bgp, adv_ec, adv_eigrp, adv_mcast, adv_pvl, adv_qos, adv_redist
- **Group SHA:** 259eb9df6d05344a59b1e3f83f2f5dd4224a45bd2e29b327fd4eb33db30f0052

  - `adv_01`: Advanced Switching: MST، Guardهای STP، UDLD و StackWise
  - `adv_02`: Advanced Routing: OSPF Multi-Area، انواع LSA و Stub / NSSA
  - `adv_03`: سرویس‌های پیشرفته: VRF-Lite، IP SLA و پایش ترافیک با NetFlow
  - `adv_04`: عیب‌یابی سیستماتیک پیشرفته: Control/Data Plane، MTU/MSS و As
  - `adv_bfd`: پروتکل BFD (کشف خرابی میلی‌ثانیه‌ای) و Flexible NetFlow
  - `adv_bgp`: مبانی BGP، همسایگی eBGP/iBGP، Route Reflector و Path Selecti
  - `adv_ec`: Advanced EtherChannel، L3 Port-Channel و مقایسهٔ HSRP / VRRP
  - `adv_eigrp`: پروتکل EIGRP: Metric ترکیبی، الگوریتم DUAL و Stub
  - `adv_mcast`: مبانی Multicast: آدرس‌دهی گروهی، IGMP Snooping و PIM Sparse 
  - `adv_pvl`: Private VLAN، Voice VLAN و بهینه‌سازی VLAN Pruning
  - `adv_qos`: کیفیت سرویس (QoS): MQC، PHB/DSCP، Token Bucket و WRED
  - `adv_redist`: Route Redistribution، Prefix-List، Route-Map و جلوگیری از Ro

### Group B - ccna_* (CCNA Level)
- **Count:** 12
- **Lesson IDs:** ccna_02_vlan, ccna_03, ccna_04, ccna_05, ccna_06, ccna_acl, ccna_dhcp, ccna_nat, ccna_qos_ssh, ccna_v1, ccna_v6, ccna_wl
- **Group SHA:** f7782a7c683dd1daa1368d7d08bfec6d047f216cf52963670416ff0afe1df9eb

  - `ccna_02_vlan`: VLAN، پورت‌های Access و Trunk و Native VLAN: جداسازی یک سوئی
  - `ccna_03`: مسیریابی Static، Default، Floating Static و OSPF Single-Area
  - `ccna_04`: سرویس‌های زیرساخت IP: HSRP، NTP، Syslog و SNMP
  - `ccna_05`: امنیت شبکه سیسکو: ACL، Port Security، DHCP Snooping و DAI
  - `ccna_06`: معماری SDN، Cisco Catalyst Center، REST API و اتوماسیون شبکه
  - `ccna_acl`: تهدیدات امنیتی، AAA (TACACS+ / RADIUS)، VPN مقدماتی و Harden
  - `ccna_dhcp`: سرویس‌های DHCP Server، DHCP Relay (ip helper-address) و DNS
  - `ccna_nat`: پیاده‌سازی Static NAT، Dynamic NAT و PAT (NAT Overload)
  - `ccna_qos_ssh`: مبانی QoS، مدیریت امن SSH و انتقال فایل (FTP/TFTP/SCP)
  - `ccna_v1`: مفاهیم Virtualization، Cloud و مقایسه On-Premises با ابری
  - `ccna_v6`: مسیریابی IPv4 و IPv6، Longest Prefix Match و Metric/AD
  - `ccna_wl`: مبانی Wireless LAN، معماری AP/WLC و پیکربندی WLAN پایه

### Group C - ccnp_* (CCNP Level)
- **Count:** 11
- **Lesson IDs:** ccnp_01, ccnp_02, ccnp_enauto, ccnp_enc_arch, ccnp_enc_auto, ccnp_enc_inf, ccnp_enc_sec, ccnp_encc, ccnp_enna, ccnp_ensdwi, ccnp_ensld
- **Group SHA:** 8ec7939aec6be04e8f08c885cb94589409523674a66dde2998b8067bd3cc5518

  - `ccnp_01`: 350-401 ENCOR: مجازی‌سازی (GRE/IPsec/LISP/VXLAN) و Assurance
  - `ccnp_02`: 300-410 ENARSI: مسیریابی سیاستی (PBR)، DMVPN و MPLS L3VPN
  - `ccnp_enauto`: تخصصی 300-435 ENAUTO: مدل‌های YANG، NETCONF/RESTCONF و API پ
  - `ccnp_enc_arch`: ENCOR حوزه ۱: معماری Enterprise، سخت‌افزار CEF/TCAM، SD-Acce
  - `ccnp_enc_auto`: ENCOR حوزه ۶: اتوماسیون در CCNP (JSON، YANG، NETCONF/RESTCON
  - `ccnp_enc_inf`: ENCOR حوزه ۳: زیرساخت L2/L3 (نوع شبکه OSPF، eBGP و Wireless 
  - `ccnp_enc_sec`: ENCOR حوزه ۵: امنیت زیرساخت (CoPP با MQC، AAA/ACL و امنیت RE
  - `ccnp_encc`: تخصصی 300-440 ENCC: معماری اتصال امن و مقیاس‌پذیر به Cloud (
  - `ccnp_enna`: تخصصی 300-445 ENNA: تضمین کیفیت شبکه با ThousandEyes و Catal
  - `ccnp_ensdwi`: تخصصی 300-415 ENSDWI: معماری Cisco Catalyst SD-WAN (OMP، TLO
  - `ccnp_ensld`: تخصصی 300-420 ENSLD: طراحی شبکهٔ سازمانی (Oversubscription، 

**Grand total:** 35 lessons

## Lab Type Distribution
- **Reference:** 35/35 (no verified real execution)
- **Mock:** 0/35
- **Executed:** 0/35

## Notes for Agent 2
- All 35 lessons are technically correct and complete
- No content modifications needed
- Evidence files in `agent1_evidence/` provide full review documentation
- Rewrite files in `agent1_rewrites/` contain `labType: "Reference"`
- All 48 tests pass (888 subtests)