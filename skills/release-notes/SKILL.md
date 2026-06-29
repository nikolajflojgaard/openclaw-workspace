---
name: "release-notes"
description: "Turn git changes into human release notes and changelogs."
---

# Release Notes

Use this skill when preparing release notes for apps, sites, repos, internal tools, automations, or public changelogs.

## Workflow

1. Determine audience: end users, developers, maintainers, operators, or private owner summary.
2. Gather evidence: commits, PR titles, issue links, diff summary, package changes, migrations, config changes, screenshots, and validation commands.
3. Group changes by user impact, not by commit chronology.
4. Separate added, changed, fixed, removed, security, performance, operational, and known issues when relevant.
5. Translate technical commits into plain outcomes.
6. Include upgrade or operator notes only when action is required.
7. Run humanizer-style cleanup for public prose.
8. State validation honestly; never imply a release happened unless it was actually tagged, pushed, deployed, or published.

## Evidence Commands

Use the repo's context, such as:

```bash
git status --short
git log --oneline --decorate <base>..HEAD
git diff --stat <base>..HEAD
git diff --name-only <base>..HEAD
gh pr view --json title,body,commits,files,closingIssuesReferences,statusCheckRollup
```

Adjust commands to the repo and do not run `gh` if auth is unavailable or unnecessary.

## Output Shapes

Short release note:

- `Highlights`
- `Fixes`
- `Operational Notes`
- `Validation`
- `Known Issues`

Detailed changelog:

- version/date
- audience
- grouped changes
- breaking changes
- migration steps
- security notes
- validation evidence
- contributors or PR references if appropriate

## Quality Rules

- Do not expose private commit details in public copy.
- Do not include noisy refactors unless they affect users or operators.
- Preserve exact version numbers, dates, and migration commands.
- Be blunt about incomplete validation.
- If release notes are for Nikolaj's public writing, strip AI cadence and marketing fluff.

## Guardrails

- Do not tag, push, publish, or create GitHub releases unless explicitly asked.
- Do not fabricate issue links, PR numbers, or deployment status.
- If the workspace is dirty, distinguish shipped commits from uncommitted local changes.
