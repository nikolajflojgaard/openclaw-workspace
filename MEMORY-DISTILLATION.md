# MEMORY-DISTILLATION.md

Use this workflow to keep memory useful.

## Trigger conditions

Run distillation when one of these is true:
- a few days of daily notes have accumulated
- the same preference or pattern appears multiple times
- `MEMORY.md` starts feeling cluttered
- a project shifts from temporary work into durable context

## Distillation workflow

1. Read recent daily files in `memory/`.
2. Extract repeated facts, stable preferences, durable decisions, and lessons.
3. Update `MEMORY.md` with only the parts that are likely to matter again.
4. Remove outdated or duplicate bullets from `MEMORY.md`.
5. If the lesson should change behavior, update `AGENTS.md`, `TOOLS.md`, or another control file.
6. Rebuild the memory index after significant changes.

## Promotion criteria

Promote if the information is:
- stable
- reusable
- decision-relevant
- likely to matter across sessions

Do not promote if it is:
- a one-off chat detail
- temporary task state
- low-signal noise
- something already captured better elsewhere

## Output standard

After distillation:
- `MEMORY.md` should stay compact
- duplicated bullets should disappear
- rules should live in system files, not in vague notes
- daily files can remain messy; long-term memory should not
