"""Local Python Mock for spec_ent (IS-IS NET/Adjacency & SD-Access to SD-WAN Hand-off).

No real Cisco IOS-XE, Catalyst Center, SD-WAN router, or CLNS packet is executed.
Strict input validation rejects non-bool flags, invalid IPv4/hex NETs, non-positive MTU,
and invalid IS-IS levels or network types.
"""
from __future__ import annotations

from dataclasses import dataclass
import ipaddress


VALID_LEVELS = {"L1", "L2", "L1L2"}
VALID_NETWORK_TYPES = {"point-to-point", "broadcast"}


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int):
        raise ValueError(f"{name} must be an int (not bool), got {val!r} ({type(val).__name__})")
    return val


def ipv4_to_isis_system_id(loopback_ipv4: str) -> str:
    """Convert an IPv4 loopback into Cisco's standard 6-byte BCD System ID."""
    if not isinstance(loopback_ipv4, str):
        raise ValueError(f"loopback_ipv4 must be str, got {loopback_ipv4!r}")
    try:
        addr = ipaddress.IPv4Address(loopback_ipv4.strip())
    except ipaddress.AddressValueError as exc:
        raise ValueError(f"Invalid IPv4 address: {loopback_ipv4!r}") from exc
    padded = "".join(f"{octet:03d}" for octet in addr.packed)
    return f"{padded[0:4]}.{padded[4:8]}.{padded[8:12]}"


def parse_isis_net(net: str) -> dict[str, str]:
    """Parse an IS-IS NET address (e.g. 49.0001.0102.5500.0001.00)."""
    if not isinstance(net, str) or not net.strip():
        raise ValueError(f"IS-IS NET must be a non-empty str, got {net!r}")
    parts = net.strip().split(".")
    if len(parts) < 5 or parts[-1] != "00":
        raise ValueError(f"Invalid IS-IS NET format or non-zero NSEL: {net}")
    sys_groups = parts[-4:-1]
    for group in sys_groups:
        if len(group) != 4:
            raise ValueError(f"System ID must be three 4-hex-digit groups: {'.'.join(sys_groups)}")
        try:
            int(group, 16)
        except ValueError as exc:
            raise ValueError(f"Non-hex group in IS-IS System ID: {group!r}") from exc
    area_parts = parts[:-4]
    if any(not p or len(p) % 2 != 0 for p in area_parts):
        raise ValueError(f"Invalid IS-IS Area ID segments: {'.'.join(area_parts)!r}")
    for p in area_parts:
        try:
            int(p, 16)
        except ValueError as exc:
            raise ValueError(f"Non-hex group in IS-IS Area ID: {p!r}") from exc
    return {"area_id": ".".join(area_parts), "system_id": ".".join(sys_groups), "nsel": parts[-1]}


@dataclass(frozen=True)
class IsisInterface:
    router: str
    net: str
    level: str  # "L1", "L2", "L1L2"
    mtu: int
    network_type: str  # "point-to-point" or "broadcast"
    hello_padding: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.router, str) or not self.router.strip():
            raise ValueError("router name must be a non-empty str")
        if self.level not in VALID_LEVELS:
            raise ValueError(f"level must be one of {sorted(VALID_LEVELS)}, got {self.level!r}")
        mtu_val = _require_int(self.mtu, "mtu")
        if mtu_val <= 0:
            raise ValueError(f"mtu must be positive, got {mtu_val}")
        if self.network_type not in VALID_NETWORK_TYPES:
            raise ValueError(f"network_type must be one of {sorted(VALID_NETWORK_TYPES)}, got {self.network_type!r}")
        _require_bool(self.hello_padding, "hello_padding")


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
    if not isinstance(vn_name, str) or not vn_name.strip():
        raise ValueError("vn_name must be a non-empty str")
    if sdwan_vpn_id is not None:
        _require_int(sdwan_vpn_id, "sdwan_vpn_id")
    _require_int(sgt_id, "sgt_id")
    if not isinstance(transport_mechanism, str):
        raise ValueError(f"transport_mechanism must be str, got {transport_mechanism!r}")

    macro_ok = sdwan_vpn_id is not None and 1 <= sdwan_vpn_id <= 65530 and sdwan_vpn_id != 512
    valid_sgt_transports = {"inline_cmd", "vxlan_gpo_metadata", "sxp"}
    micro_ok = transport_mechanism in valid_sgt_transports and 2 <= sgt_id <= 65519
    notes: list[str] = []
    if not macro_ok:
        notes.append(f"VN '{vn_name}' is not mapped to a valid SD-WAN service VPN (must be 1..65530 excluding 0/512).")
    if not micro_ok:
        notes.append(
            f"SGT {sgt_id} is lost or out of range (2..65519) across hand-off "
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
    assert sys_r1 == "0102.5500.0001"
    r1 = IsisInterface("R1-ACCESS", f"49.0001.{sys_r1}.00", "L2", 1500, "point-to-point")
    r2 = IsisInterface("R2-BORDER", f"49.0002.{sys_r2}.00", "L2", 1500, "point-to-point")
    r2_mtu_bad = IsisInterface("R2-BORDER", f"49.0002.{sys_r2}.00", "L2", 1492, "point-to-point")
    ok_adj = check_isis_adjacency(r1, r2)
    bad_adj = check_isis_adjacency(r1, r2_mtu_bad)
    assert ok_adj["up"] is True and ok_adj["formed_levels"] == ["L2"]
    assert bad_adj["up"] is False
    handoff_ok = check_sda_sdwan_handoff("VN_FINANCE", 10, 15, "sxp")
    handoff_bad = check_sda_sdwan_handoff("VN_FINANCE", 10, 15, "plain_ip")
    assert handoff_ok["macro_preserved"] is True and handoff_ok["micro_preserved"] is True
    assert handoff_bad["micro_preserved"] is False
    print("L2 cross-area healthy:", ok_adj)
    print("L2 MTU mismatch:", bad_adj)
    print("Hand-off with SXP:", handoff_ok)
    print("Hand-off plain IP:", handoff_bad)


if __name__ == "__main__":
    main()
