---
name: "secure-code-review"
description: "Review code for security risks before shipping changes."
---

# Secure Code Review

Use this skill when reviewing code that handles auth, secrets, user data, file operations, network calls, subprocesses, webhooks, browser automation, LLM/tool orchestration, or public-facing endpoints.

## Default Posture

- Findings first.
- Reproduce or point to exact evidence.
- Prefer small defensive changes over broad rewrites.
- Report secrets by type/path only; never paste secret values.
- Treat third-party skills, MCP servers, shell installers, and browser automation as untrusted until checked.

## Review Workflow

1. Define scope: diff, files, endpoint, automation, dependency, or proposed external skill.
2. Map trust boundaries: users, services, secrets, local files, network, subprocesses, generated content, and public outputs.
3. Inspect dangerous surfaces: auth, authorization, input validation, SSRF, path traversal, command injection, deserialization, XSS, CSRF, SQL/NoSQL injection, file uploads, redirects, webhook verification, logging, and error leakage.
4. For agent systems, inspect prompt injection, tool-call authorization, secret redaction, external-message sending, browsing, local file reads, and approval gates.
5. Check dependencies and install instructions for curl-pipe-shell, global installs, auto-updates, telemetry, credential reads, and postinstall scripts.
6. Verify mitigations with tests, static checks, config review, or targeted repros where practical.
7. Report findings by severity with concrete patches or controls.

## Report Format

Return:

- `status`: pass, needs-fixes, blocked, or high-risk
- `scope`
- `trust_boundaries`
- `findings`: severity, evidence, impact, fix, confidence
- `tests_or_checks`
- `residual_risk`
- `activation_recommendation`: for third-party skills/tools only

## Severity Guide

- `critical`: likely secret exposure, remote code execution, auth bypass, destructive external action, or public data leak.
- `high`: exploitable injection, missing authorization, unsafe default, unverified webhook, dangerous installer, or broad credential exposure.
- `medium`: weak validation, missing rate limits, insufficient logging redaction, risky dependency, or incomplete test coverage.
- `low`: hardening, clarity, or defense-in-depth improvement.

## Guardrails

- Do not run exploit payloads against systems you do not own.
- Do not install unknown packages globally just to inspect them.
- Do not publish vulnerability details externally without explicit approval.
- If a secret may be exposed, stop quoting output and report only path/type.
