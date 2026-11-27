#!/usr/bin/env python3
"""
Local Mock Lab — ccie_wl (CCIE Enterprise Wireless v1.1: Catalyst 9800 3-Tag Audit, RadioActive Trace & WMM QoS)
Simulates (1) Catalyst 9800 IOS-XE modular Policy/Site/RF Tag AP binding validation,
(2) RadioActive client onboarding trace (802.11 Assoc -> 802.1X EAP -> DHCP -> SGT),
and (3) RFC 8325 / Cisco DSCP-to-802.11e WMM User Priority mapping verification.
No real Cisco Catalyst 9800 WLC, Catalyst Center, or physical AP is connected.
"""

import json


DSCP_TO_WMM_UP = {
    "EF (46) Voice": {"up": 6, "ac": "AC_VO (Voice)"},
    "AF41 (34) Video": {"up": 4, "ac": "AC_VI (Video)"},
    "CS3 (24) Signaling": {"up": 3, "ac": "AC_BE / Call-Signaling"},
    "BE (0) Default": {"up": 0, "ac": "AC_BE (Best Effort)"},
}


def _require_bool(val: object, name: str) -> bool:
    if not isinstance(val, bool):
        raise ValueError(f"{name} must be a strict Python bool (True/False), got {val!r} ({type(val).__name__})")
    return val


def audit_c9800_ap_tags(ap: dict) -> dict:
    if not isinstance(ap, dict) or not isinstance(ap.get("name"), str) or not ap["name"].strip():
        raise ValueError("ap must be a dict with a non-empty string 'name'")
    for tag_key in ("policy_tag", "site_tag", "rf_tag"):
        val = ap.get(tag_key)
        if val is not None and not isinstance(val, str):
            raise ValueError(f"{tag_key} must be str or None, got {val!r} ({type(val).__name__})")
    missing = []
    if not (ap.get("policy_tag") or "").strip() or ap["policy_tag"] == "default-policy-tag":
        missing.append("Custom Policy Tag missing (WLAN not mapped to Policy Profile)")
    if not (ap.get("site_tag") or "").strip():
        missing.append("Site Tag missing (Local vs FlexConnect mode undefined)")
    if not (ap.get("rf_tag") or "").strip():
        missing.append("RF Tag missing (5 GHz / 2.4 GHz RF Profiles not bound)")
    return {"ap": ap["name"], "ssid_broadcasting": len(missing) == 0, "issues": missing}


def radioactive_client_trace(mac: str, eap_ok: bool, dhcp_ok: bool, sgt: int | None) -> dict:
    if not isinstance(mac, str) or not mac.strip():
        raise ValueError(f"mac must be a non-empty str, got {mac!r}")
    eap = _require_bool(eap_ok, "eap_ok")
    dhcp = _require_bool(dhcp_ok, "dhcp_ok")
    if sgt is not None and (isinstance(sgt, bool) or not isinstance(sgt, int) or not (0 <= sgt <= 65535)):
        raise ValueError(f"sgt must be None or int in [0, 65535] (not bool), got {sgt!r}")
    timeline = [
        {"stage": "1_80211_AUTH_ASSOC", "status": "SUCCESS"},
        {"stage": "2_8021X_EAP_TLS", "status": "SUCCESS" if eap else "FAILED_CERT_OR_ISE_TIMEOUT"},
    ]
    if not eap:
        return {"client_mac": mac, "final_state": "DEAUTHENTICATED", "timeline": timeline}
    timeline.append({"stage": "3_DHCP_IP_LEARN", "status": "SUCCESS" if dhcp else "FAILED_VLAN_OR_HELPER"})
    if not dhcp:
        return {"client_mac": mac, "final_state": "IP_LEARN_TIMEOUT", "timeline": timeline}
    timeline.append({"stage": "4_RUN_STATE_SGT", "status": f"RUN (SGT={sgt})"})
    return {"client_mac": mac, "final_state": "RUN", "timeline": timeline}


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_C9800_WLC_OR_AP_HARDWARE",
        "c9800_tag_audits": [
            audit_c9800_ap_tags({"name": "AP-FL1-01", "policy_tag": "default-policy-tag", "site_tag": "SITE-HQ", "rf_tag": None}),
            audit_c9800_ap_tags({"name": "AP-FL1-02", "policy_tag": "PT-CORP-8021X", "site_tag": "ST-HQ-LOCAL", "rf_tag": "RT-HIGHDENSITY"}),
        ],
        "radioactive_traces": {
            "dhcp_failure_case": radioactive_client_trace("aa:bb:cc:11:22:33", eap_ok=True, dhcp_ok=False, sgt=None),
            "healthy_run_state": radioactive_client_trace("aa:bb:cc:11:22:44", eap_ok=True, dhcp_ok=True, sgt=10),
        },
        "wmm_qos_dscp_mapping": DSCP_TO_WMM_UP,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
