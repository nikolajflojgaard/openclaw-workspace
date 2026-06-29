---
name: "knowledge-wiki-curator"
description: "Turn research and docs into a local navigable knowledge wiki."
---

# Knowledge Wiki Curator

Use this skill when the user wants research, documentation, repo exploration, or long-form source material turned into durable local knowledge that can be reused later.

## Default Posture

- Source-grounded, not vibes.
- Compact pages beat giant dumps.
- Local markdown first; no external database unless requested.
- Separate raw notes from curated durable knowledge.
- Preserve source paths, dates, and uncertainty.

## Workflow

1. Define the knowledge target: topic, audience, freshness needs, and where the wiki should live.
2. Gather sources: local files, repos, web pages, transcripts, PDFs, docs, or notes. Use web only when current or external facts matter.
3. Create or update an index page with scope, page list, source list, and last-reviewed date.
4. Distill sources into topic pages using a stable structure: summary, key concepts, decisions, procedures, examples, caveats, and links.
5. Cross-link related pages and add tags only when they help retrieval.
6. Keep raw extracts in a separate notes area if needed; do not pollute curated pages with long quotes.
7. Add maintenance notes: what changed, what is stale, and when to re-check.
8. Validate that links resolve and that source attributions are sufficient.

## Page Template

```markdown
# Topic

Last reviewed: YYYY-MM-DD
Sources: path/link list

## Summary

## Key Ideas

## Practical Use

## Caveats

## Related Pages
```

## Quality Rules

- Do not overwrite existing curated notes without reading them first.
- Use exact dates for time-sensitive claims.
- Cite local source paths and line numbers where useful.
- Mark speculation and inference clearly.
- Keep each page focused; split when it becomes a mixed-topic dump.

## Guardrails

- Do not store secrets, private personal data, or credentials in knowledge pages.
- Do not publish or sync private notes externally without explicit approval.
- For copyrighted sources, summarize and quote sparingly.
- For medical, legal, or financial topics, include source quality and uncertainty notes.
