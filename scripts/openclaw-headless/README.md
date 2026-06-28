# OpenClaw Headless LaunchDaemon Setup

This moves the core OpenClaw gateway and node host from user LaunchAgents to system LaunchDaemons that run as `nikolajflojgaard`.

What this solves:

- OpenClaw can start after FileVault unlock / user login and OS boot without relying on the old user LaunchAgent service.
- Telegram/backend/dev work can be available earlier.
- The process still runs as Nikolaj, not as root.

What this does not solve:

- Nothing can run before FileVault unlock.
- A normal restart does not get past FileVault. Use authenticated restart for planned unattended reboots.
- GUI tools, browser automation, iMessage, and login-Keychain-dependent tools still need the user desktop session.
- GitHub only works headlessly if its credentials are available without the interactive SSH agent or unlocked login Keychain.
- Google Workspace `gog` can work headlessly after its refresh token is valid. If the token expires while away, use `scripts/gog-remote-auth.sh` to run the remote OAuth flow: OpenClaw prints a Google URL, Nikolaj approves from any browser/phone, then OpenClaw exchanges the copied localhost redirect URL. This setup uses `gog auth keyring file` with a local encryption key at `~/Library/Application Support/gogcli/keyring-password` because the macOS login Keychain is locked before desktop login. For headless commands, prefer `scripts/gog-headless.sh ...` instead of bare `gog ...` so `GOG_KEYRING_PASSWORD` is loaded.

Commands:

```bash
scripts/openclaw-headless/install.sh
scripts/openclaw-headless/status.sh
scripts/openclaw-headless/uninstall.sh
```

The installer disables the existing user LaunchAgents to avoid duplicate gateway/node services on port `18789`. The uninstaller removes the LaunchDaemons and restores the user LaunchAgents.

## Planned Reboots Through FileVault

This Mac supports authenticated restart. For a planned restart where OpenClaw should come back without waiting at the FileVault unlock screen, run this locally in Terminal before asking OpenClaw to restart:

```bash
scripts/openclaw-headless/authrestart.sh --stage
```

Then ask OpenClaw to restart normally. The staged unlock is one-time and should be used only for maintenance windows because it temporarily reduces FileVault protection until the next reboot completes.

Test result on 2026-06-27: normal restart waited at FileVault/login; staged authenticated restart rebooted at 10:10 and OpenClaw answered Telegram with `uptime` reporting `0 users`.

For an immediate authenticated restart from Terminal:

```bash
scripts/openclaw-headless/authrestart.sh --now
```
