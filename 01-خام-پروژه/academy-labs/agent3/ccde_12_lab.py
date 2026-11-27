#!/usr/bin/env python3
"""
Local Mock Lab — ccde_12 (CCDE Scalability Architecture: 4 Scaling Walls & Scale-Out vs Scale-Up Modeler)
Models how flat topology breaks the 4 CCDE scaling walls (Control Plane O(N^2) sessions, FIB/TCAM,
Switch Radix, Operational Complexity) and shows how Hierarchy, Summarization, and Horizontal Scale-Out cure them.
No real production network devices are connected.
"""

import json


def ibgp_full_mesh_sessions(routers: int) -> int:
    return routers * (routers - 1) // 2


def ibgp_rr_sessions(routers: int, route_reflectors: int = 2) -> int:
    clients = max(routers - route_reflectors, 0)
    return clients * route_reflectors + (route_reflectors * (route_reflectors - 1) // 2)


def evaluate_four_scaling_walls(routers: int, routes_per_site: int, sites: int, summarized: bool) -> dict:
    core_rib_entries = sites if summarized else sites * routes_per_site
    return {
        "sites": sites,
        "summarized_at_boundaries": summarized,
        "core_rib_entries": core_rib_entries,
        "ibgp_sessions_flat_full_mesh": ibgp_full_mesh_sessions(routers),
        "ibgp_sessions_with_2_rr": ibgp_rr_sessions(routers, 2),
        "session_reduction_ratio": round(ibgp_full_mesh_sessions(routers) / max(ibgp_rr_sessions(routers, 2), 1), 1),
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_SCALABILITY_MODELER",
        "flat_vs_hierarchical_200_routers": {
            "flat_unsummarized": evaluate_four_scaling_walls(routers=200, routes_per_site=25, sites=200, summarized=False),
            "hierarchical_summarized_rr": evaluate_four_scaling_walls(routers=200, routes_per_site=25, sites=200, summarized=True),
        },
        "scale_up_vs_scale_out": {
            "vertical_scale_up": "Bigger single chassis -> hits hard physical/cost ceiling & huge blast radius",
            "horizontal_scale_out": "Add identical modular pods/spines/leafs -> linear growth + bounded blast radius",
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
