#!/usr/bin/env python3
"""
Local Mock Lab — ccde_14 (CCDE Network Security Architecture: Defense in Depth, Zero Trust & EW Firewall Bottleneck)
Audits Defense-in-Depth & Zero Trust controls (NIST SP 800-207) and models the classic East-West
Central Firewall Hairpin Bottleneck vs Distributed Micro-Segmentation + Selective L7 Inspection.
No real NGFW appliances, SIEMs, or production fabrics are connected.
"""

import json


def model_east_west_firewall_bottleneck(east_west_gbps: float, central_fw_capacity_gbps: float, distributed_microseg_offload_pct: float) -> dict:
    central_only_overloaded = east_west_gbps > central_fw_capacity_gbps
    remaining_for_fw = round(east_west_gbps * (1.0 - distributed_microseg_offload_pct), 2)
    hybrid_overloaded = remaining_for_fw > central_fw_capacity_gbps
    return {
        "total_east_west_gbps": east_west_gbps,
        "central_ngfw_capacity_gbps": central_fw_capacity_gbps,
        "central_hairpin_only_melts_down": central_only_overloaded,
        "after_distributed_l4_microseg_gbps": remaining_for_fw,
        "hybrid_design_healthy": not hybrid_overloaded,
    }


def audit_zero_trust_pillars(controls: dict[str, bool]) -> dict:
    missing = [k for k, v in controls.items() if not v]
    return {"maturity": "ZERO_TRUST_ALIGNED" if not missing else "GAPS_FOUND", "missing_controls": missing}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_CCDE_SECURITY_ARCH_MODELER",
        "east_west_inspection_tradeoff": model_east_west_firewall_bottleneck(
            east_west_gbps=200.0,
            central_fw_capacity_gbps=40.0,
            distributed_microseg_offload_pct=0.85,
        ),
        "zero_trust_architecture_audit": audit_zero_trust_pillars({
            "strong_identity_mfa_8021x": True,
            "device_posture_verification": True,
            "least_privilege_microsegmentation": True,
            "encrypted_traffic_analytics_or_selective_tls": True,
            "symmetric_stateful_firewall_paths": True,
            "continuous_telemetry_siem_ndr": False,
        }),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
