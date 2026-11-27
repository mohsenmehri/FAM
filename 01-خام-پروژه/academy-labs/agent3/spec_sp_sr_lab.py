#!/usr/bin/env python3
"""
Local Mock Lab — spec_sp_sr (Service Provider Segment Routing: SR-MPLS, Prefix/Adj-SID, SR-TE & TI-LFA)
Computes SR-MPLS label stacks from SRGB + Prefix-SID / Local Adj-SID, builds an explicit SR-TE
low-latency path without RSVP-TE per-flow state in the core, and computes a TI-LFA <50ms backup stack.
No real SR-MPLS / IOS-XR router is connected.
"""

import json


SRGB_START = 16000
SRGB_END = 23999

PREFIX_SIDS = {
    "PE1": 1,
    "P1": 11,
    "P2": 12,
    "P3": 13,
    "PE2": 2,
}

ADJ_SIDS = {
    ("PE1", "P1"): 24001,
    ("P1", "P2"): 24012,
    ("P2", "PE2"): 24022,
    ("P1", "P3"): 24013,
    ("P3", "PE2"): 24032,
}


def prefix_label(node: str) -> int:
    sid = SRGB_START + PREFIX_SIDS[node]
    assert SRGB_START <= sid <= SRGB_END
    return sid


def build_sr_te_stack(nodes: list[str], mode: str = "hybrid") -> list[dict]:
    stack = []
    if mode == "loose_prefix_sid":
        # Headend only pushes destination Prefix-SID; core follows IGP shortest path
        dest = nodes[-1]
        stack.append({"type": "Prefix-SID", "target": dest, "label": prefix_label(dest)})
    elif mode == "strict_sr_te":
        # Headend enforces explicit low-latency hops using Adj-SIDs (zero RSVP state in core!)
        for src, dst in zip(nodes, nodes[1:]):
            stack.append({"type": "Adj-SID", "hop": f"{src}->{dst}", "label": ADJ_SIDS[(src, dst)]})
    else:
        # Hybrid: steer via P1->P3 Adj-SID, then IGP shortest path to PE2 Prefix-SID
        stack.append({"type": "Prefix-SID", "target": "P1", "label": prefix_label("P1")})
        stack.append({"type": "Adj-SID", "hop": "P1->P3", "label": ADJ_SIDS[("P1", "P3")]})
        stack.append({"type": "Prefix-SID", "target": "PE2", "label": prefix_label("PE2")})
    return stack


def compute_ti_lfa_backup(failed_link: tuple[str, str], destination: str) -> dict:
    # Pre-computed post-convergence backup stack on P1 if P1->P2 fails
    return {
        "failed_link": f"{failed_link[0]}->{failed_link[1]}",
        "destination": destination,
        "repair_list_pushed_by_p1": [
            {"type": "Adj-SID (Q-Space/PQ)", "hop": "P1->P3", "label": ADJ_SIDS[("P1", "P3")]},
            {"type": "Prefix-SID", "target": destination, "label": prefix_label(destination)},
        ],
        "expected_switchover_ms": "<50ms (pre-installed in FIB, topology-independent)",
        "core_per_flow_state_required": 0,
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_SR_MPLS_HARDWARE",
        "srgb_range": f"{SRGB_START}-{SRGB_END}",
        "igp_shortest_path_stack_pe1_to_pe2": build_sr_te_stack(["PE1", "P1", "P2", "PE2"], mode="loose_prefix_sid"),
        "sr_te_low_latency_strict_stack": build_sr_te_stack(["PE1", "P1", "P3", "PE2"], mode="strict_sr_te"),
        "sr_te_hybrid_compressed_stack": build_sr_te_stack(["PE1", "P1", "P3", "PE2"], mode="hybrid"),
        "ti_lfa_backup_on_p1_p2_cut": compute_ti_lfa_backup(("P1", "P2"), "PE2"),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
