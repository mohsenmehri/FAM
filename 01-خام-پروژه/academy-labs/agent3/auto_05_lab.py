"""Local Data-Serialization Lab for auto_05 (JSON RFC 8259, YAML 1.1/1.2 Traps & XML Namespaces).

Runs locally in Python 3 standard library; no external network device or NETCONF server is run.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

SAMPLE_JSON = '{"hostname": "edge-01", "vlans": [10, 20], "active": true}'
INVALID_JSON_RFC8259 = "{'hostname': 'edge-01', 'active': True,}"

SAMPLE_NETCONF_XML = """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>GigabitEthernet1</name>
    <enabled>true</enabled>
  </interface>
</interfaces>
""".strip()

YAML_11_BOOL_LITERALS = frozenset({"yes", "no", "on", "off", "true", "false", "y", "n"})


def parse_json_strict(raw_json: str) -> dict[str, object]:
    """Parse strict RFC 8259 JSON (double quotes, lowercase true/false, no trailing commas)."""
    return json.loads(raw_json)


def check_invalid_json_rejected(raw_json: str) -> dict[str, object]:
    """Verify non-RFC 8259 input (single quotes, True, trailing comma) raises JSONDecodeError."""
    try:
        json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {"invalid_rfc8259_json_rejected": True, "error": exc.msg}
    return {"invalid_rfc8259_json_rejected": False, "error": ""}


def detect_yaml_11_norway_trap(unquoted_scalar: str) -> dict[str, object]:
    """Demonstrate why unquoted country code 'NO' or port state 'on' becomes boolean in YAML 1.1."""
    lowered = unquoted_scalar.strip().lower()
    trapped = lowered in YAML_11_BOOL_LITERALS
    return {
        "raw_value": unquoted_scalar,
        "yaml_1_1_coerced_to_bool": trapped,
        "safe_representation": f'"{unquoted_scalar}"',
    }


def parse_xml_with_namespace(xml_text: str) -> list[dict[str, str]]:
    """Parse IETF YANG XML using explicit Clark-notation namespace (not raw tag name)."""
    ns = {"if": "urn:ietf:params:xml:ns:yang:ietf-interfaces"}
    root = ET.fromstring(xml_text)
    rows = []
    for iface in root.findall("if:interface", ns):
        name_el = iface.find("if:name", ns)
        en_el = iface.find("if:enabled", ns)
        rows.append({
            "name": name_el.text if name_el is not None and name_el.text else "",
            "enabled": en_el.text if en_el is not None and en_el.text else "",
        })
    return rows


def main() -> None:
    print("Local Python serialization lab only — no real RESTCONF/NETCONF device is contacted.")
    print("Parsed JSON:", parse_json_strict(SAMPLE_JSON))
    invalid_check = check_invalid_json_rejected(INVALID_JSON_RFC8259)
    assert invalid_check["invalid_rfc8259_json_rejected"] is True
    print("Invalid RFC 8259 JSON check:", invalid_check)
    print("YAML 1.1 Norway trap ('NO'):", detect_yaml_11_norway_trap("NO"))
    print("YAML 1.1 safe string ('IR'):", detect_yaml_11_norway_trap("IR"))
    print("Parsed XML with Namespace:", parse_xml_with_namespace(SAMPLE_NETCONF_XML))


if __name__ == "__main__":
    main()
