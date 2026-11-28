"""Educational Local Crypto / JWT-Demo / X.509 SAN Lab for auto_07.

Execution boundary & scope disclaimer:
- Runs pure Python 3 stdlib HMAC-SHA256 / Base64URL and simplified SAN matching locally.
- This is strictly an EDUCATIONAL DEMO — NOT a production RFC 8725 JWT verifier and NOT
  a TLS/X.509 verification stack. No live TLS 1.3 handshake, OCSP/CRL revocation server,
  or production OAuth 2.0 / OIDC authorization server is contacted.
- Features intentionally NOT implemented here (required in production): JWKS/kid key
  management and rotation, asymmetric JWS (RS256/ES256/EdDSA), jti replay cache, token
  revocation, and OAuth scope/policy enforcement.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import re

_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def b64url_encode(raw: bytes) -> str:
    if not isinstance(raw, (bytes, bytearray)):
        raise ValueError("raw must be bytes")
    return base64.urlsafe_b64encode(bytes(raw)).rstrip(b"=").decode("ascii")


def b64url_decode_strict(segment: str) -> bytes:
    """Decode an unpadded ASCII Base64URL segment (RFC 7515 compact JWS); raises ValueError on invalid input."""
    if not isinstance(segment, str) or not segment or not _BASE64URL_RE.fullmatch(segment):
        raise ValueError("segment must be a non-empty unpadded ASCII Base64URL string")
    if len(segment) % 4 == 1:
        raise ValueError("invalid Base64URL segment length")
    padding = "=" * (-len(segment) % 4)
    try:
        raw = base64.urlsafe_b64decode((segment + padding).encode("ascii"))
    except ValueError as exc:
        raise ValueError("invalid Base64URL encoding") from exc
    if b64url_encode(raw) != segment:
        raise ValueError("non-canonical Base64URL segment")
    return raw


def _loads_strict_json_object(raw: bytes) -> dict[str, object]:
    """Parse UTF-8 JSON object rejecting duplicate keys and non-standard NaN/Infinity constants."""
    def _reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        obj: dict[str, object] = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError(f"duplicate JSON key: {k!r}")
            obj[k] = v
        return obj

    def _reject_constants(tok: str) -> object:
        raise ValueError(f"non-standard JSON constant: {tok!r}")

    parsed = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_reject_duplicates,
        parse_constant=_reject_constants,
    )
    if not isinstance(parsed, dict):
        raise ValueError("JSON segment must decode to an object")
    return parsed


def build_hs256_jwt_demo(
    payload: dict[str, object],
    secret: bytes,
    typ: str = "JWT",
) -> str:
    """Build a compact HS256 JWS token for local educational demonstrations only."""
    if not isinstance(payload, dict) or not isinstance(secret, (bytes, bytearray)) or not secret:
        raise ValueError("payload must be dict and secret must be non-empty bytes")
    if not isinstance(typ, str) or not typ.strip():
        raise ValueError("typ must be a non-empty str")
    header = {"alg": "HS256", "typ": typ}
    h_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(bytes(secret), f"{h_b64}.{p_b64}".encode("ascii"), hashlib.sha256).digest()
    return f"{h_b64}.{p_b64}.{b64url_encode(sig)}"


def evaluate_hs256_jwt_demo(
    token: str,
    secret: bytes,
    now_ts: int = 1764201600,
    expected_iss: str | None = None,
    expected_aud: str | None = None,
    expected_typ: str | None = None,
) -> dict[str, object]:
    """Educational HS256 JWS inspector with explicit scope boundaries (NOT a production verifier).

    Always validates compact 3-part ASCII Base64URL syntax, strict JSON objects, pinned
    alg=='HS256', constant-time bytes HMAC-SHA256 comparison (never raising TypeError on
    non-ASCII tokens), exp (required int > now_ts), and nbf (if present, int <= now_ts).
    Optionally validates iss/aud/typ when expected_* values are supplied, and reports every
    performed and unimplemented check explicitly in the returned dict.
    """
    if not isinstance(token, str) or not isinstance(secret, (bytes, bytearray)) or not secret:
        raise ValueError("token must be str and secret must be non-empty bytes")
    if isinstance(now_ts, bool) or not isinstance(now_ts, int):
        raise ValueError(f"now_ts must be an int (not bool), got {now_ts!r}")
    for opt_name, opt_val in (
        ("expected_iss", expected_iss),
        ("expected_aud", expected_aud),
        ("expected_typ", expected_typ),
    ):
        if opt_val is not None and (not isinstance(opt_val, str) or not opt_val.strip()):
            raise ValueError(f"{opt_name} must be None or a non-empty str")

    checks_performed = [
        "compact_3_part_ascii_base64url",
        "strict_json_no_duplicate_keys",
        "alg_pinned_hs256",
        "hmac_sha256_bytes_constant_time",
        "exp_required_and_unexpired",
        "nbf_if_present_not_before_now",
    ]
    checks_not_implemented = [
        "jwks_kid_key_rotation",
        "asymmetric_jws_rs256_es256_eddsa",
        "jti_replay_protection",
        "token_revocation_check",
        "oauth_scope_policy_enforcement",
    ]
    if expected_iss is not None:
        checks_performed.append("iss_exact_match")
    else:
        checks_not_implemented.append("iss_claim_not_configured")
    if expected_aud is not None:
        checks_performed.append("aud_exact_or_list_match")
    else:
        checks_not_implemented.append("aud_claim_not_configured")
    if expected_typ is not None:
        checks_performed.append("typ_header_match")
    else:
        checks_not_implemented.append("typ_header_not_configured")

    def _fail(reason: str, header: dict | None = None, payload: dict | None = None, **flags: bool) -> dict[str, object]:
        return {
            "educational_demo_only": True,
            "not_production_jwt_verifier": True,
            "demo_checks_passed": False,
            "reason": reason,
            "header": header,
            "payload": payload,
            "alg_pinned_hs256": flags.get("alg_pinned_hs256", False),
            "signature_valid": flags.get("signature_valid", False),
            "not_expired": flags.get("not_expired", False),
            "nbf_satisfied": flags.get("nbf_satisfied", False),
            "checks_performed": checks_performed,
            "checks_not_implemented": checks_not_implemented,
        }

    parts = token.split(".")
    if len(parts) != 3:
        return _fail("malformed_jwt_segment_count")
    h_b64, p_b64, s_b64 = parts

    # Reject non-ASCII / invalid Base64URL header & payload cleanly before any crypto call
    try:
        header = _loads_strict_json_object(b64url_decode_strict(h_b64))
        payload = _loads_strict_json_object(b64url_decode_strict(p_b64))
    except (ValueError, UnicodeDecodeError):
        return _fail("malformed_jwt_encoding_or_json")

    # RFC 8725: pin allowed algorithm explicitly to block alg="none" / algorithm confusion
    alg_ok = header.get("alg") == "HS256"
    if not alg_ok:
        return _fail(f"disallowed_alg:{header.get('alg')}", header=header, payload=payload, alg_pinned_hs256=False)

    if expected_typ is not None and header.get("typ") != expected_typ:
        return _fail("invalid_typ", header=header, payload=payload, alg_pinned_hs256=True)

    # Decode signature bytes strictly; non-ASCII signatures like "☃" return malformed_signature (never TypeError!)
    try:
        actual_sig_bytes = b64url_decode_strict(s_b64)
    except ValueError:
        return _fail("malformed_signature_encoding", header=header, payload=payload, alg_pinned_hs256=True)

    signing_input = f"{h_b64}.{p_b64}".encode("ascii")
    expected_sig_bytes = hmac.new(bytes(secret), signing_input, hashlib.sha256).digest()
    sig_ok = hmac.compare_digest(actual_sig_bytes, expected_sig_bytes)
    if not sig_ok:
        return _fail("invalid_signature", header=header, payload=payload, alg_pinned_hs256=True, signature_valid=False)

    exp = payload.get("exp")
    not_expired = (not isinstance(exp, bool)) and isinstance(exp, int) and exp > now_ts
    if not not_expired:
        return _fail(
            "token_expired_or_missing_exp",
            header=header,
            payload=payload,
            alg_pinned_hs256=True,
            signature_valid=True,
            not_expired=False,
        )

    nbf_ok = True
    if "nbf" in payload:
        nbf = payload["nbf"]
        nbf_ok = (not isinstance(nbf, bool)) and isinstance(nbf, int) and nbf <= now_ts
    if not nbf_ok:
        return _fail(
            "token_not_yet_valid_nbf",
            header=header,
            payload=payload,
            alg_pinned_hs256=True,
            signature_valid=True,
            not_expired=True,
            nbf_satisfied=False,
        )

    if expected_iss is not None and payload.get("iss") != expected_iss:
        return _fail(
            "invalid_issuer",
            header=header,
            payload=payload,
            alg_pinned_hs256=True,
            signature_valid=True,
            not_expired=True,
            nbf_satisfied=True,
        )

    if expected_aud is not None:
        aud = payload.get("aud")
        aud_ok = (aud == expected_aud) or (
            isinstance(aud, list) and all(isinstance(x, str) for x in aud) and expected_aud in aud
        )
        if not aud_ok:
            return _fail(
                "invalid_audience",
                header=header,
                payload=payload,
                alg_pinned_hs256=True,
                signature_valid=True,
                not_expired=True,
                nbf_satisfied=True,
            )

    return {
        "educational_demo_only": True,
        "not_production_jwt_verifier": True,
        "demo_checks_passed": True,
        "reason": "ok_educational_subset_only",
        "header": header,
        "payload": payload,
        "alg_pinned_hs256": True,
        "signature_valid": True,
        "not_expired": True,
        "nbf_satisfied": True,
        "checks_performed": checks_performed,
        "checks_not_implemented": checks_not_implemented,
    }


def _is_ip_literal(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def verify_san_match(target_host: str, cert_sans: list[str]) -> bool:
    """Simplified educational RFC 6125/9525 DNS/IP SAN match (exact or single-label left wildcard for DNS only)."""
    if not isinstance(target_host, str) or not isinstance(cert_sans, list) or not all(isinstance(s, str) for s in cert_sans):
        raise ValueError("target_host must be str and cert_sans must be list[str]")
    host = target_host.lower().strip()
    if not host or not host.isascii() or any(ch.isspace() for ch in host) or host.startswith(".") or host.endswith("."):
        return False
    host_is_ip = _is_ip_literal(host)
    for san in cert_sans:
        pattern = san.lower().strip()
        if not pattern or not pattern.isascii() or any(ch.isspace() for ch in pattern):
            continue
        if pattern == host:
            return True
        # RFC 6125/9525: wildcards are NOT valid for IP literals and match exactly one left DNS label
        if not host_is_ip and pattern.startswith("*.") and pattern.count(".") >= 2 and host.endswith(pattern[1:]):
            left_label = host[: -len(pattern[1:])]
            if left_label and "." not in left_label:
                return True
    return False


def main() -> None:
    print("Educational Python stdlib JWT/SAN demo — NOT a production JWT verifier or live TLS stack.")
    secret = b"lab-only-not-production-secret"
    now_ts = 1764201600  # 2025-11-27T00:00:00Z reference timestamp

    valid_tok = build_hs256_jwt_demo(
        {
            "iss": "https://idp.netops.example",
            "aud": "netops-api",
            "sub": "netops-bot",
            "scope": "read:interfaces",
            "nbf": now_ts - 60,
            "exp": 1893456000,
        },
        secret,
    )
    valid_res = evaluate_hs256_jwt_demo(
        valid_tok,
        secret,
        now_ts=now_ts,
        expected_iss="https://idp.netops.example",
        expected_aud="netops-api",
        expected_typ="JWT",
    )
    assert valid_res["demo_checks_passed"] is True and valid_res["educational_demo_only"] is True
    print("Valid JWT demo check:", valid_res)

    # Negative 1: Tampered payload
    parts = valid_tok.split(".")
    forged_payload = b64url_encode(json.dumps({"sub": "netops-bot", "scope": "admin:*", "exp": 1893456000}).encode("utf-8"))
    tampered_res = evaluate_hs256_jwt_demo(f"{parts[0]}.{forged_payload}.{parts[2]}", secret, now_ts=now_ts)
    assert tampered_res["demo_checks_passed"] is False and tampered_res["reason"] == "invalid_signature"
    print("Tampered JWT rejected:", tampered_res["reason"])

    # Negative 2: Non-ASCII signature ("☃") must return clean rejection, NEVER TypeError
    non_ascii_res = evaluate_hs256_jwt_demo(f"{parts[0]}.{parts[1]}.☃", secret, now_ts=now_ts)
    assert non_ascii_res["demo_checks_passed"] is False and non_ascii_res["reason"] == "malformed_signature_encoding"
    print("Non-ASCII signature rejected cleanly:", non_ascii_res["reason"])

    # Negative 3: alg="none" attack rejected explicitly
    none_hdr = b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
    none_res = evaluate_hs256_jwt_demo(f"{none_hdr}.{parts[1]}.", secret, now_ts=now_ts)
    assert none_res["demo_checks_passed"] is False and none_res["alg_pinned_hs256"] is False
    print("alg=none attack rejected:", none_res["reason"])

    # Negative 4: Expired token rejected
    expired_tok = build_hs256_jwt_demo({"sub": "netops-bot", "scope": "read:interfaces", "exp": 1700000000}, secret)
    expired_res = evaluate_hs256_jwt_demo(expired_tok, secret, now_ts=now_ts)
    assert expired_res["demo_checks_passed"] is False and expired_res["reason"] == "token_expired_or_missing_exp"
    print("Expired JWT rejected:", expired_res["reason"])

    # SAN checks (positive + negative)
    assert verify_san_match("api.netops.example", ["*.netops.example"]) is True
    assert verify_san_match("a.b.netops.example", ["*.netops.example"]) is False
    assert verify_san_match(".netops.example", ["*.netops.example"]) is False
    assert verify_san_match("10.0.0.1", ["*.0.0.1"]) is False
    print("SAN checks passed (exact/single-label DNS accepted; multi-label, leading-dot & IP-wildcard rejected).")


if __name__ == "__main__":
    main()
