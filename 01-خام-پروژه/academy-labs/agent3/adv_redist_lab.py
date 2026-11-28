"""Local Python Mock for adv_redist (Prefix-List ge/le Matcher & Mutual Redistribution Tag Guard).

Educational local model only — no live Cisco IOS/IOS-XE router is contacted.
Models:
1. Exact Prefix-List evaluation with `ge` and `le` prefix-length bounds.
2. Two-router mutual redistribution (OSPF <-> EIGRP) showing how missing route-tag
   filtering can cause Route Feedback / suboptimal domain loops, and how tagging
   (e.g., tag 110 / tag 90) blocks re-injection across border routers.
"""
from __future__ import annotations

import ipaddress


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r}")
    return val


def _require_int_range(val: object, name: str, lo: int, hi: int) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (lo <= val <= hi):
        raise ValueError(f"{name} must be an int in {lo}..{hi}, got {val!r}")
    return val


def match_prefix_list_entry(
    candidate_prefix: str,
    rule_prefix: str,
    ge: int | None = None,
    le: int | None = None,
) -> bool:
    """Evaluate Cisco-style IPv4 ip prefix-list rule with optional ge/le bounds."""
    cand = ipaddress.IPv4Network(candidate_prefix, strict=True)
    rule = ipaddress.IPv4Network(rule_prefix, strict=True)
    base_len = rule.prefixlen

    if ge is not None:
        ge_val = _require_int_range(ge, "ge", 0, 32)
        if ge_val <= base_len:
            raise ValueError(f"ge ({ge_val}) must be strictly greater than rule prefixlen ({base_len})")
    else:
        ge_val = None

    if le is not None:
        le_val = _require_int_range(le, "le", 0, 32)
        if le_val < (ge_val if ge_val is not None else base_len + 1):
            raise ValueError(f"le ({le_val}) must be >= ge/base_len+1")
    else:
        le_val = None

    if not cand.subnet_of(rule):
        return False
    if ge_val is None and le_val is None:
        return cand.prefixlen == base_len
    min_len = ge_val if ge_val is not None else base_len
    max_len = le_val if le_val is not None else 32
    return min_len <= cand.prefixlen <= max_len


def simulate_mutual_redistribution_guard(
    prefix: str,
    origin_domain: str,
    seed_metric_configured: bool,
    use_route_tags: bool,
) -> dict[str, object]:
    """Model OSPF <-> EIGRP mutual redistribution across two border routers (R1, R2)."""
    net = ipaddress.IPv4Network(prefix, strict=True)
    if origin_domain not in {"ospf", "eigrp"}:
        raise ValueError("origin_domain must be 'ospf' or 'eigrp'")
    has_seed = _require_bool(seed_metric_configured, "seed_metric_configured")
    tagged = _require_bool(use_route_tags, "use_route_tags")

    if not has_seed and origin_domain == "ospf":
        return {
            "prefix": str(net),
            "injected_into_peer_domain": False,
            "route_feedback_detected": False,
            "reason": "EIGRP_SEED_METRIC_INFINITY_WITHOUT_EXPLICIT_METRIC",
        }

    # R1 redistributes origin -> peer (tagging if enabled)
    applied_tag = (110 if origin_domain == "ospf" else 90) if tagged else 0
    # R2 checks whether to re-inject back into origin domain
    if tagged and applied_tag in (110, 90):
        return {
            "prefix": str(net),
            "injected_into_peer_domain": True,
            "applied_tag": applied_tag,
            "route_feedback_detected": False,
            "reason": "REINJECTION_BLOCKED_BY_ROUTE_MAP_TAG_DENY",
        }
    return {
        "prefix": str(net),
        "injected_into_peer_domain": True,
        "applied_tag": 0,
        "route_feedback_detected": True,
        "reason": "UNTAGGED_MUTUAL_REDISTRIBUTION_RISK_ROUTE_FEEDBACK",
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco IOS/IOS-XE router is contacted.")
    # Prefix-list 10.0.0.0/8 ge 24 le 26
    assert match_prefix_list_entry("10.10.20.0/24", "10.0.0.0/8", ge=24, le=26) is True
    assert match_prefix_list_entry("10.10.20.0/27", "10.0.0.0/8", ge=24, le=26) is False
    assert match_prefix_list_entry("192.168.1.0/24", "10.0.0.0/8", ge=24, le=26) is False
    assert match_prefix_list_entry("10.0.0.0/8", "10.0.0.0/8") is True
    assert match_prefix_list_entry("10.1.0.0/16", "10.0.0.0/8") is False

    no_seed = simulate_mutual_redistribution_guard("10.50.0.0/24", "ospf", seed_metric_configured=False, use_route_tags=True)
    unsafe = simulate_mutual_redistribution_guard("10.50.0.0/24", "eigrp", seed_metric_configured=True, use_route_tags=False)
    safe = simulate_mutual_redistribution_guard("10.50.0.0/24", "eigrp", seed_metric_configured=True, use_route_tags=True)
    assert no_seed["injected_into_peer_domain"] is False
    assert unsafe["route_feedback_detected"] is True
    assert safe["route_feedback_detected"] is False
    print("Prefix-list & mutual redistribution tag guard checks passed:", {"no_seed": no_seed, "safe": safe})


if __name__ == "__main__":
    main()
