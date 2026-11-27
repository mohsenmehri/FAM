#!/usr/bin/env python3
"""Verify the 114-ID inventory against explicitly supplied historical JSON."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(raw, inventory):
    if hashlib.sha256(raw).hexdigest() != inventory['sourceSha256']:
        raise ValueError('historical source SHA-256 differs')
    data = json.loads(raw)
    old = data['lessons']
    if not isinstance(old, dict):
        raise ValueError('expected historical lessons object')
    rows = inventory['lessons']
    ids = [row['legacyId'] for row in rows]
    if len(ids) != 114 or len(ids) != len(set(ids)) or set(ids) != set(old):
        raise ValueError('missing, extra or duplicate IDs')
    for row in rows:
        if row['title'] != old[row['legacyId']]['title']:
            raise ValueError(f"title mismatch: {row['legacyId']}")
    return len(ids)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('legacy_json', type=Path)
    args = parser.parse_args()
    inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text(encoding='utf-8'))
    try:
        count = verify(args.legacy_json.read_bytes(), inventory)
    except (KeyError, ValueError, OSError) as exc:
        parser.exit(1, f'Verification failed: {exc}\n')
    print(f'{count} historical IDs and titles match source SHA-256; not a content review')


if __name__ == '__main__':
    main()
