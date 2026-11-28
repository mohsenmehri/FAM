#!/usr/bin/env python3
"""
FAM Academy Lab — auto_09: RESTCONF Educational Loopback Simulator.

Execution boundary & honest limitations:
- Spins up an ephemeral local HTTP server on 127.0.0.1 with per-server isolated state
  (no global mutable store), strict URI routing (/restconf/data/ietf-interfaces:interfaces
  and .../interface=<name>), strict Content-Type enforcement (application/yang-data+json),
  Accept validation, bounded request body size, duplicate-key JSON rejection, RFC 7951-style
  interface payloads, and a client NoRedirectHandler.
- This is strictly a MINIMAL EDUCATIONAL SIMULATOR, NOT a full RFC 8040 implementation and
  NOT production-ready: no TLS/HTTPS, no real authentication/RBAC enforcement, no full YANG
  schema validator, and no live IOS-XE / network device is contacted.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

YANG_JSON = "application/yang-data+json"
COLLECTION_PATH = "/restconf/data/ietf-interfaces:interfaces"
ITEM_PREFIX = "/restconf/data/ietf-interfaces:interfaces/interface="
REDIRECT_TRAP_PATH = "/restconf/redirect-trap"
DEFAULT_MAX_BODY_BYTES = 65536


def _restconf_error(error_type: str, error_tag: str, message: str) -> dict:
    return {
        "ietf-restconf:errors": {
            "error": [
                {
                    "error-type": error_type,
                    "error-tag": error_tag,
                    "error-message": message,
                }
            ]
        }
    }


def _loads_strict_json(raw: str) -> object:
    def _reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        obj: dict[str, object] = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError(f"duplicate JSON key: {k!r}")
            obj[k] = v
        return obj

    def _reject_constants(tok: str) -> object:
        raise ValueError(f"non-standard JSON constant: {tok!r}")

    return json.loads(raw, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constants)


def _extract_interface_payload(body: object) -> dict | None:
    """Validate RFC 7951-style interface payload: {'ietf-interfaces:interface': [{...}]} or single object."""
    if not isinstance(body, dict) or list(body.keys()) != ["ietf-interfaces:interface"]:
        return None
    inner = body["ietf-interfaces:interface"]
    if isinstance(inner, list):
        if len(inner) != 1 or not isinstance(inner[0], dict):
            return None
        iface = inner[0]
    elif isinstance(inner, dict):
        iface = inner
    else:
        return None

    allowed_keys = {"name", "description", "enabled"}
    if not set(iface.keys()).issubset(allowed_keys):
        return None
    if not isinstance(iface.get("name"), str) or not iface["name"].strip():
        return None
    if "description" in iface and not isinstance(iface["description"], str):
        return None
    if "enabled" in iface and not isinstance(iface["enabled"], bool):
        return None
    return dict(iface)


class EducationalRestconfServer(HTTPServer):
    """Per-instance isolated RESTCONF educational simulator (no module-level mutable state)."""

    def __init__(self, server_address: tuple[str, int], handler_cls, max_body_bytes: int = DEFAULT_MAX_BODY_BYTES):
        if isinstance(max_body_bytes, bool) or not isinstance(max_body_bytes, int) or max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be a positive int")
        super().__init__(server_address, handler_cls)
        self.max_body_bytes = max_body_bytes
        self.store_lock = threading.Lock()
        self.config_store: dict[str, dict] = {
            "GigabitEthernet1": {"name": "GigabitEthernet1", "description": "WAN", "enabled": True}
        }
        self.state_store: dict[str, dict] = {
            "GigabitEthernet1": {"name": "GigabitEthernet1", "oper-status": "up", "in-octets": 982340}
        }


class RestconfHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        pass

    def _send(self, code: int, body: dict | None = None, extra_headers: dict | None = None) -> None:
        raw = json.dumps(body).encode("utf-8") if body is not None else b""
        self.send_response(code)
        if body is not None:
            self.send_header("Content-Type", YANG_JSON)
        self.send_header("Content-Length", str(len(raw)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        if raw:
            self.wfile.write(raw)

    def _check_accept(self) -> bool:
        accept = self.headers.get("Accept")
        if not accept:
            return True
        media_types = [part.split(";", 1)[0].strip().lower() for part in accept.split(",")]
        if YANG_JSON in media_types or "*/*" in media_types:
            return True
        self._send(406, _restconf_error("protocol", "invalid-value", f"Accept must allow {YANG_JSON}"))
        return False

    def _check_content_type(self) -> bool:
        ctype = self.headers.get("Content-Type", "")
        media_type = ctype.split(";", 1)[0].strip().lower()
        if media_type != YANG_JSON:
            self._send(
                415,
                _restconf_error("protocol", "invalid-value", f"Content-Type must be {YANG_JSON}, got {media_type or 'missing'}"),
            )
            return False
        return True

    def _parse_item_key(self, path: str) -> str | None:
        if not path.startswith(ITEM_PREFIX):
            return None
        encoded_key = path[len(ITEM_PREFIX) :]
        if not encoded_key or "/" in encoded_key:
            return None
        key = urllib.parse.unquote(encoded_key)
        return key if key.strip() else None

    def _read_bounded_interface(self) -> tuple[dict | None, int | None]:
        raw_len = self.headers.get("Content-Length")
        if raw_len is None or not raw_len.strip().isdigit():
            self._send(400, _restconf_error("protocol", "malformed-message", "Missing or invalid Content-Length"))
            return None, 400
        length = int(raw_len.strip())
        if length <= 0:
            self._send(400, _restconf_error("protocol", "malformed-message", "Empty request body"))
            return None, 400
        if length > self.server.max_body_bytes:
            self._send(413, _restconf_error("protocol", "too-big", f"Body exceeds limit ({self.server.max_body_bytes} bytes)"))
            return None, 413
        try:
            raw = self.rfile.read(length).decode("utf-8")
            parsed = _loads_strict_json(raw)
        except (ValueError, UnicodeDecodeError):
            self._send(400, _restconf_error("protocol", "malformed-message", "Invalid UTF-8 or strict JSON payload"))
            return None, 400
        iface = _extract_interface_payload(parsed)
        if iface is None:
            self._send(
                400,
                _restconf_error("application", "invalid-value", "Expected RFC 7951 {'ietf-interfaces:interface': [{name, ...}]}"),
            )
            return None, 400
        return iface, None

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == REDIRECT_TRAP_PATH:
            self._send(302, None, {"Location": "http://untrusted.example/steal"})
            return
        if not self._check_accept():
            return
        qs = urllib.parse.parse_qs(parsed.query)
        content = qs.get("content", ["all"])[0]
        if content not in ("config", "nonconfig", "all"):
            self._send(400, _restconf_error("protocol", "invalid-value", f"unsupported content={content}"))
            return

        if parsed.path == COLLECTION_PATH:
            with self.server.store_lock:
                if content == "config":
                    items = [dict(v) for v in self.server.config_store.values()]
                elif content == "nonconfig":
                    items = [dict(v) for v in self.server.state_store.values()]
                else:
                    names = sorted(set(self.server.config_store) | set(self.server.state_store))
                    items = [
                        {**self.server.config_store.get(n, {}), **self.server.state_store.get(n, {})}
                        for n in names
                    ]
            self._send(200, {"ietf-interfaces:interfaces": {"interface": items}})
            return

        item_key = self._parse_item_key(parsed.path)
        if item_key is not None:
            with self.server.store_lock:
                cfg = self.server.config_store.get(item_key)
                st = self.server.state_store.get(item_key)
                if content == "config":
                    found = dict(cfg) if cfg is not None else None
                elif content == "nonconfig":
                    found = dict(st) if st is not None else None
                else:
                    found = {**(cfg or {}), **(st or {})} if (cfg or st) else None
            if found is None:
                self._send(404, _restconf_error("application", "data-missing", f"Interface {item_key!r} not found"))
                return
            self._send(200, {"ietf-interfaces:interface": [found]})
            return

        self._send(404, _restconf_error("application", "invalid-value", f"Unknown resource path: {parsed.path}"))

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == REDIRECT_TRAP_PATH or self._parse_item_key(parsed.path) is not None:
            self._send(405, _restconf_error("protocol", "operation-not-supported", "POST not allowed on this resource"), {"Allow": "GET, PUT, PATCH, DELETE"})
            return
        if parsed.path != COLLECTION_PATH:
            self._send(404, _restconf_error("application", "invalid-value", f"Unknown resource path: {parsed.path}"))
            return
        if not self._check_accept() or not self._check_content_type():
            return
        iface, err = self._read_bounded_interface()
        if err is not None or iface is None:
            return
        name = iface["name"]
        with self.server.store_lock:
            if name in self.server.config_store:
                self._send(409, _restconf_error("application", "data-exists", f"Interface {name!r} already exists"))
                return
            self.server.config_store[name] = iface
        encoded_name = urllib.parse.quote(name, safe="")
        self._send(201, {"ietf-interfaces:interface": [iface]}, {"Location": f"{ITEM_PREFIX}{encoded_name}"})

    def do_PUT(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in (COLLECTION_PATH, REDIRECT_TRAP_PATH):
            self._send(405, _restconf_error("protocol", "operation-not-supported", "PUT requires a specific interface item URI"), {"Allow": "GET, POST"})
            return
        item_key = self._parse_item_key(parsed.path)
        if item_key is None:
            self._send(404, _restconf_error("application", "invalid-value", f"Unknown resource path: {parsed.path}"))
            return
        if not self._check_accept() or not self._check_content_type():
            return
        iface, err = self._read_bounded_interface()
        if err is not None or iface is None:
            return
        if iface["name"] != item_key:
            self._send(400, _restconf_error("application", "invalid-value", "URI interface key does not match payload name"))
            return
        with self.server.store_lock:
            existed = item_key in self.server.config_store
            self.server.config_store[item_key] = iface
        self._send(204 if existed else 201, None)

    def do_PATCH(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        item_key = self._parse_item_key(parsed.path)
        if item_key is None:
            code = 405 if parsed.path in (COLLECTION_PATH, REDIRECT_TRAP_PATH) else 404
            self._send(code, _restconf_error("application", "invalid-value", f"PATCH target invalid: {parsed.path}"))
            return
        if not self._check_accept() or not self._check_content_type():
            return
        iface, err = self._read_bounded_interface()
        if err is not None or iface is None:
            return
        if iface["name"] != item_key:
            self._send(400, _restconf_error("application", "invalid-value", "URI interface key does not match payload name"))
            return
        with self.server.store_lock:
            if item_key not in self.server.config_store:
                self._send(404, _restconf_error("application", "data-missing", f"Interface {item_key!r} does not exist"))
                return
            self.server.config_store[item_key] = {**self.server.config_store[item_key], **iface}
        self._send(204, None)

    def do_DELETE(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        item_key = self._parse_item_key(parsed.path)
        if item_key is None:
            code = 405 if parsed.path in (COLLECTION_PATH, REDIRECT_TRAP_PATH) else 404
            self._send(code, _restconf_error("application", "invalid-value", f"DELETE target invalid: {parsed.path}"))
            return
        with self.server.store_lock:
            if item_key not in self.server.config_store:
                self._send(404, _restconf_error("application", "data-missing", f"Interface {item_key!r} does not exist"))
                return
            del self.server.config_store[item_key]
        self._send(204, None)


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"Blocked redirect to {newurl}", headers, fp)


def _http_status(opener, req) -> int:
    try:
        with opener.open(req, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def main() -> None:
    server = EducationalRestconfServer(("127.0.0.1", 0), RestconfHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    opener = urllib.request.build_opener(NoRedirectHandler())
    base = f"http://127.0.0.1:{port}"
    headers = {"Accept": YANG_JSON, "Content-Type": YANG_JSON, "Authorization": "Bearer lab-token"}

    try:
        # 1. content=nonconfig returns operational state nodes under the requested NMDA resource
        req_state = urllib.request.Request(f"{base}{COLLECTION_PATH}?content=nonconfig", headers=headers)
        with opener.open(req_state, timeout=5) as resp:
            nonconfig_body = json.loads(resp.read().decode("utf-8"))
        assert "ietf-interfaces:interfaces" in nonconfig_body
        assert "oper-status" in nonconfig_body["ietf-interfaces:interfaces"]["interface"][0]
        assert "description" not in nonconfig_body["ietf-interfaces:interfaces"]["interface"][0]

        # 2. Negative checks: POST /wrong -> 404 (no store mutation); application/json -> 415; Accept text/plain -> 406
        lo0 = json.dumps({"ietf-interfaces:interface": [{"name": "Loopback0", "description": "Router-ID", "enabled": True}]}).encode("utf-8")
        wrong_path_code = _http_status(opener, urllib.request.Request(f"{base}/wrong", data=lo0, headers=headers, method="POST"))
        assert wrong_path_code == 404 and "Loopback0" not in server.config_store
        wrong_ctype_code = _http_status(
            opener,
            urllib.request.Request(
                f"{base}{COLLECTION_PATH}",
                data=lo0,
                headers={"Accept": YANG_JSON, "Content-Type": "application/json"},
                method="POST",
            ),
        )
        assert wrong_ctype_code == 415 and "Loopback0" not in server.config_store
        wrong_accept_code = _http_status(
            opener,
            urllib.request.Request(f"{base}{COLLECTION_PATH}", headers={"Accept": "text/plain"}),
        )
        assert wrong_accept_code == 406

        # 3. POST creates child (201) with RFC 7951 payload; duplicate POST returns 409 Conflict
        post_create_code = _http_status(opener, urllib.request.Request(f"{base}{COLLECTION_PATH}", data=lo0, headers=headers, method="POST"))
        assert post_create_code == 201
        post_dup_code = _http_status(opener, urllib.request.Request(f"{base}{COLLECTION_PATH}", data=lo0, headers=headers, method="POST"))
        assert post_dup_code == 409

        # 4. PUT replaces existing resource (204) with URI key == payload name; percent-encoded interface name works
        lo0_new = json.dumps({"ietf-interfaces:interface": [{"name": "Loopback0", "description": "Updated-RID", "enabled": True}]}).encode("utf-8")
        put_replace_code = _http_status(opener, urllib.request.Request(f"{base}{ITEM_PREFIX}Loopback0", data=lo0_new, headers=headers, method="PUT"))
        assert put_replace_code == 204
        gi001 = json.dumps({"ietf-interfaces:interface": [{"name": "GigabitEthernet0/0/1", "description": "Uplink", "enabled": True}]}).encode("utf-8")
        put_pct_code = _http_status(opener, urllib.request.Request(f"{base}{ITEM_PREFIX}GigabitEthernet0%2F0%2F1", data=gi001, headers=headers, method="PUT"))
        assert put_pct_code == 201

        # 5. Redirect trap blocked to prevent Authorization header leakage
        redirect_blocked = _http_status(opener, urllib.request.Request(f"{base}{REDIRECT_TRAP_PATH}", headers=headers)) == 302
        assert redirect_blocked
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    print("=== auto_09 RESTCONF Educational Loopback Simulator ===")
    print(json.dumps({
        "nonconfig_oper_status": nonconfig_body["ietf-interfaces:interfaces"]["interface"][0]["oper-status"],
        "wrong_path_post_status": wrong_path_code,
        "wrong_content_type_status": wrong_ctype_code,
        "wrong_accept_status": wrong_accept_code,
        "post_create_status": post_create_code,
        "post_duplicate_status": post_dup_code,
        "put_replace_status": put_replace_code,
        "put_percent_encoded_create_status": put_pct_code,
        "unsafe_redirect_blocked": redirect_blocked,
        "simulator_scope_note": "Educational loopback HTTP simulator only; not full RFC 8040, no TLS/auth, no live device.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
