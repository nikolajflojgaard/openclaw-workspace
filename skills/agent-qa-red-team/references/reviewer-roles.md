# Reviewer Roles

Use these role notes when briefing a specialized QA or red-team lane.

## Code QA

Focus on behavior, correctness, edge cases, regressions, compatibility, and tests. Prefer `git diff`, failing paths, and local validation evidence. Do not refactor during review.

## Docs QA

Focus on false claims, missing diagrams, broken links, wrong commands, stale setup steps, and generated-doc drift. Check whether docs tell an operator or future engineer what they need to know.

## Security / Privacy

Focus on secret exposure, credential handling, public side effects, auth boundaries, filesystem scope, dangerous commands, and private-data leakage. Report sensitive values by file path and type only.

## Validation QA

Focus on whether the claimed validation matches the risk. Look for commands that were skipped, failed, run in the wrong directory, or did not cover generated artifacts. Check CI/deploy status after pushes.

## Reasoning Red Team

Focus on unsupported assumptions, inflated claims, missing uncertainty, scope creep, tool-output misreads, and time-sensitive facts that were not verified.

## Release QA

Focus on branch state, dirty worktrees, commits, tags, pushed remotes, CI runs, deploy logs, release artifacts, and whether public actions were approved.

## Memory QA

Focus on whether a note is durable, compact, privacy-safe, and stored in the right place. Daily notes can be raw. Long-term memory should be curated signal only.
