#!/usr/bin/env python3
"""
FAM Academy Lab — spec_ent_sd: Cisco PnP (DHCP Option 43), SD-WAN ZTP (SUDI)
& TLOC Extension Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of DHCP Option 43 parsing
(with IP/port validation), strict-boolean SUDI/Serial whitelist verification
against vManage/Smart Account, and dual-WAN TLOC Extension reachability.
No live Catalyst Center or SD-WAN controllers.
"""

from __future__ import annotations

import ipaddress
import json


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def parse_pnp_option43(opt43: str) -> dict:
    parts = opt43.split(";")
    parsed = {}
    for p in parts:
        if p.startswith("I"):
            ip_str = p[1:]
            ipaddress.ip_address(ip_str)  # validate IP syntax
            parsed["controller_ip"] = ip_str
        elif p.startswith("J"):
            port = int(p[1:])
            if not (1 <= port <= 65535):
                raise ValueError(f"Invalid PnP controller TCP port: {port}")
            parsed["port"] = port
        elif p.startswith("K"):
            if p[1:] == "4":
                parsed["transport"] = "HTTPS"
            elif p[1:] == "1":
                parsed["transport"] = "HTTP"
            else:
                raise ValueError(f"Unsupported PnP transport code: {p!r}")
    return parsed


def verify_sdwan_ztp(device_serial: str, sudi_valid: bool, allowed_serials: set[str]) -> dict:
    sudi_ok = _require_bool(sudi_valid, "sudi_valid")
    if not sudi_ok:
        return {"admitted": False, "reason": "Invalid or missing hardware SUDI/TPM certificate"}
    if device_serial not in allowed_serials:
        return {"admitted": False, "reason": "Serial not registered in Smart Account / vManage"}
    return {"admitted": True, "reason": "Authenticated via SUDI + Smart Account whitelist"}


def tloc_available_transports(r1_direct: list[str], r2_direct: list[str], tloc_ext_enabled: bool) -> dict:
    ext_ok = _require_bool(tloc_ext_enabled, "tloc_ext_enabled")
    if not ext_ok:
        return {"R1_transports": list(r1_direct), "R2_transports": list(r2_direct)}
    return {
        "R1_transports": sorted(set(r1_direct + r2_direct)),
        "R2_transports": sorted(set(r2_direct + r1_direct)),
    }


def main() -> None:
    pnp = parse_pnp_option43("5A1D;B2;K4;I10.10.10.5;J443")
    assert pnp == {"transport": "HTTPS", "controller_ip": "10.10.10.5", "port": 443}

    whitelist = {"C8300-BR001", "C8300-BR002"}
    legit = verify_sdwan_ztp("C8300-BR001", sudi_valid=True, allowed_serials=whitelist)
    rogue_serial = verify_sdwan_ztp("C8300-ROGUE", sudi_valid=True, allowed_serials=whitelist)
    invalid_sudi = verify_sdwan_ztp("C8300-BR001", sudi_valid=False, allowed_serials=whitelist)
    assert legit["admitted"] is True and rogue_serial["admitted"] is False and invalid_sudi["admitted"] is False

    tloc = tloc_available_transports(["mpls"], ["biz-internet"], tloc_ext_enabled=True)
    assert tloc["R1_transports"] == ["biz-internet", "mpls"]

    print("=== spec_ent_sd PnP Option 43, ZTP SUDI & TLOC Extension Mock ===")
    print(json.dumps({
        "parsed_pnp_option43": pnp,
        "ztp_legit_router": legit,
        "ztp_rogue_router": rogue_serial,
        "ztp_invalid_sudi": invalid_sudi,
        "tloc_extension_transports": tloc,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
