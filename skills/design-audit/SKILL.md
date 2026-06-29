---
name: "design-audit"
description: "Review UI work against practical product-design quality gates."
---

# Design Audit

Use this skill when reviewing or final-polishing user-facing frontend work, especially apps, dashboards, tools, marketing pages, and visual prototypes.

## Default Posture

- Findings first, praise only when useful.
- Judge the product in its likely user context, not as generic Dribbble UI.
- Prefer concrete fixes over taste commentary.
- Treat layout stability, readable hierarchy, and interaction clarity as release quality, not decoration.
- Verify with screenshots when a runnable UI exists.

## Audit Workflow

1. Establish the surface: app type, target user, primary workflow, route/screen list, and expected device sizes.
2. Inspect implementation: component structure, CSS tokens, spacing system, typography, color usage, state handling, and accessibility affordances.
3. Capture evidence: screenshots at desktop and mobile widths, browser console, rendered states, and relevant file/line references.
4. Score the UI across the gates below.
5. Report prioritized findings with impact and exact remediation.
6. Re-check after fixes when changes are made.

## Quality Gates

- Task fit: the first screen supports the user's actual workflow, not a generic landing page unless explicitly requested.
- Information hierarchy: headings, labels, actions, and density match the domain and screen context.
- Layout integrity: no overlapping text, clipped controls, unstable hover states, or content that shifts unexpectedly.
- Responsive behavior: mobile and desktop both preserve workflow, tap targets, spacing, and readable text.
- Interaction states: loading, empty, error, disabled, focus, hover, selected, and success states are covered where relevant.
- Accessibility: semantic controls, keyboard reachability, visible focus, color contrast, labels, and reduced-motion respect.
- Visual system: colors, spacing, radius, shadows, and icons feel coherent without becoming one-note.
- Product polish: copy is terse, controls use familiar icons when appropriate, and repeated elements scan quickly.

## Report Format

Return:

- `status`: pass, needs-fixes, or blocked
- `scope`: screens/files reviewed
- `findings`: ordered by severity with evidence and fix
- `validation`: screenshots, commands, viewport sizes, and gaps
- `quick_wins`: small high-leverage changes
- `residual_risk`: what still needs human judgment

## Guardrails

- Do not redesign unrelated surfaces.
- Do not introduce decorative clutter to make a page feel fuller.
- Do not use stock design rules blindly; connect each recommendation to the product's actual use.
- If the UI cannot run locally, state that the audit is code/static only.
