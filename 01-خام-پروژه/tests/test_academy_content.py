"""Integrity tests for the FAM Cisco Academy comprehensive curriculum."""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = PACKAGE_ROOT / "server"
WEB_ROOT = SERVER_ROOT / "www"
ASSET_ROOT = WEB_ROOT / "academy-assets"
PRIVATE_UI = SERVER_ROOT / "private_ui"


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.assets: list[str] = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href"} and value and value.startswith("/academy-assets/"):
                self.assets.append(value.split("?", 1)[0].split("#", 1)[0])


class AcademyRedesignTests(unittest.TestCase):
    def test_academy_pages_reference_existing_local_assets_only(self):
        for page_name in ("academy.html", "academy_dashboard.html"):
            page_path = PRIVATE_UI / page_name
            self.assertTrue(page_path.is_file(), page_name)
            html = page_path.read_text(encoding="utf-8")
            parser = AssetParser()
            parser.feed(html)
            self.assertEqual(
                sorted(set(parser.assets)),
                ["/academy-assets/app.js", "/academy-assets/styles.css"],
                page_name,
            )
            for ref in parser.assets:
                local_path = (WEB_ROOT / ref.lstrip("/")).resolve()
                self.assertIn(WEB_ROOT.resolve(), local_path.parents)
                self.assertTrue(local_path.is_file(), ref)

    def test_csp_compliance_rtl_and_bootstrap_markers(self):
        for page_name in ("academy.html", "academy_dashboard.html"):
            html = (PRIVATE_UI / page_name).read_text(encoding="utf-8")
            with self.subTest(page=page_name):
                self.assertIn('lang="fa" dir="rtl"', html)
                self.assertIn("__FAM_CSP_NONCE__", html)
                self.assertIn("__FAM_ACADEMY_BOOTSTRAP__", html)
                self.assertNotRegex(html, r"\bon(?:click|change|submit|load)\s*=")
                self.assertNotIn("fonts.googleapis.com", html)

    def test_live_topology_and_dashboard_panels_exist(self):
        landing = (PRIVATE_UI / "academy.html").read_text(encoding="utf-8")
        dash = (PRIVATE_UI / "academy_dashboard.html").read_text(encoding="utf-8")
        self.assertIn('class="topo"', landing)
        self.assertIn('id="typeTarget"', landing)
        self.assertIn('href="/academy/dashboard', landing)
        for panel in ("home", "lesson", "courses", "lab", "exam", "progress", "glossary"):
            self.assertIn(f'data-panel="{panel}"', dash)
        self.assertIn('href="/academy"', dash)

    def test_comprehensive_cisco_curriculum_data_integrity(self):
        self.assertEqual(
            sorted(p.name for p in ASSET_ROOT.iterdir()),
            ["academy-data.json", "app.js", "styles.css"],
        )
        data = json.loads((ASSET_ROOT / "academy-data.json").read_text(encoding="utf-8"))
        self.assertEqual([f["id"] for f in data["faculties"]], ["f0", "f1", "f2", "f3", "f4", "f5", "f6"])
        self.assertEqual(len(data["faculties"][1]["labs"]), 25)
        self.assertEqual(len(data["faculties"][2]["labs"]), 12)
        self.assertEqual(len(data["meta"]["labTools"]), 11)
        self.assertEqual(data["meta"]["passingScore"], 85)
        self.assertEqual(data["meta"]["dailyMinutes"], 120)
        self.assertEqual([g["facultyId"] for g in data["curriculumGroups"]], ["f0", "f1", "f2", "f3", "f4", "f5", "f6"])
        counts = {g["facultyId"]: len(g["lessons"]) for g in data["curriculumGroups"]}
        self.assertEqual(counts["f5"], 7)
        self.assertEqual(counts["f6"], 20)
        all_grouped = [lid for g in data["curriculumGroups"] for lid in g["lessons"]]
        self.assertGreaterEqual(len(all_grouped), 110)
        for sid in all_grouped:
            self.assertIn(sid, data["lessons"])
            lesson = data["lessons"][sid]
            for key in ("goal", "prereq", "analogy", "summary", "ciscoRef", "sections", "table", "faq", "protocolAnalysis", "iosCommands", "lab", "troubleshooting", "exercise", "quiz"):
                self.assertIn(key, lesson, f"{sid}.{key}")
        self.assertGreaterEqual(len(data["glossary"]), 100)
        for item in data["glossary"]:
            self.assertIn(item["ref"], data["lessons"], item["term"])

    def test_f3_technical_accuracy_and_simulator_persistence(self):
        data = json.loads((ASSET_ROOT / "academy-data.json").read_text(encoding="utf-8"))
        app_js = (ASSET_ROOT / "app.js").read_text(encoding="utf-8")

        # 1. HTTP Waterfall arithmetic consistency in ccnp_enna
        enna_http = data["lessons"]["ccnp_enna"]["iosCommands"][1]["out"]
        m = re.search(r"DNS=(\d+)ms\s*\|\s*Connect=(\d+)ms\s*\|\s*SSL=(\d+)ms\s*\|\s*Wait=(\d+)ms\s*\|\s*Response=(\d+)ms", enna_http)
        self.assertIsNotNone(m, "ccnp_enna reference HTTP metrics missing")
        dns, conn, ssl, wait, resp = map(int, m.groups())
        self.assertEqual(dns + conn + ssl + wait, resp)

        # 2. Regression checks for f3 review fixes
        ex2_s = json.dumps(data["lessons"]["ccnp_enna"]["exercises"][2], ensure_ascii=False)
        self.assertNotIn("سالم بوده و فقط", ex2_s)
        self.assertIn("ECMP", ex2_s)

        arch_s5 = data["lessons"]["ccnp_enc_arch"]["lab"]["steps"][4]
        self.assertNotIn("Punt = 0", arch_s5)
        self.assertIn("fwd-asic resource tcam utilization", arch_s5)
        self.assertIn("Catalyst 9300", arch_s5)
        self.assertIn("Catalyst 9500 Standalone", arch_s5)
        self.assertIn("فرضی", arch_s5)

        sec_s5 = data["lessons"]["ccnp_enc_sec"]["lab"]["steps"][4]
        self.assertIn("eq bgp any", sec_s5)
        self.assertIn("any eq bgp", sec_s5)
        self.assertIn("class class-default", sec_s5)

        for req_id in ("ccnp_enc_inf", "ccnp_encc", "ccnp_ensld"):
            self.assertIn("پیش‌نیاز", data["lessons"][req_id]["lab"]["steps"][4], req_id)

        auto_s = json.dumps(data["lessons"]["ccnp_enc_auto"], ensure_ascii=False)
        self.assertNotIn("فراموش کرده فرمت درخواستی را با **`Accept", auto_s)
        self.assertIn("RFC 8040", auto_s)

        inf_s5 = data["lessons"]["ccnp_enc_inf"]["lab"]["steps"][4]
        self.assertIn("State/PfxRcd", inf_s5)
        self.assertIn("0", inf_s5)

        f3_ids = data["curriculumGroups"][3]["lessons"]
        self.assertEqual(len(f3_ids), 11)
        ans_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f3_ids:
            self.assertEqual(len(data["lessons"][lid]["lab"]["steps"]), 5, lid)
            for q in data["lessons"][lid]["quiz"]:
                ans_dist[q["ans"]] += 1
        self.assertTrue(all(6 <= v <= 10 for v in ans_dist.values()), ans_dist)

        # 2b. Checks for f4 Batch 1..6 (first 30 lessons in f4) + Round-6..17 regressions
        f4_b1_to_b6 = data["curriculumGroups"][4]["lessons"][:30]
        self.assertEqual(
            f4_b1_to_b6,
            [
                "spec_ent", "spec_ent_campus", "spec_ent_sd", "spec_sec", "spec_sec_vpn",
                "spec_sec_ise", "spec_dc_nx", "s11", "spec_dc_aci", "spec_dc_stor",
                "spec_sp", "spec_sp_xr", "spec_sp_sr", "spec_wl", "spec_wl_survey",
                "spec_collab", "spec_collab_gw", "auto_01", "auto_02", "auto_03",
                "auto_04", "auto_05", "auto_06", "auto_07", "auto_08",
                "auto_09", "auto_10", "auto_11", "auto_12", "auto_13",
            ],
        )
        for lid in f4_b1_to_b6:
            lesson = data["lessons"][lid]
            self.assertEqual(len(lesson.get("exercises", [])), 3, lid)
            self.assertEqual(len(lesson.get("quiz", [])), 3, lid)
            self.assertEqual(len(lesson["lab"]["steps"]), 5, lid)
            s = json.dumps(lesson, ensure_ascii=False)
            for bad in ("192.168", "1921.6800", "فوق‌العاده", "بی‌نظیر", "قانون طلایی", "طلایی", "۹۰٪", "۹۹٪", "۱۰۰٪", "۸۰٪", "جادویی"):
                self.assertNotIn(bad, s, f"{lid} contains {bad}")
        b3_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f4_b1_to_b6[10:15]:
            for q in data["lessons"][lid]["quiz"]:
                b3_dist[q["ans"]] += 1
        self.assertEqual(b3_dist, {0: 4, 1: 4, 2: 4, 3: 3})
        b4_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f4_b1_to_b6[15:20]:
            for q in data["lessons"][lid]["quiz"]:
                b4_dist[q["ans"]] += 1
        self.assertEqual(b4_dist, {0: 4, 1: 4, 2: 4, 3: 3})
        b5_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f4_b1_to_b6[20:25]:
            for q in data["lessons"][lid]["quiz"]:
                b5_dist[q["ans"]] += 1
        self.assertEqual(b5_dist, {0: 4, 1: 4, 2: 4, 3: 3})
        b6_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f4_b1_to_b6[25:30]:
            for q in data["lessons"][lid]["quiz"]:
                b6_dist[q["ans"]] += 1
        self.assertEqual(b6_dist, {0: 4, 1: 4, 2: 4, 3: 3})

        # Round-6 & Round-7 regression assertions
        ent_step = data["lessons"]["spec_ent"]["sections"][1]["steps"][0]
        self.assertIn("49.0001.0102.5500.0001.00", ent_step)
        self.assertIn("49.0001.0102.5500.0002.00", ent_step)

        sd_ctrl = data["lessons"]["spec_ent_sd"]["iosCommands"][1]
        self.assertNotIn("vbond", sd_ctrl["out"])
        self.assertIn("vBond", sd_ctrl["note"])
        self.assertNotIn("سوختن یکی از روترها، مدار متصل به آن همچنان", data["lessons"]["spec_ent_sd"]["exercise"])

        ensdwi_cmds = {c["cmd"]: c for c in data["lessons"]["ccnp_ensdwi"]["iosCommands"]}
        self.assertIn("show sdwan app-route stats", ensdwi_cmds)
        self.assertIn("نه خروجی عین CLI", ensdwi_cmds["show sdwan app-route stats"]["note"])
        self.assertIn("show sdwan app-route stats", data["lessons"]["ccnp_ensdwi"]["lab"]["steps"][4])

        sec_lesson = data["lessons"]["spec_sec"]
        self.assertIn("`mab`", sec_lesson["lab"]["steps"][4])
        self.assertIn("Low-Impact", sec_lesson["protocolAnalysis"][0])
        self.assertIn("Spoofing", sec_lesson["sections"][2]["steps"][0])

        vpn_lesson = data["lessons"]["spec_sec_vpn"]
        self.assertEqual(vpn_lesson["bridge"]["nextId"], "spec_sec_ise")
        self.assertIn("IP Multicast", vpn_lesson["protocolAnalysis"][1])
        self.assertIn("پیش از محاسبهٔ Padding", vpn_lesson["exercises"][2]["solution"])
        self.assertIn("1400", vpn_lesson["exercises"][2]["solution"])

        camp_lesson = data["lessons"]["spec_ent_campus"]
        self.assertNotIn("همیشه باید حداقل دو لینک", camp_lesson["sections"][1]["think"]["a"])
        self.assertNotIn("BFD", camp_lesson["sections"][1]["steps"][1])

        # Round-8 regression assertions (f4 Batch 2 review fixes)
        ise_lesson = data["lessons"]["spec_sec_ise"]
        self.assertIn("authorization commands 15 VTY_CMD", ise_lesson["lab"]["steps"][4])
        self.assertIn("DEAD/ERROR", ise_lesson["lab"]["steps"][4])
        self.assertIn("FAIL", ise_lesson["troubleshooting"]["analysis"])
        self.assertIn("ERROR / DEAD", ise_lesson["troubleshooting"]["analysis"])

        nx_lesson = data["lessons"]["spec_dc_nx"]
        self.assertIn("استثنای حیاتی مسیر پشتیبان", nx_lesson["sections"][1]["steps"][2])
        self.assertIn("vpc orphan-port suspend", nx_lesson["sections"][2]["p"][0])
        self.assertIn("وابسته به مسیر و تنظیمات", nx_lesson["misconceptions"][1]["reality"])

        s11_lesson = data["lessons"]["s11"]
        self.assertIn("MTU لایه ۳", s11_lesson["sections"][1]["steps"][0])
        self.assertIn("Ethernet داخلی", s11_lesson["protocolAnalysis"][1])
        self.assertIn("Ethernet داخلی", s11_lesson["exercises"][2]["solution"])

        aci_lesson = data["lessons"]["spec_dc_aci"]
        self.assertIn("فاقد Data Plane واقعی", aci_lesson["lab"]["steps"][0])
        self.assertIn("Data Plane واقعی", aci_lesson["iosCommands"][0]["note"])
        self.assertIn("خروجی نمونهٔ ثابت آموزشی برمی‌گرداند", aci_lesson["iosCommands"][2]["note"])
        self.assertNotIn("جداسازی کامل Failure Domain سیاستی", aci_lesson["quiz"][2]["opts"][3])
        self.assertIn("NDO", aci_lesson["sections"][2]["p"][0])

        stor_lesson = data["lessons"]["spec_dc_stor"]
        self.assertIn("LUN Mapping / LUN Masking", stor_lesson["lab"]["steps"][4])
        self.assertIn("HBA / Storage Rescan", stor_lesson["lab"]["steps"][4])
        self.assertIn("LUN Mapping / LUN Masking", stor_lesson["troubleshooting"]["analysis"])
        self.assertIn("Rescan", stor_lesson["troubleshooting"]["fix"])

        # Round-9 regression assertions (3 remaining Batch 2 fixes + Batch 3 semantic checks)
        self.assertIn("سوئیچِ مبدأ که فریم را از روی `Peer-Link` می‌فرستد", nx_lesson["sections"][1]["steps"][2])
        self.assertNotIn("روی سوئیچ دریافت‌کننده قطع شده باشد", nx_lesson["sections"][1]["steps"][2])
        self.assertIn("مبدأ عبور از Peer-Link", nx_lesson["exercises"][1]["solution"])

        self.assertIn("Global Configuration", ise_lesson["troubleshooting"]["fix"])
        self.assertIn("اعمال همین لیست‌های نام‌دار زیر `line vty 0 4`", ise_lesson["troubleshooting"]["fix"])

        stor_s = json.dumps(stor_lesson, ensure_ascii=False)
        self.assertNotIn("فریم کامل `2112B` FC", stor_s)
        self.assertNotIn("فریم ۲۱۱2 بایتی FC", stor_s)
        self.assertNotIn("فریم‌های `2112` بایتی FC", stor_s)
        self.assertIn("2148", stor_lesson["sections"][2]["p"][0])
        self.assertIn("Payload", stor_lesson["sections"][2]["p"][0])
        self.assertIn("Nexus 5000", stor_lesson["sections"][2]["p"][0])

        sp_lesson = data["lessons"]["spec_sp"]
        self.assertIn("Implicit Null", sp_lesson["sections"][1]["steps"][1])
        self.assertIn("LDP-IGP", sp_lesson["sections"][1]["think"]["a"])
        self.assertEqual(sp_lesson["bridge"]["nextId"], "spec_sp_xr")

        xr_lesson = data["lessons"]["spec_sp_xr"]
        self.assertIn("RFC 8212", xr_lesson["sections"][1]["steps"][1])
        self.assertIn("commit confirmed", xr_lesson["sections"][0]["bullets"][1])
        self.assertNotIn("commit confirm ", json.dumps(xr_lesson, ensure_ascii=False))
        self.assertEqual(xr_lesson["bridge"]["nextId"], "spec_sp_sr")

        sr_lesson = data["lessons"]["spec_sp_sr"]
        self.assertIn("SRGB", sr_lesson["sections"][0]["bullets"][0])
        self.assertIn("SRH", sr_lesson["sections"][1]["steps"][1])
        self.assertIn("Post-Convergence", sr_lesson["sections"][1]["steps"][2])
        self.assertEqual(sr_lesson["bridge"]["nextId"], "spec_wl")

        wl_lesson = data["lessons"]["spec_wl"]
        self.assertIn("SNR", wl_lesson["sections"][0]["bullets"][1])
        self.assertIn("OFDMA", wl_lesson["sections"][1]["steps"][0])
        self.assertIn("FlexConnect", wl_lesson["sections"][2]["p"][0])
        self.assertEqual(wl_lesson["bridge"]["nextId"], "spec_wl_survey")

        survey_lesson = data["lessons"]["spec_wl_survey"]
        self.assertIn("AP-on-a-Stick", survey_lesson["sections"][0]["bullets"][1])
        self.assertIn("3D Channel Planning", survey_lesson["sections"][1]["steps"][1])
        self.assertIn("Asymmetric Link", survey_lesson["sections"][2]["p"][0])
        self.assertEqual(survey_lesson["bridge"]["nextId"], "spec_collab")

        # Round-10 regression assertions (Batch 2 AAA/FCoE clarifications & Batch 3 review fixes)
        self.assertIn("به پلتفرم و نسخهٔ IOS/IOS-XE وابسته است", ise_lesson["lab"]["steps"][4])
        self.assertIn("هر کاربرِ از قبل احراز هویت‌شده", ise_lesson["troubleshooting"]["analysis"])

        self.assertNotIn("FCoE", stor_lesson["table"]["rows"][2][2])
        self.assertIn("class-fcoe", stor_lesson["sections"][2]["p"][0])
        self.assertIn("class-default", stor_lesson["sections"][2]["p"][0])
        self.assertIn("mtu 2158", stor_lesson["table"]["rows"][3][2])
        self.assertIn("mtu 9216", stor_lesson["table"]["rows"][3][2])

        self.assertIn("no central switching", wl_lesson["sections"][2]["p"][0])
        self.assertIn("no central switching", wl_lesson["lab"]["steps"][4])
        self.assertIn("wireless profile flex BRANCH_FLEX_PROF", wl_lesson["lab"]["steps"][4])
        self.assertIn("no central switching", wl_lesson["quiz"][2]["opts"][0])
        self.assertIn("Enhanced Open (OWE", wl_lesson["sections"][1]["steps"][1])
        self.assertIn("PMF", wl_lesson["sections"][1]["steps"][1])
        self.assertIn("Enhanced Open (OWE)", wl_lesson["quiz"][1]["opts"][3])

        survey_s = json.dumps(survey_lesson, ensure_ascii=False)
        self.assertNotIn("channel dca width", survey_s)
        self.assertNotIn("rssi-threshold", survey_s)
        self.assertIn("channel chan-width 40", survey_lesson["lab"]["steps"][4])
        self.assertIn("coverage data rssi threshold -75", survey_lesson["lab"]["steps"][4])
        self.assertIn("شماتیک/خلاصه‌شدهٔ مرجع آموزشی", survey_lesson["iosCommands"][0]["note"])
        self.assertIn("شماتیک/خلاصه‌شدهٔ مرجع آموزشی", survey_lesson["iosCommands"][1]["note"])
        self.assertNotIn("دچار اشباع `Airtime` نمی‌شود", survey_s)
        self.assertIn("برآورد اولیه", survey_lesson["exercises"][1]["solution"])
        self.assertIn("تصمیم نهایی Roaming با الگوریتم و درایور خودِ **کلاینت** است", survey_lesson["protocolAnalysis"][1])

        sr_s = json.dumps(sr_lesson, ensure_ascii=False)
        self.assertIn("RFC 9855", sr_s)
        self.assertNotIn("تغییر مسیر دوم یا افتی رخ ندهد", sr_s)
        self.assertNotIn("حداکثر `1` یا `2` برچسب", sr_s)
        self.assertIn("MSD", sr_lesson["sections"][1]["steps"][2])
        self.assertIn("Micro-loop", sr_lesson["misconceptions"][1]["reality"])

        xr_s5 = xr_lesson["lab"]["steps"][4]
        self.assertIn("network 10.255.0.1/32", xr_s5)
        self.assertIn("advertised-routes", xr_s5)
        self.assertIn("received-routes", xr_s5)
        self.assertIn("10.10.0.1 255.255.255.252", xr_s5)
        self.assertNotIn("در کسری از ثانیه ریستارت می‌گردد بدون اینکه", xr_lesson["sections"][0]["bullets"][0])
        self.assertIn("NSF / Graceful Restart", xr_lesson["sections"][0]["bullets"][0])

        # Round-11 regressions: Round-10 follow-ups (spec_wl_survey rate disable / numeric hedging, spec_wl FlexConnect wording) + Batch 4 semantic checks
        self.assertNotIn("rate RATE_6M unsupported", survey_s)
        self.assertNotIn("rate RATE_9M unsupported", survey_s)
        self.assertIn("rate RATE_6M disable", survey_lesson["lab"]["steps"][4])
        self.assertIn("rate RATE_9M disable", survey_lesson["lab"]["steps"][4])
        self.assertNotIn("نصف می‌گردد", survey_s)
        self.assertNotIn("نصف می‌شود", survey_s)

        self.assertNotIn("مد سویچینگ (`Site Tag`)", wl_lesson["iosCommands"][1]["why"])
        self.assertIn("در سناریوی چند-VLAN", wl_lesson["sections"][2]["p"][0])
        self.assertIn("Access", wl_lesson["sections"][2]["p"][0])

        collab_lesson = data["lessons"]["spec_collab"]
        self.assertIn("87.2 kbps", collab_lesson["sections"][1]["bullets"][0])
        self.assertIn("31.2 kbps", collab_lesson["sections"][1]["bullets"][1])
        self.assertIn("Line CSS", collab_lesson["sections"][2]["think"]["a"])
        self.assertEqual(collab_lesson["bridge"]["nextId"], "spec_collab_gw")

        gw_lesson = data["lessons"]["spec_collab_gw"]
        self.assertIn("ip address trusted list", gw_lesson["sections"][0]["bullets"][0])
        self.assertIn("Dial-Peer 0", gw_lesson["sections"][1]["p"][0])
        self.assertIn("Split-Horizon DNS", gw_lesson["sections"][2]["p"][1])
        self.assertEqual(gw_lesson["bridge"]["nextId"], "auto_01")

        a1_lesson = data["lessons"]["auto_01"]
        self.assertIn("chmod 600", a1_lesson["sections"][0]["bullets"][0])
        self.assertIn("iproute2", a1_lesson["sections"][1]["p"][1])
        self.assertIn("-nn", a1_lesson["sections"][1]["p"][1])
        self.assertEqual(a1_lesson["bridge"]["nextId"], "auto_02")

        a2_lesson = data["lessons"]["auto_02"]
        self.assertIn("PEP 668", a2_lesson["sections"][1]["bullets"][0])
        self.assertIn("os.environ.get", a2_lesson["sections"][1]["bullets"][1])
        self.assertEqual(a2_lesson["bridge"]["nextId"], "auto_03")

        a3_lesson = data["lessons"]["auto_03"]
        self.assertIn("isinstance(parsed, list)", a3_lesson["sections"][1]["bullets"][0])
        self.assertIn("Blast Radius", a3_lesson["sections"][2]["think"]["a"])
        self.assertEqual(a3_lesson["bridge"]["nextId"], "auto_04")

        # Round-12 regressions (Batch 4 review fixes: awk quoting, IndexError/vlan_audit.py, ssh_strict/post-check, CUBE URI/failover, MRA X12.5+, VoIP stream direction bounds)
        a1_s = json.dumps(a1_lesson, ensure_ascii=False)
        self.assertNotIn('awk "', a1_s)
        self.assertIn("awk '{print $1, $2, $NF}'", a1_lesson["sections"][0]["bullets"][1])
        self.assertIn("awk '{print $1, $2, $3, $NF}'", a1_lesson["lab"]["steps"][4])
        m_pipe = re.search(r"`(grep -E \"BGP\|SSH\|TIMEOUT\" /var/log/syslog \| awk '[^']+' \| sort \| uniq -c)`", a1_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_pipe, "auto_01 awk pipeline missing")
        if shutil.which("bash") and shutil.which("awk"):
            with tempfile.TemporaryDirectory() as tmpd:
                log_file = Path(tmpd) / "syslog"
                log_file.write_text(
                    "Nov 23 10:01:02 R1 BGP: peer 10.255.0.2 Down\n"
                    "Nov 23 10:01:02 R1 SSH: timeout 10.255.0.2\n"
                    "Nov 23 10:02:00 R1 LINK: up\n"
                    "Nov 23 10:01:02 R1 BGP: peer 10.255.0.2 Down\n",
                    encoding="utf-8",
                )
                pipeline_cmd = m_pipe.group(1).replace("/var/log/syslog", str(log_file))
                pipe_res = subprocess.run(["bash", "-lc", pipeline_cmd], capture_output=True, text=True, check=False)
                self.assertEqual(pipe_res.returncode, 0, pipe_res.stderr)
                self.assertIn("2 Nov 23 10:01:02 Down", pipe_res.stdout)
                self.assertIn("1 Nov 23 10:01:02 10.255.0.2", pipe_res.stdout)

        a2_s = json.dumps(a2_lesson, ensure_ascii=False)
        self.assertIn("IndexError", a2_lesson["sections"][1]["p"][1])
        self.assertIn("len(cols) < 6", a2_lesson["sections"][1]["think"]["a"])
        m_py = re.search(r"```python\n([\s\S]+?)\n```", a2_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_py, "auto_02 runnable vlan_audit.py block missing")
        with tempfile.TemporaryDirectory() as tmpd:
            script_path = Path(tmpd) / "vlan_audit.py"
            script_path.write_text(m_py.group(1), encoding="utf-8")
            env = dict(os.environ, NETOPS_TOKEN="demo")
            py_res = subprocess.run([sys.executable, str(script_path)], cwd=tmpd, env=env, capture_output=True, text=True, check=False)
            self.assertEqual(py_res.returncode, 0, py_res.stderr + py_res.stdout)
            self.assertIn("UP: ['GigabitEthernet0/0', 'GigabitEthernet0/1']", py_res.stdout)
            self.assertIn("SKIPPED: ['BAD_TRUNCATED_LINE     unassigned']", py_res.stdout)
            self.assertIn("MISSING: [99]", py_res.stdout)
            self.assertIn("BAD_VLAN: ['bad_id']", py_res.stdout)
            plan_txt = (Path(tmpd) / "config_plan.txt").read_text(encoding="utf-8")
            self.assertIn("vlan 99", plan_txt)
            self.assertIn("name NETOPS_99", plan_txt)

        a3_s = json.dumps(a3_lesson, ensure_ascii=False)
        self.assertIn("ssh_strict=True", a3_s)
        self.assertIn("known_hosts", a3_s)
        self.assertIn("system_host_keys", a3_s)
        self.assertIn("فیلتر محافظه‌کارانه", a3_lesson["sections"][1]["bullets"][1])
        self.assertIn("Post-Check", a3_lesson["sections"][1]["bullets"][1])
        m_a3_py = re.search(r"```python\n([\s\S]+?)\n```", a3_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a3_py, "auto_03 runnable safe_apply.py block missing")
        ns_a3: dict = {}
        exec(compile(m_a3_py.group(1), "safe_apply.py", "exec"), ns_a3)
        apply_ntp_safely = ns_a3["apply_ntp_safely"]

        class MockConn:
            def __init__(self, cfg_out: str, post_out: str, save_out: str = "Building configuration...\n[OK]", save_exc: Exception | None = None) -> None:
                self.cfg_out = cfg_out
                self.post_out = post_out
                self.save_out = save_out
                self.save_exc = save_exc
                self.saved = 0
                self.enabled = False
                self.post_checked = 0

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def enable(self):
                self.enabled = True

            def send_config_set(self, cmds):
                return self.cfg_out

            def send_command(self, cmd):
                self.post_checked += 1
                return self.post_out

            def save_config(self):
                self.saved += 1
                if self.save_exc is not None:
                    raise self.save_exc
                return self.save_out

        seen_kwargs = []

        def make_factory(conn_obj):
            def factory(**kwargs):
                seen_kwargs.append(kwargs)
                return conn_obj
            return factory

        c_cli_err = MockConn("% Invalid input detected at '^' marker.", "ntp server 10.255.0.100")
        self.assertEqual(apply_ntp_safely(make_factory(c_cli_err), {"host": "10.255.0.1"}, "10.255.0.100"), "cli_error")
        self.assertEqual(c_cli_err.saved, 0)
        self.assertEqual(c_cli_err.post_checked, 0)

        c_post_fail = MockConn("R1(config)#ntp server 10.255.0.100\nR1(config)#end", "")
        self.assertEqual(apply_ntp_safely(make_factory(c_post_fail), {"host": "10.255.0.1"}, "10.255.0.100"), "postcheck_failed")
        self.assertEqual(c_post_fail.saved, 0)
        self.assertEqual(c_post_fail.post_checked, 1)

        # Boundary test: 10.255.0.1 MUST NOT match "ntp server 10.255.0.10"
        c_prefix_trap = MockConn("R1(config)#ntp server 10.255.0.1\nR1(config)#end", "ntp server 10.255.0.10")
        self.assertEqual(apply_ntp_safely(make_factory(c_prefix_trap), {"host": "10.255.0.1"}, "10.255.0.1"), "postcheck_failed")
        self.assertEqual(c_prefix_trap.saved, 0)
        self.assertEqual(c_prefix_trap.post_checked, 1)

        # Save error output & exception MUST NOT report "saved"
        c_save_err = MockConn("R1(config)#ntp server 10.255.0.1\nR1(config)#end", "ntp server 10.255.0.1", save_out="% Error copying configuration (Timed out)")
        self.assertEqual(apply_ntp_safely(make_factory(c_save_err), {"host": "10.255.0.1"}, "10.255.0.1"), "save_failed")
        self.assertEqual(c_save_err.saved, 1)

        c_save_exc = MockConn("R1(config)#ntp server 10.255.0.1\nR1(config)#end", "ntp server 10.255.0.1", save_exc=OSError("NVRAM read-only"))
        self.assertEqual(apply_ntp_safely(make_factory(c_save_exc), {"host": "10.255.0.1"}, "10.255.0.1"), "save_failed")
        self.assertEqual(c_save_exc.saved, 1)

        # Empty / whitespace save_config() output MUST return "save_failed"
        for empty_save in ("", "   \n\t "):
            c_save_empty = MockConn("R1(config)#ntp server 10.255.0.1\nR1(config)#end", "ntp server 10.255.0.1", save_out=empty_save)
            self.assertEqual(apply_ntp_safely(make_factory(c_save_empty), {"host": "10.255.0.1"}, "10.255.0.1"), "save_failed")
            self.assertEqual(c_save_empty.saved, 1)

        # Invalid IP rejected before connection factory is called
        c_unused = MockConn("", "")
        before_calls = len(seen_kwargs)
        with self.assertRaises(ValueError):
            apply_ntp_safely(make_factory(c_unused), {"host": "10.255.0.1"}, "10.255.0.1\nno ip routing")
        self.assertEqual(len(seen_kwargs), before_calls)

        c_ok = MockConn("R1(config)#ntp server 10.255.0.100\nR1(config)#end", "ntp server 10.255.0.100 prefer")
        self.assertEqual(apply_ntp_safely(make_factory(c_ok), {"host": "10.255.0.1"}, "10.255.0.100"), "save_no_error_seen")
        self.assertEqual(c_ok.saved, 1)
        self.assertEqual(c_ok.post_checked, 1)
        self.assertTrue(all(kw.get("ssh_strict") is True and kw.get("system_host_keys") is True for kw in seen_kwargs))
        self.assertIn("Rollback", a3_s)
        self.assertIn("تغییرات ذخیره‌نشدهٔ", a3_s)
        self.assertIn("اثبات همگام‌شدن عملیاتی NTP نیست", a3_s)
        self.assertIn("save_no_error_seen", a3_s)
        self.assertEqual(a3_lesson["bridge"]["nextTitle"], data["lessons"]["auto_04"]["title"])

        # Round-14/15 Batch-5 checks (auto_04 .. auto_08 technical content & runnable bash/Python code + security/error-path tests)
        a4_lesson = data["lessons"]["auto_04"]
        a4_s = json.dumps(a4_lesson, ensure_ascii=False)
        self.assertIn("git switch -c", a4_s)
        self.assertIn("git add -p", a4_s)
        self.assertIn("git revert", a4_s)
        self.assertIn(".gitignore", a4_s)
        self.assertIn("git >= 2.28", a4_lesson["lab"]["steps"][4])
        self.assertIn("mktemp -d", a4_lesson["lab"]["steps"][4])
        self.assertEqual(a4_lesson["bridge"]["nextId"], "auto_05")
        m_a4_sh = re.search(r"```bash\n([\s\S]+?)\n```", a4_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a4_sh, "auto_04 runnable bash block missing")
        if shutil.which("bash") and shutil.which("git"):
            with tempfile.TemporaryDirectory() as outer_dir:
                # Verify running the lab script from an existing directory does NOT overwrite existing files
                sentinel = Path(outer_dir) / "inventory.yaml"
                sentinel.write_text("existing-keep\n", encoding="utf-8")
                run_cmd = m_a4_sh.group(1) + '\nprintf "LAB_DIR=%s\\n" "$LAB_DIR"\n'
                git_res = subprocess.run(["bash", "-e", "-c", run_cmd], cwd=outer_dir, capture_output=True, text=True, check=False)
                self.assertEqual(git_res.returncode, 0, git_res.stderr + git_res.stdout)
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "existing-keep\n")
                m_lab = re.search(r"LAB_DIR=(.+)", git_res.stdout)
                self.assertIsNotNone(m_lab)
                lab_path = Path(m_lab.group(1).strip())
                try:
                    ls_res = subprocess.run(["git", "ls-files"], cwd=lab_path, capture_output=True, text=True, check=True)
                    self.assertNotIn(".env", ls_res.stdout.splitlines())
                    self.assertIn(".gitignore", ls_res.stdout.splitlines())
                    self.assertIn("inventory.yaml", ls_res.stdout.splitlines())
                    inv_txt = (lab_path / "inventory.yaml").read_text(encoding="utf-8")
                    self.assertIn("R1", inv_txt)
                    self.assertIn("R2", inv_txt)

                    # Failure mode: conflicting concurrent edits on same line cause real merge conflict
                    subprocess.run(["git", "switch", "-c", "branch-a"], cwd=lab_path, check=True, capture_output=True)
                    (lab_path / "inventory.yaml").write_text("routers:\n  - R1-A\n", encoding="utf-8")
                    subprocess.run(["git", "commit", "-am", "edit A"], cwd=lab_path, check=True, capture_output=True)
                    subprocess.run(["git", "switch", "main"], cwd=lab_path, check=True, capture_output=True)
                    subprocess.run(["git", "switch", "-c", "branch-b"], cwd=lab_path, check=True, capture_output=True)
                    (lab_path / "inventory.yaml").write_text("routers:\n  - R1-B\n", encoding="utf-8")
                    subprocess.run(["git", "commit", "-am", "edit B"], cwd=lab_path, check=True, capture_output=True)
                    conflict = subprocess.run(["git", "merge", "branch-a"], cwd=lab_path, capture_output=True, text=True, check=False)
                    self.assertNotEqual(conflict.returncode, 0)
                    self.assertIn("CONFLICT", conflict.stdout + conflict.stderr)
                finally:
                    shutil.rmtree(lab_path, ignore_errors=True)

        a5_lesson = data["lessons"]["auto_05"]
        a5_s = json.dumps(a5_lesson, ensure_ascii=False)
        self.assertIn("yaml.safe_load", a5_s)
        self.assertIn("defusedxml", a5_s)
        self.assertIn("YAML 1.1", a5_s)
        self.assertEqual(a5_lesson["bridge"]["nextId"], "auto_06")
        m_a5_py = re.search(r"```python\n([\s\S]+?)\n```", a5_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a5_py, "auto_05 runnable python block missing")
        ns_a5: dict = {}
        exec(compile(m_a5_py.group(1), "data_formats_lab.py", "exec"), ns_a5)
        self.assertEqual(
            ns_a5["inspect_payloads"](),
            {"ok": True, "device": "R1-CORE", "active_vlans": [10, 105], "xml_interfaces": ["GigabitEthernet0/7"]},
        )
        # Failure modes: trailing comma in JSON, missing XML namespace, malformed XML
        bad_json_res = ns_a5["inspect_payloads"]('{"device": "R1", "vlans": [1,],}')
        self.assertFalse(bad_json_res["ok"])
        self.assertTrue(bad_json_res["error"].startswith("invalid_json"))
        no_ns_res = ns_a5["inspect_payloads"](raw_xml="<interfaces><interface><name>Gi0/7</name></interface></interfaces>")
        self.assertEqual(no_ns_res, {"ok": False, "error": "missing_namespace_or_interfaces"})
        bad_xml_res = ns_a5["inspect_payloads"](raw_xml="<interfaces><broken></interfaces>")
        self.assertEqual(bad_xml_res, {"ok": False, "error": "invalid_xml"})
        # Schema validation: missing/invalid VLAN id must NOT raise KeyError
        for bad_schema in ('{"vlans": [{"active": true}]}', '{"vlans": [{"id": "10", "active": true}]}', '{"vlans": [{"id": true, "active": true}]}', '{"vlans": ["bad"]}'):
            self.assertEqual(ns_a5["inspect_payloads"](bad_schema), {"ok": False, "error": "invalid_vlan_entry"}, bad_schema)

        a6_lesson = data["lessons"]["auto_06"]
        a6_s = json.dumps(a6_lesson, ensure_ascii=False)
        self.assertIn("RFC 5789", a6_s)
        self.assertIn("406 Not Acceptable", a6_s)
        self.assertIn("429 Too Many Requests", a6_s)
        self.assertIn("Retry-After", a6_s)
        self.assertIn("allow_redirects=False", a6_s)
        self.assertIn("لزوماً اثبات نمی‌کند هویت کاربر تایید شده", a6_s)
        self.assertEqual(a6_lesson["bridge"]["nextId"], "auto_07")
        m_a6_py = re.search(r"```python\n([\s\S]+?)\n```", a6_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a6_py, "auto_06 runnable python block missing")
        ns_a6: dict = {}
        exec(compile(m_a6_py.group(1), "rest_client_safe.py", "exec"), ns_a6)
        import http.server
        import io
        import threading
        import urllib.error
        import urllib.request

        class FakeResp:
            def __init__(self, status: int, body: bytes) -> None:
                self.status = status
                self._body = body
            def read(self) -> bytes:
                return self._body
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False

        self.assertEqual(
            ns_a6["fetch_vlans_safely"]("https://10.255.0.1/vlans", "tok", opener=lambda req, timeout: FakeResp(200, b'{"vlans":[106]}')),
            {"ok": True, "status": 200, "data": {"vlans": [106]}},
        )
        # Non-HTTPS URL must be rejected before any opener call
        with self.assertRaises(ValueError):
            ns_a6["fetch_vlans_safely"]("http://10.255.0.1/vlans", "tok")

        for code, reason in [(401, "auth_failed"), (403, "forbidden"), (429, "rate_limited:12")]:
            def _err_opener(req, timeout, _code=code):
                raise urllib.error.HTTPError(req.full_url, _code, "err", {"Retry-After": "12"}, io.BytesIO(b""))
            self.assertEqual(
                ns_a6["fetch_vlans_safely"]("https://10.255.0.1/vlans", "tok", opener=_err_opener),
                {"ok": False, "status": code, "reason": reason},
            )

        # Redirect regression test: real urllib redirect pipeline with _NoRedirectHandler MUST block 302 to HTTP target without sending Authorization
        steal_hits = []

        class StealTrapHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                steal_hits.append(dict(self.headers))
                self.send_response(200)
                self.end_headers()
            def log_message(self, *args):
                pass

        trap_srv = http.server.HTTPServer(("127.0.0.1", 0), StealTrapHandler)
        trap_port = trap_srv.server_address[1]
        trap_thread = threading.Thread(target=trap_srv.serve_forever, daemon=True)
        trap_thread.start()
        try:
            import email.message
            hdrs = email.message.Message()
            hdrs["Location"] = f"http://127.0.0.1:{trap_port}/steal"

            class FakeHttpsRedirectTransport(urllib.request.HTTPSHandler):
                def https_open(self, req):
                    resp = urllib.request.addinfourl(io.BytesIO(b""), hdrs, req.full_url, code=302)
                    resp.msg = "Found"
                    return resp

            safe_redirect_opener = urllib.request.build_opener(FakeHttpsRedirectTransport(), ns_a6["_NoRedirectHandler"]()).open
            redir_res = ns_a6["fetch_vlans_safely"]("https://10.255.0.1/vlans", "secret-token", opener=safe_redirect_opener)
            self.assertEqual(redir_res, {"ok": False, "status": 302, "reason": "redirect_blocked"})
            self.assertEqual(steal_hits, [], "Token leaked across redirect!")
        finally:
            trap_srv.shutdown()
            trap_srv.server_close()

        a7_lesson = data["lessons"]["auto_07"]
        a7_s = json.dumps(a7_lesson, ensure_ascii=False)
        self.assertIn("HTTP/3", a7_s)
        self.assertIn("QUIC", a7_s)
        self.assertIn("TLS 1.3", a7_s)
        self.assertIn("PSK-only", a7_s)
        self.assertIn("psk_ke", a7_s)
        self.assertIn("Anti-Replay", a7_s)
        self.assertIn("0-RTT", a7_s)
        self.assertIn("SAN", a7_s)
        self.assertIn("mTLS", a7_s)
        self.assertIn("OAuth 2.0", a7_s)
        self.assertNotIn("عملیات غیرIdempotent (`POST`, `PUT`, `DELETE`)", a7_s)
        self.assertIn("عملیات تغییردهندهٔ وضعیتِ Idempotent مانند `PUT` و `DELETE`", a7_s)
        self.assertEqual(a7_lesson["bridge"]["nextId"], "auto_08")
        m_a7_py = re.search(r"```python\n([\s\S]+?)\n```", a7_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a7_py, "auto_07 runnable python block missing")
        ns_a7: dict = {}
        exec(compile(m_a7_py.group(1), "jwt_verify_lab.py", "exec"), ns_a7)
        valid_tok = ns_a7["create_hs256_jwt"]({"sub": "netops", "role": "viewer", "iss": "fam-auth", "aud": "net-api", "exp": 2000000000}, b"top-secret")
        self.assertEqual(
            ns_a7["verify_hs256_jwt"](valid_tok, b"top-secret", expected_iss="fam-auth", expected_aud="net-api", now=1900000000),
            {"ok": True, "claims": {"sub": "netops", "role": "viewer", "iss": "fam-auth", "aud": "net-api", "exp": 2000000000}},
        )
        # Trailing non-base64url characters ('!!!!') MUST be rejected strictly
        self.assertEqual(ns_a7["verify_hs256_jwt"](valid_tok + "!!!!", b"top-secret", now=1900000000), {"ok": False, "error": "malformed_token"})
        # Signed token with exp: NaN (or float('nan')) MUST be rejected
        nan_tok = ns_a7["create_hs256_jwt"]({"sub": "netops", "exp": float("nan")}, b"top-secret")
        self.assertEqual(ns_a7["verify_hs256_jwt"](nan_tok, b"top-secret", now=100), {"ok": False, "error": "malformed_token"})
        # Huge int exp (10**400) MUST NOT raise uncaught OverflowError from float()
        huge_exp_tok = ns_a7["create_hs256_jwt"]({"sub": "netops", "exp": 10**400}, b"top-secret")
        self.assertEqual(ns_a7["verify_hs256_jwt"](huge_exp_tok, b"top-secret", now=100), {"ok": False, "error": "missing_or_invalid_exp"})
        # Expired token (exp: 1) MUST be rejected
        expired_tok = ns_a7["create_hs256_jwt"]({"sub": "netops", "exp": 1, "iss": "fam-auth", "aud": "net-api"}, b"top-secret")
        self.assertEqual(ns_a7["verify_hs256_jwt"](expired_tok, b"top-secret", expected_iss="fam-auth", expected_aud="net-api", now=100), {"ok": False, "error": "token_expired"})
        # Missing exp MUST be rejected
        no_exp_tok = ns_a7["create_hs256_jwt"]({"sub": "netops"}, b"top-secret")
        self.assertEqual(ns_a7["verify_hs256_jwt"](no_exp_tok, b"top-secret", now=100), {"ok": False, "error": "missing_or_invalid_exp"})
        # Wrong audience / issuer MUST be rejected
        self.assertEqual(ns_a7["verify_hs256_jwt"](valid_tok, b"top-secret", expected_aud="wrong-api", now=1900000000), {"ok": False, "error": "invalid_aud"})
        self.assertEqual(ns_a7["verify_hs256_jwt"](valid_tok, b"top-secret", expected_iss="wrong-iss", now=1900000000), {"ok": False, "error": "invalid_iss"})
        # Tampered payload & alg=none MUST be rejected
        hdr_b64, pld_b64, sig_b64 = valid_tok.split(".")
        tampered_pld = ns_a7["_b64u_enc"](b'{"sub":"netops","role":"admin","exp":2000000000}')
        self.assertEqual(ns_a7["verify_hs256_jwt"](f"{hdr_b64}.{tampered_pld}.{sig_b64}", b"top-secret", now=1900000000), {"ok": False, "error": "invalid_signature"})
        none_hdr = ns_a7["_b64u_enc"](b'{"alg":"none","typ":"JWT"}')
        self.assertEqual(ns_a7["verify_hs256_jwt"](f"{none_hdr}.{tampered_pld}.{sig_b64}", b"top-secret", now=1900000000), {"ok": False, "error": "unsupported_alg"})
        # Malformed inputs MUST return controlled error without raising JSONDecodeError
        not_json = ns_a7["_b64u_enc"](b"{bad-json")
        list_json = ns_a7["_b64u_enc"](b"[1,2,3]")
        for bad_tok in ("not-a-jwt", "a.b", "a..c", "!!!.@@@.###", valid_tok + "=", f"{not_json}.{not_json}.{not_json}", f"{list_json}.{list_json}.{not_json}", 12345):
            self.assertEqual(ns_a7["verify_hs256_jwt"](bad_tok, b"top-secret", now=100), {"ok": False, "error": "malformed_token"}, bad_tok)

        a8_lesson = data["lessons"]["auto_08"]
        a8_s = json.dumps(a8_lesson, ensure_ascii=False)
        self.assertIn("RFC 6241", a8_s)
        self.assertIn("830", a8_s)
        self.assertIn("Chunked Framing", a8_s)
        self.assertIn("confirmed-commit", a8_s)
        self.assertIn("hostkey_verify=True", a8_s)
        self.assertIn("Shared", a8_s)
        self.assertIn("persist", a8_s)
        self.assertEqual(a8_lesson["bridge"]["nextId"], "auto_09")
        m_a8_py = re.search(r"```python\n([\s\S]+?)\n```", a8_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a8_py, "auto_08 runnable python block missing")
        ns_a8: dict = {}
        exec(compile(m_a8_py.group(1), "netconf_rpc_lab.py", "exec"), ns_a8)
        import xml.etree.ElementTree as ET
        # XML builder MUST escape '&' and tag-like text cleanly without ParseError or XML injection
        tricky_desc = "R&D </description><evil/>"
        cfg_payload = ns_a8["build_ncclient_config_payload"]("Gi0/7", tricky_desc)
        cfg_root = ET.fromstring(cfg_payload)
        self.assertTrue(cfg_root.tag.endswith("}config"))
        self.assertIsNone(cfg_root.find(".//evil"))
        self.assertEqual(cfg_root.findtext(".//{urn:ietf:params:xml:ns:yang:ietf-interfaces}description"), tricky_desc)

        rpc_xml = ns_a8["build_edit_config_rpc"]("101", "candidate", "Gi0/7", tricky_desc)
        rpc_root = ET.fromstring(rpc_xml)
        self.assertTrue(rpc_root.tag.endswith("}rpc"))
        self.assertEqual(rpc_root.attrib.get("message-id"), "101")
        self.assertEqual(rpc_root.findtext(".//{urn:ietf:params:xml:ns:yang:ietf-interfaces}description"), tricky_desc)

        # Simulate ncclient.edit_config expecting <config> root (and rejecting full <rpc>)
        class MockNcSession:
            def edit_config(self, target: str, config: str):
                root = ET.fromstring(config)
                if not root.tag.endswith("}config"):
                    raise ValueError("ncclient.edit_config expects <config> root, not <rpc>")
                return '<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>'

        mock_nc = MockNcSession()
        nc_reply = mock_nc.edit_config(target="candidate", config=cfg_payload)
        self.assertEqual(ns_a8["parse_rpc_reply"](nc_reply, "101"), {"ok": True, "msg_id": "101"})
        with self.assertRaises(ValueError):
            mock_nc.edit_config(target="candidate", config=rpc_xml)

        # Wrong root tag / missing NETCONF NS MUST fail!
        for bad_root_xml in (
            '<wrong message-id="101"><ok/></wrong>',
            '<wrong message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></wrong>',
            '<rpc-reply message-id="101"><ok/></rpc-reply>',
        ):
            r_bad_root = ns_a8["parse_rpc_reply"](bad_root_xml, "101")
            self.assertEqual(r_bad_root["ok"], False, bad_root_xml)
            self.assertEqual(r_bad_root["error_tag"], "unexpected-root", bad_root_xml)

        # Contradictory reply containing BOTH <ok/> and <rpc-error> MUST fail!
        ambig_xml = '<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/><rpc-error><error-tag>in-use</error-tag></rpc-error></rpc-reply>'
        r_ambig = ns_a8["parse_rpc_reply"](ambig_xml, "101")
        self.assertEqual(r_ambig["ok"], False)
        self.assertEqual(r_ambig["error_tag"], "ambiguous-reply")

        # Empty reply with neither <ok/> nor <rpc-error> MUST fail!
        r_empty = ns_a8["parse_rpc_reply"]('<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"></rpc-reply>', "101")
        self.assertEqual(r_empty["ok"], False)
        self.assertEqual(r_empty["error_tag"], "missing-ok-or-error")

        # Mismatched message-id MUST fail!
        mismatch_res = ns_a8["parse_rpc_reply"]('<rpc-reply message-id="999" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>', "101")
        self.assertEqual(mismatch_res["ok"], False)
        self.assertEqual(mismatch_res["error_tag"], "mismatched-message-id")

        # ---- Batch 6 (auto_09..auto_13) regression assertions ----
        a9_lesson = data["lessons"]["auto_09"]
        a9_s = json.dumps(a9_lesson, ensure_ascii=False)
        self.assertIn("RFC 8040", a9_s)
        self.assertIn("{+restconf}/data", a9_s)
        self.assertIn("content=config", a9_s)
        self.assertIn("content=nonconfig", a9_s)
        self.assertIn("406 Not Acceptable", a9_s)
        self.assertIn("replace-or-create", a9_s)
        self.assertEqual(a9_lesson["bridge"]["nextId"], "auto_10")
        self.assertEqual(a9_lesson["bridge"]["nextTitle"], data["lessons"]["auto_10"]["title"])
        m_a9_py = re.search(r"```python\n([\s\S]+?)\n```", a9_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a9_py, "auto_09 runnable python block missing")
        ns_a9: dict = {}
        exec(compile(m_a9_py.group(1), "restconf_client_lab.py", "exec"), ns_a9)

        # --- auto_09: REAL _SAFE_OPENER construction in the lesson MUST include _NoRedirectHandler ---
        # This checks the actual opener object built by the lesson code (not a rebuilt copy).
        # Mutation `_SAFE_OPENER = urllib.request.build_opener()` MUST fail here.
        a9_code = m_a9_py.group(1)
        a9_safe_lines = [ln for ln in a9_code.splitlines() if "_SAFE_OPENER" in ln and "build_opener" in ln]
        self.assertTrue(a9_safe_lines, "auto_09 _SAFE_OPENER construction line missing")
        self.assertIn("_NoRedirectHandler", a9_safe_lines[0],
                      "auto_09 real _SAFE_OPENER construction must include _NoRedirectHandler")
        a9_real_handlers = [type(h).__name__ for h in ns_a9["_SAFE_OPENER"].handlers]
        self.assertIn("_NoRedirectHandler", a9_real_handlers,
                      "auto_09 real _SAFE_OPENER object must contain _NoRedirectHandler handler")

        # --- auto_09: non-HTTPS rejection ---
        with self.assertRaises(ValueError):
            ns_a9["get_config"]("http://10.255.0.1/restconf/data?content=config", "tok")
        with self.assertRaises(ValueError):
            ns_a9["put_config"]("http://10.255.0.1/restconf/data?content=config", "x", "tok")

        # --- auto_09: real XML/JSON validation (positive + negative) ---
        class A9Hdr:
            def get(self, k, default=""):
                return "application/yang-data+xml"

        class A9Resp:
            def __init__(self, headers, status=200):
                self.headers = headers
                self.status = status

        valid_xml_body = "<data xmlns=\"urn:ietf:params:xml:ns:yang:ietf-interfaces\"><interface/></data>"
        err = ns_a9["_validate_response"](A9Resp(A9Hdr()), valid_xml_body)
        self.assertIsNone(err, "valid yang-data+xml with valid XML should pass")

        class A9HdrBad:
            def get(self, k, default=""):
                return "text/evil-yang-data+xml-and-other"

        err_ctype = ns_a9["_validate_response"](A9Resp(A9HdrBad()), "<data/>")
        self.assertIsNotNone(err_ctype)
        self.assertEqual(err_ctype["ok"], False)
        self.assertEqual(err_ctype["error"], "invalid_content_type")

        class A9HdrJson:
            def get(self, k, default=""):
                return "application/yang-data+json"

        err_json = ns_a9["_validate_response"](A9Resp(A9HdrJson()), "{invalid json")
        self.assertIsNotNone(err_json)
        self.assertEqual(err_json["ok"], False)
        self.assertEqual(err_json["error"], "invalid_json")

        err_xml = ns_a9["_validate_response"](A9Resp(A9Hdr()), "<not xml")
        self.assertIsNotNone(err_xml)
        self.assertEqual(err_xml["ok"], False)
        self.assertEqual(err_xml["error"], "invalid_xml")

        # --- auto_09: default opener MUST block redirect — REAL _SAFE_OPENER construction tested ---
        # Start an HTTP server that would steal the token if redirected to
        a9_steal: list = []

        class A9StealHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                a9_steal.append(dict(self.headers))
                self.send_response(200)
                self.end_headers()
            def log_message(self, *args):
                pass

        a9_trap = http.server.HTTPServer(("127.0.0.1", 0), A9StealHandler)
        a9_port = a9_trap.server_address[1]
        a9_thread = threading.Thread(target=a9_trap.serve_forever, daemon=True)
        a9_thread.start()
        try:
            # Fake HTTPS transport returning 302 redirect to HTTP steal server
            hdrs = email.message.Message()
            hdrs["Location"] = f"http://127.0.0.1:{a9_port}/steal"

            class A9FakeRedirectTransport(urllib.request.HTTPSHandler):
                def https_open(self, req):
                    resp = urllib.request.addinfourl(io.BytesIO(b""), hdrs, req.full_url, code=302)
                    resp.msg = "Found"
                    return resp

            # --- TEST 1: REBUILD _SAFE_OPENER with fake transport + _NoRedirectHandler ---
            # This tests the REAL construction pattern from the lesson code.
            # We rebuild _SAFE_OPENER the same way the lesson does, but with fake transport.
            ns_a9["_SAFE_OPENER"] = urllib.request.build_opener(
                ns_a9["_NoRedirectHandler"](), A9FakeRedirectTransport()
            )
            a9_redir = ns_a9["get_config"]("https://10.255.0.1/restconf/data?content=config", "TEST_TOKEN")
            self.assertEqual(a9_redir["ok"], False)
            self.assertEqual(a9_redir["status"], 302)
            self.assertEqual(a9_steal, [], "auto_09 token leaked via _SAFE_OPENER with _NoRedirectHandler!")

            # --- TEST 2: MUTATION — rebuild _SAFE_OPENER WITHOUT _NoRedirectHandler ---
            # This is exactly what the user did: _SAFE_OPENER = urllib.request.build_opener()
            # The test MUST fail because redirect is followed and token leaks.
            a9_steal.clear()
            ns_a9["_SAFE_OPENER"] = urllib.request.build_opener(A9FakeRedirectTransport())
            a9_leak = ns_a9["get_config"]("https://10.255.0.1/restconf/data?content=config", "TEST_TOKEN")
            self.assertTrue(a9_steal, "mutation: _SAFE_OPENER without _NoRedirectHandler MUST leak token")
            leaked_hdrs = a9_steal[0] if a9_steal else {}
            self.assertIn("Authorization", leaked_hdrs)
            self.assertIn("TEST_TOKEN", leaked_hdrs["Authorization"])

            # --- TEST 3: PUT with _SAFE_OPENER + _NoRedirectHandler also blocks redirect ---
            a9_steal.clear()
            ns_a9["_SAFE_OPENER"] = urllib.request.build_opener(
                ns_a9["_NoRedirectHandler"](), A9FakeRedirectTransport()
            )
            a9_redir_put = ns_a9["put_config"]("https://10.255.0.1/restconf/data?content=config", "<x/>", "TEST_TOKEN")
            self.assertEqual(a9_redir_put["ok"], False)
            self.assertEqual(a9_redir_put["status"], 302)
            self.assertEqual(a9_steal, [], "auto_09 token leaked via PUT default path!")
        finally:
            a9_trap.shutdown()
            a9_trap.server_close()

        a10_lesson = data["lessons"]["auto_10"]
        a10_s = json.dumps(a10_lesson, ensure_ascii=False)
        self.assertIn("RFC 7950", a10_s)
        self.assertIn("length", a10_s)
        self.assertIn("mandatory", a10_s)
        self.assertIn("pyang", a10_s)
        self.assertIn("ناکافی", a10_s)
        self.assertEqual(a10_lesson["bridge"]["nextId"], "auto_11")
        self.assertEqual(a10_lesson["bridge"]["nextTitle"], data["lessons"]["auto_11"]["title"])
        m_a10_py = re.search(r"```python\n([\s\S]+?)\n```", a10_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a10_py, "auto_10 runnable python block missing")
        ns_a10: dict = {}
        exec(compile(m_a10_py.group(1), "yang_model_lab.py", "exec"), ns_a10)
        _yang_src = m_a10_py.group(1).split("yang_src = ", 1)[1].strip()
        _yang_body = _yang_src[3:-3] if _yang_src.startswith(chr(39) * 3) else _yang_src

        # YANG text validation
        self.assertEqual(ns_a10["validate_yang_text"](_yang_body)["ok"], True)
        self.assertEqual(ns_a10["validate_yang_text"]("this is not yang"), {"ok": False, "error": "missing_module"})
        self.assertEqual(ns_a10["validate_yang_text"]("module x {"), {"ok": False, "error": "missing_namespace"})

        # Per-list key extraction: keys are grouped by list
        lists = ns_a10["extract_list_keys"](_yang_body)
        self.assertIn("interfaces", lists)
        self.assertIn("my-list", lists)
        self.assertIn("name", lists["interfaces"])
        self.assertIn("my-id", lists["my-list"])

        # Payload for interfaces list: must NOT require my-id
        self.assertEqual(
            ns_a10["validate_payload_against_model"]({"name": "Gi0/7", "enabled": True}, _yang_body),
            {"ok": True},
        )
        # Payload for my-list list: must NOT require name
        self.assertEqual(
            ns_a10["validate_payload_against_model"]({"my-id": "x1", "tag": "t"}, _yang_body),
            {"ok": True},
        )
        # Missing key: enabled only (no name, no my-id) — cannot detect any list
        result_missing = ns_a10["validate_payload_against_model"]({"enabled": True}, _yang_body)
        self.assertEqual(result_missing["ok"], False)
        self.assertEqual(result_missing["error"], "cannot_detect_list")
        # Unknown list name must NOT succeed
        result_unknown = ns_a10["validate_payload_against_model"]({}, _yang_body, "nonexistent")
        self.assertEqual(result_unknown["ok"], False)
        self.assertEqual(result_unknown["error"], "unknown_list")
        # Ambiguous payload (keys of two lists) must error, not silently pick one
        result_amb = ns_a10["validate_payload_against_model"]({"name": "a", "my-id": "b"}, _yang_body)
        self.assertEqual(result_amb["ok"], False)
        self.assertEqual(result_amb["error"], "ambiguous_list")
        # Explicit target_list with wrong payload must fail with missing key
        result_explicit = ns_a10["validate_payload_against_model"]({"my-id": "b"}, _yang_body, "interfaces")
        self.assertEqual(result_explicit["ok"], False)
        self.assertEqual(result_explicit["error"], "missing_required_key")

        a11_lesson = data["lessons"]["auto_11"]
        a11_s = json.dumps(a11_lesson, ensure_ascii=False)
        self.assertIn("control node", a11_s)
        self.assertIn("managed node", a11_s)
        self.assertIn("inventory", a11_s)
        self.assertIn("ios_config", a11_s)
        self.assertIn("parents", a11_s)
        self.assertIn("handlers", a11_s)
        self.assertIn("cisco.ios", a11_s)
        self.assertIn("ios_routers", a11_s)
        self.assertNotIn("managed node لزوماً باید python داشته باشد", a11_s)
        # Single host is valid, not wrong
        self.assertNotIn("hosts: بر اساس یک host واحد", a11_s)
        # Quiz Q3 must have exactly ONE correct answer (combined group/host/pattern)
        a11_q3 = a11_lesson["quiz"][2]
        self.assertEqual(a11_q3["ans"], 2)
        self.assertIn("group", a11_q3["opts"][2])
        self.assertIn("host واحد", a11_q3["opts"][2])
        self.assertIn("pattern", a11_q3["opts"][2])
        self.assertIn("فقط می‌تواند", a11_q3["opts"][0])
        self.assertEqual(a11_lesson["bridge"]["nextId"], "auto_12")
        self.assertEqual(a11_lesson["bridge"]["nextTitle"], data["lessons"]["auto_12"]["title"])
        m_a11_py = re.search(r"```python\n([\s\S]+?)\n```", a11_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a11_py, "auto_11 runnable python block missing")
        ns_a11: dict = {}
        exec(compile(m_a11_py.group(1), "ansible_playbook_lab.py", "exec"), ns_a11)
        a11_step_txt = a11_lesson["lab"]["steps"][4]
        self.assertIn("parents:", a11_step_txt)
        self.assertNotIn("parent:", a11_step_txt)
        _yaml_src = m_a11_py.group(1)
        _pb_body = _yaml_src.split("playbook_yaml = ", 1)[1].strip()
        _pb_body = _pb_body[3:-3] if _pb_body.startswith(chr(39) * 3) else _pb_body
        pb = ns_a11["parse_playbook"](_pb_body)
        self.assertTrue(len(pb["plays"]) >= 1)
        self.assertEqual(pb["plays"][0]["hosts"], "ios_routers")
        self.assertTrue(any(t["module"] == "cisco.ios.ios_config" for t in pb["plays"][0]["tasks"]))
        _inv_m = re.search(r"inventory_yaml = " + chr(39) * 3 + r"([\s\S]+?)" + chr(39) * 3, _yaml_src)
        self.assertIsNotNone(_inv_m, "auto_11 lab inventory_yaml literal missing")
        _inv_body = _inv_m.group(1)
        inv = ns_a11["parse_inventory"](_inv_body)
        self.assertIn("router1", inv["hosts"])
        self.assertEqual(inv["hosts"]["router1"].get("ansible_connection"), "network_cli")
        self.assertIn("router1", inv["groups"].get("ios_routers", set()))
        self.assertEqual(ns_a11["simulate_state_compare"]({"vlan": 111}, {"vlan": 111})["changed"], 0)
        self.assertEqual(ns_a11["simulate_state_compare"]({"vlan": 111}, {"vlan": 10})["changed"], 1)

        a12_lesson = data["lessons"]["auto_12"]
        a12_s = json.dumps(a12_lesson, ensure_ascii=False)
        self.assertIn("HCL", a12_s)
        self.assertIn("provider", a12_s)
        self.assertIn("state lifecycle", a12_s)
        self.assertIn("terraform plan", a12_s)
        self.assertIn("terraform apply", a12_s)
        self.assertIn("-refresh-only", a12_s)
        self.assertIn("state drift", a12_s)
        self.assertIn("شبه‌کد", a12_s)
        self.assertIn("وضعیت مشاهده‌شده", a12_s)
        self.assertIn("محدودیت", a12_s)  # Mock limitation documented
        self.assertNotIn("-refresh-only منابع واقعی را به مطلوب برمی‌گرداند", a12_s)
        cyr = re.findall(r'[\u0400-\u04FF]+', a12_s)
        self.assertEqual(cyr, [], f"Cyrillic garble in auto_12: {cyr}")
        self.assertEqual(a12_lesson["bridge"]["nextId"], "auto_13")
        self.assertEqual(a12_lesson["bridge"]["nextTitle"], data["lessons"]["auto_13"]["title"])
        m_a12_py = re.search(r"```python\n([\s\S]+?)\n```", a12_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a12_py, "auto_12 runnable python block missing")
        ns_a12: dict = {}
        exec(compile(m_a12_py.group(1), "terraform_lab.py", "exec"), ns_a12)

        # Lifecycle: first run creates, second idempotent
        prov12 = ns_a12["MockProvider"](state={"vlan_112": None}, reality={"vlan_112": None})
        run1 = ns_a12["run_lifecycle"](prov12, {"vlan_112": "TERRAFORM_IAC"})
        self.assertEqual(run1["plan_changes"], 1)
        self.assertEqual(run1["applied_changes"], 1)
        self.assertEqual(run1["state"], {"vlan_112": "TERRAFORM_IAC"})
        run2 = ns_a12["run_lifecycle"](prov12, {"vlan_112": "TERRAFORM_IAC"})
        self.assertEqual(run2["plan_changes"], 0)
        self.assertEqual(run2["applied_changes"], 0)

        # Drift scenario: state == desired, reality changed (manual change)
        # Mock plan does NOT refresh (documented limitation) — drift NOT visible in plan
        prov_drift = ns_a12["MockProvider"](state={"vlan_112": "TERRAFORM_IAC"}, reality={"vlan_112": "MANUAL_CHANGE"})
        plan_no_refresh = prov_drift.plan({"vlan_112": "TERRAFORM_IAC"})
        # Mock limitation: plan sees state==desired, so 0 changes (drift NOT detected)
        self.assertEqual(len(plan_no_refresh["changes"]), 0)

        # refresh-only plan: proposal sync state, state NOT mutated
        refresh_result = prov_drift.refresh_only_plan({"vlan_112": "TERRAFORM_IAC"})
        self.assertEqual(prov_drift.state, {"vlan_112": "TERRAFORM_IAC"})
        self.assertEqual(prov_drift.reality, {"vlan_112": "MANUAL_CHANGE"})
        self.assertEqual(len(refresh_result["changes"]), 1)
        self.assertEqual(refresh_result["changes"][0]["action"], "update-state-only")

        # apply_refresh_only: state synced, reality unchanged
        prov_drift.apply_refresh_only()
        self.assertEqual(prov_drift.state, {"vlan_112": "MANUAL_CHANGE"})
        self.assertEqual(prov_drift.reality, {"vlan_112": "MANUAL_CHANGE"})

        # After refresh-only: state==reality, plan shows 1 change vs desired
        after_plan = prov_drift.plan({"vlan_112": "TERRAFORM_IAC"})
        self.assertEqual(len(after_plan["changes"]), 1)

        a13_lesson = data["lessons"]["auto_13"]
        a13_s = json.dumps(a13_lesson, ensure_ascii=False)
        self.assertIn("Cisco NSO", a13_s)
        self.assertIn("northbound", a13_s)
        self.assertIn("southbound", a13_s)
        self.assertIn("NETCONF", a13_s)
        self.assertIn("RESTCONF", a13_s)
        self.assertIn("service point", a13_s)
        self.assertIn("service package", a13_s)
        self.assertIn("NED", a13_s)
        self.assertIn("transaction", a13_s)
        self.assertIn("rollback", a13_s)
        self.assertIn("شبه‌کد", a13_s)
        self.assertIn("غیرنماینده", a13_s)
        # servicepoint must NOT be defined as "کدام equipment/driver"
        self.assertNotIn("equipment/driver مسئول", a13_s)
        self.assertEqual(a13_lesson["bridge"]["nextId"], "auto_14")
        self.assertEqual(a13_lesson["bridge"]["nextTitle"], data["lessons"]["auto_14"]["title"])
        m_a13_py = re.search(r"```python\n([\s\S]+?)\n```", a13_lesson["lab"]["steps"][4])
        self.assertIsNotNone(m_a13_py, "auto_13 runnable python block missing")
        ns_a13: dict = {}
        exec(compile(m_a13_py.group(1), "nso_service_lab.py", "exec"), ns_a13)
        nso13 = ns_a13["MockNso"](reachable_devices={"target-router"})
        res13 = nso13.provision_service("fam-lan", {"target-router": {"lan-vlan": 113}})
        self.assertEqual(res13["ok"], True)
        self.assertEqual(len(res13["steps"]), 1)
        self.assertEqual(res13["steps"][0]["device"], "target-router")
        self.assertEqual(res13["rolled_back"], False)
        res13_bad = nso13.provision_service("fam-lan-bad", {"target-router": {"lan-vlan": 113}, "bad-router": {"lan-vlan": 113}})
        self.assertEqual(res13_bad["ok"], False)
        self.assertIn("unreachable", res13_bad["error"])
        self.assertEqual(res13_bad["rolled_back"], True)
        self.assertTrue(any(s["action"] == "rollback" for s in res13_bad["steps"]))

        # 3. Simulator persistence & extracted lab commands verification
        m_mode = re.search(r"low === 'switchport mode access'[\s\S]*?(?=\} else if)", app_js)
        self.assertIsNotNone(m_mode)
        self.assertNotIn("nonegotiate = false", m_mode.group(0))
        self.assertIn("no switchport nonegotiate", app_js)

        node_bin = shutil.which("node")
        if not node_bin:
            msg = "Node.js binary not available; simulator VM verification could not run"
            if os.environ.get("FAM_REQUIRE_NODE") == "1":
                self.fail(msg)
            self.skipTest(msg)

        # Extract CLI commands directly from lab.steps[2] of each f4 Batch 1..6 lesson
        extracted_labs = {}
        for lid in f4_b1_to_b6:
            step_txt = data["lessons"][lid]["lab"]["steps"][2]
            start_idx = step_txt.index("`configure terminal`")
            cmds = re.findall(r"`([^`]+)`", step_txt[start_idx:])
            self.assertGreaterEqual(len(cmds), 8, lid)
            self.assertEqual(cmds[0], "configure terminal", lid)
            self.assertEqual(cmds[-1], "end", lid)
            extracted_labs[lid] = cmds

        js_script = f"""
const fs = require('fs');
const vm = require('vm');
const ACADEMY = JSON.parse(fs.readFileSync({json.dumps(str(ASSET_ROOT / 'academy-data.json'))}, 'utf8'));
const appCode = fs.readFileSync({json.dumps(str(ASSET_ROOT / 'app.js'))}, 'utf8');
const extractedLabs = {json.dumps(extracted_labs)};
const s = appCode.indexOf('function createInitialSim()');
const e = appCode.indexOf('/* ---------- رندر صفحه عمومی (/academy) ---------- */');
const simCode = appCode.slice(s, e);
function run(cmds) {{
  const outEl = {{ textContent: '', scrollTop: 0, scrollHeight: 0 }};
  const prEl = {{ textContent: '' }};
  const ctx = {{ ACADEMY, state: {{ cliMode: 'user' }} }};
  vm.runInNewContext(simCode + '\\nfunction getSim(){{ return sim; }}', ctx);
  return {{
    out: cmds.map(c => {{ outEl.textContent=''; ctx.runIosCommand(c, outEl, prEl); return outEl.textContent; }}),
    sim: ctx.getSim()
  }};
}}
function isSimError(out) {{
  const lines = (out || '').split(/\\r?\\n/);
  return lines.some(raw => {{
    const line = raw.trim();
    if (!line.startsWith('%')) return false;
    // Healthy informational syslog notifications (not errors)
    if (/^%(LINK|LINEPROTO)-\\d+-/.test(line)) return false;
    return true;
  }});
}}

const r = run(['enable','configure terminal','interface Gi0/2','switchport mode access','switchport nonegotiate','end','show running-config','configure terminal','interface Gi0/2','switchport mode access','end','show running-config','configure terminal','interface Gi0/2','no switchport nonegotiate','end','show interfaces Gi0/2 switchport']);
if (r.out[6] !== r.out[11]) throw new Error('repeated mode access altered running-config');
if (!r.out[11].includes('switchport nonegotiate')) throw new Error('nonegotiate lost after repeated mode access');
if (r.sim.interfaces['GigabitEthernet0/2'].nonegotiate !== false) throw new Error('no switchport nonegotiate failed');
const neg = run(['enable','configure terminal','interface Gi0/0','switchport nonegotiate','no switchport nonegotiate']);
if (!isSimError(neg.out[3]) || !isSimError(neg.out[4])) throw new Error('routed interface accepted nonegotiate');

function assertRunLab(id, verifyFn) {{
  const cmds = ['enable'].concat(extractedLabs[id]).concat(['show running-config']).concat(extractedLabs[id]).concat(['show running-config']);
  const res = run(cmds);
  for (let i = 0; i < res.out.length; i++) {{
    if (isSimError(res.out[i])) {{
      throw new Error(id + ' failed on ' + cmds[i] + ': ' + res.out[i]);
    }}
  }}
  const firstRunIdx = 1 + extractedLabs[id].length;
  const secondRunIdx = res.out.length - 1;
  if (res.out[firstRunIdx] !== res.out[secondRunIdx]) {{
    throw new Error(id + ' was not idempotent on repeated lab execution');
  }}
  verifyFn(res.sim, res.out[secondRunIdx]);
}}

// Negative & positive tests for line-by-line error detection
for (const badCmds of [
  ['enable'].concat(extractedLabs['spec_ent']).concat(['totally unsupported command']),
  ['enable', 'configure terminal', 'interface Gi0/99'],
  ['enable', 'configure terminal', 'vlan 9999'],
  ['enable', 'configure terminal', 'shutdown'],
  ['configure terminal']
]) {{
  const res = run(badCmds);
  if (!res.out.some(o => isSimError(o))) {{
    throw new Error('Negative test failed to catch simulator error for: ' + JSON.stringify(badCmds));
  }}
}}
const healthyInfo = run(['enable', 'configure terminal', 'interface Gi0/2', 'shutdown', 'no shutdown']);
if (isSimError(healthyInfo.out[3]) || isSimError(healthyInfo.out[4])) {{
  throw new Error('Informational syslog (%LINK/%LINEPROTO) was misclassified as simulator error');
}}

// Explicit per-VLAN and per-port assertions for all 10 f4 lessons (Batch 1 + Batch 2)
assertRunLab('spec_ent', (sim) => {{
  if (!sim.vlans[210] || sim.vlans[210].name !== 'VN_CORP_HANDOFF') throw new Error('spec_ent VLAN 210');
  if (!sim.vlans[220] || sim.vlans[220].name !== 'VN_GUEST_HANDOFF') throw new Error('spec_ent VLAN 220');
  if (sim.interfaces['GigabitEthernet0/6'].accessVlan !== 210) throw new Error('spec_ent Gi0/6 vlan');
  if (sim.interfaces['GigabitEthernet0/7'].accessVlan !== 220) throw new Error('spec_ent Gi0/7 vlan');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(210) || !allowed.includes(220)) throw new Error('spec_ent trunk missing 210/220');
}});
assertRunLab('spec_ent_campus', (sim) => {{
  if (!sim.vlans[150] || sim.vlans[150].name !== 'CORE_MGMT_OOB') throw new Error('spec_ent_campus VLAN 150');
  if (!sim.vlans[10]) throw new Error('spec_ent_campus VLAN 10');
  if (!sim.interfaces['GigabitEthernet0/1'].nonegotiate) throw new Error('spec_ent_campus nonegotiate');
  if (!sim.interfaces['GigabitEthernet0/1'].allowedVlans.includes(150)) throw new Error('spec_ent_campus trunk 150');
  if (sim.interfaces['GigabitEthernet0/6'].accessVlan !== 150) throw new Error('spec_ent_campus Gi0/6');
  if (sim.interfaces['GigabitEthernet0/7'].accessVlan !== 10) throw new Error('spec_ent_campus Gi0/7');
}});
assertRunLab('spec_ent_sd', (sim) => {{
  if (!sim.vlans[10] || sim.vlans[10].name !== 'BRANCH_DATA_VPN10') throw new Error('spec_ent_sd VLAN 10');
  if (!sim.vlans[20] || sim.vlans[20].name !== 'BRANCH_VOICE_VPN20') throw new Error('spec_ent_sd VLAN 20');
  if (!sim.vlans[99] || sim.vlans[99].name !== 'UNUSED_PARK') throw new Error('spec_ent_sd VLAN 99');
  if (!sim.interfaces['GigabitEthernet0/1'].nonegotiate) throw new Error('spec_ent_sd Gi0/1 nonegotiate');
  if (sim.interfaces['GigabitEthernet0/6'].voiceVlan !== 20 || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 20) throw new Error('spec_ent_sd Gi0/6');
  if (sim.interfaces['GigabitEthernet0/7'].adminUp !== false || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 99) throw new Error('spec_ent_sd Gi0/7');
}});
assertRunLab('spec_sec', (sim) => {{
  if (!sim.vlans[30] || sim.vlans[30].name !== 'TRUST_USERS') throw new Error('spec_sec VLAN 30');
  if (!sim.vlans[40] || sim.vlans[40].name !== 'QUARANTINE_ISOLATED') throw new Error('spec_sec VLAN 40');
  if (!sim.vlans[999] || sim.vlans[999].name !== 'PARK_SHUT') throw new Error('spec_sec VLAN 999');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 30) throw new Error('spec_sec Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/2'].adminUp || sim.interfaces['GigabitEthernet0/2'].accessVlan !== 40) throw new Error('spec_sec Gi0/2');
  if (sim.interfaces['GigabitEthernet0/7'].adminUp !== false || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 999) throw new Error('spec_sec Gi0/7');
}});
assertRunLab('spec_sec_vpn', (sim) => {{
  if (!sim.vlans[35] || sim.vlans[35].name !== 'CORP_ENCRYPT_LAN') throw new Error('spec_sec_vpn VLAN 35');
  if (!sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 35) throw new Error('spec_sec_vpn Gi0/7');
  if (!sim.interfaces['GigabitEthernet0/1'].allowedVlans.includes(35)) throw new Error('spec_sec_vpn Gi0/1 allowed 35');
}});
assertRunLab('spec_sec_ise', (sim) => {{
  if (!sim.vlans[90] || sim.vlans[90].name !== 'ISE_OOB_MGMT') throw new Error('spec_sec_ise VLAN 90');
  if (!sim.vlans[92] || sim.vlans[92].name !== 'POSTURE_QUARANTINE') throw new Error('spec_sec_ise VLAN 92');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 90) throw new Error('spec_sec_ise Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 92) throw new Error('spec_sec_ise Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(90) || !allowed.includes(92)) throw new Error('spec_sec_ise trunk 90/92');
}});
assertRunLab('spec_dc_nx', (sim) => {{
  if (!sim.vlans[100] || sim.vlans[100].name !== 'DC_APP_PROD') throw new Error('spec_dc_nx VLAN 100');
  if (!sim.vlans[105] || sim.vlans[105].name !== 'DC_DB_PROD') throw new Error('spec_dc_nx VLAN 105');
  if (!sim.vlans[199] || sim.vlans[199].name !== 'DC_MGMT_OOB') throw new Error('spec_dc_nx VLAN 199');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 100) throw new Error('spec_dc_nx Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 199) throw new Error('spec_dc_nx Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!sim.interfaces['GigabitEthernet0/1'].nonegotiate || !allowed.includes(100) || !allowed.includes(105) || !allowed.includes(199)) throw new Error('spec_dc_nx trunk');
}});
assertRunLab('s11', (sim) => {{
  if (!sim.vlans[110] || sim.vlans[110].name !== 'L2VNI_10110_WEB') throw new Error('s11 VLAN 110');
  if (!sim.vlans[120] || sim.vlans[120].name !== 'L2VNI_10120_APP') throw new Error('s11 VLAN 120');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 110) throw new Error('s11 Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 120) throw new Error('s11 Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(110) || !allowed.includes(120)) throw new Error('s11 trunk');
}});
assertRunLab('spec_dc_aci', (sim) => {{
  if (!sim.vlans[130] || sim.vlans[130].name !== 'EPG_WEB_ENCAP') throw new Error('spec_dc_aci VLAN 130');
  if (!sim.vlans[135] || sim.vlans[135].name !== 'EPG_DB_ENCAP') throw new Error('spec_dc_aci VLAN 135');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 130) throw new Error('spec_dc_aci Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 135) throw new Error('spec_dc_aci Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(130) || !allowed.includes(135)) throw new Error('spec_dc_aci trunk');
}});
assertRunLab('spec_dc_stor', (sim) => {{
  if (!sim.vlans[140] || sim.vlans[140].name !== 'SAN_FABRIC_A_SIM') throw new Error('spec_dc_stor VLAN 140');
  if (!sim.vlans[145] || sim.vlans[145].name !== 'SAN_FABRIC_B_SIM') throw new Error('spec_dc_stor VLAN 145');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 140) throw new Error('spec_dc_stor Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 145) throw new Error('spec_dc_stor Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(140) || allowed.includes(145)) throw new Error('spec_dc_stor trunk isolation');
}});
assertRunLab('spec_sp', (sim) => {{
  if (!sim.vlans[150] || sim.vlans[150].name !== 'CUST_A_CE_HANDOFF') throw new Error('spec_sp VLAN 150');
  if (!sim.vlans[155] || sim.vlans[155].name !== 'CUST_B_CE_HANDOFF') throw new Error('spec_sp VLAN 155');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 150) throw new Error('spec_sp Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 155) throw new Error('spec_sp Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(150) || !allowed.includes(155)) throw new Error('spec_sp trunk');
}});
assertRunLab('spec_sp_xr', (sim) => {{
  if (!sim.vlans[160] || sim.vlans[160].name !== 'XR_CORE_LINK') throw new Error('spec_sp_xr VLAN 160');
  if (!sim.vlans[165] || sim.vlans[165].name !== 'XR_EBGP_PEER') throw new Error('spec_sp_xr VLAN 165');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 160) throw new Error('spec_sp_xr Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 165) throw new Error('spec_sp_xr Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(160) || !allowed.includes(165)) throw new Error('spec_sp_xr trunk');
}});
assertRunLab('spec_sp_sr', (sim) => {{
  if (!sim.vlans[170] || sim.vlans[170].name !== 'SR_UNDERLAY_P1') throw new Error('spec_sp_sr VLAN 170');
  if (!sim.vlans[175] || sim.vlans[175].name !== 'SR_ANYCAST_P2') throw new Error('spec_sp_sr VLAN 175');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 170) throw new Error('spec_sp_sr Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 175) throw new Error('spec_sp_sr Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(170) || !allowed.includes(175)) throw new Error('spec_sp_sr trunk');
}});
assertRunLab('spec_wl', (sim) => {{
  if (!sim.vlans[180] || sim.vlans[180].name !== 'WL_CORP_DATA') throw new Error('spec_wl VLAN 180');
  if (!sim.vlans[185] || sim.vlans[185].name !== 'WL_GUEST_CAPWAP') throw new Error('spec_wl VLAN 185');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 180) throw new Error('spec_wl Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 185) throw new Error('spec_wl Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(180) || !allowed.includes(185)) throw new Error('spec_wl trunk');
}});
assertRunLab('spec_wl_survey', (sim) => {{
  if (!sim.vlans[190] || sim.vlans[190].name !== 'WL_FLOOR_5_PROD') throw new Error('spec_wl_survey VLAN 190');
  if (!sim.vlans[195] || sim.vlans[195].name !== 'WL_FLOOR_6_PROD') throw new Error('spec_wl_survey VLAN 195');
  if (!sim.interfaces['GigabitEthernet0/6'].nonegotiate || sim.interfaces['GigabitEthernet0/6'].accessVlan !== 190) throw new Error('spec_wl_survey Gi0/6');
  if (!sim.interfaces['GigabitEthernet0/7'].nonegotiate || !sim.interfaces['GigabitEthernet0/7'].adminUp || sim.interfaces['GigabitEthernet0/7'].accessVlan !== 195) throw new Error('spec_wl_survey Gi0/7');
  const allowed = sim.interfaces['GigabitEthernet0/1'].allowedVlans;
  if (!allowed.includes(190) || !allowed.includes(195)) throw new Error('spec_wl_survey trunk');
}});
assertRunLab('spec_collab', (sim) => {{
  if (!sim.vlans[30] || sim.vlans[30].name !== 'VOICE') throw new Error('spec_collab VLAN 30');
  const gi3 = sim.interfaces['GigabitEthernet0/3'];
  if (!gi3.nonegotiate || gi3.mode !== 'access' || gi3.accessVlan !== 10 || gi3.voiceVlan !== 30) throw new Error('spec_collab Gi0/3');
}});
assertRunLab('spec_collab_gw', (sim) => {{
  if (!sim.vlans[30] || sim.vlans[30].name !== 'VOICE') throw new Error('spec_collab_gw VLAN 30');
  if (!sim.interfaces['GigabitEthernet0/1'].allowedVlans.includes(30)) throw new Error('spec_collab_gw Gi0/1 trunk 30');
  const gi6 = sim.interfaces['GigabitEthernet0/6'];
  if (gi6.mode !== 'trunk' || !gi6.nonegotiate || gi6.nativeVlan !== 10 || !gi6.allowedVlans.includes(30) || gi6.desc !== 'CUBE-GW') throw new Error('spec_collab_gw Gi0/6');
}});
assertRunLab('auto_01', (sim) => {{
  if (!sim.vlans[99] || sim.vlans[99].name !== 'MGMT') throw new Error('auto_01 VLAN 99');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 99 || gi7.desc !== 'LINUX-NETOPS') throw new Error('auto_01 Gi0/7');
}});
assertRunLab('auto_02', (sim) => {{
  if (!sim.vlans[99] || sim.vlans[99].name !== 'NETOPS') throw new Error('auto_02 VLAN 99');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 99 || gi7.desc !== 'PY-CONTROLLER') throw new Error('auto_02 Gi0/7');
}});
assertRunLab('auto_03', (sim) => {{
  if (!sim.vlans[99] || sim.vlans[99].name !== 'AUTOMATION') throw new Error('auto_03 VLAN 99');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 99 || gi7.desc !== 'NORNIR-RUNNER') throw new Error('auto_03 Gi0/7');
}});
assertRunLab('auto_04', (sim) => {{
  if (!sim.vlans[104] || sim.vlans[104].name !== 'GIT_REPO') throw new Error('auto_04 VLAN 104');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 104 || gi7.desc !== 'GITOPS-RUNNER') throw new Error('auto_04 Gi0/7');
}});
assertRunLab('auto_05', (sim) => {{
  if (!sim.vlans[105] || sim.vlans[105].name !== 'DATA_MODELS') throw new Error('auto_05 VLAN 105');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 105 || gi7.desc !== 'SCHEMA-LAB') throw new Error('auto_05 Gi0/7');
}});
assertRunLab('auto_06', (sim) => {{
  if (!sim.vlans[106] || sim.vlans[106].name !== 'API_MGMT') throw new Error('auto_06 VLAN 106');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 106 || gi7.desc !== 'API-CLIENT') throw new Error('auto_06 Gi0/7');
}});
assertRunLab('auto_07', (sim) => {{
  if (!sim.vlans[107] || sim.vlans[107].name !== 'TLS_PKI') throw new Error('auto_07 VLAN 107');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 107 || gi7.desc !== 'PKI-GATEWAY') throw new Error('auto_07 Gi0/7');
}});
assertRunLab('auto_08', (sim) => {{
  if (!sim.vlans[108] || sim.vlans[108].name !== 'NETCONF_830') throw new Error('auto_08 VLAN 108');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 108 || gi7.desc !== 'NETCONF-CLIENT') throw new Error('auto_08 Gi0/7');
}});
assertRunLab('auto_09', (sim) => {{
  if (!sim.vlans[109] || sim.vlans[109].name !== 'RESTCONF_830') throw new Error('auto_09 VLAN 109');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 109 || gi7.desc !== 'RESTCONF-CLIENT') throw new Error('auto_09 Gi0/7');
}});
assertRunLab('auto_10', (sim) => {{
  if (!sim.vlans[110] || sim.vlans[110].name !== 'YANG_MODELS') throw new Error('auto_10 VLAN 110');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 110 || gi7.desc !== 'YANG-LAB') throw new Error('auto_10 Gi0/7');
}});
assertRunLab('auto_11', (sim) => {{
  if (!sim.vlans[111] || sim.vlans[111].name !== 'ANSIBLE_CONTROL') throw new Error('auto_11 VLAN 111');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 111 || gi7.desc !== 'ANSIBLE-CTRL') throw new Error('auto_11 Gi0/7');
}});
assertRunLab('auto_12', (sim) => {{
  if (!sim.vlans[112] || sim.vlans[112].name !== 'TERRAFORM_IAC') throw new Error('auto_12 VLAN 112');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 112 || gi7.desc !== 'TF-PROVIDER') throw new Error('auto_12 Gi0/7');
}});
assertRunLab('auto_13', (sim) => {{
  if (!sim.vlans[113] || sim.vlans[113].name !== 'NSO_ORCHESTRATION') throw new Error('auto_13 VLAN 113');
  const gi7 = sim.interfaces['GigabitEthernet0/7'];
  if (!gi7.nonegotiate || gi7.accessVlan !== 113 || gi7.desc !== 'NSO-ORCH') throw new Error('auto_13 Gi0/7');
}});
"""
        res = subprocess.run([node_bin, "-e", js_script], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stderr + res.stdout)

        # 4. Safe fenced-code DOM renderer, copy-button click/fallback behavior & CSS verification
        styles_css = (ASSET_ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".code-block{", styles_css)
        self.assertIn("white-space:pre", styles_css)
        self.assertIn("direction:ltr", styles_css)
        self.assertIn("appendRichText(li, s, lessonObj.id)", app_js)

        dom_test_js = f"""
const fs = require('fs');
const vm = require('vm');
const ACADEMY = JSON.parse(fs.readFileSync({json.dumps(str(ASSET_ROOT / 'academy-data.json'))}, 'utf8'));
const appCode = fs.readFileSync({json.dumps(str(ASSET_ROOT / 'app.js'))}, 'utf8');

const sEl = appCode.indexOf('function el(');
const eEl = appCode.indexOf('/* ---------- هماهنگی با نشست');
const elCode = appCode.slice(sEl, eEl);

const sRich = appCode.indexOf('function appendPlainRichText(');
const eRich = appCode.indexOf('function fillBars(');
const richCode = appCode.slice(sRich, eRich);

function makeNode(tag) {{
  return {{
    tagName: tag.toUpperCase(),
    className: '',
    attrs: {{}},
    children: [],
    listeners: {{}},
    _text: '',
    setAttribute(k, v) {{ this.attrs[k] = String(v); }},
    addEventListener(ev, fn) {{ this.listeners[ev] = fn; }},
    appendChild(child) {{ this.children.push(child); return child; }},
    set textContent(v) {{ this._text = String(v); this.children = []; }},
    get textContent() {{
      if (this.children.length) return this.children.map(c => c.textContent).join('');
      return this._text;
    }}
  }};
}}
const fakeDocument = {{
  createElement(tag) {{ return makeNode(tag); }},
  createTextNode(txt) {{ return {{ nodeType: 3, textContent: String(txt) }}; }}
}};

let clipboardMode = 'ok';
let copiedTexts = [];
let selectedNodes = [];
let scheduledTimers = [];

const ctx = {{
  document: fakeDocument,
  window: {{
    getSelection() {{
      return {{
        removeAllRanges() {{}},
        addRange(r) {{ selectedNodes.push(r.node); }}
      }};
    }}
  }},
  glossRegex: /\\b(Python|Netmiko|Nornir|SSH|REST|JSON|YAML|XML|JWT|NETCONF)\\b/g,
  glossMap: new Map([
    ['python', {{ term: 'Python' }}],
    ['netmiko', {{ term: 'Netmiko' }}],
    ['nornir', {{ term: 'Nornir' }}],
    ['ssh', {{ term: 'SSH' }}],
    ['rest', {{ term: 'REST' }}],
    ['json', {{ term: 'JSON' }}],
    ['yaml', {{ term: 'YAML' }}],
    ['xml', {{ term: 'XML' }}],
    ['jwt', {{ term: 'JWT' }}],
    ['netconf', {{ term: 'NETCONF' }}]
  ]),
  showGlossaryPopover() {{}},
  hideGlossaryPopover() {{}},
  glossHideTimer: null,
  setTimeout(fn, ms) {{ scheduledTimers.push({{ fn, ms }}); return scheduledTimers.length; }},
  navigator: {{
    clipboard: {{
      writeText(txt) {{
        if (clipboardMode === 'ok') {{
          copiedTexts.push(txt);
          return Promise.resolve();
        }}
        return Promise.reject(new Error('NotAllowedError'));
      }}
    }}
  }}
}};
fakeDocument.createRange = () => ({{
  node: null,
  selectNodeContents(el) {{ this.node = el; }}
}});
vm.runInNewContext(elCode + '\\n' + richCode, ctx);

function findNodes(node, pred, acc = []) {{
  if (pred(node)) acc.push(node);
  for (const c of (node.children || [])) findNodes(c, pred, acc);
  return acc;
}}

const rendered = {{}};
for (const lid of ['auto_02', 'auto_03', 'auto_04', 'auto_05', 'auto_06', 'auto_07', 'auto_08']) {{
  const li = makeNode('li');
  ctx.appendRichText(li, ACADEMY.lessons[lid].lab.steps[4], lid);
  const codes = findNodes(li, n => n.tagName === 'CODE');
  const pres = findNodes(li, n => n.tagName === 'PRE');
  const copyBtns = findNodes(li, n => n.tagName === 'BUTTON' && n.className === 'code-copy-btn');
  if (codes.length !== 1 || pres.length !== 1 || copyBtns.length !== 1) {{
    throw new Error(lid + ' expected 1 pre/code/copyBtn');
  }}
  if (pres[0].attrs.dir !== 'ltr' || pres[0].className !== 'code-block') throw new Error(lid + ' pre attrs/class');
  if (findNodes(codes[0], n => n.tagName === 'BUTTON').length !== 0) throw new Error(lid + ' glossary injected inside code');
  rendered[lid] = codes[0].textContent;
  if (lid === 'auto_03') {{
    ctx._testCopyBtn = copyBtns[0];
    ctx._testCodeEl = codes[0];
  }}
}}

// Anti-XSS check: raw <script>/<img> inside text or fenced code never creates SCRIPT/IMG elements
const liXss = makeNode('li');
ctx.appendRichText(liXss, 'قبل <script>alert(1)</script>\\n```python\\nprint("<img src=x onerror=alert(1)>")\\n```', 'auto_02');
if (findNodes(liXss, n => n.tagName === 'SCRIPT' || n.tagName === 'IMG').length !== 0) {{
  throw new Error('XSS element created!');
}}

(async () => {{
  // 1) Successful clipboard write
  clipboardMode = 'ok';
  copiedTexts = [];
  ctx._testCopyBtn.listeners.click();
  await Promise.resolve();
  await Promise.resolve();
  if (copiedTexts[0] !== rendered['auto_03']) throw new Error('copyBtn did not copy exact codeText');
  if (ctx._testCopyBtn.textContent !== 'کپی شد ✓') throw new Error('copyBtn success label mismatch: ' + ctx._testCopyBtn.textContent);
  scheduledTimers.pop().fn();
  if (ctx._testCopyBtn.textContent !== 'کپی کد') throw new Error('copyBtn did not reset label');

  // 2) Rejected clipboard write -> selection fallback
  clipboardMode = 'reject';
  selectedNodes = [];
  ctx._testCopyBtn.listeners.click();
  await Promise.resolve();
  await Promise.resolve();
  if (selectedNodes[0] !== ctx._testCodeEl) throw new Error('fallback did not select code element');
  if (ctx._testCopyBtn.textContent !== 'انتخاب شد (Ctrl+C)') throw new Error('copyBtn selection fallback label mismatch: ' + ctx._testCopyBtn.textContent);
  scheduledTimers.pop().fn();

  // 3) Missing navigator.clipboard and missing getSelection -> explicit failure label
  const ctxNoClip = {{
    document: fakeDocument,
    window: {{}},
    glossRegex: null,
    glossMap: new Map(),
    setTimeout(fn, ms) {{ scheduledTimers.push({{ fn, ms }}); }},
    navigator: undefined
  }};
  vm.runInNewContext(elCode + '\\n' + richCode, ctxNoClip);
  const liNoClip = makeNode('li');
  ctxNoClip.appendRichText(liNoClip, '```python\\nx = 1\\n```', 'auto_02');
  const btnNoClip = findNodes(liNoClip, n => n.tagName === 'BUTTON' && n.className === 'code-copy-btn')[0];
  btnNoClip.listeners.click();
  if (btnNoClip.textContent !== 'کپی ناموفق (دستی انتخاب کنید)') {{
    throw new Error('missing clipboard+selection label mismatch: ' + btnNoClip.textContent);
  }}

  console.log(JSON.stringify(rendered));
}})().catch(err => {{ console.error(err); process.exit(1); }});
"""
        dom_res = subprocess.run([node_bin, "-e", dom_test_js], capture_output=True, text=True, check=False)
        self.assertEqual(dom_res.returncode, 0, dom_res.stderr + dom_res.stdout)
        rendered_payload = json.loads(dom_res.stdout)

        # Verify the exact text rendered inside DOM <pre><code> preserves indentation and executes cleanly in Python
        with tempfile.TemporaryDirectory() as tmpd:
            p2 = Path(tmpd) / "rendered_vlan_audit.py"
            p2.write_text(rendered_payload["auto_02"], encoding="utf-8")
            env = dict(os.environ, NETOPS_TOKEN="demo")
            r2 = subprocess.run([sys.executable, str(p2)], cwd=tmpd, env=env, capture_output=True, text=True, check=False)
            self.assertEqual(r2.returncode, 0, r2.stderr + r2.stdout)
            self.assertIn("MISSING: [99]", r2.stdout)

        ns_dom_a3: dict = {}
        exec(compile(rendered_payload["auto_03"], "rendered_safe_apply.py", "exec"), ns_dom_a3)
        c_dom_ok = MockConn("R1(config)#ntp server 10.255.0.1\nR1(config)#end", "ntp server 10.255.0.1")
        self.assertEqual(ns_dom_a3["apply_ntp_safely"](make_factory(c_dom_ok), {"host": "10.255.0.1"}, "10.255.0.1"), "save_no_error_seen")

        if shutil.which("bash") and shutil.which("git"):
            with tempfile.TemporaryDirectory() as tmpd:
                sh_env = dict(os.environ, TMPDIR=tmpd)
                sh_res = subprocess.run(["bash", "-e", "-c", rendered_payload["auto_04"]], cwd=tmpd, env=sh_env, capture_output=True, text=True, check=False)
                self.assertEqual(sh_res.returncode, 0, sh_res.stderr + sh_res.stdout)

        ns_dom_b5: dict = {}
        for lid in ("auto_05", "auto_06", "auto_07", "auto_08"):
            ns_dom_b5[lid] = {}
            exec(compile(rendered_payload[lid], f"rendered_{lid}.py", "exec"), ns_dom_b5[lid])
        self.assertTrue(ns_dom_b5["auto_05"]["inspect_payloads"]()["ok"])
        with self.assertRaises(ValueError):
            ns_dom_b5["auto_06"]["fetch_vlans_safely"]("http://10.255.0.1/vlans", "tok")
        self.assertEqual(ns_dom_b5["auto_07"]["verify_hs256_jwt"]("bad.token", b"k")["error"], "malformed_token")
        self.assertIn("R&amp;D", ns_dom_b5["auto_08"]["build_ncclient_config_payload"]("Gi0/7", "R&D"))


if __name__ == "__main__":
    unittest.main()
