"""Integrity tests for the FAM Cisco Academy comprehensive curriculum."""
from __future__ import annotations

from html.parser import HTMLParser
import json
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
        self.assertIn("فرضی", arch_s5)

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

        # 3. Simulator persistence of switchport nonegotiate across repeated mode access
        m_mode = re.search(r"low === 'switchport mode access'[\s\S]*?(?=\} else if)", app_js)
        self.assertIsNotNone(m_mode)
        self.assertNotIn("nonegotiate = false", m_mode.group(0))
        self.assertIn("no switchport nonegotiate", app_js)

        node_bin = shutil.which("node")
        if node_bin:
            js_script = f"""
const fs = require('fs');
const vm = require('vm');
const ACADEMY = JSON.parse(fs.readFileSync({json.dumps(str(ASSET_ROOT / 'academy-data.json'))}, 'utf8'));
const appCode = fs.readFileSync({json.dumps(str(ASSET_ROOT / 'app.js'))}, 'utf8');
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
const r = run(['enable','configure terminal','interface Gi0/2','switchport mode access','switchport nonegotiate','end','show running-config','configure terminal','interface Gi0/2','switchport mode access','end','show running-config','configure terminal','interface Gi0/2','no switchport nonegotiate','end','show interfaces Gi0/2 switchport']);
if (r.out[6] !== r.out[11]) throw new Error('repeated mode access altered running-config');
if (!r.out[11].includes('switchport nonegotiate')) throw new Error('nonegotiate lost after repeated mode access');
if (r.sim.interfaces['GigabitEthernet0/2'].nonegotiate !== false) throw new Error('no switchport nonegotiate failed');
const neg = run(['enable','configure terminal','interface Gi0/0','switchport nonegotiate','no switchport nonegotiate']);
if (!neg.out[3].includes('Command rejected') || !neg.out[4].includes('Command rejected')) throw new Error('routed interface accepted nonegotiate');
"""
            res = subprocess.run([node_bin, "-e", js_script], capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, res.stderr + res.stdout)


if __name__ == "__main__":
    unittest.main()
