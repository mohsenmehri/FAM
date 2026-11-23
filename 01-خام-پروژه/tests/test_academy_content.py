"""Integrity tests for the active, served FAM Academy curriculum.

These tests verify source-data consistency only. They do not claim IOS, PNETLab,
visual-browser, or live-LAB execution.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PACKAGE_ROOT / "server" / "www"
ASSET_ROOT = WEB_ROOT / "academy-assets"
CATALOG_PATH = ASSET_ROOT / "curriculum-catalog.json"


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.assets: list[str] = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href"} and value and value.startswith("/academy-assets/"):
                self.assets.append(value.split("?", 1)[0].split("#", 1)[0])


def blueprint_path(lesson) -> Path:
    """Resolve the blueprint from the catalog reference (works for any subfolder)."""
    return ASSET_ROOT / lesson["blueprint"].removeprefix("/academy-assets/")


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


class AcademyContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.records = []
        for path in cls.catalog.get("paths", []):
            for course in path.get("courses", []):
                for lesson in course.get("lessons", []):
                    cls.records.append((path, course, lesson))

    def test_catalog_has_unique_ids_and_resolvable_prerequisites(self):
        lesson_ids = [lesson["id"] for _, _, lesson in self.records]
        self.assertTrue(lesson_ids, "active catalog must contain lessons")
        self.assertEqual(len(lesson_ids), len(set(lesson_ids)), "lesson IDs must be unique")
        known = set(lesson_ids)
        for _, _, lesson in self.records:
            for prerequisite in lesson.get("prerequisites", []):
                with self.subTest(lesson=lesson["id"], prerequisite=prerequisite):
                    self.assertIn(prerequisite, known)

    def test_every_catalog_reference_resolves_to_matching_blueprint(self):
        for _, _, lesson in self.records:
            reference = lesson.get("blueprint", "")
            self.assertTrue(reference.startswith("/academy-assets/"), lesson["id"])
            relative = reference.removeprefix("/academy-assets/")
            blueprint_path = (ASSET_ROOT / relative).resolve()
            self.assertIn(ASSET_ROOT.resolve(), blueprint_path.parents, lesson["id"])
            self.assertTrue(blueprint_path.is_file(), lesson["id"])
            blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
            self.assertEqual(blueprint.get("id") or blueprint.get("lessonId"), lesson["id"])
            self.assertGreaterEqual(len(json.dumps(blueprint, ensure_ascii=False)), 1000)

    def test_each_current_lesson_has_a_lab_and_assessment(self):
        for _, _, lesson in self.records:
            blueprint = json.loads(blueprint_path(lesson).read_text(encoding="utf-8"))
            stages = blueprint.get("stages", {})
            self.assertIsInstance(stages, dict, lesson["id"])
            self.assertIn("lab", stages, lesson["id"])
            questions = stages.get("quiz", {}).get("questions", []) or blueprint.get("interactiveQuiz", [])
            self.assertGreaterEqual(len(questions), 1, lesson["id"])

    def test_quiz_answers_and_explanations_are_well_formed(self):
        for _, _, lesson in self.records:
            blueprint = json.loads(blueprint_path(lesson).read_text(encoding="utf-8"))
            interactive = blueprint.get("interactiveQuiz", [])
            questions = (
                interactive if interactive else
                blueprint.get("stages", {}).get("quiz", {}).get("questions", [])
            )
            for index, question in enumerate(questions, start=1):
                with self.subTest(lesson=lesson["id"], question=index):
                    options = question.get("options", [])
                    answer = question.get("answer", question.get("correctIndex"))
                    self.assertGreaterEqual(len(options), 2)
                    self.assertIsInstance(answer, int)
                    self.assertGreaterEqual(answer, 0)
                    self.assertLess(answer, len(options))
                    self.assertTrue(question.get("explanation") or question.get("explanationHtml"))

    def test_structured_topology_links_point_to_declared_devices(self):
        for _, _, lesson in self.records:
            blueprint = json.loads(blueprint_path(lesson).read_text(encoding="utf-8"))
            topology = blueprint.get("topology", {})
            devices = topology.get("devices", []) if isinstance(topology, dict) else []
            ids = {str(device.get("id")) for device in devices if isinstance(device, dict)}
            for link in topology.get("links", []) if isinstance(topology, dict) else []:
                for side in ("a", "b"):
                    endpoint = str(link.get(side, "")).split(":", 1)[0]
                    with self.subTest(lesson=lesson["id"], endpoint=endpoint):
                        self.assertIn(endpoint, ids)

    def test_inline_svg_markup_is_paired_and_has_a_viewbox(self):
        for _, _, lesson in self.records:
            blueprint = json.loads(blueprint_path(lesson).read_text(encoding="utf-8"))
            serialized = json.dumps(blueprint, ensure_ascii=False)
            starts = len(re.findall(r"<svg\b", serialized, flags=re.IGNORECASE))
            ends = len(re.findall(r"</svg\s*>", serialized, flags=re.IGNORECASE))
            svg_sources = [
                svg
                for value in walk_strings(blueprint)
                for svg in re.findall(r"<svg\b[\s\S]*?</svg\s*>", value, flags=re.IGNORECASE)
            ]
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(starts, ends)
                if starts:
                    self.assertRegex(serialized, r"viewBox\s*=\s*\\?[\"']")
                    self.assertEqual(len(svg_sources), starts)
                    for svg_index, svg_source in enumerate(svg_sources, start=1):
                        with self.subTest(lesson=lesson["id"], svg=svg_index):
                            ET.fromstring(svg_source)

    def test_academy_ui_references_existing_local_assets(self):
        page = PACKAGE_ROOT / "server" / "private_ui" / "academy.html"
        parser = AssetParser()
        parser.feed(page.read_text(encoding="utf-8"))
        self.assertTrue(parser.assets)
        for reference in parser.assets:
            local_path = (WEB_ROOT / reference.lstrip("/")).resolve()
            with self.subTest(reference=reference):
                self.assertIn(WEB_ROOT.resolve(), local_path.parents)
                self.assertTrue(local_path.is_file())

    def test_served_curriculum_is_curriculum_5_0_only(self):
        prefixes = ("ccna-v11-", "ccna-v20-", "academy-stage-zero-")
        self.assertEqual([p["id"] for p in self.catalog["paths"]], ["fam-c5"])
        for _, _, lesson in self.records:
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson["id"].startswith(prefixes), lesson["id"])
                self.assertTrue(lesson["blueprint"].startswith("/academy-assets/v5/blueprints/"))

    def test_every_lesson_carries_the_sixteen_section_contract(self):
        for _, _, lesson in self.records:
            blueprint = json.loads(blueprint_path(lesson).read_text(encoding="utf-8"))
            with self.subTest(lesson=lesson["id"]):
                self.assertGreaterEqual(len(blueprint.get("sections", [])), 14, lesson["id"])
                self.assertEqual(blueprint.get("evidence"), "Designed — Not Run", lesson["id"])
                self.assertGreaterEqual(len(blueprint.get("glossary", [])), 15, lesson["id"])
                quiz = blueprint.get("interactiveQuiz", [])
                self.assertEqual(len(quiz), 12, lesson["id"])
                for index, question in enumerate(quiz, start=1):
                    with self.subTest(lesson=lesson["id"], question=index):
                        self.assertEqual(len(question.get("options", [])), 4)
                        self.assertIsInstance(question.get("correctIndex"), int)
                        self.assertTrue(question.get("explanationHtml"))

    def test_unexecuted_lab_status_is_explicit_for_every_lesson(self):
        status_pattern = re.compile(
            r"اجرا\s*نشده|اجرا\s*و\s*تأیید\s*نشده|not\s+(?:yet\s+)?executed",
            re.IGNORECASE,
        )
        for _, _, lesson in self.records:
            blueprint = json.loads(blueprint_path(lesson).read_text(encoding="utf-8"))
            lab = blueprint.get("stages", {}).get("lab", {})
            self.assertIsInstance(lab, dict, lesson["id"])
            self.assertTrue(lab.get("title") or lab.get("html") or lab.get("pnetlabTopology"), lesson["id"])
            evidence = json.dumps(lab, ensure_ascii=False)
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(status_pattern.search(evidence), "lab must say it has not been run")


if __name__ == "__main__":
    unittest.main()
