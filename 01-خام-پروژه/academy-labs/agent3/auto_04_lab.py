"""Local Real Git Workflow Lab for auto_04 (runs real git commands inside a temporary directory).

Uses a temporary repository and restricted Git environment; no remote or network device is used.
Not an OS-level sandbox: run only a trusted local Git binary in a trusted environment.
"""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import tempfile


def run_git(repo: Path, *args: str) -> str:
    # Do not inherit GIT_DIR, GIT_CONFIG_*, hooks, user config or templates.
    env = {
        "PATH": os.defpath, "HOME": str(repo), "XDG_CONFIG_HOME": str(repo / "xdg"),
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(repo / "no-global-config"),
        "GIT_TEMPLATE_DIR": str(repo / "empty-template"), "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "core.hooksPath",
        "GIT_CONFIG_VALUE_0": str(repo / "empty-hooks"),
        "GIT_CONFIG_KEY_1": "commit.gpgsign", "GIT_CONFIG_VALUE_1": "false",
        "LC_ALL": "C",
    }
    res = subprocess.run(
        ["git", *args], cwd=repo, env=env, capture_output=True,
        text=True, check=True, timeout=15,
    )
    return res.stdout.strip()


def simulate_safe_git_workflow() -> dict[str, object]:
    """Execute real git init, .gitignore check, branching, commit, and non-destructive git revert."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "empty-template").mkdir()
        (repo / "empty-hooks").mkdir()
        run_git(repo, "init", "-b", "main")
        run_git(repo, "config", "user.name", "FAM Lab Learner")
        run_git(repo, "config", "user.email", "learner@example.invalid")

        (repo / ".gitignore").write_text(".env\n*.key\n", encoding="utf-8")
        (repo / ".env").write_text("ROUTER_PASS=never-commit-me\n", encoding="utf-8")
        (repo / "ntp.cfg").write_text("ntp server 192.0.2.123\n", encoding="utf-8")

        run_git(repo, "add", ".gitignore", "ntp.cfg")
        run_git(repo, "commit", "-m", "Add baseline NTP config and .gitignore")

        ignored_check = run_git(repo, "check-ignore", "--", ".env")
        env_ignored = ignored_check == ".env"

        # Feature branch + intentional bad commit + safe revert
        run_git(repo, "switch", "-c", "feature/acl-change")
        (repo / "ntp.cfg").write_text("ntp server 192.0.2.123\nno ntp authenticate\n", encoding="utf-8")
        run_git(repo, "add", "ntp.cfg")
        run_git(repo, "commit", "-m", "Bad config change to revert")
        bad_sha = run_git(repo, "rev-parse", "--short", "HEAD")

        run_git(repo, "revert", "--no-edit", "HEAD")
        log_lines = run_git(repo, "log", "--oneline").splitlines()
        final_content = (repo / "ntp.cfg").read_text(encoding="utf-8").strip()

        return {
            "env_ignored_by_gitignore": env_ignored,
            "bad_commit_short_sha": bad_sha,
            "commit_count_after_revert": len(log_lines),
            "history_preserved_with_revert": len(log_lines) == 3,
            "restored_ntp_cfg": final_content,
        }


def main() -> None:
    print("Real local git runs in a temporary repository with a restricted Git environment; no remote or router used.")
    print(simulate_safe_git_workflow())


if __name__ == "__main__":
    main()
