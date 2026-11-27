"""Local Crypto/JWT/X.509 SAN Lab for auto_07.

Runs real Python 3 stdlib HMAC-SHA256 / Base64URL cryptography and SAN matching locally;
no live TLS 1.3 handshake or production OAuth server is contacted.
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


def verify_hs256_jwt(token: str, secret: bytes, now_ts: int = 1764201600) -> dict[str, object]:
    """Decode JWS payload and enforce pinned alg=='HS256', HMAC-SHA256 signature, and exp claim."""
    if not isinstance(token, str) or not isinstance(secret, (bytes, bytearray)):
        raise ValueError("token must be str and secret must be bytes")
    if isinstance(now_ts, bool) or not isinstance(now_ts, int):
        raise ValueError(f"now_ts must be an int (not bool), got {now_ts!r}")
    parts = token.split(".")
    if len(parts) != 3:
        return {"valid": False, "reason": "malformed_jwt"}
    h_b64, p_b64, s_b64 = parts
    try:
        header = json.loads(b64url_decode(h_b64))
        payload = json.loads(b64url_decode(p_b64))
    except (ValueError, UnicodeDecodeError):
        return {"valid": False, "reason": "malformed_jwt"}
    if not isinstance(header, dict) or not isinstance(payload, dict):
        return {"valid": False, "reason": "malformed_jwt"}

    # RFC 8725: Pin allowed algorithm explicitly to block alg="none" / algorithm confusion
    alg_ok = header.get("alg") == "HS256"
    expected_sig = b64url_encode(
        hmac.new(secret, f"{h_b64}.{p_b64}".encode("ascii"), hashlib.sha256).digest()
    )
    sig_ok = alg_ok and hmac.compare_digest(s_b64, expected_sig)
    exp = payload.get("exp")
    not_expired = (not isinstance(exp, bool)) and isinstance(exp, int) and exp > now_ts

    reason = "ok"
    if not alg_ok:
        reason = f"disallowed_alg:{header.get('alg')}"
    elif not sig_ok:
        reason = "invalid_signature"
    elif not not_expired:
        reason = "token_expired"

    return {
        "header": header,
        "payload": payload,
        "alg_pinned_hs256": alg_ok,
        "signature_valid": sig_ok,
        "not_expired": not_expired,
        "valid": alg_ok and sig_ok and not_expired,
        "reason": reason,
    }


def verify_san_match(target_host: str, cert_sans: list[str]) -> bool:
    """Simplified RFC 6125/9525 SAN match (exact or non-empty single-label left wildcard)."""
    if not isinstance(target_host, str) or not isinstance(cert_sans, list) or not all(isinstance(s, str) for s in cert_sans):
        raise ValueError("target_host must be str and cert_sans must be list[str]")
    host = target_host.lower().strip()
    if not host or host.startswith(".") or host.endswith("."):
        return False
    for san in cert_sans:
        pattern = san.lower().strip()
        if pattern == host:
            return True
        if pattern.startswith("*.") and host.endswith(pattern[1:]):
            left_label = host[: -len(pattern[1:])]
            if left_label and "." not in left_label:
                return True
    return False


def main() -> None:
    print("Local Python stdlib JWT/SAN crypto lab — no external HTTPS/OAuth server or router is contacted.")
    secret = b"lab-only-not-production-secret"
    now_ts = 1764201600  # 2025-11-27T00:00:00Z reference timestamp

    valid_tok = build_hs256_jwt({"sub": "netops-bot", "scope": "read:interfaces", "exp": 1893456000}, secret)
    valid_res = verify_hs256_jwt(valid_tok, secret, now_ts=now_ts)
    assert valid_res["valid"] is True
    print("Valid JWT check:", valid_res)

    # Negative 1: Tampered payload
    parts = valid_tok.split(".")
    forged_payload = b64url_encode(json.dumps({"sub": "netops-bot", "scope": "admin:*", "exp": 1893456000}).encode("utf-8"))
    tampered_res = verify_hs256_jwt(f"{parts[0]}.{forged_payload}.{parts[2]}", secret, now_ts=now_ts)
    assert tampered_res["valid"] is False and tampered_res["reason"] == "invalid_signature"
    print("Tampered JWT rejected:", tampered_res)

    # Negative 2: alg="none" attack rejected explicitly
    none_hdr = b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
    none_res = verify_hs256_jwt(f"{none_hdr}.{parts[1]}.", secret, now_ts=now_ts)
    assert none_res["valid"] is False and none_res["alg_pinned_hs256"] is False
    print("alg=none attack rejected:", none_res)

    # Negative 3: Expired token rejected
    expired_tok = build_hs256_jwt({"sub": "netops-bot", "scope": "read:interfaces", "exp": 1700000000}, secret)
    expired_res = verify_hs256_jwt(expired_tok, secret, now_ts=now_ts)
    assert expired_res["valid"] is False and expired_res["reason"] == "token_expired"
    print("Expired JWT rejected:", expired_res)

    # SAN checks (positive + negative)
    assert verify_san_match("api.netops.example", ["*.netops.example"]) is True
    assert verify_san_match("a.b.netops.example", ["*.netops.example"]) is False
    assert verify_san_match(".netops.example", ["*.netops.example"]) is False
    print("SAN checks passed (exact/single-label accepted; multi-label & leading-dot rejected).")


if __name__ == "__main__":
    main()
