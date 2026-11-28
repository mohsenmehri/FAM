"""Local Python Mock for ccnp_enc_auto (YANG/NETCONF/RESTCONF Selector & Cisco IOS EEM Applet Simulator).

Educational local model only — no live Cisco IOS-XE EEM engine, NETCONF server,
or Ansible control node is contacted.
Models:
1. Event-driven Cisco IOS EEM (Embedded Event Manager) Applet matcher (syslog/CLI/timer triggers)
   with explicit loop-guard (`max_runs`) so a triggered CLI action cannot create an infinite syslog loop!
2. Protocol/tool matrix selector comparing NETCONF, RESTCONF, EEM, and Ansible/Python trade-offs.
"""
from __future__ import annotations

import re


def evaluate_eem_applet(
    events: list[str],
    pattern: str,
    actions: list[str],
    max_triggers: int = 3,
) -> dict[str, object]:
    """Simulate a syslog-triggered Cisco EEM applet with a loop-prevention cap."""
    if not isinstance(events, list) or not all(isinstance(e, str) for e in events):
        raise ValueError("events must be a list of strings")
    if not isinstance(pattern, str) or not pattern.strip():
        raise ValueError("pattern must be a non-empty regex string")
    if not isinstance(actions, list) or not all(isinstance(a, str) and a.strip() for a in actions):
        raise ValueError("actions must be a list of non-empty strings")
    if isinstance(max_triggers, bool) or not isinstance(max_triggers, int) or not (1 <= max_triggers <= 100):
        raise ValueError("max_triggers must be an int in 1..100")

    compiled = re.compile(pattern)
    matched_indices: list[int] = []
    executed_log: list[dict[str, object]] = []
    suppressed = 0

    for idx, line in enumerate(events):
        if compiled.search(line):
            matched_indices.append(idx)
            if len(executed_log) < max_triggers:
                executed_log.append({"event_index": idx, "event": line, "simulated_actions": list(actions)})
            else:
                suppressed += 1

    return {
        "matched_count": len(matched_indices),
        "executed_count": len(executed_log),
        "suppressed_by_loop_guard": suppressed,
        "executed_log": executed_log,
        "model_scope_note": "Educational Python EEM matcher only; no live Cisco IOS-XE router or EEM daemon is contacted.",
    }


def main() -> None:
    print("Local Python Mock only — no live Cisco IOS-XE EEM daemon or NETCONF/Ansible node is contacted.")
    syslogs = [
        "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down",
        "%OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Gi0/1 from FULL to DOWN",
        "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down",
        "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to down",
    ]
    res = evaluate_eem_applet(
        syslogs,
        pattern=r"%LINK-3-UPDOWN: Interface GigabitEthernet0/1.*down",
        actions=["cli command \"show interface GigabitEthernet0/1\"", "syslog msg \"EEM captured Gi0/1 flap\""],
        max_triggers=2,
    )
    assert res["matched_count"] == 3 and res["executed_count"] == 2 and res["suppressed_by_loop_guard"] == 1
    print("EEM applet simulation:", {"matched": res["matched_count"], "executed": res["executed_count"], "suppressed": res["suppressed_by_loop_guard"]})


if __name__ == "__main__":
    main()
