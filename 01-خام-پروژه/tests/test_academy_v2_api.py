"""Dependency-free HTTP integration tests for the FAM Academy v2 preview API.

The preview server serves the exact rebuilt HTML/CSS/JS and versioned content.
It is deliberately stateless and opens no device, SSH, Telnet, Docker or VM
connections. Flask-dependent production-route tests remain in test_app_api.py
and are skipped only when Flask is absent.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys
import threading
import unittest
import urllib.error
import urllib.request

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = PACKAGE_ROOT / "server"
WWW = SERVER_DIR / "www"
V1 = WWW / "academy-content" / "v1"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
import academy_preview_server as preview  # noqa: E402

CATALOG = json.loads((V1 / "catalog.json").read_text(encoding="utf-8"))


class AcademyV2PreviewApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = preview.make_server("127.0.0.1", 0)
        cls.base = "http://127.0.0.1:" + str(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    def request(self, path, method="GET", payload=None, headers=None, follow_redirects=True):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req_headers = {"Accept": "application/json"}
        if data is not None:
            req_headers["Content-Type"] = "application/json"
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(self.base + path, data=data, headers=req_headers, method=method)
        opener = urllib.request.build_opener() if follow_redirects else urllib.request.build_opener(self.NoRedirect())
        try:
            with opener.open(req, timeout=8) as res:
                return res.status, res.headers, res.read()
        except urllib.error.HTTPError as err:
            return err.code, err.headers, err.read()

    def json_get(self, path):
        status, headers, body = self.request(path)
        self.assertEqual(status, 200, path)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        return json.loads(body.decode("utf-8"))

    def test_academy_shell_uses_replaced_markers_and_preview_safe_headers(self):
        status, headers, body = self.request("/academy")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        text = body.decode("utf-8")
        self.assertNotIn("__FAM_CSP_NONCE__", text)
        self.assertNotIn("__FAM_ACADEMY_BOOTSTRAP__", text)
        self.assertIn("window.FAM_ACADEMY_BOOTSTRAP", text)
        self.assertIn('nonce="fam-v2-preview"', text)
        self.assertIn("academy-v2.js", text)
        self.assertIn("academy-reference-ui.css", text)
        self.assertIn("fam.academy.theme", text)
        self.assertIn("fam.ui.theme", text)
        self.assertIn("famAcademyV2.progress.v1", text)
        csp = headers.get("Content-Security-Policy", "")
        self.assertIn("script-src 'self' 'nonce-fam-v2-preview'", csp)
        self.assertNotIn("frame-ancestors", csp)
        self.assertIsNone(headers.get("X-Frame-Options"))
        self.assertEqual(headers.get("Cache-Control"), "no-store")

    def test_root_redirects_to_academy(self):
        status, headers, _ = self.request("/", follow_redirects=False)
        self.assertEqual(status, 302)
        self.assertEqual(headers.get("Location"), "/academy")

    def test_static_ui_engine_css_and_generated_diagram_are_served(self):
        checks = [
            ("/academy-assets/academy-reference-ui.css", "text/css"),
            ("/academy-assets/academy-v2.css", "text/css"),
            ("/academy-assets/academy-engine.js", "text/javascript"),
            ("/academy-assets/academy-v2.js", "text/javascript"),
            ("/academy-content/v1/catalog.json", "application/json"),
            ("/academy-content/v1/assets/diagrams/l01-osi-tcpip-encapsulation.svg", "image/svg+xml"),
        ]
        for path, expected_type in checks:
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertIn(expected_type, headers.get("Content-Type", ""))
                self.assertTrue(body)

    def test_health_catalog_exercises_and_references_are_connected(self):
        health = self.json_get("/api/academy/v2/health")
        self.assertTrue(health["ok"])
        self.assertEqual(health["service"], "preview")
        catalog = self.json_get("/api/academy/v2/catalog")
        self.assertEqual(len(catalog["paths"]), 23)
        self.assertEqual(len(catalog["courses"]), 23)
        self.assertEqual(len(catalog["lessons"]), 10)
        self.assertEqual(len(catalog["simulations"]), 3)
        self.assertEqual(len(catalog["labs"]), 2)
        self.assertEqual(sum(c["status"] == "live" for c in catalog["courses"]), 5)
        exercises = self.json_get("/api/academy/v2/exercises")
        self.assertEqual(len(exercises["exercises"]), 10)
        references = self.json_get("/api/academy/v2/references")
        self.assertGreaterEqual(len(references), 20)

    def test_lesson_simulation_and_lab_detail_apis(self):
        lesson_id = CATALOG["lessons"][0]["id"]
        sim_id = CATALOG["simulations"][0]["id"]
        lab_id = CATALOG["labs"][0]["id"]
        lesson = self.json_get("/api/academy/v2/lesson/" + lesson_id)
        sim = self.json_get("/api/academy/v2/simulation/" + sim_id)
        lab = self.json_get("/api/academy/v2/lab/" + lab_id)
        self.assertEqual(lesson["id"], lesson_id)
        self.assertEqual(len(lesson["sections"]), 16)
        self.assertEqual(sim["id"], sim_id)
        self.assertGreaterEqual(len(sim["parameters"]), 3)
        self.assertEqual(lab["id"], lab_id)
        self.assertEqual(lab["executionMode"], "internal-simulator")
        self.assertIs(lab["futureIntegration"]["enabled"], False)

    def test_quiz_api_scores_correct_wrong_and_invalid_submissions(self):
        lesson_id = CATALOG["lessons"][0]["id"]
        lesson = self.json_get("/api/academy/v2/lesson/" + lesson_id)
        correct = [q["answerIndex"] for q in lesson["quiz"]]
        status, _, body = self.request("/api/academy/v2/quiz/" + lesson_id, method="POST", payload={"answers": correct})
        self.assertEqual(status, 200)
        result = json.loads(body.decode("utf-8"))
        self.assertTrue(result["ok"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["correct"], result["total"])
        self.assertTrue(all(d["correct"] for d in result["details"]))
        self.assertIn("Sample / Simulated", result["label"])

        wrong = [0 if q["answerIndex"] != 0 else 1 for q in lesson["quiz"]]
        status, _, body = self.request("/api/academy/v2/quiz/" + lesson_id, method="POST", payload={"answers": wrong})
        self.assertEqual(status, 200)
        result = json.loads(body.decode("utf-8"))
        self.assertLess(result["score"], 100)
        self.assertTrue(any(not d["correct"] for d in result["details"]))

        status, _, body = self.request("/api/academy/v2/quiz/" + lesson_id, method="POST", payload={"answers": "bad"})
        self.assertEqual(status, 400)
        self.assertFalse(json.loads(body.decode("utf-8"))["ok"])

    def test_progress_endpoint_is_stateless_and_does_not_persist_user_data(self):
        payload = {"changes": {"famAcademyV2.progress.v1": json.dumps({"completedLessons": ["demo"]})}}
        status, _, body = self.request("/api/academy/progress", method="POST", payload=payload)
        self.assertEqual(status, 200)
        result = json.loads(body.decode("utf-8"))
        self.assertTrue(result["ok"])
        self.assertTrue(result["preview"])
        self.assertFalse(result["persisted"])
        status, _, body = self.request("/api/academy/progress")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body.decode("utf-8"))["progress"], {})

    def test_path_traversal_and_legacy_content_paths_are_rejected(self):
        paths = [
            "/academy-assets/../app.py",
            "/academy-assets/%2e%2e/app.py",
            "/academy-content/../MANIFEST.sha256",
            "/academy-content/catalog.json",
            "/academy-assets/curriculum-catalog.json",
            "/academy-assets/v5/blueprints/lesson.json",
            "/api/academy/v2/lesson/../catalog.json",
        ]
        for path in paths:
            with self.subTest(path=path):
                status, _, _ = self.request(path)
                self.assertEqual(status, 404, path)

    def test_preview_server_source_is_dependency_free_and_has_no_device_or_persistence_logic(self):
        source = (SERVER_DIR / "academy_preview_server.py").read_text(encoding="utf-8")
        ast.parse(source, filename="academy_preview_server.py")
        for forbidden in ("import flask", "import paramiko", "import docker", "connect(", "ssh", "telnet"):
            self.assertNotIn(forbidden, source.lower())
        self.assertIn("0.0.0.0", source)
        self.assertIn("preview_html", source)
        self.assertIn("persist", source.lower())
        self.assertIn("user data", source.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
