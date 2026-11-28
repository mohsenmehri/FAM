"""Disposable sandbox integration tests for deploy_vm.sh and rollback_vm.sh.

Runs strictly inside tempfile.TemporaryDirectory() with a local bare Git origin,
a real WAL-mode SQLite database, and a deterministic fake `docker` shim in PATH.
Never touches any real VM, real Docker daemon, or production data.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sqlite3
import stat
import subprocess
import tempfile
import unittest

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
DEPLOY_SCRIPT = TOOLS_DIR / "deploy_vm.sh"
ROLLBACK_SCRIPT = TOOLS_DIR / "rollback_vm.sh"

FAKE_DOCKER = r"""#!/usr/bin/env python3
import os, sys
from pathlib import Path

state_file = Path(os.environ["FAKE_DOCKER_STATE"])
log_file = Path(os.environ["FAKE_DOCKER_LOG"])
args = sys.argv[1:]
with log_file.open("a", encoding="utf-8") as fh:
    fh.write(" ".join(args) + "\n")

if args[:2] != ["compose", "stop"] and args[:2] != ["compose", "ps"] and args[:2] != ["compose", "build"] and args[:2] != ["compose", "up"] and args[:2] != ["compose", "exec"]:
    sys.exit(0)

cmd = args[1]
if cmd == "stop":
    if os.environ.get("FAKE_FAIL_STOP") == "1":
        sys.stderr.write("simulated docker compose stop error\n")
        sys.exit(1)
    if os.environ.get("FAKE_STOP_LEAVES_RUNNING") == "1":
        sys.exit(0)
    state_file.write_text("STOPPED", encoding="utf-8")
    sys.exit(0)

if cmd == "ps":
    st = state_file.read_text(encoding="utf-8").strip() if state_file.exists() else "STOPPED"
    if "-q" in args and "--status" in args and "running" in args:
        if st == "RUNNING":
            print("fake-app-container-id")
        sys.exit(0)
    print(f"app   {st}")
    sys.exit(0)

if cmd == "build":
    if os.environ.get("FAKE_FAIL_BUILD") == "1":
        sys.stderr.write("simulated docker compose build failure\n")
        sys.exit(1)
    sys.exit(0)

if cmd == "up":
    if os.environ.get("FAKE_FAIL_UP") == "1":
        sys.stderr.write("simulated docker compose up failure\n")
        sys.exit(1)
    state_file.write_text("RUNNING", encoding="utf-8")
    sys.exit(0)

if cmd == "exec":
    if os.environ.get("FAKE_FAIL_HEALTH") == "1":
        sys.stderr.write("simulated healthcheck failure\n")
        sys.exit(1)
    print("APP HTTP: 200")
    sys.exit(0)
"""


def _git(cwd: Path, *args: str) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )
    return res.stdout.strip()


def _write_manifest(app_dir: Path) -> None:
    files = sorted(
        p.relative_to(app_dir).as_posix()
        for p in app_dir.rglob("*")
        if p.is_file()
        and p.name != "MANIFEST.sha256"
        and not p.relative_to(app_dir).parts[0] in ("data", "certs")
        and p.name != ".env"
    )
    res = subprocess.run(
        ["sha256sum", *[f"./{f}" for f in files]],
        cwd=str(app_dir),
        capture_output=True,
        text=True,
        check=True,
    )
    (app_dir / "MANIFEST.sha256").write_text(res.stdout, encoding="utf-8")


class DeployRollbackSandboxTests(unittest.TestCase):
    def _build_sandbox(self, tmp: Path):
        origin = tmp / "origin.git"
        origin.mkdir()
        _git(origin, "init", "--bare", "-b", "main")

        repo = tmp / "FAM"
        _git(tmp, "clone", str(origin), str(repo))
        _git(repo, "checkout", "-b", "main")

        (repo / ".gitignore").write_text(
            "01-خام-پروژه/.env\n01-خام-پروژه/certs/\n01-خام-پروژه/data/\n",
            encoding="utf-8",
        )
        app_dir = repo / "01-خام-پروژه"
        (app_dir / "tools").mkdir(parents=True)
        (app_dir / "docker-compose.yml").write_text("services:\n  app:\n    image: fam-app:1.0\n", encoding="utf-8")
        (app_dir / "version.txt").write_text("v1-old\n", encoding="utf-8")
        shutil.copy2(DEPLOY_SCRIPT, app_dir / "tools/deploy_vm.sh")
        shutil.copy2(ROLLBACK_SCRIPT, app_dir / "tools/rollback_vm.sh")
        _write_manifest(app_dir)
        _git(repo, "add", ".")
        _git(repo, "commit", "-m", "v1 baseline")
        _git(repo, "push", "-u", "origin", "main")
        prev_sha = _git(repo, "rev-parse", "HEAD")

        # Create target branch v2 commit on origin via separate temp clone
        pusher = tmp / "pusher"
        _git(tmp, "clone", str(origin), str(pusher))
        _git(pusher, "checkout", "-b", "arena/test-target")
        p_app = pusher / "01-خام-پروژه"
        (p_app / "version.txt").write_text("v2-new\n", encoding="utf-8")
        _write_manifest(p_app)
        _git(pusher, "add", ".")
        _git(pusher, "commit", "-m", "v2 release candidate")
        _git(pusher, "push", "-u", "origin", "arena/test-target")
        target_sha = _git(pusher, "rev-parse", "HEAD")

        # Create ignored runtime files + real WAL-mode SQLite DB on VM repo
        (app_dir / ".env").write_text("FAM_PUBLIC_ORIGIN=https://fam.local\n", encoding="utf-8")
        (app_dir / "certs").mkdir()
        (app_dir / "certs/server.crt").write_text("OLD-CERT\n", encoding="utf-8")
        (app_dir / "data").mkdir()
        (app_dir / "data/equipment_known_hosts").write_text("10.0.0.1 ssh-ed25519 AAAA\n", encoding="utf-8")
        db_path = app_dir / "data/fam.sqlite3"
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT);")
        conn.execute("INSERT INTO users(username) VALUES ('admin'), ('student1');")
        conn.commit()
        conn.close()

        # Fake docker shim in PATH
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        docker_bin = bin_dir / "docker"
        docker_bin.write_text(FAKE_DOCKER, encoding="utf-8")
        docker_bin.chmod(docker_bin.stat().st_mode | stat.S_IXUSR)
        state_file = tmp / "docker.state"
        state_file.write_text("RUNNING", encoding="utf-8")
        log_file = tmp / "docker.log"
        backups = tmp / "backups"
        backups.mkdir()

        base_env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "FAM_REPO_DIR": str(repo),
            "FAM_TARGET_BRANCH": "arena/test-target",
            "FAM_TARGET_SHA": target_sha,
            "FAM_BACKUP_BASE": str(backups),
            "FAKE_DOCKER_STATE": str(state_file),
            "FAKE_DOCKER_LOG": str(log_file),
        }
        return repo, app_dir, prev_sha, target_sha, backups, state_file, base_env

    def test_preflight_blocks_dirty_tree_unpushed_and_divergent_branch_without_stopping_service(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, prev_sha, target_sha, _, state_file, env = self._build_sandbox(Path(td))
            # 1. Untracked file blocks before docker stop
            (repo / "stray.txt").write_text("oops", encoding="utf-8")
            r = subprocess.run([str(DEPLOY_SCRIPT)], env=env, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("SERVICE_STATE=RUNNING_UNCHANGED", r.stderr)
            self.assertEqual(state_file.read_text(), "RUNNING")
            (repo / "stray.txt").unlink()

            # 2. Divergent local commit on target branch blocks (NO git checkout -B overwrite!)
            _git(repo, "checkout", "-b", "arena/test-target", prev_sha)
            (repo / "local_only.txt").write_text("keep-me", encoding="utf-8")
            _git(repo, "add", "local_only.txt")
            _git(repo, "commit", "-m", "local divergent commit")
            div_sha = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "main")

            r2 = subprocess.run([str(DEPLOY_SCRIPT)], env=env, capture_output=True, text=True)
            self.assertNotEqual(r2.returncode, 0)
            self.assertIn("SERVICE_STATE=RUNNING_UNCHANGED", r2.stderr)
            self.assertEqual(state_file.read_text(), "RUNNING")
            self.assertEqual(_git(repo, "rev-parse", "arena/test-target"), div_sha)

    def test_stop_failure_or_lingering_container_aborts_before_backup(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, _, _, backups, state_file, env = self._build_sandbox(Path(td))
            r1 = subprocess.run([str(DEPLOY_SCRIPT)], env={**env, "FAKE_FAIL_STOP": "1"}, capture_output=True, text=True)
            self.assertNotEqual(r1.returncode, 0)
            self.assertIn("SERVICE_STATE=STOP_FAILED_CHECK_DOCKER", r1.stderr)
            self.assertEqual(list(backups.iterdir()), [])
            self.assertEqual(state_file.read_text(), "RUNNING")

            r2 = subprocess.run([str(DEPLOY_SCRIPT)], env={**env, "FAKE_STOP_LEAVES_RUNNING": "1"}, capture_output=True, text=True)
            self.assertNotEqual(r2.returncode, 0)
            self.assertIn("SERVICE_STATE=STOP_FAILED_CHECK_DOCKER", r2.stderr)
            self.assertEqual(list(backups.iterdir()), [])

    def test_failure_after_stop_at_build_leaves_service_stopped_and_rollback_recovers_cleanly(self):
        with tempfile.TemporaryDirectory() as td:
            repo, app_dir, prev_sha, target_sha, backups, state_file, env = self._build_sandbox(Path(td))
            # Fail after stop & code update during `docker compose build`
            r = subprocess.run([str(DEPLOY_SCRIPT)], env={**env, "FAKE_FAIL_BUILD": "1"}, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("DEPLOY FAILED at step: 10a-build-image", r.stderr)
            self.assertIn("SERVICE_STATE=STOPPED_CODE_UPDATED_NEEDS_ROLLBACK_OR_RETRY", r.stderr)
            self.assertIn("ROLLBACK_CMD=", r.stderr)
            self.assertEqual(state_file.read_text(), "STOPPED")
            self.assertEqual(_git(repo, "rev-parse", "HEAD"), target_sha)

            backup_dirs = list(backups.glob("fam-upgrade-*"))
            self.assertEqual(len(backup_dirs), 1)
            backup_root = backup_dirs[0]

            # Execute rollback_vm.sh to recover cleanly
            rb = subprocess.run([str(ROLLBACK_SCRIPT), str(backup_root)], env=env, capture_output=True, text=True)
            self.assertEqual(rb.returncode, 0, rb.stderr + rb.stdout)
            self.assertIn("SERVICE_STATE=RUNNING_ROLLED_BACK", rb.stdout)
            self.assertEqual(state_file.read_text(), "RUNNING")
            self.assertEqual(_git(repo, "rev-parse", "HEAD"), prev_sha)
            self.assertEqual(_git(repo, "rev-parse", "--abbrev-ref", "HEAD"), "main")
            self.assertEqual((app_dir / "version.txt").read_text(), "v1-old\n")

    def test_failure_after_up_at_healthcheck_reports_running_unhealthy_and_rollback_recovers(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, prev_sha, _, backups, state_file, env = self._build_sandbox(Path(td))
            r = subprocess.run([str(DEPLOY_SCRIPT)], env={**env, "FAKE_FAIL_HEALTH": "1"}, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("DEPLOY FAILED at step: 10c-healthcheck", r.stderr)
            self.assertIn("SERVICE_STATE=RUNNING_UNHEALTHY_NEEDS_ROLLBACK_OR_INSPECTION", r.stderr)
            self.assertEqual(state_file.read_text(), "RUNNING")
            backup_root = next(backups.glob("fam-upgrade-*"))
            rb = subprocess.run([str(ROLLBACK_SCRIPT), str(backup_root)], env=env, capture_output=True, text=True)
            self.assertEqual(rb.returncode, 0, rb.stderr + rb.stdout)
            self.assertIn("SERVICE_STATE=RUNNING_ROLLED_BACK", rb.stdout)
            self.assertEqual(_git(repo, "rev-parse", "HEAD"), prev_sha)

    def test_full_deploy_post_backup_writes_and_rollback_restores_db_and_reports_extra_files(self):
        with tempfile.TemporaryDirectory() as td:
            repo, app_dir, prev_sha, target_sha, backups, state_file, env = self._build_sandbox(Path(td))
            r = subprocess.run([str(DEPLOY_SCRIPT)], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            self.assertIn("SERVICE_STATE=RUNNING_UPGRADED", r.stdout)
            self.assertEqual(state_file.read_text(), "RUNNING")
            self.assertEqual(_git(repo, "rev-parse", "HEAD"), target_sha)

            # Simulate post-upgrade writes (new user + edited .env + extra file under data/tmp)
            conn = sqlite3.connect(str(app_dir / "data/fam.sqlite3"))
            conn.execute("INSERT INTO users(username) VALUES ('post_upgrade_user');")
            conn.commit()
            conn.close()
            (app_dir / ".env").write_text("FAM_PUBLIC_ORIGIN=https://changed.local\n", encoding="utf-8")
            (app_dir / "data/tmp").mkdir(exist_ok=True)
            (app_dir / "data/tmp/post-backup.log").write_text("temp", encoding="utf-8")

            backup_root = next(backups.glob("fam-upgrade-*"))
            rb = subprocess.run([str(ROLLBACK_SCRIPT), str(backup_root)], env=env, capture_output=True, text=True)
            self.assertEqual(rb.returncode, 0, rb.stderr + rb.stdout)
            self.assertIn("SERVICE_STATE=RUNNING_ROLLED_BACK", rb.stdout)
            self.assertIn("./tmp/post-backup.log", rb.stdout)

            # Verify DB rolled back cleanly to pre-upgrade snapshot
            conn = sqlite3.connect(str(app_dir / "data/fam.sqlite3"))
            users = [row[0] for row in conn.execute("SELECT username FROM users ORDER BY id;").fetchall()]
            chk = conn.execute("PRAGMA integrity_check;").fetchall()
            conn.close()
            self.assertEqual(users, ["admin", "student1"])
            self.assertEqual(chk, [("ok",)])
            self.assertEqual((app_dir / ".env").read_text(), "FAM_PUBLIC_ORIGIN=https://fam.local\n")
            self.assertEqual(_git(repo, "rev-parse", "HEAD"), prev_sha)


if __name__ == "__main__":
    unittest.main()
