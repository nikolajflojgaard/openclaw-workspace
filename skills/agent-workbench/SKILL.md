---
name: "agent-workbench"
description: "Turn messy requests into scoped agent workbench runs with lanes, briefs, state, gates, and reports."
---

# Agent Workbench

Use this skill when a request is too messy to execute directly and needs to be shaped into lanes, briefs, state, gates, and a final report before or during agent work.

The workbench is not a planning ceremony. It is an execution packet: enough structure to keep the work moving without losing ownership, validation, or privacy boundaries.

## Relationship To The Hub

- Use `agent-orchestration-hub` to decide whether multiple agents are worth using.
- Use this skill to create the concrete workbench run the hub operates from.
- Keep the main agent accountable for scope, privacy, validation, external actions, commits, pushes, and final claims.
- Treat every generated brief as draftable; tighten it before launching an agent.

## Default Workflow

1. **Capture the request**
   - Preserve the user's actual objective.
   - Identify deliverables, constraints, repositories, files, external side effects, and validation needs.
   - Mark unknowns without stopping unless the unknown makes execution unsafe.

2. **Choose lanes**
   Use the smallest lane set that covers the work:
   - `Intake`: clarify objective, acceptance criteria, constraints, and non-goals.
   - `Map`: inspect repos, docs, APIs, systems, prior memory, or source material.
   - `Design`: define structure, contracts, data flow, UI flow, or implementation plan.
   - `Build`: write scoped code, docs, assets, or proposals.
   - `Review`: read-only bug, security, quality, and missing-validation pass.
   - `Test`: run validation, reproduce failures, check generated artifacts, or inspect screenshots.
   - `Release`: commit, publish, deploy, or watch CI after approval.
   - `Monitor`: wait on CI, external jobs, approvals, or scheduled follow-ups.

3. **Set ownership**
   - One writer per file or repo surface.
   - Review and test lanes are read-only by default.
   - Release lanes do not change implementation unless explicitly promoted.
   - External/public actions require explicit approval unless the user already authorized them.

4. **Create the run packet**
   Prefer the bundled CLI for a deterministic scaffold:

   ```bash
   python3 scripts/agent_workbench.py create "<request>" --output .workbench/<slug>
   ```

   Add explicit lanes when the shape is known:

   ```bash
   python3 scripts/agent_workbench.py create "<request>" \
     --lane "Build:Implement scoped changes:writes src and tests" \
     --lane "Review:Find bugs and missing validation:read-only" \
     --output .workbench/<slug>
   ```

5. **Tighten briefs**
   For each brief, ensure it includes:
   - objective
   - relevant context
   - scope and non-goals
   - write permissions
   - privacy boundaries
   - expected output
   - validation
   - stop conditions

6. **Run the work**
   - Use the hub's orchestration rules for launching agents.
   - Update `state.json` as lanes move from `pending` to `running`, `blocked`, `needs-review`, `done`, or `discarded`.
   - Record artifacts with path, owner, purpose, and whether the hub verified them.
   - Keep user updates short and concrete during long work.

7. **Gate before release**
   Complete `gate-checklist.md` before claiming work shipped:
   - request matched
   - user changes preserved
   - write ownership respected
   - validation run or gap stated
   - secrets/private data protected
   - external actions approved
   - CI/deploy checked when relevant

8. **Report**
   Finish with:
   - what changed or shipped
   - lanes/agents used
   - validation run
   - commits, links, artifacts, or proposals
   - residual risks and blocked items
   - next action only when it naturally follows

## Lane Sizing Rules

- Use one lane when a task is mostly linear.
- Use builder-reviewer for serious code, docs, security, release, or memory changes.
- Use fan-out when repos, files, sources, or systems are independent.
- Use a monitor lane for CI, deployments, media jobs, approvals, or delayed imports.
- Avoid splitting work so much that coordination becomes the work.

## Dirty Worktree Rules

- Check status before assigning write lanes.
- Do not reset, clean, checkout, or overwrite unrelated user changes.
- If a repo is dirty, either scope the write lane around existing changes or stop and report the conflict.
- Commit only the files owned by the run.

## State Discipline

Keep `state.json` compact. It should answer:

- what are we trying to do?
- which lanes exist?
- who owns what?
- what artifacts matter?
- what gates remain?
- what is blocked?

Do not turn state into a diary. Put durable lessons in memory files only when they matter later.

## CLI

The bundled script is intentionally local and boring:

```bash
python3 scripts/agent_workbench.py create "<request>" --output <dir>
python3 scripts/agent_workbench.py create "<request>" --lane "Name:Goal:Writes" --output <dir>
```

It writes a scaffold only. It does not spawn agents or perform external actions.

## Templates

- `templates/brief.md` - agent brief template
- `templates/workbench-state.json` - compact run state template
- `templates/gate-checklist.md` - release gate checklist
- `templates/final-report.md` - final report scaffold
