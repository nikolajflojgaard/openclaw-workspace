---
name: "agent-qa-red-team"
description: "Read-only QA/red-team reviews for bugs, validation gaps, weak reasoning, and overclaims."
---

# Agent QA / Red Team

Use this skill when serious work deserves an independent read-only second pass before the hub claims it is done.

The reviewer is not a co-author. The reviewer finds actionable problems, missing evidence, and release-blocking risks. Findings come first. Summaries are secondary.

## Default Posture

- Read-only unless the hub explicitly promotes the lane.
- Findings before praise.
- Evidence over vibes.
- Reproduction over speculation.
- Blockers are named plainly.
- Low-confidence risks are separated from high-confidence findings.
- Secrets are reported by path/type only, never pasted.

## Review Workflow

1. Define review scope: changed files, commits, diffs, docs, generated artifacts, commands, screenshots, claims, and explicit non-goals.
2. Choose the smallest useful reviewer role set: Code QA, Docs QA, Security/Privacy, Validation QA, Reasoning Red Team, Release QA, or Memory QA.
3. Inspect evidence with `git diff`, `git status`, logs, generated files, exact commands, file/line references, or reproduction steps.
4. Classify findings as `blocker`, `high`, `medium`, `low`, `question`, or `risk`.
5. Write each finding with severity, title, evidence, impact, recommendation, and confidence.
6. Report in this order: Blockers, Findings, Questions, Low-confidence risks, Validation gaps, Summary.
7. Let the hub verify the review and decide whether to fix now, defer, ask the user, rerun validation, or stop release.

## Reviewer Contract

Return:

- `status`: done, blocked, partial, or no-findings
- `scope`: what was reviewed
- `findings`: prioritized list
- `questions`: decision points
- `validation_gaps`: checks not run or weak evidence
- `risks`: low-confidence concerns
- `summary`: short synthesis only after findings
- `handoff`: exact next action for the hub

## Read-Only Rules

- Do not edit files during a review lane.
- Do not stage, commit, push, deploy, publish, or send messages.
- Do not run destructive commands.
- Avoid commands that mutate lockfiles, caches, or generated outputs unless the hub explicitly asks for a tester lane.
- For secret findings, report the file path and secret type only.

## Validation Claims

Challenge validation claims when tests were not run, generated files were not checked, CI status was not inspected after push, screenshots were not verified for UI work, docs drift checks were skipped, a command failed but was hidden, or release was claimed before publication/deploy evidence existed.

## Overclaim Detection

Flag overclaims when the final answer says shipped, deployed, applied, published, fixed, validated, no issues, all, safe, latest, or current without matching evidence.

## Repo

Public source and support scripts live at https://github.com/nikolajflojgaard/agent-qa-red-team.
