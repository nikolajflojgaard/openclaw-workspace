---
name: "context-resume-handoff"
description: "Resume and hand off long sessions when context reaches 50k tokens."
---

# Context Resume Handoff

Use this when the current session is getting large, context usage reaches about 50k tokens, compaction risk is high, or the user asks to preserve continuity before starting a new session.

## Trigger

Check for this skill when any of these are true:

- `session_status` or runtime usage shows roughly `>= 50000` tokens in the current session.
- The conversation is long enough that important active state may be lost in compaction.
- A tool/runtime warning says context is low, compaction is likely, or history was summarized.
- Nikolaj asks to resume, hand off, start fresh, preserve context, or continue in a new session.

If no token usage tool is available, use judgment. Prefer a handoff once the thread contains multiple active tasks, file edits, cron changes, approvals, or unresolved external state.

## Procedure

1. Inspect current session state when tools are available.

   ```text
   session_status({"sessionKey":"current"})
   get_goal()
   ```

   Use `sessions_history` only if needed to recover recent facts that are not already in working context. Keep it small.

2. Build a concise resume package. Include only information needed to continue acting correctly.

   Required sections:

   - **Current Objective**: what Nikolaj most recently asked for and what remains.
   - **Active Decisions/Preferences**: durable preferences or constraints from this session.
   - **Completed Work**: concrete changes already made, including file paths, cron IDs, skill proposal IDs, commits, or external state.
   - **Pending Work**: unfinished tasks, blockers, approvals, failed commands, and next commands.
   - **Touched Files/State**: local files edited, new state files, cron jobs, and skills applied/proposed.
   - **Verification**: tests/checks already run and their outcomes.
   - **Cautions**: privacy, secrets, external actions, user approvals, or things not to repeat.
   - **Next Action**: the first thing the new session should do.

3. Persist the handoff if the state is durable.

   - For ordinary active work, write a compact note to today's `memory/YYYY-MM-DD.md`.
   - For substantial active work, create `memory/session-resumes/YYYY-MM-DD-HHMM.md` and link/summarize it from the daily note.
   - Do not store secrets, OAuth tokens, private message contents beyond what is needed, or large raw transcripts.

4. Tell Nikolaj briefly that a fresh continuation is being started.

   In Telegram/direct chat, use the visible message tool if normal final replies are not auto-delivered. Keep it short:

   ```text
   Context is getting heavy, so I saved a handoff and started a fresh continuation session. I’ll continue from there with the active state preserved.
   ```

5. Start a fresh session when session tools are available.

   Use `sessions_spawn` with isolated context and include the resume package as the first task. Prefer a stable task name if available.

   Example task:

   ```text
   Continue Nikolaj's active work as Jason. First read the workspace startup files required by AGENTS.md. Then use this handoff as current state:

   <resume package>

   Continue with the Next Action. Do not restart completed work. Preserve privacy and ask before external actions that need human approval.
   ```

   Use `context: "isolated"` unless the child truly needs the full transcript. The resume should be enough.

6. Stop doing substantial work in the old session after spawning the continuation.

   The old session may send a short visible pointer to Nikolaj, but do not split active implementation across old and new sessions.

## Resume Quality Bar

A good resume lets the next session act without rereading the whole transcript. It must include IDs and paths exactly when they matter.

Prefer specifics:

- `cron job 69da8ece-57d7-424b-8bf1-1089a740b791`
- `scripts/evdrive_fsd_monitor.py`
- `Skill Workshop proposal gog-oauth-recovery-20260615-27837b18c8 applied`
- `memory/2026-06-15.md updated`

Avoid vague summaries like “we discussed cars” or “some files changed”.

## Safety Rules

- Do not include secrets, tokens, OAuth refresh tokens, passwords, API keys, private message dumps, or unnecessary personal data in the resume.
- Do not claim the new session is active unless `sessions_spawn` or equivalent succeeded.
- If session spawning fails, save the resume and tell Nikolaj the handoff is saved but a new session could not be started.
- If the user is in a group/shared context, do not include private main-session memory in visible messages.
- Do not mark goals complete just because the session is being handed off.
