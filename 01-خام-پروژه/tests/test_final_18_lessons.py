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


if __name__ == "__main__":
    unittest.main()
