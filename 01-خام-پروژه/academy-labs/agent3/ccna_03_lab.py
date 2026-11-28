"""Local Python Mock for ccna_03 (Static/Floating Static Routing & OSPF Single-Area).

No real Cisco router or live OSPF process is contacted.
Models:
1. OSPF Cost calculation with configurable reference-bandwidth (default 100 Mbps vs 10G/100G).
2. OSPF Single-Area adjacency checks (Area, Hello/Dead, Subnet, MTU, Router-ID, Auth, Passive,
   Network Type, DROTHER 2WAY normalcy, and local-only Process ID).
3. Floating Static Route selection when primary dynamic/static route is active vs withdrawn.
"""
from __future__ import annotations

import ipaddress
import math

VALID_OSPF_NET_TYPES = frozenset({"broadcast", "point_to_point"})


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool, got {val!r} ({type(val).__name__})")
    return val


def _require_pos_finite(val: object, name: str) -> float:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a positive finite number (not bool), got {val!r}")
    try:
        f = float(val)
    except OverflowError as exc:
        raise ValueError(f"{name} overflowed IEEE-754 float: {val!r}") from exc
    if not math.isfinite(f) or f <= 0:
        raise ValueError(f"{name} must be positive and finite, got {val!r}")
    return f


def ospf_interface_cost(link_bw_mbps: float, ref_bw_mbps: float = 100.0) -> int:
    """Compute Cisco-style OSPF cost = max(1, int(ref_bw_mbps / link_bw_mbps))."""
    bw = _require_pos_finite(link_bw_mbps, "link_bw_mbps")
    ref = _require_pos_finite(ref_bw_mbps, "ref_bw_mbps")
    ratio = ref / bw
    if not math.isfinite(ratio):
        raise ValueError("OSPF cost calculation overflowed")
    return max(1, int(ratio))


def check_ospf_adjacency(r1: dict[str, object], r2: dict[str, object]) -> dict[str, object]:
    """Evaluate OSPF Single-Area neighbor state between two interfaces."""
    for label, r in (("r1", r1), ("r2", r2)):
        if not isinstance(r, dict):
            raise ValueError(f"{label} must be a dict")
        ipaddress.IPv4Address(str(r["router_id"]))
        ipaddress.IPv4Interface(str(r["interface_ip"]))
        if r.get("network_type", "broadcast") not in VALID_OSPF_NET_TYPES:
            raise ValueError(f"{label} network_type must be in {sorted(VALID_OSPF_NET_TYPES)}")
        _require_bool(r.get("passive", False), f"{label}.passive")
        for fld in ("area", "hello_sec", "dead_sec", "mtu", "process_id", "priority"):
            v = r[fld]
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                raise ValueError(f"{label}.{fld} must be a non-negative int (not bool)")

    blockers: list[str] = []
    warnings: list[str] = []

    if r1["passive"] or r2["passive"]:
        blockers.append("PASSIVE_INTERFACE: no OSPF Hello packets exchanged on passive interface")
    if r1["router_id"] == r2["router_id"]:
        blockers.append("DUPLICATE_ROUTER_ID: neighbor Router IDs must be unique")
    if r1["area"] != r2["area"]:
        blockers.append(f"AREA_MISMATCH: R1 area {r1['area']} vs R2 area {r2['area']}")
    if r1["hello_sec"] != r2["hello_sec"] or r1["dead_sec"] != r2["dead_sec"]:
        blockers.append("TIMER_MISMATCH: Hello and Dead intervals must match")
    if r1.get("auth_key", "") != r2.get("auth_key", ""):
        blockers.append("AUTH_MISMATCH: OSPF authentication credentials differ")

    net1 = ipaddress.IPv4Interface(str(r1["interface_ip"])).network
    net2 = ipaddress.IPv4Interface(str(r2["interface_ip"])).network
    if net1 != net2:
        blockers.append(f"SUBNET_MISMATCH: {net1} vs {net2}")

    # Process ID is locally significant — mismatch does NOT prevent adjacency!
    if r1["process_id"] != r2["process_id"]:
        warnings.append("LOCAL_PROCESS_ID_DIFFERS_OK: Process ID is locally significant only")

    if blockers:
        return {"state": "DOWN", "full_or_healthy": False, "blockers": blockers, "warnings": warnings}

    if r1["mtu"] != r2["mtu"]:
        return {
            "state": "EXSTART_STUCK",
            "full_or_healthy": False,
            "blockers": [f"MTU_MISMATCH: R1={r1['mtu']} vs R2={r2['mtu']}"],
            "warnings": warnings,
        }

    nt1 = r1.get("network_type", "broadcast")
    nt2 = r2.get("network_type", "broadcast")
    if nt1 != nt2:
        warnings.append("NETWORK_TYPE_MISMATCH_SPF_RISK: adjacency may reach FULL if timers match, but SPF route installation breaks (Type 1 vs Type 2 LSA)")

    if nt1 == "broadcast" and nt2 == "broadcast" and r1["priority"] == 0 and r2["priority"] == 0:
        return {
            "state": "2WAY_DROTHER",
            "full_or_healthy": True,
            "blockers": [],
            "warnings": warnings + ["DROTHER_2WAY_NORMAL: two DROTHER peers remain in 2WAY on broadcast links"],
        }

    return {
        "state": "FULL",
        "full_or_healthy": nt1 == nt2,
        "blockers": [] if nt1 == nt2 else ["SPF_BROKEN_BY_NETWORK_TYPE_MISMATCH"],
        "warnings": warnings,
    }


def select_floating_static(
    primary_up: bool,
    primary_ad: int = 110,
    floating_ad: int = 120,
) -> dict[str, object]:
    """Model floating static failover (requires floating_ad > primary_ad)."""
    up = _require_bool(primary_up, "primary_up")
    for name, v in (("primary_ad", primary_ad), ("floating_ad", floating_ad)):
        if isinstance(v, bool) or not isinstance(v, int) or not (1 <= v <= 254):
            raise ValueError(f"{name} must be an int in 1..254, got {v!r}")
    if floating_ad <= primary_ad:
        raise ValueError("floating_ad must be strictly greater than primary_ad to act as backup")
    return {
        "active_path": "primary" if up else "floating_static_backup",
        "installed_ad": primary_ad if up else floating_ad,
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco router or OSPF network is contacted.")
    # 1. Reference bandwidth distinction
    assert ospf_interface_cost(1000, 100) == 1 and ospf_interface_cost(10000, 100) == 1
    assert ospf_interface_cost(1000, 100000) == 100 and ospf_interface_cost(10000, 100000) == 10
    print("Cost @ ref=100G (1G vs 10G):", ospf_interface_cost(1000, 100000), ospf_interface_cost(10000, 100000))

    # 2. Healthy OSPF adjacency despite DIFFERENT Process IDs (1 vs 99)
    r1 = {"router_id": "1.1.1.1", "interface_ip": "10.10.0.1/30", "area": 0, "hello_sec": 10, "dead_sec": 40, "mtu": 1500, "process_id": 1, "priority": 1, "passive": False, "network_type": "broadcast"}
    r2 = {"router_id": "2.2.2.2", "interface_ip": "10.10.0.2/30", "area": 0, "hello_sec": 10, "dead_sec": 40, "mtu": 1500, "process_id": 99, "priority": 1, "passive": False, "network_type": "broadcast"}
    adj_ok = check_ospf_adjacency(r1, r2)
    assert adj_ok["state"] == "FULL" and adj_ok["full_or_healthy"] is True

    # 3. MTU mismatch -> EXSTART_STUCK
    adj_mtu = check_ospf_adjacency(r1, {**r2, "mtu": 1400})
    assert adj_mtu["state"] == "EXSTART_STUCK"
    print("Adjacency OK (different PIDs):", adj_ok["state"], "| MTU mismatch:", adj_mtu["state"])

    # 4. Floating static failover
    assert select_floating_static(True)["active_path"] == "primary"
    assert select_floating_static(False)["active_path"] == "floating_static_backup"
    print("Floating static failover verified.")


if __name__ == "__main__":
    main()
