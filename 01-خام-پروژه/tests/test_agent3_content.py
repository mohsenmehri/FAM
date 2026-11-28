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
    # Phase 12A — Transferred CCNA Core Batch (5 of 17 former Agent 1 lessons)
    "ccna_02_vlan", "ccna_v1", "ccna_v6", "ccna_03", "ccna_04",
    # Phase 12B — Transferred CCNA Services/Security/Wireless/SDN Batch (7 of 17 former Agent 1 lessons)
    "ccna_dhcp", "ccna_nat", "ccna_05", "ccna_acl", "ccna_qos_ssh", "ccna_wl", "ccna_06",
    # Phase 12C — Transferred Advanced Switching/Routing/Troubleshooting/BFD Batch (5 of 17 former Agent 1 lessons)
    "adv_01", "adv_02", "adv_03", "adv_04", "adv_bfd",
    # Final Consolidation Batches 1-3 — Remaining 7 Advanced + 11 CCNP lessons (18 lessons -> 99 total in agent3/)
    "adv_pvl", "adv_ec", "adv_eigrp", "adv_redist", "adv_bgp", "adv_qos", "adv_mcast",
    "ccnp_01", "ccnp_02", "ccnp_enc_arch", "ccnp_enc_inf", "ccnp_enc_sec", "ccnp_enc_auto",
    "ccnp_ensdwi", "ccnp_ensld", "ccnp_enauto", "ccnp_encc", "ccnp_enna",
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
        self.assertEqual(len(AGENT3_ALLOWED_IDS), 99)
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
        good_tok = auto07.build_hs256_jwt_demo({"sub": "u", "exp": now_ts + 3600}, secret)
        good_res = auto07.evaluate_hs256_jwt_demo(good_tok, secret, now_ts=now_ts)
        self.assertTrue(good_res["demo_checks_passed"])
        self.assertTrue(good_res["educational_demo_only"])

        parts = good_tok.split(".")
        none_hdr = auto07.b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
        self.assertFalse(auto07.evaluate_hs256_jwt_demo(f"{none_hdr}.{parts[1]}.", secret, now_ts=now_ts)["demo_checks_passed"])

        exp_tok = auto07.build_hs256_jwt_demo({"sub": "u", "exp": now_ts - 10}, secret)
        exp_res = auto07.evaluate_hs256_jwt_demo(exp_tok, secret, now_ts=now_ts)
        self.assertFalse(exp_res["demo_checks_passed"])
        self.assertEqual(exp_res["reason"], "token_expired_or_missing_exp")

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
                ev_text = str(data.get("evidence", ""))
                self.assertTrue(
                    ev_text == "Designed — Not Run" or ("اجرا نشده" in ev_text),
                    f"{lesson_id}: evidence must honestly state non-live-equipment execution, got {ev_text!r}",
                )
                rev_status = data.get("reviewStatus", "")
                self.assertIn("بازبینی مستقل", rev_status)
                self.assertIn("انجام نشده", rev_status)

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

    def test_phase10d_ccde_complete_strict_validation_sweep(self):
        """Phase 10D: complete 100% CCDE strict bool/numeric/range/overflow validation (9 remaining labs)."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        bad_bools = ("False", "True", "", 0, 1, None, [], {})
        bad_nums = (-1, float("nan"), float("inf"), 10**500, True)

        # 1. ccde_03
        m = load_module(AGENT3_LAB_DIR / "ccde_03_lab.py", "ccde_03_p10d")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.select_sp_transport(bv, True)
        for bn in bad_nums:
            with self.assertRaises(ValueError):
                m.model_sp_peering_economics(bn, 0.65, 18000, 0.5)
        with self.assertRaises(ValueError):
            m.model_sp_peering_economics(100, 0.65, 18000, 1.5)

        # 2. ccde_05
        m = load_module(AGENT3_LAB_DIR / "ccde_05_lab.py", "ccde_05_p10d")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.evaluate_dci_l2_stretch(bv, True)
        for bn in (0, -5, float("nan"), float("inf"), 10**500, True):
            with self.assertRaises(ValueError):
                m.evaluate_dci_distance("A-B", bn)

        # 3. ccde_06
        m = load_module(AGENT3_LAB_DIR / "ccde_06_lab.py", "ccde_06_p10d")
        for bn in bad_nums:
            with self.assertRaises(ValueError):
                m.compare_wan_tco(10, bn, 350, 150)
        with self.assertRaises(ValueError):
            m.aar_select_path("VoIP", {"max_rtt": 100, "max_jitter": 15, "max_loss": 0.5}, [])

        # 4. ccde_07
        m = load_module(AGENT3_LAB_DIR / "ccde_07_lab.py", "ccde_07_p10d")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.select_cloud_interconnect(10.0, bv, True)
        with self.assertRaises(ValueError):
            m.detect_cidr_overlaps({"A": "10.0.0.1/24"})  # host bits set

        # 5. ccde_10
        m = load_module(AGENT3_LAB_DIR / "ccde_10_lab.py", "ccde_10_p10d")
        for bad_p in (-0.1, 1.1, float("nan"), float("inf"), 10**500, True):
            with self.assertRaises(ValueError):
                m.series_availability([0.99, bad_p])
            with self.assertRaises(ValueError):
                m.parallel_availability([0.99, bad_p])
        with self.assertRaises(ValueError):
            m.series_availability([])

        # 6. ccde_15
        m = load_module(AGENT3_LAB_DIR / "ccde_15_lab.py", "ccde_15_p10d")
        for bn in bad_nums:
            with self.assertRaises(ValueError):
                m.rto_financial_justification(bn, 2.0, 4.0, 0.25, 250000.0)

        # 7. ccde_16
        m = load_module(AGENT3_LAB_DIR / "ccde_16_lab.py", "ccde_16_p10d")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.select_migration_strategy(5, bv)
            with self.assertRaises(ValueError):
                m.evaluate_mop_gate(bv, {"bgp": True}, 10, 60)
            with self.assertRaises(ValueError):
                m.evaluate_mop_gate(True, {"bgp": bv}, 10, 60)

        # 8. ccde_19
        m = load_module(AGENT3_LAB_DIR / "ccde_19_lab.py", "ccde_19_p10d")
        ok19 = {
            "max_routers_per_igp_domain": 200, "inter_domain_stitching": "bgp_lu_unified_sr",
            "flex_algo_slices": 2, "tilfa_enabled": True, "rings_two_connected_within_msd": True,
            "service_plane": "evpn_plus_l3vpn_bgp_free_core", "migration_mechanism": "phased_srms_coexistence",
            "rpki_and_flowspec": True, "ixp_cdn_offload_pct": 65,
        }
        for key in ("tilfa_enabled", "rings_two_connected_within_msd", "rpki_and_flowspec"):
            for bv in bad_bools:
                with self.assertRaises(ValueError):
                    m.validate_aria_telecom_hld({**ok19, key: bv})
            missing = ok19.copy()
            del missing[key]
            with self.assertRaises(ValueError):
                m.validate_aria_telecom_hld(missing)
        for bad_pct in (-1, 101, float("nan"), 10**500, True):
            with self.assertRaises(ValueError):
                m.validate_aria_telecom_hld({**ok19, "ixp_cdn_offload_pct": bad_pct})

        # 9. ccde_20
        m = load_module(AGENT3_LAB_DIR / "ccde_20_lab.py", "ccde_20_p10d")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                m.audit_hld_completeness(m.REQUIRED_HLD_SECTIONS, bv)
            with self.assertRaises(ValueError):
                m.detect_exam_400_007_traps({
                    "ignores_budget_or_ops_skill_constraint": bv,
                    "chooses_most_complex_tech_without_driver": False,
                    "skips_migration_coexistence": False,
                })

    def test_phase10e_automation_complete_strict_validation_sweep(self):
        """Phase 10E: complete 100% unmerged Automation strict validation (auto_06, auto_07, auto_09, auto_15, auto_16, auto_17)."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        bad_bools = ("False", "True", "", 0, 1, None, [], {})

        # 1. auto_07: bool exp rejected (isinstance(True, int) trap!), malformed base64/JSON returns clean rejection
        a07 = load_module(AGENT3_LAB_DIR / "auto_07_lab.py", "auto_07_p10e")
        secret = b"test-secret"
        bool_exp_tok = a07.build_hs256_jwt_demo({"sub": "bot", "exp": True}, secret)
        res_bool_exp = a07.evaluate_hs256_jwt_demo(bool_exp_tok, secret, now_ts=0)
        self.assertFalse(res_bool_exp["demo_checks_passed"])
        self.assertEqual(res_bool_exp["reason"], "token_expired_or_missing_exp")
        self.assertFalse(a07.evaluate_hs256_jwt_demo("not!b64.not!b64.sig", secret)["demo_checks_passed"])
        with self.assertRaises(ValueError):
            a07.evaluate_hs256_jwt_demo(bool_exp_tok, secret, now_ts=True)

        # 2. auto_15: invalid desired / prefixes types rejected
        a15 = load_module(AGENT3_LAB_DIR / "auto_15_lab.py", "auto_15_p10e")
        iac = a15.MiniDeclarativeIaC()
        with self.assertRaises(ValueError):
            iac.plan({"bad": "not-a-dict"})
        with self.assertRaises(ValueError):
            a15.validate_sot_prefixes(["10.0.0.1/24"])  # host bits set
        with self.assertRaises(ValueError):
            a15.validate_sot_prefixes("10.0.0.0/24")

        # 3. auto_16: strict bool on post_verify_ok (no "False" skipping rollback!)
        a16 = load_module(AGENT3_LAB_DIR / "auto_16_lab.py", "auto_16_p10e")
        for bv in bad_bools:
            with self.assertRaises(ValueError):
                a16.run_pipeline({"raw_yaml": "vlan: 30\n", "vlan_id": 30}, post_verify_ok=bv)

        # 4. auto_17: catches space-separated ENV secrets and rejects non-list inputs
        a17 = load_module(AGENT3_LAB_DIR / "auto_17_lab.py", "auto_17_p10e")
        self.assertTrue(len(a17.audit_dockerfile(["FROM python:3.11-slim", "USER appuser", "ENV API_PASSWORD supersecret"])) == 1)
        self.assertEqual(a17.audit_dockerfile(["# note about :latest", "FROM python:3.11-slim", "USER appuser"]), [])
        with self.assertRaises(ValueError):
            a17.audit_dockerfile("FROM python:3.11-slim")

        # 5. auto_06 & auto_09: loopback HTTP labs execute cleanly with stricter 400 validation
        a06 = load_module(AGENT3_LAB_DIR / "auto_06_lab.py", "auto_06_p10e")
        r06 = a06.run_local_rest_lab()
        self.assertEqual(r06["bad_post_status"], 400)
        self.assertEqual(r06["duplicate_post_status"], 409)

    def test_phase11_handoff_f3a80939_ccde18_and_auto03_remediation(self):
        """Phase 11: full remediation of AGENT-HANDOFF-fa.md @ f3a809393e on ccde_18 and auto_03."""
        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. ccde_18 prose/quiz/sources regressions
        c18 = json.loads((BLUEPRINT_DIR / "ccde_18.json").read_text(encoding="utf-8"))
        c18_txt = json.dumps(
            {k: c18[k] for k in ("title", "sections", "glossary", "stages", "interactiveQuiz")},
            ensure_ascii=False,
        )
        self.assertEqual(c18["meta"]["version"], "reviewed.12")
        for forbidden in (
            "۹۰ تا ۹۵",
            "۹۰–۹۵",
            "میلیون‌ها دلار",
            "سناریوی واقعی",
            "واقعی RTT",
            "مسیر واقعی",
            "Dell Metro Node",
            "delltechnologies.com",
            "MetroCluster/vMSC",
        ):
            self.assertNotIn(forbidden, c18_txt, f"ccde_18 still contains stale phrase: {forbidden}")
        self.assertIn("https://docs.netapp.com/us-en/netapp-solutions-virtualization/vmware/vmw-vmsc-with-smas.html", c18["meta"]["sources"])
        self.assertIn("https://docs.netapp.com/us-en/ontap-select/concept_ha_config.html", c18["meta"]["sources"])
        self.assertIn("Single-Router SPOF", c18_txt)
        self.assertIn("به‌تنهایی انطباق PCI-DSS یا تحقق کامل Zero Trust را اثبات یا تضمین نمی‌کند", c18["interactiveQuiz"][4]["explanationHtml"])
        self.assertIn("Route-Leaking", c18["interactiveQuiz"][5]["options"][1])
        self.assertIn("SPOF", c18["interactiveQuiz"][7]["explanationHtml"])

        # 2. auto_03 prose/quiz/sources regressions
        a03 = json.loads((BLUEPRINT_DIR / "auto_03.json").read_text(encoding="utf-8"))
        a03_txt = json.dumps(
            {k: a03[k] for k in ("title", "sections", "glossary", "stages", "interactiveQuiz")},
            ensure_ascii=False,
        )
        self.assertTrue(a03["meta"]["version"].startswith(("reviewed.", "integration-review.")))
        for forbidden in ("زیر ۱ دقیقه", "ظرف ۵ ثانیه", "dry_run=True BEFORE prod!"):
            self.assertNotIn(forbidden, a03_txt, f"auto_03 still contains stale phrase: {forbidden}")
        for required in (
            "task.is_dry_run()",
            "nornir_netmiko",
            "data.role",
            "read_timeout",
            "commit",
        ):
            self.assertIn(required, a03_txt, f"auto_03 missing required nuance: {required}")

        # 3. auto_03_lab.py unit checks: SimpleInventory data.role, explicit dry_run guard, platform save_config
        mod = load_module(AGENT3_LAB_DIR / "auto_03_lab.py", "auto_03_p11")
        inv = [
            {"host": "192.0.2.11", "platform": "cisco_ios", "groups": ["campus"], "data": {"role": "pilot"}},
            {"host": "192.0.2.12", "platform": "cisco_xr", "groups": ["core"], "data": {"role": "production"}},
        ]
        res = mod.run_nornir_style_pilot(inv, "pilot", ["ntp server 192.0.2.123"], dry_run=True)
        self.assertEqual(len(res), 1)
        self.assertFalse(res[0]["applied"])
        self.assertTrue(res[0]["dry_run_honored"])
        self.assertTrue(res[0]["session_closed"])

        # Fail-closed when task/plugin does NOT support dry_run (mirroring raw nornir_netmiko)
        with self.assertRaises(RuntimeError):
            mod.run_nornir_style_pilot(
                inv, "pilot", ["ntp server 192.0.2.123"], dry_run=True, task_honors_dry_run=False
            )

        # Platform-dependent save_config() behavior
        with mod.MockNetmikoConnection("192.0.2.11", platform="cisco_ios") as ios:
            ios.send_config_set(["ntp server 192.0.2.123"])
            self.assertTrue(ios.dirty_running_config)
            self.assertTrue(ios.save_config()["saved"])
            self.assertFalse(ios.dirty_running_config)
        with mod.MockNetmikoConnection("192.0.2.12", platform="cisco_xr") as xr:
            with self.assertRaises(NotImplementedError):
                xr.save_config()

        # Invalid task_honors_dry_run, role_filter, or commands rejected
        with self.assertRaises(ValueError):
            mod.run_nornir_style_pilot(inv, "pilot", ["cmd"], dry_run=True, task_honors_dry_run="True")
        with self.assertRaises(ValueError):
            mod.run_nornir_style_pilot(inv, "", ["cmd"], dry_run=True)
        with self.assertRaises(ValueError):
            mod.run_nornir_style_pilot(inv, "pilot", [""], dry_run=True)

    def test_phase12a_transferred_ccna_core_batch(self):
        """Phase 12A: independent technical audit & strict lab validation for 5 transferred CCNA lessons."""
        batch_ids = ("ccna_02_vlan", "ccna_v1", "ccna_v6", "ccna_03", "ccna_04")
        flagged_imports = {"socket", "http", "urllib", "requests", "subprocess", "os"}

        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        for lid in batch_ids:
            lab_path = AGENT3_LAB_DIR / f"{lid}_lab.py"
            tree = ast.parse(lab_path.read_text(encoding="utf-8"))
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(n.name.split(".")[0] for n in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertEqual(mods & flagged_imports, set(), f"{lid}_lab.py uses flagged import: {mods & flagged_imports}")

        # 1. ccna_02_vlan: discrepancy reconciliation + strict lab tests
        bp_vlan = json.loads((BLUEPRINT_DIR / "ccna_02_vlan.json").read_text(encoding="utf-8"))
        txt_vlan = json.dumps(
            {k: bp_vlan[k] for k in ("title", "sections", "glossary", "stages", "interactiveQuiz")},
            ensure_ascii=False,
        )
        for required in ("10,20,50,999", "nonegotiate", "vlan dot1q tag native", "encapsulation dot1q", "show vlan brief", "اجرا نشده"):
            self.assertIn(required, txt_vlan)
        self.assertNotIn("اجرا شده روی سوئیچ واقعی", txt_vlan)
        m_vlan = load_module(AGENT3_LAB_DIR / "ccna_02_vlan_lab.py", "ccna_02_vlan_p12a")
        ev_bad = m_vlan.audit_trunk_pair(
            [10, 20, 999], [10, 20, 999], [10, 20], [10, 20, 999], 999, 1, [10, 20, 50]
        )
        self.assertFalse(ev_bad["model_checks_ok"])
        ev_good = m_vlan.audit_trunk_pair(
            [10, 20, 50, 999], [10, 20, 50, 999], [10, 20, 50, 999], [10, 20, 50, 999], 999, 999, [10, 20, 50]
        )
        self.assertTrue(ev_good["model_checks_ok"])
        with self.assertRaises(ValueError):
            m_vlan.evaluate_dtp_link("trunk", "trunk", sw1_nonegotiate="True")
        with self.assertRaises(ValueError):
            m_vlan.audit_trunk_pair([10, 999], [10, 999], [10, 999], [10, 999], 4095, 4095, [10])

        # 2. ccna_v1: container qualification, EST/VST/VGT & shared kernel + strict lab tests
        bp_v1 = json.loads((BLUEPRINT_DIR / "ccna_v1.json").read_text(encoding="utf-8"))
        txt_v1 = json.dumps(bp_v1["sections"], ensure_ascii=False)
        for required in ("EST", "VST", "VGT", "کرنل"):
            self.assertIn(required, txt_v1)
        m_v1 = load_module(AGENT3_LAB_DIR / "ccna_v1_lab.py", "ccna_v1_p12a")
        self.assertFalse(m_v1.audit_vswitch_uplink("EST", [10], "trunk", [10, 20])["model_checks_ok"])
        self.assertFalse(m_v1.audit_vswitch_uplink("VST", [10, 20], "access", [10])["model_checks_ok"])
        self.assertTrue(m_v1.audit_vswitch_uplink("VST", [10, 20], "trunk", [10, 20, 30])["model_checks_ok"])
        with self.assertRaises(ValueError):
            m_v1.classify_cloud_responsibility("UnknownModel")

        # 3. ccna_v6: vendor-default AD, RFC 5340 vs 5838, fe80 exit-if, IPv6-only RID + strict lab tests
        bp_v6 = json.loads((BLUEPRINT_DIR / "ccna_v6.json").read_text(encoding="utf-8"))
        txt_v6 = json.dumps(bp_v6["sections"], ensure_ascii=False)
        for required in ("RFC 5340", "RFC 5838", "fe80::", "ipv6 unicast-routing"):
            self.assertIn(required, txt_v6)
        m_v6 = load_module(AGENT3_LAB_DIR / "ccna_v6_lab.py", "ccna_v6_p12a")
        self.assertFalse(m_v6.validate_ipv6_static_next_hop("2001:db8:99::/64", "fe80::2", None)["valid"])
        self.assertTrue(m_v6.validate_ipv6_static_next_hop("2001:db8:99::/64", "fe80::2", "Gi0/0")["valid"])
        self.assertFalse(m_v6.validate_ospfv3_router_id(False, None)["can_start_in_ios_model"])
        tie = m_v6.build_fib_from_candidates([
            {"prefix": "10.99.0.0/24", "protocol": "ospf", "ad": 110, "metric": 10},
            {"prefix": "10.99.0.0/24", "protocol": "eigrp", "ad": 110, "metric": 2816},
        ])
        self.assertEqual(len(tie["ambiguous_cross_protocol_ties"]), 1)
        self.assertEqual(tie["installed_fib_routes"], [])
        with self.assertRaises(ValueError):
            m_v6.lookup_best_route("2001:db8:1:2::9", [], ipv6_unicast_routing="True")
        with self.assertRaises(ValueError):
            m_v6.validate_ipv6_static_next_hop("2001:db8:99::1/64", "fe80::2", "Gi0/0")

        # 4. ccna_03: complete OSPF adjacency, Mbps ref-bw, 2WAY/DROTHER, Floating Static + strict lab tests
        bp_03 = json.loads((BLUEPRINT_DIR / "ccna_03.json").read_text(encoding="utf-8"))
        txt_03 = json.dumps(bp_03["sections"], ensure_ascii=False)
        for required in ("auto-cost reference-bandwidth", "2WAY", "EXSTART", "IP SLA"):
            self.assertIn(required, txt_03)
        m_03 = load_module(AGENT3_LAB_DIR / "ccna_03_lab.py", "ccna_03_p12a")
        self.assertEqual(m_03.ospf_interface_cost(1000, 100000), 100)
        self.assertEqual(m_03.ospf_interface_cost(10000, 100000), 10)
        with self.assertRaises(ValueError):
            m_03.ospf_interface_cost(10**500, 100)
        with self.assertRaises(ValueError):
            m_03.select_floating_static("True", 110, 120)

        # 5. ccna_04: HSRPv1/v2, VRRP, preempt delay, NTP 1..15/16, Syslog 0..7/TLS, SNMPv3 + strict lab tests
        bp_04 = json.loads((BLUEPRINT_DIR / "ccna_04.json").read_text(encoding="utf-8"))
        txt_04 = json.dumps(bp_04["sections"], ensure_ascii=False)
        for required in ("224.0.0.102", "VRRP", "preempt delay", "6514", "authPriv"):
            self.assertIn(required, txt_04)
        m_04 = load_module(AGENT3_LAB_DIR / "ccna_04_lab.py", "ccna_04_p12a")
        self.assertFalse(m_04.evaluate_ntp_stratum(15)["synchronized"])
        self.assertEqual(m_04.evaluate_ntp_stratum(15)["local_stratum"], 16)
        self.assertFalse(m_04.audit_snmp_config("v2c")["secure"])
        self.assertTrue(m_04.audit_snmp_config("v3", "authPriv")["secure"])
        with self.assertRaises(ValueError):
            m_04.evaluate_hsrp_pair(
                {"name": "R1", "version": 2, "group": 10, "priority": 150, "preempt": "True", "ip": "10.0.10.2"},
                {"name": "R2", "version": 2, "group": 10, "priority": 100, "preempt": False, "ip": "10.0.10.3"},
            )
        with self.assertRaises(ValueError):
            m_04.filter_syslog_events([(8, "bad")], 4)

    def test_phase12b_transferred_ccna_services_security_batch(self):
        """Phase 12B: independent technical audit & strict lab validation for 7 transferred CCNA lessons."""
        batch_ids = ("ccna_dhcp", "ccna_nat", "ccna_05", "ccna_acl", "ccna_qos_ssh", "ccna_wl", "ccna_06")
        flagged_imports = {"socket", "http", "urllib", "requests", "subprocess", "os"}

        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        for lid in batch_ids:
            lab_path = AGENT3_LAB_DIR / f"{lid}_lab.py"
            tree = ast.parse(lab_path.read_text(encoding="utf-8"))
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(n.name.split(".")[0] for n in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertEqual(mods & flagged_imports, set(), f"{lid}_lab.py uses flagged import: {mods & flagged_imports}")

        # 1. ccna_dhcp: giaddr, excluded-address, APIPA, DNS UDP/TCP 53
        m_dhcp = load_module(AGENT3_LAB_DIR / "ccna_dhcp_lab.py", "ccna_dhcp_p12b")
        self.assertEqual(
            m_dhcp.allocate_dhcp_lease("10.10.10.0/24", [("10.10.10.1", "10.10.10.10")], set(), "aa:bb:cc:00:00:01")["assigned_ip"],
            "10.10.10.11",
        )
        self.assertFalse(m_dhcp.simulate_dhcp_relay(30, "10.10.30.1", None, {"V10": "10.10.10.0/24"})["dora_success"])
        with self.assertRaises(ValueError):
            m_dhcp.simulate_dhcp_relay(10, "10.10.10.1", "10.99.0.10", {}, server_reachable="True")

        # 2. ccna_nat: Inside->Outside Routing before NAT, Outside->Inside NAT before Routing, RFC 1918
        m_nat = load_module(AGENT3_LAB_DIR / "ccna_nat_lab.py", "ccna_nat_p12b")
        self.assertFalse(m_nat.is_rfc1918_private("203.0.113.10"))
        self.assertFalse(
            m_nat.simulate_outbound_nat("192.168.10.11", 50000, "198.51.100.1", 443, "pat", True, True, False, ["203.0.113.10"], {})["translated"]
        )
        with self.assertRaises(ValueError):
            m_nat.simulate_inbound_return_nat("203.0.113.10:50000", {}, has_internal_route="True")

        # 3. ccna_05: ACL implicit deny, Port Security rejects dynamic ports, DAI needs Snooping/ARP ACL
        m_05 = load_module(AGENT3_LAB_DIR / "ccna_05_lab.py", "ccna_05_p12b")
        with self.assertRaises(ValueError):
            m_05.evaluate_port_security("dynamic_auto", 1, set(), "aa:bb:cc:00:00:01")
        self.assertEqual(m_05.evaluate_dai_packet(False, "10.10.10.5", "aa:aa:aa:00:00:01", {}, {})["action"], "drop")
        with self.assertRaises(ValueError):
            m_05.evaluate_dai_packet("False", "10.10.10.5", "aa:aa:aa:00:00:01", {}, {})

        # 4. ccna_acl: AAA fallback NOT triggered on explicit reject; Type 7 reversible vs Type 9 secure
        m_acl = load_module(AGENT3_LAB_DIR / "ccna_acl_lab.py", "ccna_acl_p12b")
        self.assertFalse(m_acl.evaluate_aaa_login(["group_tacacs+", "local"], True, False, True)["authenticated"])
        self.assertTrue(m_acl.evaluate_aaa_login(["group_tacacs+", "local"], False, False, True)["authenticated"])
        self.assertTrue(m_acl.audit_password_type(7)["reversible"])
        self.assertTrue(m_acl.audit_password_type(9)["secure_for_prod"])
        with self.assertRaises(ValueError):
            m_acl.evaluate_aaa_login(["group_tacacs+"], "True", True, True)

        # 5. ccna_qos_ssh: VoIP SLA overflow guard, EF/46, SSHv2 prerequisites, SCP vs FTP
        m_qos = load_module(AGENT3_LAB_DIR / "ccna_qos_ssh_lab.py", "ccna_qos_ssh_p12b")
        self.assertEqual(m_qos.classify_dscp_marking("voice")["dscp_decimal"], 46)
        self.assertFalse(m_qos.audit_ssh_prerequisites("Router", "", 0, 2, ["telnet"], False)["ssh_ready_and_hardened"])
        self.assertTrue(m_qos.audit_file_transfer_protocol("SCP")["encrypted"])
        with self.assertRaises(ValueError):
            m_qos.evaluate_voip_qos_sla(10**500, 10.0, 0.1)

        # 6. ccna_wl: CRITICAL regression — verify Local Mode quiz Q2 fixed (AP=Access, WLC=Trunk) + lab checks
        bp_wl = json.loads((BLUEPRINT_DIR / "ccna_wl.json").read_text(encoding="utf-8"))
        q2 = bp_wl["interactiveQuiz"][1]
        self.assertEqual(q2["correctIndex"], 1)
        self.assertIn("AP در حالت Access", q2["options"][1])
        self.assertIn("WLC در حالت Trunk", q2["options"][1])
        m_wl = load_module(AGENT3_LAB_DIR / "ccna_wl_lab.py", "ccna_wl_p12b")
        self.assertTrue(m_wl.audit_ap_wlc_switchports("local", "access", "trunk")["architecture_valid"])
        self.assertFalse(m_wl.audit_ap_wlc_switchports("local", "trunk", "access")["architecture_valid"])
        with self.assertRaises(ValueError):
            m_wl.audit_wlan_security("WPA3-Personal", pmf_enabled="True")

        # 7. ccna_06: NBI/SBI, REST CRUD status codes, Agentless Ansible, YAML Tab detection
        m_06 = load_module(AGENT3_LAB_DIR / "ccna_06_lab.py", "ccna_06_p12b")
        self.assertEqual(m_06.compare_config_mgmt_tool("ansible")["architecture"], "Agentless")
        self.assertFalse(m_06.validate_json_and_yaml_indent('{"a": 1}', ["a:", "\tb: 1"])["yaml_valid"])
        with self.assertRaises(ValueError):
            m_06.validate_json_and_yaml_indent('{"a": 1}', ["a: 1"], allow_tabs="False")

    def test_phase12c_transferred_advanced_batch(self):
        """Phase 12C: independent technical audit & strict lab validation for 5 transferred adv_* lessons."""
        batch_ids = ("adv_01", "adv_02", "adv_03", "adv_04", "adv_bfd")
        flagged_imports = {"socket", "http", "urllib", "requests", "subprocess", "os"}

        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        for lid in batch_ids:
            lab_path = AGENT3_LAB_DIR / f"{lid}_lab.py"
            tree = ast.parse(lab_path.read_text(encoding="utf-8"))
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(n.name.split(".")[0] for n in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertEqual(mods & flagged_imports, set(), f"{lid}_lab.py uses flagged import: {mods & flagged_imports}")

        # 1. adv_01: MST 3-key match, Interface BPDU Filter loop trap, Root/Loop mutual exclusion, UDLD Aggressive
        m_a01 = load_module(AGENT3_LAB_DIR / "adv_01_lab.py", "adv_01_p12c")
        with self.assertRaises(ValueError):
            m_a01.evaluate_stp_port_protection("distribution_downlink", "superior_bpdu_received", root_guard=True, loop_guard=True)
        self.assertTrue(
            m_a01.evaluate_stp_port_protection("access_portfast", "bpdu_received", interface_bpdu_filter=True)["l2_loop_risk"]
        )
        self.assertEqual(m_a01.evaluate_udld_fiber_fault("aggressive", True, 8)["port_state"], "err-disabled")
        with self.assertRaises(ValueError):
            m_a01.evaluate_udld_fiber_fault("aggressive", "True", 8)

        # 2. adv_02: Area 0 cannot be stub/nssa, Standard NSSA has no auto-default, O > O IA & E1 > E2
        m_a02 = load_module(AGENT3_LAB_DIR / "adv_02_lab.py", "adv_02_p12c")
        with self.assertRaises(ValueError):
            m_a02.evaluate_ospf_area_policy(0, "stub")
        self.assertFalse(m_a02.evaluate_ospf_area_policy(10, "nssa")["auto_default_route"])
        self.assertTrue(m_a02.evaluate_ospf_area_policy(10, "totally_nssa")["auto_default_route"])
        self.assertEqual(
            m_a02.select_ospf_path([
                {"name": "Inter", "code": "O IA", "internal_cost": 5},
                {"name": "Intra", "code": "O", "internal_cost": 999},
            ])["winner"],
            "Intra",
        )
        with self.assertRaises(ValueError):
            m_a02.evaluate_ospf_area_policy(10, "nssa", nssa_default_info_originate="True")

        # 3. adv_03: vrf forwarding strips existing IP, IP SLA detects indirect WAN outage, NetFlow 5-tuple
        m_a03 = load_module(AGENT3_LAB_DIR / "adv_03_lab.py", "adv_03_p12c")
        res_vrf = m_a03.apply_vrf_forwarding("Gi0/0.20", "192.168.10.1/24", "GUEST", {}, None)
        self.assertTrue(res_vrf["previous_ip_stripped_by_ios"])
        self.assertIsNone(res_vrf["active_ip"])
        self.assertEqual(
            m_a03.evaluate_ip_sla_failover(True, False, True, "udp-jitter", False)["active_path"],
            "INVALID_PROBE_CONFIG",
        )
        with self.assertRaises(ValueError):
            m_a03.evaluate_ip_sla_failover("True", False, True)

        # 4. adv_04: GRE 1476/1436, GRE+IPsec 1400/1360, IOS vs Linux/Win DF ping sizes, PMTUD & Asymmetric FW/uRPF
        m_a04 = load_module(AGENT3_LAB_DIR / "adv_04_lab.py", "adv_04_p12c")
        gre = m_a04.compute_tunnel_mtu_mss(1500, "gre_ipv4")
        self.assertEqual((gre["ip_mtu"], gre["ip_tcp_adjust_mss"], gre["linux_win_ping_df_payload"]), (1476, 1436, 1448))
        self.assertEqual(m_a04.simulate_pmtud_packet(1500, 1476, True, False)["outcome"], "PMTUD_BLACKHOLE_HANG")
        self.assertFalse(m_a04.evaluate_asymmetric_flow("FW-A", "FW-B", False)["tcp_established"])
        with self.assertRaises(ValueError):
            m_a04.simulate_pmtud_packet(1500, 1476, "True", False)

        # 5. adv_bfd: RFC 5880 asymmetric negotiation (max(local_rx, peer_tx)), Multihop 4784, FNF active timeout 60
        m_bfd = load_module(AGENT3_LAB_DIR / "adv_bfd_lab.py", "adv_bfd_p12c")
        self.assertEqual(m_bfd.negotiate_bfd_detection(50, 50, 3, 200, 200, 3)["r1_detects_r2_down_ms"], 600)
        self.assertEqual(m_bfd.negotiate_bfd_detection(100, 100, 3, 100, 100, 3, multihop=True)["udp_control_port"], 4784)
        self.assertEqual(m_bfd.simulate_fnf_active_timeout(1500, 60, 1500)["export_buckets"], 25)
        with self.assertRaises(ValueError):
            m_bfd.negotiate_bfd_detection(50, 50, 3, 50, 50, 3, multihop="True")

    def test_phase13_handoff_9cdaf84b_auto07_09_and_proactive_audit(self):
        """Phase 13: resolve batch-auto-07-09-intake-fa.md & ccde_18 @ 9cdaf84b4e + proactively harden auto_11/13/14."""
        import threading
        import urllib.error
        import urllib.request

        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. auto_07: non-ASCII signature ("☃") must NEVER raise TypeError; explicit educational boundary; nbf/iss/aud/RFC 8725
        a07 = load_module(AGENT3_LAB_DIR / "auto_07_lab.py", "auto_07_p13")
        secret = b"p13-test-secret"
        now_ts = 1764201600
        tok = a07.build_hs256_jwt_demo(
            {"iss": "https://idp.example", "aud": ["api-a", "api-b"], "sub": "bot", "nbf": now_ts - 10, "exp": now_ts + 600},
            secret,
        )
        h, p, s = tok.split(".")
        snowman_res = a07.evaluate_hs256_jwt_demo(f"{h}.{p}.☃", secret, now_ts=now_ts)
        self.assertFalse(snowman_res["demo_checks_passed"])
        self.assertEqual(snowman_res["reason"], "malformed_signature_encoding")
        self.assertTrue(snowman_res["not_production_jwt_verifier"])
        self.assertNotIn("valid", snowman_res)
        self.assertIn("jwks_kid_key_rotation", snowman_res["checks_not_implemented"])

        # Future nbf & mismatched iss/aud rejected cleanly
        future_nbf_tok = a07.build_hs256_jwt_demo({"sub": "bot", "nbf": now_ts + 300, "exp": now_ts + 600}, secret)
        self.assertEqual(a07.evaluate_hs256_jwt_demo(future_nbf_tok, secret, now_ts=now_ts)["reason"], "token_not_yet_valid_nbf")
        self.assertEqual(
            a07.evaluate_hs256_jwt_demo(tok, secret, now_ts=now_ts, expected_iss="https://other.example")["reason"],
            "invalid_issuer",
        )
        self.assertEqual(
            a07.evaluate_hs256_jwt_demo(tok, secret, now_ts=now_ts, expected_aud="api-z")["reason"],
            "invalid_audience",
        )
        self.assertTrue(
            a07.evaluate_hs256_jwt_demo(tok, secret, now_ts=now_ts, expected_iss="https://idp.example", expected_aud="api-b")["demo_checks_passed"]
        )
        # IP literal wildcard rejected in SAN match
        self.assertFalse(a07.verify_san_match("10.0.0.1", ["*.0.0.1"]))
        # Prose regression: RFC 8725 cited and revocation explicitly client/policy dependent
        bp07_txt = (BLUEPRINT_DIR / "auto_07.json").read_text(encoding="utf-8")
        self.assertIn("RFC 8725", bp07_txt)
        self.assertIn("یکسان و همگانی نیست", bp07_txt)

        # 2. auto_08: byte-oriented RFC 6242 chunking splits multi-byte UTF-8 ('سلام') cleanly on 1-byte chunks
        a08 = load_module(AGENT3_LAB_DIR / "auto_08_lab.py", "auto_08_p13")
        framed_persian = a08.frame_netconf_1_1_chunked("سلام", chunk_size=1)
        self.assertIsInstance(framed_persian, bytes)
        self.assertEqual(a08.parse_netconf_1_1_chunked(framed_persian), "سلام")
        # Leading zero, truncated body, missing terminator, trailing bytes, invalid UTF-8 all raise ValueError
        for bad_frame in (
            b"\n#04\nabcd\n##\n",
            b"\n#10\nabc\n##\n",
            b"\n#3\nabc",
            b"\n#3\nabc\n##\nextra",
            b"\n##\n",
            b"\n#2\n\xff\xfe\n##\n",
        ):
            with self.assertRaises(ValueError):
                a08.parse_netconf_1_1_chunked(bad_frame)

        # 3. auto_09: per-server isolated state, POST /wrong -> 404 (no mutation), application/json -> 415, Accept -> 406, body cap -> 413
        a09 = load_module(AGENT3_LAB_DIR / "auto_09_lab.py", "auto_09_p13")
        srv = a09.EducationalRestconfServer(("127.0.0.1", 0), a09.RestconfHandler, max_body_bytes=256)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            base = f"http://127.0.0.1:{port}"
            payload = json.dumps({"ietf-interfaces:interface": [{"name": "Loopback99", "enabled": True}]}).encode("utf-8")

            # POST /wrong with application/json MUST NOT mutate store (404)
            req_wrong = urllib.request.Request(
                f"{base}/wrong",
                data=payload,
                headers={"Content-Type": "application/json", "Accept": a09.YANG_JSON},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx_wrong:
                urllib.request.urlopen(req_wrong, timeout=5)
            self.assertEqual(ctx_wrong.exception.code, 404)
            self.assertNotIn("Loopback99", srv.config_store)

            # Valid collection path with wrong Content-Type: application/json -> 415 (no mutation)
            req_415 = urllib.request.Request(
                f"{base}{a09.COLLECTION_PATH}",
                data=payload,
                headers={"Content-Type": "application/json", "Accept": a09.YANG_JSON},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx_415:
                urllib.request.urlopen(req_415, timeout=5)
            self.assertEqual(ctx_415.exception.code, 415)
            self.assertNotIn("Loopback99", srv.config_store)

            # Oversized body -> 413 Payload Too Large
            big_payload = json.dumps({"ietf-interfaces:interface": [{"name": "Loopback99", "description": "x" * 400}]}).encode("utf-8")
            req_413 = urllib.request.Request(
                f"{base}{a09.COLLECTION_PATH}",
                data=big_payload,
                headers={"Content-Type": a09.YANG_JSON, "Accept": a09.YANG_JSON},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx_413:
                urllib.request.urlopen(req_413, timeout=5)
            self.assertEqual(ctx_413.exception.code, 413)

            # Incompatible Accept -> 406
            req_406 = urllib.request.Request(f"{base}{a09.COLLECTION_PATH}", headers={"Accept": "text/plain"})
            with self.assertRaises(urllib.error.HTTPError) as ctx_406:
                urllib.request.urlopen(req_406, timeout=5)
            self.assertEqual(ctx_406.exception.code, 406)
        finally:
            srv.shutdown()
            t.join(timeout=5)
            srv.server_close()

        # 4. ccde_18: unhashable profile (list/dict) raises ValueError (not TypeError) + Broadcom KB 326979 scoped to data sites
        c18 = load_module(AGENT3_LAB_DIR / "ccde_18_lab.py", "ccde_18_p13")
        sample_design = {
            "dc_distance_km": 5000,
            "storage_replication": "asynchronous",
            "target_rpo_minutes": 15,
            "dci_l2_stretched": False,
            "gslb_enabled": True,
            "wan_model": "regional_sdwan_sase",
            "cloud_hub": "dual_colo_exchange",
            "macro_vrfs": 4,
            "micro_sgt_enabled": True,
            "eu_residency_policy_enforced": True,
            "eu_personal_data_transferred_outside_eea": False,
            "encryption_in_transit_assumed": True,
        }
        for bad_prof in ([], {}, 123, None):
            with self.assertRaises(ValueError):
                c18.validate_pars_global_hld(sample_design, sync_product_profile=bad_prof)
        self.assertIn("326979", (BLUEPRINT_DIR / "ccde_18.json").read_text(encoding="utf-8"))

        # 5. Proactive audit: auto_11 isolated state + element validation; auto_13 unhashable device/fail_on; auto_14 strict GET path & bad query
        a11 = load_module(AGENT3_LAB_DIR / "auto_11_lab.py", "auto_11_p13")
        with self.assertRaises(ValueError):
            a11.run_ios_config_task("core_routers", [123], ["description OK"], device_state=a11.build_initial_device_state())
        a13 = load_module(AGENT3_LAB_DIR / "auto_13_lab.py", "auto_13_p13")
        nso = a13.NsoOrchestratorMock()
        with self.assertRaises(ValueError):
            nso.commit_service("VRF1", "65000:1", fail_on_device=[])
        with self.assertRaises(ValueError):
            nso.check_sync({})
        a14 = load_module(AGENT3_LAB_DIR / "auto_14_lab.py", "auto_14_p13")
        cat_srv = a14.MockCatalystServer(("127.0.0.1", 0), a14.MockCatalystCenter)
        cat_port = cat_srv.server_address[1]
        cat_t = threading.Thread(target=cat_srv.serve_forever, daemon=True)
        cat_t.start()
        try:
            with self.assertRaises(urllib.error.HTTPError) as ctx_cat404:
                urllib.request.urlopen(
                    urllib.request.Request(f"http://127.0.0.1:{cat_port}/wrong", headers={"X-Auth-Token": "mock-dna-token-123"}),
                    timeout=5,
                )
            self.assertEqual(ctx_cat404.exception.code, 404)
            with self.assertRaises(urllib.error.HTTPError) as ctx_cat400:
                urllib.request.urlopen(
                    urllib.request.Request(
                        f"http://127.0.0.1:{cat_port}{a14.DEVICES_PATH}?offset=abc&limit=2",
                        headers={"X-Auth-Token": "mock-dna-token-123"},
                    ),
                    timeout=5,
                )
            self.assertEqual(ctx_cat400.exception.code, 400)
        finally:
            cat_srv.shutdown()
            cat_t.join(timeout=5)
            cat_srv.server_close()

    def test_phase14_handoff_ffd6a320_auto07_09_and_ccna_fixes(self):
        """Phase 14: resolve remaining findings in AGENT-HANDOFF-fa.md & batch-auto-07-09-intake-fa.md @ ffd6a320ca."""
        import socket
        import threading
        import time
        import urllib.error
        import urllib.request

        def load_module(path: Path, mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, path)
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. auto_07: 1100-level nested JSON never raises RecursionError; checks_configured vs checks_executed
        a07 = load_module(AGENT3_LAB_DIR / "auto_07_lab.py", "auto_07_p14")
        secret = b"p14-secret"
        now_ts = 1764201600
        tok = a07.build_hs256_jwt_demo({"sub": "u", "exp": now_ts + 600}, secret)
        h, p, s = tok.split(".")
        deep_p = a07.b64url_encode(('{"a":' * 1100 + "1" + "}" * 1100).encode("ascii"))
        deep_res = a07.evaluate_hs256_jwt_demo(f"{h}.{deep_p}.{s}", secret, now_ts=now_ts)
        self.assertFalse(deep_res["demo_checks_passed"])
        self.assertEqual(deep_res["reason"], "malformed_jwt_encoding_or_json")
        self.assertNotIn("checks_performed", deep_res)
        self.assertIn("checks_configured", deep_res)
        self.assertIn("checks_executed", deep_res)
        # Early failure must NOT claim later steps (signature/exp) were executed
        self.assertNotIn("hmac_sha256_bytes_constant_time", deep_res["checks_executed"])
        self.assertNotIn("exp_required_and_unexpired", deep_res["checks_executed"])
        self.assertFalse(a07.verify_san_match("foo.netops.example", ["f*.netops.example"]))
        self.assertFalse(a07.verify_san_match("a.b.netops.example", ["*.*.netops.example"]))
        self.assertIn("RFC 8470", (BLUEPRINT_DIR / "auto_07.json").read_text(encoding="utf-8"))

        # 2. auto_08: unlocked session_id=None cannot bypass lock; overlapping confirmed-commit rejected; session-id in prose
        a08 = load_module(AGENT3_LAB_DIR / "auto_08_lab.py", "auto_08_p14")
        ds = a08.NetconfDatastoreMock()
        with self.assertRaises((ValueError, RuntimeError)):
            ds.edit_candidate(None, ["permit 10.0.0.0/24"])
        with self.assertRaises((ValueError, RuntimeError)):
            ds.commit_confirmed(None)
        ds.lock("s1")
        ds.edit_candidate("s1", ["permit 10.1.0.0/24"])
        ds.commit_confirmed("s1")
        with self.assertRaises(RuntimeError):
            ds.commit_confirmed("s1")  # overlapping pending confirmed-commit must fail
        bp08_txt = (BLUEPRINT_DIR / "auto_08.json").read_text(encoding="utf-8")
        self.assertNotIn("lock-id", bp08_txt)
        self.assertIn("session-id", bp08_txt)

        # 3. auto_09: Accept q=0 -> 406, stalled half-body client times out (408) & shutdown completes cleanly
        a09 = load_module(AGENT3_LAB_DIR / "auto_09_lab.py", "auto_09_p14")
        self.assertFalse(a09.accept_allows_yang_json(f"{a09.YANG_JSON};q=0"))
        self.assertFalse(a09.accept_allows_yang_json(f"{a09.YANG_JSON};q=0, */*;q=0.5"))
        self.assertFalse(a09.accept_allows_yang_json("*/*;q=0"))
        self.assertTrue(a09.accept_allows_yang_json(f"{a09.YANG_JSON};q=0.8"))

        srv = a09.EducationalRestconfServer(("127.0.0.1", 0), a09.RestconfHandler, request_timeout_sec=0.25)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            base = f"http://127.0.0.1:{port}"
            for bad_accept in (f"{a09.YANG_JSON};q=0", f"{a09.YANG_JSON};q=0, */*;q=0.5", "*/*;q=0"):
                with self.assertRaises(urllib.error.HTTPError) as ctx_406:
                    urllib.request.urlopen(
                        urllib.request.Request(f"{base}{a09.COLLECTION_PATH}", headers={"Accept": bad_accept}),
                        timeout=5,
                    )
                self.assertEqual(ctx_406.exception.code, 406)

            # Stalled half-body client must receive 408 timeout and MUST NOT hang server or mutate store
            with socket.create_connection(("127.0.0.1", port), timeout=3.0) as sock:
                sock.settimeout(3.0)
                partial_req = (
                    f"POST {a09.COLLECTION_PATH} HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Content-Type: {a09.YANG_JSON}\r\n"
                    f"Accept: {a09.YANG_JSON}\r\n"
                    f"Content-Length: 200\r\n"
                    f"\r\n"
                    "{\"ietf"
                ).encode("ascii")
                sock.sendall(partial_req)
                resp_head = sock.recv(512).decode("latin1")
            self.assertIn("408", resp_head)
            self.assertEqual(list(srv.config_store.keys()), ["GigabitEthernet1"])

            # Malformed percent-encoding in item URI -> 404
            with self.assertRaises(urllib.error.HTTPError) as ctx_pct:
                urllib.request.urlopen(
                    urllib.request.Request(f"{base}{a09.ITEM_PREFIX}Loopback%ZZ", headers={"Accept": a09.YANG_JSON}),
                    timeout=5,
                )
            self.assertEqual(ctx_pct.exception.code, 404)
        finally:
            t0 = time.monotonic()
            srv.shutdown()
            t.join(timeout=5)
            srv.server_close()
            self.assertLess(time.monotonic() - t0, 2.0)

        # 4. ccna_02_vlan, ccna_v1, ccna_v6 sync fixes from ffd6a320ca
        bp_vlan_txt = (BLUEPRINT_DIR / "ccna_02_vlan.json").read_text(encoding="utf-8")
        self.assertNotIn("تگ ۴بیتی", bp_vlan_txt)
        self.assertTrue("تگ ۴ بایتی" in bp_vlan_txt or "تگ ۴بایتی" in bp_vlan_txt)
        m_vlan = load_module(AGENT3_LAB_DIR / "ccna_02_vlan_lab.py", "ccna_02_vlan_p14")
        with self.assertRaises(ValueError):
            m_vlan.evaluate_dtp_link([], "trunk")
        missing_nat = m_vlan.audit_trunk_pair([1, 10], [1, 10, 999], [10, 999], [10, 999], 999, 999, [10])
        self.assertFalse(missing_nat["model_checks_ok"])
        self.assertTrue(any("SW1_NATIVE_MISSING" in i for i in missing_nat["issues"]))

        bp_v6_txt = (BLUEPRINT_DIR / "ccna_v6.json").read_text(encoding="utf-8")
        self.assertIn("Policy-Based Routing", bp_v6_txt)
        self.assertIn("FIB", bp_v6_txt)

    def test_all_agent3_lab_scripts_execute_cleanly(self):
        scripts = sorted(AGENT3_LAB_DIR.glob("*_lab.py"))
        self.assertEqual(len(scripts), 99)
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
