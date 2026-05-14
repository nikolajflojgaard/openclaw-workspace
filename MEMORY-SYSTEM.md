# MEMORY-SYSTEM.md

A practical memory system for Jason.

## Goal

Remember what matters without turning memory into a junk drawer.

## Memory layers

### 1. Working memory
Current conversation and immediate task state.

Use for:
- active decisions
- current constraints
- in-flight work
- temporary context

Do not try to persist this mentally. If it matters after the session, write it down.

### 2. Episodic memory
Daily notes in `memory/YYYY-MM-DD.md`.

Use for:
- what happened today
- decisions made
- experiments tried
- failures, fixes, and observations
- small but potentially useful facts

This is the raw log. It can be messy.

### 3. Semantic memory
Curated long-term memory in `MEMORY.md`.

Use for:
- stable preferences
- identity facts
- recurring workflows
- durable project context
- standing instructions
- lessons worth keeping

This is the distilled layer. Keep it short and high-signal.

## Promotion rules

Promote from daily notes to `MEMORY.md` only if the information is:
- likely to matter again
- stable enough to survive beyond one day
- useful for future decisions or writing

Do not promote:
- one-off chatter
- transient emotions unless explicitly relevant
- noisy logs
- speculative ideas that have not hardened into preference or direction

## Retrieval rules

Before answering from memory:
1. check the curated layer first when the question is about preferences, prior decisions, or recurring setup
2. check recent daily notes for recency and nuance
3. prefer specific facts over vibes
4. say when confidence is low

## Writing rules for memory

When storing memory:
- write concrete facts, not vague impressions
- prefer bullets over paragraphs
- capture the implication, not just the event
- store the why when it matters

Bad:
- Nikolaj liked the thing.

Better:
- Nikolaj prefers short, ruthless daily briefings over broad summaries.

## Memory maintenance

Every few days:
- review recent daily notes
- merge repeated patterns into `MEMORY.md`
- remove stale or redundant long-term memory
- keep the system compact enough to stay useful

## Behavioral rule

If a lesson should change future behavior, update the system, not just the notes.

That means:
- add the durable fact to `MEMORY.md`
- add workflow guidance to `AGENTS.md` or another control file when needed
- do not rely on “I’ll remember that”

## Current design preference

Default to a human memory model:
- raw log layer
- curated long-term layer
- selective promotion
- retrieval before response
- periodic distillation

Avoid the naive model where every fact is treated as equally important.
