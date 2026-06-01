#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import uuid
from datetime import datetime, timedelta, date
from urllib.parse import quote

HA_BASE = "http://192.168.0.241:8123"
WORKSPACE = str(Path(__file__).resolve().parent.parent)
DEFAULT_SECTIONS = [
    "Global",
    "Denmark / EU",
    "Markets",
    "Tech / AI",
    "Today to watch",
    "Copenhagen weather",
    "If I only do 3 things today",
    "Nikolaj’s Tasks",
    "Household Chores",
    "Solar",
]


def sh(cmd, cwd=None):
    return subprocess.check_output(cmd, text=True, cwd=cwd).strip()


def get_token():
    user = sh(["whoami"])
    return sh(["security", "find-generic-password", "-a", user, "-s", "homeassistant-mcp-token", "-w"])


def ha_request(path, token, method="GET", body=None):
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(HA_BASE + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None


def ha_get(path, token):
    return ha_request(path, token)


def ha_post(path, token, body):
    return ha_request(path, token, method="POST", body=body)


def refresh_household_chore_sensors(token):
    entity_ids = [
        "sensor.household_chores_next_3_tasks",
        "sensor.household_chores_today_tasks",
        "sensor.household_chores_nikolaj_tasks_2",
        "sensor.household_chores_nikolaj_next_3_tasks_2",
        "sensor.household_chores_janice_tasks_2",
        "sensor.household_chores_janice_next_3_tasks_2",
        "sensor.household_chores_nelly_tasks_2",
        "sensor.household_chores_nelly_next_3_tasks_2",
        "sensor.household_chores_jamie_tasks_2",
        "sensor.household_chores_jamie_next_3_tasks_2",
    ]
    try:
        ha_post("/api/services/homeassistant/update_entity", token, {"entity_id": entity_ids})
    except Exception:
        return False
    return True


def safe_state(entity_id, token):
    try:
        return ha_get(f"/api/states/{entity_id}", token)
    except Exception:
        return None


def yesterday_yield(token, entity_id="sensor.solax_yield_today_4"):
    now = datetime.now().astimezone()
    start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    path = (
        "/api/history/period/"
        + quote(start.isoformat(), safe="")
        + f"?filter_entity_id={entity_id}&end_time="
        + quote(end.isoformat(), safe="")
    )
    try:
        data = ha_get(path, token)
        vals = []
        for item in data[0]:
            try:
                vals.append(float(item.get("state")))
            except Exception:
                pass
        return max(vals) if vals else None
    except Exception:
        return None


def build_top3(household, nikolaj, energy):
    js = f'''
import {{ buildTopThreeForBrief, formatTopThreeForBrief }} from "./family-ops/packages/engine/src/index.js";
const household = {json.dumps(household)};
const nikolaj = {json.dumps(nikolaj)};
const energy = {json.dumps(energy)};
const result = buildTopThreeForBrief({{ householdChoresSensor: household, nikolajChoresSensor: nikolaj, energy }});
console.log(JSON.stringify({{ result, lines: formatTopThreeForBrief(result) }}));
'''
    out = subprocess.check_output(["node", "--input-type=module", "-e", js], text=True, cwd=WORKSPACE)
    return json.loads(out)


def _titles_from_state(state):
    if not state or not isinstance(state, dict):
        return []
    attrs = state.get("attributes") or {}
    titles = attrs.get("titles") if isinstance(attrs.get("titles"), list) else []
    return [str(item).strip() for item in titles if str(item).strip()]


def _tasks_from_state(state):
    if not state or not isinstance(state, dict):
        return []
    attrs = state.get("attributes") or {}
    tasks = attrs.get("tasks") if isinstance(attrs.get("tasks"), list) else []
    normalized = []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        assignee_names = item.get("assignee_names") if isinstance(item.get("assignee_names"), list) else []
        assignees = item.get("assignees") if isinstance(item.get("assignees"), list) else []
        raw_date = str(item.get("date") or item.get("due") or "").strip() or None
        parsed_date = None
        days_overdue = None
        status = "undated"
        if raw_date:
            try:
                parsed_date = date.fromisoformat(raw_date)
                days_overdue = (date.today() - parsed_date).days
                if days_overdue > 0:
                    status = "overdue"
                elif days_overdue == 0:
                    status = "today"
                else:
                    status = "upcoming"
            except Exception:
                status = "dated"
        normalized.append(
            {
                "title": str(item.get("title") or item.get("name") or item.get("task") or "").strip(),
                "date": raw_date,
                "display_date": (f"{raw_date} (overdue {days_overdue}d)" if raw_date and days_overdue and days_overdue > 0 else raw_date),
                "days_overdue": days_overdue if days_overdue and days_overdue > 0 else 0,
                "status": status,
                "assignee": ", ".join(assignee_names or assignees) if (assignee_names or assignees) else str(item.get("assignee") or item.get("person") or "").strip() or None,
            }
        )
    return [item for item in normalized if item.get("title")]


def _weather_summary(state):
    if not state or not isinstance(state, dict):
        return None
    attrs = state.get("attributes") or {}
    condition = str(state.get("state") or "").strip()
    temperature = attrs.get("temperature")
    parts = []
    if condition:
        parts.append(condition)
    if temperature not in (None, "unknown", "unavailable"):
        parts.append(f"{temperature}°C")
    return " • ".join(parts) if parts else None


def parse_sections(text):
    if not text:
        return []
    normalized = text.replace("\r\n", "\n").strip()
    lines = normalized.split("\n")
    sections = []
    current_title = None
    current_lines = []

    def flush():
        nonlocal current_title, current_lines
        if current_title:
            body = "\n".join(line.rstrip() for line in current_lines).strip()
            if body:
                sections.append({"title": current_title, "body": body})
        current_title = None
        current_lines = []

    for raw in lines:
        line = raw.strip()
        matched = None
        for title in DEFAULT_SECTIONS:
            if line == f"**{title}**" or line == title:
                matched = title
                break
        if matched:
            flush()
            current_title = matched
            continue
        if current_title:
            current_lines.append(raw)
    flush()
    return sections


def build_brief_text(sections):
    blocks = []
    for section in sections:
        body = section.get("body", "").strip()
        if not body:
            continue
        blocks.append(f"{section['title']}\n{body}")
    return "\n\n".join(blocks) if blocks else None


def build_payload(brief_text, token):
    refresh_household_chore_sensors(token)
    household = safe_state("sensor.household_chores_next_3_tasks", token)
    nikolaj = safe_state("sensor.household_chores_nikolaj_next_3_tasks_2", token)
    solar_power = safe_state("sensor.solax_ac_power_3", token)
    home_power = safe_state("sensor.solax_husforbrug_effekt", token)
    solar_today = safe_state("sensor.solax_yield_today_4", token)
    weather = safe_state("weather.forecast_hjem", token)
    yesterday = yesterday_yield(token)

    energy = {
        "solarWatts": float(solar_power["state"]) if solar_power and solar_power.get("state") not in (None, "unknown", "unavailable") else 0,
        "homeWatts": float(home_power["state"]) if home_power and home_power.get("state") not in (None, "unknown", "unavailable") else 0,
        "priceState": "normal",
    }
    top3 = build_top3(household, nikolaj, energy)
    top3_lines = top3.get("lines") if isinstance(top3, dict) and isinstance(top3.get("lines"), list) else []
    nikolaj_tasks = _tasks_from_state(nikolaj)
    household_tasks = _tasks_from_state(household)
    sections = parse_sections(brief_text)
    summary = top3_lines[0] if top3_lines else (sections[0]["body"].split("\n")[0].strip() if sections else None)

    return {
        "package_kind": "daily_brief",
        "generated_at": datetime.now().astimezone().isoformat(),
        "summary": summary,
        "brief_text": build_brief_text(sections),
        "sections": sections,
        "household": household,
        "nikolaj": nikolaj,
        "household_titles": _titles_from_state(household),
        "nikolaj_titles": _titles_from_state(nikolaj),
        "household_tasks": household_tasks,
        "nikolaj_tasks": nikolaj_tasks,
        "solar_power": solar_power,
        "home_power": home_power,
        "solar_today": solar_today,
        "solar_yesterday_kwh": yesterday,
        "weather": weather,
        "top3": top3,
    }


def publish_payload(token, entry_id, payload, source="full_daily_brief"):
    return ha_post(
        "/api/services/home_brief/publish_daily_brief_package?return_response=1",
        token,
        {
            "entry_id": entry_id,
            "source": source,
            "payload": payload,
        },
    )


def generate_brief_via_agent(prompt_path):
    prompt = f'''Read and follow the briefing spec at `{prompt_path}`.

Before writing the brief, run this exact command from the workspace and use its JSON output as the live Home Assistant ground truth plus Top 3 decision layer:

`python3 scripts/daily_brief_runtime.py`

Requirements:
- Use the spec exactly.
- Always include the Home Assistant chores sensor `sensor.household_chores_next_3_tasks`.
- Use the JSON from `scripts/daily_brief_runtime.py` for chores, Nikolaj tasks, weather, solar, and the `If I only do 3 things today` section.
- Do not fall back to vague MCP summaries for those sections.
- Keep the result concise but high-signal.
- Write naturally, like a sharp human analyst.
- Do not expose tokens or secret values.
- If any one data source fails, continue and note the missing section briefly rather than failing the whole brief.
- Reply with only the final brief text.
- Do not wrap the result in code fences.
'''
    isolated_session_id = f"daily-brief-{uuid.uuid4()}"
    cmd = [
        "openclaw",
        "agent",
        "--local",
        "--agent",
        "main",
        "--session-id",
        isolated_session_id,
        "--message",
        prompt,
        "--timeout",
        "240",
    ]
    # Deliberately force a fresh session here.
    # Reusing the caller session causes the daily-brief generator to inherit
    # large chat history, which has led to context overflows and slow runs.
    result = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or f"openclaw agent failed with exit code {result.returncode}")
    return result.stdout.strip()


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Publish full daily brief package into Home Brief")
    parser.add_argument("--entry-id", help="Home Brief config entry id to publish into")
    parser.add_argument("--brief-file", help="Path to plain text daily brief source")
    parser.add_argument("--generate-from-prompt", action="store_true", help="Generate the full brief from the standard prompt before publishing")
    parser.add_argument("--prompt-path", default=f"{WORKSPACE}/prompts/openclaw_daily_brief.md", help="Prompt spec path used with --generate-from-prompt")
    parser.add_argument("--source", default="full_daily_brief", help="Source label recorded by Home Brief")
    parser.add_argument("--generate-only", action="store_true", help="Generate/build the brief and payload but do not publish to Home Brief")
    args = parser.parse_args(argv)
    if not args.generate_only and not args.entry_id:
        parser.error("--entry-id is required unless --generate-only is used")
    return args


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.generate_from_prompt:
        brief_text = generate_brief_via_agent(args.prompt_path)
    elif args.brief_file:
        brief_text = open(args.brief_file, "r", encoding="utf-8").read()
    else:
        raise SystemExit("Provide --brief-file or --generate-from-prompt")
    token = get_token()
    payload = build_payload(brief_text, token)
    if args.generate_only:
        print(json.dumps({"ok": True, "generated_only": True, "payload": payload, "brief_text": brief_text}, ensure_ascii=False))
        return
    result = publish_payload(token, args.entry_id, payload, source=args.source)
    print(json.dumps({"ok": True, "published": result, "payload": payload, "brief_text": brief_text}, ensure_ascii=False))


if __name__ == "__main__":
    main()
