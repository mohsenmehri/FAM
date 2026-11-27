#!/usr/bin/env python3
"""
Local Mock Lab — spec_collab_gw (Collaboration Voice Gateways: CUBE/SBC, SIP Dial-Peers & SRST Failover)
Simulates inbound/outbound SIP Dial-Peer longest-match routing on a Cisco CUBE/IOS-XE Voice Gateway,
DTMF relay negotiation (rtp-nte), and branch SRST survivability when WAN to HQ CUCM fails.
No real Cisco CUBE, ISR Voice Gateway, or CUCM cluster is connected.
"""

import json


DIAL_PEERS = [
    {"tag": 100, "pattern": "911", "target": "ITSP-SIP-TRUNK-PRIMARY", "preference": 0, "dtmf": "rtp-nte", "emergency": True},
    {"tag": 200, "pattern": "9021", "target": "ITSP-SIP-TRUNK-PRIMARY", "preference": 0, "dtmf": "rtp-nte", "emergency": False},
    {"tag": 201, "pattern": "9021", "target": "ITSP-SIP-TRUNK-BACKUP", "preference": 1, "dtmf": "rtp-nte", "emergency": False},
    {"tag": 300, "pattern": "9", "target": "ITSP-SIP-TRUNK-PRIMARY", "preference": 0, "dtmf": "rtp-nte", "emergency": False},
]


def match_outbound_dial_peer(dialed_number: str, primary_trunk_up: bool = True) -> dict:
    candidates = [dp for dp in DIAL_PEERS if dialed_number.startswith(dp["pattern"])]
    # Longest match first, then lowest preference
    candidates.sort(key=lambda d: (-len(d["pattern"]), d["preference"]))
    for dp in candidates:
        if dp["target"] == "ITSP-SIP-TRUNK-PRIMARY" and not primary_trunk_up:
            continue
        return {
            "dialed": dialed_number,
            "matched_dial_peer": dp["tag"],
            "pattern": dp["pattern"],
            "routed_to": dp["target"],
            "dtmf_relay": dp["dtmf"],
            "emergency": dp["emergency"],
        }
    return {"dialed": dialed_number, "matched_dial_peer": None, "error": "503 Service Unavailable"}


def evaluate_branch_phone_state(wan_to_cucm_up: bool, srst_configured: bool) -> dict:
    if wan_to_cucm_up:
        return {"registered_with": "HQ-CUCM-Cluster", "call_survivability": "FULL_FEATURES", "e911_ok": True}
    if srst_configured:
        return {
            "registered_with": "Branch-Local-Router-SRST",
            "call_survivability": "SURVIVABLE_LOCAL_AND_PSTN_E911",
            "e911_ok": True,
        }
    return {
        "registered_with": "UNREGISTERED",
        "call_survivability": "TOTAL_VOICE_OUTAGE",
        "e911_ok": False,
    }


def main() -> None:
    report = {
        "mode": "LOCAL_MOCK_NO_REAL_CUBE_OR_CUCM_HARDWARE",
        "dial_peer_routing": {
            "emergency_911": match_outbound_dial_peer("911", primary_trunk_up=True),
            "tehran_primary_up": match_outbound_dial_peer("902188776655", primary_trunk_up=True),
            "tehran_primary_down_failover": match_outbound_dial_peer("902188776655", primary_trunk_up=False),
        },
        "srst_wan_outage_comparison": {
            "wan_up": evaluate_branch_phone_state(wan_to_cucm_up=True, srst_configured=True),
            "wan_down_with_srst": evaluate_branch_phone_state(wan_to_cucm_up=False, srst_configured=True),
            "wan_down_without_srst": evaluate_branch_phone_state(wan_to_cucm_up=False, srst_configured=False),
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
