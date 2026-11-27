#!/usr/bin/env python3
"""
FAM Academy Lab — auto_08: NETCONF (RFC 6241 / RFC 6242) Local Mock.
Execution boundary: Pure local Python 3 stdlib simulation of NETCONF 1.1
chunked framing, running/candidate datastores, <lock>, <edit-config>,
<validate>, and <confirmed-commit> rollback. No live router/SSH-830 connected.
"""

from __future__ import annotations

import copy
import json


def frame_netconf_1_0(xml_payload: str) -> str:
    return xml_payload + "]]>]]>"


def frame_netconf_1_1_chunked(xml_payload: str) -> str:
    data = xml_payload.encode("utf-8")
    return f"\n#{len(data)}\n{xml_payload}\n##\n"


def parse_netconf_1_1_chunked(framed: str) -> str:
    assert framed.startswith("\n#") and framed.endswith("\n##\n")
    first_nl = framed.index("\n", 2)
    length = int(framed[2:first_nl])
    body = framed[first_nl + 1 : -4]
    assert len(body.encode("utf-8")) == length, "Chunk length mismatch"
    return body


class NetconfDatastoreMock:
    def __init__(self) -> None:
        self.running = {"acl_mgmt": ["permit 10.0.0.0/24"]}
        self.candidate = copy.deepcopy(self.running)
        self.locked_by: str | None = None
        self.pending_backup: dict | None = None

    def lock(self, session_id: str) -> None:
        if self.locked_by and self.locked_by != session_id:
            raise RuntimeError(f"Datastore already locked by {self.locked_by}")
        self.locked_by = session_id

    def unlock(self, session_id: str) -> None:
        if self.locked_by == session_id:
            self.locked_by = None

    def edit_candidate(self, session_id: str, new_acl: list[str]) -> None:
        assert self.locked_by == session_id, "Must hold <lock> before edit"
        self.candidate["acl_mgmt"] = list(new_acl)

    def validate_candidate(self) -> bool:
        return bool(self.candidate.get("acl_mgmt"))

    def commit_confirmed(self, session_id: str) -> None:
        assert self.locked_by == session_id
        assert self.validate_candidate(), "Validation failed"
        self.pending_backup = copy.deepcopy(self.running)
        self.running = copy.deepcopy(self.candidate)

    def confirm_timeout_expired(self) -> None:
        if self.pending_backup is not None:
            self.running = copy.deepcopy(self.pending_backup)
            self.candidate = copy.deepcopy(self.pending_backup)
            self.pending_backup = None

    def confirm_commit(self) -> None:
        self.pending_backup = None


def main() -> None:
    tricky_xml = "<rpc><description>Contains delimiter ]]>]]> inside banner</description></rpc>"
    v10 = frame_netconf_1_0(tricky_xml)
    v10_split_pieces = v10.split("]]>]]>")  # breaks prematurely!
    v11 = frame_netconf_1_1_chunked(tricky_xml)
    v11_decoded = parse_netconf_1_1_chunked(v11)
    assert len(v10_split_pieces) > 2, "NETCONF 1.0 delimiter should break on embedded ]]>]]>"
    assert v11_decoded == tricky_xml, "NETCONF 1.1 chunked framing must preserve payload intact"

    ds = NetconfDatastoreMock()
    ds.lock("sess-101")
    ds.edit_candidate("sess-101", ["deny any"])  # broken ACL that locks out admin!
    ds.commit_confirmed("sess-101")
    assert ds.running["acl_mgmt"] == ["deny any"]
    # Admin loses SSH access -> cannot send confirming <commit/> -> timeout expires
    ds.confirm_timeout_expired()
    assert ds.running["acl_mgmt"] == ["permit 10.0.0.0/24"], "Auto-rollback failed"

    # Safe change with explicit confirming <commit/>
    ds.edit_candidate("sess-101", ["permit 10.0.0.0/24", "permit 10.1.0.0/24"])
    ds.commit_confirmed("sess-101")
    ds.confirm_commit()
    ds.unlock("sess-101")
    assert len(ds.running["acl_mgmt"]) == 2

    print("=== auto_08 NETCONF RFC 6241/6242 Local Mock Lab ===")
    print(json.dumps({
        "netconf_1_0_broken_split_count": len(v10_split_pieces),
        "netconf_1_1_chunked_intact": v11_decoded == tricky_xml,
        "confirmed_commit_auto_rollback_verified": True,
        "final_running_acl": ds.running["acl_mgmt"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
