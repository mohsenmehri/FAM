import json
import os
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parent
SERVER_DIR = PACKAGE_ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import equipment_guard

try:
    import app as fam_app_module
    HAS_FLASK = True
except ModuleNotFoundError:
    HAS_FLASK = False


class FamPackagingTests(unittest.TestCase):
    def test_nginx_configs_exist_and_include_security_headers(self):
        raw_nginx = PACKAGE_ROOT / "nginx.conf"
        delivery_dir = REPO_ROOT / "02-فایل-های-اجرایی"
        delivery_nginx = delivery_dir / "nginx.conf"
        self.assertTrue(raw_nginx.is_file(), "01-خام-پروژه/nginx.conf must exist for docker-compose")
        raw_text = raw_nginx.read_text(encoding="utf-8")
        if delivery_dir.is_dir():
            self.assertTrue(delivery_nginx.is_file(), "02-فایل-های-اجرایی/nginx.conf must exist")
            self.assertEqual(raw_text, delivery_nginx.read_text(encoding="utf-8"))
        self.assertIn('X-Content-Type-Options "nosniff"', raw_text)
        self.assertIn('X-Frame-Options "DENY"', raw_text)
        self.assertIn('Cache-Control "no-store"', raw_text)
        self.assertIn("server_tokens off;", raw_text)
        gzip_lines = [line for line in raw_text.splitlines() if "gzip_types" in line]
        self.assertTrue(gzip_lines, "gzip_types directive must be present")
        for line in gzip_lines:
            self.assertNotIn("text/html", line)

    def test_dockerfile_sets_executable_loader_permissions(self):
        dockerfile = (PACKAGE_ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("ld-linux-", dockerfile)
        self.assertIn("chmod 0755", dockerfile)

    def test_compose_enables_trusted_proxy_and_nginx_forwarding(self):
        raw_compose = (PACKAGE_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn('FAM_TRUST_PROXY: "1"', raw_compose)
        delivery_dir = REPO_ROOT / "02-فایل-های-اجرایی"
        if delivery_dir.is_dir():
            delivery_compose = (delivery_dir / "docker-compose.yml").read_text(encoding="utf-8")
            self.assertIn('FAM_TRUST_PROXY: "1"', delivery_compose)
        raw_nginx = (PACKAGE_ROOT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;", raw_nginx)
        self.assertIn("proxy_set_header X-Forwarded-Proto https;", raw_nginx)

    def test_fam_html_keeps_branch_site_selector_visible_and_optional(self):
        html = (SERVER_DIR / "private_ui" / "FAM.html").read_text(encoding="utf-8")
        self.assertIn("site.closest('label').hidden=false;site.disabled=!siteKind.value;site.required=!isBranch;", html)
        self.assertIn("اختیاری (بدون محل مشخص)", html)
        self.assertIn("site.value||(isBranch?null:'')", html)
        self.assertNotIn("site.closest('label').hidden=isBranch", html)


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
        try:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(res.headers.get("Referrer-Policy"), "same-origin")
            self.assertEqual(res.headers.get("Cache-Control"), "no-store")
            self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        finally:
            res.close()

        for path in (
            "/api/status",
            "/api/state",
            "/api/users",
            "/api/equipment/state",
            "/api/real/status",
            "/academy",
            "/academy-assets/curriculum-catalog.json",
            "/academy-assets/lesson-engine.js",
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

        asset_res = self.client.get("/academy-assets/curriculum-catalog.json", environ_base=self.https_env)
        try:
            self.assertEqual(asset_res.status_code, 200)
        finally:
            asset_res.close()

        out = self.client.post(
            "/api/logout",
            json={},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(out.status_code, 200)
        self.assertEqual(self.client.get("/api/state", environ_base=self.https_env).status_code, 401)

    def test_terraform_lesson_assets_and_quiz_progress_require_session(self):
        path = "/academy-assets/v5/blueprints/academy-automation-terraform.json"
        self.assertEqual(self.client.get(path, environ_base=self.https_env).status_code, 401)
        login = self._login_admin()
        self.assertEqual(login.status_code, 200)
        csrf = login.get_json()["csrf"]
        catalog = self.client.get("/academy-assets/curriculum-catalog.json", environ_base=self.https_env).get_json()
        lesson = next(lesson for track in catalog["paths"] for course in track["courses"]
                      for lesson in course["lessons"] if lesson["id"] == "academy-automation-terraform")
        self.assertEqual(lesson["blueprint"], path)
        res = self.client.get(path, environ_base=self.https_env)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["lessonId"], lesson["id"])
        res.close()
        state = {"completed": [], "labs": {"quizAttempts": {lesson["id"]: {
            "correct": 6, "incorrect": 2, "unanswered": 4, "total": 12}}}}
        saved = self.client.post("/api/academy/progress", json={"changes": {"fam4.learn.v1": json.dumps(state)}, "expectedRevision": 0},
                                 headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf}, environ_base=self.https_env)
        self.assertEqual(saved.status_code, 200)
        page = self.client.get("/academy", environ_base=self.https_env).get_data(as_text=True)
        self.assertIn('academy-automation-terraform', page)
        self.assertIn('quizAttempts', page)
        out = self.client.post("/api/logout", json={}, headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
                               environ_base=self.https_env)
        self.assertEqual(out.status_code, 200)
        self.assertEqual(self.client.get(path, environ_base=self.https_env).status_code, 401)

    def test_academy_progress_cas_concurrency_and_atomic_backup(self):
        clients = []
        for _ in range(8):
            c = self.app.test_client()
            login = c.post('/api/login', json={'username':'admin', 'password':self.ADMIN_PASSWORD},
                           headers={'Origin':self.ORIGIN}, environ_base=self.https_env)
            self.assertEqual(login.status_code, 200)
            clients.append((c, login.get_json()['csrf']))
        def post(c, csrf, value, revision):
            return c.post('/api/academy/progress',
                json={'changes':{'fam4.learn.v1':json.dumps(value)}, 'expectedRevision':revision},
                headers={'Origin':self.ORIGIN, 'X-FAM-CSRF':csrf}, environ_base=self.https_env)
        initial={'completed':['initial'], 'labs':{}}
        first=post(*clients[0], initial, 0)
        self.assertEqual(first.status_code, 200); self.assertEqual(first.get_json()['revision'], 1)
        missing=clients[0][0].post('/api/academy/progress', json={'changes':{'fam4.learn.v1':'{}'}},
                headers={'Origin':self.ORIGIN,'X-FAM-CSRF':clients[0][1]},environ_base=self.https_env)
        self.assertEqual(missing.status_code,409)
        barrier=threading.Barrier(9); results=[]; errors=[]; lock=threading.Lock()
        def worker(index):
            try:
                barrier.wait(timeout=10)
                response=post(*clients[index], {'completed':[f'client-{index}'],'labs':{}}, 1)
                with lock: results.append((index,response.status_code,response.get_json()))
            except BaseException as exc:
                with lock: errors.append(repr(exc))
        threads=[threading.Thread(target=worker,args=(i,)) for i in range(8)]
        for thread in threads: thread.start()
        try: barrier.wait(timeout=10)
        finally:
            for thread in threads: thread.join(timeout=20)
        self.assertFalse(any(t.is_alive() for t in threads)); self.assertEqual(errors,[])
        self.assertEqual(len(results),8)
        self.assertEqual(sorted(x[1] for x in results),[200]+[409]*7)
        winner=next(i for i,status,_ in results if status==200)
        with sqlite3.connect(self.db_path) as db:
            row=db.execute('SELECT payload,revision FROM academy_progress').fetchone()
            backups=db.execute('SELECT revision,payload FROM academy_progress_backups').fetchall()
        self.assertEqual(row[1],2)
        self.assertEqual(json.loads(json.loads(row[0])['fam4.learn.v1'])['completed'],[f'client-{winner}'])
        self.assertEqual(len(backups),1); self.assertEqual(backups[0][0],1)
        self.assertEqual(json.loads(json.loads(backups[0][1])['fam4.learn.v1']),initial)
        with sqlite3.connect(self.db_path) as db:
            db.execute("CREATE TRIGGER fail_progress_update BEFORE UPDATE ON academy_progress BEGIN SELECT RAISE(ABORT, 'simulated disk error'); END")
        failed=post(*clients[0], {'completed':['fail'],'labs':{}}, 2)
        self.assertNotEqual(failed.status_code,200)
        with sqlite3.connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM academy_progress_backups').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT revision FROM academy_progress').fetchone()[0],2)

    def test_academy_progress_legacy_and_unknown_cannot_be_overwritten(self):
        csrf=self._login_admin().get_json()['csrf']
        headers={'Origin':self.ORIGIN,'X-FAM-CSRF':csrf}
        with sqlite3.connect(self.db_path) as db:
            uid=db.execute("SELECT id FROM users WHERE username='admin'").fetchone()[0]
        for raw in (json.dumps({'completedLessons':['s01'],'notes':{'s01':'private'}}),
                    json.dumps({'completed':[],'completedLessons':['s01']}), '{bad', '{}'):
            with self.subTest(raw=raw):
                data=json.dumps({'fam4.learn.v1':raw, 'unknown':'preserve-me'})
                with sqlite3.connect(self.db_path) as db:
                    db.execute('INSERT OR REPLACE INTO academy_progress(user_id,payload,updated_at,revision) VALUES(?,?,?,?)',(uid,data,0,7))
                response=self.client.post('/api/academy/progress',json={'changes':{'fam4.learn.v1':json.dumps({'completed':[]})},'expectedRevision':7},headers=headers,environ_base=self.https_env)
                self.assertEqual(response.status_code,409)
                with sqlite3.connect(self.db_path) as db:
                    self.assertEqual(db.execute('SELECT payload,revision FROM academy_progress WHERE user_id=?',(uid,)).fetchone(),(data,7))
        # Old clients may still update other keys without silently erasing unknown data.
        response=self.client.post('/api/academy/progress',json={'changes':{'fam3.progress.v1':'{}'}},headers=headers,environ_base=self.https_env)
        self.assertEqual(response.status_code,200)
        with sqlite3.connect(self.db_path) as db:
            payload,rev=db.execute('SELECT payload,revision FROM academy_progress WHERE user_id=?',(uid,)).fetchone()
            self.assertEqual(json.loads(payload)['unknown'],'preserve-me'); self.assertEqual(rev,8)

    def test_osi_lesson_is_resolvable_and_auth_gated(self):
        path = "/academy-assets/v5/blueprints/academy-stage-zero-osi-fa.json"
        self.assertEqual(self.client.get(path, environ_base=self.https_env).status_code, 401)
        self.assertEqual(self._login_admin().status_code, 200)
        response = self.client.get(path, environ_base=self.https_env)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["lessonId"], "academy-stage-zero-osi-fa")
        response.close()

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


@unittest.skipUnless(HAS_FLASK, "Flask is not installed in this Python environment")
class FamProxyFixTests(unittest.TestCase):
    ORIGIN = "https://fam-test.local"
    ADMIN_PASSWORD = "TestAdminPassword!2026"

    def _make_app(self, trust_proxy, trusted_proxies=None):
        tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(tmpdir.name) / "proxy_test.sqlite3"
        cfg = {
            "TESTING": True,
            "DB_PATH": str(db_path),
            "PUBLIC_ORIGIN": self.ORIGIN,
            "TRUST_PROXY": trust_proxy,
        }
        if trusted_proxies is not None:
            cfg["TRUSTED_PROXIES"] = trusted_proxies
        with patch.dict(
            os.environ,
            {
                "FAM_DB": str(db_path),
                "FAM_PUBLIC_ORIGIN": self.ORIGIN,
                "FAM_INITIAL_PASSWORD": self.ADMIN_PASSWORD,
            },
        ):
            app = fam_app_module.create_app(cfg)

        @app.get("/_test_whoami")
        def _whoami():
            from flask import jsonify, request
            return jsonify(
                remote_addr=request.remote_addr,
                scheme=request.scheme,
                host=request.host,
            )

        return tmpdir, app

    def test_proxy_headers_ignored_when_trust_proxy_disabled(self):
        tmpdir, app = self._make_app(trust_proxy=False)
        try:
            client = app.test_client()
            res = client.get(
                "/_test_whoami",
                headers={
                    "Host": "fam-test.local",
                    "X-Forwarded-For": "198.51.100.77",
                    "X-Forwarded-Proto": "https",
                    "X-Forwarded-Host": "evil.example",
                },
                environ_base={"REMOTE_ADDR": "172.18.0.2", "wsgi.url_scheme": "http"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["remote_addr"], "172.18.0.2")
            self.assertEqual(data["scheme"], "http")
            self.assertEqual(data["host"], "fam-test.local")
        finally:
            tmpdir.cleanup()

    def test_trusted_proxy_uses_rightmost_hop_and_blocks_untrusted_peer_spoofing(self):
        tmpdir, app = self._make_app(trust_proxy=True, trusted_proxies="127.0.0.0/8,172.16.0.0/12")
        try:
            client = app.test_client()
            # Trusted nginx peer with spoofed leftmost X-Forwarded-For + X-Forwarded-Host:
            # must pick the rightmost 1 hop (198.51.100.44) and ignore X-Forwarded-Host/Port/Prefix.
            proxied = client.get(
                "/_test_whoami",
                headers={
                    "Host": "fam-test.local",
                    "X-Forwarded-For": "9.9.9.9, 198.51.100.44",
                    "X-Forwarded-Proto": "https",
                    "X-Forwarded-Host": "evil.example",
                    "X-Forwarded-Port": "9999",
                    "X-Forwarded-Prefix": "/evil",
                },
                environ_base={"REMOTE_ADDR": "172.18.0.2", "wsgi.url_scheme": "http"},
            )
            self.assertEqual(proxied.status_code, 200)
            pdata = proxied.get_json()
            self.assertEqual(pdata["remote_addr"], "198.51.100.44")
            self.assertEqual(pdata["scheme"], "https")
            self.assertEqual(pdata["host"], "fam-test.local")

            # Untrusted direct peer spoofing X-Forwarded-For & X-Forwarded-Proto:
            spoofed = client.get(
                "/_test_whoami",
                headers={
                    "Host": "fam-test.local",
                    "X-Forwarded-For": "1.2.3.4",
                    "X-Forwarded-Proto": "https",
                },
                environ_base={"REMOTE_ADDR": "203.0.113.99", "wsgi.url_scheme": "http"},
            )
            self.assertEqual(spoofed.status_code, 200)
            sdata = spoofed.get_json()
            self.assertEqual(sdata["remote_addr"], "203.0.113.99")
            self.assertEqual(sdata["scheme"], "http")
        finally:
            tmpdir.cleanup()

    def test_rate_limit_isolates_clients_and_ignores_spoofed_xff_behind_trusted_proxy(self):
        tmpdir, app = self._make_app(trust_proxy=True, trusted_proxies="172.16.0.0/12")
        try:
            client = app.test_client()
            for i in range(10):
                res = client.post(
                    "/api/login",
                    json={"username": "admin", "password": "wrong-password"},
                    headers={
                        "Origin": self.ORIGIN,
                        "X-Forwarded-For": f"10.255.0.{i + 1}, 198.51.100.10",
                        "X-Forwarded-Proto": "https",
                    },
                    environ_base={"REMOTE_ADDR": "172.18.0.2"},
                )
                self.assertEqual(res.status_code, 401)

            blocked = client.post(
                "/api/login",
                json={"username": "admin", "password": self.ADMIN_PASSWORD},
                headers={
                    "Origin": self.ORIGIN,
                    "X-Forwarded-For": "8.8.8.8, 198.51.100.10",
                    "X-Forwarded-Proto": "https",
                },
                environ_base={"REMOTE_ADDR": "172.18.0.2"},
            )
            self.assertEqual(blocked.status_code, 429)

            other_client = client.post(
                "/api/login",
                json={"username": "admin", "password": self.ADMIN_PASSWORD},
                headers={
                    "Origin": self.ORIGIN,
                    "X-Forwarded-For": "198.51.100.11",
                    "X-Forwarded-Proto": "https",
                },
                environ_base={"REMOTE_ADDR": "172.18.0.2"},
            )
            self.assertEqual(other_client.status_code, 200)
        finally:
            tmpdir.cleanup()


class FamEquipmentConcurrencyTests(unittest.TestCase):
    def test_resolve_max_concurrent_handles_invalid_zero_negative_and_bounds(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FAM_EQUIPMENT_MAX_CONCURRENT", None)
            self.assertEqual(equipment_guard.resolve_max_concurrent(), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent(""), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent("invalid"), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent("3.5"), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent("0"), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent(0), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent("-5"), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent(-10), 8)
            self.assertEqual(equipment_guard.resolve_max_concurrent("1"), 1)
            self.assertEqual(equipment_guard.resolve_max_concurrent("16"), 16)
            self.assertEqual(equipment_guard.resolve_max_concurrent("32"), 32)
            self.assertEqual(equipment_guard.resolve_max_concurrent("33"), 32)
            self.assertEqual(equipment_guard.resolve_max_concurrent(999), 32)

        with patch.dict(os.environ, {"FAM_EQUIPMENT_MAX_CONCURRENT": "4"}):
            self.assertEqual(equipment_guard.resolve_max_concurrent(), 4)
        with patch.dict(os.environ, {"FAM_EQUIPMENT_MAX_CONCURRENT": "-2"}):
            self.assertEqual(equipment_guard.resolve_max_concurrent(), 8)
        with patch.dict(os.environ, {"FAM_EQUIPMENT_MAX_CONCURRENT": "64"}):
            self.assertEqual(equipment_guard.resolve_max_concurrent(), 32)
        with patch.dict(os.environ, {"FAM_EQUIPMENT_MAX_CONCURRENT": "not-an-int"}):
            self.assertEqual(equipment_guard.resolve_max_concurrent(), 8)

    def test_per_host_exclusive_lock_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = equipment_guard.EquipmentGuard(Path(tmpdir) / "guard.sqlite3", maximum=8)
            with guard.admit("10.10.10.1"):
                with self.assertRaises(equipment_guard.AdmissionError) as ctx:
                    with guard.admit("10.10.10.1"):
                        pass
                self.assertEqual(ctx.exception.code, "equipment_busy")
            # Released cleanly
            with guard.admit("10.10.10.1"):
                pass

    def test_multithreaded_global_concurrency_cap_race(self):
        # SQLite triggers observe the table at the actual INSERT and DELETE,
        # within the same serialized transaction as the lease mutation.
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "race.sqlite3"
            guard = equipment_guard.EquipmentGuard(path, maximum=3)
            with sqlite3.connect(path) as db:
                db.executescript("""
                    CREATE TABLE lease_events (action TEXT, n INTEGER);
                    CREATE TRIGGER lease_added AFTER INSERT ON equipment_leases BEGIN
                        INSERT INTO lease_events VALUES ('insert', (SELECT COUNT(*) FROM equipment_leases));
                    END;
                    CREATE TRIGGER lease_removed AFTER DELETE ON equipment_leases BEGIN
                        INSERT INTO lease_events VALUES ('delete', (SELECT COUNT(*) FROM equipment_leases));
                    END;
                """)

            admitted, busy, errors = [], [], []
            lock = threading.Lock()
            # All workers in each wave attempt admission while successful workers
            # remain in their contexts; the main thread alone releases them.
            for wave in range(2):
                start = threading.Barrier(9)
                release = threading.Event()
                finished_attempts = threading.Condition()
                attempts = [0]

                def worker(idx):
                    reported = False
                    try:
                        start.wait(timeout=10)
                        with guard.admit(f"10.20.{wave}.{idx + 1}"):
                            with lock:
                                admitted.append((wave, idx))
                            with finished_attempts:
                                attempts[0] += 1
                                reported = True
                                finished_attempts.notify_all()
                            if not release.wait(timeout=15):
                                raise TimeoutError("lease release not signalled")
                    except equipment_guard.AdmissionError as exc:
                        with lock:
                            busy.append(exc.code)
                    except BaseException as exc:
                        with lock:
                            errors.append(repr(exc))
                    finally:
                        if not reported:
                            with finished_attempts:
                                attempts[0] += 1
                                finished_attempts.notify_all()

                threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
                for thread in threads:
                    thread.start()
                try:
                    start.wait(timeout=10)
                    with finished_attempts:
                        all_attempted = finished_attempts.wait_for(lambda: attempts[0] == 8, timeout=12)
                    self.assertTrue(all_attempted, "workers did not finish admission attempts")
                    with sqlite3.connect(path) as db:
                        self.assertEqual(db.execute("SELECT COUNT(*) FROM equipment_leases").fetchone()[0], 3)
                finally:
                    release.set()
                    for thread in threads:
                        thread.join(timeout=20)
                self.assertFalse(any(thread.is_alive() for thread in threads))

            self.assertEqual(errors, [])
            self.assertEqual(len(admitted), 6)  # total across both waves, not simultaneous
            self.assertEqual(busy, ["equipment_busy"] * 10)
            with sqlite3.connect(path) as db:
                events = db.execute("SELECT action, n FROM lease_events ORDER BY rowid").fetchall()
                self.assertEqual(db.execute("SELECT COUNT(*) FROM equipment_leases").fetchone()[0], 0)
            self.assertEqual(sum(action == "insert" for action, _ in events), 6)
            self.assertEqual(sum(action == "delete" for action, _ in events), 6)
            self.assertEqual(max(n for _, n in events), 3)
            self.assertTrue(all(0 <= n <= 3 for _, n in events))

    @unittest.skipUnless(HAS_FLASK, "Flask is not installed in this Python environment")
    def test_app_wires_fam_equipment_max_concurrent_from_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "cfg.sqlite3"
            with patch.dict(
                os.environ,
                {
                    "FAM_DB": str(db_path),
                    "FAM_PUBLIC_ORIGIN": "https://fam-test.local",
                    "FAM_EQUIPMENT_MAX_CONCURRENT": "5",
                },
            ):
                app = fam_app_module.create_app({"TESTING": True, "DB_PATH": str(db_path), "PUBLIC_ORIGIN": "https://fam-test.local"})
            self.assertEqual(app.extensions["equipment_guard"].maximum, 5)


@unittest.skipUnless(HAS_FLASK, "Flask is not installed in this Python environment")
class FamEquipmentAuditAndBranchSiteTests(unittest.TestCase):
    ORIGIN = "https://fam-test.local"
    ADMIN_PASSWORD = "TestAdminPassword!2026"

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "audit_fam.sqlite3"
        self.env_patch = patch.dict(
            os.environ,
            {
                "FAM_DB": str(self.db_path),
                "FAM_PUBLIC_ORIGIN": self.ORIGIN,
                "FAM_INITIAL_PASSWORD": self.ADMIN_PASSWORD,
                "FAM_EQUIPMENT_OPS_ENABLED": "1",
            },
        )
        self.env_patch.start()
        self.app = fam_app_module.create_app(
            {
                "TESTING": True,
                "DB_PATH": str(self.db_path),
                "PUBLIC_ORIGIN": self.ORIGIN,
                "EQUIPMENT_OPS_ENABLED": True,
            }
        )
        self.client = self.app.test_client()
        self.https_env = {"wsgi.url_scheme": "https", "HTTP_HOST": "fam-test.local"}

    def tearDown(self):
        self.env_patch.stop()
        self.tmpdir.cleanup()

    def _login(self, username, password):
        res = self.client.post(
            "/api/login",
            json={"username": username, "password": password},
            headers={"Origin": self.ORIGIN},
            environ_base=self.https_env,
        )
        self.assertEqual(res.status_code, 200)
        return res.get_json()

    def test_audit_records_success_failure_without_secrets_enforces_admin_and_is_append_only(self):
        admin_login = self._login("admin", self.ADMIN_PASSWORD)
        admin_csrf = admin_login["csrf"]

        # Create a non-admin operator who holds equipment-operations, equipment-scan,
        # equipment-audit, and clear-history — must STILL be forbidden from /api/equipment/audit.
        users_res = self.client.get("/api/users", environ_base=self.https_env).get_json()
        op_id = "operator-0001-test"
        op_pw = "OperatorPass!2026"
        new_users = users_res["users"] + [
            {
                "id": op_id,
                "username": "netop",
                "name": "Network Operator",
                "enabled": True,
                "regions": ["1"],
                "sheets": [],
                "categories": ["equipment"],
                "permissions": [
                    "view-history",
                    "clear-history",
                    "equipment-operations",
                    "equipment-scan",
                    "equipment-audit",
                ],
                "equipmentScope": {
                    "types": ["*"],
                    "models": ["*"],
                    "regions": ["*"],
                    "siteKinds": ["*"],
                    "sites": ["*"],
                },
                "password": op_pw,
            }
        ]
        save_users = self.client.post(
            "/api/users",
            json={"revision": users_res["revision"], "users": new_users},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": admin_csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(save_users.status_code, 200)

        secret_pw = "SuperSecretDevicePass!99"
        secret_enable = "EnableSecret!88"
        cli_snippet = "Fa0/1   up   up   CLIENT-PORT-SECRET-DESC"

        # 1) Mocked SSH success + failure under operator session
        op_login = self._login("netop", op_pw)
        op_csrf = op_login["csrf"]

        with patch("equipment_ops._execute") as mock_exec:
            mock_exec.return_value = {
                "ok": True,
                "output": f"Interface Status Protocol Description\n{cli_snippet}\n",
                "redacted": False,
            }
            ok_res = self.client.post(
                "/api/equipment/descriptions",
                json={
                    "host": "10.10.20.5",
                    "username": "netuser",
                    "password": secret_pw,
                    "enable": secret_enable,
                },
                headers={"Origin": self.ORIGIN, "X-FAM-CSRF": op_csrf},
                environ_base=self.https_env,
            )
            self.assertEqual(ok_res.status_code, 200)

            mock_exec.return_value = {"ok": False, "error": "authentication_failed"}
            fail_res = self.client.post(
                "/api/equipment/check",
                json={
                    "host": "10.10.20.6",
                    "username": "netuser",
                    "password": secret_pw,
                },
                headers={"Origin": self.ORIGIN, "X-FAM-CSRF": op_csrf},
                environ_base=self.https_env,
            )
            self.assertEqual(fail_res.status_code, 502)

        # Operator cannot read /api/equipment/audit even with equipment-audit permission
        op_audit = self.client.get(
            "/api/equipment/audit",
            headers={"X-FAM-CSRF": op_csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(op_audit.status_code, 403)

        # Operator calling /api/history/clear cannot affect equipment_audit
        clear_res = self.client.post(
            "/api/history/clear",
            json={"confirm": True},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": op_csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(clear_res.status_code, 200)

        # Admin reads /api/equipment/audit and verifies contents
        self._login("admin", self.ADMIN_PASSWORD)
        admin_csrf = self.client.get("/api/session", environ_base=self.https_env).get_json()["csrf"]
        admin_clear = self.client.post(
            "/api/history/clear",
            json={"confirm": True},
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": admin_csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(admin_clear.status_code, 200)

        audit_res = self.client.get(
            "/api/equipment/audit?limit=50",
            headers={"X-FAM-CSRF": admin_csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(audit_res.status_code, 200)
        audit_body = audit_res.get_json()
        self.assertEqual(audit_body["total"], 2)
        serialized = json.dumps(audit_body)
        for sensitive in (secret_pw, secret_enable, cli_snippet, "CLIENT-PORT-SECRET-DESC", "netuser"):
            self.assertNotIn(sensitive, serialized)

        items = audit_body["items"]
        self.assertEqual(items[0]["operation"], "status")
        self.assertEqual(items[0]["host"], "10.10.20.6")
        self.assertEqual(items[0]["outcome"], "failed")
        self.assertEqual(items[0]["code"], "authentication_failed")
        self.assertEqual(items[0]["username"], "netop")

        self.assertEqual(items[1]["operation"], "descriptions")
        self.assertEqual(items[1]["host"], "10.10.20.5")
        self.assertEqual(items[1]["outcome"], "success")
        self.assertEqual(items[1]["code"], "ok")
        self.assertEqual(items[1]["username"], "netop")

        # Verify SQLite append-only triggers reject UPDATE and DELETE
        with sqlite3.connect(self.db_path) as db:
            with self.assertRaises(sqlite3.DatabaseError):
                db.execute("UPDATE equipment_audit SET outcome='success'")
            with self.assertRaises(sqlite3.DatabaseError):
                db.execute("DELETE FROM equipment_audit")

    def test_branch_equipment_supports_optional_and_selected_site(self):
        admin_login = self._login("admin", self.ADMIN_PASSWORD)
        csrf = admin_login["csrf"]
        eq_state = self.client.get("/api/equipment/state", environ_base=self.https_env).get_json()
        inv = eq_state["inventory"]
        inv["catalog"]["sites"].append({"id": "branch-site-1", "name": "شعبه مرکزی", "siteKindId": "kind-branch"})
        inv["nodes"] = [
            {
                "id": "node-branch-no-site",
                "name": "Branch Switch No Site",
                "host": "10.30.1.1",
                "typeId": "type-switch",
                "modelId": "model-2960",
                "regionId": "region-1",
                "siteKindId": "kind-branch",
                "siteId": None,
            },
            {
                "id": "node-branch-with-site",
                "name": "Branch Switch With Site",
                "host": "10.30.1.2",
                "typeId": "type-switch",
                "modelId": "model-2960",
                "regionId": "region-1",
                "siteKindId": "kind-branch",
                "siteId": "branch-site-1",
            },
        ]
        save_res = self.client.post(
            "/api/equipment/state",
            json={
                "revision": eq_state["revision"],
                "requestId": str(uuid.uuid4()),
                "kind": "inventory",
                "value": inv,
            },
            headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
            environ_base=self.https_env,
        )
        self.assertEqual(save_res.status_code, 200)
        saved_nodes = {n["id"]: n for n in save_res.get_json()["inventory"]["nodes"]}
        self.assertIsNone(saved_nodes["node-branch-no-site"]["siteId"])
        self.assertEqual(saved_nodes["node-branch-with-site"]["siteId"], "branch-site-1")

    def test_diagnose_and_mac_recovery_apply_return_428_on_enable_required(self):
        admin_login = self._login("admin", self.ADMIN_PASSWORD)
        csrf = admin_login["csrf"]
        with patch("equipment_ops._execute") as mock_exec:
            mock_exec.return_value = {"ok": False, "error": "enable_required"}
            diag_res = self.client.post(
                "/api/equipment/diagnose",
                json={
                    "host": "10.10.20.5",
                    "username": "netuser",
                    "password": "SwitchPass!2026",
                    "clientIp": "10.10.20.99",
                    "clientMac": "",
                },
                headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
                environ_base=self.https_env,
            )
            self.assertEqual(diag_res.status_code, 428)

            valid_plan = {
                "interface": "Fa0/1",
                "reason": "psecure-violation",
                "macPolicy": "clear-and-relearn",
                "maximum": 1,
                "total": 1,
                "violations": 2,
                "planHash": "a" * 64,
            }
            mock_exec.side_effect = [
                {"ok": True, "plan": valid_plan},
                {"ok": False, "error": "enable_required"},
            ]
            plan_res = self.client.post(
                "/api/equipment/mac-recovery/plan",
                json={
                    "host": "10.10.20.5",
                    "username": "netuser",
                    "password": "SwitchPass!2026",
                    "interface": "Fa0/1",
                },
                headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
                environ_base=self.https_env,
            )
            self.assertEqual(plan_res.status_code, 200)
            ticket = plan_res.get_json()["ticket"]

            apply_res = self.client.post(
                "/api/equipment/mac-recovery/apply",
                json={
                    "host": "10.10.20.5",
                    "username": "netuser",
                    "password": "SwitchPass!2026",
                    "interface": "Fa0/1",
                    "planHash": "a" * 64,
                    "ticket": ticket,
                },
                headers={"Origin": self.ORIGIN, "X-FAM-CSRF": csrf},
                environ_base=self.https_env,
            )
            self.assertEqual(apply_res.status_code, 428)
            self.assertEqual(apply_res.get_json().get("code"), "enable_required")


if __name__ == "__main__":
    unittest.main()
