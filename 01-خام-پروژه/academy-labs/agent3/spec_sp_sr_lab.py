#!/usr/bin/env python3
"""
Local Mock Lab — spec_sp_sr (Service Provider Segment Routing: SR-MPLS, Prefix/Adj-SID, SR-TE & TI-LFA)
Computes SR-MPLS label stacks from SRGB + Prefix-SID / Local Adj-SID, builds an explicit SR-TE
low-latency path without RSVP-TE per-flow state in the core, and verifies TI-LFA backup stacks
including two-connected topology and hardware MSD (Maximum SID Depth) prerequisites.
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
        dest = nodes[-1]
        stack.append({"type": "Prefix-SID", "target": dest, "label": prefix_label(dest)})
    elif mode == "strict_sr_te":
        for src, dst in zip(nodes, nodes[1:]):
            stack.append({"type": "Adj-SID", "hop": f"{src}->{dst}", "label": ADJ_SIDS[(src, dst)]})
    else:
        # Hybrid: steer to first intermediate node via Prefix-SID, force explicit Adj-SID hop, then destination Prefix-SID
        mid_src, mid_dst, dest = nodes[1], nodes[2], nodes[-1]
        stack.append({"type": "Prefix-SID", "target": mid_src, "label": prefix_label(mid_src)})
        stack.append({"type": "Adj-SID", "hop": f"{mid_src}->{mid_dst}", "label": ADJ_SIDS[(mid_src, mid_dst)]})
        stack.append({"type": "Prefix-SID", "target": dest, "label": prefix_label(dest)})
    return stack


def compute_ti_lfa_backup(
    failed_link: tuple[str, str],
    destination: str,
    alternate_hop: tuple[str, str] | None,
    hardware_msd: int = 4,
) -> dict:
    if alternate_hop is None:
        return {
            "failed_link": f"{failed_link[0]}->{failed_link[1]}",
            "destination": destination,
            "protected": False,
            "reason": "Cut-edge / singly-homed topology: TI-LFA requires a 2-connected alternate path",
        }
    repair_list = [
        {"type": "Adj-SID (Q-Space/PQ)", "hop": f"{alternate_hop[0]}->{alternate_hop[1]}", "label": ADJ_SIDS[alternate_hop]},
        {"type": "Prefix-SID", "target": destination, "label": prefix_label(destination)},
    ]
    msd_ok = len(repair_list) <= hardware_msd
    return {
        "failed_link": f"{failed_link[0]}->{failed_link[1]}",
        "destination": destination,
        "repair_list_pushed": repair_list,
        "repair_stack_depth": len(repair_list),
        "hardware_msd": hardware_msd,
        "protected": msd_ok,
        "note": (
            "Pre-installed in FIB; typical <50ms FRR target (subject to fast link-down/BFD detection & MSD)"
            if msd_ok
            else f"Blocked: repair stack depth ({len(repair_list)}) exceeds hardware MSD ({hardware_msd})"
        ),
        "core_per_flow_state_required": 0,
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_SR_MPLS_HARDWARE",
        "srgb_range": f"{SRGB_START}-{SRGB_END}",
        "igp_shortest_path_stack_pe1_to_pe2": build_sr_te_stack(["PE1", "P1", "P2", "PE2"], mode="loose_prefix_sid"),
        "sr_te_low_latency_strict_stack": build_sr_te_stack(["PE1", "P1", "P3", "PE2"], mode="strict_sr_te"),
        "sr_te_hybrid_compressed_stack": build_sr_te_stack(["PE1", "P1", "P3", "PE2"], mode="hybrid"),
        "ti_lfa_backup_on_p1_p2_cut": compute_ti_lfa_backup(("P1", "P2"), "PE2", ("P1", "P3"), hardware_msd=4),
        "ti_lfa_blocked_by_low_msd": compute_ti_lfa_backup(("P1", "P2"), "PE2", ("P1", "P3"), hardware_msd=1),
        "ti_lfa_singly_homed_cut_edge": compute_ti_lfa_backup(("PE1", "P1"), "PE2", None, hardware_msd=4),
    }
    assert report["ti_lfa_backup_on_p1_p2_cut"]["protected"] is True
    assert report["ti_lfa_blocked_by_low_msd"]["protected"] is False
    assert report["ti_lfa_singly_homed_cut_edge"]["protected"] is False
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
