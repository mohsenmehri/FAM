"""Local Crypto/JWT/X.509 SAN & HTTP/3 Inspector Lab for auto_07.

Runs locally in Python 3 stdlib; no live TLS 1.3 handshake or production OAuth server is contacted.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def build_hs256_jwt(payload: dict[str, object], secret: bytes) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(secret, f"{h_b64}.{p_b64}".encode("ascii"), hashlib.sha256).digest()
    return f"{h_b64}.{p_b64}.{b64url_encode(sig)}"


def verify_hs256_jwt(token: str, secret: bytes) -> dict[str, object]:
    """Decode JWS payload (showing it is readable without secret) and verify HMAC-SHA256 integrity."""
    h_b64, p_b64, s_b64 = token.split(".")
    header = json.loads(b64url_decode(h_b64))
    payload = json.loads(b64url_decode(p_b64))
    expected_sig = b64url_encode(
        hmac.new(secret, f"{h_b64}.{p_b64}".encode("ascii"), hashlib.sha256).digest()
    )
    valid = hmac.compare_digest(s_b64, expected_sig)
    return {"header": header, "payload": payload, "signature_valid": valid}


def verify_san_match(target_host: str, cert_sans: list[str]) -> bool:
    """Simplified RFC 6125/9525 SAN match (exact or single-label left wildcard)."""
    host = target_host.lower().strip()
    for san in cert_sans:
        pattern = san.lower().strip()
        if pattern == host:
            return True
        if pattern.startswith("*.") and host.count(".") == pattern.count(".") and host.endswith(pattern[1:]):
            return True
    return False


def main() -> None:
    print("Local Python JWT/SAN lab only — no external HTTPS/OAuth server or router is contacted.")
    secret = b"lab-only-not-production-secret"
    token = build_hs256_jwt({"sub": "netops-bot", "scope": "read:interfaces", "exp": 1893456000}, secret)
    print("Valid JWT check:", verify_hs256_jwt(token, secret))
    # Tamper payload to elevate scope without re-signing
    parts = token.split(".")
    forged_payload = b64url_encode(json.dumps({"sub": "netops-bot", "scope": "admin:*"}).encode("utf-8"))
    forged_token = f"{parts[0]}.{forged_payload}.{parts[2]}"
    print("Tampered JWT rejected:", verify_hs256_jwt(forged_token, secret))
    print("SAN match exact:", verify_san_match("api.netops.example", ["*.netops.example"]))
    print("SAN multi-label wildcard rejected:", verify_san_match("a.b.netops.example", ["*.netops.example"]))


if __name__ == "__main__":
    main()
