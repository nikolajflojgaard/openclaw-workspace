#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
FILES = [ROOT / 'MEMORY.md', ROOT / 'MEMORY-SYSTEM.md', ROOT / 'MEMORY-DISTILLATION.md']
MEMORY_DIR = ROOT / 'memory'
OUT = MEMORY_DIR / 'index.json'


def score_line(line: str) -> int:
    s = line.strip()
    if not s:
        return 0
    score = 1
    if s.startswith('- '):
        score += 2
    if '`' in s:
        score += 1
    if len(s) > 40:
        score += 1
    return score


def iter_files():
    for path in FILES:
        if path.exists():
            yield path
    if MEMORY_DIR.exists():
        for path in sorted(MEMORY_DIR.glob('20*.md')):
            yield path


def main():
    docs = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        lines = text.splitlines()
        entries = []
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            entries.append({
                'line': idx,
                'text': stripped,
                'score': score_line(stripped),
            })
        docs.append({
            'path': rel,
            'updated_at': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            'entries': entries,
        })

    payload = {
        'generated_at': datetime.now().isoformat(),
        'docs': docs,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    main()
