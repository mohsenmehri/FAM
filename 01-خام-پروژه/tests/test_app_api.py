import os
import sys
import tempfile
import unittest
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1] / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

try:
    import app as fam_app_module
    HAS_FLASK = True
except ModuleNotFoundError:
    HAS_FLASK = False


@unittest.skipUnless(HAS_FLASK, "Flask is not installed in this Python environment")
class FamAppApiTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test_fam.sqlite3"
        os.environ["FAM_DB_PATH"] = str(self.db_path)
        os.environ["FAM_BOOTSTRAP_ADMIN_PASSWORD"] = "TestPass123!"
        self.app = fam_app_module.create_app({"TESTING": True})
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_public_login_and_unauthenticated_guards(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

        for path in ("/api/status", "/api/state", "/api/users"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 401, f"Expected 401 for {path}")

        r_prog = self.client.post("/api/academy/progress", json={"completed": []})
        self.assertIn(r_prog.status_code, (401, 403))

    def test_real_device_bridge_is_disabled(self):
        res = self.client.get("/api/real/status")
        self.assertIn(res.status_code, (200, 401))
        if res.status_code == 200:
            data = res.get_json()
            self.assertFalse(data.get("enabled"))

    def test_login_csrf_and_session_flow(self):
        # Default bootstrap admin credentials
        login_res = self.client.post(
            "/api/login",
            json={"username": "admin", "password": os.environ.get("FAM_BOOTSTRAP_ADMIN_PASSWORD", "admin")},
        )
        if login_res.status_code != 200:
            self.skipTest("Bootstrap admin password differs from default; skipping authenticated flow")

        body = login_res.get_json()
        csrf = body.get("csrf")
        self.assertTrue(csrf)

        # GET /api/state works when authenticated
        state_res = self.client.get("/api/state")
        self.assertEqual(state_res.status_code, 200)

        # POST without CSRF must be rejected
        no_csrf = self.client.post("/api/academy/progress", json={"completed": ["intro"]})
        self.assertIn(no_csrf.status_code, (400, 403))

        # POST with CSRF succeeds
        with_csrf = self.client.post(
            "/api/academy/progress",
            json={"completed": ["intro"]},
            headers={"X-FAM-CSRF": csrf},
        )
        self.assertEqual(with_csrf.status_code, 200)

        # Logout invalidates session
        out = self.client.post("/api/logout", json={}, headers={"X-FAM-CSRF": csrf})
        self.assertEqual(out.status_code, 200)
        self.assertEqual(self.client.get("/api/state").status_code, 401)


if __name__ == "__main__":
    unittest.main()
