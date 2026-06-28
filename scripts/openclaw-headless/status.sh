#!/usr/bin/env bash
set -euo pipefail

uid="$(id -u)"

echo "System LaunchDaemons:"
launchctl print system/ai.openclaw.gateway.headless 2>/dev/null | sed -n '1,35p' || echo "  gateway headless: not loaded"
launchctl print system/ai.openclaw.node.headless 2>/dev/null | sed -n '1,35p' || echo "  node headless: not loaded"

echo
echo "User LaunchAgents:"
launchctl print "gui/$uid/ai.openclaw.gateway" 2>/dev/null | sed -n '1,18p' || echo "  gateway LaunchAgent: not loaded"
launchctl print "gui/$uid/ai.openclaw.node" 2>/dev/null | sed -n '1,18p' || echo "  node LaunchAgent: not loaded"

echo
openclaw status --deep
