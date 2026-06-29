---
name: "pairwise-test-design"
description: "Design compact pairwise/combinatorial test suites."
---

# Pairwise Test Design

Use this skill when exhaustive testing is too large but single happy-path tests are too weak.

## Workflow

1. Identify the behavior under test and the failure modes that matter.
2. Extract dimensions: inputs, roles, permissions, feature flags, environment, browser/device, locale, data state, integration state, and error conditions.
3. Define values for each dimension. Keep values behaviorally meaningful, not just syntactic.
4. Add constraints for impossible or irrelevant combinations.
5. Generate a pairwise matrix using an available tool such as PICT, a local package, or a small script. If no generator is available, manually build a minimal covering matrix and state the limitation.
6. Add mandatory edge cases that pairwise coverage may miss: boundaries, null/empty, max length, duplicate, concurrent update, timeout, permission denial, retry, and migration/backward-compat states.
7. Map each row to an executable test, manual QA step, or fixture.
8. Report what is covered and what is deliberately out of scope.

## Output Shape

Return:

- `model`: dimensions, values, and constraints
- `matrix`: numbered test combinations
- `must_run_edges`: cases added outside pairwise coverage
- `automation_plan`: where these tests should live
- `coverage_notes`: risks pairwise testing does not cover

## Quality Rules

- Keep the matrix small enough to run repeatedly.
- Preserve important business cases even if the generator would omit them.
- Do not hide constraints; impossible combinations must be explicit.
- Prefer stable IDs for rows so failures can be tracked over time.
- For UI flows, include viewport and input-method dimensions when layout or accessibility risk exists.

## Guardrails

- Do not claim full coverage from pairwise coverage.
- Do not invent requirements. If a dimension is uncertain, mark it as an assumption.
- Do not install generators globally without user approval; prefer existing local tools or temporary project-local execution.
