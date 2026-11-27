"""Local Python Mock for spec_ent (IS-IS NET/Adjacency & SD-Access to SD-WAN Hand-off).

No real Cisco IOS-XE, Catalyst Center, SD-WAN router, or CLNS packet is executed.
"""
from __future__ import annotations

from dataclasses import dataclass


def ipv4_to_isis_system_id(loopback_ipv4: str) -> str:
    """Convert an IPv4 loopback into Cisco's standard 6-byte BCD System ID."""
    octets = [int(part) for part in loopback_ipv4.strip().split(".")]
    if len(octets) != 4 or any(not (0 <= o <= 255) for o in octets):
        raise ValueError(f"Invalid IPv4 address: {loopback_ipv4}")
    padded = "".join(f"{o:03d}" for o in octets)
    return f"{padded[0:4]}.{padded[4:8]}.{padded[8:12]}"


def parse_isis_net(net: str) -> dict[str, str]:
    """Parse an IS-IS NET address (e.g. 49.0001.0102.5500.0001.00)."""
    parts = net.strip().split(".")
    if len(parts) < 5 or parts[-1] != "00":
        raise ValueError(f"Invalid IS-IS NET format or non-zero NSEL: {net}")
    system_id = ".".join(parts[-4:-1])
    if any(len(group) != 4 for group in parts[-4:-1]):
        raise ValueError(f"System ID must be three 4-hex-digit groups: {system_id}")
    area_id = ".".join(parts[:-4])
    return {"area_id": area_id, "system_id": system_id, "nsel": parts[-1]}


@dataclass(frozen=True)
class IsisInterface:
    router: str
    net: str
    level: str  # "L1", "L2", "L1L2"
    mtu: int
    network_type: str  # "point-to-point" or "broadcast"
    hello_padding: bool = True


def check_isis_adjacency(a: IsisInterface, b: IsisInterface) -> dict[str, object]:
    """Evaluate whether two IS-IS interfaces can form an L1 and/or L2 adjacency."""
    pa = parse_isis_net(a.net)
    pb = parse_isis_net(b.net)
    reasons: list[str] = []

    if pa["system_id"] == pb["system_id"]:
        reasons.append("Duplicate 6-byte System ID prevents adjacency.")
    if a.network_type != b.network_type:
        reasons.append(f"Network type mismatch: {a.network_type} vs {b.network_type}.")
    if (a.hello_padding or b.hello_padding) and a.mtu != b.mtu:
        reasons.append(f"MTU mismatch ({a.mtu} vs {b.mtu}) with hello padding enabled.")

    levels_a = {"L1", "L2"} if a.level == "L1L2" else {a.level}
    levels_b = {"L1", "L2"} if b.level == "L1L2" else {b.level}
    common = sorted(levels_a & levels_b)
    formed: list[str] = []

    if not reasons:
        if "L1" in common:
            if pa["area_id"] == pb["area_id"]:
                formed.append("L1")
            else:
                reasons.append(f"L1 requires matching Area ID ({pa['area_id']} != {pb['area_id']}).")
        if "L2" in common:
            formed.append("L2")
        if not common:
            reasons.append(f"No overlapping IS-IS level ({a.level} vs {b.level}).")

    return {"up": bool(formed), "formed_levels": formed, "reasons": reasons}


def check_sda_sdwan_handoff(
    vn_name: str,
    sdwan_vpn_id: int | None,
    sgt_id: int,
    transport_mechanism: str,
) -> dict[str, object]:
    """Validate macro (VRF/VN -> VPN) and micro (SGT) preservation across Border hand-off."""
    macro_ok = sdwan_vpn_id is not None and sdwan_vpn_id > 0
    valid_sgt_transports = {"inline_cmd", "vxlan_gpo_metadata", "sxp"}
    micro_ok = transport_mechanism in valid_sgt_transports and 2 <= sgt_id <= 65519
    notes: list[str] = []
    if not macro_ok:
        notes.append(f"VN '{vn_name}' is not mapped to a valid SD-WAN service VPN.")
    if not micro_ok:
        notes.append(
            f"SGT {sgt_id} is lost across hand-off: plain IP carries no SGT "
            f"(transport='{transport_mechanism}')."
        )
    return {
        "vn": vn_name,
        "sdwan_vpn": sdwan_vpn_id,
        "sgt": sgt_id,
        "macro_preserved": macro_ok,
        "micro_preserved": micro_ok,
        "notes": notes,
    }


def main() -> None:
    print("Local Python Mock only — no real Cisco router, IS-IS process, or SD-WAN fabric is run.")
    sys_r1 = ipv4_to_isis_system_id("10.255.0.1")
    sys_r2 = ipv4_to_isis_system_id("10.255.0.2")
    r1 = IsisInterface("R1-ACCESS", f"49.0001.{sys_r1}.00", "L2", 1500, "point-to-point")
    r2 = IsisInterface("R2-BORDER", f"49.0002.{sys_r2}.00", "L2", 1500, "point-to-point")
    r2_mtu_bad = IsisInterface("R2-BORDER", f"49.0002.{sys_r2}.00", "L2", 1492, "point-to-point")
    print("L2 cross-area healthy:", check_isis_adjacency(r1, r2))
    print("L2 MTU mismatch:", check_isis_adjacency(r1, r2_mtu_bad))
    print("Hand-off with SXP:", check_sda_sdwan_handoff("VN_FINANCE", 10, 15, "sxp"))
    print("Hand-off plain IP:", check_sda_sdwan_handoff("VN_FINANCE", 10, 15, "plain_ip"))


if __name__ == "__main__":
    main()
