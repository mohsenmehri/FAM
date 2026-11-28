"""Local Python Mock for ccnp_enna (Network Assurance: Synthetic Path Hop Fault Isolation & Health Score).

Educational local model only — no live Cisco ThousandEyes agent, BGP collector,
or Catalyst Center Assurance cluster is contacted.
Models:
1. Synthetic end-to-end transaction breakdown (DNS -> TCP -> TLS -> HTTP TTFB) isolating which
   layer dominates user-perceived delay even when interface status is `up/up`.
2. Path hop-by-hop loss localization (distinguishing ICMP-rate-limited intermediate transit hops
   from genuine sustained loss propagating to the destination!).
"""
from __future__ import annotations

import math


def _require_non_neg_float(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(float(val)) or float(val) < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {val!r}")
    return float(val)


def analyze_synthetic_http_waterfall(
    dns_ms: float,
    tcp_connect_ms: float,
    tls_handshake_ms: float,
    http_ttfb_ms: float,
) -> dict[str, object]:
    """Identify the dominant latency layer in a synthetic HTTP/TLS transaction."""
    stages = {
        "dns": _require_non_neg_float(dns_ms, "dns_ms"),
        "tcp": _require_non_neg_float(tcp_connect_ms, "tcp_connect_ms"),
        "tls": _require_non_neg_float(tls_handshake_ms, "tls_handshake_ms"),
        "http_ttfb": _require_non_neg_float(http_ttfb_ms, "http_ttfb_ms"),
    }
    total = sum(stages.values())
    if total == 0:
        raise ValueError("total waterfall time must be > 0")
    dominant = max(stages, key=lambda k: stages[k])
    share = round((stages[dominant] / total) * 100.0, 2)
    return {
        "total_ms": round(total, 2),
        "dominant_stage": dominant,
        "dominant_share_pct": share,
        "stages_ms": stages,
    }


def localize_path_loss(hops: list[dict[str, object]]) -> dict[str, object]:
    """Distinguish control-plane ICMP rate-limiting on one transit hop from real sustained path loss."""
    if not isinstance(hops, list) or len(hops) < 2:
        raise ValueError("hops must be a list of at least 2 hop dicts")
    losses = []
    for h in hops:
        hop_num = h.get("hop")
        if isinstance(hop_num, bool) or not isinstance(hop_num, int) or hop_num < 1:
            raise ValueError("hop must be a positive int")
        loss = _require_non_neg_float(h["loss_pct"], "loss_pct")
        if loss > 100.0:
            raise ValueError("loss_pct must be <= 100")
        losses.append((hop_num, str(h.get("node", "")), loss))

    end_loss = losses[-1][2]
    if end_loss == 0.0:
        transit_spikes = [x for x in losses[:-1] if x[2] > 0.0]
        return {
            "real_forwarding_loss": False,
            "destination_loss_pct": 0.0,
            "diagnosis": "ICMP_CONTROL_PLANE_RATE_LIMIT_ARTIFACT" if transit_spikes else "PATH_CLEAN_ZERO_LOSS",
            "suspect_hop": None,
        }
    first_sustained = next((x for x in losses if x[2] >= end_loss * 0.5), losses[-1])
    return {
        "real_forwarding_loss": True,
        "destination_loss_pct": end_loss,
        "diagnosis": "SUSTAINED_DATA_PLANE_LOSS_PROPAGATING_TO_DESTINATION",
        "suspect_hop": {"hop": first_sustained[0], "node": first_sustained[1], "loss_pct": first_sustained[2]},
    }


def main() -> None:
    print("Local Python Mock only — no live ThousandEyes agent or Catalyst Center cluster is contacted.")
    wf = analyze_synthetic_http_waterfall(dns_ms=15.0, tcp_connect_ms=25.0, tls_handshake_ms=40.0, http_ttfb_ms=620.0)
    assert wf["dominant_stage"] == "http_ttfb"
    artifact = localize_path_loss([
        {"hop": 1, "node": "gw-edge", "loss_pct": 0.0},
        {"hop": 2, "node": "isp-core-copp", "loss_pct": 35.0},
        {"hop": 3, "node": "saas-vip", "loss_pct": 0.0},
    ])
    real_fault = localize_path_loss([
        {"hop": 1, "node": "gw-edge", "loss_pct": 0.0},
        {"hop": 2, "node": "isp-peering-congestion", "loss_pct": 12.0},
        {"hop": 3, "node": "saas-vip", "loss_pct": 12.0},
    ])
    assert artifact["real_forwarding_loss"] is False and real_fault["real_forwarding_loss"] is True
    print("Synthetic HTTP waterfall:", wf)
    print("Path loss diagnosis:", {"artifact": artifact["diagnosis"], "real": real_fault["suspect_hop"]})


if __name__ == "__main__":
    main()
