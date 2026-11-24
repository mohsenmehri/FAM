#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic content builder for FAM Academy v2 vertical slice.

This script creates a versioned, validated, *new* curriculum under
server/www/academy-content/v1/. It deliberately does not recreate any of the
143 intentionally deleted legacy paths and does not touch the root MANIFEST.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "server" / "www" / "academy-content" / "v1"
WEB = "/academy-content/v1"


def write_json(rel: str, data) -> None:
    p = V1 / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(rel: str, text: str) -> None:
    p = V1 / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def web_path(rel: str) -> str:
    return f"{WEB}/{rel}"


def svg_diagram(title: str, desc: str, nodes: list[dict], edges: list[dict]) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 280" role="img" aria-labelledby="t d" dir="rtl">',
        f'<title id="t">{title}</title>',
        f'<desc id="d">{desc}</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/></marker>',
        '<linearGradient id="node" x1="0" x2="1"><stop offset="0" stop-color="#17233c"/><stop offset="1" stop-color="#22345a"/></linearGradient></defs>',
        '<rect x="1" y="1" width="858" height="278" rx="18" fill="#0b1220" stroke="#25334d"/>',
    ]
    pos = {n["id"]: n for n in nodes}
    for e in edges:
        a, b = pos[e["from"]], pos[e["to"]]
        x1, y1, x2, y2 = a["x"], a["y"], b["x"], b["y"]
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" opacity="0.85"/>')
        if e.get("label"):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 8
            parts.append(f'<text x="{mx:.0f}" y="{my:.0f}" fill="#93a4c3" font-size="12" text-anchor="middle" direction="rtl">{e["label"]}</text>')
    for n in nodes:
        x, y = n["x"], n["y"]
        w = n.get("w", 148)
        parts.append(f'<rect x="{x-w/2:.0f}" y="{y-34:.0f}" width="{w}" height="68" rx="14" fill="url(#node)" stroke="#3b4d72"/>')
        parts.append(f'<text x="{x}" y="{y-4}" fill="#e6edf7" font-size="14" font-weight="700" text-anchor="middle" direction="rtl">{n["label"]}</text>')
        if n.get("sub"):
            parts.append(f'<text x="{x}" y="{y+18}" fill="#93a4c3" font-size="11" text-anchor="middle" direction="ltr">{n["sub"]}</text>')
    parts.append('</svg>\n')
    return "\n".join(parts)


REFERENCES = {
    "RFC826": {"title": "RFC 826 — An Ethernet Address Resolution Protocol", "publisher": "IETF", "type": "RFC", "year": 1982, "note": "Historic baseline for ARP on Ethernet."},
    "IEEE8023": {"title": "IEEE 802.3 — Ethernet", "publisher": "IEEE", "type": "Standard", "year": 2022, "note": "Ethernet MAC frame and physical-layer family."},
    "IEEE8021Q": {"title": "IEEE 802.1Q — Bridges and Bridged Networks / VLANs", "publisher": "IEEE", "type": "Standard", "year": 2022, "note": "802.1Q tagging, native VLAN and trunk concepts."},
    "IEEE8021D": {"title": "IEEE 802.1D — MAC Bridges / STP", "publisher": "IEEE", "type": "Standard", "year": 2004, "note": "Classic Spanning Tree baseline; modern networks often use RSTP."},
    "IEEE8021AX": {"title": "IEEE 802.1AX — Link Aggregation", "publisher": "IEEE", "type": "Standard", "year": 2020, "note": "LACP and EtherChannel standard baseline."},
    "RFC791": {"title": "RFC 791 — Internet Protocol", "publisher": "IETF", "type": "RFC", "year": 1981, "note": "IPv4 header and addressing."},
    "RFC4632": {"title": "RFC 4632 — Classless Inter-domain Routing (CIDR)", "publisher": "IETF", "type": "RFC", "year": 2006, "note": "Prefix notation and aggregation."},
    "RFC1918": {"title": "RFC 1918 — Address Allocation for Private Internets", "publisher": "IETF", "type": "RFC", "year": 1996, "note": "Private IPv4 ranges."},
    "RFC8200": {"title": "RFC 8200 — Internet Protocol, Version 6 (IPv6)", "publisher": "IETF", "type": "RFC", "year": 2017, "note": "IPv6 header and addressing architecture."},
    "RFC4861": {"title": "RFC 4861 — Neighbor Discovery for IPv6", "publisher": "IETF", "type": "RFC", "year": 2007, "note": "NDP, RA/RS and address resolution replacement for ARP."},
    "RFC5737": {"title": "RFC 5737 — IPv4 Address Blocks Reserved for Documentation", "publisher": "IETF", "type": "RFC", "year": 2010, "note": "Documentation-only prefixes used in examples and labs."},
    "RFC2328": {"title": "RFC 2328 — OSPF Version 2", "publisher": "IETF", "type": "RFC", "year": 1998, "note": "OSPFv2 neighbor states, LSAs and SPF."},
    "RFC5340": {"title": "RFC 5340 — OSPF for IPv6", "publisher": "IETF", "type": "RFC", "year": 2008, "note": "OSPFv3 differences."},
    "RFC4271": {"title": "RFC 4271 — A Border Gateway Protocol 4 (BGP-4)", "publisher": "IETF", "type": "RFC", "year": 2006, "note": "BGP path selection baseline."},
    "RFC7868": {"title": "RFC 7868 — Cisco's Enhanced Interior Gateway Routing Protocol (EIGRP)", "publisher": "IETF", "type": "Informational RFC", "year": 2016, "note": "Published protocol description; vendor implementations may differ."},
    "RFC793": {"title": "RFC 793 — Transmission Control Protocol", "publisher": "IETF", "type": "RFC", "year": 1981, "note": "TCP handshake and reliability baseline."},
    "RFC768": {"title": "RFC 768 — User Datagram Protocol", "publisher": "IETF", "type": "RFC", "year": 1980, "note": "UDP datagram service."},
    "RFC2131": {"title": "RFC 2131 — Dynamic Host Configuration Protocol", "publisher": "IETF", "type": "RFC", "year": 1997, "note": "DORA process."},
    "RFC1034": {"title": "RFC 1034 — Domain Names: Concepts and Facilities", "publisher": "IETF", "type": "RFC", "year": 1987, "note": "DNS namespace and resolution."},
    "RFC1035": {"title": "RFC 1035 — Domain Names: Implementation and Specification", "publisher": "IETF", "type": "RFC", "year": 1987, "note": "DNS message and record formats."},
    "RFC5905": {"title": "RFC 5905 — Network Time Protocol Version 4", "publisher": "IETF", "type": "RFC", "year": 2010, "note": "NTP time synchronisation."},
    "RFC5424": {"title": "RFC 5424 — The Syslog Protocol", "publisher": "IETF", "type": "RFC", "year": 2009, "note": "Syslog message format."},
    "RFC4301": {"title": "RFC 4301 — Security Architecture for IP", "publisher": "IETF", "type": "RFC", "year": 2005, "note": "IPsec architecture."},
    "RFC2474": {"title": "RFC 2474 — Definition of the DS Field in IPv4/IPv6 Headers", "publisher": "IETF", "type": "RFC", "year": 1998, "note": "DSCP marking."},
    "CISCO_IOS_XE": {"title": "Cisco IOS XE Configuration Guides — Switching, Routing and Security sections", "publisher": "Cisco", "type": "Vendor documentation", "year": None, "note": "Command syntax varies by platform and software release; verify target version before production use."},
    "WIRESHARK_DOCS": {"title": "Wireshark User's Guide and Display Filter Reference", "publisher": "Wireshark Foundation", "type": "Tool documentation", "year": None, "note": "Packet capture and protocol dissection reference."},
}


PATH_OUTLINES = {
    "p01-network-fundamentals": (["مدلهای OSI و TCP/IP", "Encapsulation و مسیر بسته"], ["تحلیل لایههای یک بسته HTTP", "بازیابی توپولوژی از Packet Capture"], "ساخت یک Packet Journey تعاملی برای ترافیک داخلی و اینترنت"),
    "p02-ethernet-switching": (["Ethernet Frame و MAC Learning", "Switching، Collision Domain و Broadcast Domain"], ["خواندن جدول MAC", "ردیابی Unknown Unicast"], "پیکربندی دو سوئیچ و مشاهده یادگیری آدرسهای MAC"),
    "p03-vlan-stp-etherchannel": (["Access VLAN و Trunk 802.1Q", "STP/RSTP، Root Bridge و EtherChannel"], ["محاسبه پورت Blocked", "مقایسه LACP و PaGP"], "ساخت VLAN، Trunk و جلوگیری از Loop با RSTP"),
    "p04-ipv4-ipv6-subnetting": (["IPv4، CIDR و VLSM", "IPv6 Addressing و SLAAC/ND"], ["طراحی VLSM برای چهار سایت", "تحلیل آدرسهای IPv6 و Prefix"], "آدرسدهی دوگانه IPv4/IPv6 و بررسی همزیستی"),
    "p05-routing-concepts": (["Routing Table و Longest Prefix Match", "Administrative Distance و Metric"], ["مقایسه مسیرهای Connected/Static/OSPF", "پیشبینی مسیر با چند Prefix"], "ساخت جدول مسیریابی با مسیرهای رقابتی"),
    "p06-static-dynamic-routing": (["Static Route و Next-hop", "مقایسه Dynamic Routing Protocols"], ["عیبیابی Static Route", "انتخاب پروتکل براساس مقیاس"], "ترکیب Static Route و OSPF با Floating Static"),
    "p07-ospf": (["OSPF Neighbor و LSDB", "SPF، Cost و Area Design"], ["تحلیل LSA Type 1 و 2", "محاسبه Cost مسیر"], "پیادهسازی OSPF Single-Area و Multi-Area"),
    "p08-eigrp": (["EIGRP Neighbor و DUAL", "Metric، Feasible Successor و Stub"], ["محاسبه Composite Metric", "طراحی Stub Routing"], "همسایگی EIGRP و بازیابی مسیر"),
    "p09-bgp": (["BGP Sessions و Path Attributes", "Route Selection و Policy"], ["تحلیل AS_PATH و LOCAL_PREF", "فیلتر Prefix با Route-map"], "eBGP/iBGP در یک توپولوژی کوچک"),
    "p10-advanced-switching-routing": (["FHRP، Stack و Chassis", " redistribution و Route Filtering"], ["مقایسه HSRP و VRRP", "جلوگیری از Routing Loop"], "پیادهسازی Gateway Redundancy و Redistribution کنترلشده"),
    "p11-acl-security": (["Standard/Extended ACL", "Port Security، DHCP Snooping و DAI"], ["نوشتن ACL با Wildcard Mask", "تحلیل Control-plane Policing"], "محافظت لایه دسترسی و فیلتر ترافیک"),
    "p12-nat-services": (["Static/ Dynamic NAT و PAT", "Service Publishing و NAT Order"], ["محاسبه Translation Table", "عیبیابی PAT Overload"], "اتصال شبکه خصوصی به سرویس مستندسازی با PAT"),
    "p13-dhcp-dns-ntp-syslog": (["DHCP DORA و Relay", "DNS، NTP و Syslog"], ["تحلیل پیامهای DORA", "همزمانسازی زمان و لاگ"], "ساخت سرویسهای پایهای شبکه و خواندن لاگها"),
    "p14-qos-voip": (["QoS Models و DSCP", "Queuing، Policing و Voice VLAN"], ["علامتگذاری RTP", "مقایسه LLQ و CBWFQ"], "اولویتبندی ترافیک صدا در لینک پرازدحام"),
    "p15-vpn-ipsec": (["IPsec Architecture و IKE", "Site-to-Site Tunnel و GRE"], ["تحلیل Security Association", "عیبیابی Tunnel"], "ساخت تونل Site-to-Site در محیط شبیهساز"),
    "p16-wireless": (["WLAN، 802.11 و RF", "WLC، SSID و Security"], ["محاسبه Channel Plan", "مقایسه WPA2/WPA3 Enterprise"], "طراحی پوشش WLAN و اعتبارسنجی Roaming"),
    "p17-automation": (["APIs، YANG و NETCONF/RESTCONF", "Ansible و Telemetry"], ["خواندن مدل YANG", "ساخت Playbook بایدیمن"], "دریافت وضعیت اینترفیسها از API و اعمال تغییر کنترلشده"),
    "p18-linux-networking": (["Linux Network Namespaces و iproute2", "Routing، Firewall و Troubleshooting"], ["ساخت veth pair", "تحلیل ss و tcpdump"], "ساخت یک شبکه مینیاتوری با namespaceها"),
    "p19-monitoring-troubleshooting": (["SNMP، Flow و Telemetry", "روشمندسازی Troubleshooting"], ["خواندن SNMP OID", "تحلیل ترافیک با tcpdump"], "تشخیص علت ریشهای قطعی لایه ۲ و لایه ۳"),
    "p20-enterprise-design": (["Hierarchical Design و Campus", "Redundancy، IP Plan و Failure Domains"], ["طراحی Core/Distribution/Access", "محاسبه ظرفیت Uplink"], "طراحی شبکه سازمانی چندسایته"),
    "p21-data-center": (["Leaf-Spine و VXLAN/EVPN", "MLAG، Fabric و Overlay"], ["مقایسه L2 و L3 Fabric", "تحلیل Encapsulation VXLAN"], "ساخت یک Fabric کوچک Leaf-Spine در شبیهساز"),
    "p22-cloud-modern": (["Cloud Networking و VPC", "SDN، Container Networking و SASE"], ["مقایسه VPC و VNet", "تحلیل CNI"], "اتصال امن محیط On-prem به Cloud"),
    "p23-cisco-exam-prep": (["CCNA Blueprint و نقشه مرور", "CCNP ENCOR و آزمون عملی"], ["تحلیل سؤالات سناریومحور", "مرور طراحی و Troubleshooting"], "آزمون جامع شبیهسازیشده با پاسخ تشریحی"),
}


PATHS = [
    ("p01-network-fundamentals", "مبانی شبکه و مدلهای ارتباطی", "پایه", [], ["p02-ethernet-switching", "p04-ipv4-ipv6-subnetting"]),
    ("p02-ethernet-switching", "Ethernet و Switching", "پایه", ["p01-network-fundamentals"], ["p03-vlan-stp-etherchannel"]),
    ("p03-vlan-stp-etherchannel", "VLAN، Trunk، STP و EtherChannel", "متوسط", ["p02-ethernet-switching"], ["p07-ospf", "p10-advanced-switching-routing"]),
    ("p04-ipv4-ipv6-subnetting", "IPv4، IPv6 و Subnetting", "متوسط", ["p01-network-fundamentals"], ["p05-routing-concepts"]),
    ("p05-routing-concepts", "Routing و مفاهیم مسیریابی", "متوسط", ["p04-ipv4-ipv6-subnetting"], ["p06-static-dynamic-routing"]),
    ("p06-static-dynamic-routing", "Static Routing و Dynamic Routing", "متوسط", ["p05-routing-concepts"], ["p07-ospf", "p08-eigrp", "p09-bgp"]),
    ("p07-ospf", "OSPF", "متوسط", ["p05-routing-concepts", "p06-static-dynamic-routing"], ["p10-advanced-switching-routing"]),
    ("p08-eigrp", "EIGRP", "متوسط", ["p06-static-dynamic-routing"], ["p10-advanced-switching-routing"]),
    ("p09-bgp", "BGP", "پیشرفته", ["p07-ospf", "p08-eigrp"], ["p20-enterprise-design", "p21-data-center"]),
    ("p10-advanced-switching-routing", "Switching و Routing پیشرفته", "پیشرفته", ["p03-vlan-stp-etherchannel", "p07-ospf"], ["p20-enterprise-design"]),
    ("p11-acl-security", "ACL و Network Security", "متوسط", ["p04-ipv4-ipv6-subnetting", "p02-ethernet-switching"], ["p15-vpn-ipsec"]),
    ("p12-nat-services", "NAT و خدمات شبکه", "متوسط", ["p04-ipv4-ipv6-subnetting", "p11-acl-security"], ["p13-dhcp-dns-ntp-syslog"]),
    ("p13-dhcp-dns-ntp-syslog", "DHCP، DNS، NTP و Syslog", "متوسط", ["p04-ipv4-ipv6-subnetting"], ["p19-monitoring-troubleshooting"]),
    ("p14-qos-voip", "QoS و Voice over IP", "پیشرفته", ["p11-acl-security", "p13-dhcp-dns-ntp-syslog"], ["p20-enterprise-design"]),
    ("p15-vpn-ipsec", "VPN، IPsec و تونلها", "پیشرفته", ["p11-acl-security", "p09-bgp"], ["p22-cloud-modern"]),
    ("p16-wireless", "Wireless Networking", "متوسط", ["p03-vlan-stp-etherchannel"], ["p20-enterprise-design"]),
    ("p18-linux-networking", "Linux Networking", "متوسط", ["p01-network-fundamentals"], ["p17-automation", "p19-monitoring-troubleshooting"]),
    ("p17-automation", "Network Automation", "پیشرفته", ["p13-dhcp-dns-ntp-syslog", "p18-linux-networking"], ["p21-data-center", "p22-cloud-modern"]),
    ("p19-monitoring-troubleshooting", "Monitoring و Troubleshooting", "پیشرفته", ["p07-ospf", "p13-dhcp-dns-ntp-syslog"], ["p20-enterprise-design"]),
    ("p20-enterprise-design", "طراحی و معماری شبکههای سازمانی", "پیشرفته", ["p09-bgp", "p10-advanced-switching-routing", "p19-monitoring-troubleshooting"], ["p21-data-center", "p22-cloud-modern"]),
    ("p21-data-center", "Data Center Networking", "پیشرفته", ["p20-enterprise-design"], ["p22-cloud-modern"]),
    ("p22-cloud-modern", "مفاهیم Cloud و شبکههای مدرن", "پیشرفته", ["p20-enterprise-design", "p15-vpn-ipsec"], ["p23-cisco-exam-prep"]),
    ("p23-cisco-exam-prep", "آمادگی آزمونهای Cisco مانند CCNA، CCNP و ENCOR", "پیشرفته", ["p07-ospf", "p11-acl-security", "p20-enterprise-design"], []),
]


OBJECTIVES = {
    pid: [
        f"تبیین اصول {title} بدون تکیه بر حفظیات",
        "تحلیل رفتار بستهها و جدولهای تصمیمگیری در یک سناریوی مستند",
        "پیادهسازی و عیبیابی پیکربندی در Simulator داخلی پیش از اتصال به تجهیزات واقعی",
    ]
    for pid, title, _, _, _ in PATHS
}


def planned_course(pid: str, title: str, level: str, prereqs: list[str], order: int, next_paths: list[str]) -> dict:
    chapters, exercises, labs = PATH_OUTLINES[pid]
    ch_outline_1, ch_outline_2, ex1, ex2, lab_scenario = chapters[0], chapters[1], exercises[0], exercises[1], labs
    return {
        "id": f"c{order:02d}-{pid}",
        "pathId": pid,
        "title": f"دوره {title}",
        "level": level,
        "status": "planned",
        "summary": f"نقشه راه {title}؛ محتوای کامل این دوره در P1 تولید خواهد شد.",
        "prerequisites": prereqs,
        "objectives": OBJECTIVES[pid],
        "nextPaths": next_paths,
        "chapters": [
            {"id": f"{pid}-ch01", "title": ch_outline_1, "lessonIds": [], "exerciseIds": [f"{pid}-ex01"], "labIds": [], "status": "planned", "outline": [f"مفاهیم کلیدی {ch_outline_1}", f"تمرین تحلیلی مرتبط با {ch_outline_1}"]},
            {"id": f"{pid}-ch02", "title": ch_outline_2, "lessonIds": [], "exerciseIds": [f"{pid}-ex02"], "labIds": [f"{pid}-lab01"], "status": "planned", "outline": [f"مفاهیم کلیدی {ch_outline_2}", f"سناریوی عملی {ch_outline_2}"]},
        ],
        "plannedExercises": [
            {"id": f"{pid}-ex01", "title": ex1, "status": "planned"},
            {"id": f"{pid}-ex02", "title": ex2, "status": "planned"},
        ],
        "plannedLabs": [
            {"id": f"{pid}-lab01", "title": f"آزمایشگاه {title}", "scenario": lab_scenario, "status": "planned"},
        ],
    }


LESSON_SPECS = [
    {
        "id": "l01-osi-tcpip-encapsulation",
        "title": "Encapsulation در OSI و TCP/IP: سفر یک درخواست HTTP",
        "courseId": "c01-network-fundamentals", "chapterId": "p01-network-fundamentals-ch01", "pathId": "p01-network-fundamentals",
        "level": "پایه", "durationMinutes": 35, "order": 1,
        "summary": "مسیر لایهبهلایه یک پیام HTTP را از Application تا bits و برعکس دنبال میکنیم.",
        "objectives": ["نامگذاری PDU هر لایه", "تشخیص محل افزودهشدن IP و MAC", "توضیح نقش MTU در Fragmentation"],
        "prerequisites": ["آشنایی اولیه با آدرس IP و مرورگر"],
        "concept": "مدل OSI هفت لایه قراردادی برای گفتگو درباره وظایف است؛ مدل TCP/IP چهار لایه عملیاتی است که پروتکلهای اینترنت روی آن پیاده میشوند. هیچکدام «بسته واقعی» نیستند، بلکه چارچوب تحلیلاند.",
        "deep": "وقتی مرورگر درخواستی میسازد، داده در Application ایجاد میشود، TCP آن را Segment میکند، IP یک Header با Source/Destination اضافه میکند و Ethernet یک Frame با MAC مقصد Hop بعدی میسازد. در مقصد هر لایه Header متناظر خود را برمیدارد. نکته کلیدی این است که آدرس IP مقصد نهاییدر طول مسیر ثابت میماند، ولی آدرس MAC در هر Hop تغییر میکند.",
        "diagram": {"caption": "نمایش لایهها و تغییر آدرس MAC در هر Hop؛ مقادیر نمونه از RFC 5737 هستند.", "nodes": [{"id": "app", "x": 90, "y": 140, "label": "Client", "sub": "192.0.2.10"}, {"id": "sw", "x": 300, "y": 140, "label": "Access Switch", "sub": "L2"}, {"id": "r", "x": 510, "y": 140, "label": "Router", "sub": "192.0.2.1"}, {"id": "srv", "x": 740, "y": 140, "label": "Web Server", "sub": "203.0.113.10"}], "edges": [{"from": "app", "to": "sw", "label": "HTTP / TCP / IP / Ethernet"}, {"from": "sw", "to": "r", "label": "Frame → Gateway MAC"}, {"from": "r", "to": "srv", "label": "New Frame, same IP"}]},
        "example": "در یک شبکه خانگی، کلاینت 192.0.2.10 قصد دارد به 203.0.113.10 برسد. چون مقصد در سابنت محلی نیست، Frame را به MAC Default Gateway میفرستد؛ روتر IP Packet را نگه میدارد و Frame تازهای برای Hop بعدی میسازد.",
        "scenario": "یک ترافیک HTTP ساده را در Wireshark فرض کنید: ابتدا DNS، سپس TCP SYN، SYN/ACK، ACK و بعد GET. در Packet Journey شبیهساز، هر Hop یک ردیف جدول تولید میکند.",
        "commands": [],
        "walkthrough": [],
        "sample": ["[Simulated] #1 192.0.2.10 → 192.0.2.1 | Ethernet | dst MAC = Gateway | IP dst = 203.0.113.10", "[Simulated] #2 192.0.2.1 → 198.51.100.1 | Ethernet | dst MAC = Next Hop | IP dst unchanged", "[Simulated] #3 203.0.113.10 → 192.0.2.10 | HTTP 200 OK | decapsulation at receiver"],
        "mistakes": ["یکی دانستن MAC و IP", "تصور اینکه مدل OSI دقیقاً همان پیادهسازی TCP/IP است", "فراموشکردن تغییر MAC در هر Hop"],
        "troubleshoot": ["از l بالا به پایین شروع کنید: ابتدا لینک و ARP، بعد IP، بعد TCP و در نهایت Application.", "اگر ping برقرار است ولی HTTP نه، TCP/443 یا 80 و نام DNS را جداگانه بررسی کنید."],
        "key": ["PDU لایه ۴ Segment، لایه ۳ Packet و لایه ۲ Frame است.", "IP مقصد ثابت؛ MAC مقصد در هر Hop عوض میشود.", "MTU تعیین میکند آیا IP نیاز به Fragmentation دارد یا خیر."],
        "version": "استاندارد IP در RFC 791 تعریف شده و IPv6 در RFC 8200 جایگزین ساختار آدرسدهی شده است؛ رفتار Encapsulation در اصول مشابه است ولی Headerها متفاوتاند. پیادهسازی vendor ممکن است در Offloadهای سختافزاری تفاوت داشته باشد.",
        "refs": ["RFC791", "RFC8200", "RFC5737", "WIRESHARK_DOCS"],
        "quiz": [
            {"id": "q1", "prompt": "کدام آدرس در طول مسیر بین روترها معمولاً تغییر میکند؟", "options": ["IP مقصد", "MAC مقصد", "Port مقصد", "شماره Sequence"], "answer": 1, "explain": "MAC مربوط به Hop بعدی است و در هر لایه ۲ جدید بازنویسی میشود."},
            {"id": "q2", "prompt": "PDU لایه شبکه در مدل OSI چیست؟", "options": ["Frame", "Segment", "Packet", "Bit"], "answer": 2, "explain": "لایه ۳ Packet میسازد؛ لایه ۲ Frame و لایه ۴ Segment."},
            {"id": "q3", "prompt": "اگر بستهای بزرگتر از MTU لینک خروجی باشد، کدام لایه تصمیم به Fragmentation میگیرد؟", "options": ["Ethernet", "IP", "TCP", "HTTP"], "answer": 1, "explain": "Fragmentation در IPv4 توسط لایه IP انجام میشود؛ در IPv6 معمولاً به مبدأ و Path MTU Discovery واگذار میشود."},
        ],
        "next": ["l02-ethernet-arp"], "simulationIds": ["sim-arp-discovery"], "labIds": [], "exerciseId": "ex01-packet-layers",
    },
    {
        "id": "l02-ethernet-arp",
        "title": "Ethernet Frame و ARP: کشف MAC در یک Broadcast Domain",
        "courseId": "c01-network-fundamentals", "chapterId": "p01-network-fundamentals-ch01", "pathId": "p01-network-fundamentals",
        "level": "پایه", "durationMinutes": 40, "order": 2,
        "summary": "رفتار ARP Request/Reply، ARP Cache و تفاوت مقصد محلی و remote را تحلیل میکنیم.",
        "objectives": ["تفسیر فیلدهای Ethernet Frame", "پیشبینی مقصد ARP برای مقصد خارج از سابنت", "تشخیص اثر ARP Cache روی ترافیک Broadcast"],
        "prerequisites": ["l01-osi-tcpip-encapsulation"],
        "concept": "ARP پلی بین آدرس IP لایه ۳ و آدرس MAC لایه ۲ است. تا زمانی که فرستنده MAC مقصد یا Next-hop را نداند، نمیتواند Frame بسازد؛ بنابراین ابتدا یک درخواست Broadcast میفرستد.",
        "deep": "اگر مقصد در همان سابنت باشد، ARP برای IP مقصد ارسال میشود. اگر مقصد خارج از سابنت باشد، ARP برای IP Default Gateway ارسال میشود و IP Packet همچنان مقصد نهایی را در Header خود حفظ میکند. پاسخ ARP unicast است و فقط درخواستکننده Cache را بهروز میکند؛ سایر میزبانها معمولاً فقط درخواست را میشنوند.",
        "diagram": {"caption": "ARP Request بهصورت Broadcast و ARP Reply بهصورت Unicast؛ MACها نمونه هستند.", "nodes": [{"id": "a", "x": 130, "y": 140, "label": "Host A", "sub": "192.0.2.10"}, {"id": "sw", "x": 400, "y": 140, "label": "Switch", "sub": "L2 Flood"}, {"id": "b", "x": 680, "y": 80, "label": "Host B", "sub": "192.0.2.20"}, {"id": "c", "x": 680, "y": 210, "label": "Host C", "sub": "192.0.2.30"}], "edges": [{"from": "a", "to": "sw", "label": "Who has 192.0.2.20?"}, {"from": "sw", "to": "b", "label": "Flood"}, {"from": "sw", "to": "c", "label": "Flood"}, {"from": "b", "to": "a", "label": "Reply: 192.0.2.20 is at 02:00:00:00:00:20"}]},
        "example": "Host A با 192.0.2.10/24 میخواهد 192.0.2.20 را پینگ کند. ابتدا `show arp` یا `ip neigh` خالی است؛ یک ARP Request با Destination MAC `ff:ff:ff:ff:ff:ff` ارسال میشود و Host B پاسخ میدهد.",
        "scenario": "در شبیهساز ARP، تغییر Subnet Mask، Cache Hit و Gateway مشاهده کنید: با مقصد remote، درخواست به جای IP مقصد برای Gateway ساخته میشود.",
        "commands": [{"command": "show ip arp", "explain": "نمایش نگاشت IP به MAC در IOS."}, {"command": "clear arp-cache", "explain": "پاککردن Cache برای مشاهده دوباره فرایند کشف؛ این دستور فقط در محیط آزمایشی انجام شود."}],
        "walkthrough": [{"line": "show ip arp", "explain": "خروجی شامل Age، IP، MAC و Interface است."}, {"line": "clear arp-cache", "explain": "ورودیهای پویا حذف میشوند تا ARP بعدی دوباره Broadcast تولید کند."}],
        "sample": ["Sample / Simulated — Internal Simulator", "Protocol  Address   Age  Hardware Addr   Interface", "Internet  192.0.2.20  0   0200.0000.0020  Gi0/1"],
        "mistakes": ["تصور اینکه ARP از روتر عبور میکند", "استفاده از Broadcast MAC برای مقصد remote", "اشتباه گرفتن Gratuitous ARP با Reply معمولی"],
        "troubleshoot": ["اگر ARP Resolve نمیشود، VLAN، پورت Access و Subnet Mask را بررسی کنید.", "Duplicate IP با Gratuitous ARP و پیامهای Duplicate Address شناسایی میشود."],
        "key": ["ARP Request Broadcast است؛ Reply معمولاً Unicast است.", "Router مرز Broadcast Domain است.", "IPv6 بهجای ARP از Neighbor Discovery و ICMPv6 استفاده میکند."],
        "version": "RFC 826 تاریخی است؛ در IPv6، RFC 4861 جایگزین ARP شده است. برخی پلتفرمها Proxy ARP یا ARP Suppression دارند که رفتار را تغییر میدهد.",
        "refs": ["RFC826", "IEEE8023", "RFC4861", "CISCO_IOS_XE"],
        "quiz": [
            {"id": "q1", "prompt": "مقصد ARP Request برای یک IP خارج از سابنت محلی کدام است؟", "options": ["IP مقصد نهایی", "IP Default Gateway", "MAC سرور DNS", "Broadcast IP 255.255.255.255"], "answer": 1, "explain": "لایه ۲ باید MAC Next-hop یعنی Gateway را پیدا کند."},
            {"id": "q2", "prompt": "Destination MAC در ARP Request چیست؟", "options": ["00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff", "MAC روتر", "MAC مقصد نهایی"], "answer": 1, "explain": "درخواست به تمام گرههای Broadcast Domain ارسال میشود."},
            {"id": "q3", "prompt": "کدام پروتکل در IPv6 وظیفه مشابه ARP را انجام میدهد؟", "options": ["DHCPv6", "NDP/ICMPv6", "OSPFv3", "TCP"], "answer": 1, "explain": "Neighbor Discovery در RFC 4861 تعریف شده است."},
        ],
        "next": ["l03-vlan-access-ports"], "simulationIds": ["sim-arp-discovery"], "labIds": [], "exerciseId": "ex02-arp-cache",
    },
    {
        "id": "l03-vlan-access-ports",
        "title": "Access VLAN و تفکیک Broadcast Domain",
        "courseId": "c02-switching-vlan", "chapterId": "p03-vlan-stp-etherchannel-ch01", "pathId": "p03-vlan-stp-etherchannel",
        "level": "متوسط", "durationMinutes": 45, "order": 3,
        "summary": "یک سوئیچ را به چند Broadcast Domain منطقی تقسیم میکنیم و رفتار پورت Access را بررسی میکنیم.",
        "objectives": ["تعریف VLAN و Access Port", "توضیح جدول MAC بهازای VLAN", "تشخیص نیاز به Routing برای ارتباط بین VLANها"],
        "prerequisites": ["l02-ethernet-arp"],
        "concept": "VLAN یک شماره و یک جدول forwarding مستقل روی همان سختافزار سوئیچ است. پورت Access متعلق به یک VLAN است و Frame بدون Tag دریافت/ارسال میکند.",
        "deep": "سوئیچ فریمهای یک VLAN را فقط به پورتهای همان VLAN و Trunkهای مجاز میفرستد. بنابراین Broadcast، Unknown Unicast و یادگیری MAC در هر VLAN جداگانه انجام میشود. دو کلاینت در VLAN 10 و VLAN 20 بدون لایه ۳ نمیتوانند مستقیماً ARP یکدیگر را بشنوند، حتی اگر به یک سوئیچ متصل باشند.",
        "diagram": {"caption": "دو VLAN روی یک سوئیچ؛ ارتباط بین آنها نیازمند Router یا SVI است.", "nodes": [{"id": "a", "x": 120, "y": 90, "label": "PC-A", "sub": "VLAN 10"}, {"id": "b", "x": 120, "y": 210, "label": "PC-B", "sub": "VLAN 20"}, {"id": "sw", "x": 410, "y": 150, "label": "Access Switch", "sub": "MAC table per VLAN"}, {"id": "r", "x": 710, "y": 150, "label": "Router / SVI", "sub": "Inter-VLAN"}], "edges": [{"from": "a", "to": "sw", "label": "untagged"}, {"from": "b", "to": "sw", "label": "untagged"}, {"from": "sw", "to": "r", "label": "trunk or SVI"}]},
        "example": "پورت Gi0/1 در VLAN 10 و Gi0/2 در VLAN 20 قرار میگیرد. `show vlan brief` دو گروه جدا نشان میدهد و Broadcast ARP هرکدام فقط در همان گروه دیده میشود.",
        "scenario": "در شبیهساز VLAN، پارامتر Destination VLAN را تغییر دهید تا ببینید بدون Inter-VLAN Routing تحویل لایه ۲ انجام نمیشود.",
        "commands": [{"command": "vlan 10", "explain": "ایجاد VLAN 10 در پایگاه VLAN."}, {"command": "name Users", "explain": "اختصاص نام خوانا به VLAN."}, {"command": "interface GigabitEthernet0/1", "explain": "ورود به تنظیمات پورت."}, {"command": "switchport mode access", "explain": "ثابتکردن پورت در حالت Access."}, {"command": "switchport access vlan 10", "explain": "تخصیص پورت به VLAN 10."}, {"command": "no shutdown", "explain": "فعالکردن پورت."}],
        "walkthrough": [{"line": "vlan 10 / name Users", "explain": "VLAN و نام آن را در VLAN Database ثبت میکند."}, {"line": "switchport mode access", "explain": "از مذاکره خودکار DTP جلوگیری و پورت را بدون Tag نگه میدارد."}, {"line": "switchport access vlan 10", "explain": "همه Frameهای بدون Tag این پورت به VLAN 10 نگاشت میشوند."}],
        "sample": ["Sample / Simulated — Internal Simulator", "VLAN Name                 Status    Ports", "10   Users                active    Gi0/1", "20   Servers              active    Gi0/2"],
        "mistakes": ["فراموشکردن ساخت VLAN قبل از تخصیص", "تصور اینکه Access Portها Tag دارند", "قراردادن Default Gateway کلاینتها در VLAN اشتباه"],
        "troubleshoot": ["`show vlan brief`، `show interfaces status` و `show mac address-table vlan 10` را بهترتیب بررسی کنید.", "اگر پورت در VLAN اشتباه است، ARP و DHCP هر دو شکست میخورند."],
        "key": ["Access Port فریم untagged حمل میکند.", "هر VLAN Broadcast Domain مستقل دارد.", "برای ارتباط VLANها به SVI، Router-on-a-Stick یا لایه ۳ نیاز است."],
        "version": "IEEE 802.1Q استاندارد VLAN Tagging است. پیادهسازی Cisco نامگذاری VLAN، VTP و `switchport` دارد؛ سایر vendorها ممکن است اصطلاحات متفاوتی بهکار ببرند.",
        "refs": ["IEEE8021Q", "CISCO_IOS_XE", "RFC826"],
        "quiz": [
            {"id": "q1", "prompt": "Frame روی پورت Access چگونه ارسال میشود؟", "options": ["همیشه Tagged", "بدون 802.1Q Tag", "با VXLAN VNI", "فقط با ISL"], "answer": 1, "explain": "Access Port برای تجهیزات endpoint فریم untagged میفرستد."},
            {"id": "q2", "prompt": "دو کلاینت در VLAN 10 و VLAN 20 روی یک سوئیچ چه نیازی دارند؟", "options": ["هیچ، سوئیچ مسیریابی میکند", "Trunk", "لایه ۳ / Inter-VLAN Routing", "STP غیرفعال"], "answer": 2, "explain": "VLANها Broadcast Domain جدا هستند و عبور از آنها نیازمند Routing است."},
            {"id": "q3", "prompt": "کدام دستور پورت را به VLAN 10 اختصاص میدهد؟", "options": ["switchport trunk allowed vlan 10", "switchport access vlan 10", "network 10.0.0.0 area 0", "ip address 10.0.0.1"], "answer": 1, "explain": "دستور access vlan مخصوص پورت Access است."},
        ],
        "next": ["l04-trunk-8021q"], "simulationIds": ["sim-vlan-trunk"], "labIds": ["lab-vlan-trunk"], "exerciseId": "ex03-vlan-access",
    },
    {
        "id": "l04-trunk-8021q",
        "title": "Trunk 802.1Q، Allowed VLAN و Native VLAN",
        "courseId": "c02-switching-vlan", "chapterId": "p03-vlan-stp-etherchannel-ch01", "pathId": "p03-vlan-stp-etherchannel",
        "level": "متوسط", "durationMinutes": 50, "order": 4,
        "summary": "چگونگی حمل چند VLAN روی یک لینک، Tag 802.1Q و خطاهای رایج Native VLAN را بررسی میکنیم.",
        "objectives": ["تفسیر فیلد VLAN ID در Tag", "پیکربندی Allowed VLAN", "تشخیص Native VLAN Mismatch"],
        "prerequisites": ["l03-vlan-access-ports"],
        "concept": "Trunk لینکی است که فریمهای چند VLAN را با برچسب 802.1Q حمل میکند. استثنا، Native VLAN است که بهطور پیشفرض بدون Tag ارسال میشود.",
        "deep": "Tag 802.1Q شامل TPID، PCP، DEI و VID دوازدهبیتی است. Allowed VLAN List مشخص میکند کدام VLANها اجازه عبور دارند. اگر Native VLAN دو سر Trunk یکسان نباشد، فریم untagged یک سر در VLAN دیگری تفسیر میشود؛ این هم خطر امنیتی و هم خطای ارتباطی ایجاد میکند.",
        "diagram": {"caption": "دو سوئیچ از طریق Trunk؛ VLAN 10 Tagged و VLAN 99 Native/untagged است.", "nodes": [{"id": "s1", "x": 150, "y": 140, "label": "SW1", "sub": "Gi0/24 trunk"}, {"id": "s2", "x": 690, "y": 140, "label": "SW2", "sub": "Gi0/24 trunk"}, {"id": "v10", "x": 420, "y": 70, "label": "VLAN 10", "sub": "tagged 802.1Q"}, {"id": "v99", "x": 420, "y": 215, "label": "VLAN 99", "sub": "native / untagged"}], "edges": [{"from": "s1", "to": "s2", "label": "allowed 10,20,99"}, {"from": "v10", "to": "v99", "label": "same physical link"}]},
        "example": "لینک Gi0/24 بین SW1 و SW2 فقط VLANهای 10، 20 و 99 را حمل میکند. بسته VLAN 30 در همان لحظه ورود به Trunk حذف میشود.",
        "scenario": "در شبیهساز VLAN/Trunk، Allowed List و Native VLAN دو سر را تغییر دهید؛ جدول تصمیمگیری دقیقاً علت Drop یا تحویل را نشان میدهد.",
        "commands": [{"command": "interface GigabitEthernet0/24", "explain": "انتخاب لینک بین سوئیچها."}, {"command": "switchport mode trunk", "explain": "فعالکردن حالت Trunk."}, {"command": "switchport trunk allowed vlan 10,20,99", "explain": "محدودکردن VLANهای مجاز."}, {"command": "switchport trunk native vlan 99", "explain": "تعیین VLAN بدون Tag؛ باید دو سر یکسان باشد."}, {"command": "show interfaces trunk", "explain": "بررسی وضعیت، Allowed VLAN و Native VLAN."}],
        "walkthrough": [{"line": "switchport mode trunk", "explain": "پورت را به حالت 802.1Q Trunk ثابت میکند."}, {"line": "switchport trunk allowed vlan 10,20,99", "explain": "VLANهای دیگر حتی اگر وجود داشته باشند از این لینک عبور نمیکنند."}, {"line": "switchport trunk native vlan 99", "explain": "فریمهای VLAN 99 بدون Tag ارسال میشوند؛ mismatch دو سر خطرناک است."}],
        "sample": ["Sample / Simulated — Internal Simulator", "Port      Mode  Encapsulation  Status  Native vlan", "Gi0/24    on    802.1q         trunking 99", "Port      Vlans allowed on trunk", "Gi0/24    10,20,99"],
        "mistakes": ["Native VLAN متفاوت در دو سر", "فراموشکردن اضافهکردن VLAN جدید به Allowed List", "استفاده از VLAN 1 بهعنوان Native بدون مستندسازی"],
        "troubleshoot": ["دستور `show interfaces trunk` را در هر دو سوئیچ مقایسه کنید.", "پیام `%SPANTREE-2-RECV_PVID_ERR` معمولاً نشانه Native VLAN Mismatch است."],
        "key": ["VID در 802.1Q دوازده بیت است.", "Allowed List رفتار Data Plane را تعیین میکند.", "Tag کردن Native VLAN در نسخههای جدید توصیه امنیتی رایج است."],
        "version": "IEEE 802.1Q جایگزین ISL قدیمی Cisco شده است. برخی پلتفرمها امکان `vlan dot1q tag native` دارند؛ حتماً نسخه IOS XE/NX-OS هدف را بررسی کنید.",
        "refs": ["IEEE8021Q", "CISCO_IOS_XE", "IEEE8021D"],
        "quiz": [
            {"id": "q1", "prompt": "اگر VLAN 30 در Allowed List نباشد چه رخ میدهد؟", "options": ["به Native VLAN تبدیل میشود", "از Trunk عبور نمیکند", "بهطور خودکار Tagged میشود", "به روتر ارسال میشود"], "answer": 1, "explain": "سوئیچ فریم VLAN غیرمجاز را روی آن Trunk Forward نمیکند."},
            {"id": "q2", "prompt": "کدام فریم روی Trunk معمولاً بدون Tag است؟", "options": ["VLAN 10", "VLAN 20", "Native VLAN", "همه VLANها"], "answer": 2, "explain": "Native VLAN بهطور پیشفرض untagged حمل میشود."},
            {"id": "q3", "prompt": "Native VLAN Mismatch چه پیامدی دارد؟", "options": ["افزایش MTU", "تفسیر فریم untagged در VLAN اشتباه", "غیرفعالشدن STP", "تغییر IP Gateway"], "answer": 1, "explain": "دو سر فریم بدون Tag را به VLANهای متفاوتی نگاشت میکنند."},
        ],
        "next": ["l05-ipv4-subnetting"], "simulationIds": ["sim-vlan-trunk"], "labIds": ["lab-vlan-trunk"], "exerciseId": "ex04-trunk-allowed",
    },
    {
        "id": "l05-ipv4-subnetting",
        "title": "IPv4، CIDR و Subnetting قابل محاسبه",
        "courseId": "c03-ip-addressing", "chapterId": "p04-ipv4-ipv6-subnetting-ch01", "pathId": "p04-ipv4-ipv6-subnetting",
        "level": "متوسط", "durationMinutes": 55, "order": 5,
        "summary": "Subnet Mask، Prefix، Network/Broadcast/Host Range و VLSM را با اعداد مستند محاسبه میکنیم.",
        "objectives": ["تبدیل Prefix به Mask", "محاسابه Network و Broadcast", "طراحی VLSM بدون همپوشانی"],
        "prerequisites": ["l04-trunk-8021q"],
        "concept": "آدرس IPv4 دو بخش Network و Host دارد؛ Prefix طول بخش Network را مشخص میکند. عملیات AND بین آدرس و Mask، Network Address را بهدست میدهد.",
        "deep": "برای `/26`، دو بیت Host از آخرین octet قرض گرفته میشود؛ بنابراین چهار سابنت با ۶۲ آدرس قابلاستفاده داریم. VLSM یعنی تقسیم یک بلوک به prefixهای متفاوت براساس نیاز واقعی؛ شرط صحت، عدم همپوشانی و ترتیب از بزرگترین نیاز به کوچکترین است.",
        "diagram": {"caption": "تقسیم 198.51.100.0/24 به چهار بلوک /26؛ آدرسها از RFC 5737 هستند.", "nodes": [{"id": "b0", "x": 140, "y": 80, "label": ".0/26", "sub": "198.51.100.0"}, {"id": "b1", "x": 380, "y": 80, "label": ".64/26", "sub": "198.51.100.64"}, {"id": "b2", "x": 620, "y": 80, "label": ".128/26", "sub": "198.51.100.128"}, {"id": "b3", "x": 770, "y": 190, "label": ".192/26", "sub": "198.51.100.192"}], "edges": [{"from": "b0", "to": "b1", "label": "+64"}, {"from": "b1", "to": "b2", "label": "+64"}, {"from": "b2", "to": "b3", "label": "+64"}]},
        "example": "بلوک مستند 198.51.100.0/24 برای چهار سایت تقسیم میشود: .0/26، .64/26، .128/26 و .192/26. در هر بلوک آدرس اول Network و آخرین آدرس Broadcast است.",
        "scenario": "در تمرین، تعداد Hostها را تغییر دهید و کوچکترین Prefix مناسب را انتخاب کنید؛ سپس بررسی کنید که بلوکها همپوشانی نداشته باشند.",
        "commands": [],
        "walkthrough": [],
        "sample": ["Sample / Simulated — Subnet Calculator", "198.51.100.64/26 | Network=198.51.100.64 | Broadcast=198.51.100.127 | Usable=198.51.100.65-126"],
        "mistakes": ["محاسبه تعداد Host بهجای تعداد آدرس", "استفاده از /31 برای شبکههای معمولی بدون آگاهی از Point-to-Point", "همپوشانی VLSM"],
        "troubleshoot": ["ابتدا Prefix، سپس Network Address، سپس Default Gateway و در نهایت Subnet Mask کلاینت را مقایسه کنید.", "اگر Host مقصد را remote تشخیص میدهد، Mask اشتباه است."],
        "key": ["`/n` یعنی n بیت اول Network.", "تعداد آدرس قابلاستفاده `2^(32-n)-2` برای prefixهای معمولی است.", "RFC 1918 محدودههای خصوصی و RFC 5737 محدودههای مستندسازی را تعریف میکند."],
        "version": "CIDR در RFC 4632 جایگزین کلاسهای A/B/C شده است. `/31` برای لینکهای Point-to-Point و `/32` برای Host Route رفتار ویژه دارند.",
        "refs": ["RFC791", "RFC4632", "RFC1918", "RFC5737"],
        "quiz": [
            {"id": "q1", "prompt": "Broadcast آدرس 198.51.100.64/26 چیست؟", "options": ["198.51.100.64", "198.51.100.126", "198.51.100.127", "198.51.100.128"], "answer": 2, "explain": "بلوک ۶۴ تا ۱۲۷ است؛ آخرین آدرس Broadcast است."},
            {"id": "q2", "prompt": "چند آدرس قابلاستفاده در /27 وجود دارد؟", "options": ["30", "32", "62", "14"], "answer": 0, "explain": "32 آدرس کل منهای Network و Broadcast میشود ۳۰."},
            {"id": "q3", "prompt": "کدام RFC محدودههای مستندسازی 192.0.2.0/24 و 198.51.100.0/24 را مشخص میکند؟", "options": ["RFC 1918", "RFC 5737", "RFC 2328", "RFC 793"], "answer": 1, "explain": "RFC 5737 این بلوکها را برای مثالها رزرو کرده است."},
        ],
        "next": ["l06-ipv6-addressing"], "simulationIds": [], "labIds": [], "exerciseId": "ex05-vlsm",
    },
    {
        "id": "l06-ipv6-addressing",
        "title": "IPv6 Addressing، SLAAC و Neighbor Discovery",
        "courseId": "c03-ip-addressing", "chapterId": "p04-ipv4-ipv6-subnetting-ch01", "pathId": "p04-ipv4-ipv6-subnetting",
        "level": "متوسط", "durationMinutes": 45, "order": 6,
        "summary": "ساختار آدرس ۱۲۸بیتی، انواع آدرس و جایگزینی ARP با NDP را توضیح میدهیم.",
        "objectives": ["خواندن Prefix و Interface ID", "تفکیک Link-local، Global و Unique-local", "مقایسه SLAAC و DHCPv6"],
        "prerequisites": ["l05-ipv4-subnetting"],
        "concept": "IPv6 آدرس ۱۲۸بیتی دارد و معمولاً بهصورت هشت گروه هگزادسیمال نوشته میشود. فشردهسازی `::` فقط یکبار مجاز است و صفرهای پیشرو حذف میشوند.",
        "deep": "آدرس Link-local با `fe80::/10` شروع میشود و فقط در همان لینک معتبر است. Global Unicast معمولاً از `2000::/3` و Unique-local از `fc00::/7` است. SLAAC با Router Advertisement Prefix را اعلام میکند و میزبان Interface ID میسازد؛ DHCPv6 میتواند آدرس یا سایر اطلاعات را بدهد. NDP بهجای ARP از ICMPv6 NS/NA استفاده میکند.",
        "diagram": {"caption": "Router Advertisement، SLAAC و Neighbor Solicitation در یک لینک IPv6.", "nodes": [{"id": "r", "x": 140, "y": 140, "label": "Router", "sub": "2001:db8:1::1"}, {"id": "h", "x": 700, "y": 140, "label": "Host", "sub": "SLAAC EUI-64 / random"}], "edges": [{"from": "r", "to": "h", "label": "RA: 2001:db8:1::/64"}, {"from": "h", "to": "r", "label": "NS / NA (NDP)"}]},
        "example": "پیشوند مستند `2001:db8:1::/64` از RFC 3849/مستندسازی برای مثالها استفاده میشود. روتر در RA اعلام میکند و میزبان آدرسی مانند `2001:db8:1::20` میسازد.",
        "scenario": "در تمرین، یک آدرس فشردهشده را به Form کامل برگردانید و نوع آن را تعیین کنید؛ سپس پیام NS/NA را با ARP مقایسه کنید.",
        "commands": [{"command": "ipv6 unicast-routing", "explain": "فعالکردن forwarding IPv6 در IOS."}, {"command": "interface GigabitEthernet0/0", "explain": "انتخاب اینترفیس لینک."}, {"command": "ipv6 address 2001:db8:1::1/64", "explain": "اختصاص آدرس Global Unicast مستند به اینترفیس."}, {"command": "show ipv6 interface brief", "explain": "نمایش خلاصه آدرسها و وضعیت اینترفیسها."}],
        "walkthrough": [{"line": "ipv6 unicast-routing", "explain": "بدون آن، روتر بستههای IPv6 بین اینترفیسها Forward نمیکند."}, {"line": "ipv6 address 2001:db8:1::1/64", "explain": "Prefix /64 برای SLAAC روی LAN رایج است."}],
        "sample": ["Sample / Simulated — Internal Simulator", "GigabitEthernet0/0 [up/up]", "FE80::1", "2001:DB8:1::1"],
        "mistakes": ["استفاده بیش از یک `::` در یک آدرس", "تصور اینکه IPv6 به NAT وابسته است", "اشتباه گرفتن Link-local با Global"],
        "troubleshoot": ["`show ipv6 interface brief` و `show ipv6 neighbors` را بررسی کنید.", "اگر RA دریافت نمیشود، SLAAC شکل نمیگیرد؛ فیلتر ICMPv6 را چک کنید."],
        "key": ["IPv6 از ARP استفاده نمیکند.", "RAها در ICMPv6 هستند.", "Prefix /64 برای اغلب LANها و SLAAC استاندارد عملی است."],
        "version": "RFC 8200 جایگزین RFC 2460 شده و RFC 4861 NDP را تعریف میکند. Privacy Extensions و RFC 4941 ممکن است Interface ID تصادفی تولید کنند.",
        "refs": ["RFC8200", "RFC4861", "CISCO_IOS_XE"],
        "quiz": [
            {"id": "q1", "prompt": "کدام پیشوند نشانه Link-local است؟", "options": ["2000::/3", "fc00::/7", "fe80::/10", "ff00::/8"], "answer": 2, "explain": "Link-localها با fe80::/10 شروع میشوند."},
            {"id": "q2", "prompt": "کدام پیام IPv6 جایگزین ARP Request است؟", "options": ["Router Advertisement", "Neighbor Solicitation", "DHCPv6 Solicit", "Echo Request"], "answer": 1, "explain": "NS/NA در NDP نگاشت IP به MAC را انجام میدهند."},
            {"id": "q3", "prompt": "SLAAC چه چیزی را از روتر دریافت میکند؟", "options": ["آدرس کامل از DHCP", "Prefix از Router Advertisement", "MAC Gateway", "Route-map"], "answer": 1, "explain": "RA prefix را اعلام میکند و میزبان Interface ID را میسازد."},
        ],
        "next": ["l07-static-routing"], "simulationIds": [], "labIds": [], "exerciseId": "ex06-ipv6-prefix",
    },
    {
        "id": "l07-static-routing",
        "title": "Routing Table، Longest Prefix Match و Static Route",
        "courseId": "c04-routing-ospf", "chapterId": "p07-ospf-ch01", "pathId": "p07-ospf",
        "level": "متوسط", "durationMinutes": 50, "order": 7,
        "summary": "ساختار جدول مسیریابی، ترتیب تصمیمگیری و پیکربندی مسیرهای Static امن را بررسی میکنیم.",
        "objectives": ["خواندن یک Route Entry", "توضیح Longest Prefix Match", "پیکربندی Next-hop و Floating Static"],
        "prerequisites": ["l05-ipv4-subnetting"],
        "concept": "روتر هنگام دریافت Packet، مقصد را باPrefixهای جدول مسیریابی مقایسه میکند؛ دقیقترین Prefix برنده میشود، حتی اگر Administrative Distance مسیر دیگری کمتر باشد.",
        "deep": "ترتیب تصمیم به این شکل است: ابتدا Longest Prefix Match، سپس در میان مسیرهای همprefix، کمترین AD و سپس Metric. مسیر Connected بر Static و Dynamic مقدم است. Static Route برای مقاصد مشخص و پایدار مناسب است، ولی در توپولوژیهای بزرگ نگهداری دستی خطاخیز میشود.",
        "diagram": {"caption": "دو مسیر به سمت 203.0.113.0/24؛ longest prefix قبل از AD تصمیم میگیرد.", "nodes": [{"id": "h", "x": 110, "y": 140, "label": "Host", "sub": "192.0.2.10"}, {"id": "r1", "x": 360, "y": 140, "label": "R1", "sub": "RIB / FIB"}, {"id": "r2", "x": 640, "y": 80, "label": "R2", "sub": "192.0.2.1"}, {"id": "r3", "x": 640, "y": 210, "label": "R3", "sub": "198.51.100.1"}], "edges": [{"from": "h", "to": "r1", "label": "dst 203.0.113.10"}, {"from": "r1", "to": "r2", "label": "203.0.113.0/24"}, {"from": "r1", "to": "r3", "label": "203.0.113.0/25"}]},
        "example": "دو مسیر `203.0.113.0/24 via 192.0.2.1` و `203.0.113.0/25 via 198.51.100.1` وجود دارد. برای مقصد `203.0.113.10` مسیر /25 انتخاب میشود، چون دقیقتر است.",
        "scenario": "در تمرین، Prefixها و AD را تغییر دهید و مسیر منتخب را پیشبینی کنید؛ سپس با Packet Journey مسیر طیشده را مقایسه کنید.",
        "commands": [{"command": "ip route 203.0.113.0 255.255.255.0 192.0.2.1", "explain": "مسیر Static به شبکه مستند از طریق Next-hop."}, {"command": "ip route 203.0.113.0 255.255.255.0 198.51.100.1 200", "explain": "Floating Static با AD=200 بهعنوان پشتیبان."}, {"command": "show ip route static", "explain": "نمایش مسیرهای Static و AD آنها."}],
        "walkthrough": [{"line": "ip route ... 192.0.2.1", "explain": "یک مسیر با AD پیشفرض ۱ ایجاد میکند."}, {"line": "ip route ... 198.51.100.1 200", "explain": "همان Prefix با AD بدتر فقط در صورت حذف مسیر اصلی وارد جدول میشود."}],
        "sample": ["Sample / Simulated — Internal Simulator", "S    203.0.113.0/24 [1/0] via 192.0.2.1", "S    203.0.113.0/24 [200/0] via 198.51.100.1 (floating, inactive)"],
        "mistakes": ["مقایسه AD پیش از Prefix", "Next-hop خارج از شبکه Connected", "فراموشکردن مسیر برگشت"],
        "troubleshoot": ["`show ip route <prefix>` و `show ip cef <prefix>` را مقایسه کنید.", "مسیر رفت و برگشت را جداگانه بررسی کنید؛ نبود مسیر برگشت علت رایج یکطرفهشدن ارتباط است."],
        "key": ["Longest Prefix Match اولویت اول است.", "AD فقط بین مسیرهای همprefix مقایسه میشود.", "Static Route مسیر برگشت هم نیاز دارد."],
        "version": "مقادیر پیشفرض AD در Cisco متفاوت از برخی vendorهاست؛ مثلاً Connected=0 و Static=1 در IOS رایج است. همیشه مستند نسخه هدف را بررسی کنید.",
        "refs": ["RFC791", "RFC4632", "RFC5737", "CISCO_IOS_XE"],
        "quiz": [
            {"id": "q1", "prompt": "کدام معیار ابتدا در انتخاب مسیر بررسی میشود؟", "options": ["Administrative Distance", "Metric", "Longest Prefix Match", "نام اینترفیس"], "answer": 2, "explain": "اول دقیقترین Prefix، سپس AD/Metric."},
            {"id": "q2", "prompt": "AD=200 روی Static Route دوم چه کاربردی دارد؟", "options": ["افزایش امنیت", "Floating Backup", "تغییر MTU", "فعالکردن OSPF"], "answer": 1, "explain": "تا زمانی که مسیر بهتر موجود است، مسیر با AD بالاتر inactive میماند."},
            {"id": "q3", "prompt": "علت رایج یکطرفهشدن ارتباط با Static Route چیست؟", "options": ["کمبود ARP", "نبود مسیر برگشت", "فعالبودن CDP", "MTU بزرگ"], "answer": 1, "explain": "روتر مقصد باید مسیری به سمت مبدأ داشته باشد."},
        ],
        "next": ["l08-ospf-neighbor-formation"], "simulationIds": [], "labIds": [], "exerciseId": "ex07-longest-match",
    },
    {
        "id": "l08-ospf-neighbor-formation",
        "title": "OSPF Neighbor Formation و ماشین حالتها",
        "courseId": "c04-routing-ospf", "chapterId": "p07-ospf-ch01", "pathId": "p07-ospf",
        "level": "متوسط", "durationMinutes": 60, "order": 8,
        "summary": "از Hello تا Full، شرایط همسایگی، DR/BDR و mismatchهای متداول را گامبهگام تحلیل میکنیم.",
        "objectives": ["نامبردن حالتهای Neighbor", "تشخیص پارامترهای لازم برای adjacency", "توضیح نقش DR/BDR در Broadcast"],
        "prerequisites": ["l07-static-routing"],
        "concept": "OSPF قبل از تبادل LSA باید همسایگی بسازد. Hello Packet پارامترهایی مانند Area ID، Timers، Authentication و Router ID را حمل میکند؛ ناسازگاری در همان ابتدا جلوی پیشروی را میگیرد.",
        "deep": "حالتها معمولاً Down، Attempt/Init، 2-Way، ExStart، Exchange، Loading و Full هستند. در شبکه Broadcast، DR/BDR انتخاب میشود و روترهای DROther با یکدیگر فقط تا 2-Way میروند، ولی با DR/BDR به Full میرسند. MTU mismatch اغلب در ExStart/Exchange متوقف میکند.",
        "diagram": {"caption": "ماشین حالت OSPF و پارامترهایی که باید دو سر یکسان باشند.", "nodes": [{"id": "down", "x": 90, "y": 140, "label": "Down", "sub": "no Hello"}, {"id": "init", "x": 250, "y": 140, "label": "Init", "sub": "Hello seen"}, {"id": "two", "x": 410, "y": 140, "label": "2-Way", "sub": "DR/BDR"}, {"id": "ex", "x": 570, "y": 140, "label": "ExStart/Exchange", "sub": "DBD / MTU"}, {"id": "full", "x": 760, "y": 140, "label": "Full", "sub": "LSDB sync"}], "edges": [{"from": "down", "to": "init", "label": "Hello"}, {"from": "init", "to": "two", "label": "2-way check"}, {"from": "two", "to": "ex", "label": "DR election"}, {"from": "ex", "to": "full", "label": "LSR/LSU"}]},
        "example": "دو روتر در Area 0 با Hello=10 و Dead=40 و MTU=1500 به Full میرسند. اگر Area یک سر 1 باشد، حالت در Init/2-Way متوقف میشود.",
        "scenario": "شبیهساز OSPF Area، Timer، Auth و MTU را تغییرپذیر میکند؛ هر mismatch دقیقاً در مرحله متناظر گزارش میشود.",
        "commands": [{"command": "router ospf 1", "explain": "فعالکردن فرایند OSPF با Process ID محلی ۱."}, {"command": "network 192.0.2.0 0.0.0.255 area 0", "explain": "فعالکردن OSPF روی اینترفیسهای منطبق با شبکه مستند."}, {"command": "passive-interface GigabitEthernet0/1", "explain": "جلوگیری از ارسال Hello روی پورت کاربران بدون حذف شبکه از Advertisement."}, {"command": "show ip ospf neighbor", "explain": "بررسی حالت همسایگی و DR/BDR."}],
        "walkthrough": [{"line": "router ospf 1", "explain": "Process ID محلی است و لازم نیست دو روتر یکسان باشد."}, {"line": "network ... area 0", "explain": "Wildcard Mask مشخص میکند کدام اینترفیسها Hello بفرستند."}, {"line": "show ip ospf neighbor", "explain": "FULL/DR یا FULL/BDR یعنی LSDB همزمان شده است."}],
        "sample": ["Sample / Simulated — Internal Simulator", "Neighbor ID  Pri  State   Dead Time  Address      Interface", "198.51.100.2  1   FULL/DR 00:00:34   192.0.2.2    Gi0/0"],
        "mistakes": ["یکسان پنداشتن Process ID و Area ID", "عدم تطابق Hello/Dead", "MTU متفاوت روی لینک"],
        "troubleshoot": ["`show ip ospf interface` برای Timer/Area/MTU و `show ip ospf neighbor` برای State را مقایسه کنید.", "لاگ `%OSPF-5-ADJCHG` نقطه شکست adjacency را نشان میدهد."],
        "key": ["Process ID محلی است؛ Area ID باید مشترک باشد.", "Hello/Dead و Auth و MTU باید سازگار باشند.", "در Broadcast، DROtherها با هم Full نمیشوند."],
        "version": "RFC 2328 OSPFv2 و RFC 5340 OSPFv3 را تعریف میکنند. رفتار `network` در IOS XE و نحوه پشتیبانی Authentication بین نسخهها ممکن است متفاوت باشد.",
        "refs": ["RFC2328", "RFC5340", "CISCO_IOS_XE"],
        "quiz": [
            {"id": "q1", "prompt": "کدام پارامتر لازم نیست دو سر OSPF یکسان باشد؟", "options": ["Area ID", "Hello Interval", "Process ID", "Dead Interval"], "answer": 2, "explain": "Process ID فقط محلی است."},
            {"id": "q2", "prompt": "MTU Mismatch معمولاً adjacency را در کدام مرحله متوقف میکند؟", "options": ["Down", "2-Way", "ExStart/Exchange", "Full"], "answer": 2, "explain": "تبادل DBD به MTU حساس است."},
            {"id": "q3", "prompt": "در شبکه Broadcast، DROther با DROther دیگر معمولاً چه حالتی دارد؟", "options": ["Full", "2-Way", "Loading", "Attempt"], "answer": 1, "explain": "فقط با DR/BDR به Full میرسند."},
        ],
        "next": ["l09-ospf-spf-cost"], "simulationIds": ["sim-ospf-neighbor"], "labIds": ["lab-ospf-single-area"], "exerciseId": "ex08-ospf-states",
    },
    {
        "id": "l09-ospf-spf-cost",
        "title": "OSPF SPF، Cost و انتخاب مسیر",
        "courseId": "c04-routing-ospf", "chapterId": "p07-ospf-ch02", "pathId": "p07-ospf",
        "level": "متوسط", "durationMinutes": 50, "order": 9,
        "summary": "الگوریتم Dijkstra، محاسبه Cost و اثر Bandwidth Reference را روی مسیر منتخب بررسی میکنیم.",
        "objectives": ["توضیح LSDB بهعنوان_graph", "محاسبه Cost تجمعی", "پیشبینی اثر `auto-cost reference-bandwidth`"],
        "prerequisites": ["l08-ospf-neighbor-formation"],
        "concept": "وقتی adjacency به Full رسید، روترها LSAها را در LSDB نگه میدارند. SPF یک گراف از روترها و لینکها میسازد و کوتاهترین مسیر را با جمع Costها محاسبه میکند.",
        "deep": "در Cisco، Cost پیشفرض هر لینک `reference-bandwidth / interface-bandwidth` است و Reference پیشفرض ۱۰۰Mbps است؛ بنابراین FastEthernet و GigabitEthernet هر دو Cost=1 میگیرند مگر اینکه Reference را بالا ببرید. OSPF فقط مسیرهای درون Area را با SPF کامل محاسبه میکند و بین Areaها از Summary LSA و قواعد ABR استفاده میشود.",
        "diagram": {"caption": "گراف سه روتر؛ مسیر مستقیم Cost=10 و مسیر دو Hopـه Cost=2+2=4 برنده است.", "nodes": [{"id": "r1", "x": 120, "y": 140, "label": "R1", "sub": "root of SPF"}, {"id": "r2", "x": 420, "y": 70, "label": "R2", "sub": "via 10Mbps"}, {"id": "r3", "x": 420, "y": 215, "label": "R3", "sub": "via 1Gbps"}, {"id": "r4", "x": 730, "y": 140, "label": "R4", "sub": "destination"}], "edges": [{"from": "r1", "to": "r2", "label": "cost 10"}, {"from": "r1", "to": "r3", "label": "cost 2"}, {"from": "r3", "to": "r4", "label": "cost 2"}, {"from": "r2", "to": "r4", "label": "cost 10"}]},
        "example": "R1 به R4 یا مستقیم از R2 با Cost 20 میرسد یا از R3 با Cost 4. SPF مسیر دوم را انتخاب میکند، حتی تعداد Hopها بیشتر است.",
        "scenario": "در تمرین، Reference Bandwidth را از 100 به 10000 تغییر دهید و ببینید Cost لینکهای سریع چگونه متمایز میشود.",
        "commands": [{"command": "router ospf 1", "explain": "ورود به پیکربندی فرایند OSPF."}, {"command": "auto-cost reference-bandwidth 10000", "explain": "تنظیم Reference به ۱۰Gbps؛ باید در تمام روترهای Area یکسان باشد."}, {"command": "show ip ospf interface brief", "explain": "نمایش Cost و وضعیت اینترفیسها."}, {"command": "show ip route ospf", "explain": "نمایش مسیرهای یادگرفتهشده از OSPF."}],
        "walkthrough": [{"line": "auto-cost reference-bandwidth 10000", "explain": "عدد بر حسب Mbps است و محاسبه Cost را تغییر میدهد."}, {"line": "show ip route ospf", "explain": "ستون `[110/cost]` شامل AD=110 و Cost نهایی است."}],
        "sample": ["Sample / Simulated — Internal Simulator", "O    203.0.113.0/24 [110/4] via 198.51.100.2, 00:00:12, Gi0/0"],
        "mistakes": ["تغییر Reference فقط روی یک روتر", "مقایسه Hop Count بهجای Cost", "فراموشکردن تفاوت Intra-area و Inter-area"],
        "troubleshoot": ["`show ip ospf database` و `show ip ospf interface` را با هم ببینید.", "اگر Costها غیرمنتظرهاند، Reference Bandwidth همه روترها را مقایسه کنید."],
        "key": ["OSPF مسیر را با جمع Cost انتخاب میکند.", "AD مسیر OSPF در IOS معمولاً ۱۱۰ است.", "Reference Bandwidth باید در سراسر Area یکسان باشد."],
        "version": "RFC 2328 متریک استاندارد را تعریف میکند، ولی فرمول پیشفرض Reference/Bandwidth رفتار vendor است. در OSPFv3 و شبکههای Multi-Area قواعد اضافی وجود دارد.",
        "refs": ["RFC2328", "CISCO_IOS_XE", "RFC5737"],
        "quiz": [
            {"id": "q1", "prompt": "معیار اصلی OSPF برای انتخاب کوتاهترین مسیر چیست؟", "options": ["Hop Count", "جمع Cost لینکها", "تعداد LSA", "AD مقصد"], "answer": 1, "explain": "Dijkstra کمترین Cost تجمعی را پیدا میکند."},
            {"id": "q2", "prompt": "[110/4] در خروجی `show ip route ospf` یعنی چه؟", "options": ["AD=4 و Cost=110", "AD=110 و Cost=4", "4 Hop و 110ms", "Area 110"], "answer": 1, "explain": "عدد اول AD و دوم Cost است."},
            {"id": "q3", "prompt": "چرا Reference Bandwidth باید یکسان باشد؟", "options": ["برای جلوگیری از Loop", "برای محاسبه Cost سازگار", "برای فعالکردن DR", "برای کاهش Hello"], "answer": 1, "explain": "در غیر این صورت روترها یک لینک را با Cost متفاوت میبینند."},
        ],
        "next": ["l10-acl-filtering"], "simulationIds": ["sim-ospf-neighbor"], "labIds": ["lab-ospf-single-area"], "exerciseId": "ex09-spf-cost",
    },
    {
        "id": "l10-acl-filtering",
        "title": "ACL Packet Filtering و Wildcard Mask",
        "courseId": "c05-network-security", "chapterId": "p11-acl-security-ch01", "pathId": "p11-acl-security",
        "level": "متوسط", "durationMinutes": 55, "order": 10,
        "summary": "منطق Top-down ACL، Standard/Extended و محل اعمال آنها را با سناریوی امن تحلیل میکنیم.",
        "objectives": ["تفسیر ACE و Implicit Deny", "محاسبه Wildcard Mask", "انتخاب محل مناسب Standard و Extended ACL"],
        "prerequisites": ["l05-ipv4-subnetting", "l07-static-routing"],
        "concept": "ACL فهرستی ترتیبی از قواعد permit/deny است. اولین قانون منطبق اعمال میشود و در انتها یک Implicit Deny وجود دارد که در خروجی نمایش داده نمیشود.",
        "deep": "Standard ACL فقط Source IP را بررسی میکند و بهتر است نزدیک مقصد اعمال شود تا مسیرهای دیگر ناخواسته بسته نشوند. Extended ACL میتواند Source، Destination، Protocol و Port را بررسی کند و معمولاً نزدیک مبدأ قرار میگیرد تا ترافیک غیرمجاز زودتر حذف شود. Wildcard Mask برعکس Subnet Mask است: بیت ۱ یعنی «اهمیتی ندارد».",
        "diagram": {"caption": "یک Extended ACL نزدیک مبدأ، ترافیک Telnet را پیش از ورود به Backbone حذف میکند.", "nodes": [{"id": "u", "x": 110, "y": 140, "label": "Users", "sub": "192.0.2.0/24"}, {"id": "r", "x": 380, "y": 140, "label": "Edge Router", "sub": "ACL IN"}, {"id": "srv", "x": 700, "y": 140, "label": "Server", "sub": "203.0.113.10"}], "edges": [{"from": "u", "to": "r", "label": "TCP 23 denied"}, {"from": "r", "to": "srv", "label": "HTTPS permitted"}]},
        "example": "برای جلوگیری از Telnet کاربران 192.0.2.0/24 به سرور 203.0.113.10، Extended ACL نزدیک مبدأ نوشته میشود و در انتها `permit ip any any` بقیه ترافیک را مجاز میکند.",
        "scenario": "در تمرین، ترتیب ACEها را جابهجا کنید تا ببینید چگونه یک `permit ip any any` زودهنگام، قانون deny بعدی را بیه اثر میکند.",
        "commands": [{"command": "ip access-list extended EDGE-IN", "explain": "ساخت یک Named Extended ACL."}, {"command": "deny tcp 192.0.2.0 0.0.0.255 host 203.0.113.10 eq 23", "explain": "مسدودکردن Telnet از سابنت کاربران به سرور مستند."}, {"command": "permit ip any any", "explain": "مجازکردن سایر ترافیکها پس از قانون deny."}, {"command": "interface GigabitEthernet0/0", "explain": "انتخاب اینترفیس ورودی نزدیک مبدأ."}, {"command": "ip access-group EDGE-IN in", "explain": "اعمال ACL در جهت Inbound."}, {"command": "show access-lists EDGE-IN", "explain": "نمایش شمارندهها و ترتیب قواعد."}],
        "walkthrough": [{"line": "deny tcp ... eq 23", "explain": "Wildcard `0.0.0.255` یعنی ۲۴ بیت اول دقیق و octet آخر آزاد است."}, {"line": "permit ip any any", "explain": "بدون این خط، Implicit Deny بقیه ترافیک را حذف میکند."}, {"line": "ip access-group EDGE-IN in", "explain": "جهت اعمال بسیار مهم است؛ in یعنی بستهها پیش از تصمیم Routing بررسی میشوند."}],
        "sample": ["Sample / Simulated — Internal Simulator", "Extended IP access list EDGE-IN", "10 deny tcp 192.0.2.0 0.0.0.255 host 203.0.113.10 eq telnet (3 matches)", "20 permit ip any any (17 matches)"],
        "mistakes": ["قراردادن `permit any` پیش از deny", "فراموشکردن Implicit Deny", "استفاده از Subnet Mask بهجای Wildcard"],
        "troubleshoot": ["`show access-lists` شمارندهها را نشان میدهد؛ اگر قانون درست افزایش نمییابد، جهت یا محل ACL اشتباه است.", "تست را با یک منبع و مقصد مشخص آغاز کنید، سپس قواعد را محدود کنید."],
        "key": ["اولین Match تصمیم نهایی است.", "Standard ACL نزدیک مقصد؛ Extended ACL نزدیک مبدأ.", "Wildcard بیت ۱ یعنی Wildcard/Ignore."],
        "version": "منطق ACE در مستندات Cisco توضیح داده شده؛ نحو Named ACL و شماره خطوط بین IOS و IOS XE تفاوتهای جزئی دارد. ACLهای IPv6 ساختار جداگانه دارند.",
        "refs": ["CISCO_IOS_XE", "RFC5737", "RFC793"],
        "quiz": [
            {"id": "q1", "prompt": "آخرین قاعده نادیده در یک ACL IPv4 Cisco چیست؟", "options": ["permit any", "deny any", "log all", "reset counters"], "answer": 1, "explain": "Implicit Deny همه ترافیک باقیمانده را حذف میکند."},
            {"id": "q2", "prompt": "Wildcard متناظر /24 چیست؟", "options": ["255.255.255.0", "0.0.0.255", "0.0.0.0", "255.255.0.0"], "answer": 1, "explain": "بیتهای صفر یعنی دقیق، بیتهای یک یعنی آزاد."},
            {"id": "q3", "prompt": "Extended ACL معمولاً کجا اعمال میشود؟", "options": ["نزدیک مبدأ", "نزدیک مقصد", "روی سوئیچ لایه ۲", "فقط روی Loopback"], "answer": 0, "explain": "چون میتواند مقصد و پورت را تشخیص دهد، حذف زودهنگام ترافیک بهینهتر است."},
        ],
        "next": [], "simulationIds": [], "labIds": [], "exerciseId": "ex10-acl-order",
    },
]


LIVE_COURSES = {
    "c01-network-fundamentals": {
        "pathId": "p01-network-fundamentals", "title": "دوره مبانی شبکه و مدلهای ارتباطی", "level": "پایه", "status": "live",
        "summary": "دو درس کامل برای درک Encapsulation، Ethernet و ARP قبل از ورود به Switching.",
        "prerequisites": [], "objectives": OBJECTIVES["p01-network-fundamentals"], "nextPaths": ["p02-ethernet-switching", "p04-ipv4-ipv6-subnetting"],
        "chapters": [{"id": "p01-network-fundamentals-ch01", "title": "لایهها، Frame و کشف آدرس", "lessonIds": ["l01-osi-tcpip-encapsulation", "l02-ethernet-arp"], "exerciseIds": ["ex01-packet-layers", "ex02-arp-cache"], "labIds": [], "status": "live"}],
    },
    "c02-switching-vlan": {
        "pathId": "p03-vlan-stp-etherchannel", "title": "دوره VLAN، Trunk و Switching", "level": "متوسط", "status": "live",
        "summary": "دو درس متصل به شبیهساز VLAN/Trunk و آزمایشگاه پیکربندی سوئیچ.",
        "prerequisites": ["p01-network-fundamentals", "p02-ethernet-switching"], "objectives": OBJECTIVES["p03-vlan-stp-etherchannel"], "nextPaths": ["p07-ospf"],
        "chapters": [{"id": "p03-vlan-stp-etherchannel-ch01", "title": "Access، Trunk و 802.1Q", "lessonIds": ["l03-vlan-access-ports", "l04-trunk-8021q"], "exerciseIds": ["ex03-vlan-access", "ex04-trunk-allowed"], "labIds": ["lab-vlan-trunk"], "status": "live"}],
    },
    "c03-ip-addressing": {
        "pathId": "p04-ipv4-ipv6-subnetting", "title": "دوره IPv4، IPv6 و Subnetting", "level": "متوسط", "status": "live",
        "summary": "محاسبه prefix، VLSM، آدرسهای IPv6 و Neighbor Discovery.",
        "prerequisites": ["p01-network-fundamentals"], "objectives": OBJECTIVES["p04-ipv4-ipv6-subnetting"], "nextPaths": ["p05-routing-concepts"],
        "chapters": [{"id": "p04-ipv4-ipv6-subnetting-ch01", "title": "آدرسدهی و طراحی سابنت", "lessonIds": ["l05-ipv4-subnetting", "l06-ipv6-addressing"], "exerciseIds": ["ex05-vlsm", "ex06-ipv6-prefix"], "labIds": [], "status": "live"}],
    },
    "c04-routing-ospf": {
        "pathId": "p07-ospf", "title": "دوره Routing و OSPF", "level": "متوسط", "status": "live",
        "summary": "سه درس پیوسته از Routing Table تا Neighbor Formation و SPF، همراه با آزمایشگاه OSPF.",
        "prerequisites": ["p04-ipv4-ipv6-subnetting", "p05-routing-concepts", "p06-static-dynamic-routing"], "objectives": OBJECTIVES["p07-ospf"], "nextPaths": ["p10-advanced-switching-routing"],
        "chapters": [{"id": "p07-ospf-ch01", "title": "مسیریابی و همسایگی", "lessonIds": ["l07-static-routing", "l08-ospf-neighbor-formation"], "exerciseIds": ["ex07-longest-match", "ex08-ospf-states"], "labIds": ["lab-ospf-single-area"], "status": "live"}, {"id": "p07-ospf-ch02", "title": "SPF و Cost", "lessonIds": ["l09-ospf-spf-cost"], "exerciseIds": ["ex09-spf-cost"], "labIds": [], "status": "live"}],
    },
    "c05-network-security": {
        "pathId": "p11-acl-security", "title": "دوره ACL و امنیت شبکه", "level": "متوسط", "status": "live",
        "summary": "یک درس کامل درباره منطق فیلتر بستهها، Wildcard Mask و محل اعمال ACL.",
        "prerequisites": ["p04-ipv4-ipv6-subnetting", "p02-ethernet-switching"], "objectives": OBJECTIVES["p11-acl-security"], "nextPaths": ["p12-nat-services", "p15-vpn-ipsec"],
        "chapters": [{"id": "p11-acl-security-ch01", "title": "فیلتر کردن ترافیک", "lessonIds": ["l10-acl-filtering"], "exerciseIds": ["ex10-acl-order"], "labIds": [], "status": "live"}],
    },
}


for _course_id, _course in LIVE_COURSES.items():
    _course["id"] = _course_id
LIVE_COURSES_BY_PATH = {_course["pathId"]: _course for _course in LIVE_COURSES.values()}


EXERCISES = [
    {"id": "ex01-packet-layers", "lessonId": "l01-osi-tcpip-encapsulation", "title": "ردیابی لایههای یک بسته", "prompt": "برای یک درخواست HTTP به 203.0.113.10، مشخص کنید در هر Hop کدام فیلد تغییر میکند و کدام ثابت میماند.", "hint": "IP مقصد نهایی vs MAC مقصد Hop بعدی.", "expected": "IP مقصد ثابت است؛ MAC مقصد و TTL در هر Hop تغییر میکنند."},
    {"id": "ex02-arp-cache", "lessonId": "l02-ethernet-arp", "title": "تأثیر ARP Cache", "prompt": "اگر ورودی 192.0.2.20 از قبل در Cache باشد، کدام پیامها حذف میشوند؟", "hint": "Request و Reply تنها زمانی لازماند که MAC ناشناخته باشد.", "expected": "ARP Request Broadcast و Reply Unicast حذف میشوند و فریم مستقیماً ساخته میشود."},
    {"id": "ex03-vlan-access", "lessonId": "l03-vlan-access-ports", "title": "تشخیص VLAN اشتباه", "prompt": "کلاینتی در VLAN 10 نمیتواند Gateway خود را پیدا کند؛ دو دلیل لایه ۲ بنویسید.", "hint": "پورت Access و جدول MAC.", "expected": "پورت در VLAN اشتباه است یا Gateway/SVI در VLAN دیگری قرار دارد."},
    {"id": "ex04-trunk-allowed", "lessonId": "l04-trunk-8021q", "title": "Allowed List", "prompt": "VLAN 30 روی هر دو سوئیچ وجود دارد ولی ارتباط برقرار نیست؛ کدام خروجی را بررسی میکنید؟", "hint": "show interfaces trunk.", "expected": "باید VLAN 30 به Allowed VLAN List دو سر اضافه شود."},
    {"id": "ex05-vlsm", "lessonId": "l05-ipv4-subnetting", "title": "طراحی VLSM بدون همپوشانی", "prompt": "برای نیازهای ۵۰، ۲۵، ۱۰ و ۲ Host از 198.51.100.0/24 prefixها را پیشنهاد دهید.", "hint": "از بزرگترین نیاز شروع کنید.", "expected": "/26، /27، /28 و /30 بهترتیب، بدون همپوشانی."},
    {"id": "ex06-ipv6-prefix", "lessonId": "l06-ipv6-addressing", "title": "نوع آدرس IPv6", "prompt": "آدرس fe80::1 را طبقهبندی کنید و بگویید آیا از روتر عبور میکند.", "hint": "fe80::/10.", "expected": "Link-local است و فقط همان لینک معتبر است؛ روتر آن را Forward نمیکند."},
    {"id": "ex07-longest-match", "lessonId": "l07-static-routing", "title": "پیشبینی مسیر", "prompt": "با /24 via R2 و /25 via R3، مقصد 203.0.113.10 کدام مسیر را میگیرد؟", "hint": "longest prefix first.", "expected": "/25 via R3، هرچند AD ممکن است بالاتر باشد."},
    {"id": "ex08-ospf-states", "lessonId": "l08-ospf-neighbor-formation", "title": "عیبیابی OSPF", "prompt": "همسایگی در ExStart مانده است؛ سه پارامتر مشکوک را نام ببرید.", "hint": "DBD exchange.", "expected": "MTU، Router ID تکراری و mismatch مربوط به DBD/Options."},
    {"id": "ex09-spf-cost", "lessonId": "l09-ospf-spf-cost", "title": "محاسبه Cost", "prompt": "مسیر R1-R3-R4 با Costهای ۲ و ۲ در مقابل R1-R2-R4 با ۱۰ و ۱۰، کدام برنده است؟", "hint": "جمع Cost.", "expected": "جمع ۴ برنده میشود، حتی با تعداد Hop ظاهری بیشتر."},
    {"id": "ex10-acl-order", "lessonId": "l10-acl-filtering", "title": "ترتیب ACE", "prompt": "چرا deny بعد از `permit ip any any` هیچگاه دیده نمیشود؟", "hint": "first match.", "expected": "قانون permit زودتر منطبق میشود و بررسی متوقف میگردد."},
]


SIMULATIONS = [
    {
        "id": "sim-arp-discovery", "title": "ARP و فرایند کشف MAC", "logic": "arpResolve",
        "objective": "نشان دادن تفاوت مقصد محلی/remote، اثر Cache و ساخت Ethernet Frame.",
        "lessonIds": ["l01-osi-tcpip-encapsulation", "l02-ethernet-arp"],
        "parameters": [
            {"id": "sourceIp", "label": "IP مبدأ", "type": "text", "default": "192.0.2.10"},
            {"id": "targetIp", "label": "IP مقصد", "type": "text", "default": "192.0.2.20"},
            {"id": "mask", "label": "Prefix طول", "type": "number", "default": 24, "min": 8, "max": 30},
            {"id": "gatewayIp", "label": "Default Gateway", "type": "text", "default": "192.0.2.1"},
            {"id": "cacheHit", "label": "ورودی از قبل در Cache", "type": "checkbox", "default": False},
            {"id": "vlanId", "label": "VLAN", "type": "number", "default": 10, "min": 1, "max": 4094},
        ],
        "steps": ["بررسی سابنت", "تصمیم مقصد ARP", "ارسال درخواست یا استفاده از Cache", "دریافت پاسخ", "ساخت Frame نهایی"],
        "limitations": ["مدل ساده /8 تا /30 IPv4؛ Proxy ARP، Gratuitous ARP و VLAN ACL مدل نشدهاند.", "MACها و زمانها نمونهاند و خروجی واقعی دستگاه نیستند."],
        "references": ["RFC826", "IEEE8023", "RFC4861"],
        "diagram": {"caption": "توپولوژی ARP: یک Broadcast Domain و یک Gateway.", "nodes": [{"id": "a", "x": 130, "y": 140, "label": "Host A", "sub": "192.0.2.10"}, {"id": "s", "x": 410, "y": 140, "label": "Switch", "sub": "VLAN"}, {"id": "b", "x": 700, "y": 80, "label": "Target / Gateway", "sub": "192.0.2.20"}], "edges": [{"from": "a", "to": "s", "label": "ARP Request"}, {"from": "s", "to": "b", "label": "Flood"}]},
    },
    {
        "id": "sim-vlan-trunk", "title": "VLAN و Trunk 802.1Q", "logic": "vlanForward",
        "objective": "مشاهده اثر VLAN مبدأ/مقصد، Allowed List، Native VLAN و Tag بر تحویل فریم.",
        "lessonIds": ["l03-vlan-access-ports", "l04-trunk-8021q"],
        "parameters": [
            {"id": "sourceVlan", "label": "VLAN مبدأ", "type": "number", "default": 10, "min": 1, "max": 4094},
            {"id": "destinationVlan", "label": "VLAN مقصد", "type": "number", "default": 10, "min": 1, "max": 4094},
            {"id": "trunkAllowed", "label": "VLANهای مجاز", "type": "text", "default": "10,20,99"},
            {"id": "nativeVlan", "label": "Native VLAN سر مبدأ", "type": "number", "default": 99, "min": 1, "max": 4094},
            {"id": "remoteNativeVlan", "label": "Native VLAN سر مقصد", "type": "number", "default": 99, "min": 1, "max": 4094},
            {"id": "tagNative", "label": "Tag کردن Native VLAN", "type": "checkbox", "default": False},
        ],
        "steps": ["دریافت فریم از پورت Access", "بررسی Allowed List", "تصمیم Tag/Untagged", "عبور از Trunk", "تحویل در VLAN مقصد"],
        "limitations": ["فقط یک لینک Trunk و یک Broadcast Domain مدل شده؛ STP، DTP و VTP مدل نشدهاند.", "Inter-VLAN Routing بهعنوان نیاز خارجی گزارش میشود، ولی پیادهسازی نشده است."],
        "references": ["IEEE8021Q", "CISCO_IOS_XE"],
        "diagram": {"caption": "مسیر فریم از پورت Access تا پورت مقصد روی Trunk.", "nodes": [{"id": "a", "x": 120, "y": 140, "label": "Access src", "sub": "untagged"}, {"id": "s1", "x": 360, "y": 140, "label": "SW1", "sub": "tag decision"}, {"id": "s2", "x": 620, "y": 140, "label": "SW2", "sub": "native check"}, {"id": "b", "x": 800, "y": 140, "label": "Access dst", "sub": "untagged"}], "edges": [{"from": "a", "to": "s1", "label": "frame in"}, {"from": "s1", "to": "s2", "label": "trunk"}, {"from": "s2", "to": "b", "label": "frame out"}]},
    },
    {
        "id": "sim-ospf-neighbor", "title": "OSPF Neighbor Formation", "logic": "ospfAdjacency",
        "objective": "پیمایش ماشین حالت OSPF و مشاهده اثر mismatch پارامترها.",
        "lessonIds": ["l08-ospf-neighbor-formation", "l09-ospf-spf-cost"],
        "parameters": [
            {"id": "areaId", "label": "Area مبدأ", "type": "text", "default": "0"},
            {"id": "remoteAreaId", "label": "Area مقصد", "type": "text", "default": "0"},
            {"id": "hello", "label": "Hello مبدأ (s)", "type": "number", "default": 10, "min": 1, "max": 60},
            {"id": "remoteHello", "label": "Hello مقصد (s)", "type": "number", "default": 10, "min": 1, "max": 60},
            {"id": "dead", "label": "Dead مبدأ (s)", "type": "number", "default": 40, "min": 4, "max": 240},
            {"id": "remoteDead", "label": "Dead مقصد (s)", "type": "number", "default": 40, "min": 4, "max": 240},
            {"id": "auth", "label": "Auth مبدأ", "type": "select", "default": "none", "options": ["none", "md5"]},
            {"id": "remoteAuth", "label": "Auth مقصد", "type": "select", "default": "none", "options": ["none", "md5"]},
            {"id": "mtu", "label": "MTU مبدأ", "type": "number", "default": 1500, "min": 576, "max": 9000},
            {"id": "remoteMtu", "label": "MTU مقصد", "type": "number", "default": 1500, "min": 576, "max": 9000},
            {"id": "networkType", "label": "نوع شبکه", "type": "select", "default": "broadcast", "options": ["broadcast", "point-to-point"]},
            {"id": "priority", "label": "Priority روتر", "type": "number", "default": 1, "min": 0, "max": 255},
        ],
        "steps": ["Down", "Init", "2-Way", "ExStart", "Exchange", "Loading", "Full"],
        "limitations": ["مدل آموزشی OSPFv2 است؛ LSA flooding کامل، NBMA و OSPFv3 پیادهسازی نشدهاند.", "انتخاب DR/BDR بهصورت ساده و بر اساس Priority مدل شده است."],
        "references": ["RFC2328", "RFC5340", "CISCO_IOS_XE"],
        "diagram": {"caption": "دو روتر و پارامترهایی که پیش از Full باید سازگار باشند.", "nodes": [{"id": "r1", "x": 180, "y": 140, "label": "R1", "sub": "Area / Hello / MTU"}, {"id": "r2", "x": 680, "y": 140, "label": "R2", "sub": "Area / Hello / MTU"}], "edges": [{"from": "r1", "to": "r2", "label": "Hello → DBD → LSR → LSU"}]},
    },
]


LABS = [
    {
        "id": "lab-vlan-trunk", "title": "آزمایشگاه VLAN و Trunk روی دو سوئیچ",
        "lessonIds": ["l03-vlan-access-ports", "l04-trunk-8021q"],
        "scenario": "دو کلاینت در VLAN 10 و VLAN 20 به دو سوئیچ متصلاند و لینک بین سوئیچها باید فقط VLANهای تعیینشده را حمل کند.",
        "objectives": ["ساخت VLANها", "تخصیص پورتهای Access", "پیکربندی Trunk و Allowed List", "بررسی Native VLAN"],
        "executionMode": "internal-simulator", "realDeviceConnection": False,
        "status": "Designed — Simulated, Not Run on Real Device",
        "topology": {"summary": "SW1 و SW2 از طریق Gi0/24؛ PC-A روی Gi0/1 و PC-B روی Gi0/2.", "diagramPath": web_path("assets/diagrams/lab-vlan-trunk.svg"), "devices": ["SW1", "SW2", "PC-A", "PC-B"]},
        "addressingTable": [{"device": "PC-A", "interface": "NIC", "address": "192.0.2.10", "mask": "255.255.255.0", "gateway": "192.0.2.1", "vlan": "10"}, {"device": "PC-B", "interface": "NIC", "address": "192.0.2.20", "mask": "255.255.255.0", "gateway": "192.0.2.1", "vlan": "20"}, {"device": "SW1", "interface": "Vlan99", "address": "192.0.2.2", "mask": "255.255.255.0", "gateway": "-", "vlan": "99"}],
        "equipment": ["۲ سوئیچ لایه ۲ با پشتیبانی 802.1Q", "۲ کلاینت", "کابلهای Ethernet", "Simulator داخلی FAM Academy"],
        "steps": [
            {"id": "s1", "title": "ساخت VLANها", "commands": ["enable", "configure terminal", "vlan 10", "name Users", "vlan 20", "name Servers", "vlan 99", "name Management"], "expectedState": "VLAN 10، 20 و 99 ایجاد شدهاند."},
            {"id": "s2", "title": "تخصیص پورت Access", "commands": ["interface GigabitEthernet0/1", "switchport mode access", "switchport access vlan 10", "no shutdown", "exit", "interface GigabitEthernet0/2", "switchport mode access", "switchport access vlan 20", "no shutdown", "exit"], "expectedState": "Gi0/1 در VLAN 10 و Gi0/2 در VLAN 20 است."},
            {"id": "s3", "title": "پیکربندی Trunk", "commands": ["interface GigabitEthernet0/24", "switchport mode trunk", "switchport trunk allowed vlan 10,20,99", "switchport trunk native vlan 99", "no shutdown", "end"], "expectedState": "Trunk با Allowed List و Native VLAN 99 فعال است."},
            {"id": "s4", "title": "اعتبارسنجی", "commands": ["show vlan brief", "show interfaces trunk", "show interfaces status"], "expectedState": "خروجیها VLANها، Trunk و وضعیت پورتها را نشان میدهند."},
            {"id": "s5", "title": "سناریوی خرابی", "commands": ["configure terminal", "interface GigabitEthernet0/24", "switchport trunk allowed vlan 10,99", "end", "show interfaces trunk"], "expectedState": "VLAN 20 دیگر در Allowed List نیست و ترافیک آن از Trunk عبور نمیکند."},
        ],
        "expectedOutput": {"label": "Sample / Simulated — Internal Simulator", "lines": ["VLAN 10 Users active Gi0/1", "VLAN 20 Servers active Gi0/2", "Gi0/24 on 802.1q trunking native 99", "Allowed VLANs: 10,20,99"]},
        "reviewQuestions": ["چرا VLAN 20 در مرحله خرابی دیگر عبور نمیکند؟", "اگر Native VLAN دو سر متفاوت باشد چه رخ میدهد؟", "برای ارتباط PC-A و PC-B چه لایهای لازم است؟"],
        "failureScenario": "Allowed VLAN List در یک سر Trunk فاقد VLAN 20 است.",
        "troubleshooting": ["`show interfaces trunk` را در هر دو سوئیچ مقایسه کنید.", "سپس `show vlan brief` و پورت Access مربوطه را بررسی کنید."],
        "successCriteria": ["هر چهار مرحله نخست اجرا شود", "خروجی `show interfaces trunk` شامل VLAN 10، 20 و 99 باشد", "هیچ اتصال به تجهیز واقعی برقرار نشود"],
        "references": ["IEEE8021Q", "CISCO_IOS_XE"],
        "futureIntegration": {"enabled": False, "pnetlab": "planned", "eveNg": "planned", "realDevices": "disabled", "note": "This mission uses an internal simulator only; no SSH/Telnet or operational connection is opened."},
        "diagram": {"caption": "توپولوژی آزمایشگاه VLAN/Trunk", "nodes": [{"id": "a", "x": 100, "y": 80, "label": "PC-A", "sub": "VLAN 10"}, {"id": "b", "x": 100, "y": 210, "label": "PC-B", "sub": "VLAN 20"}, {"id": "s1", "x": 340, "y": 145, "label": "SW1", "sub": "Gi0/24"}, {"id": "s2", "x": 620, "y": 145, "label": "SW2", "sub": "Gi0/24"}], "edges": [{"from": "a", "to": "s1", "label": "access 10"}, {"from": "b", "to": "s1", "label": "access 20"}, {"from": "s1", "to": "s2", "label": "trunk 10,20,99"}]},
    },
    {
        "id": "lab-ospf-single-area", "title": "آزمایشگاه OSPF Single-Area بین دو روتر",
        "lessonIds": ["l08-ospf-neighbor-formation", "l09-ospf-spf-cost"],
        "scenario": "دو روتر R1 و R2 روی یک لینک مستند 192.0.2.0/30 در Area 0 همسایه میشوند و شبکه Loopback یکدیگر را یاد میگیرند.",
        "objectives": ["آدرسدهی اینترفیسها", "فعالکردن OSPF", "بررسی Full adjacency", "مشاهده مسیر OSPF"],
        "executionMode": "internal-simulator", "realDeviceConnection": False,
        "status": "Designed — Simulated, Not Run on Real Device",
        "topology": {"summary": "R1 و R2 از طریق Gi0/0؛ Loopbackها شبکههای 198.51.100.0/24 و 203.0.113.0/24 را اعلام میکنند.", "diagramPath": web_path("assets/diagrams/lab-ospf-single-area.svg"), "devices": ["R1", "R2"]},
        "addressingTable": [{"device": "R1", "interface": "Gi0/0", "address": "192.0.2.1", "mask": "255.255.255.252", "gateway": "-", "area": "0"}, {"device": "R1", "interface": "Loopback0", "address": "198.51.100.1", "mask": "255.255.255.0", "gateway": "-", "area": "0"}, {"device": "R2", "interface": "Gi0/0", "address": "192.0.2.2", "mask": "255.255.255.252", "gateway": "-", "area": "0"}, {"device": "R2", "interface": "Loopback0", "address": "203.0.113.1", "mask": "255.255.255.0", "gateway": "-", "area": "0"}],
        "equipment": ["۲ روتر با پشتیبانی OSPFv2", "یک لینک Point-to-Point", "Simulator داخلی FAM Academy"],
        "steps": [
            {"id": "s1", "title": "آدرسدهی R1", "commands": ["enable", "configure terminal", "hostname R1", "interface GigabitEthernet0/0", "ip address 192.0.2.1 255.255.255.252", "no shutdown", "exit", "interface Loopback0", "ip address 198.51.100.1 255.255.255.0", "exit"], "expectedState": "اینترفیسهای R1 آدرس گرفتهاند."},
            {"id": "s2", "title": "فعالکردن OSPF", "commands": ["router ospf 1", "network 192.0.2.0 0.0.0.3 area 0", "network 198.51.100.0 0.0.0.255 area 0", "end"], "expectedState": "فرایند OSPF شبکههای متصل را اعلام میکند."},
            {"id": "s3", "title": "پیکربندی R2", "commands": ["configure terminal", "hostname R2", "interface GigabitEthernet0/0", "ip address 192.0.2.2 255.255.255.252", "no shutdown", "exit", "interface Loopback0", "ip address 203.0.113.1 255.255.255.0", "exit", "router ospf 1", "network 192.0.2.0 0.0.0.3 area 0", "network 203.0.113.0 0.0.0.255 area 0", "end"], "expectedState": "R2 نیز در Area 0 قرار دارد."},
            {"id": "s4", "title": "بررسی همسایگی", "commands": ["show ip ospf neighbor", "show ip route ospf"], "expectedState": "همسایگی FULL و مسیر OSPF دیده میشود."},
            {"id": "s5", "title": "سناریوی خرابی", "commands": ["configure terminal", "router ospf 1", "network 192.0.2.0 0.0.0.3 area 1", "end", "show ip ospf neighbor"], "expectedState": "Area mismatch باعث عدم تشکیل adjacency میشود."},
        ],
        "expectedOutput": {"label": "Sample / Simulated — Internal Simulator", "lines": ["Neighbor ID  Pri  State   Dead Time  Address     Interface", "203.0.113.1   1   FULL/DR 00:00:34  192.0.2.2   Gi0/0", "O 203.0.113.0/24 [110/2] via 192.0.2.2"]},
        "reviewQuestions": ["چرا Process ID الزاماً یکسان نیست ولی Area ID باید یکسان باشد؟", "کدام خروجی نشاندهنده LSDB synchronized است؟", "MTU mismatch در کدام حالت ظاهر میشود؟"],
        "failureScenario": "Area ID یک سر از 0 به 1 تغییر میکند.",
        "troubleshooting": ["`show ip ospf interface` و `show ip ospf neighbor` را مقایسه کنید.", "سپس لاگ تغییر adjacency را بررسی کنید."],
        "successCriteria": ["چهار مرحله نخست اجرا شود", "خروجی `show ip ospf neighbor` حالت FULL داشته باشد", "هیچ اتصال به تجهیز واقعی برقرار نشود"],
        "references": ["RFC2328", "CISCO_IOS_XE", "RFC5737"],
        "futureIntegration": {"enabled": False, "pnetlab": "planned", "eveNg": "planned", "realDevices": "disabled", "note": "Future adapter can map these steps to PNETLab/EVE-NG, but it is not enabled here."},
        "diagram": {"caption": "توپولوژی آزمایشگاه OSPF", "nodes": [{"id": "r1", "x": 180, "y": 140, "label": "R1", "sub": "192.0.2.1/30"}, {"id": "r2", "x": 660, "y": 140, "label": "R2", "sub": "192.0.2.2/30"}, {"id": "l1", "x": 180, "y": 60, "label": "Lo0 R1", "sub": "198.51.100.1"}, {"id": "l2", "x": 660, "y": 220, "label": "Lo0 R2", "sub": "203.0.113.1"}], "edges": [{"from": "r1", "to": "r2", "label": "Area 0"}, {"from": "l1", "to": "r1", "label": "advertise"}, {"from": "r2", "to": "l2", "label": "advertise"}]},
    },
]


SCHEMA_DEFS = {
    "catalog.schema.json": {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "fam-academy-v1/catalog",
        "title": "FAM Academy v2 Catalog", "type": "object",
        "required": ["schemaVersion", "contentVersion", "language", "direction", "paths", "courses", "lessons", "simulations", "labs"],
        "properties": {"schemaVersion": {"const": "fam-academy-v1"}, "contentVersion": {"type": "string"}, "language": {"const": "fa"}, "direction": {"const": "rtl"}, "paths": {"type": "array", "minItems": 23}, "courses": {"type": "array", "minItems": 23}, "lessons": {"type": "array", "minItems": 10}, "simulations": {"type": "array", "minItems": 3}, "labs": {"type": "array", "minItems": 2}},
    },
    "lesson.schema.json": {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "fam-academy-v1/lesson",
        "title": "FAM Academy Lesson", "type": "object",
        "required": ["id", "title", "level", "durationMinutes", "objectives", "prerequisites", "sections", "references", "quiz", "diagramPath", "simulationIds", "labIds", "exerciseId", "status"],
        "properties": {"id": {"type": "string"}, "title": {"type": "string"}, "level": {"enum": ["پایه", "متوسط", "پیشرفته"]}, "durationMinutes": {"type": "integer", "minimum": 20}, "objectives": {"type": "array", "minItems": 3}, "sections": {"type": "object", "minProperties": 16}, "quiz": {"type": "array", "minItems": 3}},
    },
    "simulation.schema.json": {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "fam-academy-v1/simulation",
        "title": "FAM Academy Simulation", "type": "object",
        "required": ["id", "title", "logic", "objective", "parameters", "steps", "limitations", "references", "diagramPath", "lessonIds"],
        "properties": {"parameters": {"type": "array", "minItems": 3}, "steps": {"type": "array", "minItems": 4}, "logic": {"enum": ["arpResolve", "vlanForward", "ospfAdjacency"]}},
    },
    "lab.schema.json": {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "fam-academy-v1/lab",
        "title": "FAM Academy Lab", "type": "object",
        "required": ["id", "title", "scenario", "objectives", "executionMode", "realDeviceConnection", "topology", "addressingTable", "equipment", "steps", "expectedOutput", "reviewQuestions", "failureScenario", "troubleshooting", "successCriteria", "lessonIds"],
        "properties": {"executionMode": {"const": "internal-simulator"}, "realDeviceConnection": {"const": False}, "steps": {"type": "array", "minItems": 5}},
    },
}


def build_lesson(spec: dict) -> dict:
    refs = spec["refs"]
    ref_titles = [REFERENCES[r]["title"] for r in refs]
    commands_body = ["دستورات مرتبط Cisco IOS در ادامه آمدهاند؛ نحو دقیق باید با نسخه پلتفرم هدف تطبیق داده شود."] if spec["commands"] else ["این درس عمدتاً مفهومی است؛ دستور IOS مستقیمی برای اجرای اصل مفهوم لازم نیست. خروجی زیر همچنان نمونهای شبیهسازیشده است."]
    quiz_body = ["آزمون کوتاه شامل پرسشهای سناریومحور است؛ پاسخ تشریحی پس از ثبت نمایش داده میشود."]
    next_body = ["پس از این درس، مسیر زیر پیشنهاد میشود: " + ("، ".join(spec["next"]) if spec["next"] else "پایان مسیر فعلی؛ بازگشت به داشبورد و انتخاب مسیر بعدی.")]
    sections = {
        "concept": {"title": "توضیح مفهومی", "body": [spec["concept"]]},
        "deepDive": {"title": "توضیح عمیق", "body": [spec["deep"]]},
        "diagram": {"title": "دیاگرام و نمایش بصری", "body": [spec["diagram"]["caption"]], "path": web_path(f"assets/diagrams/{spec['id']}.svg")},
        "realExample": {"title": "مثال واقعی", "body": [spec["example"]]},
        "scenario": {"title": "سناریوی عملی", "body": [spec["scenario"]]},
        "commands": {"title": "دستورات مرتبط Cisco IOS", "body": commands_body, "commands": spec["commands"]},
        "commandWalkthrough": {"title": "توضیح خطبهخط دستورات", "body": ["هر خط دستور و اثر آن بر Data Plane یا Control Plane توضیح داده شده است."], "lines": spec["walkthrough"]},
        "sampleOutput": {"title": "خروجی نمونه", "body": ["خروجی زیر توسط Simulator داخلی FAM Academy تولید شده و صرفاً نمونهای آموزشی با برچسب Sample/Simulated است."], "label": "Sample / Simulated — Internal Simulator", "lines": spec["sample"]},
        "commonMistakes": {"title": "خطاهای رایج", "body": spec["mistakes"]},
        "troubleshooting": {"title": "روش Troubleshooting", "body": spec["troubleshoot"]},
        "keyPoints": {"title": "نکات مهم", "body": spec["key"]},
        "versionNotes": {"title": "استاندارد، نسخه و رفتار Vendor", "body": [spec["version"]]},
        "summary": {"title": "جمع بندی", "body": [spec["summary"]]},
        "references": {"title": "منابع معتبر", "body": ref_titles},
        "quiz": {"title": "آزمون کوتاه", "body": quiz_body},
        "nextSteps": {"title": "گام بعد", "body": next_body},
    }
    quiz = [{"id": q["id"], "prompt": q["prompt"], "options": q["options"], "answerIndex": q["answer"], "explanation": q["explain"], "points": 1} for q in spec["quiz"]]
    return {
        "schemaVersion": "fam-academy-v1", "id": spec["id"], "title": spec["title"], "level": spec["level"],
        "durationMinutes": spec["durationMinutes"], "order": spec["order"], "status": "live",
        "courseId": spec["courseId"], "chapterId": spec["chapterId"], "pathId": spec["pathId"],
        "summary": spec["summary"], "objectives": spec["objectives"], "prerequisites": spec["prerequisites"],
        "sections": sections, "references": refs, "quiz": quiz,
        "diagramPath": web_path(f"assets/diagrams/{spec['id']}.svg"),
        "assetRefs": [web_path(f"assets/diagrams/{spec['id']}.svg")],
        "simulationIds": spec["simulationIds"], "labIds": spec["labIds"], "exerciseId": spec["exerciseId"],
        "nextLessonIds": spec["next"], "contentPath": web_path(f"lessons/{spec['id']}.json"),
        "apiPath": f"/api/academy/v2/lesson/{spec['id']}", "version": "2026.11.24-p0",
    }


def main() -> None:
    V1.mkdir(parents=True, exist_ok=True)
    write_json("references.json", REFERENCES)
    for name, schema in SCHEMA_DEFS.items():
        write_json(f"schemas/{name}", schema)

    # Diagrams
    for spec in LESSON_SPECS:
        d = spec["diagram"]
        write_text(f"assets/diagrams/{spec['id']}.svg", svg_diagram(spec["title"], d["caption"], d["nodes"], d["edges"]))
    for sim in SIMULATIONS:
        d = sim["diagram"]
        write_text(f"assets/diagrams/{sim['id']}.svg", svg_diagram(sim["title"], d["caption"], d["nodes"], d["edges"]))
    for lab in LABS:
        d = lab["diagram"]
        write_text(f"assets/diagrams/{lab['id']}.svg", svg_diagram(lab["title"], d["caption"], d["nodes"], d["edges"]))

    # Lessons, simulations, labs, exercises
    lessons = []
    lesson_summaries = []
    for spec in LESSON_SPECS:
        lesson = build_lesson(spec)
        write_json(f"lessons/{spec['id']}.json", lesson)
        lessons.append(lesson)
        lesson_summaries.append({
            "id": lesson["id"], "title": lesson["title"], "level": lesson["level"], "durationMinutes": lesson["durationMinutes"],
            "order": lesson["order"], "courseId": lesson["courseId"], "chapterId": lesson["chapterId"], "pathId": lesson["pathId"],
            "summary": lesson["summary"], "objectives": lesson["objectives"], "prerequisites": lesson["prerequisites"],
            "status": lesson["status"], "contentPath": lesson["contentPath"], "apiPath": lesson["apiPath"],
            "diagramPath": lesson["diagramPath"], "assetRefs": lesson["assetRefs"], "simulationIds": lesson["simulationIds"],
            "labIds": lesson["labIds"], "exerciseId": lesson["exerciseId"], "nextLessonIds": lesson["nextLessonIds"],
        })
    sim_summaries = []
    for sim in SIMULATIONS:
        data = dict(sim)
        data.update({
            "schemaVersion": "fam-academy-v1", "status": "live",
            "contentPath": web_path(f"simulations/{sim['id']}.json"),
            "apiPath": f"/api/academy/v2/simulation/{sim['id']}",
            "diagramPath": web_path(f"assets/diagrams/{sim['id']}.svg"),
            "assetRefs": [web_path(f"assets/diagrams/{sim['id']}.svg")],
            "version": "2026.11.24-p0",
        })
        data.pop("diagram", None)
        write_json(f"simulations/{sim['id']}.json", data)
        sim_summaries.append({k: data[k] for k in ["id", "title", "logic", "objective", "status", "apiPath", "contentPath", "diagramPath", "lessonIds", "limitations"]})
    lab_summaries = []
    for lab in LABS:
        data = dict(lab)
        data.update({
            "schemaVersion": "fam-academy-v1", "status": "live",
            "contentPath": web_path(f"labs/{lab['id']}.json"),
            "apiPath": f"/api/academy/v2/lab/{lab['id']}",
            "assetRefs": [lab["topology"]["diagramPath"]],
            "version": "2026.11.24-p0",
        })
        data.pop("diagram", None)
        write_json(f"labs/{lab['id']}.json", data)
        lab_summaries.append({k: data[k] for k in ["id", "title", "scenario", "status", "apiPath", "contentPath", "lessonIds", "executionMode"]})
    write_json("exercises.json", {"schemaVersion": "fam-academy-v1", "version": "2026.11.24-p0", "status": "live", "exercises": EXERCISES})

    # Paths and courses
    paths = []
    courses = []
    for order, (pid, title, level, prereqs, next_paths) in enumerate(PATHS, 1):
        paths.append({"id": pid, "title": title, "level": level, "order": order, "prerequisites": prereqs, "objectives": OBJECTIVES[pid], "nextPaths": next_paths})
        course = planned_course(pid, title, level, prereqs, order, next_paths)
        if pid in LIVE_COURSES_BY_PATH:
            course = dict(LIVE_COURSES_BY_PATH[pid])
        courses.append(course)

    catalog = {
        "schemaVersion": "fam-academy-v1", "contentVersion": "2026.11.24-p0", "title": "FAM Academy — بازسازی از صفر",
        "language": "fa", "direction": "rtl", "status": "vertical-slice",
        "release": {"target": "presentation-ready P0", "livePaths": 23, "liveCourses": 5, "plannedCourses": 18, "liveLessons": 10, "liveSimulations": 3, "liveLabs": 2, "liveExercises": 10},
        "api": {
            "catalog": "/api/academy/v2/catalog", "lesson": "/api/academy/v2/lesson/{id}",
            "simulation": "/api/academy/v2/simulation/{id}", "lab": "/api/academy/v2/lab/{id}",
            "exercises": "/api/academy/v2/exercises", "quiz": "/api/academy/v2/quiz/{lessonId}",
            "progress": "/api/academy/progress", "health": "/api/academy/v2/health",
        },
        "storageKey": "famAcademyV2.progress.v1", "legacyStorageKeysPreserved": ["fam4.learn.v1", "fam3.progress.v1", "fam3.lab.v1", "fam3.profile.v1"],
        "paths": paths, "courses": courses, "lessons": lesson_summaries, "simulations": sim_summaries, "labs": lab_summaries,
        "exercises": web_path("exercises.json"), "references": web_path("references.json"),
        "schemas": {name: web_path(f"schemas/{name}") for name in SCHEMA_DEFS},
        "manifest": web_path("manifest.json"),
        "designPrinciples": [
            "محتوای آموزشی، کاتالوگ، موتور نمایش، موتور شبیهسازی، موتور Lab، ارزیابی، پیشرفت و UI از هم جدا هستند.",
            "درسهای P0 کامل و عمیق نوشته شدهاند؛ مسیرهای P1 فقط نقشه راه هستند و محتوای ضعیف تولید نشده است.",
            "خروجیها و دستورات در Simulator داخلی اجرا یا تولید میشوند و هرگز بهعنوان خروجی تجهیز واقعی معرفی نمیشوند.",
        ],
        "limitations": [
            "۱۸ مسیر یادگیری P1 فقط ساختار و نقشه راه دارند؛ درس/شبیهساز/لاب کامل برای آنها تولید نشده است.",
            "شبیهسازها آموزشی و محدودند؛ برای مثال OSPF LSA flooding کامل و VLAN STP مدل نشدهاند.",
            "اتصال به PNETLab/EVE-NG یا تجهیزات واقعی غیرفعال است و فقط معماری آینده مستند شده است.",
            "Flask در محیط تست محلی نصب نیست؛ نسخه پیشنمایش با سرور استاندارد Python اجرا و تست میشود.",
        ],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    write_json("catalog.json", catalog)

    # Independent manifest for new v1 content only
    files = []
    for p in sorted(V1.rglob("*")):
        if not p.is_file() or p.name == "manifest.json":
            continue
        rel = p.relative_to(V1).as_posix()
        b = p.read_bytes()
        files.append({"path": rel, "size": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    aggregate = hashlib.sha256(("\n".join(f"{f['size']}|{f['sha256']}|{f['path']}" for f in files)).encode()).hexdigest()
    write_json("manifest.json", {
        "schemaVersion": "fam-academy-manifest-v1", "contentVersion": catalog["contentVersion"],
        "generatedAt": datetime.now(timezone.utc).isoformat(), "fileCount": len(files),
        "aggregateSha256": aggregate, "files": files,
        "note": "Independent manifest for academy-content/v1 only. Root MANIFEST.sha256 is intentionally unchanged and still carries the 143 prior deletions.",
    })
    print(f"generated {len(files)} v1 files; {len(LESSON_SPECS)} lessons; {len(SIMULATIONS)} simulations; {len(LABS)} labs; {len(courses)} courses; {len(paths)} paths")
    print(f"aggregateSha256={aggregate}")


if __name__ == "__main__":
    main()
