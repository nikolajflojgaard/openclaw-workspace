#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is macOS-only." >&2
  exit 70
fi

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plist_dir="$repo_dir/plists"
uid="$(id -u)"
user="nikolajflojgaard"
launch_agents="/Users/$user/Library/LaunchAgents"
launch_daemons="/Library/LaunchDaemons"

gateway_agent="$launch_agents/ai.openclaw.gateway.plist"
node_agent="$launch_agents/ai.openclaw.node.plist"
gateway_daemon="$launch_daemons/ai.openclaw.gateway.headless.plist"
node_daemon="$launch_daemons/ai.openclaw.node.headless.plist"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 69
  }
}

need plutil
need sudo
need launchctl

plutil -lint "$plist_dir/ai.openclaw.gateway.headless.plist" >/dev/null
plutil -lint "$plist_dir/ai.openclaw.node.headless.plist" >/dev/null
test -x /opt/homebrew/opt/node@22/bin/node
test -f /opt/homebrew/lib/node_modules/openclaw/dist/index.js
mkdir -p "/Users/$user/Library/Logs/openclaw" "/Users/$user/.openclaw/tmp"

echo "Installing OpenClaw headless LaunchDaemons."
echo "This will disable the user LaunchAgents to avoid duplicate services on port 18789."
sudo -v

launchctl bootout "gui/$uid" "$gateway_agent" >/dev/null 2>&1 || true
launchctl bootout "gui/$uid" "$node_agent" >/dev/null 2>&1 || true
launchctl disable "gui/$uid/ai.openclaw.gateway" >/dev/null 2>&1 || true
launchctl disable "gui/$uid/ai.openclaw.node" >/dev/null 2>&1 || true

sudo launchctl bootout system "$gateway_daemon" >/dev/null 2>&1 || true
sudo launchctl bootout system "$node_daemon" >/dev/null 2>&1 || true

sudo install -o root -g wheel -m 0644 "$plist_dir/ai.openclaw.gateway.headless.plist" "$gateway_daemon"
sudo install -o root -g wheel -m 0644 "$plist_dir/ai.openclaw.node.headless.plist" "$node_daemon"

sudo launchctl bootstrap system "$gateway_daemon"
sudo launchctl bootstrap system "$node_daemon"
sudo launchctl enable system/ai.openclaw.gateway.headless
sudo launchctl enable system/ai.openclaw.node.headless
sudo launchctl kickstart -k system/ai.openclaw.gateway.headless
sudo launchctl kickstart -k system/ai.openclaw.node.headless

"$repo_dir/status.sh"
