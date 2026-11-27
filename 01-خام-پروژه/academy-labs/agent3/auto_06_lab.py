"""Local Loopback HTTP REST API Lab for auto_06 (runs a real ephemeral HTTP server on 127.0.0.1).

Uses Python stdlib http.server on localhost only; no external Catalyst Center/Meraki/router is used.
Validates JSON payloads, returning 400 Bad Request on malformed/missing fields and 409 Conflict on duplicate POST.
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import urllib.error
import urllib.request


def run_local_rest_lab() -> dict[str, object]:
    """Start an ephemeral localhost REST server, test CRUD + error status codes, and shut down cleanly."""
    store: dict[str, dict[str, object]] = {
        "10": {"id": "10", "name": "CORP_DATA", "state": "active"},
    }

    class VlanHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # noqa: A002
            return

        def _send_json(self, code: int, payload: object | None = None) -> None:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if payload is not None:
                self.wfile.write(json.dumps(payload).encode("utf-8"))

        def _read_json(self) -> dict[str, object] | None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                obj = json.loads(raw)
                return obj if isinstance(obj, dict) else None
            except (ValueError, UnicodeDecodeError):
                return None

        def do_GET(self):
            parts = self.path.strip("/").split("/")
            if parts == ["api", "vlans"]:
                self._send_json(200, list(store.values()))
            elif len(parts) == 3 and parts[:2] == ["api", "vlans"]:
                item = store.get(parts[2])
                self._send_json(200, item) if item else self._send_json(404, {"error": "not_found"})
            else:
                self._send_json(404, {"error": "unknown_path"})

        def do_POST(self):
            body = self._read_json()
            if body is None or "id" not in body or "name" not in body:
                self._send_json(400, {"error": "invalid_or_incomplete_payload"})
                return
            vid = str(body["id"])
            if vid in store:
                self._send_json(409, {"error": "already_exists"})
                return
            store[vid] = {"id": vid, "name": str(body["name"]), "state": str(body.get("state", "active"))}
            self._send_json(201, store[vid])

        def do_PUT(self):
            vid = self.path.strip("/").split("/")[-1]
            body = self._read_json()
            if body is None or "name" not in body:
                self._send_json(400, {"error": "invalid_or_incomplete_payload"})
                return
            store[vid] = {"id": vid, "name": str(body["name"]), "state": str(body.get("state", "active"))}
            self._send_json(200, store[vid])

        def do_PATCH(self):
            vid = self.path.strip("/").split("/")[-1]
            if vid not in store:
                self._send_json(404, {"error": "not_found"})
                return
            body = self._read_json()
            if body is None:
                self._send_json(400, {"error": "invalid_json"})
                return
            store[vid].update(body)
            self._send_json(200, store[vid])

        def do_DELETE(self):
            vid = self.path.strip("/").split("/")[-1]
            if vid in store:
                del store[vid]
                self.send_response(204)
                self.end_headers()
            else:
                self._send_json(404, {"error": "not_found"})

    server = HTTPServer(("127.0.0.1", 0), VlanHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def call(method: str, path: str, body: dict[str, object] | None = None) -> tuple[int, str]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            return err.code, err.read().decode("utf-8")

    try:
        r_bad = call("POST", "/api/vlans", {"name": "NO_ID"})
        r_post = call("POST", "/api/vlans", {"id": "20", "name": "VOICE"})
        r_dup = call("POST", "/api/vlans", {"id": "20", "name": "VOICE_DUP"})
        r_patch = call("PATCH", "/api/vlans/20", {"name": "VOICE_CORP"})
        r_put_1 = call("PUT", "/api/vlans/20", {"name": "VOICE_FINAL", "state": "active"})
        r_put_2 = call("PUT", "/api/vlans/20", {"name": "VOICE_FINAL", "state": "active"})
        r_del = call("DELETE", "/api/vlans/20")
        r_missing = call("GET", "/api/vlans/20")
        return {
            "bad_post_status": r_bad[0],
            "post_status": r_post[0],
            "duplicate_post_status": r_dup[0],
            "patch_status": r_patch[0],
            "put_idempotent_same_result": r_put_1 == r_put_2 and r_put_1[0] == 200,
            "delete_status": r_del[0],
            "get_after_delete_status": r_missing[0],
        }
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    print("Local loopback 127.0.0.1 REST lab only — no external SDN controller or router is contacted.")
    res = run_local_rest_lab()
    assert res["bad_post_status"] == 400
    assert res["post_status"] == 201
    assert res["duplicate_post_status"] == 409
    assert res["patch_status"] == 200
    assert res["put_idempotent_same_result"] is True
    assert res["delete_status"] == 204
    assert res["get_after_delete_status"] == 404
    print(res)


if __name__ == "__main__":
    main()
