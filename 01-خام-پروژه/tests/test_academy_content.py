"""Integrity tests for the FAM Cisco Academy comprehensive curriculum."""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
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

        # 2b. Checks for f4 Batch 1..4 (first 20 lessons in f4) + Round-6..11 regressions
        f4_b1_b2_b3_b4 = data["curriculumGroups"][4]["lessons"][:20]
        self.assertEqual(
            f4_b1_b2_b3_b4,
            [
                "spec_ent", "spec_ent_campus", "spec_ent_sd", "spec_sec", "spec_sec_vpn",
                "spec_sec_ise", "spec_dc_nx", "s11", "spec_dc_aci", "spec_dc_stor",
                "spec_sp", "spec_sp_xr", "spec_sp_sr", "spec_wl", "spec_wl_survey",
                "spec_collab", "spec_collab_gw", "auto_01", "auto_02", "auto_03",
            ],
        )
        for lid in f4_b1_b2_b3_b4:
            lesson = data["lessons"][lid]
            self.assertEqual(len(lesson.get("exercises", [])), 3, lid)
            self.assertEqual(len(lesson.get("quiz", [])), 3, lid)
            self.assertEqual(len(lesson["lab"]["steps"]), 5, lid)
            s = json.dumps(lesson, ensure_ascii=False)
            for bad in ("192.168", "1921.6800", "فوق‌العاده", "بی‌نظیر", "قانون طلایی", "۹۰٪", "۹۹٪", "۱۰۰٪", "۸۰٪", "جادویی"):
                self.assertNotIn(bad, s, f"{lid} contains {bad}")
        b3_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f4_b1_b2_b3_b4[10:15]:
            for q in data["lessons"][lid]["quiz"]:
                b3_dist[q["ans"]] += 1
        self.assertEqual(b3_dist, {0: 4, 1: 4, 2: 4, 3: 3})
        b4_dist = {0: 0, 1: 0, 2: 0, 3: 0}
        for lid in f4_b1_b2_b3_b4[15:20]:
            for q in data["lessons"][lid]["quiz"]:
                b4_dist[q["ans"]] += 1
        self.assertEqual(b4_dist, {0: 4, 1: 4, 2: 4, 3: 3})

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

        # Extract CLI commands directly from lab.steps[2] of each f4 Batch 1..4 lesson
        extracted_labs = {}
        for lid in f4_b1_b2_b3_b4:
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
"""
        res = subprocess.run([node_bin, "-e", js_script], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stderr + res.stdout)


if __name__ == "__main__":
    unittest.main()
