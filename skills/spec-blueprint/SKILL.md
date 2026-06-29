---
name: "spec-blueprint"
description: "Turn messy feature requests into buildable specs and plans."
---

# Spec Blueprint

Use this skill when a request is too broad to implement safely from a single sentence, or when the work crosses UI, data, API, automation, or operational boundaries.

## Default Posture

- Ship smaller.
- Clarify only what cannot be reasonably inferred.
- Prefer a thin buildable slice over a grand plan.
- Tie every requirement to validation.
- Keep the blueprint short enough to execute.

## Blueprint Workflow

1. Restate the outcome in one paragraph.
2. Identify users, workflows, inputs, outputs, and non-goals.
3. Inspect existing code, docs, APIs, data contracts, and deployment paths before proposing changes.
4. Define the smallest useful slice.
5. Sketch architecture: ownership boundaries, data flow, persistence, integrations, auth, failure modes, and observability.
6. Break implementation into ordered steps with validation after each meaningful chunk.
7. Identify risks, assumptions, and decisions needed from the user.
8. If implementation is authorized, work from the blueprint and update it when reality changes.

## Output Shape

Return:

- `objective`
- `users_and_workflows`
- `scope`
- `non_goals`
- `architecture`
- `data_contracts`
- `implementation_plan`
- `validation_plan`
- `risks_and_assumptions`
- `open_questions`

## Quality Rules

- Do not ask the user for details already discoverable from the repo.
- Do not over-specify throwaway work.
- Do not invent a platform or framework when the existing repo has one.
- Include rollback or recovery notes for external actions, migrations, scheduled jobs, and automations.
- For frontend work, include target screens and viewport validation.

## Guardrails

- A blueprint is not completion. Do not claim the work is shipped until implementation and validation are done.
- If a user asks for direct implementation and the scope is small, skip the full blueprint and build.
- If the work affects public systems or messages, require explicit approval before external action.
