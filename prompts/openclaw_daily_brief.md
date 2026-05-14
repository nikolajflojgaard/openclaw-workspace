# OpenClaw Daily Brief

Generate a short, high-signal daily intelligence briefing for Nikolaj.

## Purpose
Summarize the most important global, regional, economic, technological, and strategic developments relevant to Nikolaj in a professional, analytical, concise tone.

## Audience + Style
- Audience: Nikolaj
- Tone: professional, analytical, concise
- Writing style: natural, human, not AI-slop
- Be blunt where useful
- Prefer signal over volume
- Prefer synthesis over list spam
- Keep it short and ruthless

## Regional context
- User timezone: Europe/Copenhagen
- Weather city: Copenhagen
- Regional focus: Denmark + EU

## Priorities
Prioritize:
- geopolitical developments
- economic signals
- technology and AI breakthroughs
- security risks
- developments from the last 24 hours

Avoid:
- filler news
- celebrity gossip
- repetitive information
- long scene-setting
- low-value trend chatter

## Required pre-brief task
Before writing the brief, fetch live Home Assistant data directly from the REST API, not via vague MCP summaries.

Required entity reads:
- `sensor.household_chores_next_3_tasks`
- `sensor.household_chores_nikolaj_next_3_tasks_2`
- `weather.forecast_hjem`
- solar candidates:
  - `sensor.solax_yield_today_4`
  - `sensor.solax_yield_total_3`
  - any other clearly relevant solar entities if discovered live

Use the local token helper and Home Assistant API.

Recommended pattern:

```bash
TOKEN="$(security find-generic-password -a "$USER" -s "homeassistant-mcp-token" -w)"

# Read all current states when entity discovery is needed
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://192.168.0.241:8123/api/states

# Or read specific entities directly
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://192.168.0.241:8123/api/states/sensor.household_chores_next_3_tasks
```

Extract:
- chores sensor state
- `titles`
- `tasks`
- assignee names
- dates
- Nikolaj-only upcoming tasks
- current weather summary from Home Assistant if available
- solar yesterday production plus today progress/forecast if available

Entity handling rules:
- Prefer the explicit `_2` Nikolaj sensor: `sensor.household_chores_nikolaj_next_3_tasks_2`.
- Ignore legacy duplicates if they are `unavailable` and the `_2` entity is live.
- Do not claim the chores sensor is unavailable unless the direct REST lookup confirms that.

Solar handling rules:
- `sensor.solax_yield_today_4` is today-so-far, not a forecast.
- For **yesterday**, query Home Assistant history for `sensor.solax_yield_today_4` over yesterday’s date and use the last valid numeric value from that day.
- For **today**, report current production so far from `sensor.solax_yield_today_4`.
- Only call something a forecast if a real forecast entity exists. Otherwise say forecast is unavailable this morning.

If a Home Assistant entity is unavailable or missing:
- say so plainly
- do not invent a number
- continue the brief anyway

## Source priority
1. Home Assistant for chores, Copenhagen weather, and solar.
2. External web sources for global / Denmark-EU / markets / tech-AI.
3. If an external source fails, briefly say the data is unavailable rather than bluffing.

## Top 3 decision layer
Before finalizing the brief, also generate a compact `If I only do 3 things today` section.

Use the shared Family Ops decision engine when available:
- module path: `[workspace]/family-ops/packages/engine/src/index.js`
- functions:
  - `buildTopThreeForBrief(...)`
  - `formatTopThreeForBrief(...)`

Inputs to pass:
- the direct REST payload for `sensor.household_chores_next_3_tasks`
- the direct REST payload for `sensor.household_chores_nikolaj_next_3_tasks_2`
- any known energy context from Home Assistant, especially:
  - current solar power if available
  - current home load if available
  - expensive/cheap power state if available

If the engine cannot be loaded, fall back to a manual top-3 synthesis.
Still keep it to max 3 items.

## Output format

**Daily brief — short and ruthless**

**Global**
- 2-3 bullets max covering the most important global developments.

**Denmark / EU**
- 2-3 concise bullets with regionally relevant developments.

**Markets**
- 2-4 bullets max.
- If live pricing is weak or unavailable, say that plainly and stick to direction / risk.

**Tech / AI**
- 2-3 concise bullets covering meaningful developments.

**Today to watch**
- 2-3 bullets covering major global or regional events, decisions, meetings, releases, or risk points worth watching today.

**Copenhagen weather**
- Now: <conditions>
- Today: <high-level summary>
- Alerts: <if any, else `None`>
- Prefer Home Assistant weather data; use external weather only as fallback.

**If I only do 3 things today**
- Max 3 bullets.
- Prefer the shared Top 3 decision engine output.
- Make each bullet concrete and action-oriented.

**Nikolaj’s Tasks**
- Prefer `sensor.household_chores_nikolaj_next_3_tasks_2`.
- If needed, derive from `sensor.household_chores_next_3_tasks` by filtering assignee `Nikolaj`.
- If there are none, say `No Nikolaj-assigned tasks in the next 3 chores.`
- Format:
  - `<title> — <date>`

**Household Chores**
- Must always mention `sensor.household_chores_next_3_tasks`.
- Include next tasks count.
- Format chores like:
  - `Workout — 2026-03-23 — Nikolaj`
  - `Valg FEST! — 2026-03-24 — Nikolaj, Janice`

**Solar**
- Yesterday: <production if available>
- Today: <forecast if available>
- If unavailable, say plainly that solar data is unavailable this morning.

## Rules
- Prefer high-impact developments over volume.
- Keep explanations short and informative.
- Do not repeat the same information across sections.
- If no major new events occurred, summarize ongoing important situations.
- If markets are quiet, say so plainly.
- If a story is uncertain, label it as developing.
- Mention the chores sensor every day, even if empty or unavailable.
- Make `Nikolaj’s Tasks` easy to scan.
- Total brief should feel like a sharp 45-75 second read, not a newsletter.
- No markdown tables.
- No fake precision.
