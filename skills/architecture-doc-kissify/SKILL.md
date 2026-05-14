---
name: architecture-doc-kissify
description: Review enterprise integration/API/microservice/workflow design documents, especially consultant-written DLDs or solution docs, and rewrite them into clearer, shorter, KISS-style architecture markdown. Use when the user shares architecture proposals, design docs, Word/Confluence exports, diagrams, or requirements and wants a blunt review, simplification, target architecture, or cleaner .md documentation for work.
---

# Architecture Doc Kissify

Use this skill when Nikolaj shares architecture/design material from work and wants it:
- reviewed critically
- simplified aggressively
- rewritten as better `.md`
- turned into practical architecture docs instead of consultant fog

This skill is for **job architecture work**, not generic writing cleanup.

## Core stance

Default to:
- keep it simple
- challenge unnecessary components
- separate lookup, command, workflow, and event patterns
- align to the actual platform baseline
- prefer architecture clarity over document completeness theater

Blunt rule:

**If a simple integration is dressed up like a distributed systems PhD thesis, cut it down.**

## Known platform baseline

Assume these are standing constraints unless Nikolaj says otherwise:
- Azure APIM is the API platform for internal and external APIs
- TDC NET Ping token and OAuth2 are the security baseline
- Kafka runs on-prem
- Artemis runs on-prem
- this setup is baseline reality, not something to casually redesign

Use this baseline when evaluating or reshaping designs.

## What to do when a design doc arrives

### 1. Identify the true interaction types
Classify each operation as one of:
- synchronous lookup API
- synchronous command/state change
- asynchronous command or event
- workflow/orchestration
- data projection / bulk retrieval

Do not let one document blur them together.

### 2. Find pattern confusion fast
Look specifically for contradictions like:
- “synchronous request/response” plus Kafka in the critical path
- workflow language with no real process state
- microservice split with no real domain ownership
- messaging added because platform exists, not because behavior needs it
- NFR sections that are placeholders pretending to be decisions

Call these out clearly.

### 3. Review against KISS
Ask:
- what is the smallest architecture that still preserves correctness?
- which components are actually required?
- what is just enterprise decoration?
- what would fail if we removed Kafka / BPMN / extra services / extra hops?

### 4. Recommend a cleaner target shape
Default heuristics:
- real-time lookups → synchronous API + direct downstream call path
- state changes → synchronous command in, optional async side effects only if justified
- workflow only if waits/timers/manual tasks/compensations actually exist
- Kafka only when event propagation or replay really matters
- Artemis only when point-to-point async task delivery is the right pattern

### 5. Produce useful output
Depending on what Nikolaj asks for, generate one or more of:
- blunt review doc
- target architecture doc
- KISS rewrite of the original design
- short stakeholder summary
- red/yellow/green scorecard
- open questions / challenge list

## Preferred output shapes

### A. Review doc
Use when Nikolaj wants evaluation.

Recommended structure:
- Executive summary
- What is good
- What is weak
- Main architectural concerns
- Fit to platform baseline
- Questions to challenge
- Final recommendation

### B. Target architecture doc
Use when Nikolaj wants a better approach.

Recommended structure:
- Context
- Fixed platform assumptions
- Recommended pattern per operation
- Service responsibilities
- Security/trust boundary
- Kafka/Artemis guidance
- Sequence diagrams
- Final recommendation

### C. KISS design rewrite
Use when the original doc is too bloated.

Recommended structure:
- Purpose
- Scope
- Recommended integration pattern
- Runtime flow
- Security
- API operations
- Error handling
- What is explicitly not needed
- Final recommendation

Keep this version short and readable.

## Mermaid guidance

Prefer Mermaid only when it adds clarity.

Good candidates:
- context diagram
- synchronous API sequence
- async command sequence
- workflow sequence

Do not over-diagram trivial logic.

## Tone and style

Write like an internal architect, not a consultant.

That means:
- plain language
- direct conclusions
- explicit tradeoffs
- minimal fluff
- no fake certainty
- no “comprehensive” theater unless the complexity is real

## File handling guidance

When saving output:
- reusable templates belong in `Documents/architecturalTemplates/`
- actual case work belongs in `Documents/architectureWork/active/`
- rough early concepts can go in `Documents/architectureWork/ideas/`

Use descriptive file names tied to the initiative/system names.

## Default challenge questions

Use these when pressure-testing designs:
- Is this really synchronous, async, or mixed?
- Why is each technology present?
- Is Kafka/Artemis actually needed here?
- Does APIM remain the obvious front door?
- What does the microservice truly own?
- Are we adding network hops for real value?
- Is the error model aligned to the actual runtime pattern?
- Are the NFRs real or placeholders?
- Could this be explained more simply without losing correctness?

## Success criteria

A good result should:
- be shorter than the original design doc
- be clearer about runtime pattern
- remove unjustified complexity
- align to the actual TDC NET platform baseline
- give Nikolaj something he can use in architecture discussions immediately
