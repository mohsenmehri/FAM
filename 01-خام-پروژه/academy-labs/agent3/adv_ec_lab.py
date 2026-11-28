"""Local Python Mock for adv_ec (EtherChannel Flow Hashing & FHRP Priority/Tracking Model).

Educational local model only — no live Cisco Catalyst/Nexus switch, hardware ASIC hash
pipeline, or real HSRP/VRRP/GLBP multicast control plane is contacted.
Models:
1. Illustrative per-flow hash distribution across N member links using dst-ip vs src-dst-ip-port
   (demonstrating why flow entropy & hash key choice matter, without assuming a single universal
   hardware hash bit-width across all switch ASICs).
2. FHRP (HSRP/VRRP) active election with preemption, IP SLA object-tracking decrement,
   and failover eligibility.
"""
from __future__ import annotations

import hashlib
import ipaddress

VALID_HASH_MODES = frozenset({"dst-ip", "src-dst-ip", "src-dst-ip-port"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r}")
    return val


def _require_int_range(val: object, name: str, lo: int, hi: int) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (lo <= val <= hi):
        raise ValueError(f"{name} must be an int in {lo}..{hi}, got {val!r}")
    return val


def simulate_etherchannel_hash(
    flows: list[dict[str, object]],
    member_count: int,
    hash_mode: str,
) -> dict[str, object]:
    """Illustrative deterministic per-flow hash distribution across N links (NOT ASIC-exact)."""
    n_links = _require_int_range(member_count, "member_count", 1, 16)
    if not isinstance(hash_mode, str) or hash_mode not in VALID_HASH_MODES:
        raise ValueError(f"hash_mode must be in {sorted(VALID_HASH_MODES)}")
    if not isinstance(flows, list) or not flows:
        raise ValueError("flows must be a non-empty list of flow dicts")

    counts = [0] * n_links
    for flow in flows:
        if not isinstance(flow, dict):
            raise ValueError("each flow must be a dict")
        src_ip = str(ipaddress.ip_address(str(flow["src_ip"])))
        dst_ip = str(ipaddress.ip_address(str(flow["dst_ip"])))
        src_port = _require_int_range(flow["src_port"], "src_port", 1, 65535)
        dst_port = _require_int_range(flow["dst_port"], "dst_port", 1, 65535)
        if hash_mode == "dst-ip":
            key = dst_ip
        elif hash_mode == "src-dst-ip":
            key = f"{src_ip}|{dst_ip}"
        else:
            key = f"{src_ip}:{src_port}|{dst_ip}:{dst_port}"
        digest = hashlib.sha256(key.encode("ascii")).digest()
        bucket = int.from_bytes(digest[:4], "big") % n_links
        counts[bucket] += 1

    utilized_links = sum(1 for c in counts if c > 0)
    return {
        "hash_mode": hash_mode,
        "member_count": n_links,
        "per_link_flow_counts": counts,
        "utilized_links": utilized_links,
        "max_link_share_pct": round((max(counts) / len(flows)) * 100.0, 2),
        "model_scope_note": "Illustrative SHA-256 flow-entropy model only; real switch ASIC hash algorithms and bucket tables vary by hardware platform.",
    }


def evaluate_fhrp_failover(
    r1_priority: int,
    r2_priority: int,
    track_decrement: int,
    uplink_up: bool,
    r2_preempt: bool,
) -> dict[str, object]:
    """Model HSRP/VRRP active router election before and after tracked uplink failure."""
    p1 = _require_int_range(r1_priority, "r1_priority", 0, 255)
    p2 = _require_int_range(r2_priority, "r2_priority", 0, 255)
    dec = _require_int_range(track_decrement, "track_decrement", 0, 255)
    up = _require_bool(uplink_up, "uplink_up")
    preempt = _require_bool(r2_preempt, "r2_preempt")

    eff_p1 = p1 if up else max(0, p1 - dec)
    if up:
        active = "R1" if eff_p1 >= p2 else "R2"
        reason = "UPLINK_UP_NORMAL_ELECTION"
    else:
        if p2 > eff_p1 and preempt:
            active = "R2"
            reason = "PREEMPT_FAILOVER_TO_R2_AFTER_TRACK_DECREMENT"
        elif p2 > eff_p1 and not preempt:
            active = "R1"
            reason = "STUCK_ON_R1_BECAUSE_R2_PREEMPT_DISABLED"
        else:
            active = "R1"
            reason = "DECREMENT_TOO_SMALL_R1_STILL_HIGHER"

    return {
        "r1_effective_priority": eff_p1,
        "r2_priority": p2,
        "active_router_in_model": active,
        "reason": reason,
    }


def main() -> None:
    print("Local Python Mock only — no live Catalyst/Nexus ASIC or real FHRP peers are contacted.")
    # Many users talking to a single server IP (e.g., backup server)
    flows = [
        {"src_ip": f"10.10.1.{i}", "dst_ip": "10.20.0.50", "src_port": 40000 + i, "dst_port": 443}
        for i in range(10, 42)
    ]
    poor = simulate_etherchannel_hash(flows, member_count=4, hash_mode="dst-ip")
    better = simulate_etherchannel_hash(flows, member_count=4, hash_mode="src-dst-ip-port")
    assert poor["utilized_links"] == 1 and better["utilized_links"] > 1
    print("dst-ip hash (single server hotspot):", poor)
    print("src-dst-ip-port hash (distributed):", better)

    no_preempt = evaluate_fhrp_failover(110, 100, track_decrement=20, uplink_up=False, r2_preempt=False)
    with_preempt = evaluate_fhrp_failover(110, 100, track_decrement=20, uplink_up=False, r2_preempt=True)
    assert no_preempt["active_router_in_model"] == "R1"
    assert with_preempt["active_router_in_model"] == "R2"
    print("FHRP failover with preempt:", with_preempt)


if __name__ == "__main__":
    main()
