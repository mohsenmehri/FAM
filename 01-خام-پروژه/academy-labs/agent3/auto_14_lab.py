#!/usr/bin/env python3
"""
FAM Academy Lab — auto_14: Cisco DevNet SDK Pattern & ChatOps RBAC Loopback Lab.

Execution boundary & limitations:
- Ephemeral local loopback HTTP server on 127.0.0.1 with per-server isolated state,
  strict route validation (/dna/system/api/v1/auth/token and /dna/intent/api/v1/network-device),
  safe query parameter validation, bounded Retry-After sleep handling, and ChatOps allowlist
  audit modeling.
- Educational simulator only: no TLS, no real Cisco Catalyst Center / DevNet Sandbox,
  and no live network devices are contacted.
"""

from __future__ import annotations

import json
import math
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

AUTH_PATH = "/dna/system/api/v1/auth/token"
DEVICES_PATH = "/dna/intent/api/v1/network-device"
MAX_RETRY_AFTER_SEC = 2.0


class MockCatalystServer(HTTPServer):
    def __init__(self, server_address, handler_cls):
        super().__init__(server_address, handler_cls)
        self.rate_hits = 0
        self.devices = [{"id": f"dev-{i}", "hostname": f"BRANCH-R{i}", "platform": "C8300"} for i in range(1, 6)]


class MockCatalystCenter(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        pass

    def _json(self, code: int, body: dict, headers: dict | None = None) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == AUTH_PATH:
            self._json(200, {"Token": "mock-dna-token-123"})
            return
        self._json(404, {"error": "unknown endpoint"})

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != DEVICES_PATH:
            self._json(404, {"error": "unknown endpoint"})
            return
        if self.headers.get("X-Auth-Token") != "mock-dna-token-123":
            self._json(401, {"error": "invalid token"})
            return
        qs = urllib.parse.parse_qs(parsed.query)
        try:
            offset_1based = int(qs.get("offset", ["1"])[0])
            limit = int(qs.get("limit", ["2"])[0])
        except ValueError:
            self._json(400, {"error": "offset and limit must be integers"})
            return
        offset = offset_1based - 1
        if offset < 0 or limit <= 0:
            self._json(400, {"error": "invalid offset or limit"})
            return
        self.server.rate_hits += 1
        if self.server.rate_hits == 1:
            self._json(429, {"error": "rate limit"}, {"Retry-After": "0"})
            return
        self._json(200, {"response": self.server.devices[offset : offset + limit]})


class MiniSdkClient:
    def __init__(self, base_url: str) -> None:
        if not isinstance(base_url, str) or not base_url.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise ValueError("base_url must be a local loopback http:// URL")
        self.base_url = base_url.rstrip("/")
        self.token = self._fetch_token()
        self.retries_handled = 0

    def _fetch_token(self) -> str:
        req = urllib.request.Request(f"{self.base_url}{AUTH_PATH}", method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))["Token"]

    @staticmethod
    def _safe_retry_delay(header_val: str | None) -> float:
        if header_val is None:
            return 0.0
        try:
            val = float(header_val)
        except ValueError:
            return 0.0
        if not math.isfinite(val) or val < 0:
            return 0.0
        return min(val, MAX_RETRY_AFTER_SEC)

    def get_all_devices(self, page_size: int = 2, max_retries: int = 5) -> list[dict]:
        if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size <= 0:
            raise ValueError(f"page_size must be a positive int (not bool), got {page_size!r}")
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError(f"max_retries must be a non-negative int (not bool), got {max_retries!r}")

        collected = []
        offset = 1
        while True:
            url = f"{self.base_url}{DEVICES_PATH}?offset={offset}&limit={page_size}"
            req = urllib.request.Request(url, headers={"X-Auth-Token": self.token})
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    batch = json.loads(resp.read().decode("utf-8"))["response"]
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and self.retries_handled < max_retries:
                    self.retries_handled += 1
                    time.sleep(self._safe_retry_delay(exc.headers.get("Retry-After")))
                    continue
                raise
            if not batch:
                break
            collected.extend(batch)
            offset += page_size
        return collected


CHATOPS_ALLOWLIST = {
    "noc-read": {"show_inventory", "show_bgp_summary"},
    "net-admin": {"show_inventory", "show_bgp_summary", "bounce_port"},
}


def chatops_execute(user: str, role: str, command: str) -> dict:
    if not all(isinstance(x, str) and x.strip() for x in (user, role, command)):
        raise ValueError("user, role, and command must be non-empty str")
    allowed = command in CHATOPS_ALLOWLIST.get(role, set())
    return {"user": user, "role": role, "command": command, "allowed": allowed, "audited": True}


def main() -> None:
    server = MockCatalystServer(("127.0.0.1", 0), MockCatalystCenter)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        sdk = MiniSdkClient(f"http://127.0.0.1:{port}")
        all_devs = sdk.get_all_devices(page_size=2)
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert len(all_devs) == 5, "Pagination must collect all 5 devices"
    assert sdk.retries_handled == 1, "SDK must transparently handle 429 Retry-After"

    audit_ok = chatops_execute("sara", "noc-read", "show_inventory")
    audit_denied = chatops_execute("sara", "noc-read", "bounce_port")
    assert audit_ok["allowed"] is True and audit_denied["allowed"] is False

    print("=== auto_14 DevNet SDK Pattern & ChatOps RBAC Loopback Simulator ===")
    print(json.dumps({
        "devices_collected_via_pagination": len(all_devs),
        "rate_limit_429_retries_handled": sdk.retries_handled,
        "chatops_audit_sample": [audit_ok, audit_denied],
        "simulator_scope_note": "Educational loopback HTTP simulator only; no TLS, no live Catalyst Center.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
