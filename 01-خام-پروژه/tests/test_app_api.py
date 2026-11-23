import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parent
SERVER_DIR = PACKAGE_ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

try:
    import app as fam_app_module
    HAS_FLASK = True
except ModuleNotFoundError:
    HAS_FLASK = False


class FamPackagingTests(unittest.TestCase):
    def test_nginx_configs_exist_and_include_security_headers(self):
        raw_nginx = PACKAGE_ROOT / "nginx.conf"
        delivery_nginx = REPO_ROOT / "02-فایل-های-اجرایی" / "nginx.conf"
        self.assertTrue(raw_nginx.is_file(), "01-خام-پروژه/nginx.conf must exist for docker-compose")
        self.assertTrue(delivery_nginx.is_file(), "02-فایل-های-اجرایی/nginx.conf must exist")
        raw_text = raw_nginx.read_text(encoding="utf-8")
        self.assertEqual(raw_text, delivery_nginx.read_text(encoding="utf-8"))
        self.assertIn('X-Content-Type-Options "nosniff"', raw_text)
        self.assertIn('X-Frame-Options "DENY"', raw_text)
        self.assertIn('Cache-Control "no-store"', raw_text)
        self.assertIn("server_tokens off;", raw_text)

    def test_dockerfile_sets_executable_loader_permissions(self):
        dockerfile = (PACKAGE_ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("ld-linux-", dockerfile)
        self.assertIn("chmod 0755", dockerfile)


@unittest.skipUnless(HAS_FLASK, "Flask is not installed in this Python environment")
class FamAppApiTests(unittest.TestCase):
    ORIGIN = "https://fam-test.local"
    ADMIN_PASSWORD = "TestAdminPassword!2026"

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test_fam.sqlite3"
        self.env_patch = patch.dict(
            os.environ,
            {
                "FAM_DB": str(self.db_path),
                "FAM_PUBLIC_ORIGIN": self.ORIGIN,
                "FAM_INITIAL_PASSWORD": self.ADMIN_PASSWORD,
            },
        )
        self.env_patch.start()
        self.app = fam_app_module.create_app(
            {
                "TESTING": True,
                "DB_PATH": str(self.db_path),
                "PUBLIC_ORIGIN": self.ORIGIN,
            }
        )
        self.client = self.app.test_client()
        self.https_env = {"wsgi.url_scheme": "https", "HTTP_HOST": "fam-test.local"}

    def tearDown(self):
        self.env_patch.stop()
        self.tmpdir.cleanup()

    def _login_admin(self):
        return self.client.post(
            "/api/login",
            json={"username": "admin", "password": self.ADMIN_PASSWORD},
            headers={"Origin": self.ORIGIN},
            environ_base=self.https_env,
        )

    def test_public_login_and_unauthenticated_guards(self):
        res = self.client.get("/", environ_base=self.https_env)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("Referrer-Policy"), "same-origin")
        self.assertEqual(res.headers.get("Cache-Control"), "no-store")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")

        for path in (
            "/api/status",
            "/api/state",
            "/api/users",
            "/api/equipment/state",
            "/api/real/status",
            "/academy",
            "/academy-content/catalog.json",
        ):
            r = self.client.get(path, environ_base=self.https_env)
            self.assertEqual(r.status_code, 401, f"Expected 401 for {path}")

        for ui_path in ("/app", "/FAM.html"):
            r_ui = self.client.get(ui_path, environ_base=self.https_env)
            self.assertEqual(r_ui.status_code, 302)
            self.assertTrue(r_ui.headers.get("Location", "").endswith("/login.html"))

        r_prog = self.client.post(
            "/api/academy/progress",
            json={"changes": {"fam3.progress.v1": "{}"}},
            headers={"Origin": self.ORIGIN},
            environ_base=self.https_env,
        )
        self.assertEqual(r_prog.status_code, 401)

    def test_origin_enforcement_on_mutating_requests(self):
        no_origin = self.client.post(
            "/api/login",
            json={"username": "admin", "password": self.ADMIN_PASSWORD},
            environ_base=self.https_env,
        )
        self.assertEqual(no_origin.status_code, 403)

        bad_origin = self.client.post(
            "/api/login",
            json={"username": "admin", "password": self.ADMIN_PASSWORD},
            headers={"Origin": "https://evil.example"},
            environ_base=self.https_env,
        )
        self.assertEqual(bad_origin.status_code, 403)

    def test_real_device_bridge_is_disabled_when_authenticated(self):
        login_res = self._login_admin()
        self.assertEqual(login_res.status_code, 200)
        csrf = login_res.get_json()["csrf"]

        res = self.client.get("/api/real/status", environ_base=self.https_env)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data.get("enabled"))

        post_res = self.client.post(
            "/api/real/session",
            json={},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(post_res.status_code, 503)

    def test_login_csrf_academy_progress_equipment_and_logout_flow(self):
        login_res = self._login_admin()
        self.assertEqual(login_res.status_code, 200)

        body = login_res.get_json()
        csrf = body.get("csrf")
        self.assertTrue(csrf)
        self.assertEqual(body["user"]["username"], "admin")

        state_res = self.client.get("/api/state", environ_base=self.https_env)
        self.assertEqual(state_res.status_code, 200)

        eq_res = self.client.get("/api/equipment/state", environ_base=self.https_env)
        self.assertEqual(eq_res.status_code, 200)
        self.assertIn("inventory", eq_res.get_json())

        no_csrf = self.client.post(
            "/api/academy/progress",
            json={"changes": {"fam3.progress.v1": "{}"}},
            headers={"Origin": self.ORIGIN},
            environ_base=self.https_env,
        )
        self.assertEqual(no_csrf.status_code, 403)

        bad_payload = self.client.post(
            "/api/academy/progress",
            json={"completed": ["intro"]},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(bad_payload.status_code, 400)

        with_csrf = self.client.post(
            "/api/academy/progress",
            json={"changes": {"fam3.progress.v1": json.dumps({"done": ["intro"]})}},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(with_csrf.status_code, 200)
        self.assertTrue(with_csrf.get_json().get("ok"))

        academy_res = self.client.get("/academy", environ_base=self.https_env)
        self.assertEqual(academy_res.status_code, 200)
        self.assertIn("fam3.progress.v1", academy_res.get_data(as_text=True))

        out = self.client.post(
            "/api/logout",
            json={},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(out.status_code, 200)
        self.assertEqual(self.client.get("/api/state", environ_base=self.https_env).status_code, 401)

    def test_login_rate_limit_blocks_after_ten_failures(self):
        for attempt in range(10):
            res = self.client.post(
                "/api/login",
                json={"username": "admin", "password": "wrong-password"},
                headers={"Origin": self.ORIGIN},
                environ_base=self.https_env,
            )
            self.assertEqual(res.status_code, 401, f"Attempt {attempt + 1} should return 401")

        locked = self.client.post(
            "/api/login",
            json={"username": "admin", "password": self.ADMIN_PASSWORD},
            headers={"Origin": self.ORIGIN},
            environ_base=self.https_env,
        )
        self.assertEqual(locked.status_code, 429)


if __name__ == "__main__":
    unittest.main()
