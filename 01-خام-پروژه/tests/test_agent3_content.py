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
            "target_rpo_minutes": 15,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }
        res_ok = c18_mod.validate_pars_global_hld(base_ok, "netapp_vmsc_snapmirror_active_sync")
        self.assertTrue(res_ok["all_architectural_checks_passed"])
        self.assertIn("unverified HLD design assumptions", res_ok["domain_validations"][3]["assumption_disclaimer"])
        self.assertIn("not legal opinions", res_ok["domain_validations"][3]["assumption_disclaimer"])

        # Metro distance (150 km) where sync IS feasible: note MUST say "within", NEVER "exceeds"!
        metro_sync_ok = c18_mod.validate_pars_global_hld(
            {**base_ok, "dc_distance_km": 150, "assumed_equipment_and_detour_overhead_ms": 1.0, "storage_replication": "synchronous", "target_rpo_minutes": 0},
            "vmware_vsan_stretched",
        )
        self.assertTrue(metro_sync_ok["all_architectural_checks_passed"])
        dci_metro = metro_sync_ok["domain_validations"][0]
        self.assertTrue(dci_metro["sync_feasible_for_profile"])
        self.assertTrue(dci_metro["replication_ok"])
        self.assertTrue(dci_metro["l2_stretch_policy_ok"])
        self.assertIn("within", dci_metro["note"])
        self.assertNotIn("violates", dci_metro["note"])
        self.assertNotIn("exceeds", dci_metro["note"])

        # Metro distance with L2 stretched: replication_ok is True, l2_stretch_policy_ok is False
        metro_l2_bad = c18_mod.validate_pars_global_hld(
            {**base_ok, "dc_distance_km": 150, "assumed_equipment_and_detour_overhead_ms": 1.0, "storage_replication": "synchronous", "target_rpo_minutes": 0, "dci_l2_stretched": True},
            "vmware_vsan_stretched",
        )
        self.assertFalse(metro_l2_bad["all_architectural_checks_passed"])
        dci_metro_bad = metro_l2_bad["domain_validations"][0]
        self.assertTrue(dci_metro_bad["replication_ok"])
        self.assertFalse(dci_metro_bad["l2_stretch_policy_ok"])
        self.assertNotIn("exceeds", dci_metro_bad["note"])
        self.assertIn("policy", dci_metro_bad["note"])

        # Missing encryption assumption must fail compliance technical controls
        bad_comp = c18_mod.validate_pars_global_hld({**base_ok, "encryption_in_transit_assumed": False})
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

    def test_phase5_remaining_tracks_labs_and_regressions(self):
        """Phase 5 unit & negative-case tests across Specialist, CCIE, CCDE, and Automation remaining lessons."""
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

        # --- Category 1: Specialist ---
        # spec_ent_campus: identical C9200/C9300 pairs MUST be rejected for SVL
        svl = load_module(AGENT3_LAB_DIR / "spec_ent_campus_lab.py", "spec_ent_campus_testmod")
        c9200_pair = svl.validate_svl_pair(
            {"model": "C9200-48P", "ios_xe": "17.9.4a", "license": "network-advantage"},
            {"model": "C9200-48P", "ios_xe": "17.9.4a", "license": "network-advantage"},
        )
        self.assertEqual(len(c9200_pair), 1)
        self.assertIn("C9200/C9300", c9200_pair[0])
        self.assertNotIn("ارتقای بدون قطعی (Graceful Shutdown یک گره)", student_text("spec_ent_campus"))

        # spec_dc_nx: dual-homed vPC upgrade must explicitly qualify Orphan Ports
        dc_nx_txt = student_text("spec_dc_nx")
        self.assertNotIn("(بدون قطعی سرورهای Dual-Homed)", dc_nx_txt)
        self.assertIn("Orphan Port", dc_nx_txt)

        # spec_sec_vpn: reverse-only asymmetry & negative counters must NOT report healthy
        vpn = load_module(AGENT3_LAB_DIR / "spec_sec_vpn_lab.py", "spec_sec_vpn_testmod")
        self.assertEqual(vpn.diagnose_ipsec_counters(0, 180), "ONE_WAY_OUTBOUND_MISSING_CHECK_LOCAL_ROUTE_OR_CRYPTO_ACL")
        with self.assertRaises(ValueError):
            vpn.diagnose_ipsec_counters(-1, 10)

        # spec_dc_stor: multi-initiator detection works across arbitrary HBA OUIs (not hardcoded 20:00:00:11)
        stor = load_module(AGENT3_LAB_DIR / "spec_dc_stor_lab.py", "spec_dc_stor_testmod")
        init_a = {"vsan": 100, "wwpn": "21:00:00:24:ff:01:00:01"}
        init_b = {"vsan": 100, "wwpn": "10:00:00:90:fa:02:00:02"}
        tgt = {"vsan": 100, "wwpn": "50:00:09:70:00:01:00:01"}
        res_multi = stor.evaluate_fc_access(
            init_a,
            tgt,
            [{"name": "Z_BAD", "vsan": 100, "members": [init_a["wwpn"], init_b["wwpn"], tgt["wwpn"]]}],
            known_initiator_wwpns={init_a["wwpn"], init_b["wwpn"]},
        )
        self.assertFalse(res_multi["single_initiator_best_practice"])
        self.assertEqual(res_multi["initiators_in_zone"], 2)

        # spec_sp_xr: strict CIDR validation rejects non-CIDR /21 with host bits and overly specific /28
        xr = load_module(AGENT3_LAB_DIR / "spec_sp_xr_lab.py", "spec_sp_xr_testmod")
        self.assertEqual(xr.eval_rpl_policy("RPL_CUST_IN", "198.51.100.0", 21)["action"], "DROP")
        self.assertEqual(xr.eval_rpl_policy("RPL_CUST_IN", "198.51.100.0", 28)["action"], "DROP")
        self.assertEqual(xr.eval_rpl_policy("RPL_CUST_IN", "198.51.100.128", 25)["action"], "PASS")

        # spec_cyber_hunt: unsorted beacon logs detected; <4 samples never false-positive
        hunt = load_module(AGENT3_LAB_DIR / "spec_cyber_hunt_lab.py", "spec_cyber_hunt_testmod")
        self.assertTrue(hunt.detect_beaconing([240, 0, 180, 60, 120])["beaconing_suspected"])
        self.assertFalse(hunt.detect_beaconing([0, 60])["beaconing_suspected"])
        self.assertFalse(hunt.detect_beaconing([10, 10, 10, 10])["beaconing_suspected"])

        # --- Category 2: CCIE ---
        # ccie_collab: detects 172.16.0.0/12 & 100.64.0.0/10 private SDP leaks; rejects unknown codecs
        collab = load_module(AGENT3_LAB_DIR / "ccie_collab_lab.py", "ccie_collab_testmod")
        self.assertIn("One-Way", collab.diagnose_sip_trace(["INVITE", "200 OK", "ACK"], "172.16.50.12")["symptom"])
        self.assertIn("One-Way", collab.diagnose_sip_trace(["INVITE", "200 OK", "ACK"], "100.64.1.5")["symptom"])
        with self.assertRaises(ValueError):
            collab.evaluate_cucm_call(["PT_WAN"], "PT_WAN", "UNKNOWN_CODEC", 100)
        self.assertIn("بی‌ارتباط با قانون حریم خصوصی GDPR اروپا", student_text("ccie_collab"))

        # ccie_sec: distinguishes 45s NTP ops warning from 300s RFC 4120 Kerberos hard failure & TLS decrypt gate
        csec = load_module(AGENT3_LAB_DIR / "ccie_sec_lab.py", "ccie_sec_testmod")
        pf_45 = csec.audit_ntp_dns_preflight([{"name": "N1", "clock_skew_sec": 45, "dns_forward_reverse_ok": True}])
        self.assertTrue(pf_45["preflight_passed"])
        self.assertEqual(len(pf_45["warnings"]), 1)
        pf_350 = csec.audit_ntp_dns_preflight([{"name": "N1", "clock_skew_sec": 350, "dns_forward_reverse_ok": True}])
        self.assertFalse(pf_350["preflight_passed"])
        blind = csec.ftd_packet_tracer(
            {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC", "tls_decrypted": False, "contains_exploit_sig": True},
            {"10.10.20.15": 10},
        )
        self.assertEqual(blind["result"], "ALLOW_UNINSPECTED_TLS")

        # --- Category 3: CCDE ---
        # ccde_01: rejects invalid SLA/weights/domains and removes absolute "بدون قطعی" wording
        c01 = load_module(AGENT3_LAB_DIR / "ccde_01_lab.py", "ccde_01_testmod")
        with self.assertRaises(ValueError):
            c01.sla_downtime_budget(101.0)
        with self.assertRaises(ValueError):
            c01.blast_radius(1000, 0)
        with self.assertRaises(ValueError):
            c01.weighted_tradeoff({"a": 0.5, "b": 0.2}, {"opt": {"a": 5, "b": 5}})
        self.assertNotIn("ارتقای بدون قطعی", student_text("ccde_01"))
        self.assertNotIn("برنامه Rollback بدون قطعی", student_text("ccde_01"))

        # ccde_20: removes absolute "مهاجرت بدون قطعی" / "zero-downtime" wording
        c20_txt = student_text("ccde_20")
        self.assertNotIn("مهاجرت بدون قطعی", c20_txt)
        self.assertNotIn("zero-downtime", c20_txt)

        # --- Category 4: Automation ---
        # auto_16: rejects Python bool True as VLAN ID & tab YAML
        a16 = load_module(AGENT3_LAB_DIR / "auto_16_lab.py", "auto_16_testmod")
        self.assertEqual(a16.run_pipeline({"raw_yaml": "vlan: true\n", "vlan_id": True})["status"], "blocked_at_test")
        self.assertEqual(a16.run_pipeline({"raw_yaml": "vlan:\t30\n", "vlan_id": 30})["status"], "blocked_at_lint")

        # auto_17: catches USER 0, final-USER escalation back to root/0, and ENV TOKEN=
        a17 = load_module(AGENT3_LAB_DIR / "auto_17_lab.py", "auto_17_testmod")
        self.assertTrue(len(a17.audit_dockerfile(["FROM python:3.11-slim", "USER 0"])) >= 1)
        self.assertTrue(len(a17.audit_dockerfile(["FROM python:3.11-slim", "USER appuser", "USER root"])) >= 1)
        self.assertTrue(len(a17.audit_dockerfile(["FROM python:3.11-slim", "USER appuser", "ENV API_TOKEN=xyz"])) >= 1)
        self.assertEqual(a17.audit_dockerfile(["FROM python:3.11-slim", "USER appuser"]), [])

    def test_phase6_ccde_18_remediation_and_remaining_labs(self):
        """Phase 6 negative & boundary tests: ccde_18 Agent 2 findings + ccde_04, ccde_09, ccde_12, ccde_13, auto_15."""
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

        # --- Part A: ccde_18 complete remediation ---
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_phase6_testmod")
        valid_design = {
            "dc_distance_km": 5000,
            "storage_replication": "asynchronous",
            "target_rpo_minutes": 15,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }

        # 1. Negative, zero, bool, NaN, inf distances MUST raise ValueError
        for bad_dist in (-500, 0, True, float("nan"), float("inf")):
            with self.subTest(bad_dist=bad_dist):
                with self.assertRaises(ValueError):
                    c18.validate_pars_global_hld({**valid_design, "dc_distance_km": bad_dist})

        # Unknown sync product profile MUST raise ValueError
        with self.assertRaises(ValueError):
            c18.validate_pars_global_hld(valid_design, "unknown_storage_product")

        # 2. Invalid storage_replication mode at metro distance (150 km) MUST fail & NEVER say "is supported"
        bad_mode = c18.validate_pars_global_hld(
            {**valid_design, "dc_distance_km": 150, "assumed_equipment_and_detour_overhead_ms": 1.0, "storage_replication": "not-a-real-mode"},
            "vmware_vsan_stretched",
        )
        self.assertFalse(bad_mode["all_architectural_checks_passed"])
        dci_bad = bad_mode["domain_validations"][0]
        self.assertFalse(dci_bad["storage_replication_valid"])
        self.assertFalse(dci_bad["replication_ok"])
        self.assertFalse(dci_bad["pass"])
        self.assertIn("unsupported storage_replication mode", dci_bad["note"])
        self.assertNotIn("is supported", dci_bad["note"])

        # 3. GSLB & RPO explicitly checked
        no_gslb = c18.validate_pars_global_hld({**valid_design, "gslb_enabled": False})
        self.assertFalse(no_gslb["all_architectural_checks_passed"])
        self.assertFalse(no_gslb["domain_validations"][0]["gslb_ok"])
        self.assertIn("REJECTED (GSLB)", no_gslb["domain_validations"][0]["note"])

        async_rpo0 = c18.validate_pars_global_hld({**valid_design, "target_rpo_minutes": 0})
        self.assertFalse(async_rpo0["all_architectural_checks_passed"])
        self.assertFalse(async_rpo0["domain_validations"][0]["rpo_ok"])
        self.assertIn("REJECTED (RPO)", async_rpo0["domain_validations"][0]["note"])

        # 4. Residency vs Chapter V transfer separation
        # 4a) Corporate residency enforced + no transfer outside EEA + safeguard=None => PASS
        res_local_only = c18.validate_pars_global_hld(valid_design)
        self.assertTrue(res_local_only["all_architectural_checks_passed"])
        # 4b) Contradiction: residency enforced=True AND transferred_outside_eea=True => FAIL
        res_contradiction = c18.validate_pars_global_hld({
            **valid_design,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": True,
            "chapter_v_transfer_safeguard": "adequacy_decision",
        })
        self.assertFalse(res_contradiction["all_architectural_checks_passed"])
        self.assertFalse(res_contradiction["domain_validations"][3]["residency_consistency_ok"])
        # 4c) Transfer outside EEA without safeguard => FAIL
        res_missing_safeguard = c18.validate_pars_global_hld({
            **valid_design,
            "eu_residency_policy_enforced": False,
            "eu_personal_data_transferred_outside_eea": True,
            "chapter_v_transfer_safeguard": None,
        })
        self.assertFalse(res_missing_safeguard["all_architectural_checks_passed"])
        self.assertFalse(res_missing_safeguard["domain_validations"][3]["chapter_v_ok"])
        # 4d) Transfer outside EEA WITH valid Chapter V safeguard (SCCs + TIA) => PASS
        res_valid_scc = c18.validate_pars_global_hld({
            **valid_design,
            "eu_residency_policy_enforced": False,
            "eu_personal_data_transferred_outside_eea": True,
            "chapter_v_transfer_safeguard": "sccs_plus_tia_supplementary_measures",
        })
        self.assertTrue(res_valid_scc["all_architectural_checks_passed"])

        # 5. Latency assumption alignment & ccde_18.json text regressions
        dci_5000 = res_local_only["domain_validations"][0]
        self.assertEqual(dci_5000["propagation_only_min_rtt_ms"], 50.0)
        self.assertEqual(dci_5000["routed_propagation_only_rtt_ms"], 70.0)
        self.assertEqual(dci_5000["assumed_total_end_to_end_rtt_ms"], 105.0)
        self.assertIn("not measured carrier RTT", dci_5000["latency_assumption_note"])

        c18_txt = student_text("ccde_18")
        self.assertNotIn("جلوی حرکت افقی باج‌افزار را می‌گیرد", c18_txt)
        self.assertNotIn("بدون هیچ تغییر در هسته!", c18_txt)
        self.assertNotIn("امکان ارتباط بی‌وقفه میان شعبی که هنوز روی MPLS قدیمی هستند", c18_txt)
        self.assertIn("کنترل ضدحلقه", c18_txt)

        # --- Part B: Remaining audited labs (ccde_04, ccde_09, ccde_12, ccde_13, auto_15) ---
        c04 = load_module(AGENT3_LAB_DIR / "ccde_04_lab.py", "ccde_04_phase6_testmod")
        with self.assertRaises(ValueError):
            c04.clos_3stage_max_servers(3, 3.0)
        with self.assertRaises(ValueError):
            c04.clos_3stage_max_servers(64, 0.0)
        with self.assertRaises(ValueError):
            c04.clos_5stage_max_servers(64, 65, 1.0)
        self.assertFalse(
            c04.audit_ai_ml_fabric({"name": "X", "oversubscription": 1.0, "ecn_enabled": True, "pfc_enabled": True, "load_balancing": "garbage"})["ai_fabric_ready"]
        )

        c09 = load_module(AGENT3_LAB_DIR / "ccde_09_lab.py", "ccde_09_phase6_testmod")
        with self.assertRaises(ValueError):
            c09.simulate_flap_dampening(-1)
        self.assertEqual(c09.simulate_flap_dampening(0)["action"], "NO_FAULT_STEADY_STATE")

        c12 = load_module(AGENT3_LAB_DIR / "ccde_12_lab.py", "ccde_12_phase6_testmod")
        with self.assertRaises(ValueError):
            c12.ibgp_rr_sessions(2, route_reflectors=3)
        with self.assertRaises(ValueError):
            c12.ibgp_full_mesh_sessions(0)

        c13 = load_module(AGENT3_LAB_DIR / "ccde_13_lab.py", "ccde_13_phase6_testmod")
        with self.assertRaises(ValueError):
            c13.simulate_post_failure_te({"A": {"capacity_gbps": 100}}, 10, 10, "NONEXISTENT")
        with self.assertRaises(ValueError):
            c13.simulate_post_failure_te({"A": {"capacity_gbps": 100}}, 10, 10, "A")
        self.assertNotIn("Drop فوری ۱۰۰٪ نشست‌ها", student_text("ccde_13"))

        a15 = load_module(AGENT3_LAB_DIR / "auto_15_lab.py", "auto_15_phase6_testmod")
        self.assertEqual(a15.validate_sot_prefixes(["10.0.0.0/24", "2001:db8:1::/48"]), [])
        self.assertEqual(len(a15.validate_sot_prefixes(["10.0.0.0/24", "2001:db8::/32", "2001:db8:1::/48"])), 1)

    def test_phase7_strict_boolean_typing_and_remaining_labs(self):
        """Phase 7 strict bool validation ("False"/"True"/0/1/None rejected) across ccde_18 and 6 remaining labs."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        bad_bools = ("False", "True", 0, 1, None)

        # 1. ccde_18_lab: EVERY boolean field MUST reject "False", "True", 0, 1, None + expose rpo_scope_note
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_phase7_testmod")
        valid_c18 = {
            "dc_distance_km": 5000,
            "storage_replication": "asynchronous",
            "target_rpo_minutes": 15,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }
        bool_keys = (
            "dci_l2_stretched",
            "gslb_enabled",
            "micro_sgt_enabled",
            "eu_residency_policy_enforced",
            "eu_personal_data_transferred_outside_eea",
            "encryption_in_transit_assumed",
        )
        for key in bool_keys:
            for bad_val in bad_bools:
                with self.subTest(ccde_18_bool_key=key, bad_val=bad_val):
                    with self.assertRaises(ValueError):
                        c18.validate_pars_global_hld({**valid_c18, key: bad_val})
            with self.subTest(ccde_18_missing_key=key):
                missing_copy = {k: v for k, v in valid_c18.items() if k != key}
                with self.assertRaises(ValueError):
                    c18.validate_pars_global_hld(missing_copy)

        res_c18 = c18.validate_pars_global_hld(valid_c18)
        self.assertTrue(res_c18["all_architectural_checks_passed"])
        self.assertIn("does NOT prove real achieved RPO", res_c18["domain_validations"][0]["rpo_scope_note"])

        # 2. spec_sec_lab: reject truthy string "False" on authenticated & decrypt_enabled
        ssec = load_module(AGENT3_LAB_DIR / "spec_sec_lab.py", "spec_sec_phase7_testmod")
        for bad_val in bad_bools:
            with self.assertRaises(ValueError):
                ssec.evaluate_8021x_port("multi-domain", "closed", [{"mac": "aa", "domain": "DATA", "authenticated": bad_val}])
            with self.assertRaises(ValueError):
                ssec.evaluate_ftd_tls_and_ips(ssec.TlsFlow("a.example", "web", False, True), decrypt_enabled=bad_val)

        # 3. spec_ent_sd_lab: reject non-bool sudi_valid/tloc_ext_enabled & invalid PnP IP/port
        ssd = load_module(AGENT3_LAB_DIR / "spec_ent_sd_lab.py", "spec_ent_sd_phase7_testmod")
        for bad_val in bad_bools:
            with self.assertRaises(ValueError):
                ssd.verify_sdwan_ztp("C8300-BR001", sudi_valid=bad_val, allowed_serials={"C8300-BR001"})
            with self.assertRaises(ValueError):
                ssd.tloc_available_transports(["mpls"], ["dia"], tloc_ext_enabled=bad_val)
        with self.assertRaises(ValueError):
            ssd.parse_pnp_option43("5A1D;K4;I999.1.1.1;J443")
        with self.assertRaises(ValueError):
            ssd.parse_pnp_option43("5A1D;K4;I10.10.10.5;J99999")

        # 4. ccie_sec_lab: reject non-bool tls_decrypted / dns_forward_reverse_ok
        csec = load_module(AGENT3_LAB_DIR / "ccie_sec_lab.py", "ccie_sec_phase7_testmod")
        for bad_val in bad_bools:
            with self.assertRaises(ValueError):
                csec.ftd_packet_tracer(
                    {"src_ip": "10.10.20.15", "dst_ip": "10.20.50.10", "dst_port": 443, "dst_zone": "DC", "tls_decrypted": bad_val},
                    {"10.10.20.15": 10},
                )
            with self.assertRaises(ValueError):
                csec.audit_ntp_dns_preflight([{"name": "N1", "clock_skew_sec": 0, "dns_forward_reverse_ok": bad_val}])

        # 5. ccde_02_lab: reject non-bool flags, users<=0, empty/mixed subnets
        c02 = load_module(AGENT3_LAB_DIR / "ccde_02_lab.py", "ccde_02_phase7_testmod")
        for bad_val in bad_bools:
            with self.assertRaises(ValueError):
                c02.classify_branch_profile(12, revenue_critical=bad_val)
            with self.assertRaises(ValueError):
                c02.recommend_campus_access(bad_val, False, 150)
        with self.assertRaises(ValueError):
            c02.classify_branch_profile(0, False)
        with self.assertRaises(ValueError):
            c02.verify_block_summarization([])
        with self.assertRaises(ValueError):
            c02.verify_block_summarization(["10.0.0.0/24", "2001:db8::/48"])

        # 6. ccde_17_lab: reject negative and all-zero costs (prevents ZeroDivisionError)
        c17 = load_module(AGENT3_LAB_DIR / "ccde_17_lab.py", "ccde_17_phase7_testmod")
        with self.assertRaises(ValueError):
            c17.compute_5yr_tco("ZeroCost", 0, 0, 0, 0)
        with self.assertRaises(ValueError):
            c17.compute_5yr_tco("NegCost", -100, 10, 10, 10)

        # 7. auto_20_lab: reject human_approved="False"/"True"/0/1/None & invalid z_score/confidence
        a20 = load_module(AGENT3_LAB_DIR / "auto_20_lab.py", "auto_20_phase7_testmod")
        for bad_val in bad_bools:
            with self.assertRaises(ValueError):
                a20.remediation_decision("failover_regional_hub", 125, 0.96, human_approved=bad_val)
        with self.assertRaises(ValueError):
            a20.z_score(68.0, [])
        with self.assertRaises(ValueError):
            a20.z_score(68.0, [22.0, 22.0, 22.0])
        with self.assertRaises(ValueError):
            a20.remediation_decision("shift_single_branch_sdwan_path", 1, 1.5, False)

    def test_phase8a_ccde18_dynamic_vrf_and_specialist_core_labs(self):
        """Phase 8A: ccde_18 dynamic macro_vrfs + empty/container bool rejections + 5 Specialist Core labs."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. ccde_18: dynamic macro_vrfs message + "", [], {} bool rejections
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_phase8a_testmod")
        base_c18 = {
            "dc_distance_km": 5000,
            "storage_replication": "asynchronous",
            "target_rpo_minutes": 15,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }
        for vrf_count in (3, 5, 6):
            res = c18.validate_pars_global_hld({**base_c18, "macro_vrfs": vrf_count})
            self.assertTrue(res["all_architectural_checks_passed"])
            note = res["domain_validations"][3]["note"]
            self.assertIn(f"{vrf_count} Macro VRFs", note)
            self.assertNotIn("4 Macro VRFs", note)

        extra_bad_bools = ("", [], {})
        for key in (
            "dci_l2_stretched",
            "gslb_enabled",
            "micro_sgt_enabled",
            "eu_residency_policy_enforced",
            "eu_personal_data_transferred_outside_eea",
            "encryption_in_transit_assumed",
        ):
            for bad_val in extra_bad_bools:
                with self.assertRaises(ValueError):
                    c18.validate_pars_global_hld({**base_c18, key: bad_val})

        # 2. spec_ent: hex NET, strict hello_padding bool, non-bool VPN/SGT
        sent = load_module(AGENT3_LAB_DIR / "spec_ent_lab.py", "spec_ent_phase8a_testmod")
        with self.assertRaises(ValueError):
            sent.parse_isis_net("49.0001.ZZZZ.0000.0001.00")
        with self.assertRaises(ValueError):
            sent.IsisInterface("R1", "49.0001.0102.5500.0001.00", "L2", 1500, "point-to-point", hello_padding="False")
        with self.assertRaises(ValueError):
            sent.check_sda_sdwan_handoff("VN_A", True, 15, "sxp")

        # 3. spec_sp: non-PHP swap returns VPN label (not transport label!) + label bounds
        ssp = load_module(AGENT3_LAB_DIR / "spec_sp_lab.py", "spec_sp_phase8a_testmod")
        non_php = ssp.simulate_mpls_l3vpn_forwarding(24, 30, 18001, 1500, 1508)
        self.assertTrue(non_php["delivered"])
        self.assertEqual(non_php["final_vpn_label"], 18001)
        with self.assertRaises(ValueError):
            ssp.simulate_mpls_l3vpn_forwarding(24, 3, 2_000_000, 1500, 1508)

        # 4. spec_wl: strict bool on C9800 flags + negative cable loss rejected
        swl = load_module(AGENT3_LAB_DIR / "spec_wl_lab.py", "spec_wl_phase8a_testmod")
        for bad in ("False", "True", 0, 1, None):
            with self.assertRaises(ValueError):
                swl.resolve_c9800_ap_behavior(bad, True, False, False, True)
        with self.assertRaises(ValueError):
            swl.compute_rf_link(14.0, -1.0, 4.0, -64.0, -90.0, 20)

        # 5. spec_collab: strict dot1q bool + packetization_ms=0 prevented
        scol = load_module(AGENT3_LAB_DIR / "spec_collab_lab.py", "spec_collab_phase8a_testmod")
        with self.assertRaises(ValueError):
            scol.voip_bandwidth_per_direction("G.711", dot1q="False")
        with self.assertRaises(ValueError):
            scol.voip_bandwidth_per_direction("G.711", packetization_ms=0)
        with self.assertRaises(ValueError):
            scol.evaluate_cucm_dial_plan("", ["PT_A"], [], [])

        # 6. spec_cyber: threshold<=0, bool ts, empty fqdn rejected
        scyb = load_module(AGENT3_LAB_DIR / "spec_cyber_lab.py", "spec_cyber_phase8a_testmod")
        with self.assertRaises(ValueError):
            scyb.detect_ssh_bruteforce([], threshold=0)
        with self.assertRaises(ValueError):
            scyb.detect_ssh_bruteforce([{"ts": True, "src_ip": "198.51.100.1", "service": "ssh", "outcome": "failure"}])
        with self.assertRaises(ValueError):
            scyb.score_dns_tunneling("")

    def test_phase8b_ccie_and_remaining_specialist_labs(self):
        """Phase 8B: strict bool & boundary checks completing 100% of CCIE and Specialist tracks."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        bad_bools = ("False", "True", 0, 1, None)

        # 1. ccie_sp: strict bools & prefix_sid_index
        csp = load_module(AGENT3_LAB_DIR / "ccie_sp_lab.py", "ccie_sp_phase8b_testmod")
        ok_pe1 = {"igp_lo0_reachable": True, "prefix_sid_index": 1, "rt_export": ["65000:100"], "xr_ebgp_rpl_attached": True}
        ok_pe2 = {"igp_lo0_reachable": True, "prefix_sid_index": 2, "rt_import": ["65000:100"], "xr_ebgp_rpl_attached": True}
        for bad in bad_bools:
            with self.assertRaises(ValueError):
                csp.debug_mpls_l3vpn_bottom_up(ok_pe1, {**ok_pe2, "xr_ebgp_rpl_attached": bad})
        with self.assertRaises(ValueError):
            csp.debug_mpls_l3vpn_bottom_up({**ok_pe1, "prefix_sid_index": True}, ok_pe2)

        # 2. ccie_auto: dry_run strict bool + multi-service fastmap_clean
        cauto = load_module(AGENT3_LAB_DIR / "ccie_auto_lab.py", "ccie_auto_phase8b_testmod")
        nso = cauto.MockNSOEngine()
        for bad in bad_bools:
            with self.assertRaises(ValueError):
                nso.apply_l3vpn_service("S1", "VRF1", "65000:1", dry_run=bad)
        nso.apply_l3vpn_service("S1", "VRF1", "65000:1", dry_run=False)
        nso.apply_l3vpn_service("S2", "VRF2", "65000:2", dry_run=False)
        del_s1 = nso.delete_l3vpn_service("S1")
        self.assertTrue(del_s1["deleted"])
        self.assertTrue(del_s1["fastmap_clean"])
        self.assertIn("VRF2", nso.device_cdb["PE1"]["vrfs"])

        # 3. spec_collab_gw: strict bools & empty dialed_number
        cgw = load_module(AGENT3_LAB_DIR / "spec_collab_gw_lab.py", "spec_collab_gw_phase8b_testmod")
        for bad in bad_bools:
            with self.assertRaises(ValueError):
                cgw.evaluate_branch_phone_state(bad, True)
            with self.assertRaises(ValueError):
                cgw.match_outbound_dial_peer("911", primary_trunk_up=bad)
        with self.assertRaises(ValueError):
            cgw.match_outbound_dial_peer("")

        # 4. spec_sec_ise: strict bools + leading-whitespace TACACS+ deny normalization
        ise = load_module(AGENT3_LAB_DIR / "spec_sec_ise_lab.py", "spec_sec_ise_phase8b_testmod")
        self.assertFalse(ise.tacacs_authorize_command("net-admin", "   reload"))
        for bad in bad_bools:
            with self.assertRaises(ValueError):
                ise.evaluate_posture_and_pxgrid("u@corp", "10.0.0.1", av_updated=bad, os_patched=True)

        # 5. spec_sp_sr: unknown mode, short hybrid path, invalid MSD rejected
        sr = load_module(AGENT3_LAB_DIR / "spec_sp_sr_lab.py", "spec_sp_sr_phase8b_testmod")
        with self.assertRaises(ValueError):
            sr.build_sr_te_stack(["PE1", "P1", "P3", "PE2"], mode="invalid_mode")
        with self.assertRaises(ValueError):
            sr.build_sr_te_stack(["PE1", "PE2"], mode="hybrid")
        with self.assertRaises(ValueError):
            sr.compute_ti_lfa_backup(("P1", "P2"), "PE2", ("P1", "P3"), hardware_msd=True)
        with self.assertRaises(ValueError):
            sr.compute_ti_lfa_backup(("P1", "P2"), "PE2", ("P1", "P3"), hardware_msd=0)

    def test_phase8c1_automation_core_labs(self):
        """Phase 8C-1: auto_01 log-injection guard, auto_03 strict bool, auto_06 400/409, auto_08 RFC 6242, auto_10 YANG."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. auto_01: username containing 'from' does NOT spoof IP; malformed line raises ValueError
        a01 = load_module(AGENT3_LAB_DIR / "auto_01_lab.py", "auto_01_phase8c1_testmod")
        tricky_log = "Nov 27 02:10:01 h sshd[1]: Failed password for invalid user from evil from 198.51.100.99 port 2222 ssh2\n"
        self.assertEqual(a01.parse_failed_ssh_counts(tricky_log), [("198.51.100.99", 1)])
        with self.assertRaises(ValueError):
            a01.parse_failed_ssh_counts("Nov 27 sshd: Failed password for root without_from_clause\n")

        # 2. auto_03: strict bools & max_workers
        a03 = load_module(AGENT3_LAB_DIR / "auto_03_lab.py", "auto_03_phase8c1_testmod")
        for bad in ("False", "True", 0, 1, None):
            with self.assertRaises(ValueError):
                a03.run_nornir_style_pilot([{"host": "192.0.2.1", "role": "pilot"}], "pilot", ["cmd"], dry_run=bad)
        with self.assertRaises(ValueError):
            a03.run_nornir_style_pilot([], "pilot", [], max_workers=0)

        # 3. auto_06: real loopback HTTP server returns 400 on bad JSON & 409 on duplicate POST
        a06 = load_module(AGENT3_LAB_DIR / "auto_06_lab.py", "auto_06_phase8c1_testmod")
        rest = a06.run_local_rest_lab()
        self.assertEqual(rest["bad_post_status"], 400)
        self.assertEqual(rest["duplicate_post_status"], 409)
        self.assertTrue(rest["put_idempotent_same_result"])

        # 4. auto_08: multi-chunk RFC 6242 + ValueError/RuntimeError instead of assert
        a08 = load_module(AGENT3_LAB_DIR / "auto_08_lab.py", "auto_08_phase8c1_testmod")
        xml = "<rpc><msg>]]>]]> multi-chunk test</msg></rpc>"
        self.assertEqual(a08.parse_netconf_1_1_chunked(a08.frame_netconf_1_1_chunked(xml, chunk_size=10)), xml)
        with self.assertRaises(ValueError):
            a08.parse_netconf_1_1_chunked("\n#999\ntruncated\n##\n")
        ds = a08.NetconfDatastoreMock()
        with self.assertRaises(RuntimeError):
            ds.edit_candidate("sess-unlocked", ["permit any"])

        # 5. auto_10: non-dict payload & non-bool YANG dhcp leaf
        a10 = load_module(AGENT3_LAB_DIR / "auto_10_lab.py", "auto_10_phase8c1_testmod")
        self.assertTrue(len(a10.validate_vlan_payload("not-a-dict")) == 1)
        errs = a10.validate_vlan_payload({"vlans": [{"vlan-id": 10, "name": "CORP", "dhcp": "False"}]})
        self.assertTrue(any("boolean" in e for e in errs))

    def test_phase8c2_remaining_automation_labs(self):
        """Phase 8C-2: complete 100% of Automation track (auto_11, auto_13, auto_14, auto_18, auto_19)."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. auto_11: strict bool check_mode + handler_actually_executed
        a11 = load_module(AGENT3_LAB_DIR / "auto_11_lab.py", "auto_11_phase8c2_testmod")
        for bad in ("False", "True", 0, 1, None):
            with self.assertRaises(ValueError):
                a11.run_ios_config_task("core_routers", ["interface Loopback0"], ["desc X"], check_mode=bad)

        # 2. auto_13: empty VRF/RD & unknown device rejected
        a13 = load_module(AGENT3_LAB_DIR / "auto_13_lab.py", "auto_13_phase8c2_testmod")
        nso = a13.NsoOrchestratorMock()
        with self.assertRaises(ValueError):
            nso.commit_service("", "65000:1")
        with self.assertRaises(ValueError):
            nso.check_sync("NON_EXISTENT_DEV")

        # 3. auto_14: page_size<=0 rejected & server 429 state is per-instance (repeatable!)
        a14 = load_module(AGENT3_LAB_DIR / "auto_14_lab.py", "auto_14_phase8c2_testmod")
        with self.assertRaises(ValueError):
            a14.chatops_execute("", "noc-read", "show_inventory")
        # Run loopback server twice to prove 429 retry is repeatable per instance
        import threading as _th
        for _ in range(2):
            srv = a14.MockCatalystServer(("127.0.0.1", 0), a14.MockCatalystCenter)
            t = _th.Thread(target=srv.serve_forever, daemon=True)
            t.start()
            try:
                sdk = a14.MiniSdkClient(f"http://127.0.0.1:{srv.server_address[1]}")
                with self.assertRaises(ValueError):
                    sdk.get_all_devices(page_size=0)
                devs = sdk.get_all_devices(page_size=2)
                self.assertEqual(len(devs), 5)
                self.assertEqual(sdk.retries_handled, 1)
            finally:
                srv.shutdown()
                srv.server_close()

        # 4. auto_18: non-dict & empty router/prefix rejected
        a18 = load_module(AGENT3_LAB_DIR / "auto_18_lab.py", "auto_18_phase8c2_testmod")
        with self.assertRaises(ValueError):
            a18.dq_filter_down_bgp_peers("not-a-dict")
        with self.assertRaises(ValueError):
            a18.batfish_style_trace({}, "", "10.0.0.0/24")

        # 5. auto_19: inverted hysteresis thresholds & out-of-range cpu_pct rejected
        a19 = load_module(AGENT3_LAB_DIR / "auto_19_lab.py", "auto_19_phase8c2_testmod")
        with self.assertRaises(ValueError):
            a19.evaluate_alert_hysteresis([80, 90], high_thresh=80.0, clear_thresh=85.0)
        with self.assertRaises(ValueError):
            a19.encode_compact_metric(1000, 1, 100, 105.0)

    def test_phase8d_remaining_ccde_labs(self):
        """Phase 8D: complete 100% of CCDE track (ccde_08, ccde_11, ccde_14) -> 0 lessons left at reviewed.1."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. ccde_08: vrfs<=0, bool, empty SGT rejected
        c08 = load_module(AGENT3_LAB_DIR / "ccde_08_lab.py", "ccde_08_phase8d_testmod")
        with self.assertRaises(ValueError):
            c08.evaluate_segmentation_plan(0, 10, 4)
        with self.assertRaises(ValueError):
            c08.evaluate_segmentation_plan(True, 10, 4)
        with self.assertRaises(ValueError):
            c08.check_sgt_matrix("", "PCI_POS", {})

        # 2. ccde_11: cap<=0 / capacity<=0 / missing dimension rejected (prevents ZeroDivisionError)
        c11 = load_module(AGENT3_LAB_DIR / "ccde_11_lab.py", "ccde_11_phase8d_testmod")
        with self.assertRaises(ValueError):
            c11.forecast_5yr_capacity(10.0, 0.2, failover_utilization_cap=0.0)
        with self.assertRaises(ValueError):
            c11.forecast_5yr_capacity(10.0, 0.2, failover_utilization_cap=1.5)
        with self.assertRaises(ValueError):
            c11.audit_five_dimensions({"throughput_gbps": 5.0}, {"throughput_gbps": 0.0})

        # 3. ccde_14: Zero Trust strict bool ("False" must NOT pass!) + offload bounds
        c14 = load_module(AGENT3_LAB_DIR / "ccde_14_lab.py", "ccde_14_phase8d_testmod")
        for bad in ("False", "True", 0, 1, None):
            with self.assertRaises(ValueError):
                c14.audit_zero_trust_pillars({"mfa": True, "siem": bad})
        with self.assertRaises(ValueError):
            c14.model_east_west_firewall_bottleneck(100.0, 40.0, 1.2)
        with self.assertRaises(ValueError):
            c14.model_east_west_firewall_bottleneck(100.0, 0.0, 0.5)

    def test_phase9_agent_handoff_ccde18_and_auto20_fixes(self):
        """Phase 9: verify all AGENT-HANDOFF-fa.md @ 53871318 items on ccde_18 and auto_20."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. ccde_18: 10**500 -> ValueError (NOT OverflowError), exact NetApp profiles & strict < 10 ms boundary
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_phase9_testmod")
        base_c18 = {
            "dc_distance_km": 5000,
            "storage_replication": "asynchronous",
            "target_rpo_minutes": 15,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }
        with self.assertRaises(ValueError):
            c18.validate_pars_global_hld({**base_c18, "dc_distance_km": 10**500})
        with self.assertRaises(ValueError):
            c18.validate_pars_global_hld({**base_c18, "target_rpo_minutes": 10**500})
        with self.assertRaises(ValueError):
            c18.validate_pars_global_hld(base_c18, "vmware_vmsc_netapp_metrocluster")

        # Strict < 10.0 ms on netapp_vmsc_snapmirror_active_sync: 10.0 ms exact is NOT feasible, 9.9 ms IS feasible
        exact_10ms = {
            **base_c18,
            "dc_distance_km": 500,  # 500 * 0.01 * 1.4 = 7.0 ms routed prop + 3.0 ms overhead = 10.0 ms exact
            "assumed_equipment_and_detour_overhead_ms": 3.0,
            "storage_replication": "synchronous",
            "target_rpo_minutes": 0,
        }
        r_10 = c18.validate_pars_global_hld(exact_10ms, "netapp_vmsc_snapmirror_active_sync")
        self.assertEqual(r_10["domain_validations"][0]["assumed_total_end_to_end_rtt_ms"], 10.0)
        self.assertFalse(r_10["domain_validations"][0]["sync_feasible_for_profile"])
        self.assertFalse(r_10["all_architectural_checks_passed"])

        under_10ms = {**exact_10ms, "assumed_equipment_and_detour_overhead_ms": 2.9}
        r_99 = c18.validate_pars_global_hld(under_10ms, "netapp_vmsc_snapmirror_active_sync")
        self.assertEqual(r_99["domain_validations"][0]["assumed_total_end_to_end_rtt_ms"], 9.9)
        self.assertTrue(r_99["domain_validations"][0]["sync_feasible_for_profile"])
        self.assertTrue(r_99["all_architectural_checks_passed"])

        # ONTAP Select MetroCluster SDS: <= 5.0 ms RTT AND <= 5.0 ms jitter (fail-closed if jitter omitted)
        at_5ms = {**exact_10ms, "dc_distance_km": 200, "assumed_equipment_and_detour_overhead_ms": 2.2, "assumed_jitter_ms": 5.0}
        r_sds_ok = c18.validate_pars_global_hld(at_5ms, "netapp_ontap_select_metrocluster_sds")
        self.assertTrue(r_sds_ok["domain_validations"][0]["sync_feasible_for_profile"])
        over_5ms = {**at_5ms, "assumed_equipment_and_detour_overhead_ms": 2.3}
        r_sds_fail = c18.validate_pars_global_hld(over_5ms, "netapp_ontap_select_metrocluster_sds")
        self.assertFalse(r_sds_fail["domain_validations"][0]["sync_feasible_for_profile"])

        # 2. auto_20: z_score rejects NaN/Inf/bool/10**500; remediation_decision allowlist + simulation_only + causal_caveat
        a20 = load_module(AGENT3_LAB_DIR / "auto_20_lab.py", "auto_20_phase9_testmod")
        for bad_base in (
            [10.0, float("nan"), 12.0],
            [10.0, float("inf"), 12.0],
            [10.0, float("-inf"), 12.0],
            [10.0, True, 12.0],
            [10.0, False, 12.0],
            [10.0, 10**500, 12.0],
        ):
            with self.assertRaises(ValueError):
                a20.z_score(20.0, bad_base)
        with self.assertRaises(ValueError):
            a20.z_score(10**500, [10.0, 12.0])

        for bad_action in ("destroy_everything", "", None, 123, "drop_database"):
            with self.assertRaises(ValueError):
                a20.remediation_decision(bad_action, 0, 0.95, False)

        sim_ok = a20.remediation_decision("shift_single_branch_sdwan_path", 1, 0.95, False)
        self.assertTrue(sim_ok["simulation_only"])
        self.assertTrue(sim_ok["simulated_execution_allowed"])
        self.assertNotIn("executed", sim_ok)

        rca = a20.correlate_root_cause({"HUB-WEST"}, [{"branch_id": "BR-1", "hub": "HUB-WEST"}])
        self.assertIn("heuristic", rca["causal_caveat"].lower())

    def test_phase10a_handoff_f4e3ab1f_ccde18_jitter_and_auto20_zscore(self):
        """Phase 10A: ccde_18 fail-closed ONTAP Select jitter + auto_20 overflow & constant-baseline Z-score."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. ccde_18: fail-closed jitter on netapp_ontap_select_metrocluster_sds
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_phase10a_testmod")
        metro_base = {
            "dc_distance_km": 150,
            "assumed_equipment_and_detour_overhead_ms": 1.0,
            "storage_replication": "synchronous",
            "target_rpo_minutes": 0,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }
        # Omitted assumed_jitter_ms -> MUST fail closed (never claim jitter compliance!)
        r_missing = c18.validate_pars_global_hld(metro_base, "netapp_ontap_select_metrocluster_sds")
        d0 = r_missing["domain_validations"][0]
        self.assertTrue(d0["rtt_feasible_for_profile"])
        self.assertTrue(d0["jitter_required_by_profile"])
        self.assertFalse(d0["jitter_feasible_for_profile"])
        self.assertFalse(d0["sync_feasible_for_profile"])
        self.assertFalse(r_missing["all_architectural_checks_passed"])
        self.assertNotIn("satisfy", d0["note"].lower())

        # Jitter > 5.0 ms -> rejected; Jitter == 5.0 ms -> passes
        r_high_jitter = c18.validate_pars_global_hld(
            {**metro_base, "assumed_jitter_ms": 5.1}, "netapp_ontap_select_metrocluster_sds"
        )
        self.assertFalse(r_high_jitter["all_architectural_checks_passed"])
        self.assertFalse(r_high_jitter["domain_validations"][0]["jitter_feasible_for_profile"])

        r_ok_jitter = c18.validate_pars_global_hld(
            {**metro_base, "assumed_jitter_ms": 5.0}, "netapp_ontap_select_metrocluster_sds"
        )
        self.assertTrue(r_ok_jitter["all_architectural_checks_passed"])
        self.assertTrue(r_ok_jitter["domain_validations"][0]["jitter_feasible_for_profile"])

        # Invalid jitter types/values raise ValueError
        for bad_j in (-0.1, True, False, "2.0", float("nan"), float("inf"), 10**500):
            with self.assertRaises(ValueError):
                c18.validate_pars_global_hld({**metro_base, "assumed_jitter_ms": bad_j}, "netapp_ontap_select_metrocluster_sds")

        # 2. auto_20: scale-normalized Z-score + non-finite/overflow -> ValueError; constant baseline -> ValueError
        a20 = load_module(AGENT3_LAB_DIR / "auto_20_lab.py", "auto_20_phase10a_testmod")
        self.assertAlmostEqual(a20.z_score(1, [1e200, 0]), -1.0)
        self.assertAlmostEqual(a20.z_score(1e200, [1e200, 0]), 1.0)
        self.assertAlmostEqual(a20.z_score(1e308, [-1e308, 1e308]), 1.0)
        with self.assertRaises(ValueError):
            a20.z_score(1e308, [1e-308, 2e-308])
        with self.assertRaises(ValueError):
            a20.z_score(10**500, [1, 2])
        with self.assertRaises(ValueError):
            a20.z_score(5.0, [5.0, 5.0, 5.0])
        with self.assertRaises(ValueError):
            a20.z_score(9.0, [5.0, 5.0, 5.0])

    def test_phase10b_unrounded_rtt_scaled_zscore_and_overflow_sweep(self):
        """Phase 10B: ccde_18 unrounded RTT + async w/o jitter, auto_20 scaled Z-score, & 7-lab OverflowError->ValueError sweep."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. ccde_18 unrounded strict RTT boundary (< 10.0 ms) & async pass without jitter on ONTAP Select
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_phase10b_testmod")
        base = {
            "dc_distance_km": 100,
            "assumed_equipment_and_detour_overhead_ms": 8.599,
            "storage_replication": "synchronous",
            "target_rpo_minutes": 0,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "hybrid_sdwan_regional_hubs_plus_sase",
            "cloud_hub": "dual_colo_cloud_exchange_direct_connect",
            "macro_vrfs": 3,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "chapter_v_transfer_safeguard": None,
            "encryption_in_transit_assumed": True,
        }
        # 100*0.014 + 8.599 = 9.999 < 10.0 -> MUST PASS (would falsely fail if rounded to 10.00!)
        self.assertTrue(
            c18.validate_pars_global_hld(base, "netapp_vmsc_snapmirror_active_sync")["domain_validations"][0]["pass"]
        )
        # 100*0.014 + 8.6 = 10.0 -> MUST FAIL strict < 10.0
        self.assertFalse(
            c18.validate_pars_global_hld(
                {**base, "assumed_equipment_and_detour_overhead_ms": 8.6},
                "netapp_vmsc_snapmirror_active_sync",
            )["domain_validations"][0]["pass"]
        )
        # ONTAP Select async with target_rpo_minutes=15 passes even if assumed_jitter_ms is omitted
        self.assertTrue(
            c18.validate_pars_global_hld(
                {**base, "storage_replication": "asynchronous", "target_rpo_minutes": 15},
                "netapp_ontap_select_metrocluster_sds",
            )["domain_validations"][0]["pass"]
        )

        # 2. auto_19, ccde_11, ccde_14, ccde_17, spec_cyber, spec_wl, ccie_sec: 10**500 -> ValueError (never OverflowError)
        a19 = load_module(AGENT3_LAB_DIR / "auto_19_lab.py", "auto_19_phase10b_testmod")
        with self.assertRaises(ValueError):
            a19.evaluate_alert_hysteresis([10**500])

        c11 = load_module(AGENT3_LAB_DIR / "ccde_11_lab.py", "ccde_11_phase10b_testmod")
        with self.assertRaises(ValueError):
            c11.forecast_5yr_capacity(10**500, 0.2, 100.0)

        c14 = load_module(AGENT3_LAB_DIR / "ccde_14_lab.py", "ccde_14_phase10b_testmod")
        with self.assertRaises(ValueError):
            c14.model_east_west_firewall_bottleneck(10**500, 10.0, 0.5)

        c17 = load_module(AGENT3_LAB_DIR / "ccde_17_lab.py", "ccde_17_phase10b_testmod")
        with self.assertRaises(ValueError):
            c17.compute_5yr_tco("X", 10**500, 0, 0, 0)

        scy = load_module(AGENT3_LAB_DIR / "spec_cyber_lab.py", "spec_cyber_phase10b_testmod")
        with self.assertRaises(ValueError):
            scy.detect_c2_beaconing([0, 1, 2, 10**500])
        res_zero = scy.detect_c2_beaconing([5, 5, 5, 5])
        self.assertIsNone(res_zero["cv"])
        self.assertFalse(res_zero["beaconing_suspected"])

        swl = load_module(AGENT3_LAB_DIR / "spec_wl_lab.py", "spec_wl_phase10b_testmod")
        with self.assertRaises(ValueError):
            swl.dbm_to_mw(10**500)
        with self.assertRaises(ValueError):
            swl.dbm_to_mw(10000)

        csec = load_module(AGENT3_LAB_DIR / "ccie_sec_lab.py", "ccie_sec_phase10b_testmod")
        for bad_skew in (float("nan"), float("inf"), 10**500, True):
            with self.assertRaises(ValueError):
                csec.audit_ntp_dns_preflight([{"name": "ISE-1", "clock_skew_sec": bad_skew, "dns_forward_reverse_ok": True}])

    def test_phase10c_ccie_and_specialist_strict_validation_sweep(self):
        """Phase 10C: strict bool/numeric/range/overflow validation across 10 CCIE & Specialist labs."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        bad_bools = ("False", "True", "", 0, 1, None, [], {})

        # 1. ccie_01
        m = load_module(AGENT3_LAB_DIR / "ccie_01_lab.py", "ccie_01_p10c")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.check_sda_fusion_vrf("CORP", bv, True, True)
            with self.assertRaises(ValueError):
                m.simulate_redistribution("10.0.0.0/24", "EIGRP", 90, bv)
        for bad_pct in (-1, 101, float("nan"), float("inf"), 10**500, True):
            with self.assertRaises(ValueError):
                m.evaluate_ccie_exam_gate(bad_pct, 80.0)
        with self.assertRaises(ValueError):
            m.simulate_redistribution("10.0.0.1/24", "EIGRP", 90, True)  # host bits set

        # 2. ccie_dc
        m = load_module(AGENT3_LAB_DIR / "ccie_dc_lab.py", "ccie_dc_p10c")
        ok_aci = {k: True for k in ("aaep_bound_to_domain", "vlan_in_domain_pool", "bd_unicast_routing", "bd_has_subnet", "bd_vrf_attached", "contract_applied_both_sides")}
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.verify_aci_5_link_chain({**ok_aci, "contract_applied_both_sides": bv})
            with self.assertRaises(ValueError):
                m.verify_nxos_evpn_vxlan(bv, ["10.0.0.1"], True, 10010)
        with self.assertRaises(ValueError):
            m.verify_nxos_evpn_vxlan(True, ["999.999.1.1"], True, 10010)
        with self.assertRaises(ValueError):
            m.verify_nxos_evpn_vxlan(True, ["10.0.0.1"], True, 16_777_216)

        # 3. ccie_wl
        m = load_module(AGENT3_LAB_DIR / "ccie_wl_lab.py", "ccie_wl_p10c")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.radioactive_client_trace("aa:bb:cc:dd:ee:ff", bv, True, 10)
        with self.assertRaises(ValueError):
            m.radioactive_client_trace("aa:bb:cc:dd:ee:ff", True, True, 70000)

        # 4. spec_dc_aci
        m = load_module(AGENT3_LAB_DIR / "spec_dc_aci_lab.py", "spec_dc_aci_p10c")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.apic_offline_impact(bv)
            with self.assertRaises(ValueError):
                m.evaluate_aci_traffic("EPG-A", "EPG-B", 443, bv, [])
        with self.assertRaises(ValueError):
            m.evaluate_aci_traffic("EPG-A", "EPG-B", 0, True, [])

        # 5. spec_dc_nx
        m = load_module(AGENT3_LAB_DIR / "spec_dc_nx_lab.py", "spec_dc_nx_p10c")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.simulate_peer_link_failure(bv, True)
        with self.assertRaises(ValueError):
            m.check_vpc_type1({"mtu": 9216, "stp_mode": "rapid-pvst", "native_vlan": 4095}, {"mtu": 9216, "stp_mode": "rapid-pvst", "native_vlan": 1})

        # 6. spec_dc_stor
        m = load_module(AGENT3_LAB_DIR / "spec_dc_stor_lab.py", "spec_dc_stor_p10c")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.check_fcoe_dcb_readiness({"name": "Eth1/1", "pfc_cos3_enabled": bv, "ets_enabled": True, "mtu": 9216})
        with self.assertRaises(ValueError):
            m.check_fcoe_dcb_readiness({"name": "Eth1/1", "ets_enabled": True, "mtu": 9216})  # missing required bool

        # 7. spec_ent_campus
        m = load_module(AGENT3_LAB_DIR / "spec_ent_campus_lab.py", "spec_ent_campus_p10c")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.simulate_svl_failure(bv, True)

        # 8. spec_sp_xr
        m = load_module(AGENT3_LAB_DIR / "spec_sp_xr_lab.py", "spec_sp_xr_p10c")
        xr = m.MockIOSXRRouter()
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                xr.commit(confirmed_seconds=60, confirmed_by_operator=bv)
        with self.assertRaises(ValueError):
            xr.commit(confirmed_seconds=0, confirmed_by_operator=True)

        # 9. spec_wl_survey
        m = load_module(AGENT3_LAB_DIR / "spec_wl_survey_lab.py", "spec_wl_survey_p10c")
        for bad_d in (0, -5, float("nan"), float("inf"), 10**500, True):
            with self.assertRaises(ValueError):
                m.fspl_db(bad_d, 5180.0)
        with self.assertRaises(ValueError):
            m.audit_24ghz_plan({"AP-1": 15})
        with self.assertRaises(ValueError):
            m.evaluate_rf_cell(14.0, 4.0, 10.0, 5180.0, ["unknown_wall"])

        # 10. spec_cyber_hunt
        m = load_module(AGENT3_LAB_DIR / "spec_cyber_hunt_lab.py", "spec_cyber_hunt_p10c")
        for bad_ts in (float("nan"), float("inf"), 10**500, True):
            with self.assertRaises(ValueError):
                m.detect_beaconing([0, 10, 20, bad_ts])

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
