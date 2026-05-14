---
name: tesla-ring-arrival
description: Detect likely arrival of Janice in a white Tesla Model Y (Juniper) using Home Assistant Tesla + Ring signals, with optional vision verification from Ring snapshots. Use when setting up or operating arrival pings in a defined time window (default 15:30-16:40) and notifying via Telegram with the message "Janice er hjemme".
---

Use this skill to run stable arrival detection in two modes:

1) **Signal mode (default):** Tesla location + Ring motion + user presence.
2) **Vision mode (optional):** Signal mode + snapshot verification via vision model.

## Files
- Detector script: `scripts/tesla_ring_arrival_check.py`
- Config guide: `references/config.md`

## Quick run

```bash
HA_TOKEN='<home-assistant-token>' python3 skills/tesla-ring-arrival/scripts/tesla_ring_arrival_check.py
```

If conditions match, script prints exactly:

`Janice er hjemme`

Otherwise it prints nothing.

## Expected automation behavior
- Evaluate only inside the time window (default 15:30-16:40 Europe/Copenhagen).
- Trigger candidate when Tesla tracker flips `not_home -> home`.
- Require corroboration (`binary_sensor ... user_present = on` or recent Ring front motion).
- De-duplicate alerts to one ping per day.
- In vision mode, require positive model match before printing.

## Environment variables
- `HA_TOKEN` (required)
- `HA_WS_URL` (optional)
- `HA_HTTP_URL` (optional)
- `OPENAI` + `_API_KEY` (optional, enables vision verification)
- `OPENAI_MODEL` (optional, default `gpt-4.1-mini`)
- `WINDOW_START` (optional, default `15:30`)
- `WINDOW_END` (optional, default `16:40`)

## Cron integration pattern
Run every 2 minutes between 15:00-16:59 and forward output to Telegram only if output is non-empty.
