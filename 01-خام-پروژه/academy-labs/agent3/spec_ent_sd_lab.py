#!/usr/bin/env python3
"""
FAM Academy Lab — spec_ent_sd: Cisco PnP (DHCP Option 43), SD-WAN ZTP (SUDI)
& TLOC Extension Local Mock.
Execution boundary: Pure Python 3 stdlib simulation of DHCP Option 43 parsing,
SUDI/Serial whitelist verification against vManage/Smart Account, and dual-WAN
TLOC Extension reachability. No live Catalyst Center or SD-WAN controllers.
"""

from __future__ import annotations

import json


def parse_pnp_option43(opt43: str) -> dict:
    parts = opt43.split(";")
    parsed = {}
    for p in parts:
        if p.startswith("I"):
            parsed["controller_ip"] = p[1:]
        elif p.startswith("J"):
            parsed["port"] = int(p[1:])
        elif p.startswith("K"):
            parsed["transport"] = "HTTPS" if p[1:] == "4" else "HTTP"
    return parsed


def verify_sdwan_ztp(device_serial: str, sudi_valid: bool, allowed_serials: set[str]) -> dict:
    if not sudi_valid:
        return {"admitted": False, "reason": "Invalid or missing hardware SUDI/TPM certificate"}
    if device_serial not in allowed_serials:
        return {"admitted": False, "reason": "Serial not registered in Smart Account / vManage"}
    return {"admitted": True, "reason": "Authenticated via SUDI + Smart Account whitelist"}


def tloc_available_transports(r1_direct: list[str], r2_direct: list[str], tloc_ext_enabled: bool) -> dict:
    if not tloc_ext_enabled:
        return {"R1_transports": r1_direct, "R2_transports": r2_direct}
    return {
        "R1_transports": sorted(set(r1_direct + r2_direct)),
        "R2_transports": sorted(set(r2_direct + r1_direct)),
    }


def main() -> None:
    pnp = parse_pnp_option43("5A1D;B2;K4;I10.10.10.5;J443")
    assert pnp == {"transport": "HTTPS", "controller_ip": "10.10.10.5", "port": 443}

    whitelist = {"C8300-BR001", "C8300-BR002"}
    legit = verify_sdwan_ztp("C8300-BR001", sudi_valid=True, allowed_serials=whitelist)
    rogue = verify_sdwan_ztp("C8300-ROGUE", sudi_valid=True, allowed_serials=whitelist)
    assert legit["admitted"] is True and rogue["admitted"] is False

    tloc = tloc_available_transports(["mpls"], ["biz-internet"], tloc_ext_enabled=True)
    assert tloc["R1_transports"] == ["biz-internet", "mpls"]

    print("=== spec_ent_sd PnP Option 43, ZTP SUDI & TLOC Extension Mock ===")
    print(json.dumps({
        "parsed_pnp_option43": pnp,
        "ztp_legit_router": legit,
        "ztp_rogue_router": rogue,
        "tloc_extension_transports": tloc,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
