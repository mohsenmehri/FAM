#!/usr/bin/env python3
"""
Local Mock Lab — ccde_04 (CCDE Large Scale Network Design & AI/ML Fabric: 5-Stage Clos & RoCEv2 ECN/PFC)
Calculates 3-Stage vs 5-Stage Clos (Super-Spine/Pod) maximum server radix and oversubscription,
and audits AI/ML GPU cluster fabric readiness (RoCEv2 lossless PFC/ECN, 1:1 non-blocking, elephant flow spraying).
No real hyperscale switch fabric or NVIDIA GPU cluster is connected.
"""

import json


def clos_3stage_max_servers(switch_radix: int, oversubscription: float = 3.0) -> dict:
    # Each Spine has `switch_radix` ports -> max `switch_radix` Leafs.
    # On each Leaf, split ports between uplinks (u) and servers (s) such that s / u = oversubscription
    uplinks_per_leaf = int(round(switch_radix / (1.0 + oversubscription)))
    servers_per_leaf = switch_radix - uplinks_per_leaf
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
    # In a 5-Stage Clos (Leaf -> Pod-Spine -> Super-Spine), each Pod-Spine splits ports down/up
    leafs_per_pod = switch_radix // 2
    uplinks_per_leaf = int(round(switch_radix / (1.0 + oversubscription)))
    servers_per_leaf = switch_radix - uplinks_per_leaf
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
    gaps = []
    if cfg["oversubscription"] > 1.0:
        gaps.append("AI GPU all-reduce collective needs 1:1 non-blocking rail-optimized fabric")
    if not (cfg["ecn_enabled"] and cfg["pfc_enabled"]):
        gaps.append("RoCEv2 requires ECN (proactive marking) + PFC (last-resort lossless pause) tuned together")
    if cfg["load_balancing"] == "static_5tuple_ecmp":
        gaps.append("Static 5-tuple ECMP suffers hash polarization on elephant AI flows — use DLB / Packet Spraying")
    return {"profile": cfg["name"], "ai_fabric_ready": len(gaps) == 0, "gaps": gaps}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_LARGESCALE_AI_MODELER",
        "clos_scaling_64port_switches": {
            "three_stage_3to1": clos_3stage_max_servers(64, 3.0),
            "five_stage_8pods_nonblocking": clos_5stage_max_servers(64, 8, 1.0),
        },
        "ai_fabric_audits": [
            audit_ai_ml_fabric({"name": "Standard_Web_DC", "oversubscription": 3.0, "ecn_enabled": False, "pfc_enabled": False, "load_balancing": "static_5tuple_ecmp"}),
            audit_ai_ml_fabric({"name": "GPU_AI_Cluster_Fabric", "oversubscription": 1.0, "ecn_enabled": True, "pfc_enabled": True, "load_balancing": "adaptive_dlb_packet_spraying"}),
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
