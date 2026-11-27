#!/usr/bin/env python3
"""
Local Mock Lab — ccde_04 (CCDE Large Scale Network Design & AI/ML Fabric: 5-Stage Clos & RoCEv2 ECN/PFC)
Calculates 3-Stage vs 5-Stage Clos (Super-Spine/Pod) maximum server radix and oversubscription with strict
boundary validation (valid radix, positive oversubscription, non-zero uplinks/servers, pods <= switch_radix),
and audits AI/ML GPU cluster fabric readiness using an explicit adaptive load-balancing allowlist.
No real hyperscale switch fabric or NVIDIA GPU cluster is connected.
"""

import json

ADAPTIVE_AI_LB_MODES = frozenset({
    "adaptive_dlb_packet_spraying",
    "adaptive_routing",
    "packet_spraying",
})


def clos_3stage_max_servers(switch_radix: int, oversubscription: float = 3.0) -> dict:
    if isinstance(switch_radix, bool) or not isinstance(switch_radix, int) or switch_radix < 4 or switch_radix % 2 != 0:
        raise ValueError(f"switch_radix must be an even integer >= 4, got {switch_radix!r}")
    if isinstance(oversubscription, bool) or not isinstance(oversubscription, (int, float)) or oversubscription <= 0:
        raise ValueError(f"oversubscription must be > 0, got {oversubscription!r}")
    uplinks_per_leaf = int(round(switch_radix / (1.0 + oversubscription)))
    servers_per_leaf = switch_radix - uplinks_per_leaf
    if uplinks_per_leaf < 1 or servers_per_leaf < 1:
        raise ValueError(
            f"switch_radix={switch_radix} cannot realize oversubscription={oversubscription} "
            f"(computed uplinks={uplinks_per_leaf}, servers={servers_per_leaf})"
        )
    max_leafs = switch_radix
    return {
        "topology": "3-Stage Clos (Leaf-Spine)",
        "switch_radix": switch_radix,
        "oversubscription_ratio": f"{round(servers_per_leaf / uplinks_per_leaf, 2)}:1",
        "max_leafs": max_leafs,
        "max_spines": uplinks_per_leaf,
        "max_server_ports": max_leafs * servers_per_leaf,
    }


def clos_5stage_max_servers(switch_radix: int, pods: int, oversubscription: float = 1.0) -> dict:
    if isinstance(switch_radix, bool) or not isinstance(switch_radix, int) or switch_radix < 4 or switch_radix % 2 != 0:
        raise ValueError(f"switch_radix must be an even integer >= 4, got {switch_radix!r}")
    if isinstance(pods, bool) or not isinstance(pods, int) or not (1 <= pods <= switch_radix):
        raise ValueError(f"pods must be an integer in 1..{switch_radix} (bounded by Super-Spine radix), got {pods!r}")
    if isinstance(oversubscription, bool) or not isinstance(oversubscription, (int, float)) or oversubscription <= 0:
        raise ValueError(f"oversubscription must be > 0, got {oversubscription!r}")
    leafs_per_pod = switch_radix // 2
    uplinks_per_leaf = int(round(switch_radix / (1.0 + oversubscription)))
    servers_per_leaf = switch_radix - uplinks_per_leaf
    if uplinks_per_leaf < 1 or servers_per_leaf < 1:
        raise ValueError(f"Invalid port split for switch_radix={switch_radix}, oversubscription={oversubscription}")
    total_leafs = leafs_per_pod * pods
    return {
        "topology": "5-Stage Clos (Leaf -> Pod-Spine -> Super-Spine)",
        "switch_radix": switch_radix,
        "pods": pods,
        "oversubscription_ratio": f"{round(servers_per_leaf / uplinks_per_leaf, 2)}:1",
        "total_leafs": total_leafs,
        "total_server_ports": total_leafs * servers_per_leaf,
    }


def audit_ai_ml_fabric(cfg: dict) -> dict:
    oversub = cfg["oversubscription"]
    if isinstance(oversub, bool) or not isinstance(oversub, (int, float)) or oversub <= 0:
        raise ValueError(f"oversubscription must be > 0, got {oversub!r}")
    gaps = []
    if oversub > 1.0:
        gaps.append("AI GPU all-reduce collective typically targets 1:1 non-blocking rail-optimized fabric")
    if not (cfg["ecn_enabled"] and cfg["pfc_enabled"]):
        gaps.append("RoCEv2 lossless profile expects ECN (proactive marking) + PFC (last-resort pause) tuned together")
    lb = cfg.get("load_balancing", "")
    if lb not in ADAPTIVE_AI_LB_MODES:
        gaps.append(
            f"Load balancing '{lb}' is not in adaptive AI allowlist {sorted(ADAPTIVE_AI_LB_MODES)} "
            "(risk of hash polarization on elephant AI flows)"
        )
    return {"profile": cfg["name"], "ai_fabric_ready": len(gaps) == 0, "gaps": gaps}


def main() -> None:
    c3 = clos_3stage_max_servers(64, 3.0)
    c5 = clos_5stage_max_servers(64, 8, 1.0)
    bad_web = audit_ai_ml_fabric({"name": "Standard_Web_DC", "oversubscription": 3.0, "ecn_enabled": False, "pfc_enabled": False, "load_balancing": "static_5tuple_ecmp"})
    good_gpu = audit_ai_ml_fabric({"name": "GPU_AI_Cluster_Fabric", "oversubscription": 1.0, "ecn_enabled": True, "pfc_enabled": True, "load_balancing": "adaptive_dlb_packet_spraying"})
    bad_lb = audit_ai_ml_fabric({"name": "Unknown_LB_Fabric", "oversubscription": 1.0, "ecn_enabled": True, "pfc_enabled": True, "load_balancing": "unknown_lb_mode"})

    assert c3["max_server_ports"] == 3072
    assert c5["total_server_ports"] == 8192
    assert bad_web["ai_fabric_ready"] is False and len(bad_web["gaps"]) == 3
    assert good_gpu["ai_fabric_ready"] is True
    assert bad_lb["ai_fabric_ready"] is False

    report = {
        "mode": "LOCAL_MOCK_CCDE_LARGESCALE_AI_MODELER",
        "clos_scaling_64port_switches": {
            "three_stage_3to1": c3,
            "five_stage_8pods_nonblocking": c5,
        },
        "ai_fabric_audits": [bad_web, good_gpu, bad_lb],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
