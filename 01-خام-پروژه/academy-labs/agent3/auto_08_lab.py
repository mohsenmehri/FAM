#!/usr/bin/env python3
"""
FAM Academy Lab — auto_08: NETCONF (RFC 6241 / RFC 6242) Local Educational Simulator.

Execution boundary & honest limitations:
- Byte-oriented RFC 6242 Section 4.2 chunked framing in pure Python 3 stdlib:
  chunks are split strictly on OCTET boundaries (not characters), so multi-byte
  UTF-8 sequences (e.g., Persian text like 'سلام') split across chunk boundaries
  frame and reassemble cleanly without UnicodeDecodeError, with UTF-8 decoding
  performed only at the complete reassembled message boundary.
- The datastore class (NetconfDatastoreMock) is a MINIMAL EDUCATIONAL STATE MACHINE:
  it does NOT model real concurrent NETCONF sessions, real YANG/XML schema validation,
  real wall-clock confirm-timeout timers, persist/persist-id cross-session handoff,
  or live SSH-830 network devices.
"""

from __future__ import annotations

import copy
import json
import re

RFC6242_MAX_CHUNK_SIZE = 4294967295  # 2^32 - 1 per RFC 6242 Section 4.2 ABNF
_CHUNK_SIZE_RE = re.compile(rb"^[1-9][0-9]{0,9}$")


def frame_netconf_1_0(xml_payload: str) -> str:
    if not isinstance(xml_payload, str):
        raise ValueError("xml_payload must be str")
    return xml_payload + "]]>]]>"


def frame_netconf_1_1_chunked(xml_payload: str | bytes, chunk_size: int | None = None) -> bytes:
    """Encode payload into byte-oriented RFC 6242 Section 4.2 chunked framing.

    Per RFC 6242, chunk-size counts OCTETS (1..4294967295); individual chunks do NOT
    need to be standalone valid UTF-8 strings.
    """
    if isinstance(xml_payload, str):
        data = xml_payload.encode("utf-8")
    elif isinstance(xml_payload, (bytes, bytearray)):
        data = bytes(xml_payload)
    else:
        raise ValueError("xml_payload must be non-empty str or bytes")
    if not data:
        raise ValueError("xml_payload must be non-empty")

    if chunk_size is None:
        if len(data) > RFC6242_MAX_CHUNK_SIZE:
            raise ValueError("single chunk exceeds RFC 6242 max chunk-size")
        return b"\n#" + str(len(data)).encode("ascii") + b"\n" + data + b"\n##\n"

    if (
        isinstance(chunk_size, bool)
        or not isinstance(chunk_size, int)
        or chunk_size <= 0
        or chunk_size > RFC6242_MAX_CHUNK_SIZE
    ):
        raise ValueError(
            f"chunk_size must be an int in 1..{RFC6242_MAX_CHUNK_SIZE} (not bool), got {chunk_size!r}"
        )

    parts: list[bytes] = []
    for i in range(0, len(data), chunk_size):
        piece = data[i : i + chunk_size]
        parts.append(b"\n#" + str(len(piece)).encode("ascii") + b"\n" + piece)
    parts.append(b"\n##\n")
    return b"".join(parts)


def parse_netconf_1_1_chunked_bytes(framed: bytes | str) -> bytes:
    """Parse RFC 6242 Section 4.2 chunked framing into raw reassembled message octets."""
    if isinstance(framed, str):
        raw = framed.encode("utf-8")
    elif isinstance(framed, (bytes, bytearray)):
        raw = bytes(framed)
    else:
        raise ValueError("framed message must be bytes or str")

    pos = 0
    chunks: list[bytes] = []
    while pos < len(raw):
        if raw[pos : pos + 4] == b"\n##\n":
            pos += 4
            if pos != len(raw):
                raise ValueError("Trailing bytes after RFC 6242 end-of-chunks marker")
            if not chunks:
                raise ValueError("RFC 6242 message contained zero chunks")
            return b"".join(chunks)
        if not raw[pos:].startswith(b"\n#"):
            raise ValueError(f"Invalid RFC 6242 chunk header at byte {pos}")
        nl = raw.find(b"\n", pos + 2)
        if nl == -1:
            raise ValueError("Unterminated RFC 6242 chunk length header")
        size_token = raw[pos + 2 : nl]
        if not _CHUNK_SIZE_RE.fullmatch(size_token):
            raise ValueError(f"Invalid RFC 6242 chunk-size token: {size_token!r}")
        size = int(size_token.decode("ascii"))
        if size <= 0 or size > RFC6242_MAX_CHUNK_SIZE:
            raise ValueError(f"RFC 6242 chunk-size out of range: {size}")
        start = nl + 1
        end = start + size
        if end > len(raw):
            raise ValueError("Truncated RFC 6242 chunk body")
        chunks.append(raw[start:end])
        pos = end
    raise ValueError("Missing RFC 6242 end-of-chunks marker '\\n##\\n'")


def parse_netconf_1_1_chunked(framed: bytes | str) -> str:
    """Reassemble RFC 6242 byte chunks first, then decode complete UTF-8 message text."""
    reassembled = parse_netconf_1_1_chunked_bytes(framed)
    try:
        return reassembled.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Reassembled NETCONF 1.1 payload is not valid UTF-8") from exc


class NetconfDatastoreMock:
    """Minimal educational datastore state machine (NOT a real NETCONF server/timer/validator)."""

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
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty str")
        if self.locked_by is not None and self.locked_by != session_id:
            raise RuntimeError(f"Session {session_id!r} cannot unlock lock held by {self.locked_by!r}")
        self.locked_by = None

    def edit_candidate(self, session_id: str, new_acl: list[str]) -> None:
        if not isinstance(session_id, str) or not session_id.strip() or self.locked_by != session_id:
            raise RuntimeError("Must hold <lock> before edit")
        if not isinstance(new_acl, list) or not all(isinstance(rule, str) and rule.strip() for rule in new_acl):
            raise ValueError("new_acl must be a list of non-empty str")
        self.candidate["acl_mgmt"] = list(new_acl)

    def validate_candidate(self) -> bool:
        return bool(self.candidate.get("acl_mgmt"))

    def commit_confirmed(self, session_id: str) -> None:
        if not isinstance(session_id, str) or not session_id.strip() or self.locked_by != session_id:
            raise RuntimeError("Must hold <lock> before confirmed-commit")
        if self.pending_backup is not None:
            raise RuntimeError("This minimal model does not support repeated confirmed commits")
        if not self.validate_candidate():
            raise ValueError("Candidate datastore validation failed (empty acl_mgmt)")
        self.pending_backup = copy.deepcopy(self.running)
        self.running = copy.deepcopy(self.candidate)

    def confirm_timeout_expired(self) -> None:
        if self.pending_backup is not None:
            self.running = copy.deepcopy(self.pending_backup)
            self.candidate = copy.deepcopy(self.pending_backup)
            self.pending_backup = None

    def confirm_commit(self, session_id: str) -> None:
        if not isinstance(session_id, str) or not session_id.strip() or self.locked_by != session_id or self.pending_backup is None:
            raise RuntimeError("Model confirmation requires owner and pending change")
        self.pending_backup = None


def main() -> None:
    tricky_xml = "<rpc><!-- valid XML comment ]]>]]> --><description>فارسی سلام</description></rpc>"
    v10 = frame_netconf_1_0(tricky_xml)
    v10_split_pieces = v10.split("]]>]]>")  # breaks prematurely!
    v11 = frame_netconf_1_1_chunked(tricky_xml)
    v11_decoded = parse_netconf_1_1_chunked(v11)
    v11_multi = parse_netconf_1_1_chunked(frame_netconf_1_1_chunked(tricky_xml, chunk_size=7))
    # Byte-oriented UTF-8 check: 1-byte chunks across multi-byte Persian characters ('سلام' = 8 UTF-8 octets)
    persian_1byte_framed = frame_netconf_1_1_chunked("سلام", chunk_size=1)
    assert parse_netconf_1_1_chunked(persian_1byte_framed) == "سلام"
    assert len(v10_split_pieces) > 2, "NETCONF 1.0 delimiter should break on embedded ]]>]]>"
    assert v11_decoded == tricky_xml and v11_multi == tricky_xml

    ds = NetconfDatastoreMock()
    ds.lock("sess-101")
    ds.edit_candidate("sess-101", ["deny any"])  # broken ACL that locks out admin!
    ds.commit_confirmed("sess-101")
    assert ds.running["acl_mgmt"] == ["deny any"]
    # Simulated timeout expiration (no real wall-clock timer or live router)
    ds.confirm_timeout_expired()
    assert ds.running["acl_mgmt"] == ["permit 10.0.0.0/24"], "Auto-rollback failed"

    # Safe change with explicit confirming <commit/>
    ds.edit_candidate("sess-101", ["permit 10.0.0.0/24", "permit 10.1.0.0/24"])
    ds.commit_confirmed("sess-101")
    ds.confirm_commit("sess-101")
    ds.unlock("sess-101")
    assert len(ds.running["acl_mgmt"]) == 2

    print("=== auto_08 NETCONF RFC 6241/6242 Byte-Oriented Local Simulator ===")
    print(json.dumps({
        "netconf_1_0_broken_split_count": len(v10_split_pieces),
        "netconf_1_1_chunked_intact": v11_decoded == tricky_xml,
        "netconf_1_1_multichunk_intact": v11_multi == tricky_xml,
        "utf8_1byte_octet_chunking_verified": True,
        "confirmed_commit_mock_rollback_verified": True,
        "final_running_acl": ds.running["acl_mgmt"],
        "simulator_scope_note": "Educational mock only; no live SSH-830 router, real YANG validator, or wall-clock timer.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
