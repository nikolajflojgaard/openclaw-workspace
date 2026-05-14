#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from urllib.parse import quote

HA_BASE = "http://192.168.0.241:8123"
WORKSPACE = Path(__file__).resolve().parent.parent


def sh(cmd):
    return subprocess.check_output(cmd, text=True).strip()


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
    out = subprocess.check_output(["node", "--input-type=module", "-e", js], text=True, cwd=str(WORKSPACE))
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
        normalized.append(
            {
                "title": str(item.get("title") or item.get("name") or item.get("task") or "").strip(),
                "date": str(item.get("date") or item.get("due") or "").strip() or None,
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


def _build_brief_text(top3_lines, nikolaj_tasks, household_tasks, weather, solar_today, yesterday):
    sections = []
    if top3_lines:
        sections.append("If I only do 3 things today\n" + "\n".join(f"• {line}" for line in top3_lines[:3]))
    if nikolaj_tasks:
        sections.append(
            "Nikolaj’s Tasks\n" + "\n".join(
                f"• {item['title']}" + (f" — {item['date']}" if item.get('date') else "")
                for item in nikolaj_tasks[:3]
            )
        )
    if household_tasks:
        sections.append(
            "Household Chores\n" + "\n".join(
                f"• {item['title']}"
                + (f" — {item['date']}" if item.get('date') else "")
                + (f" — {item['assignee']}" if item.get('assignee') else "")
                for item in household_tasks[:3]
            )
        )
    weather_line = _weather_summary(weather)
    solar_today_state = solar_today.get("state") if isinstance(solar_today, dict) else None
    solar_lines = []
    if weather_line:
        solar_lines.append(f"Now: {weather_line}")
    if yesterday is not None:
        solar_lines.append(f"Yesterday: {yesterday} kWh")
    if solar_today_state not in (None, "unknown", "unavailable"):
        solar_lines.append(f"Today so far: {solar_today_state} kWh")
    if solar_lines:
        sections.append("Weather / Solar\n" + "\n".join(f"• {line}" for line in solar_lines))
    return "\n\n".join(sections) if sections else None


def build_payload(token):
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
    summary = top3_lines[0] if top3_lines else None
    brief_text = _build_brief_text(top3_lines, nikolaj_tasks, household_tasks, weather, solar_today, yesterday)

    return {
        "package_kind": "daily_brief",
        "generated_at": datetime.now().astimezone().isoformat(),
        "summary": summary,
        "brief_text": brief_text,
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


def publish_payload(token, entry_id, payload, source="daily_brief_runtime"):
    return ha_post(
        "/api/services/home_brief/publish_daily_brief_package?return_response=1",
        token,
        {
            "entry_id": entry_id,
            "source": source,
            "payload": payload,
        },
    )


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Build and optionally publish Home Brief daily brief package")
    parser.add_argument("--publish-entry-id", help="Home Brief config entry id to publish into")
    parser.add_argument("--source", default="daily_brief_runtime", help="Source label recorded by Home Brief")
    parser.add_argument("--print-only", action="store_true", help="Only print the payload JSON")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    token = get_token()
    payload = build_payload(token)

    if args.publish_entry_id:
        result = publish_payload(token, args.publish_entry_id, payload, source=args.source)
        print(json.dumps({"ok": True, "published": result, "payload": payload}, ensure_ascii=False))
        return

    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
