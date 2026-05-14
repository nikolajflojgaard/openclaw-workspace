#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <on|off|toggle> <entity_id> [brightness_pct]" >&2
  exit 1
fi

action="$1"
entity_id="$2"
brightness="${3:-}"

case "$action" in
  on) service="light/turn_on" ;;
  off) service="light/turn_off" ;;
  toggle) service="light/toggle" ;;
  *) echo "Invalid action: $action" >&2; exit 1 ;;
esac

if [[ -n "$brightness" && "$action" == "on" ]]; then
  payload=$(printf '{"entity_id":"%s","brightness_pct":%s}' "$entity_id" "$brightness")
else
  payload=$(printf '{"entity_id":"%s"}' "$entity_id")
fi

"$(dirname "$0")/ha_api.sh" "/api/services/$service" -X POST -d "$payload"
