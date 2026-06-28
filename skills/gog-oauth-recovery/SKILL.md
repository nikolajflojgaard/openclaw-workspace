---
name: "gog-oauth-recovery"
description: "Recover gog OAuth locally or by phone for headless Google Workspace use."
---

# gog OAuth Recovery

Use this when a workflow using `gog` fails with auth errors such as `invalid_grant`, expired token, revoked token, missing refresh token, Google Drive auth failure, or a missing headless keyring password.

## Defaults For Nikolaj's Workspace

- Default account: `nikolaj.floejgaard@gmail.com`
- Default services for Drive/spec workflows: `docs,drive,sheets`
- Full Google Workspace services when explicitly needed: `gmail,calendar,drive,contacts,docs,sheets`
- Drive verify parent: `1jfj6EqzSsUsyA2_cz6ui2PeObZaTyanD`
- Preferred headless wrapper: `/Users/nikolajflojgaard/.openclaw/workspace/scripts/gog-headless.sh`
- Preferred remote phone auth helper: `/Users/nikolajflojgaard/.openclaw/workspace/scripts/gog-remote-auth.sh`
- File keyring password path: `~/Library/Application Support/gogcli/keyring-password`
- Drive sweep repo: `/Users/nikolajflojgaard/.openclaw/workspace/work-architecture-playbook`
- Drive sweep command: `python3 scripts/sync_drive_specs.py`

## Decision Rule

Prefer the remote phone/browser flow when Jason is running headless, before desktop login, over Telegram, or whenever local browser auth is unavailable. Use local `gog auth add` only when a normal desktop browser session is available and safe.

## Quick Verification

Run this first when checking whether the token is already usable:

```bash
cd /Users/nikolajflojgaard/.openclaw/workspace
scripts/gog-remote-auth.sh --verify
```

If it prints `gog auth OK for nikolaj.floejgaard@gmail.com`, auth is working for the default Drive/Docs/Sheets scope.

## Remote Phone Recovery Flow

Use this flow when Nikolaj is away from the Mac or Jason cannot complete a local browser login.

1. Start the remote OAuth flow.

   ```bash
   cd /Users/nikolajflojgaard/.openclaw/workspace
   scripts/gog-remote-auth.sh --start
   ```

2. Send Nikolaj only the printed Google `auth_url` and ask him to open it on a signed-in phone/browser, approve access, and send back the final browser address beginning with `127.0.0.1:49428/oauth2/callback?...`.

3. Finish the flow with the returned redirect URL.

   ```bash
   cd /Users/nikolajflojgaard/.openclaw/workspace
   scripts/gog-remote-auth.sh --finish '<redirect-url-from-nikolaj>'
   ```

4. The helper verifies Drive access after exchanging the code. If verification passes, rerun the originally failed workflow once.

## Local Desktop Recovery Flow

Use this only when a local desktop browser session is available.

1. Confirm the failure is an OAuth/token failure.
   - Look for `invalid_grant`, `expired`, `revoked`, `refresh token`, `auth token`, `unauthorized_client`, or Drive auth errors.
   - Do not use this skill for ordinary file-not-found, permission, render, YAML, Chrome, or network failures.

2. Inspect current auth state.

   ```bash
   scripts/gog-headless.sh auth status
   scripts/gog-headless.sh auth list
   ```

3. Re-authorize the account using the existing stored OAuth client credentials.

   ```bash
   gog auth add nikolaj.floejgaard@gmail.com --services docs,drive,sheets
   ```

4. If `gog auth add` reports an existing broken token and does not overwrite it cleanly, remove only the broken token for the affected account, then add it again.

   ```bash
   scripts/gog-headless.sh auth remove nikolaj.floejgaard@gmail.com
   gog auth add nikolaj.floejgaard@gmail.com --services docs,drive,sheets
   ```

   Only remove the token when re-adding failed or the token is clearly unusable. Do not remove client credentials unless Nikolaj explicitly asks.

5. Handle browser or consent prompts.
   - If a local browser opens and the account can be selected/approved without needing secrets from Nikolaj, proceed.
   - If Google asks for a password, 2FA, passkey approval, CAPTCHA, or account choice that cannot be completed safely, message Nikolaj with the exact prompt and wait.
   - Do not ask Nikolaj for his Google password or 2FA code. Let him complete the Google prompt directly.

6. Verify Drive access.

   ```bash
   cd /Users/nikolajflojgaard/.openclaw/workspace
   scripts/gog-remote-auth.sh --verify
   ```

## Headless Wrapper Use

For scripted `gog` commands in headless contexts, use `scripts/gog-headless.sh` rather than bare `gog`. The wrapper loads `GOG_KEYRING_PASSWORD` from the local `0600` file-keyring password file so `gog` does not block on an interactive keyring prompt.

Example:

```bash
cd /Users/nikolajflojgaard/.openclaw/workspace
scripts/gog-headless.sh drive ls --parent 1jfj6EqzSsUsyA2_cz6ui2PeObZaTyanD --max 1 --json --no-input -a nikolaj.floejgaard@gmail.com
```

## Rerun The Failed Workflow

For the scheduled Drive folder sweep:

```bash
cd /Users/nikolajflojgaard/.openclaw/workspace/work-architecture-playbook
python3 scripts/sync_drive_specs.py
```

## Reporting

- If auth is fixed and the workflow returns `no_changes`, say auth is fixed and the sweep found no new files.
- If files were processed, summarize the file names and actions.
- If auth still fails, include the exact failing command and compact error.
- If remote phone approval is needed, send the auth URL and ask only for the final localhost redirect URL from the browser address bar.

## Safety Rules

- Do not exfiltrate OAuth tokens, client secrets, refresh tokens, keychain entries, keyring passwords, or credential files into chat.
- Never ask Nikolaj for his Google password, 2FA code, passkey, or recovery code.
- It is acceptable to receive the one-time localhost redirect URL from Nikolaj for `gog auth add --remote --step 2`; treat it as sensitive and use it only once.
- Do not delete broad Google credentials or unrelated account tokens.
- Do not remove client credentials unless Nikolaj explicitly asks.
- Use `--no-input` for verification and scripted Drive commands after auth is restored.
- Do not send emails, create calendar events, edit Drive contents, or upload files unless that was the original failed workflow or Nikolaj explicitly asks.

## Troubleshooting

If `gog` prompts for a keyring password in a headless session, use `scripts/gog-headless.sh` or `scripts/gog-remote-auth.sh`, not bare `gog`.

If the wrapper refuses the keyring password file due to permissions, fix the file mode locally before retrying:

```bash
chmod 600 ~/Library/Application\ Support/gogcli/keyring-password
```

If the remote flow times out, rerun `scripts/gog-remote-auth.sh --start` and send Nikolaj the fresh auth URL. Do not reuse an old redirect URL.
