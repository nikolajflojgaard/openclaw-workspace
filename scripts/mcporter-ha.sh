#!/bin/zsh
set -euo pipefail

export HOMEASSISTANT_MCP_TOKEN="$(security find-generic-password -a "$USER" -s "homeassistant-mcp-token" -w)"
exec mcporter "$@"
