---
name: "host-restart"
description: "Harden restart script with exact args and safe check mode."
---

# Host Restart

Use this skill when Nikolaj asks to restart the machine this agent is currently running on.

## Safety Rules

- Treat a host restart as disruptive. Do not run the reboot command unless the current user message explicitly confirms the restart now.
- If the user asks to create, inspect, plan, test, check, validate, or add a restart handle, run only the safe check path. Do not restart.
- Never validate by appending fake flags to `--confirm`; the script accepts `--check` for non-disruptive validation.
- Never ask Nikolaj to paste a macOS/Linux login or sudo password into chat. Do not store passwords in files, memory, environment variables, or skill content.
- Preferred privilege model: a one-time sudoers rule granting passwordless access only to the exact shutdown command.
- Preferred post-reboot model: run OpenClaw via launchd/system service. Do not solve reboot recovery by storing the user's login password.
- Before restarting, send a short visible message that the machine is about to restart and that the agent may disconnect.
- Do not restart if active work is in progress, a deploy is running, or a long-running command/session is active unless the user explicitly says to restart anyway.
- Do not hide failures. If permissions block restart or post-reboot availability is uncertain, say that clearly and provide the exact local setup command Nikolaj can run.

## One-Time Restart Setup

If restart is blocked by non-interactive sudo, recommend this local setup instead of asking for a password in chat.

On macOS for user `nikolajflojgaard`:

```bash
tmp=$(mktemp)
printf '%s\n' 'nikolajflojgaard ALL=(root) NOPASSWD: /sbin/shutdown -r now' > "$tmp"
sudo visudo -cf "$tmp" && sudo install -m 0440 "$tmp" /private/etc/sudoers.d/openclaw-host-restart
rm -f "$tmp"
sudo -n -l /sbin/shutdown
```

On Linux, use the same pattern but install to `/etc/sudoers.d/openclaw-host-restart`; verify the shutdown path first with `command -v shutdown` and use that exact path in the sudoers rule.

## Post-Reboot Availability

Restart permission and login recovery are separate problems.

- Do not ask for or store the macOS login password.
- If FileVault blocks boot at the disk-unlock screen, OpenClaw cannot return until the Mac is unlocked. For planned restarts, Nikolaj may use macOS authenticated restart locally; do not automate it by storing passwords.
- If the Mac reaches the user session, OpenClaw should return through its launchd agent. Current expected gateway LaunchAgent path: `/Users/nikolajflojgaard/Library/LaunchAgents/ai.openclaw.gateway.plist`.
- To verify launchd recovery before restart, run:

```bash
launchctl print gui/$(id -u)/ai.openclaw.gateway
```

- If Nikolaj wants OpenClaw available before interactive login, treat that as a separate service-hardening task: convert the relevant OpenClaw component to a root LaunchDaemon with minimal environment and secrets, then test reboot recovery. Do not use auto-login or password files as the default solution.

## Preflight

1. Confirm the target is the local host running this agent, not a remote machine.
2. Check current OS:
   - macOS: `uname -s` returns `Darwin`.
   - Linux: `uname -s` returns `Linux`.
3. Check obvious active work:
   - `pgrep -fl "astro|vite|next|npm|pnpm|yarn|gh|git|rsync|ftp|node"`
   - Treat OpenClaw's own `node`/`openclaw` processes as expected, not active deploy work.
   - `git -C /Users/nikolajflojgaard/.openclaw/workspace status --short` when relevant.
4. Check non-interactive sudo readiness:
   - Preferred: `scripts/restart_host.sh --check`
   - macOS fallback: `sudo -n -l /sbin/shutdown`
   - Linux fallback: `sudo -n -l /sbin/shutdown` or the exact path returned by `command -v shutdown`.
5. Check post-reboot recovery path:
   - macOS user LaunchAgent: `launchctl print gui/$(id -u)/ai.openclaw.gateway`
   - If this fails, warn that OpenClaw may not come back automatically after login.
6. If active work exists, summarize it and ask whether to restart anyway.
7. If sudo readiness fails, stop and send the one-time restart setup instructions. Do not try interactive sudo.

## Restart Commands

Safe check:

```bash
scripts/restart_host.sh --check
```

Actual restart, only after explicit confirmation:

```bash
scripts/restart_host.sh --confirm
```

Manual fallback:

- macOS: `sudo -n /sbin/shutdown -r now`
- Linux systemd: `sudo -n /sbin/shutdown -r now` or `sudo -n /usr/sbin/shutdown -r now` if that is the system path.

If `sudo -n` fails because the sudoers rule is missing, stop and tell Nikolaj to run the one-time setup. Do not ask for or accept the password in chat.

## Flow

1. If the request is ambiguous, ask one concise confirmation question.
2. If confirmed, run preflight using `scripts/restart_host.sh --check`.
3. If preflight is clear and sudo readiness passes, send a visible warning message.
4. Run the restart command through `scripts/restart_host.sh --confirm`.
5. Expect the session to disconnect; do not claim success unless the command returns before disconnecting.
