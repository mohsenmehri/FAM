#!/usr/bin/env python3
"""Read-only intake of JSON blueprints; never imports, executes or integrates code.

Structural checks only. A clean result is NOT a technical or security review.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect(paths, owner, inventory):
    allowed = {row['legacyId'] for row in inventory['lessons'] if row['owner'] == owner}
    found, errors = {}, []
    for path in paths:
        path = Path(path)
        try:
            if path.stat().st_size > 4_000_000:
                raise ValueError('file exceeds 4 MB intake limit')
            bp = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(bp, dict):
                raise ValueError('expected JSON object')
            lesson = bp.get('lessonId')
            if not isinstance(lesson, str) or lesson not in allowed:
                raise ValueError(f'lessonId not assigned to {owner}: {lesson!r}')
            if lesson in found:
                raise ValueError(f'duplicate lessonId: {lesson}')
            if bp.get('schema') != 'fam-app-blueprint-v1':
                raise ValueError('unsupported schema')
            if not isinstance(bp.get('sections'), list) or not bp['sections']:
                raise ValueError('missing lesson sections')
            if not isinstance(bp.get('interactiveQuiz'), list) or not bp['interactiveQuiz']:
                raise ValueError('missing interactive quiz')
            # The raw content remains untrusted; no automatic HTML or code execution.
            found[lesson] = str(path)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f'{path}: {exc}')
    if not paths:
        errors.append('no files supplied')
    return {'owner': owner, 'acceptedForInspection': found, 'errors': errors,
            'notYetProvided': sorted(allowed - found.keys()),
            'warning': 'Structure only; not integrated, content-reviewed, safe to execute, or progress-migrated.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True, choices=('agent-1', 'agent-3'))
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    inventory = json.loads((ROOT / 'academy-labs/legacy-coverage.json').read_text(encoding='utf-8'))
    result = inspect(args.files, args.owner, inventory)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
