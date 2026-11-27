import ast
import html
import importlib.util
import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_DIR = ROOT / "server" / "www" / "academy-assets" / "v5" / "blueprints"
AGENT3_LAB_DIR = ROOT / "academy-labs" / "agent3"
REVIEW_DIR = ROOT / "academy-labs" / "reviews"

AGENT3_ALLOWED_IDS = {
    # Core Specialist (6)
    "spec_ent", "spec_sec", "spec_sp", "spec_wl", "spec_collab", "spec_cyber",
    # Deep Specialist (12)
    "spec_ent_campus", "spec_ent_sd", "spec_sec_vpn", "spec_sec_ise",
    "spec_dc_nx", "spec_dc_aci", "spec_dc_stor", "spec_sp_xr", "spec_sp_sr",
    "spec_wl_survey", "spec_collab_gw", "spec_cyber_hunt",
    # Automation except auto_12 (19)
    "auto_01", "auto_02", "auto_03", "auto_04", "auto_05", "auto_06", "auto_07",
    "auto_08", "auto_09", "auto_10", "auto_11", "auto_13", "auto_14", "auto_15",
    "auto_16", "auto_17", "auto_18", "auto_19", "auto_20",
    # CCIE (7)
    "ccie_01", "ccie_sec", "ccie_dc", "ccie_sp", "ccie_wl", "ccie_collab", "ccie_auto",
    # CCDE (20)
    *[f"ccde_{i:02d}" for i in range(1, 21)],
}

FORBIDDEN_LEGACY_TYPOS = (
    "تلgern",
    "شوائع",
    "politicaها",
    "استخراجدرس",
    "چهخروجیی",
    "عمولاتی",
    "مرزهای camino",
    "فیبرpath",
    "سبین-لیف",
    "سه تاقا",
    "یک الشيء",
    "مبتنی بر یتیک",
    "n preservation",
    "inicialmente",
    "diferencia",
)

UNEXECUTED_MARKERS = (
    "اجرا نشده",
    "متصل نشده",
    "بدون اتصال",
    "تجهیز واقعی",
    "شبیه‌سازی",
    "Mock",
)


def discover_agent3_blueprints() -> list[tuple[str, Path]]:
    found = []
    for lab_file in sorted(AGENT3_LAB_DIR.glob("*_lab.py")):
        lesson_id = lab_file.name.removesuffix("_lab.py")
        bp_path = BLUEPRINT_DIR / f"{lesson_id}.json"
        if bp_path.exists():
            found.append((lesson_id, bp_path))
    return found


class Agent3ContentIntegrityTests(unittest.TestCase):
    def test_discovered_lessons_are_strictly_within_agent3_scope(self):
        discovered = discover_agent3_blueprints()
        discovered_ids = {lesson_id for lesson_id, _ in discovered}
        self.assertEqual(len(AGENT3_ALLOWED_IDS), 64)
        self.assertEqual(
            discovered_ids,
            AGENT3_ALLOWED_IDS,
            f"Missing: {sorted(AGENT3_ALLOWED_IDS - discovered_ids)} | Extra: {sorted(discovered_ids - AGENT3_ALLOWED_IDS)}",
        )
        self.assertNotIn("auto_12", discovered_ids, "auto_12 belongs to Agent 2")

    def test_integration_guide_lists_all_64_lessons(self):
        guide_path = ROOT / "AGENT3-INTEGRATION-GUIDE-fa.md"
        self.assertTrue(guide_path.exists(), "Missing AGENT3-INTEGRATION-GUIDE-fa.md")
        guide_text = guide_path.read_text(encoding="utf-8")
        for lesson_id in sorted(AGENT3_ALLOWED_IDS):
            self.assertIn(f"`{lesson_id}`", guide_text, f"{lesson_id} missing from AGENT3-INTEGRATION-GUIDE-fa.md")

    def test_technical_audit_regressions(self):
        """Regression assertions for technical & semantic audit fixes (Phase 2)."""
        audit_log = ROOT / "AGENT3-TECHNICAL-AUDIT-LOG-fa.md"
        self.assertTrue(audit_log.exists(), "Missing AGENT3-TECHNICAL-AUDIT-LOG-fa.md")
        audit_text = audit_log.read_text(encoding="utf-8")
        self.assertIn("author-agent-self-review-not-independent", audit_text)
        self.assertIn("بازبینی مستقل", audit_text)

        def load_student_text(lid: str) -> tuple[dict, str]:
            data = json.loads((BLUEPRINT_DIR / f"{lid}.json").read_text(encoding="utf-8"))
            txt = json.dumps(
                {
                    "sections": data["sections"],
                    "glossary": data["glossary"],
                    "quiz": data["interactiveQuiz"],
                    "lab": data["stages"]["lab"],
                },
                ensure_ascii=False,
            )
            return data, txt

        # 1. ccde_18 & ccde_05: synchronous replication RTT ceiling must be product-conditioned, not universal 5ms
        for lid in ("ccde_18", "ccde_05"):
            data, txt = load_student_text(lid)
            self.assertNotIn("سقف ۵ms", txt, f"{lid} still has unconditional 5ms ceiling")
            self.assertNotIn("سقف ~۵ms", txt, f"{lid} still has unconditional ~5ms ceiling")
            self.assertNotIn("(~500km)", txt, f"{lid} still has contradictory ~500km SVG claim")
            self.assertIn("vSAN", txt, f"{lid} must cite product-specific vSAN <=5ms threshold")
            self.assertIn("MetroCluster", txt, f"{lid} must cite product-specific MetroCluster/vMSC <=10ms threshold")
            self.assertEqual(data["meta"]["semanticReview"]["reviewer"], "author-agent-self-review-not-independent")

        # 2. spec_dc_aci: Multi-Site data-plane vs NDO/APIC (500ms) & ND cluster (50ms / legacy MSO 150ms)
        _, aci_txt = load_student_text("spec_dc_aci")
        self.assertNotIn("تا ~۱۵۰ میلی‌ثانیه بین سایت‌ها", aci_txt)
        self.assertIn("۵۰۰ms", aci_txt)

        # 3. ccde_07: AWS Direct Connect 99.9% (2x2) vs 99.99% (4+ connections across 2+ locations) & Azure 99.95%
        _, c07_txt = load_student_text("ccde_07")
        self.assertNotIn("SLA بالای ۹۹٫۹۹٪", c07_txt)
        self.assertIn("۴ اتصال", c07_txt)
        self.assertIn("۹۹٫۹۵٪", c07_txt)

        # 4. spec_sp_sr & ccde_19: TI-LFA conditioned on 2-connected topology & hardware MSD
        for lid in ("spec_sp_sr", "ccde_19"):
            _, sr_txt = load_student_text(lid)
            self.assertNotIn("در هر توپولوژی دلخواه", sr_txt)
            self.assertIn("۲-همبند", sr_txt)
            self.assertIn("MSD", sr_txt)

        # 5. ccde_14: distinguish HTTPS/TLS (1.2 + 1.3) from TLS 1.3-only
        _, c14_txt = load_student_text("ccde_14")
        self.assertNotIn("بیش از ۹۵٪ ترافیک وب و بدافزارها رمزنگاری TLS 1.3 دارند", c14_txt)
        self.assertIn("TLS 1.2", c14_txt)

        # 6. ccde_08 & ccde_15 & ccde_18: PCI scope reduction must be QSA-conditioned, not guaranteed 95%
        for lid in ("ccde_08", "ccde_15", "ccde_18"):
            _, pci_txt = load_student_text(lid)
            self.assertIn("QSA", pci_txt)

        # 7. ccde_11: Microburst detection not sole method
        _, c11_txt = load_student_text("ccde_11")
        self.assertNotIn("تنها راه شکار واقعی Microburst", c11_txt)

        # 8. spec_sec_ise: Kerberos 5-min skew explicitly marked as AD default
        _, ise_txt = load_student_text("spec_sec_ise")
        self.assertIn("MaxClockSkew", ise_txt)

        # 9. auto_02, auto_08, spec_collab_gw: no unconditional 'همیشه باید' in quiz explanations
        for lid in ("auto_02", "auto_08", "spec_collab_gw"):
            _, t = load_student_text(lid)
            self.assertNotIn("همیشه باید", t)

        # 10. Phase 3 technical & semantic regressions across additional lessons
        # ccde_10: N+1=4 over N=3 is ~33.3% extra cost (NOT 25%), plus Common-Mode independence caveat
        _, c10_txt = load_student_text("ccde_10")
        self.assertNotIn("تنها با ۲۵٪ هزینه اضافه", c10_txt)
        self.assertIn("۳۳٫۳٪", c10_txt)
        self.assertIn("Common-Mode", c10_txt)

        # spec_dc_aci: Multi-Pod/Multi-Site Spine IPN/ISN exception explicitly noted
        self.assertIn("IPN/ISN", aci_txt)

        # spec_wl_survey: Section 7 harmonized with Q1 (no unconditional 'مطلقاً فقط')
        _, wls_txt = load_student_text("spec_wl_survey")
        self.assertNotIn("مطلقاً فقط از کانال‌های", wls_txt)
        self.assertIn("ETSI", wls_txt)

        # ccie_01: EIGRP External AD=170 distinguished from Internal AD=90 & illustrative thresholds noted
        _, ei_txt = load_student_text("ccie_01")
        self.assertIn("EIGRP External", ei_txt)
        self.assertIn("AD=90", ei_txt)

        # ccie_dc: official 7-domain weights & no guaranteed <3min / unverified 90%/95%
        _, dc_txt = load_student_text("ccie_dc")
        self.assertNotIn("حل تضمینی مشکلات اتصال بین EPGها در کمتر از ۳ دقیقه", dc_txt)
        self.assertNotIn("بیش از ۹۰٪ مشکلات", dc_txt)
        self.assertIn("Sec/Svc (10%)", dc_txt)

        # ccie_wl: no unverified 90% stat & 2026 WLCOR naming
        _, cwl_txt = load_student_text("ccie_wl")
        self.assertNotIn("۹۰٪ مشکلات «پخش نشدن SSID»", cwl_txt)
        self.assertIn("350-101 WLCOR", cwl_txt)

        # ccde_03, ccde_05, ccde_16: remove unverified/categorical stats & unconditional TI-LFA in lab
        _, c03_txt = load_student_text("ccde_03")
        self.assertNotIn("دسترسی تضمینی به ۱۰۰٪ اینترنت جهانی", c03_txt)
        self.assertNotIn("gives 100% <50ms TI-LFA", c03_txt)
        _, c05_txt = load_student_text("ccde_05")
        self.assertNotIn("بیش از ۸۰٪ سازمان‌ها", c05_txt)
        self.assertNotIn("بیش از ۸۰٪ کسب‌وکارها", c05_txt)
        _, c16_txt = load_student_text("ccde_16")
        self.assertNotIn("در ۹۵٪ پروژه‌های واقعی", c16_txt)

        # auto_09: NMDA RFC 8343 ?content=nonconfig uses ietf-interfaces:interfaces (not deprecated interfaces-state)
        _, a09_txt = load_student_text("auto_09")
        self.assertIn("RFC 8343", a09_txt)
        self.assertNotIn("ietf-interfaces:interfaces-state", (AGENT3_LAB_DIR / "auto_09_lab.py").read_text(encoding="utf-8"))

        # 11. Upgraded lab scripts must exercise both negative and positive assertions
        for lid, expected_tokens in (
            ("ccde_18", ["rejected_sync_l2_proposal", "approved_hld_validation", "vmware_vsan_stretched"]),
            ("ccde_05", ["vmware_vsan_stretched", "netapp_metrocluster_or_vmsc"]),
            ("spec_sp_sr", ["ti_lfa_blocked_by_low_msd", "ti_lfa_singly_homed_cut_edge"]),
            ("ccde_19", ["rejected_flat_forklift_proposal", "approved_hld_validation"]),
            ("auto_05", ["nan_constant", "pos_infinity", "neg_infinity", "strict_parser_rejected"]),
            ("auto_07", ["alg=none attack rejected", "Expired JWT rejected"]),
            ("ccie_01", ["Illustrative thresholds only"]),
        ):
            proc = subprocess.run(
                [sys.executable, str(AGENT3_LAB_DIR / f"{lid}_lab.py")],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for tok in expected_tokens:
                self.assertIn(tok, proc.stdout, f"{lid}_lab.py missing expected output token {tok!r}")

    def test_auto_05_strict_rfc8259_and_auto_07_jwt_unit_checks(self):
        """Directly test auto_05_lab strict RFC 8259 parser (NaN/Infinity/-Infinity/duplicates) & auto_07_lab JWT/SAN."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        auto05 = load_module(AGENT3_LAB_DIR / "auto_05_lab.py", "auto_05_lab_testmod")
        self.assertEqual(auto05.parse_json_strict('{"ok": true, "n": 42}'), {"ok": True, "n": 42})
        # Non-object top-level RFC 8259 JSON values must parse cleanly without crashing
        self.assertEqual(auto05.parse_json_strict("[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(auto05.parse_json_strict('"ok"'), "ok")
        self.assertIs(auto05.parse_json_strict("true"), True)
        self.assertIsNone(auto05.parse_json_strict("null"))
        self.assertEqual(auto05.parse_json_strict("42"), 42)
        # Non-RFC 8259 constants accepted by plain json.loads MUST be rejected by parse_json_strict
        for bad_const in ('{"x": NaN}', '{"x": Infinity}', '{"x": -Infinity}'):
            with self.subTest(bad_const=bad_const):
                with self.assertRaises(ValueError):
                    auto05.parse_json_strict(bad_const)
                res = auto05.check_invalid_json_rejected(bad_const)
                self.assertTrue(res["rejected"], f"{bad_const} must be rejected")

        # Duplicate keys: RFC 8259 Sec 4 (SHOULD be unique -> Python default last-wins vs strict rejection)
        with self.assertRaises(ValueError):
            auto05.parse_json_strict('{"k": 1, "k": 2}', reject_duplicate_keys=True)
        dup = auto05.demonstrate_duplicate_key_behavior('{"k": 1, "k": 2}')
        self.assertEqual(dup["python_default_last_wins"], {"k": 2})
        self.assertTrue(dup["strict_parser_rejected"])

        # auto_07: alg="none", expired token, and leading-dot SAN edge case must all be rejected
        auto07 = load_module(AGENT3_LAB_DIR / "auto_07_lab.py", "auto_07_lab_testmod")
        secret = b"unit-test-secret"
        now_ts = 1764201600
        good_tok = auto07.build_hs256_jwt({"sub": "u", "exp": now_ts + 3600}, secret)
        self.assertTrue(auto07.verify_hs256_jwt(good_tok, secret, now_ts=now_ts)["valid"])

        parts = good_tok.split(".")
        none_hdr = auto07.b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
        self.assertFalse(auto07.verify_hs256_jwt(f"{none_hdr}.{parts[1]}.", secret, now_ts=now_ts)["valid"])

        exp_tok = auto07.build_hs256_jwt({"sub": "u", "exp": now_ts - 10}, secret)
        exp_res = auto07.verify_hs256_jwt(exp_tok, secret, now_ts=now_ts)
        self.assertFalse(exp_res["valid"])
        self.assertEqual(exp_res["reason"], "token_expired")

        self.assertTrue(auto07.verify_san_match("api.netops.example", ["*.netops.example"]))
        self.assertFalse(auto07.verify_san_match("a.b.netops.example", ["*.netops.example"]))
        self.assertFalse(auto07.verify_san_match(".netops.example", ["*.netops.example"]))

    def test_lab_execution_classification_accuracy(self):
        """Ensure real-CLI (auto_04) and loopback-HTTP labs are classified accurately, never mislabeled as all-Mock."""
        audit_text = (ROOT / "AGENT3-TECHNICAL-AUDIT-LOG-fa.md").read_text(encoding="utf-8")
        guide_text = (ROOT / "AGENT3-INTEGRATION-GUIDE-fa.md").read_text(encoding="utf-8")

        # Verify actual AST capabilities match reported classification
        def imported_modules(path: Path) -> set[str]:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(n.name.split(".")[0] for n in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            return mods

        self.assertIn("subprocess", imported_modules(AGENT3_LAB_DIR / "auto_04_lab.py"))
        for lid in ("auto_06", "auto_09", "auto_14"):
            self.assertIn("http", imported_modules(AGENT3_LAB_DIR / f"{lid}_lab.py"))

        # Every single one of the 64 lab filenames must appear explicitly in the audit execution matrix
        for lid in sorted(AGENT3_ALLOWED_IDS):
            self.assertIn(f"`{lid}_lab.py`", audit_text, f"{lid}_lab.py missing from execution classification table")

        # Neither report may falsely claim all 64 labs are purely Local Mock
        self.assertIn("auto_04_lab.py", guide_text)
        self.assertIn("اجرای باینری خارجی واقعی", guide_text)
        self.assertNotIn("اما این اسکریپت‌ها **شبیه‌ساز / مدل‌ساز محلی (Local Mock)** هستند", guide_text)

    def test_blueprints_schema_svg_quiz_lab_and_review_integrity(self):
        discovered = discover_agent3_blueprints()
        for lesson_id, bp_path in discovered:
            with self.subTest(lesson_id=lesson_id):
                raw_text = bp_path.read_text(encoding="utf-8")
                data = json.loads(raw_text)
                student_facing_text = json.dumps(
                    {
                        "title": data.get("title"),
                        "sections": data.get("sections"),
                        "glossary": data.get("glossary"),
                        "stages": data.get("stages"),
                        "interactiveQuiz": data.get("interactiveQuiz"),
                    },
                    ensure_ascii=False,
                )
                for bad in FORBIDDEN_LEGACY_TYPOS:
                    self.assertNotIn(
                        bad,
                        student_facing_text,
                        f"Legacy typo {bad!r} leaked into student-facing content of {lesson_id}",
                    )
                self.assertEqual(data.get("schema"), "fam-app-blueprint-v1")
                self.assertEqual(data.get("lessonId"), lesson_id)
                self.assertEqual(data.get("objectiveId"), lesson_id)
                self.assertEqual(data.get("kind"), "lesson")
                self.assertEqual(data.get("evidence"), "Designed — Not Run")
                self.assertIn("بازبینی مستقل انجام نشده", data.get("reviewStatus", ""))

                sections = data.get("sections", [])
                self.assertGreaterEqual(len(sections), 14)
                sec_ids = set()
                svg_count = 0
                for sec in sections:
                    self.assertTrue(sec.get("id"))
                    self.assertNotIn(sec["id"], sec_ids)
                    sec_ids.add(sec["id"])
                    self.assertTrue(sec.get("title", "").strip())
                    sec_html = sec.get("html", "")
                    self.assertTrue(sec_html.strip())
                    for match in re.findall(r"<svg\b[^>]*>.*?</svg>", sec_html, flags=re.DOTALL):
                        svg_count += 1
                        root = ET.fromstring(match)
                        self.assertTrue(root.attrib.get("viewBox"), f"SVG missing viewBox in {lesson_id}")
                self.assertGreaterEqual(svg_count, 1, f"{lesson_id} must contain at least one valid inline SVG")

                glossary = data.get("glossary", [])
                self.assertGreaterEqual(len(glossary), 15)
                for item in glossary:
                    self.assertTrue(item.get("term", "").strip())
                    self.assertTrue(item.get("fa", "").strip())
                    self.assertTrue(item.get("simple", "").strip())

                quiz = data.get("interactiveQuiz", [])
                self.assertEqual(len(quiz), 12)
                for q_idx, q in enumerate(quiz):
                    self.assertTrue(q.get("title", "").strip(), f"{lesson_id} Q{q_idx} empty title")
                    opts = q.get("options", [])
                    self.assertEqual(len(opts), 4, f"{lesson_id} Q{q_idx} must have 4 options")
                    self.assertEqual(len(set(opts)), 4, f"{lesson_id} Q{q_idx} has duplicate options")
                    self.assertIn(q.get("correctIndex"), (0, 1, 2, 3))
                    self.assertTrue(q.get("explanationHtml", "").strip())

                lab = data.get("stages", {}).get("lab", {})
                lab_html = lab.get("html", "")
                self.assertTrue(any(m in lab_html for m in UNEXECUTED_MARKERS))
                self.assertTrue(any(m in lab.get("executionStatus", "") for m in UNEXECUTED_MARKERS))

                lab_script = AGENT3_LAB_DIR / f"{lesson_id}_lab.py"
                self.assertTrue(lab_script.exists(), f"Missing lab script {lab_script}")
                # Enforce exact byte-for-byte embedding INCLUDING trailing newline
                escaped_src = html.escape(lab_script.read_text(encoding="utf-8"))
                self.assertIn(
                    escaped_src,
                    lab_html,
                    f"{lesson_id} lab.html does not embed exact byte-for-byte escaped source (including trailing newline) of {lab_script.name}",
                )

                review_path = REVIEW_DIR / f"{lesson_id}-review-fa.md"
                self.assertTrue(review_path.exists(), f"Missing review log {review_path}")
                review_text = review_path.read_text(encoding="utf-8")
                self.assertIn("بازبینی مستقل", review_text)

                meta = data.get("meta", {})
                self.assertGreaterEqual(len(meta.get("sources", [])), 1)
                self.assertGreaterEqual(len(meta.get("limitations", [])), 1)
                self.assertEqual(
                    meta.get("semanticReview", {}).get("reviewer"),
                    "author-agent-self-review-not-independent",
                )

    def test_phase4_ccde_18_ccde_19_dynamic_labs_and_regressions(self):
        """Phase 4 regressions: ccde_18/ccde_19 dynamic pass/fail lab diagnostics, GDPR Chapter V nuance, auto_04 hash vs encryption."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        def student_text(lid: str) -> str:
            d = json.loads((BLUEPRINT_DIR / f"{lid}.json").read_text(encoding="utf-8"))
            return json.dumps(
                {k: d.get(k) for k in ("title", "sections", "glossary", "stages", "interactiveQuiz")},
                ensure_ascii=False,
            )

        # 1. ccde_18_lab.py direct unit checks (no hardcoded contradictory notes!)
        c18_mod = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_lab_testmod")
        base_ok = {
            "dc_distance_km": 5000,
            "storage_replication": "asynchronous",
            "dci_l2_stretched": False,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "cross_border_transfer_basis": "eu_eea_residency_policy",
            "encryption_in_transit": True,
        }
        res_ok = c18_mod.validate_pars_global_hld(base_ok, "vmware_vmsc_netapp_metrocluster")
        self.assertTrue(res_ok["all_architectural_checks_passed"])
        self.assertIn("Chapter V", res_ok["domain_validations"][3]["compliance_scope_note"])
        self.assertIn("technical controls only", res_ok["domain_validations"][3]["compliance_scope_note"])

        # Metro distance (150 km) where sync IS feasible: note MUST say "within", NEVER "exceeds"!
        metro_sync_ok = c18_mod.validate_pars_global_hld(
            {**base_ok, "dc_distance_km": 150, "storage_replication": "synchronous"},
            "vmware_vsan_stretched",
        )
        self.assertTrue(metro_sync_ok["all_architectural_checks_passed"])
        dci_metro = metro_sync_ok["domain_validations"][0]
        self.assertTrue(dci_metro["sync_feasible_for_profile"])
        self.assertTrue(dci_metro["replication_ok"])
        self.assertTrue(dci_metro["l2_stretch_policy_ok"])
        self.assertIn("within", dci_metro["note"])
        self.assertNotIn("exceeds", dci_metro["note"])

        # Metro distance with L2 stretched: replication_ok is True, l2_stretch_policy_ok is False
        metro_l2_bad = c18_mod.validate_pars_global_hld(
            {**base_ok, "dc_distance_km": 150, "storage_replication": "synchronous", "dci_l2_stretched": True},
            "vmware_vsan_stretched",
        )
        self.assertFalse(metro_l2_bad["all_architectural_checks_passed"])
        dci_metro_bad = metro_l2_bad["domain_validations"][0]
        self.assertTrue(dci_metro_bad["replication_ok"])
        self.assertFalse(dci_metro_bad["l2_stretch_policy_ok"])
        self.assertNotIn("exceeds", dci_metro_bad["note"])
        self.assertIn("policy", dci_metro_bad["note"])

        # Missing encryption or transfer basis must fail compliance technical controls
        bad_comp = c18_mod.validate_pars_global_hld({**base_ok, "encryption_in_transit": False})
        self.assertFalse(bad_comp["all_architectural_checks_passed"])
        self.assertFalse(bad_comp["domain_validations"][3]["pass"])

        # 2. ccde_19_lab.py direct unit checks (dynamic pass/fail notes on all 5 pillars)
        c19_mod = load_module(AGENT3_LAB_DIR / "ccde_19_lab.py", "ccde_19_lab_testmod")
        c19_fail = c19_mod.validate_aria_telecom_hld({
            "max_routers_per_igp_domain": 2050,
            "inter_domain_stitching": "single_flat_igp",
            "flex_algo_slices": 1,
            "tilfa_enabled": True,
            "rings_two_connected_within_msd": False,
            "service_plane": "legacy_vpls_plus_bgp_in_core",
            "migration_mechanism": "overnight_forklift_cutover",
            "rpki_and_flowspec": False,
            "ixp_cdn_offload_pct": 15,
        })
        self.assertFalse(c19_fail["all_pillars_validated"])
        for p in c19_fail["pillars"]:
            self.assertFalse(p["pass"])
            self.assertTrue(p["note"].startswith("REJECTED:"), f"Failed pillar missing REJECTED note: {p}")
            self.assertNotIn("Zero-Downtime", p["pillar"])

        # 3. Blueprint semantic regressions (ccde_18, ccde_19, ccde_15, auto_04)
        c18_txt = student_text("ccde_18")
        self.assertIn("EDPB", c18_txt)
        self.assertIn("فصل ۵ GDPR", c18_txt)
        self.assertNotIn("صفر قطعی", c18_txt)
        self.assertNotIn("Zero-Downtime", c18_txt)
        self.assertNotIn("نقض سنگین جریمه GDPR", c18_txt)

        c19_txt = student_text("ccde_19")
        self.assertNotIn("Zero-Downtime", c19_txt)
        self.assertNotIn("مهاجرت SRMS رینگ-به-رینگ بدون قطعی", c19_txt)

        a04_txt = student_text("auto_04")
        self.assertNotIn("تاریخچه رمزنگاری‌شده", a04_txt)
        self.assertIn("هش رمزنگاری", a04_txt)

        c15_txt = student_text("ccde_15")
        self.assertNotIn("ممنوعیت خروج داده‌های شهروندان", c15_txt)
        self.assertIn("EDPB", c15_txt)
        self.assertIn("فصل ۵", c15_txt)

    def test_all_agent3_lab_scripts_execute_cleanly(self):
        scripts = sorted(AGENT3_LAB_DIR.glob("*_lab.py"))
        self.assertEqual(len(scripts), 64)
        for script in scripts:
            with self.subTest(script=script.name):
                proc = subprocess.run(
                    [sys.executable, str(script)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(
                    proc.returncode,
                    0,
                    f"{script.name} failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
                )
                self.assertTrue(proc.stdout.strip(), f"{script.name} produced empty stdout")


if __name__ == "__main__":
    unittest.main()
