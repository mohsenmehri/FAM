"""Local Python Mock for ccnp_ensdwi (Cisco Catalyst SD-WAN OMP TLOC & AAR SLA Selector).

Educational local model only — no live vManage/vSmart/vBond/WAN-Edge controller,
OMP session, or live BFD probe is contacted.
Models:
1. Application-Aware Routing (AAR) SLA tunnel selector across MPLS / biz-internet / lte TLOCs
   checking BFD loss %, latency (ms), and jitter (ms) against an application SLA class.
2. Fallback behavior when NO transport meets SLA (strict preferred-color vs fallback-to-best-available).
"""
from __future__ import annotations

import math


def _require_non_neg_float(val: object, name: str, max_val: float = 100_000.0) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(float(val)):
        raise ValueError(f"{name} must be a finite number, got {val!r}")
    f = float(val)
    if not (0.0 <= f <= max_val):
        raise ValueError(f"{name} must be in 0..{max_val}, got {f}")
    return f


def select_aar_tloc(
    tlocs: list[dict[str, object]],
    max_loss_pct: float,
    max_latency_ms: float,
    max_jitter_ms: float,
    preferred_color: str | None = None,
) -> dict[str, object]:
    """Select an SD-WAN TLOC meeting BFD SLA thresholds, with explicit fallback if none comply."""
    mloss = _require_non_neg_float(max_loss_pct, "max_loss_pct", 100.0)
    mlat = _require_non_neg_float(max_latency_ms, "max_latency_ms", 60_000.0)
    mjit = _require_non_neg_float(max_jitter_ms, "max_jitter_ms", 60_000.0)
    if not isinstance(tlocs, list) or not tlocs:
        raise ValueError("tlocs must be a non-empty list")

    compliant: list[dict[str, object]] = []
    up_tlocs: list[dict[str, object]] = []
    for t in tlocs:
        color = str(t.get("color", "")).strip()
        if not color:
            raise ValueError("tloc color must be non-empty")
        bfd_up = t.get("bfd_up")
        if not isinstance(bfd_up, bool):
            raise ValueError("bfd_up must be a strict bool")
        loss = _require_non_neg_float(t["loss_pct"], "loss_pct", 100.0)
        lat = _require_non_neg_float(t["latency_ms"], "latency_ms", 60_000.0)
        jit = _require_non_neg_float(t["jitter_ms"], "jitter_ms", 60_000.0)
        entry = {"color": color, "bfd_up": bfd_up, "loss_pct": loss, "latency_ms": lat, "jitter_ms": jit}
        if not bfd_up:
            continue
        up_tlocs.append(entry)
        if loss <= mloss and lat <= mlat and jit <= mjit:
            compliant.append(entry)

    if not up_tlocs:
        return {"selected_color": None, "sla_met": False, "reason": "NO_BFD_UP_TLOC_AVAILABLE"}

    if compliant:
        if preferred_color:
            pref = [c for c in compliant if c["color"] == preferred_color]
            if pref:
                return {"selected_color": pref[0]["color"], "sla_met": True, "reason": "PREFERRED_COLOR_MET_SLA"}
        best = sorted(compliant, key=lambda x: (x["loss_pct"], x["latency_ms"], x["jitter_ms"]))[0]
        return {"selected_color": best["color"], "sla_met": True, "reason": "BEST_SLA_COMPLIANT_TLOC"}

    fallback = sorted(up_tlocs, key=lambda x: (x["loss_pct"], x["latency_ms"], x["jitter_ms"]))[0]
    return {
        "selected_color": fallback["color"],
        "sla_met": False,
        "reason": "NO_TLOC_MET_SLA_FALLBACK_TO_LEAST_DEGRADED_UP_TLOC",
    }


def main() -> None:
    print("Local Python Mock only — no live vManage/vSmart/vBond/WAN-Edge or BFD probe is contacted.")
    tlocs = [
        {"color": "mpls", "bfd_up": True, "loss_pct": 3.5, "latency_ms": 40.0, "jitter_ms": 5.0},
        {"color": "biz-internet", "bfd_up": True, "loss_pct": 0.2, "latency_ms": 55.0, "jitter_ms": 8.0},
        {"color": "lte", "bfd_up": False, "loss_pct": 0.0, "latency_ms": 90.0, "jitter_ms": 20.0},
    ]
    res = select_aar_tloc(tlocs, max_loss_pct=1.0, max_latency_ms=150.0, max_jitter_ms=30.0, preferred_color="mpls")
    assert res["selected_color"] == "biz-internet" and res["sla_met"] is True
    print("AAR SLA selection (MPLS degraded -> switched to biz-internet):", res)


if __name__ == "__main__":
    main()
