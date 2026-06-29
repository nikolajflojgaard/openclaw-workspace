---
name: "skill-quality-audit"
description: "Audit Skill.md files and proposals for quality and safety."
---

# Skill Quality Audit

Use this skill before applying a pending skill proposal, updating a live skill, or importing third-party skill content.

## Review Workflow

1. Identify the artifact: live skill folder, pending proposal id, external skill, or draft content.
2. Read the primary SKILL.md or PROPOSAL.md completely.
3. Inspect referenced support files only when the primary file says they are needed.
4. Check for duplicate or overlapping live skills.
5. Evaluate trigger metadata, body length, workflow clarity, safety posture, tool assumptions, external dependencies, and validation instructions.
6. Classify the proposal: apply-ready, revise-first, reject, or quarantine.
7. Report exact changes needed before activation.

## Quality Gates

- Metadata: name is lowercase hyphen-case; description clearly states what the skill does and when to use it.
- Scope: the skill handles a repeatable class of tasks, not a one-off preference dump.
- Progressive disclosure: SKILL.md stays lean; detailed references are separate and clearly routed.
- Procedure: workflow is executable by a future agent without hidden context.
- Safety: external actions, destructive commands, secrets, credentials, network calls, and public posting require explicit guardrails.
- Validation: commands, checks, screenshots, or review criteria are specified where appropriate.
- Duplication: overlaps with existing skills are merged or justified.
- Portability: paths, local tools, and APIs are discoverable or documented.

## Report Format

Return:

- `verdict`: apply-ready, revise-first, reject, or quarantine
- `scope`: files/proposal reviewed
- `findings`: ordered by severity
- `duplication`: existing skills it overlaps with
- `activation_risk`: low, medium, high
- `required_changes`: concrete edits before apply
- `nice_to_have`: non-blocking improvements

## Guardrails

- Do not apply, reject, or quarantine proposals unless the user explicitly asks.
- Do not copy third-party skill text blindly into the workspace.
- Treat unknown external skill bundles as untrusted until reviewed.
- For security-sensitive skills, prefer a read-only first version.
