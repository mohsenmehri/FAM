"""Local Python 3 stdlib mock lab for ccna_acl (AAA TACACS+/RADIUS, Password Hardening & IPsec).

Boundary: Pure in-memory simulation using Python stdlib only.
No real Cisco router, ISE/TACACS+/RADIUS server, or IPsec tunnel is executed.
"""
from __future__ import annotations


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def evaluate_aaa_login(
    method_list: list[str],
    aaa_server_reachable: bool,
    aaa_server_accepts: bool,
    local_user_accepts: bool,
) -> dict[str, object]:
    """Simulate Cisco AAA login fallback semantics (fallback triggers ONLY on server unreachable)."""
    if not isinstance(method_list, list) or not method_list:
        raise ValueError("method_list must be a non-empty list")
    _require_bool(aaa_server_reachable, "aaa_server_reachable")
    _require_bool(aaa_server_accepts, "aaa_server_accepts")
    _require_bool(local_user_accepts, "local_user_accepts")

    for method in method_list:
        if method in ("group_tacacs+", "group_radius"):
            if not aaa_server_reachable:
                continue  # Try next method in fallback list
            return {
                "authenticated": aaa_server_accepts,
                "used_method": method,
                "fallback_triggered": False,
                "note": "Server responded; fallback to local is NOT consulted on explicit reject",
            }
        elif method == "local":
            return {
                "authenticated": local_user_accepts,
                "used_method": "local",
                "fallback_triggered": True,
                "note": "Emergency local fallback used because central AAA server was unreachable",
            }
        else:
            raise ValueError(f"Unsupported AAA method: {method}")

    return {
        "authenticated": False,
        "used_method": None,
        "fallback_triggered": False,
        "note": "LOCKED_OUT_NO_LOCAL_FALLBACK_CONFIGURED",
    }


def compare_aaa_protocols(use_case: str) -> dict[str, object]:
    """Recommend TACACS+ vs RADIUS based on Cisco CCNA security architecture."""
    if use_case == "device_admin_cli":
        return {
            "recommended": "TACACS+",
            "transport": "TCP/49",
            "encryption_scope": "Entire packet body (except 12-byte header)",
            "aaa_separation": "Separate Authentication, Authorization (per-command CLI), Accounting",
        }
    if use_case == "network_access_8021x_vpn":
        return {
            "recommended": "RADIUS",
            "transport": "UDP/1812 (Auth) & UDP/1813 (Acct) [or RadSec TLS TCP/2083]",
            "encryption_scope": "Password attribute only (in classic UDP RADIUS)",
            "aaa_separation": "Combines Authentication & Authorization; separate Accounting",
        }
    raise ValueError("use_case must be 'device_admin_cli' or 'network_access_8021x_vpn'")


def audit_password_type(cisco_type: int) -> dict[str, object]:
    """Audit Cisco IOS password/secret hash types (Type 0, 7, 5, 8, 9)."""
    if type(cisco_type) is not int or cisco_type not in (0, 5, 7, 8, 9):
        raise ValueError("cisco_type must be one of 0, 5, 7, 8, 9")
    profiles = {
        0: {"algorithm": "Cleartext", "reversible": True, "secure_for_prod": False},
        7: {"algorithm": "Vigenere obfuscation (service password-encryption)", "reversible": True, "secure_for_prod": False},
        5: {"algorithm": "MD5 salted hash", "reversible": False, "secure_for_prod": False},
        8: {"algorithm": "PBKDF2-HMAC-SHA256", "reversible": False, "secure_for_prod": True},
        9: {"algorithm": "scrypt (memory-hard KDF)", "reversible": False, "secure_for_prod": True},
    }
    return {"cisco_type": cisco_type, **profiles[cisco_type]}


def main() -> None:
    # Wrong password on reachable server must NOT fall back to local!
    reject_no_fb = evaluate_aaa_login(["group_tacacs+", "local"], True, False, True)
    assert reject_no_fb["authenticated"] is False and reject_no_fb["fallback_triggered"] is False

    # Unreachable server with local fallback succeeds
    ok_fb = evaluate_aaa_login(["group_tacacs+", "local"], False, False, True)
    assert ok_fb["authenticated"] is True and ok_fb["fallback_triggered"] is True

    # Unreachable server without local fallback -> lockout
    lockout = evaluate_aaa_login(["group_tacacs+"], False, False, True)
    assert lockout["authenticated"] is False and "LOCKED_OUT" in str(lockout["note"])

    t_rec = compare_aaa_protocols("device_admin_cli")
    assert t_rec["recommended"] == "TACACS+"
    assert audit_password_type(7)["reversible"] is True
    assert audit_password_type(9)["secure_for_prod"] is True

    print("AAA Explicit Reject (no fallback):", reject_no_fb)
    print("AAA Server Unreachable -> Local Fallback:", ok_fb)
    print("AAA Lockout Risk:", lockout)
    print("Protocol Selection:", t_rec)
    print("Hash Audit (Type 7 vs 9):", audit_password_type(7), audit_password_type(9))


if __name__ == "__main__":
    main()
