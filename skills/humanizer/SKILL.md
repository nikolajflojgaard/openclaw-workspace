---
name: humanizer
description: Strip common AI-writing patterns from drafts before publishing. Use when preparing user-facing prose (posts, briefs, emails, long chat replies), especially texts longer than ~120 words. Detect and rewrite obvious tells (stock phrases, hedging, performed authenticity), and structural patterns (em dashes, rule-of-three cadence, filler transitions).
---

Use the bundled script for deterministic cleanup:

- Command:
  - `python3 skills/humanizer/scripts/humanize.py --in <input.txt> --out <output.txt>`
  - or `python3 skills/humanizer/scripts/humanize.py --text "..."`

Workflow:
1. Run the script on any user-facing prose longer than ~120 words.
2. Review flagged issues from stdout (`flags` list).
3. Keep meaning intact; tighten only style and patterning.
4. If the text is intentionally formal or legal, keep domain terms and only remove obvious AI cadence.

Rules enforced by script:
- Replace stock openers/bridges (e.g., “at the end of the day”, “it’s worth noting”).
- Reduce hedging clusters (e.g., “might”, “could”, “arguably”, “perhaps”) when unnecessary.
- Replace em dash with comma/period where possible.
- Collapse “performed authenticity” scaffolding (“let’s be real”, “honestly”, “as an AI…”).
- Break repetitive “rule-of-three” rhetorical cadence when it sounds templated.

If needed, inspect phrase lists in `references/patterns.md`.
Run regression checks:
- `python3 skills/humanizer/tests/test_humanize.py`
