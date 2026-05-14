#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${HA_ENV_FILE:-$HOME/.openclaw/secrets/ha.env}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing HA env file: $ENV_FILE" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$ENV_FILE"

if [[ -z "${HA_URL:-}" || -z "${HA_TOKEN:-}" ]]; then
  echo "HA_URL/HA_TOKEN missing in $ENV_FILE" >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path> [curl args...]" >&2
  echo "Example: $0 /api/" >&2
  exit 1
fi

path="$1"; shift || true
curl -sS "$HA_URL$path" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$@"
