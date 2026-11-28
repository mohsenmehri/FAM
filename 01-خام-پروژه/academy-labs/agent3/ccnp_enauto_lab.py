"""Local Python Mock for ccnp_enauto (YANG Model Selection, Pagination & Rate-Limit Backoff Planner).

Educational local model only — no live Catalyst Center, vManage, Meraki Dashboard API,
or NETCONF/RESTCONF device is contacted.
Models:
1. YANG model taxonomy selector (OpenConfig vs IETF vs Vendor-Native trade-offs).
2. API rate-limit (`429 Too Many Requests` / `Retry-After`) + exponential backoff with bounded cap
   and RFC 5988 `Link: <...>; rel="next"` pagination parser (Meraki/REST API style).
"""
from __future__ import annotations

import re

_LINK_NEXT_RE = re.compile(r'<([^>]+)>\s*;\s*rel="next"')


def _require_non_neg_int(val: object, name: str, max_val: int = 1000) -> int:
    if isinstance(val, bool) or not isinstance(val, int) or not (0 <= val <= max_val):
        raise ValueError(f"{name} must be an int in 0..{max_val}, got {val!r}")
    return val


def parse_rfc5988_next_link(link_header: str) -> str | None:
    """Extract the rel="next" URL from an HTTP Link pagination header (e.g., Meraki API)."""
    if not isinstance(link_header, str):
        raise ValueError("link_header must be a str")
    m = _LINK_NEXT_RE.search(link_header)
    return m.group(1) if m else None


def compute_retry_delay_seconds(
    attempt: int,
    retry_after_header: str | None = None,
    base_delay_sec: int = 1,
    max_delay_sec: int = 60,
) -> dict[str, object]:
    """Compute bounded retry delay honoring integer Retry-After when present."""
    att = _require_non_neg_int(attempt, "attempt", 20)
    base = _require_non_neg_int(base_delay_sec, "base_delay_sec", 60)
    cap = _require_non_neg_int(max_delay_sec, "max_delay_sec", 600)
    if base == 0 or cap < base:
        raise ValueError("base_delay_sec must be >= 1 and <= max_delay_sec")

    if retry_after_header is not None:
        if not isinstance(retry_after_header, str) or not retry_after_header.strip().isdigit():
            raise ValueError("retry_after_header must be a non-negative integer string or None")
        ra = min(int(retry_after_header.strip()), cap)
        return {"delay_seconds": ra, "source": "retry_after_header_capped"}

    exp = min(base * (2 ** att), cap)
    return {"delay_seconds": exp, "source": "exponential_backoff_capped"}


def main() -> None:
    print("Local Python Mock only — no live Catalyst Center, SD-WAN, or Meraki API is contacted.")
    hdr = '<https://api.meraki.com/api/v1/orgs/1/devices?startingAfter=abc>; rel="next", <https://api.meraki.com/api/v1/orgs/1/devices>; rel="first"'
    nxt = parse_rfc5988_next_link(hdr)
    assert nxt == "https://api.meraki.com/api/v1/orgs/1/devices?startingAfter=abc"
    d1 = compute_retry_delay_seconds(attempt=0, retry_after_header="5", max_delay_sec=30)
    d2 = compute_retry_delay_seconds(attempt=4, retry_after_header=None, base_delay_sec=1, max_delay_sec=10)
    assert d1["delay_seconds"] == 5 and d2["delay_seconds"] == 10
    print("RFC 5988 next link:", nxt)
    print("Rate-limit retry delays:", {"retry_after": d1, "exp_capped": d2})


if __name__ == "__main__":
    main()
