"""Local Data-Serialization Lab for auto_05 (Strict JSON RFC 8259, YAML 1.1/1.2 Traps & XML Namespaces).

Runs real Python 3 stdlib parsers (json, xml.etree.ElementTree) locally; no external NETCONF/RESTCONF
device or third-party PyYAML package is invoked.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

SAMPLE_JSON = '{"hostname": "edge-01", "vlans": [10, 20], "active": true}'
INVALID_JSON_SYNTAX = "{'hostname': 'edge-01', 'active': True,}"
INVALID_JSON_NAN = '{"x": NaN}'
INVALID_JSON_INF = '{"x": Infinity}'
INVALID_JSON_NEG_INF = '{"x": -Infinity}'
DUPLICATE_KEY_JSON = '{"vlan": 10, "vlan": 20}'

SAMPLE_NETCONF_XML = """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>GigabitEthernet1</name>
    <enabled>true</enabled>
  </interface>
</interfaces>
""".strip()

YAML_11_BOOL_LITERALS = frozenset({"yes", "no", "on", "off", "true", "false", "y", "n"})


def _reject_non_rfc8259_constant(token: str) -> object:
    """Reject Python json extension constants (NaN, Infinity, -Infinity) forbidden by RFC 8259."""
    raise ValueError(f"Non-RFC 8259 constant is not allowed in strict JSON: {token}")


def _reject_duplicate_object_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject duplicate object member names defensively (RFC 8259 Section 4: SHOULD be unique)."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(
                f"Duplicate JSON object key {key!r} rejected (RFC 8259 Section 4: names SHOULD be unique; "
                "behavior across parsers is unpredictable)"
            )
        result[key] = value
    return result


def parse_json_strict(raw_json: str, *, reject_duplicate_keys: bool = True) -> object:
    """Parse JSON strictly per RFC 8259: rejects NaN/Infinity/-Infinity and (by default) duplicate keys.

    Note on RFC 8259 Section 4:
    - NaN, Infinity, and -Infinity are NOT valid JSON tokens in RFC 8259 (Python's default json.loads
      accepts them as a non-standard extension unless parse_constant rejects them).
    - Duplicate object member names are discouraged by RFC 8259 Section 4 ("SHOULD be unique") rather
      than syntactically forbidden, because parser behavior varies (Python defaults to last-key-wins).
      Strict interoperability/security parsers reject duplicate keys via object_pairs_hook.
    """
    pairs_hook = _reject_duplicate_object_keys if reject_duplicate_keys else None
    return json.loads(
        raw_json,
        parse_constant=_reject_non_rfc8259_constant,
        object_pairs_hook=pairs_hook,
    )


def check_invalid_json_rejected(raw_json: str, *, reject_duplicate_keys: bool = True) -> dict[str, object]:
    """Verify non-RFC 8259 JSON (syntax error, NaN/Infinity/-Infinity, or duplicate key) is rejected."""
    try:
        parse_json_strict(raw_json, reject_duplicate_keys=reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        return {"rejected": True, "error_type": type(exc).__name__, "error": str(exc)}
    return {"rejected": False, "error_type": "", "error": ""}


def demonstrate_duplicate_key_behavior(raw_json: str) -> dict[str, object]:
    """Contrast Python default json.loads (silent last-key-wins) vs strict duplicate-key rejection."""
    default_parsed = json.loads(raw_json, parse_constant=_reject_non_rfc8259_constant)
    strict_check = check_invalid_json_rejected(raw_json, reject_duplicate_keys=True)
    return {
        "input": raw_json,
        "rfc8259_section_4_rule": "Object member names SHOULD be unique (syntactically permitted, unpredictable across parsers)",
        "python_default_last_wins": default_parsed,
        "strict_parser_rejected": strict_check["rejected"],
        "strict_error": strict_check["error"],
    }


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
    print("Local Python stdlib serialization lab — real json/xml parsers executed; no network device contacted.")
    parsed = parse_json_strict(SAMPLE_JSON)
    assert parsed == {"hostname": "edge-01", "vlans": [10, 20], "active": True}
    print("Parsed strict RFC 8259 JSON:", parsed)

    # Negative tests: syntax errors + non-RFC 8259 constants (NaN, Infinity, -Infinity)
    for label, sample in [
        ("invalid_syntax", INVALID_JSON_SYNTAX),
        ("nan_constant", INVALID_JSON_NAN),
        ("pos_infinity", INVALID_JSON_INF),
        ("neg_infinity", INVALID_JSON_NEG_INF),
    ]:
        res = check_invalid_json_rejected(sample)
        assert res["rejected"] is True, f"Expected {label} to be rejected!"
        print(f"Negative check [{label}]:", res)

    # Duplicate keys: RFC 8259 Section 4 (SHOULD be unique -> Python last-wins vs strict rejection)
    dup_report = demonstrate_duplicate_key_behavior(DUPLICATE_KEY_JSON)
    assert dup_report["python_default_last_wins"] == {"vlan": 20}
    assert dup_report["strict_parser_rejected"] is True
    print("Duplicate-key RFC 8259 Section 4 check:", dup_report)

    print("YAML 1.1 Norway trap ('NO'):", detect_yaml_11_norway_trap("NO"))
    print("YAML 1.1 safe string ('IR'):", detect_yaml_11_norway_trap("IR"))
    xml_rows = parse_xml_with_namespace(SAMPLE_NETCONF_XML)
    assert xml_rows == [{"name": "GigabitEthernet1", "enabled": "true"}]
    print("Parsed XML with Namespace:", xml_rows)


if __name__ == "__main__":
    main()
