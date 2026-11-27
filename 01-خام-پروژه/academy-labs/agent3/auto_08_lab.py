#!/usr/bin/env python3
"""
FAM Academy Lab — auto_08: NETCONF (RFC 6241 / RFC 6242) Local Mock.
Execution boundary: Pure local Python 3 stdlib simulation of NETCONF 1.1
multi-chunk framing (explicit ValueError checks, never disabled by python -O),
running/candidate datastores, <lock>, <edit-config>, <validate>, and
<confirmed-commit> rollback. No live router/SSH-830 connected.
"""

from __future__ import annotations

import copy
import json


def frame_netconf_1_0(xml_payload: str) -> str:
    if not isinstance(xml_payload, str):
        raise ValueError("xml_payload must be str")
    return xml_payload + "]]>]]>"


def frame_netconf_1_1_chunked(xml_payload: str, chunk_size: int | None = None) -> str:
    if not isinstance(xml_payload, str) or not xml_payload:
        raise ValueError("xml_payload must be a non-empty str")
    data = xml_payload.encode("utf-8")
    if chunk_size is None:
        return f"\n#{len(data)}\n{xml_payload}\n##\n"
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError(f"chunk_size must be a positive int, got {chunk_size!r}")
    parts = []
    for i in range(0, len(data), chunk_size):
        piece = data[i : i + chunk_size]
        parts.append(f"\n#{len(piece)}\n" + piece.decode("utf-8"))
    parts.append("\n##\n")
    return "".join(parts)


def parse_netconf_1_1_chunked(framed: str) -> str:
    """Parse RFC 6242 Section 4.2 chunked framing (supports single and multi-chunk messages)."""
    if not isinstance(framed, str):
        raise ValueError("framed message must be str")
    raw = framed.encode("utf-8")
    pos = 0
    chunks: list[bytes] = []
    while pos < len(raw):
        if raw[pos : pos + 4] == b"\n##\n":
            pos += 4
            if pos != len(raw):
                raise ValueError("Trailing bytes after RFC 6242 end-of-chunks marker")
            if not chunks:
                raise ValueError("RFC 6242 message contained zero chunks")
            return b"".join(chunks).decode("utf-8")
        if not raw[pos:].startswith(b"\n#"):
            raise ValueError(f"Invalid RFC 6242 chunk header at byte {pos}")
        nl = raw.find(b"\n", pos + 2)
        if nl == -1:
            raise ValueError("Unterminated RFC 6242 chunk length header")
        size_token = raw[pos + 2 : nl].decode("ascii")
        if not size_token.isdigit() or int(size_token) <= 0:
            raise ValueError(f"Invalid RFC 6242 chunk size: {size_token!r}")
        size = int(size_token)
        start = nl + 1
        end = start + size
        if end > len(raw):
            raise ValueError("Truncated RFC 6242 chunk body")
        chunks.append(raw[start:end])
        pos = end
    raise ValueError("Missing RFC 6242 end-of-chunks marker '\\n##\\n'")


class NetconfDatastoreMock:
    def __init__(self) -> None:
        self.running = {"acl_mgmt": ["permit 10.0.0.0/24"]}
        self.candidate = copy.deepcopy(self.running)
        self.locked_by: str | None = None
        self.pending_backup: dict | None = None

    def lock(self, session_id: str) -> None:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty str")
        if self.locked_by and self.locked_by != session_id:
            raise RuntimeError(f"Datastore already locked by {self.locked_by}")
        self.locked_by = session_id

    def unlock(self, session_id: str) -> None:
        if self.locked_by == session_id:
            self.locked_by = None

    def edit_candidate(self, session_id: str, new_acl: list[str]) -> None:
        if self.locked_by != session_id:
            raise RuntimeError("Must hold <lock> before edit")
        self.candidate["acl_mgmt"] = list(new_acl)

    def validate_candidate(self) -> bool:
        return bool(self.candidate.get("acl_mgmt"))

    def commit_confirmed(self, session_id: str) -> None:
        if self.locked_by != session_id:
            raise RuntimeError("Must hold <lock> before confirmed-commit")
        if not self.validate_candidate():
            raise ValueError("Candidate datastore validation failed (empty acl_mgmt)")
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
    v11_multi = parse_netconf_1_1_chunked(frame_netconf_1_1_chunked(tricky_xml, chunk_size=20))
    assert len(v10_split_pieces) > 2, "NETCONF 1.0 delimiter should break on embedded ]]>]]>"
    assert v11_decoded == tricky_xml and v11_multi == tricky_xml

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
        "netconf_1_1_multichunk_intact": v11_multi == tricky_xml,
        "confirmed_commit_auto_rollback_verified": True,
        "final_running_acl": ds.running["acl_mgmt"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
