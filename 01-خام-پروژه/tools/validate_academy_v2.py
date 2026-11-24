#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dependency-free validator for FAM Academy v2 content, links, contracts and hashes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "server" / "www"
CONTENT = WWW / "academy-content"
V1 = CONTENT / "v1"
ASSETS = WWW / "academy-assets"
PRIVATE_UI = ROOT / "server" / "private_ui"
ROOT_MANIFEST = ROOT / "MANIFEST.sha256"
ROOT_MANIFEST_BASELINE_SHA256 = "4e6e209a453aa48b1d5390151d3b8ed4654605977c43f66dd5cd0556c04365d3"
ENGINE_FUNCTIONS = {"arpResolve", "vlanForward", "ospfAdjacency"}
REQUIRED_SECTIONS = {
    "concept", "deepDive", "diagram", "realExample", "scenario", "commands",
    "commandWalkthrough", "sampleOutput", "commonMistakes", "troubleshooting",
    "keyPoints", "versionNotes", "summary", "references", "quiz", "nextSteps",
}
CJK = re.compile(r"[\u3400-\u9fff]")
WEB_PATH = re.compile(r"/academy-(?:content|assets)/[A-Za-z0-9_./-]+")
SECRET_PATTERNS = [
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", re.I),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?:password|passwd|secret|api[_-]?token|private[_-]?key)\s*[:=]\s*['\"][^'\"]{6,}['\"]", re.I),
]


def read_json(rel: str):
    return json.loads(V1.joinpath(rel).read_text(encoding="utf-8"))


def file_for_web_path(web: str) -> Path | None:
    if web.startswith("/academy-content/"):
        return CONTENT / web[len("/academy-content/"):]
    if web.startswith("/academy-assets/"):
        return ASSETS / web[len("/academy-assets/"):]
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path | None = None) -> dict:
    global ROOT, WWW, CONTENT, V1, ASSETS, PRIVATE_UI, ROOT_MANIFEST
    if root is not None:
        ROOT = Path(root).resolve()
        WWW = ROOT / "server" / "www"
        CONTENT = WWW / "academy-content"
        V1 = CONTENT / "v1"
        ASSETS = WWW / "academy-assets"
        PRIVATE_UI = ROOT / "server" / "private_ui"
        ROOT_MANIFEST = ROOT / "MANIFEST.sha256"
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    counts: dict[str, int] = {}

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    catalog = read_json("catalog.json")
    references = read_json("references.json")
    exercises = read_json("exercises.json")["exercises"]
    lessons = [read_json(f"lessons/{p.name}") for p in sorted((V1 / "lessons").glob("*.json"))]
    simulations = [read_json(f"simulations/{p.name}") for p in sorted((V1 / "simulations").glob("*.json"))]
    labs = [read_json(f"labs/{p.name}") for p in sorted((V1 / "labs").glob("*.json"))]
    manifest = read_json("manifest.json")
    checks.append("loaded catalog, references, exercises, lessons, simulations, labs and manifest")

    # Basic catalog contract
    need(catalog.get("schemaVersion") == "fam-academy-v1", "catalog.schemaVersion must be fam-academy-v1")
    need(catalog.get("language") == "fa", "catalog.language must be fa")
    need(catalog.get("direction") == "rtl", "catalog.direction must be rtl")
    need(len(catalog.get("paths", [])) == 23, "catalog must contain exactly 23 paths")
    need(len(catalog.get("courses", [])) == 23, "catalog must contain exactly 23 courses")
    need(len(catalog.get("lessons", [])) == 10, "catalog must contain exactly 10 lesson summaries")
    need(len(catalog.get("simulations", [])) == 3, "catalog must contain exactly 3 simulation summaries")
    need(len(catalog.get("labs", [])) == 2, "catalog must contain exactly 2 lab summaries")
    need(catalog.get("storageKey") == "famAcademyV2.progress.v1", "catalog storageKey must be isolated from legacy progress")
    for key in ["catalog", "lesson", "simulation", "lab", "exercises", "quiz", "progress", "health"]:
        need(key in catalog.get("api", {}), f"catalog.api.{key} is missing")
    checks.append("catalog top-level contract, API map and storage key")

    # Paths: order, prerequisites and next paths
    paths = catalog["paths"]
    path_ids = {p["id"] for p in paths}
    need(len(path_ids) == len(paths), "duplicate path IDs")
    orders = [p["order"] for p in paths]
    need(orders == list(range(1, 24)), "path.order must be 1..23 without gaps")
    by_id = {p["id"]: p for p in paths}
    for p in paths:
        need(isinstance(p.get("objectives"), list) and len(p["objectives"]) >= 3, f"path {p['id']} needs >=3 objectives")
        for q in p.get("prerequisites", []):
            need(q in path_ids, f"path {p['id']} prerequisite {q} does not exist")
            need(by_id[q]["order"] < p["order"], f"path {p['id']} prerequisite {q} must be earlier")
        for q in p.get("nextPaths", []):
            need(q in path_ids, f"path {p['id']} nextPath {q} does not exist")
            need(by_id[q]["order"] > p["order"], f"path {p['id']} nextPath {q} must be later")
    checks.append("23 paths: unique IDs, sequential order, valid prerequisites and next paths")

    # Courses and live content
    courses = catalog["courses"]
    course_ids = {c["id"] for c in courses}
    need(len(course_ids) == len(courses), "duplicate course IDs")
    live_courses = [c for c in courses if c.get("status") == "live"]
    planned_courses = [c for c in courses if c.get("status") == "planned"]
    need(len(live_courses) == 5, "expected exactly 5 live courses")
    need(len(planned_courses) == 18, "expected exactly 18 planned roadmap courses")
    warnings.append(f"{len(planned_courses)} courses are roadmap-only (P1); no weak filler lessons were generated.")
    lesson_summaries = {l["id"]: l for l in catalog["lessons"]}
    for c in courses:
        need(c["pathId"] in path_ids, f"course {c['id']} pathId invalid")
        for ch in c.get("chapters", []):
            need(ch.get("status") in {"live", "planned"}, f"chapter {ch.get('id')} lacks status")
            if ch.get("status") == "live":
                for lid in ch.get("lessonIds", []):
                    need(lid in lesson_summaries, f"chapter {ch['id']} references missing lesson {lid}")
    checks.append("23 courses: 5 live, 18 clearly marked P1; live chapter lesson links")

    # Lessons
    lesson_ids = [l["id"] for l in lessons]
    need(len(lesson_ids) == len(set(lesson_ids)) == 10, "expected 10 unique lesson files")
    need(set(lesson_ids) == set(lesson_summaries), "lesson files and catalog lesson summaries differ")
    concept_bodies, deep_bodies, summary_bodies = [], [], []
    for l in lessons:
        lid = l["id"]
        for field in ["title", "level", "durationMinutes", "objectives", "prerequisites", "sections", "references", "quiz", "diagramPath", "simulationIds", "labIds", "exerciseId", "status"]:
            need(field in l, f"lesson {lid} missing {field}")
        need(l.get("status") == "live", f"lesson {lid} status must be live")
        need(l.get("durationMinutes", 0) >= 20, f"lesson {lid} duration too short")
        need(len(l.get("objectives", [])) >= 3, f"lesson {lid} needs >=3 objectives")
        need(l.get("courseId") in course_ids, f"lesson {lid} courseId invalid")
        need(l.get("pathId") in path_ids, f"lesson {lid} pathId invalid")
        sections = l.get("sections", {})
        need(REQUIRED_SECTIONS <= set(sections), f"lesson {lid} missing required sections: {sorted(REQUIRED_SECTIONS - set(sections))}")
        for key, sec in sections.items():
            need(isinstance(sec, dict) and sec.get("title") and sec.get("body"), f"lesson {lid} section {key} is empty")
        sample = sections.get("sampleOutput", {})
        need("Sample" in sample.get("label", "") and "Simulated" in sample.get("label", ""), f"lesson {lid} sampleOutput must be labelled Sample/Simulated")
        need(bool(sample.get("lines")), f"lesson {lid} sampleOutput has no lines")
        concept_bodies.append(sections["concept"]["body"][0])
        deep_bodies.append(sections["deepDive"]["body"][0])
        summary_bodies.append(sections["summary"]["body"][0])
        for q in l.get("quiz", []):
            need(len(q.get("options", [])) >= 2, f"lesson {lid} quiz {q.get('id')} needs options")
            need(isinstance(q.get("answerIndex"), int) and 0 <= q["answerIndex"] < len(q.get("options", [])), f"lesson {lid} quiz {q.get('id')} answerIndex invalid")
            need(bool(q.get("explanation")), f"lesson {lid} quiz {q.get('id')} lacks explanation")
        need(len(l.get("quiz", [])) >= 3, f"lesson {lid} needs >=3 quiz questions")
        for r in l.get("references", []):
            need(r in references, f"lesson {lid} reference {r} missing")
        for sid in l.get("simulationIds", []):
            need(sid in {s["id"] for s in simulations}, f"lesson {lid} simulation {sid} missing")
        for lab_id in l.get("labIds", []):
            need(lab_id in {lab["id"] for lab in labs}, f"lesson {lid} lab {lab_id} missing")
        need(l.get("exerciseId") in {e["id"] for e in exercises}, f"lesson {lid} exercise missing")
        for nid in l.get("nextLessonIds", []):
            need(nid in lesson_ids, f"lesson {lid} nextLesson {nid} missing")
        need(file_for_web_path(l["contentPath"]).is_file(), f"lesson {lid} contentPath does not resolve")
        need(file_for_web_path(l["diagramPath"]).is_file(), f"lesson {lid} diagramPath missing")
        for a in l.get("assetRefs", []):
            need(file_for_web_path(a) and file_for_web_path(a).is_file(), f"lesson {lid} assetRef missing: {a}")
        need(l.get("apiPath") == f"/api/academy/v2/lesson/{lid}", f"lesson {lid} apiPath incorrect")
    need(len(set(concept_bodies)) == 10 and len(set(deep_bodies)) == 10 and len(set(summary_bodies)) == 10, "lesson concept/deep-dive/summary texts must be unique")
    checks.append("10 full lessons: 16 sections each, unique bodies, valid quiz, references, assets and API paths")

    # Simulations
    sim_ids = {s["id"] for s in simulations}
    for s in simulations:
        need(s.get("logic") in ENGINE_FUNCTIONS, f"simulation {s['id']} has unknown logic")
        need(len(s.get("parameters", [])) >= 3, f"simulation {s['id']} needs >=3 parameters")
        need(len(s.get("steps", [])) >= 4, f"simulation {s['id']} needs >=4 steps")
        need(bool(s.get("limitations")), f"simulation {s['id']} must declare limitations")
        for lid in s.get("lessonIds", []):
            need(lid in lesson_ids, f"simulation {s['id']} lesson {lid} missing")
        need(file_for_web_path(s["diagramPath"]).is_file(), f"simulation {s['id']} diagram missing")
        for r in s.get("references", []):
            need(r in references, f"simulation {s['id']} reference {r} missing")
    checks.append("3 simulations: known engine logic, >=3 parameters, steps, limitations and diagrams")

    # Labs
    lab_ids = {lab["id"] for lab in labs}
    for lab in labs:
        need(lab.get("executionMode") == "internal-simulator", f"lab {lab['id']} executionMode invalid")
        need(lab.get("realDeviceConnection") is False, f"lab {lab['id']} must not connect to real devices")
        future = lab.get("futureIntegration", {})
        need(future.get("enabled") is False, f"lab {lab['id']} future adapters must remain disabled")
        need(future.get("realDevices") == "disabled", f"lab {lab['id']} realDevices must remain disabled")
        need(len(lab.get("steps", [])) >= 5, f"lab {lab['id']} needs >=5 steps")
        need(bool(lab.get("addressingTable")), f"lab {lab['id']} addressingTable missing")
        need("Sample" in lab.get("expectedOutput", {}).get("label", "") and "Simulated" in lab.get("expectedOutput", {}).get("label", ""), f"lab {lab['id']} expectedOutput label invalid")
        for st in lab.get("steps", []):
            need(bool(st.get("commands")), f"lab {lab['id']} step {st.get('id')} has no commands")
        for field in ["scenario", "objectives", "topology", "equipment", "reviewQuestions", "failureScenario", "troubleshooting", "successCriteria", "futureIntegration"]:
            need(bool(lab.get(field)), f"lab {lab['id']} missing {field}")
        need(file_for_web_path(lab["topology"]["diagramPath"]).is_file(), f"lab {lab['id']} topology diagram missing")
        for lid in lab.get("lessonIds", []):
            need(lid in lesson_ids, f"lab {lab['id']} lesson {lid} missing")
        for r in lab.get("references", []):
            need(r in references, f"lab {lab['id']} reference {r} missing")
    checks.append("2 labs: internal simulator only, >=5 steps, addressing, expected output, failure and troubleshooting")

    # Exercises and references
    exercise_ids = {e["id"] for e in exercises}
    need(len(exercise_ids) == len(exercises) == 10, "expected 10 unique exercises")
    for e in exercises:
        need(e.get("lessonId") in lesson_ids, f"exercise {e['id']} lessonId invalid")
        for field in ["title", "prompt", "hint", "expected"]:
            need(bool(e.get(field)), f"exercise {e['id']} missing {field}")
    for rid, ref in references.items():
        need(bool(ref.get("title")) and bool(ref.get("publisher")) and bool(ref.get("type")), f"reference {rid} incomplete")
    checks.append("10 exercises and complete reference registry")

    # Schemas
    for name in ["catalog.schema.json", "lesson.schema.json", "simulation.schema.json", "lab.schema.json"]:
        p = V1 / "schemas" / name
        need(p.is_file(), f"schema {name} missing")
        if p.is_file():
            sc = json.loads(p.read_text(encoding="utf-8"))
            need("$schema" in sc and "required" in sc, f"schema {name} incomplete")
    checks.append("4 JSON Schema contract files present")

    # Broken web-path scan across all v1 JSON files
    broken = []
    for p in sorted(V1.rglob("*.json")):
        text = p.read_text(encoding="utf-8")
        for match in WEB_PATH.findall(text):
            target = file_for_web_path(match.rstrip(".,;:)\"'"))
            if not target or not target.is_file():
                broken.append(f"{p.relative_to(V1)} -> {match}")
    need(not broken, "broken web paths: " + "; ".join(broken[:8]))
    checks.append("all /academy-content and /academy-assets references resolve")

    # Independent manifest
    expected_files = []
    for p in sorted(V1.rglob("*")):
        if p.is_file() and p.name != "manifest.json":
            expected_files.append({"path": p.relative_to(V1).as_posix(), "size": p.stat().st_size, "sha256": sha256(p)})
    mf = {f["path"]: f for f in manifest.get("files", [])}
    need(manifest.get("fileCount") == len(expected_files), f"manifest fileCount {manifest.get('fileCount')} != {len(expected_files)}")
    for f in expected_files:
        entry = mf.get(f["path"])
        need(entry is not None, f"manifest missing {f['path']}")
        if entry:
            need(entry.get("size") == f["size"] and entry.get("sha256") == f["sha256"], f"manifest hash/size mismatch for {f['path']}")
    agg = hashlib.sha256(("\n".join(f"{f['size']}|{f['sha256']}|{f['path']}" for f in expected_files)).encode("utf-8")).hexdigest()
    need(manifest.get("aggregateSha256") == agg, "manifest aggregateSha256 mismatch")
    checks.append(f"independent v1 manifest verifies {len(expected_files)} files and aggregate hash")

    # Root manifest and legacy deletion preservation
    need(ROOT_MANIFEST.is_file(), "root MANIFEST.sha256 missing")
    root_hash = sha256(ROOT_MANIFEST)
    need(root_hash == ROOT_MANIFEST_BASELINE_SHA256, "root MANIFEST.sha256 was modified; it must remain unchanged in this mission")
    root_lines = ROOT_MANIFEST.read_text(encoding="utf-8").splitlines()
    valid = missing = mismatch = 0
    mismatch_paths = []
    for line in root_lines:
        if not line.strip():
            continue
        h, rel = line.split(None, 1)
        target = ROOT / rel.strip()
        if not target.is_file():
            missing += 1
        elif sha256(target) == h:
            valid += 1
        else:
            mismatch += 1
            mismatch_paths.append(rel.strip())
    warnings.append(f"root MANIFEST.sha256 unchanged: {len(root_lines)} entries, {valid} valid, {missing} missing (prior deletions), {mismatch} mismatch (expected for tracked files modified after baseline)")
    if mismatch_paths:
        warnings.append("root manifest mismatch paths: " + ", ".join(mismatch_paths))
    legacy = [
        CONTENT / "catalog.json",
        ASSETS / "curriculum-catalog.json",
        ASSETS / "v5" / "blueprints",
    ]
    for p in legacy:
        need(not p.exists(), f"legacy deleted path must not be restored: {p.relative_to(ROOT)}")
    direct = [p for p in CONTENT.iterdir() if p.is_file()]
    need(not direct, "legacy files must not be recreated directly under academy-content/")
    checks.append("root manifest unchanged; no legacy deleted path was restored")

    # UI / engine / preview static checks
    html = (PRIVATE_UI / "academy.html").read_text(encoding="utf-8")
    css = (ASSETS / "academy-v2.css").read_text(encoding="utf-8")
    engine = (ASSETS / "academy-engine.js").read_text(encoding="utf-8")
    app_js = (ASSETS / "academy-v2.js").read_text(encoding="utf-8")
    preview = (ROOT / "server" / "academy_preview_server.py").read_text(encoding="utf-8")
    need('dir="rtl"' in html and 'lang="fa"' in html, "academy.html must be fa/RTL")
    need('name="viewport"' in html, "academy.html missing responsive viewport")
    need(html.count("__FAM_ACADEMY_BOOTSTRAP__") == 1, "bootstrap marker must appear exactly once")
    need(html.count("__FAM_CSP_NONCE__") == 1, "CSP nonce marker must appear exactly once")
    need("curriculum-catalog.json" not in html, "academy.html still references deleted legacy catalog")
    need("academy-v2.js" in html and "academy-engine.js" in html, "new UI scripts missing")
    need("@media" in css and "direction: rtl" in css, "academy-v2.css must include RTL and responsive rules")
    for fn in ENGINE_FUNCTIONS:
        need(fn in engine, f"engine missing {fn}")
    need("/api/academy/v2/catalog" in app_js, "UI must use new v2 API")
    need("famAcademyV2.progress.v1" in app_js, "UI must use isolated progress key")
    need("preview_html" in preview and "0.0.0.0" in preview, "preview server contract incomplete")
    checks.append("RTL/responsive UI, new API usage, engine functions and preview server contract")

    # FAM Academy shell integration
    ref_css = (ASSETS / "academy-reference-ui.css")
    need(ref_css.is_file(), "retained FAM Academy shell CSS is missing")
    need("academy-reference-ui.css" in html, "academy.html must load the FAM Academy shell CSS")
    need('data-theme="dark"' in html, "academy.html must declare the FAM theme root")
    need("fam.academy.theme" in html and "fam.ui.theme" in html, "FAM theme bridge keys missing")
    need("app-shell" in app_js and "academy-section-head" in app_js and "academy-menu-toggle" in app_js, "FAM shell markup missing from SPA")
    need('href="/app"' in app_js, "back-to-FAM link missing from SPA")
    need("FAM Academy shell integration" in css and 'html[data-theme="light"]' in css, "FAM shell/theme CSS compatibility missing")
    if ref_css.is_file():
        ref_text = ref_css.read_text(encoding="utf-8")
        need("learning-journey.jpg" not in ref_text or (ASSETS / "learning-journey.jpg").is_file(), "FAM shell background image missing")
    checks.append("FAM Academy shell: sidebar/topbar/section-head, theme bridge and back-to-FAM links")

    # No CJK artifacts and no obvious secrets in new files
    scan_files = list(V1.rglob("*")) + [PRIVATE_UI / "academy.html", ASSETS / "academy-v2.css", ASSETS / "academy-engine.js", ASSETS / "academy-v2.js", ROOT / "server" / "academy_preview_server.py"]
    for p in scan_files:
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        if CJK.search(text):
            errors.append(f"unexpected CJK characters in {p.relative_to(ROOT)}")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                errors.append(f"possible secret pattern in {p.relative_to(ROOT)}")
    checks.append("new content/code scanned for CJK artifacts and obvious secret patterns")

    counts = {
        "paths": len(paths), "courses": len(courses), "liveCourses": len(live_courses),
        "plannedCourses": len(planned_courses), "lessons": len(lessons), "sectionsPerLesson": len(REQUIRED_SECTIONS),
        "simulations": len(simulations), "labs": len(labs), "exercises": len(exercises),
        "references": len(references), "manifestFiles": len(expected_files),
        "rootManifestEntries": len(root_lines), "rootManifestValid": valid,
        "rootManifestMissing": missing, "rootManifestMismatch": mismatch,
    }
    return {"ok": not errors, "errors": errors, "warnings": warnings, "checks": checks, "counts": counts}


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate FAM Academy v2")
    ap.add_argument("--root", default=None, help="Project root (default: parent of tools/)")
    ap.add_argument("--json", action="store_true", help="Print JSON result")
    args = ap.parse_args()
    result = validate(Path(args.root) if args.root else None)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("FAM Academy v2 validator:", "PASS" if result["ok"] else "FAIL")
        for c in result["checks"]:
            print("  ✓", c)
        for w in result["warnings"]:
            print("  !", w)
        for e in result["errors"]:
            print("  ✗", e)
        print("counts:", json.dumps(result["counts"], ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
