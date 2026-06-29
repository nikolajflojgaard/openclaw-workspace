---
name: "vendor-evaluation"
description: "Evaluate tools/vendors with claim checks and weighted criteria."
---

# Vendor Evaluation

Use this skill when deciding whether to adopt, pay for, integrate, or activate a tool, vendor, API, plugin, MCP server, or third-party skill collection.

## Workflow

1. Define the job-to-be-done and the decision deadline.
2. List candidates and the current default option, including "do nothing".
3. Define weighted criteria: capability fit, workflow fit, security/privacy, data ownership, reliability, operational burden, integration effort, lock-in, cost, support, and exit path.
4. Gather evidence from official docs, pricing, changelogs, repos, issues, status pages, security docs, and hands-on trials where practical.
5. Separate vendor claims from verified facts.
6. Identify risks: external data transfer, credential scope, public actions, auto-updates, install scripts, telemetry, missing export, and unclear licensing.
7. Score candidates and explain the tradeoffs.
8. Recommend adopt, trial, defer, reject, or build internally.

## Output Shape

Return:

- `decision_context`
- `criteria_weights`
- `candidate_table`
- `verified_evidence`
- `claim_checks`
- `risk_register`
- `cost_model`
- `recommendation`
- `trial_plan`
- `exit_plan`

## Quality Rules

- Prefer primary sources for current pricing, security, and API claims.
- Use exact dates for pricing and product-state claims.
- Do not overvalue star counts or marketing pages.
- Include setup/maintenance cost, not just subscription price.
- For agent tools, inspect what the tool can read, write, execute, send, and auto-update.

## Guardrails

- Do not sign up, authorize OAuth, enter payment details, send emails, post externally, or install privileged tooling without explicit approval.
- Do not paste private data into vendor demos or public web forms.
- Treat unknown MCP servers, browser automation tools, and shell installers as high-risk until reviewed.
