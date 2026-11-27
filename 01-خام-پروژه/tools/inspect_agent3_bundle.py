#!/usr/bin/env python3
"""Inspect an extracted untrusted Agent 3 snapshot without executing or integrating it.

This checks presence, exact embedded lab text, provenance hashes and limited AST
signals. It does not certify code safety, semantic accuracy, or coverage quality.
"""
import argparse
import ast
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAGGED = {'socket', 'http', 'urllib', 'requests', 'subprocess', 'os'}


def read_in_root(base, relative):
    path = base / relative
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(base.resolve()) or not resolved.is_file():
        raise ValueError(f'path outside extracted bundle or not a file: {relative}')
    if resolved.stat().st_size > 4_000_000:
        raise ValueError(f'file too large: {relative}')
    return resolved.read_bytes()


def inspect(base, inventory):
    ids = sorted(row['legacyId'] for row in inventory['lessons'] if row['owner'] == 'agent-3')
    result = {'expected': len(ids), 'records': {}, 'errors': [],
              'warning': 'Static structural inspection only; no code was executed, reviewed, or integrated.'}
    for lesson in ids:
        try:
            blueprint_path = f'server/www/academy-assets/v5/blueprints/{lesson}.json'
            lab_path = f'academy-labs/agent3/{lesson}_lab.py'
            review_path = f'academy-labs/reviews/{lesson}-review-fa.md'
            blueprint_data = read_in_root(base, blueprint_path)
            lab_data = read_in_root(base, lab_path)
            review_data = read_in_root(base, review_path)
            bp = json.loads(blueprint_data)
            if bp.get('lessonId') != lesson or bp.get('objectiveId') != lesson:
                raise ValueError('lessonId/objectiveId mismatch')
            if bp.get('schema') != 'fam-app-blueprint-v1':
                raise ValueError('unexpected schema')
            lab_source = lab_data.decode('utf-8')
            embedded = lab_source in html.unescape(bp['stages']['lab']['html'])
            if not embedded:
                raise ValueError('embedded lab does not match source')
            tree = ast.parse(lab_source, filename=lab_path)
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split('.')[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.add((node.module or '').split('.')[0])
            result['records'][lesson] = {
                'blueprintSha256': hashlib.sha256(blueprint_data).hexdigest(),
                'labSha256': hashlib.sha256(lab_data).hexdigest(),
                'reviewSha256': hashlib.sha256(review_data).hexdigest(),
                'flaggedImports': sorted(imports & FLAGGED),
                'status': bp.get('reviewStatus', ''),
            }
        except (OSError, ValueError, KeyError, TypeError, UnicodeError, SyntaxError) as exc:
            result['errors'].append({'lesson': lesson, 'error': str(exc)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extracted_package', type=Path, help='extracted 01-خام-پروژه directory')
    args = parser.parse_args()
    inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text(encoding='utf-8'))
    result = inspect(args.extracted_package, inventory)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
