#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dependency-free preview server for FAM Academy v2.

It serves the rebuilt static UI, versioned content, and read-only/quiz APIs for
local presentation and automated integration tests. It does NOT start the
production Flask service, does NOT open device connections, does NOT persist
user data, and does NOT write progress to the repository.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

SERVER_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVER_ROOT.parent
WWW = SERVER_ROOT / "www"
PRIVATE_UI = SERVER_ROOT / "private_ui"
V1 = WWW / "academy-content" / "v1"
PREVIEW_NONCE = "fam-v2-preview"
OUTPUT_LABEL = "Sample / Simulated — Internal Simulator"

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".md": "text/markdown; charset=utf-8",
}


def safe_join(base: Path, rel: str) -> Path | None:
    base = base.resolve()
    target = (base / rel).resolve()
    if base != target and base not in target.parents:
        return None
    return target


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def evaluate_quiz(lesson_id: str, body: dict) -> dict:
    lesson_path = safe_join(V1, f"lessons/{lesson_id}.json")
    if not lesson_path or not lesson_path.is_file():
        return {"ok": False, "error": "lesson not found"}
    lesson = load_json(lesson_path)
    answers = body.get("answers") if isinstance(body, dict) else None
    if not isinstance(answers, list):
        return {"ok": False, "error": "answers must be a list"}
    quiz = lesson.get("quiz", [])
    details = []
    correct = 0
    for i, q in enumerate(quiz):
        given = answers[i] if i < len(answers) else None
        good = isinstance(given, int) and not isinstance(given, bool) and 0 <= given < len(q["options"]) and given == q["answerIndex"]
        if good:
            correct += 1
        details.append({
            "id": q["id"], "prompt": q["prompt"], "given": given,
            "correctIndex": q["answerIndex"], "correct": good,
            "explanation": q["explanation"], "options": q["options"],
        })
    total = len(quiz)
    return {
        "ok": True, "total": total, "correct": correct,
        "score": round(100 * correct / total) if total else 0,
        "details": details, "label": OUTPUT_LABEL,
    }


def preview_html() -> bytes:
    page = (PRIVATE_UI / "academy.html").read_text(encoding="utf-8")
    boot = {
        "previewMode": True,
        "userName": "میهمان ارائه",
        "csrf": "",
        "progress": {},
        "academyVersion": "v2",
        "contentVersion": "2026.11.24-p0",
    }
    encoded = json.dumps(boot, ensure_ascii=True, separators=(",", ":"))
    encoded = encoded.replace("<", r"\u003c").replace(">", r"\u003e").replace("&", r"\u0026")
    page = page.replace("__FAM_ACADEMY_BOOTSTRAP__", encoded)
    page = page.replace("__FAM_CSP_NONCE__", PREVIEW_NONCE)
    return page.encode("utf-8")


def make_handler(root: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "FAMAcademyPreview/2.0"

        def log_message(self, fmt: str, *args) -> None:
            sys.stderr.write("[preview] " + (fmt % args) + "\n")

        def _headers(self, extra: dict | None = None) -> dict:
            h = {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "same-origin",
                # Intentionally no X-Frame-Options / frame-ancestors: Arena preview embeds this page.
                "Content-Security-Policy": (
                    "default-src 'self'; base-uri 'none'; form-action 'self'; "
                    "object-src 'none'; img-src 'self' data: blob:; "
                    "script-src 'self' 'nonce-" + PREVIEW_NONCE + "'; "
                    "style-src 'self' 'unsafe-inline'; connect-src 'self'; font-src 'self' data:"
                ),
            }
            if extra:
                h.update(extra)
            return h

        def _send(self, status: int, body: bytes, content_type: str, extra: dict | None = None) -> None:
            self.send_response(status)
            for k, v in self._headers(extra).items():
                self.send_header(k, v)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _json(self, status: int, data: dict) -> None:
            self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def _file(self, path: Path | None) -> None:
            if not path or not path.is_file():
                return self._json(404, {"ok": False, "error": "not found"})
            ctype = MIME.get(path.suffix.lower()) or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            return self._send(200, path.read_bytes(), ctype)

        def _body(self) -> dict:
            try:
                n = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return {}
            if n <= 0 or n > 1024 * 1024:
                return {}
            try:
                return json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception:
                return {}

        def do_HEAD(self) -> None:
            self.do_GET()

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            path = unquote(parsed.path)
            if path in ("/", ""):
                self.send_response(302)
                self.send_header("Location", "/academy")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if path == "/academy":
                return self._send(200, preview_html(), MIME[".html"])
            if path == "/api/academy/v2/health":
                return self._json(200, {"ok": True, "service": "preview", "schemaVersion": "fam-academy-v1", "contentVersion": "2026.11.24-p0"})
            if path == "/api/academy/v2/catalog":
                return self._file(safe_join(V1, "catalog.json"))
            if path == "/api/academy/v2/exercises":
                return self._file(safe_join(V1, "exercises.json"))
            if path == "/api/academy/v2/references":
                return self._file(safe_join(V1, "references.json"))
            if path.startswith("/api/academy/v2/lesson/"):
                lesson_id = path.rsplit("/", 1)[-1]
                return self._file(safe_join(V1, f"lessons/{lesson_id}.json"))
            if path.startswith("/api/academy/v2/simulation/"):
                sim_id = path.rsplit("/", 1)[-1]
                return self._file(safe_join(V1, f"simulations/{sim_id}.json"))
            if path.startswith("/api/academy/v2/lab/"):
                lab_id = path.rsplit("/", 1)[-1]
                return self._file(safe_join(V1, f"labs/{lab_id}.json"))
            if path == "/api/academy/progress":
                return self._json(200, {"ok": True, "preview": True, "progress": {}})
            if path.startswith("/academy-assets/"):
                rel = path[len("/academy-assets/"):]
                return self._file(safe_join(WWW / "academy-assets", rel))
            if path.startswith("/academy-content/"):
                rel = path[len("/academy-content/"):]
                return self._file(safe_join(WWW / "academy-content", rel))
            if path == "/favicon.ico":
                return self._json(404, {"ok": False, "error": "not found"})
            return self._json(404, {"ok": False, "error": "not found", "path": path})

        def do_POST(self) -> None:
            parsed = urlsplit(self.path)
            path = unquote(parsed.path)
            if path.startswith("/api/academy/v2/quiz/"):
                lesson_id = path.rsplit("/", 1)[-1]
                result = evaluate_quiz(lesson_id, self._body())
                return self._json(200 if result.get("ok") else 400, result)
            if path == "/api/academy/progress":
                # Preview is stateless: accept the shape but do not persist user data.
                self._body()
                return self._json(200, {"ok": True, "preview": True, "persisted": False})
            return self._json(404, {"ok": False, "error": "not found"})

    return Handler


class PreviewServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_server(host: str = "127.0.0.1", port: int = 0, root: Path = PROJECT_ROOT) -> PreviewServer:
    return PreviewServer((host, port), make_handler(root))


def main() -> int:
    ap = argparse.ArgumentParser(description="FAM Academy v2 preview server")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    server = make_server(args.host, args.port)
    actual = server.server_address[1]
    print(f"FAM Academy preview listening on http://{args.host}:{actual}/academy", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
