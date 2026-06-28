#!/bin/zsh
set -euo pipefail

export HOMEASSISTANT_MCP_TOKEN="$(python3 "$(dirname "$0")/ha_token.py")"
exec mcporter "$@"
