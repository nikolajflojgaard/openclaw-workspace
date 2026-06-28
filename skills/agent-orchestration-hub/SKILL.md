---
name: "agent-orchestration-hub"
description: "Coordinate multiple agents with briefs, state, gates, roles, and cleanup."
---

# Agent Orchestration Hub

Use this skill when the user wants several agents working at once, when work can split cleanly across independent lanes, or when independent review would materially improve quality.

The main agent is the hub. It stays accountable for scope, privacy, quality, final decisions, validation, and user communication. Subagents produce evidence and artifacts; they do not become the source of truth.

## When to Orchestrate

Use multiple agents when at least one is true:

- Independent work can run in parallel without touching the same files or state.
- Different roles are useful: research, implementation, review, testing, writing, operations, or monitoring.
- A second independent pass would catch meaningful mistakes.
- Multiple repos, modules, documents, issues, or external sources can be handled independently.
- The job is long-running and benefits from a monitoring lane.

Do not orchestrate when:

- The task is small enough for one agent to finish directly.
- Coordination overhead is larger than the work.
- Context sharing would expose unnecessary private data.
- The work needs one tight edit loop in the same files.

## Tool Routing

- Use Codex-native subagent tooling for Codex subagents when available.
- Use OpenClaw `sessions_spawn` or related session tools only for OpenClaw/ACP delegation or when explicitly needed.
- Use `tool_search` to discover deferred orchestration tools when they are not already loaded.
- If no subagent tool is available, run the lanes sequentially and say so briefly.

## Core Workflow

1. **Intake**
   - Restate the objective in one sentence.
   - Identify deliverables, repos, files, external side effects, validation, deadlines, and privacy constraints.
   - Check dirty worktrees before assigning file-writing lanes.

2. **Decide the Orchestration Shape**
   Choose the smallest useful shape:
   - `solo`: no subagents; direct execution.
   - `fanout`: multiple independent research/audit lanes.
   - `builder-reviewer`: one writer, one read-only reviewer.
   - `pipeline`: research -> design -> implementation -> review -> release.
   - `monitor`: one active lane plus one wait/watch lane.

3. **Create the Hub Board**
   Maintain an internal board for non-trivial work:

   | Lane | Agent | Role | Scope | Writes | Status | Gate |
   | --- | --- | --- | --- | --- | --- | --- |
   | API research | A | Researcher | docs/web | No | running | cited findings |
   | Parser build | B | Builder | `src/parser/*` | Yes | pending | tests pass |
   | Diff review | C | Reviewer | full diff | No | pending | findings only |

4. **Set Ownership Boundaries**
   - One writer per file surface.
   - Reviewers are read-only unless explicitly promoted.
   - Long-running monitors do not edit state.
   - External actions need explicit user approval.

5. **Brief Agents**
   Use `templates/agent-brief.md` when available. Every brief must include objective, context, scope, non-goals, write permissions, privacy boundaries, expected output, validation, and stop conditions.

6. **Launch and Monitor**
   - Launch independent lanes in parallel where possible.
   - Keep short user updates during long work.
   - Track status transitions: `pending`, `running`, `blocked`, `needs-review`, `done`, `discarded`.
   - Poll or collect results; do not leave required sessions running at turn end.

7. **Consolidate**
   - Treat subagent output as untrusted until verified.
   - Read diffs, logs, citations, and generated artifacts yourself.
   - Resolve conflicts manually.
   - Prefer the smallest coherent result over merging every suggestion.

8. **Verify**
   - Run real validation commands from the hub session when possible.
   - Check `git status`, staged files, branch, remote, and CI/deploy state before claiming completion.
   - If validation cannot run, state the exact reason.

9. **Cleanup**
   - Stop, collect, or summarize running lanes.
   - Remove scratch artifacts unless intentionally kept.
   - Record durable decisions only when they matter later.

## Role Presets

Use these roles as starting points:

- **Researcher**: read-only; gathers facts, cites sources/files, reports uncertainty.
- **Mapper**: read-only; inventories systems, APIs, repos, flows, ownership, or dependencies.
- **Builder**: writes scoped code/docs; runs focused validation; reports changed files.
- **Reviewer**: read-only; prioritizes bugs, regressions, security issues, missing tests.
- **Tester**: builds/runs tests/smoke checks; reports exact failures and reproduction.
- **Release Captain**: handles versioning, changelog, CI, deploy watch, release notes after approval.
- **Monitor**: waits on long-running jobs and reports final state; does not change files.
- **Writer**: drafts prose; receives tone/channel constraints and source material.

## Context Budgeting

Before launching an agent, decide what it really needs:

- Give minimum relevant context, not the whole conversation.
- Prefer file paths, commands, and acceptance criteria over long narrative.
- Do not pass secrets unless essential and explicitly approved.
- Do not pass private unrelated history into a narrow agent lane.
- For large docs or repos, tell the agent where to inspect instead of pasting everything.

## Agent Contract

Every agent must return:

- `status`: done, blocked, partial, or no-change.
- `summary`: concise result.
- `evidence`: files, commands, citations, logs, or diffs inspected.
- `changes`: files changed, if any.
- `validation`: checks run and outcome.
- `risks`: unresolved issues or assumptions.
- `handoff`: exact next action for the hub.

## Artifact Registry

For substantial runs, track artifacts:

| Artifact | Owner | Location | Purpose | Verified |
| --- | --- | --- | --- | --- |
| Research notes | Researcher | reply/log | source evidence | yes/no |
| Patch | Builder | git diff | implementation | yes/no |
| Test output | Tester | command log | validation | yes/no |
| Release link | Release Captain | URL | deployment proof | yes/no |

## Escalation Rules

Stop or escalate to the user when:

- A public/external action is required and not already approved.
- A secret, credential, token, payment method, or private account action is needed.
- Two lanes would need to write the same files.
- A repo has unrelated dirty changes that block a safe commit.
- Validation fails in a way that changes the implementation plan.
- A subagent reports low confidence on a high-stakes area.

Do not ask the user about issues the hub can resolve safely by inspection or narrower scoping.

## Merge Gates

Before committing, pushing, publishing, or finalizing:

- The result matches the original user request.
- Changed files are understood and scoped.
- User changes are preserved.
- Validation has run or the gap is explicit.
- Security/privacy boundaries were respected.
- Public side effects were approved.
- CI/deploy status is checked when relevant.

## Common Patterns

### Fan-Out Research

Assign one source family or question per agent. Require citations or file references. Hub compares evidence and writes the final answer.

### Parallel Repo Sweep

Assign one repo per agent. Require before/after `git status`, audit/test output, and a clear commit boundary. Hub verifies pushes and CI.

### Builder + Reviewer

Builder writes scoped changes. Reviewer is read-only and reports findings only. Hub decides what to apply.

### Research + Implementation Pipeline

Researcher identifies constraints. Hub accepts design boundary. Builder implements. Reviewer/tester verifies. Hub releases.

### Long-Running Monitor

Use for CI, deploys, imports, media generation, or external jobs. Set timeout and final handoff. Do not leave monitors ownerless.

## Status Language

Good updates are concrete:

- "I split this into API research, repo implementation, and read-only review. The builder owns `src/importer/*`; nobody else will write there."
- "The implementation is in, review found one real edge case, and I am running final tests now."
- "CI failed in deploy because secrets are missing; build itself passed. I am not changing secrets without approval."

Avoid orchestration theater:

- Do not claim agents are working if no task was actually launched.
- Do not present activity as completion.
- Do not hide failed or skipped validation.

## Templates

Use bundled templates when useful:

- `templates/agent-brief.md` for launching subagents.
- `templates/hub-state.json` for resumable multi-agent runs.
- `templates/final-report.md` for final synthesis.

## Final Report

For substantial orchestrated work, finish with:

- What shipped or changed
- Workstreams/agents used
- Validation results
- Commits, PRs, release links, or artifacts
- Residual risks and blocked items
- Next follow-up only if it genuinely builds on the request
