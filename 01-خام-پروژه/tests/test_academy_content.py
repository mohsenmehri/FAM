"""FAM Academy v2 content and UI contract tests.

The legacy curriculum-catalog/blueprint tests were replaced because that content
was intentionally retired. This suite validates the versioned v1 curriculum,
independent manifest, links, RTL shell, pure engine, preview server and the
preservation of the 143 prior deletions. It uses only stdlib and Node's syntax
checker; no Flask, jsonschema, browser or network dependency is required.
"""
from __future__ import annotations

import ast
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PACKAGE_ROOT / "tools"
WEB_ROOT = PACKAGE_ROOT / "server" / "www"
ASSETS = WEB_ROOT / "academy-assets"
CONTENT = WEB_ROOT / "academy-content"
V1 = CONTENT / "v1"
PRIVATE_UI = PACKAGE_ROOT / "server" / "private_ui"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))
import validate_academy_v2 as validator  # noqa: E402

VALIDATION = validator.validate(PACKAGE_ROOT)
CATALOG = json.loads((V1 / "catalog.json").read_text(encoding="utf-8"))
EXERCISES = json.loads((V1 / "exercises.json").read_text(encoding="utf-8"))["exercises"]
REFERENCES = json.loads((V1 / "references.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((V1 / "manifest.json").read_text(encoding="utf-8"))


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.assets: list[str] = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href"} and value and value.startswith(("/academy-assets/", "/academy-content/")):
                self.assets.append(value.split("?", 1)[0].split("#", 1)[0])


def web_file(web: str) -> Path:
    if web.startswith("/academy-assets/"):
        return ASSETS / web[len("/academy-assets/"):]
    if web.startswith("/academy-content/"):
        return CONTENT / web[len("/academy-content/"):]
    raise ValueError(web)


def all_json_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from all_json_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_json_strings(child)


class AcademyV2ContentTests(unittest.TestCase):
    def test_validator_reports_no_errors(self):
        self.assertTrue(VALIDATION["ok"], "\n".join(VALIDATION["errors"]))
        self.assertGreaterEqual(len(VALIDATION["checks"]), 14)

    def test_catalog_counts_and_version_contract(self):
        self.assertEqual(CATALOG["schemaVersion"], "fam-academy-v1")
        self.assertEqual(CATALOG["contentVersion"], "2026.11.24-p0")
        self.assertEqual(CATALOG["language"], "fa")
        self.assertEqual(CATALOG["direction"], "rtl")
        self.assertEqual(CATALOG["storageKey"], "famAcademyV2.progress.v1")
        counts = VALIDATION["counts"]
        self.assertEqual(counts["paths"], 23)
        self.assertEqual(counts["courses"], 23)
        self.assertEqual(counts["liveCourses"], 5)
        self.assertEqual(counts["plannedCourses"], 18)
        self.assertEqual(counts["lessons"], 10)
        self.assertEqual(counts["simulations"], 3)
        self.assertEqual(counts["labs"], 2)
        self.assertEqual(counts["exercises"], 10)

    def test_paths_have_unique_ids_sequential_order_and_valid_relations(self):
        paths = CATALOG["paths"]
        ids = {p["id"] for p in paths}
        self.assertEqual(len(ids), 23)
        self.assertEqual([p["order"] for p in paths], list(range(1, 24)))
        by_id = {p["id"]: p for p in paths}
        for p in paths:
            self.assertGreaterEqual(len(p["objectives"]), 3)
            self.assertTrue(p["prerequisites"] or p["id"] == "p01-network-fundamentals")
            for q in p["prerequisites"]:
                self.assertIn(q, ids)
                self.assertLess(by_id[q]["order"], p["order"])
            for q in p["nextPaths"]:
                self.assertIn(q, ids)
                self.assertGreater(by_id[q]["order"], p["order"])

    def test_live_courses_are_connected_to_lessons_and_clearly_distinguished_from_roadmap(self):
        lesson_ids = {l["id"] for l in CATALOG["lessons"]}
        live = [c for c in CATALOG["courses"] if c["status"] == "live"]
        planned = [c for c in CATALOG["courses"] if c["status"] == "planned"]
        self.assertEqual(len(live), 5)
        self.assertEqual(len(planned), 18)
        for c in live:
            self.assertTrue(c.get("objectives"))
            self.assertTrue(c.get("prerequisites") or c["id"] == "c01-network-fundamentals")
            referenced = [lid for ch in c["chapters"] for lid in ch.get("lessonIds", [])]
            self.assertTrue(referenced)
            self.assertTrue(set(referenced) <= lesson_ids)
        for c in planned:
            self.assertEqual(c["status"], "planned")
            self.assertTrue(all(ch["status"] == "planned" for ch in c["chapters"]))

    def test_every_lesson_has_sixteen_non_empty_sections_and_unique_core_text(self):
        required = {
            "concept", "deepDive", "diagram", "realExample", "scenario", "commands",
            "commandWalkthrough", "sampleOutput", "commonMistakes", "troubleshooting",
            "keyPoints", "versionNotes", "summary", "references", "quiz", "nextSteps",
        }
        concepts, deeps, summaries = [], [], []
        for summary in CATALOG["lessons"]:
            lesson = json.loads((V1 / "lessons" / (summary["id"] + ".json")).read_text(encoding="utf-8"))
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(lesson["status"], "live")
                self.assertGreaterEqual(lesson["durationMinutes"], 20)
                self.assertGreaterEqual(len(lesson["objectives"]), 3)
                sections = lesson["sections"]
                self.assertTrue(required <= set(sections))
                self.assertEqual(len(sections), 16)
                for key, section in sections.items():
                    self.assertTrue(section.get("title"), key)
                    self.assertTrue(section.get("body"), key)
                self.assertIn("Sample", sections["sampleOutput"]["label"])
                self.assertIn("Simulated", sections["sampleOutput"]["label"])
                self.assertTrue(sections["sampleOutput"]["lines"])
                concepts.append(sections["concept"]["body"][0])
                deeps.append(sections["deepDive"]["body"][0])
                summaries.append(sections["summary"]["body"][0])
        for values in (concepts, deeps, summaries):
            self.assertEqual(len(set(values)), 10, "filler or duplicate lesson text detected")

    def test_quiz_answers_options_explanations_and_api_paths_are_valid(self):
        for summary in CATALOG["lessons"]:
            lesson = json.loads((V1 / "lessons" / (summary["id"] + ".json")).read_text(encoding="utf-8"))
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(lesson["apiPath"], "/api/academy/v2/lesson/" + lesson["id"])
                self.assertGreaterEqual(len(lesson["quiz"]), 3)
                for q in lesson["quiz"]:
                    self.assertGreaterEqual(len(q["options"]), 2)
                    self.assertIsInstance(q["answerIndex"], int)
                    self.assertGreaterEqual(q["answerIndex"], 0)
                    self.assertLess(q["answerIndex"], len(q["options"]))
                    self.assertTrue(q["explanation"])
                for ref in lesson["references"]:
                    self.assertIn(ref, REFERENCES)
                self.assertIn(lesson["exerciseId"], {e["id"] for e in EXERCISES})

    def test_all_web_paths_and_declared_assets_resolve_inside_versioned_tree(self):
        for p in sorted(V1.rglob("*.json")):
            text = p.read_text(encoding="utf-8")
            for match in re.findall(r"/academy-(?:content|assets)/[A-Za-z0-9_./-]+", text):
                target = web_file(match.rstrip(".,;:)\"'"))
                with self.subTest(file=p.relative_to(V1).as_posix(), path=match):
                    self.assertTrue(target.is_file(), match)
                    self.assertIn(WEB_ROOT.resolve(), target.resolve().parents)

    def test_all_generated_diagrams_are_well_formed_svg(self):
        diagrams = sorted((V1 / "assets" / "diagrams").glob("*.svg"))
        self.assertGreaterEqual(len(diagrams), 10)
        for diagram in diagrams:
            with self.subTest(diagram=diagram.name):
                root = ET.fromstring(diagram.read_text(encoding="utf-8"))
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertIn("viewBox", root.attrib)
                self.assertNotIn("<script", diagram.read_text(encoding="utf-8").lower())

    def test_simulations_use_known_engine_logic_and_declare_limits(self):
        expected = {"arpResolve", "vlanForward", "ospfAdjacency"}
        for sim in CATALOG["simulations"]:
            data = json.loads((V1 / "simulations" / (sim["id"] + ".json")).read_text(encoding="utf-8"))
            with self.subTest(sim=data["id"]):
                self.assertIn(data["logic"], expected)
                self.assertGreaterEqual(len(data["parameters"]), 3)
                self.assertGreaterEqual(len(data["steps"]), 4)
                self.assertTrue(data["limitations"])
                self.assertTrue(web_file(data["diagramPath"]).is_file())
                self.assertTrue(data["lessonIds"])

    def test_labs_are_designed_for_internal_simulator_only(self):
        for lab in CATALOG["labs"]:
            data = json.loads((V1 / "labs" / (lab["id"] + ".json")).read_text(encoding="utf-8"))
            with self.subTest(lab=data["id"]):
                self.assertEqual(data["executionMode"], "internal-simulator")
                self.assertIs(data["realDeviceConnection"], False)
                self.assertFalse(data["futureIntegration"]["enabled"])
                self.assertGreaterEqual(len(data["steps"]), 5)
                self.assertTrue(data["addressingTable"])
                self.assertTrue(data["reviewQuestions"])
                self.assertTrue(data["failureScenario"])
                self.assertTrue(data["troubleshooting"])
                self.assertTrue(data["successCriteria"])
                self.assertIn("Sample", data["expectedOutput"]["label"])
                self.assertIn("Simulated", data["expectedOutput"]["label"])

    def test_independent_manifest_matches_every_generated_file(self):
        files = []
        for p in sorted(V1.rglob("*")):
            if p.is_file() and p.name != "manifest.json":
                files.append({"path": p.relative_to(V1).as_posix(), "size": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
        self.assertEqual(MANIFEST["fileCount"], len(files))
        manifest_map = {f["path"]: f for f in MANIFEST["files"]}
        for f in files:
            self.assertEqual(manifest_map[f["path"]]["sha256"], f["sha256"], f["path"])
            self.assertEqual(manifest_map[f["path"]]["size"], f["size"], f["path"])
        aggregate = hashlib.sha256(("\n".join(f"{f['size']}|{f['sha256']}|{f['path']}" for f in files)).encode()).hexdigest()
        self.assertEqual(MANIFEST["aggregateSha256"], aggregate)

    def test_root_manifest_is_unchanged_and_deleted_legacy_paths_are_not_restored(self):
        root_manifest = PACKAGE_ROOT / "MANIFEST.sha256"
        self.assertEqual(
            hashlib.sha256(root_manifest.read_bytes()).hexdigest(),
            "4e6e209a453aa48b1d5390151d3b8ed4654605977c43f66dd5cd0556c04365d3",
        )
        for legacy in (
            CONTENT / "catalog.json",
            ASSETS / "curriculum-catalog.json",
            ASSETS / "v5" / "blueprints",
        ):
            self.assertFalse(legacy.exists(), legacy)
        self.assertFalse([p for p in CONTENT.iterdir() if p.is_file()], "no unversioned content files allowed")

    def test_html_shell_is_rtl_responsive_and_references_existing_v2_assets(self):
        html = (PRIVATE_UI / "academy.html").read_text(encoding="utf-8")
        self.assertIn('lang="fa"', html)
        self.assertIn('dir="rtl"', html)
        self.assertIn('name="viewport"', html)
        self.assertEqual(html.count("__FAM_CSP_NONCE__"), 1)
        self.assertEqual(html.count("__FAM_ACADEMY_BOOTSTRAP__"), 1)
        self.assertNotIn("curriculum-catalog.json", html)
        parser = AssetParser()
        parser.feed(html)
        self.assertTrue(parser.assets)
        for asset in parser.assets:
            with self.subTest(asset=asset):
                self.assertTrue(web_file(asset).is_file())
        for required in ("academy-engine.js", "academy-v2.js", "academy-v2.css", "academy-reference-ui.css", "famAcademyV2.progress.v1"):
            self.assertIn(required, html)
        self.assertIn('data-theme="dark"', html)
        self.assertIn("fam.academy.theme", html)
        self.assertIn("fam.ui.theme", html)

    def test_css_and_spa_use_responsive_rtl_and_new_versioned_api(self):
        css = (ASSETS / "academy-v2.css").read_text(encoding="utf-8")
        js = (ASSETS / "academy-v2.js").read_text(encoding="utf-8")
        engine = (ASSETS / "academy-engine.js").read_text(encoding="utf-8")
        self.assertIn("direction: rtl", css)
        self.assertIn("@media", css)
        self.assertEqual(css.count("{"), css.count("}"))
        self.assertIn("/api/academy/v2/catalog", js)
        self.assertIn("famAcademyV2.progress.v1", js)
        for route in ("#/dashboard", "#/paths", "#/progress", "#/course/", "#/lesson/", "#/sim/", "#/lab/", "#/quiz/"):
            self.assertIn(route, js)
        for fn in ("arpResolve", "vlanForward", "ospfAdjacency", "evaluateQuiz", "createLabState", "runLabCommand"):
            self.assertIn(fn, engine)
        self.assertNotIn("fetch('http", js.lower())
        for shell in ("app-shell", "academy-section-head", "academy-menu-toggle", "theme-toggle", 'href="/app"'):
            self.assertIn(shell, js)
        self.assertIn("FAM Academy shell integration", css)
        self.assertIn('html[data-theme="light"]', css)
        self.assertTrue((ASSETS / "academy-reference-ui.css").is_file())

    def test_no_cjk_contamination_or_obvious_secret_patterns_in_new_files(self):
        cjk = re.compile(r"[\u3400-\u9fff]")
        secrets = [
            re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", re.I),
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"(?:password|passwd|secret|api[_-]?token|private[_-]?key)\s*[:=]\s*['\"][^'\"]{6,}['\"]", re.I),
        ]
        scan = list(V1.rglob("*")) + [
            PRIVATE_UI / "academy.html",
            ASSETS / "academy-v2.css",
            ASSETS / "academy-v2.js",
            ASSETS / "academy-engine.js",
            PACKAGE_ROOT / "server" / "academy_preview_server.py",
        ]
        for p in scan:
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8")
            with self.subTest(file=p.relative_to(PACKAGE_ROOT).as_posix()):
                self.assertIsNone(cjk.search(text), "unexpected CJK characters")
                for pattern in secrets:
                    self.assertIsNone(pattern.search(text), "possible secret pattern")

    def test_python_sources_and_javascript_syntax_are_valid(self):
        for p in (
            TOOLS_ROOT / "build_academy_v2_content.py",
            TOOLS_ROOT / "validate_academy_v2.py",
            PACKAGE_ROOT / "server" / "app.py",
            PACKAGE_ROOT / "server" / "academy_preview_server.py",
        ):
            with self.subTest(file=p.relative_to(PACKAGE_ROOT).as_posix()):
                ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        node = shutil.which("node")
        if node:
            for p in (ASSETS / "academy-engine.js", ASSETS / "academy-v2.js"):
                result = subprocess.run([node, "--check", str(p)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_json_schemas_are_present_and_define_required_contracts(self):
        for name in ("catalog.schema.json", "lesson.schema.json", "simulation.schema.json", "lab.schema.json"):
            schema = json.loads((V1 / "schemas" / name).read_text(encoding="utf-8"))
            with self.subTest(schema=name):
                self.assertIn("$schema", schema)
                self.assertIn("required", schema)
                self.assertIn("properties", schema)


if __name__ == "__main__":
    unittest.main(verbosity=2)
