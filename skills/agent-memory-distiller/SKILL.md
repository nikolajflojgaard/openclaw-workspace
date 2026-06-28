---
name: "agent-memory-distiller"
description: "Distill recent notes, commits, chats, and outcomes into compact long-term memory updates."
---

# Agent Memory Distiller

Use this skill when recent activity needs to be reviewed for durable memory, or when `MEMORY.md` needs cleanup without turning it into a junk drawer.

Daily notes are raw. Long-term memory is curated. The goal is not to remember everything. The goal is to preserve the few facts that will improve future behavior.

## Memory Layers

- **Working memory**: current conversation and active task state. Do not persist unless it matters later.
- **Daily notes**: `memory/YYYY-MM-DD.md`. Raw chronology, decisions, experiments, failures, fixes, and observations.
- **Long-term memory**: `MEMORY.md`. Stable preferences, durable project context, recurring workflows, standing decisions, and lessons worth keeping.

## Default Workflow

1. **Set scope**
   - Default to recent daily notes, usually the last 3-7 days.
   - Include yesterday only when today's note or the task suggests continuity.
   - Include commits, chats, or repo outcomes only when they materially explain the memory candidate.
   - Avoid loading all memory history unless cleanup requires it.

2. **Collect raw inputs**
   Prefer the bundled read-only packet generator:

   ```bash
   python3 scripts/agent_memory_distiller.py packet <workspace> --days 7 --out /tmp/memory-distillation.md
   ```

   Add repos when commits matter:

   ```bash
   python3 scripts/agent_memory_distiller.py packet <workspace> --repo <repo> --days 7 --out /tmp/memory-distillation.md
   ```

3. **Extract candidates**
   Look for:
   - stable user preferences
   - durable project context
   - repeated workflows or rules
   - decisions likely to matter again
   - lessons from mistakes or debugging
   - recurring people, systems, repos, or schedules
   - contradictions or stale long-term memory

4. **Reject noise**
   Do not promote:
   - one-off task logs
   - transient status
   - raw command output
   - speculative ideas that have not hardened
   - secrets, tokens, credentials, or sensitive personal data
   - details already captured better elsewhere

5. **Draft an update plan before editing**
   Produce:
   - `promote`: bullets to add or revise in `MEMORY.md`
   - `remove`: stale or duplicate bullets to delete
   - `keep_daily_only`: useful raw context that should not become long-term memory
   - `privacy_flags`: sensitive items to avoid or redact
   - `no_change`: explicit reason when nothing should be promoted

6. **Edit long-term memory only when justified**
   - Keep `MEMORY.md` compact.
   - Prefer concrete bullets over paragraphs.
   - Capture the implication, not just the event.
   - Preserve existing wording when it is already good.
   - Remove duplicates and stale facts in the same pass.

7. **Update system files when behavior should change**
   If the lesson is a standing rule, update the right control file instead of burying it in memory:
   - `AGENTS.md` for agent behavior
   - `TOOLS.md` for local setup and tool notes
   - a skill file for reusable workflow changes
   - `MEMORY.md` for stable context and preferences

8. **Rebuild retrieval index after significant changes**
   When the workspace uses a local memory index, run:

   ```bash
   python3 scripts/memory_index.py
   ```

   Skip this if no meaningful long-term memory changed.

## No-Change Reports

Say no when nothing deserves promotion. A good no-change report names:

- inputs reviewed
- why candidates were rejected
- whether any privacy-sensitive items were avoided
- whether index rebuild was skipped

## Privacy Rules

- Do not copy secrets into memory.
- Do not promote private third-party details unless explicitly useful and appropriate.
- Do not expose long-term memory in group chats or shared contexts.
- Report sensitive findings by type and location only.
- Prefer project-level facts over personal details when both would work.

## Cleanup Rules

Remove or revise long-term memory when it is:

- contradicted by newer decisions
- duplicated elsewhere
- too operational or temporary
- no longer useful for future behavior
- sensitive beyond its utility
- better represented as a skill, tool note, or control-file rule

## Output Shape

Use `templates/memory-update-plan.md` for proposed edits.
Use `templates/no-change-report.md` when nothing should change.
Use `templates/review-checklist.md` before editing `MEMORY.md`.

## Quality Bar

Good memory is:

- stable
- reusable
- decision-relevant
- compact
- privacy-aware
- easier to retrieve than rediscover

Bad memory is:

- a transcript
- a build log
- vague sentiment
- stale task state
- duplicated instructions
- secrets or sensitive personal context without a clear need
