#!/usr/bin/env bash
# Daily Brief Generator — inkluderer Household Chores
# Kører fra cron med korrekt HA auth

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source HA credentials
export HA_ENV_FILE="${HOME}/.openclaw/secrets/ha.env"
if [[ -f "$HA_ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$HA_ENV_FILE"
fi

# Hent Household Chores data
get_chores() {
    local output=""
    
    # Dagens opgaver
    if command -v "${SCRIPT_DIR}/ha_api.sh" &> /dev/null; then
        local today_tasks
        today_tasks=$("${SCRIPT_DIR}/ha_api.sh" /api/states/sensor.household_chores_today_tasks 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tasks = d.get('attributes', {}).get('tasks', [])
    for t in tasks:
        print(f\"- {t.get('title', '?')}\")
except:
    pass
" 2>/dev/null || echo "")
        
        if [[ -n "$today_tasks" ]]; then
            output="**Dagens opgaver:**\n$today_tasks"
        else
            output="**Dagens opgaver:** Ingen"
        fi
        
        # Nikolajs næste 3
        local next_tasks
        next_tasks=$("${SCRIPT_DIR}/ha_api.sh" /api/states/sensor.household_chores_nikolaj_next_3_tasks_2 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tasks = d.get('attributes', {}).get('tasks', [])
    for t in tasks:
        col = t.get('column', '?')
        print(f\"- {t.get('title', '?')} ({col})\")
except:
    pass
" 2>/dev/null || echo "")
        
        if [[ -n "$next_tasks" ]]; then
            output="$output\n\n**Dine næste opgaver:**\n$next_tasks"
        fi
    else
        output="Kunne ikke loade ha_api.sh"
    fi
    
    echo -e "$output"
}

# Hvis kaldt direkte, print chores
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    get_chores
fi
