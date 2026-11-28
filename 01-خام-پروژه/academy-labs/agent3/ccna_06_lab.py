"""Local Python 3 stdlib mock lab for ccna_06 (SDN Planes, Catalyst Center, REST CRUD & JSON/YAML/Ansible).

Boundary: Pure in-memory simulation using Python stdlib only (json).
No real Cisco Catalyst Center, RESTCONF endpoint, HTTP server, or Ansible controller is executed.
"""
from __future__ import annotations

import json


def _require_bool(val: object, name: str) -> bool:
    if type(val) is not bool:
        raise ValueError(f"{name} must be a strict bool, got {type(val).__name__}")
    return val


def _require_non_empty_str(val: object, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return val.strip()


def classify_sdn_interface(direction: str, protocol: str) -> dict[str, object]:
    """Classify Northbound API (app <-> controller) vs Southbound API (controller <-> device)."""
    d = _require_non_empty_str(direction, "direction").lower()
    p = _require_non_empty_str(protocol, "protocol")
    if d == "northbound":
        return {
            "direction": "Northbound API (NBI)",
            "peers": "Applications / Scripts / ITSM <-> SDN Controller",
            "protocol": p,
            "typical_format": "REST over HTTPS (JSON)",
        }
    if d == "southbound":
        return {
            "direction": "Southbound API (SBI)",
            "peers": "SDN Controller <-> Network Devices",
            "protocol": p,
            "typical_examples": ["NETCONF", "RESTCONF", "OpenFlow", "OpFlex", "SSH/SNMP"],
        }
    raise ValueError("direction must be 'northbound' or 'southbound'")


def simulate_rest_crud(
    store: dict[str, dict[str, object]],
    method: str,
    resource_id: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    """Simulate REST API CRUD semantics (POST/GET/PUT/PATCH/DELETE) with standard HTTP status codes."""
    m = _require_non_empty_str(method, "method").upper()
    rid = _require_non_empty_str(resource_id, "resource_id")

    if m == "POST":
        if payload is None:
            return {"status": 400, "error": "Missing JSON payload"}
        if rid in store:
            return {"status": 409, "error": f"Resource {rid} already exists"}
        store[rid] = dict(payload)
        return {"status": 201, "resource_id": rid, "body": store[rid]}
    if m == "GET":
        if rid not in store:
            return {"status": 404, "error": f"Resource {rid} not found"}
        return {"status": 200, "resource_id": rid, "body": store[rid]}
    if m == "PUT":
        if payload is None:
            return {"status": 400, "error": "Missing JSON payload"}
        existed = rid in store
        store[rid] = dict(payload)
        return {"status": 200 if existed else 201, "resource_id": rid, "body": store[rid]}
    if m == "PATCH":
        if rid not in store:
            return {"status": 404, "error": f"Resource {rid} not found"}
        if payload is None:
            return {"status": 400, "error": "Missing JSON payload"}
        store[rid].update(payload)
        return {"status": 200, "resource_id": rid, "body": store[rid]}
    if m == "DELETE":
        if rid not in store:
            return {"status": 404, "error": f"Resource {rid} not found"}
        del store[rid]
        return {"status": 204, "resource_id": rid}
    raise ValueError(f"Unsupported HTTP method: {method}")


def compare_config_mgmt_tool(tool: str) -> dict[str, object]:
    """Compare Ansible, Puppet, and Chef architecture for CCNA automation."""
    t = _require_non_empty_str(tool, "tool").lower()
    tools = {
        "ansible": {"architecture": "Agentless", "model": "Push (SSH/NETCONF/REST)", "language": "YAML Playbooks (Python)"},
        "puppet": {"architecture": "Agent-based (typically)", "model": "Pull (TCP 8140)", "language": "Ruby-based DSL Manifests"},
        "chef": {"architecture": "Agent-based", "model": "Pull", "language": "Ruby Recipes/Cookbooks"},
    }
    if t not in tools:
        raise ValueError(f"Unsupported tool: {tool}")
    return {"tool": t, **tools[t]}


def validate_json_and_yaml_indent(json_text: str, yaml_lines: list[str], allow_tabs: bool = False) -> dict[str, object]:
    """Verify strict JSON parsing and detect illegal Tab indentation in YAML."""
    _require_bool(allow_tabs, "allow_tabs")
    parsed = json.loads(json_text)
    tab_lines = [i + 1 for i, line in enumerate(yaml_lines) if "\t" in line]
    yaml_valid = len(tab_lines) == 0 or allow_tabs
    return {"json_keys": sorted(parsed.keys()) if isinstance(parsed, dict) else [], "yaml_valid": yaml_valid, "tab_lines": tab_lines}


def main() -> None:
    nbi = classify_sdn_interface("northbound", "REST/HTTPS (JSON)")
    sbi = classify_sdn_interface("southbound", "NETCONF/RESTCONF")
    assert "Northbound" in str(nbi["direction"]) and "Southbound" in str(sbi["direction"])

    store: dict[str, dict[str, object]] = {}
    c_res = simulate_rest_crud(store, "POST", "vlan-10", {"vlan_id": 10, "name": "FINANCE"})
    p_res = simulate_rest_crud(store, "PATCH", "vlan-10", {"name": "FINANCE_CORE"})
    d_res = simulate_rest_crud(store, "DELETE", "vlan-10")
    g_404 = simulate_rest_crud(store, "GET", "vlan-10")
    assert c_res["status"] == 201 and p_res["body"]["name"] == "FINANCE_CORE"
    assert d_res["status"] == 204 and g_404["status"] == 404

    ans = compare_config_mgmt_tool("ansible")
    assert ans["architecture"] == "Agentless"

    fmt = validate_json_and_yaml_indent('{"hostname": "SW1", "vlans": [10, 20]}', ["vlans:", "\t- 10"])
    assert fmt["yaml_valid"] is False and fmt["tab_lines"] == [2]

    print("SDN APIs:", nbi, sbi)
    print("REST CRUD:", c_res, p_res, d_res, g_404)
    print("Ansible Profile:", ans)
    print("JSON/YAML Format Check:", fmt)


if __name__ == "__main__":
    main()
