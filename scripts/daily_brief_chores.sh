#!/usr/bin/env bash
# Henter household chores data via mcporter (MCP)
# Bruges af daily brief

set -euo pipefail

# Hent dagens opgaver via mcporter (virker i cron kontekst)
echo "=== HOUSEHOLD CHORES I DAG ==="

# Brug mcporter til at hente context og parse chores data
mcporter call homeassistant.GetLiveContext --output json 2>/dev/null | python3 << 'PYEOF'
import sys, json, re

try:
    data = json.load(sys.stdin)
    text = data.get("result", "")
    
    # Find alle sensorer med "chores" i navnet
    chore_sensors = re.findall(
        r'- names: Household chores today tasks\s+domain: sensor\s+state: [\'"]([^\'"]+)[\'"]',
        text, re.IGNORECASE
    )
    
    if chore_sensors:
        print(f"Opgaver i dag: {chore_sensors[0]}")
    else:
        print("Ingen chores data i live context")
        
except Exception as e:
    print(f"Kunne ikke hente chores: {e}")
PYEOF

echo ""
echo "=== DINE NÆSTE 3 OPGAVER ==="
mcporter call homeassistant.GetLiveContext --output json 2>/dev/null | python3 << 'PYEOF'
import sys, json, re

try:
    data = json.load(sys.stdin)
    text = data.get("result", "")
    
    # Find next 3 tasks
    matches = re.findall(
        r'- names: Household chores nikolaj next 3 tasks[^}]*?domain: sensor\s+state: [\'"]([^\'"]+)[\'"]',
        text, re.IGNORECASE | re.DOTALL
    )
    
    if matches:
        print(f"Antal kommende opgaver: {matches[0]}")
    else:
        print("Ingen kommende opgaver fundet")
        
except Exception as e:
    print(f"Kunne ikke hente næste opgaver: {e}")
PYEOF
