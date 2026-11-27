#!/usr/bin/env python3
"""
FAM Academy Lab — auto_09: RESTCONF (RFC 8040) Local Loopback Lab.
Execution boundary: Spins up an ephemeral local HTTP server on 127.0.0.1
implementing RFC 8040 content=config/nonconfig, POST vs PUT semantics,
application/yang-data+json headers, and a strict NoRedirectHandler so
Authorization headers are never leaked across redirects. No live IOS-XE device.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

YANG_JSON = "application/yang-data+json"
CONFIG_STORE = {
    "GigabitEthernet1": {"name": "GigabitEthernet1", "description": "WAN", "enabled": True}
}
STATE_STORE = {
    "GigabitEthernet1": {"name": "GigabitEthernet1", "oper-status": "up", "in-octets": 982340}
}


class RestconfHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        pass

    def _send(self, code: int, body: dict | None = None, extra_headers: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", YANG_JSON)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        if body is not None:
            self.wfile.write(json.dumps(body).encode("utf-8"))

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/restconf/redirect-trap":
            self._send(302, None, {"Location": "http://untrusted.example/steal"})
            return
        qs = urllib.parse.parse_qs(parsed.query)
        content = qs.get("content", ["all"])[0]
        if parsed.path == "/restconf/data/ietf-interfaces:interfaces":
            if content == "config":
                self._send(200, {"ietf-interfaces:interfaces": {"interface": list(CONFIG_STORE.values())}})
            elif content == "nonconfig":
                # RFC 8040 Sec 4.8.1 + RFC 8343 (NMDA): filter nonconfig descendants under the requested resource
                self._send(200, {"ietf-interfaces:interfaces": {"interface": list(STATE_STORE.values())}})
            else:
                merged = [
                    {**CONFIG_STORE.get(name, {}), **STATE_STORE.get(name, {})}
                    for name in sorted(set(CONFIG_STORE) | set(STATE_STORE))
                ]
                self._send(200, {"ietf-interfaces:interfaces": {"interface": merged}})
            return
        self._send(404, {"error": "resource not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        name = payload["name"]
        if name in CONFIG_STORE:
            self._send(409, {"ietf-restconf:errors": {"error": [{"error-tag": "data-exists"}]}})
            return
        CONFIG_STORE[name] = payload
        self._send(201, payload, {"Location": f"/restconf/data/ietf-interfaces:interfaces/interface={name}"})

    def do_PUT(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        name = payload["name"]
        existed = name in CONFIG_STORE
        CONFIG_STORE[name] = payload
        self._send(204 if existed else 201, None)


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"Blocked redirect to {newurl}", headers, fp)


def main() -> None:
    server = HTTPServer(("127.0.0.1", 0), RestconfHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    opener = urllib.request.build_opener(NoRedirectHandler())
    base = f"http://127.0.0.1:{port}"
    headers = {"Accept": YANG_JSON, "Content-Type": YANG_JSON, "Authorization": "Bearer lab-token"}

    try:
        # 1. content=nonconfig returns operational state nodes under the requested NMDA resource
        req_state = urllib.request.Request(f"{base}/restconf/data/ietf-interfaces:interfaces?content=nonconfig", headers=headers)
        with opener.open(req_state, timeout=5) as resp:
            nonconfig_body = json.loads(resp.read().decode("utf-8"))
        assert "ietf-interfaces:interfaces" in nonconfig_body
        assert "oper-status" in nonconfig_body["ietf-interfaces:interfaces"]["interface"][0]
        assert "description" not in nonconfig_body["ietf-interfaces:interfaces"]["interface"][0]

        # 2. POST creates child (201); duplicate POST returns 409 Conflict
        lo0 = json.dumps({"name": "Loopback0", "description": "Router-ID", "enabled": True}).encode("utf-8")
        with opener.open(urllib.request.Request(f"{base}/restconf/data/ietf-interfaces:interfaces", data=lo0, headers=headers, method="POST"), timeout=5) as r:
            post_create_code = r.status
        assert post_create_code == 201
        try:
            opener.open(urllib.request.Request(f"{base}/restconf/data/ietf-interfaces:interfaces", data=lo0, headers=headers, method="POST"), timeout=5)
            post_dup_code = 200
        except urllib.error.HTTPError as exc:
            post_dup_code = exc.code
        assert post_dup_code == 409

        # 3. PUT replaces existing resource (204)
        lo0_new = json.dumps({"name": "Loopback0", "description": "Updated-RID", "enabled": True}).encode("utf-8")
        with opener.open(urllib.request.Request(f"{base}/restconf/data/ietf-interfaces:interfaces/interface=Loopback0", data=lo0_new, headers=headers, method="PUT"), timeout=5) as r:
            put_replace_code = r.status
        assert put_replace_code == 204

        # 4. Redirect trap blocked to prevent Authorization header leakage
        try:
            opener.open(urllib.request.Request(f"{base}/restconf/redirect-trap", headers=headers), timeout=5)
            redirect_blocked = False
        except urllib.error.HTTPError as exc:
            redirect_blocked = exc.code == 302
        assert redirect_blocked
    finally:
        server.shutdown()
        server.server_close()

    print("=== auto_09 RESTCONF RFC 8040 Loopback Lab ===")
    print(json.dumps({
        "nonconfig_oper_status": nonconfig_body["ietf-interfaces:interfaces"]["interface"][0]["oper-status"],
        "post_create_status": post_create_code,
        "post_duplicate_status": post_dup_code,
        "put_replace_status": put_replace_code,
        "unsafe_redirect_blocked": redirect_blocked,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
