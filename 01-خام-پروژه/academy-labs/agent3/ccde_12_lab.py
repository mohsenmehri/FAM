#!/usr/bin/env python3
"""
Local Mock Lab — ccde_12 (CCDE Scalability Architecture: 4 Scaling Walls & Scale-Out vs Scale-Up Modeler)
Models how flat topology breaks the 4 CCDE scaling walls (Control Plane O(N^2) sessions, FIB/TCAM,
Switch Radix, Operational Complexity) with strict input validation on router/RR/site counts.
No real production network devices are connected.
"""

import json


def _require_pos_int(val: object, name: str, minimum: int = 1) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or val < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}, got {val!r}")
    return val


def ibgp_full_mesh_sessions(routers: int) -> int:
    n = _require_pos_int(routers, "routers", minimum=1)
    return n * (n - 1) // 2


def ibgp_rr_sessions(routers: int, route_reflectors: int = 2) -> int:
    n = _require_pos_int(routers, "routers", minimum=1)
    rr = _require_pos_int(route_reflectors, "route_reflectors", minimum=1)
    if rr > n:
        raise ValueError(f"route_reflectors ({rr}) cannot exceed total routers ({n})")
    clients = n - rr
    return clients * rr + (rr * (rr - 1) // 2)


def evaluate_four_scaling_walls(routers: int, routes_per_site: int, sites: int, summarized: bool) -> dict:
    n = _require_pos_int(routers, "routers", minimum=2)
    rps = _require_pos_int(routes_per_site, "routes_per_site", minimum=1)
    st = _require_pos_int(sites, "sites", minimum=1)
    core_rib_entries = st if summarized else st * rps
    fm = ibgp_full_mesh_sessions(n)
    rr_cnt = min(2, n)
    rr_sess = ibgp_rr_sessions(n, rr_cnt)
    return {
        "sites": st,
        "summarized_at_boundaries": summarized,
        "core_rib_entries": core_rib_entries,
        "ibgp_sessions_flat_full_mesh": fm,
        "ibgp_sessions_with_rr": rr_sess,
        "session_reduction_ratio": round(fm / max(rr_sess, 1), 1),
    }


def main() -> None:
    flat = evaluate_four_scaling_walls(routers=200, routes_per_site=25, sites=200, summarized=False)
    hier = evaluate_four_scaling_walls(routers=200, routes_per_site=25, sites=200, summarized=True)
    assert flat["core_rib_entries"] == 5000 and hier["core_rib_entries"] == 200
    assert flat["ibgp_sessions_flat_full_mesh"] == 19900
    assert hier["ibgp_sessions_with_rr"] == 397

    report = {
        "mode": "LOCAL_MOCK_CCDE_SCALABILITY_MODELER",
        "flat_vs_hierarchical_200_routers": {
            "flat_unsummarized": flat,
            "hierarchical_summarized_rr": hier,
        },
        "scale_up_vs_scale_out": {
            "vertical_scale_up": "Bigger single chassis -> hits hard physical/cost ceiling & huge blast radius",
            "horizontal_scale_out": "Add identical modular pods/spines/leafs -> linear growth + bounded blast radius",
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
