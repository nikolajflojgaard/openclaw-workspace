---
name: "gog-oauth-recovery"
description: "Recover gog Google Workspace OAuth after invalid_grant failures."
---

# gog OAuth Recovery

Use this when a workflow using `gog` fails with auth errors such as `invalid_grant`, expired token, revoked token, missing refresh token, or Google Drive auth failure.

## Defaults For Nikolaj's Workspace

- Default account: `nikolaj.floejgaard@gmail.com`
- Current work Drive services: `docs,drive,sheets`
- Drive sweep repo: `/Users/nikolajflojgaard/.openclaw/workspace/work-architecture-playbook`
- Drive sweep command: `python3 scripts/sync_drive_specs.py`
- The common failed cron is the Google Drive folder sweep for `General designs` and `API spec drop/YAML` to PDF.

## Recovery Workflow

1. Confirm the failure is an OAuth/token failure.
   - Look for `invalid_grant`, `expired`, `revoked`, `refresh token`, `auth token`, or `unauthorized_client`.
   - Do not use this skill for ordinary file-not-found, permission, render, YAML, Chrome, or network failures.

2. Inspect current auth state.

   ```bash
   gog auth status
   gog auth list
   ```

3. Re-authorize the account using the existing stored OAuth client credentials.

   ```bash
   gog auth add nikolaj.floejgaard@gmail.com --services docs,drive,sheets
   ```

   If the user explicitly needs Gmail/Calendar too, include the extra services:

   ```bash
   gog auth add nikolaj.floejgaard@gmail.com --services gmail,calendar,drive,contacts,docs,sheets
   ```

4. If `gog auth add` reports an existing broken token and does not overwrite it cleanly, remove only the broken token for the affected account, then add it again.

   ```bash
   gog auth remove nikolaj.floejgaard@gmail.com
   gog auth add nikolaj.floejgaard@gmail.com --services docs,drive,sheets
   ```

   Only remove the token when re-adding failed or the token is clearly unusable. Do not remove client credentials unless the user explicitly asks.

5. Handle browser or consent prompts.
   - If a local browser opens and the account can be selected/approved without needing secrets from the user, proceed.
   - If Google asks for a password, 2FA, passkey approval, CAPTCHA, or account choice that cannot be completed safely, message Nikolaj with the exact prompt and wait.
   - Do not ask Nikolaj for his Google password or 2FA code. Let him complete the Google prompt directly.

6. Verify Drive access with a small read-only command.

   ```bash
   gog drive ls --parent 1jfj6EqzSsUsyA2_cz6ui2PeObZaTyanD --max 1 --json --no-input -a nikolaj.floejgaard@gmail.com
   ```

7. Rerun the originally failed workflow once.

   For the scheduled Drive folder sweep:

   ```bash
   cd /Users/nikolajflojgaard/.openclaw/workspace/work-architecture-playbook
   python3 scripts/sync_drive_specs.py
   ```

8. Report the outcome briefly.
   - If auth is fixed and the workflow returns `no_changes`, say auth is fixed and the sweep found no new files.
   - If files were processed, summarize the file names and actions.
   - If auth still fails, include the exact failing command and the compact error.

## Safety Rules

- Do not exfiltrate OAuth tokens, client secrets, refresh tokens, keychain entries, or credential files into chat.
- Do not delete broad Google credentials or unrelated account tokens.
- Do not use `--no-input` for the re-auth command; it must be allowed to open the OAuth browser flow.
- Use `--no-input` for verification and scripted Drive commands after auth is restored.
- Do not send emails, create calendar events, edit Drive contents, or upload files unless that was the original failed workflow or the user explicitly asks.

## Quick Triage Commands

```bash
gog auth status
gog auth list
gog drive ls --parent 1jfj6EqzSsUsyA2_cz6ui2PeObZaTyanD --max 1 --json --no-input -a nikolaj.floejgaard@gmail.com
```

If those pass, the token is usable for the Drive sweep.
