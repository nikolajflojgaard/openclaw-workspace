#!/usr/bin/env python3
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / 'memory' / 'index.json'
TOKEN_RE = re.compile(r"[a-zA-Z0-9_'-]+")
STOP = {
    'the','a','an','and','or','to','of','in','on','for','with','is','it','this','that','be','as','at','by','from','are','was','were','i','you','we','they','he','she','my','your','our'
}


def tok(s):
    return [t.lower() for t in TOKEN_RE.findall(s) if t.lower() not in STOP]


def cosine(a, b):
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[k] * b[k] for k in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    if not da or not db:
        return 0.0
    return num / (da * db)


def main():
    if len(sys.argv) < 2:
        print('Usage: memory_search.py <query>')
        sys.exit(1)
    query = ' '.join(sys.argv[1:])
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    qv = Counter(tok(query))
    results = []
    for doc in data['docs']:
        for entry in doc['entries']:
            ev = Counter(tok(entry['text']))
            sim = cosine(qv, ev)
            if sim <= 0:
                continue
            score = sim + (entry.get('score', 0) * 0.02)
            results.append({
                'path': doc['path'],
                'line': entry['line'],
                'text': entry['text'],
                'score': round(score, 4),
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    print(json.dumps(results[:10], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
