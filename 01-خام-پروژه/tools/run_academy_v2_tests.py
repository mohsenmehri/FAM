#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the complete dependency-free FAM Academy v2 verification suite.

It starts an ephemeral preview HTTP server, executes the validator, all Python
unittest files, Node engine tests, and the SPA integration test both against
local JSON fixtures and against the real preview HTTP API. It writes a compact
Markdown summary and a full log file to reports/. No package installation,
Flask service, browser automation, VM, Docker or network device is used.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
SERVER = PROJECT / "server"
TOOLS = PROJECT / "tools"
TESTS = PROJECT / "tests"
REPORTS = REPO / "reports"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))
import academy_preview_server as preview  # noqa: E402

REPORTS.mkdir(parents=True, exist_ok=True)
SUMMARY_PATH = REPORTS / "academy-v2-verification.md"
LOG_PATH = REPORTS / "academy-v2-test-logs.txt"
NODE = shutil.which("node") or "node"


def run(name, command, env=None, cwd=PROJECT, timeout=300):
    merged = os.environ.copy()
    merged.pop("ACADEMY_V2_API_BASE", None)
    if env:
        merged.update(env)
    try:
        proc = subprocess.run(command, cwd=str(cwd), env=merged, text=True, capture_output=True, timeout=timeout)
        result = {
            "name": name,
            "command": " ".join(str(x) for x in command),
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except Exception as exc:  # pragma: no cover - reports environment failure
        result = {"name": name, "command": " ".join(str(x) for x in command), "returncode": 1, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    return result


def last_lines(text, count=12):
    lines = text.splitlines()
    return "\n".join(lines[-count:]).strip()


def parse_unittest(result):
    m = re.search(r"Ran (\d+) tests", result["stdout"] + result["stderr"])
    return int(m.group(1)) if m else None


def parse_node(result):
    text = result["stdout"] + result["stderr"]
    passed = re.search(r"# pass (\d+)", text)
    failed = re.search(r"# fail (\d+)", text)
    return (int(passed.group(1)) if passed else None, int(failed.group(1)) if failed else None)


def git(*args):
    return subprocess.run(["git", *args], cwd=str(REPO), text=True, capture_output=True).stdout.strip()


def main() -> int:
    server = preview.make_server("127.0.0.1", 0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    api_base = f"http://127.0.0.1:{port}"
    print(f"verification preview server: {api_base}", flush=True)

    results = []
    try:
        results.append(run("content validator", [sys.executable, "-B", str(TOOLS / "validate_academy_v2.py"), "--json"]))
        results.append(run("python unittest suite", [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TESTS), "-p", "test_*.py", "-v"]))
        results.append(run("node engine tests", [NODE, "--test", str(TESTS / "test_academy_v2_engine.test.mjs")]))
        results.append(run("node syntax checks", [NODE, "--check", str(SERVER / "www" / "academy-assets" / "academy-engine.js")]))
        results.append(run("node SPA syntax check", [NODE, "--check", str(SERVER / "www" / "academy-assets" / "academy-v2.js")]))
        results.append(run("SPA UI flow (file fixtures)", [NODE, "--test", str(TESTS / "test_academy_v2_ui.test.mjs")]))
        results.append(run("SPA UI flow (live preview HTTP API)", [NODE, "--test", str(TESTS / "test_academy_v2_ui.test.mjs")], env={"ACADEMY_V2_API_BASE": api_base}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    validator_json = {}
    try:
        validator_json = json.loads(results[0]["stdout"])
    except Exception:
        pass
    all_ok = all(r["returncode"] == 0 for r in results)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    head = git("rev-parse", "HEAD")
    status = git("status", "--short", "-uall")
    status_lines = [line for line in status.splitlines() if line.strip()]

    with LOG_PATH.open("w", encoding="utf-8") as log:
        log.write(f"FAM Academy v2 verification log — {timestamp}\n")
        log.write(f"Preview API base: {api_base}\n")
        log.write(f"Branch: {branch} HEAD: {head}\n")
        for result in results:
            log.write("\n" + "=" * 80 + "\n")
            log.write(f"COMMAND: {result['command']}\nRETURN CODE: {result['returncode']}\n")
            log.write("\n--- STDOUT ---\n" + result["stdout"])
            log.write("\n--- STDERR ---\n" + result["stderr"] + "\n")
        log.write("\n" + "=" * 80 + "\nGIT STATUS --short -uall\n" + status + "\n")

    lines = [
        "# FAM Academy v2 — verification report",
        "",
        f"- Generated: `{timestamp}`",
        f"- Overall: **{'PASS' if all_ok else 'FAIL'}**",
        f"- Branch / HEAD: `{branch}` / `{head}`",
        f"- Preview API used during tests: `{api_base}` (ephemeral, stopped after tests)",
        "- Browser visual automation: **not run** — Chromium/Playwright/Selenium are unavailable; a DOM-shim SPA flow test was run instead.",
        "",
        "## Command results",
        "",
        "| Check | Result | Details |",
        "|---|---:|---|",
    ]
    for result in results:
        detail = ""
        if result["name"] == "content validator" and validator_json:
            counts = validator_json.get("counts", {})
            detail = f"validator ok={validator_json.get('ok')}; checks={len(validator_json.get('checks', []))}; errors={len(validator_json.get('errors', []))}; lessons={counts.get('lessons')}; sims={counts.get('simulations')}; labs={counts.get('labs')}"
        elif result["name"] == "python unittest suite":
            n = parse_unittest(result)
            skipped = re.search(r"skipped=(\d+)", result["stdout"] + result["stderr"])
            detail = f"Ran {n} tests" + (f"; skipped={skipped.group(1)}" if skipped else "")
        elif "node" in result["name"].lower() and "syntax" not in result["name"]:
            passed, failed = parse_node(result)
            detail = f"node pass={passed}; fail={failed}"
        else:
            detail = "exit 0" if result["returncode"] == 0 else "see log"
        lines.append(f"| {result['name']} | {'PASS' if result['returncode'] == 0 else 'FAIL'} | {detail} |")

    lines += [
        "",
        "## Exact command tails",
        "",
    ]
    for result in results:
        lines += [
            f"### {result['name']}",
            "",
            f"`{result['command']}` → exit `{result['returncode']}`",
            "",
            "```text",
            last_lines(result["stdout"] + "\n" + result["stderr"], 10) or "(no output)",
            "```",
            "",
        ]
    lines += [
        "## Git status snapshot",
        "",
        f"- `git status --short -uall` lines: {len(status_lines)}",
        f"- Deleted legacy paths (` D`): {sum(1 for line in status_lines if line.startswith(' D') or line.startswith('D '))}",
        f"- Modified tracked paths (` M`): {sum(1 for line in status_lines if line.startswith(' M') or line.startswith('M '))}",
        f"- Untracked paths (`??`): {sum(1 for line in status_lines if line.startswith('??'))}",
        "",
        "Full stdout/stderr of every command is in `reports/academy-v2-test-logs.txt`.",
        "",
        "## Known, explicit limitations",
        "",
        "- Browser visual/interactive rendering was not photographed or pixel-tested; no browser engine is installed.",
        "- 18 of 23 courses are honest P1 roadmap entries; the presentation-ready vertical slice contains 5 connected live courses, 10 complete lessons, 3 simulations and 2 labs.",
        "- Flask-dependent production route tests are skipped in this environment because Flask is absent; their v2 contract is checked statically and the equivalent read-only/quiz API is exercised over HTTP in the preview server.",
        "- Root `MANIFEST.sha256` is unchanged. Its missing/mismatch counts reflect the 143 intentionally preserved deletions and tracked files modified during this rebuild, not manifest corruption.",
        "",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"FAM Academy v2 verification: {'PASS' if all_ok else 'FAIL'}")
    for result in results:
        print(f"  {result['name']}: exit {result['returncode']}")
    print(f"summary: {SUMMARY_PATH}")
    print(f"full log: {LOG_PATH}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
