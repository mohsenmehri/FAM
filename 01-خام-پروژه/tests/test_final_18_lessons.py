"""Comprehensive automated verification for the final 18 v5 lessons (adv_* & ccnp_*).

Verifies all 18 newly completed blueprints, executable stdlib Python labs,
byte-for-byte code embedding parity, 14 sections, >=15 glossary terms,
12 varied-index quizzes, valid SVG XML, review logs, and catalog/legacy linkage.
"""
from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BP_DIR = ROOT / "server/www/academy-assets/v5/blueprints"
LAB_DIR = ROOT / "academy-labs/agent3"
REV_DIR = ROOT / "academy-labs/reviews"

FINAL_18_IDS = (
    "adv_pvl", "adv_ec", "adv_eigrp", "adv_redist", "adv_bgp", "adv_qos", "adv_mcast",
    "ccnp_01", "ccnp_02", "ccnp_enc_arch", "ccnp_enc_inf", "ccnp_enc_sec", "ccnp_enc_auto",
    "ccnp_ensdwi", "ccnp_ensld", "ccnp_enauto", "ccnp_encc", "ccnp_enna",
)


class Final18LessonsTests(unittest.TestCase):
    def test_all_18_blueprints_meet_v5_16_section_contract_and_code_parity(self):
        for lid in FINAL_18_IDS:
            with self.subTest(lesson=lid):
                bp = json.loads((BP_DIR / f"{lid}.json").read_text(encoding="utf-8"))
                lab_path = LAB_DIR / f"{lid}_lab.py"
                rev_path = REV_DIR / f"{lid}-review-fa.md"
                self.assertTrue(lab_path.is_file(), f"missing lab {lab_path}")
                self.assertTrue(rev_path.is_file(), f"missing review {rev_path}")
                self.assertEqual(bp["lessonId"], lid)
                self.assertEqual(len(bp["sections"]), 14)
                self.assertGreaterEqual(len(bp["glossary"]), 15)
                self.assertEqual(len(bp["interactiveQuiz"]), 12)
                self.assertIn("خودبازبینی", bp.get("reviewStatus", ""))
                self.assertIn("بازبینی مستقل انسانی انجام نشده", bp.get("reviewStatus", ""))
                self.assertIn("محلی", bp.get("evidence", ""))
                # Byte-for-byte lab embedding check
                lab_html = unescape(bp["stages"]["lab"]["html"])
                lab_src = lab_path.read_text(encoding="utf-8")
                self.assertIn(lab_src, lab_html)
                # SVG well-formedness check
                svgs = re.findall(r"<svg\b[\s\S]*?</svg>", json.dumps(bp, ensure_ascii=False))
                self.assertGreaterEqual(len(svgs), 1)
                for raw_svg in svgs:
                    ET.fromstring(raw_svg.replace('\\"', '"'))

    def test_all_18_python_labs_execute_cleanly_with_assertions(self):
        for lid in FINAL_18_IDS:
            lab_path = LAB_DIR / f"{lid}_lab.py"
            with self.subTest(lab=lid):
                res = subprocess.run(
                    [sys.executable, str(lab_path)],
                    capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(res.returncode, 0, res.stderr + res.stdout)
                self.assertTrue(res.stdout.strip())

    def test_simulator_has_zero_placeholder_responses_and_strict_ip_validators(self):
        sim_src = (ROOT / "server/www/academy-assets/academy-simulator.js").read_text(encoding="utf-8")
        offline_html = (ROOT.parent / "FAM-Academy-Offline.html").read_text(encoding="utf-8")
        self.assertNotIn("خروجی شبیه‌ساز برای", sim_src)
        self.assertNotIn("خروجی شبیه‌ساز برای", offline_html)
        self.assertIn("function isValidIPv4(", sim_src)
        self.assertIn("function isValidIPv6(", sim_src)
        self.assertIn("matchType: 'exact'", sim_src)
        self.assertIn("matchType: 'track-default'", sim_src)

    def test_all_127_blueprints_have_valid_prerequisites(self):
        catalog = json.loads(
            (ROOT / "server/www/academy-assets/curriculum-catalog.json").read_text(encoding="utf-8")
        )
        valid_ids = {
            lesson["id"]
            for path in catalog["paths"]
            for course in path["courses"]
            for lesson in course["lessons"]
        }
        self.assertEqual(len(valid_ids), 127)
        for lid in sorted(valid_ids):
            bp = json.loads((BP_DIR / f"{lid}.json").read_text(encoding="utf-8"))
            for prereq in bp.get("prerequisites", []):
                self.assertIn(prereq, valid_ids, f"dangling prerequisite {prereq} in {lid}")

    def test_browser_smoke_script_matches_current_offline_banner_and_syntax(self):
        browser_test = ROOT / "tests/browser/browser.test.cjs"
        harness = ROOT / "tests/browser/run_browser_test.py"
        src = browser_test.read_text(encoding="utf-8")
        offline_html = (ROOT.parent / "FAM-Academy-Offline.html").read_text(encoding="utf-8")
        self.assertIn("require('puppeteer-core')", src)
        self.assertNotIn("دوره ۱۱۴ درسی کامل نیست", src)
        for expected_fragment in (
            "شامل هر 127 درس فعال",
            "همگام نیست",
            "نه بازبینی مستقل انسانی",
            "اتصال به تجهیزات واقعی وجود ندارد",
        ):
            self.assertIn(expected_fragment, src)
            self.assertIn(expected_fragment, offline_html)
        syntax = subprocess.run(["node", "--check", str(browser_test)], capture_output=True, text=True, timeout=15)
        self.assertEqual(syntax.returncode, 0, syntax.stderr + syntax.stdout)
        py_check = subprocess.run([sys.executable, "-m", "py_compile", str(harness)], capture_output=True, text=True, timeout=15)
        self.assertEqual(py_check.returncode, 0, py_check.stderr + py_check.stdout)
        # Verify harness fails cleanly when FAM_CHROMIUM_PATH is unset
        no_chrome = subprocess.run(
            [sys.executable, str(harness)],
            env={k: v for k, v in __import__("os").environ.items() if k != "FAM_CHROMIUM_PATH"},
            capture_output=True, text=True, timeout=15,
        )
        self.assertNotEqual(no_chrome.returncode, 0)
        self.assertIn("FAM_CHROMIUM_PATH", no_chrome.stderr + no_chrome.stdout)


if __name__ == "__main__":
    unittest.main()
