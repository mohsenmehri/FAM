"""Local Real Git Workflow Lab for auto_04 (runs real git commands inside a temporary directory).

Modifies ONLY an isolated temporary directory; never touches your project repository or remotes.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile


def run_git(repo: Path, *args: str) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.strip()


def simulate_safe_git_workflow() -> dict[str, object]:
    """Execute real git init, .gitignore check, branching, commit, and non-destructive git revert."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        run_git(repo, "init", "-b", "main")
        run_git(repo, "config", "user.name", "FAM Lab Learner")
        run_git(repo, "config", "user.email", "learner@example.invalid")

        (repo / ".gitignore").write_text(".env\n*.key\n", encoding="utf-8")
        (repo / ".env").write_text("ROUTER_PASS=never-commit-me\n", encoding="utf-8")
        (repo / "ntp.cfg").write_text("ntp server 192.0.2.123\n", encoding="utf-8")

        run_git(repo, "add", ".gitignore", "ntp.cfg")
        run_git(repo, "commit", "-m", "Add baseline NTP config and .gitignore")

        ignored_check = run_git(repo, "status", "--porcelain")
        env_ignored = ".env" not in ignored_check

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
    print("Real local git executed ONLY in an isolated temporary directory; no remote or router touched.")
    print(simulate_safe_git_workflow())


if __name__ == "__main__":
    main()
