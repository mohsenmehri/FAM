#!/usr/bin/env python3
"""
Local Mock Lab — ccde_14 (CCDE Network Security Architecture: Defense in Depth, Zero Trust & EW Firewall Bottleneck)
Audits Defense-in-Depth & Zero Trust controls (NIST SP 800-207) and models the classic East-West
Central Firewall Hairpin Bottleneck vs Distributed Micro-Segmentation + Selective L7 Inspection.
Strict validation rejects non-bool Zero Trust control values (preventing "False" -> True bypasses),
offload percentages outside [0.0, 1.0], and non-positive firewall capacities.
No real NGFW appliances, SIEMs, or production fabrics are connected.
"""

import json
import math


def _require_finite_num(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    try:
        fval = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds IEEE-754 finite float range: {val!r}") from exc
    if not math.isfinite(fval):
        raise ValueError(f"{name} must be a finite number (not bool), got {val!r}")
    return fval


def model_east_west_firewall_bottleneck(
    east_west_gbps: float,
    central_fw_capacity_gbps: float,
    distributed_microseg_offload_pct: float,
) -> dict:
    ew = _require_finite_num(east_west_gbps, "east_west_gbps")
    fw_cap = _require_finite_num(central_fw_capacity_gbps, "central_fw_capacity_gbps")
    offload = _require_finite_num(distributed_microseg_offload_pct, "distributed_microseg_offload_pct")
    if ew < 0:
        raise ValueError(f"east_west_gbps must be non-negative, got {ew}")
    if fw_cap <= 0:
        raise ValueError(f"central_fw_capacity_gbps must be positive, got {fw_cap}")
    if not (0.0 <= offload <= 1.0):
        raise ValueError(f"distributed_microseg_offload_pct must be within [0.0, 1.0], got {offload}")

    central_only_overloaded = ew > fw_cap
    remaining_for_fw = round(ew * (1.0 - offload), 2)
    hybrid_overloaded = remaining_for_fw > fw_cap
    return {
        "total_east_west_gbps": ew,
        "central_ngfw_capacity_gbps": fw_cap,
        "central_hairpin_only_melts_down": central_only_overloaded,
        "after_distributed_l4_microseg_gbps": remaining_for_fw,
        "hybrid_design_healthy": not hybrid_overloaded,
    }


def audit_zero_trust_pillars(controls: dict[str, bool]) -> dict:
    if not isinstance(controls, dict) or not controls:
        raise ValueError("controls must be a non-empty dict of control_name -> strict bool")
    missing = []
    for key, val in controls.items():
        if not isinstance(val, bool):
            raise ValueError(
                f"Zero Trust control '{key}' must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})"
            )
        if not val:
            missing.append(key)
    return {
        "maturity": "ZERO_TRUST_ALIGNED" if not missing else "GAPS_FOUND",
        "missing_controls": missing,
    }


def main() -> None:
    ew_res = model_east_west_firewall_bottleneck(
        east_west_gbps=200.0,
        central_fw_capacity_gbps=40.0,
        distributed_microseg_offload_pct=0.85,
    )
    zt_res = audit_zero_trust_pillars({
        "strong_identity_mfa_8021x": True,
        "device_posture_verification": True,
        "least_privilege_microsegmentation": True,
        "encrypted_traffic_analytics_or_selective_tls": True,
        "symmetric_stateful_firewall_paths": True,
        "continuous_telemetry_siem_ndr": False,
    })
    assert ew_res["central_hairpin_only_melts_down"] is True
    assert ew_res["after_distributed_l4_microseg_gbps"] == 30.0
    assert ew_res["hybrid_design_healthy"] is True
    assert zt_res["maturity"] == "GAPS_FOUND" and zt_res["missing_controls"] == ["continuous_telemetry_siem_ndr"]

    report = {
        "mode": "LOCAL_MOCK_CCDE_SECURITY_ARCH_MODELER",
        "east_west_inspection_tradeoff": ew_res,
        "zero_trust_architecture_audit": zt_res,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
