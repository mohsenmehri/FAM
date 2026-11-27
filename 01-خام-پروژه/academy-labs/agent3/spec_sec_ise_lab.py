#!/usr/bin/env python3
"""
FAM Academy Lab — spec_sec_ise: Cisco ISE Personas, TACACS+ Per-Command AuthZ,
Posture CoA Transition & pxGrid Context Exchange Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of ISE distributed roles,
TACACS+ command-level RBAC (with leading-whitespace normalization), Posture
quarantine-to-compliant CoA (with strict bool typing), and pxGrid publishing to FTD.
No live Cisco ISE appliance connected.
"""

from __future__ import annotations

import json

TACACS_SHELL_POLICY = {
    "helpdesk": {"allow_prefixes": ("show ",), "deny_prefixes": ("configure ", "reload", "debug ")},
    "net-admin": {"allow_prefixes": ("show ", "configure ", "copy "), "deny_prefixes": ("reload",)},
}


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def tacacs_authorize_command(role: str, command: str) -> bool:
    if not isinstance(role, str) or not isinstance(command, str):
        raise ValueError("role and command must be str")
    norm_cmd = command.strip().lower()
    if not norm_cmd:
        return False
    pol = TACACS_SHELL_POLICY.get(role, {"allow_prefixes": (), "deny_prefixes": ()})
    if any(norm_cmd.startswith(d) for d in pol["deny_prefixes"]):
        return False
    return any(norm_cmd.startswith(a) for a in pol["allow_prefixes"])


def evaluate_posture_and_pxgrid(user: str, ip: str, av_updated: bool, os_patched: bool) -> dict:
    if not isinstance(user, str) or not user.strip() or not isinstance(ip, str) or not ip.strip():
        raise ValueError("user and ip must be non-empty str")
    av_ok = _require_bool(av_updated, "av_updated")
    os_ok = _require_bool(os_patched, "os_patched")
    compliant = av_ok and os_ok
    if compliant:
        return {
            "posture_status": "Compliant",
            "coa_action": "Reauthenticate -> Full Corp Access",
            "sgt": 10,
            "pxgrid_topic_published": {"user": user, "ip": ip, "sgt": 10, "posture": "Compliant"},
        }
    return {
        "posture_status": "Non-Compliant",
        "coa_action": "Apply Remediation dACL (AV/Patch Server Only)",
        "sgt": 99,
        "pxgrid_topic_published": {"user": user, "ip": ip, "sgt": 99, "posture": "Non-Compliant"},
    }


def main() -> None:
    assert tacacs_authorize_command("helpdesk", "show ip interface brief") is True
    assert tacacs_authorize_command("helpdesk", "configure terminal") is False
    assert tacacs_authorize_command("net-admin", "configure terminal") is True
    assert tacacs_authorize_command("net-admin", "reload") is False
    assert tacacs_authorize_command("net-admin", "  reload") is False

    before = evaluate_posture_and_pxgrid("ali@corp", "10.20.1.55", av_updated=False, os_patched=True)
    after = evaluate_posture_and_pxgrid("ali@corp", "10.20.1.55", av_updated=True, os_patched=True)
    assert before["sgt"] == 99 and after["sgt"] == 10

    print("=== spec_sec_ise TACACS+, Posture & pxGrid Local Mock ===")
    print(json.dumps({
        "tacacs_helpdesk_show": True,
        "tacacs_helpdesk_conf_t": False,
        "posture_before_patch": before,
        "posture_after_remediation_coa": after,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
