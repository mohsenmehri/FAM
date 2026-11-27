"""Local Python Mock for spec_collab (VoIP Bandwidth Math, SIP/SDP & CUCM Dial Plan).

No real Cisco CUCM, CUBE, SIP phone, or RTP media stream is executed.
Strict validation rejects non-bool flags (e.g. dot1q='False'), non-positive packetization
intervals (preventing ZeroDivisionError), negative overhead bytes, and empty dialed strings.
"""
from __future__ import annotations

CODECS = {
    "G.711": {"payload_bytes_20ms": 160, "codec_kbps": 64.0},
    "G.729": {"payload_bytes_20ms": 20, "codec_kbps": 8.0},
}


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_int(val: object, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int):
        raise ValueError(f"{name} must be an int (not bool), got {val!r} ({type(val).__name__})")
    return val


def voip_bandwidth_per_direction(
    codec: str,
    packetization_ms: int = 20,
    dot1q: bool = False,
    include_wire_preamble_ifg: bool = False,
    srtp_auth_tag_bytes: int = 0,
    tunnel_overhead_bytes: int = 0,
) -> dict[str, float]:
    """Compute exact single-direction VoIP bandwidth in kbps for L3 and L2 Ethernet."""
    if codec not in CODECS:
        raise ValueError(f"Unsupported codec: {codec!r}")
    pkt_ms = _require_int(packetization_ms, "packetization_ms")
    if pkt_ms <= 0:
        raise ValueError(f"packetization_ms must be positive, got {pkt_ms}")
    use_dot1q = _require_bool(dot1q, "dot1q")
    use_wire = _require_bool(include_wire_preamble_ifg, "include_wire_preamble_ifg")
    srtp_b = _require_int(srtp_auth_tag_bytes, "srtp_auth_tag_bytes")
    tunnel_b = _require_int(tunnel_overhead_bytes, "tunnel_overhead_bytes")
    if srtp_b < 0 or tunnel_b < 0:
        raise ValueError("srtp_auth_tag_bytes and tunnel_overhead_bytes must be non-negative")

    pps = 1000.0 / pkt_ms
    scale = pkt_ms / 20.0
    payload = CODECS[codec]["payload_bytes_20ms"] * scale
    l3_l4_headers = 20 + 8 + 12  # IPv4 (20) + UDP (8) + RTP (12) = 40 B
    l3_bytes = payload + l3_l4_headers + srtp_b + tunnel_b
    eth_header_fcs = 18 + (4 if use_dot1q else 0)
    l2_bytes = l3_bytes + eth_header_fcs
    wire_bytes = l2_bytes + (20 if use_wire else 0)  # 8B Preamble/SFD + 12B IFG
    return {
        "pps": pps,
        "l3_bytes": l3_bytes,
        "l3_kbps": round((l3_bytes * 8 * pps) / 1000.0, 2),
        "l2_bytes": l2_bytes,
        "l2_kbps": round((l2_bytes * 8 * pps) / 1000.0, 2),
        "wire_kbps": round((wire_bytes * 8 * pps) / 1000.0, 2),
    }


def evaluate_cucm_dial_plan(
    dialed_number: str,
    line_css: list[str],
    device_css: list[str],
    route_table: list[dict[str, str]],
) -> dict[str, object]:
    """Model CUCM CSS evaluation: Line CSS precedes Device CSS, longest match wins, CSS order breaks ties."""
    if not isinstance(dialed_number, str) or not dialed_number.strip():
        raise ValueError("dialed_number must be a non-empty str")
    effective_css = list(line_css) + [p for p in device_css if p not in line_css]
    candidates = []
    for entry in route_table:
        part = entry["partition"]
        if part not in effective_css:
            continue
        prefix = entry["prefix"]
        if dialed_number.startswith(prefix):
            candidates.append((len(prefix), -effective_css.index(part), entry))
    if not candidates:
        return {"matched": False, "effective_css": effective_css, "action": "reorder_tone_blocked"}
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    winner = candidates[0][2]
    return {
        "matched": True,
        "effective_css": effective_css,
        "matched_pattern": winner["prefix"],
        "partition": winner["partition"],
        "action": winner["action"],
    }


def main() -> None:
    print("Local Python Mock only — no real CUCM cluster, SIP trunk, or RTP flow is run.")
    g711_base = voip_bandwidth_per_direction("G.711")
    g711_q = voip_bandwidth_per_direction("G.711", dot1q=True)
    g729_base = voip_bandwidth_per_direction("G.729")
    assert g711_base["l2_kbps"] == 87.2
    assert g711_q["l2_kbps"] == 88.8
    assert g729_base["l2_kbps"] == 31.2
    routes = [
        {"prefix": "900", "partition": "PT_BLOCK_INTL", "action": "block"},
        {"prefix": "900", "partition": "PT_ALLOW_INTL", "action": "route_to_cube"},
        {"prefix": "9", "partition": "PT_LOCAL", "action": "route_local"},
    ]
    res = evaluate_cucm_dial_plan("900441234", ["PT_BLOCK_INTL"], ["PT_ALLOW_INTL", "PT_LOCAL"], routes)
    assert res["matched"] is True and res["action"] == "block"
    print("G.711 (20ms, base Eth):", g711_base)
    print("G.711 (20ms, 802.1Q):", g711_q)
    print("G.729 (20ms, base Eth):", g729_base)
    print("Line CSS overrides Device CSS on tie:", res)


if __name__ == "__main__":
    main()
