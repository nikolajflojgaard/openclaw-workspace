# DEBUG-LOOP.md

A practical debug workflow for Jason.

Use this when a bug is real, reproducible, and worth fixing properly.

## Goal

Stop guessing. Reproduce, isolate, patch, verify, ship.

## Loop

1. **Define the bug clearly**
   - What happened?
   - What should have happened?
   - Which exact flow triggered it?

2. **Find the real mutation path**
   - UI action
   - websocket/service call
   - backend/storage write
   - downstream sync/update/render path

3. **Instrument or inspect at the narrowest useful layer**
   - prefer tracing the exact handler over broad “maybe this” fixes
   - add logging or assertions if needed

4. **Patch the source of truth**
   - prefer backend/storage correctness over frontend compensating hacks
   - only patch UI when the bug is truly UI-local

5. **Test the specific broken flow**
   - reproduce with the exact action that failed before
   - also test nearby flows for regressions

6. **Ship completely**
   - build
   - commit
   - push
   - release/tag if HACS or similar distribution is involved
   - verify deployment/update path

7. **State the honest status**
   - fixed
   - partially fixed
   - workaround only
   - still broken but narrowed

## Rules

- Do not call a workaround a fix.
- Do not trust assumed code paths if the real UX says otherwise.
- If the bug survives one patch, stop broad guessing and trace the exact live path.
- For HA/HACS integrations, treat backend version, frontend version, tag, release, and restart expectations as one release unit.
