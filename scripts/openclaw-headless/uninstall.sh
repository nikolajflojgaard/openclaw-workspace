#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This uninstaller is macOS-only." >&2
  exit 70
fi

uid="$(id -u)"
user="nikolajflojgaard"
launch_agents="/Users/$user/Library/LaunchAgents"
launch_daemons="/Library/LaunchDaemons"

gateway_agent="$launch_agents/ai.openclaw.gateway.plist"
node_agent="$launch_agents/ai.openclaw.node.plist"
gateway_daemon="$launch_daemons/ai.openclaw.gateway.headless.plist"
node_daemon="$launch_daemons/ai.openclaw.node.headless.plist"

echo "Removing OpenClaw headless LaunchDaemons and restoring user LaunchAgents."
sudo -v

sudo launchctl bootout system "$node_daemon" >/dev/null 2>&1 || true
sudo launchctl bootout system "$gateway_daemon" >/dev/null 2>&1 || true
sudo rm -f "$node_daemon" "$gateway_daemon"

launchctl enable "gui/$uid/ai.openclaw.gateway" >/dev/null 2>&1 || true
launchctl enable "gui/$uid/ai.openclaw.node" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$uid" "$gateway_agent" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$uid" "$node_agent" >/dev/null 2>&1 || true
launchctl kickstart -k "gui/$uid/ai.openclaw.gateway" >/dev/null 2>&1 || true
launchctl kickstart -k "gui/$uid/ai.openclaw.node" >/dev/null 2>&1 || true

echo "Restored user LaunchAgents. Current status:"
openclaw status --deep
