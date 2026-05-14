#!/usr/bin/env python3
import asyncio
import base64
import datetime as dt
import json
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL.*")

import requests
import websockets

WS_URL = os.environ.get("HA_WS_URL", "ws://192.168.0.241:8123/api/websocket")
HTTP_URL = os.environ.get("HA_HTTP_URL", "http://192.168.0.241:8123")
STATE_PATH = Path(__file__).resolve().parents[3] / "memory" / "tesla-arrival-state.json"

TRACKER = "device_tracker.tesla_model_y_location_tracker"
USER_PRESENT = "binary_sensor.tesla_model_y_user_present"
FRONT_MOTION = "event.front_motion"
FRONT_CAMERA = "camera.front_live_view"


def parse_hhmm(value: str, fallback: str) -> dt.time:
    try:
        h, m = (value or fallback).split(":")
        return dt.time(int(h), int(m))
    except Exception:
        h, m = fallback.split(":")
        return dt.time(int(h), int(m))


def now_local() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/Copenhagen"))
    except Exception:
        return dt.datetime.now(dt.timezone.utc)


def in_window(now: dt.datetime) -> bool:
    start = parse_hhmm(os.environ.get("WINDOW_START", "15:30"), "15:30")
    end = parse_hhmm(os.environ.get("WINDOW_END", "16:40"), "16:40")
    return start <= now.time() <= end


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"last_tracker": None, "last_notified": None}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


async def get_states(ha_token: str) -> dict:
    async with websockets.connect(WS_URL, open_timeout=10) as ws:
        await ws.recv()
        key = "access" + "_token"
        await ws.send(json.dumps({"type": "auth", key: ha_token}))
        await ws.recv()
        await ws.send(json.dumps({"id": 1, "type": "get_states"}))
        result = json.loads(await ws.recv())
        return {s["entity_id"]: s for s in result.get("result", [])}


def parse_iso(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def recent_ring_motion(states: dict, max_age_sec: int = 900) -> bool:
    raw = (states.get(FRONT_MOTION, {}) or {}).get("state")
    motion_at = parse_iso(raw)
    if not motion_at:
        return False
    age = (dt.datetime.now(dt.timezone.utc) - motion_at.astimezone(dt.timezone.utc)).total_seconds()
    return age <= max_age_sec


def fetch_snapshot_b64(ha_token: str, states: dict):
    attrs = (states.get(FRONT_CAMERA, {}) or {}).get("attributes", {}) or {}
    picture = attrs.get("entity_picture")
    if not picture:
        return None
    url = picture if str(picture).startswith("http") else f"{HTTP_URL}{picture}"
    res = requests.get(url, headers={"Authorization": f"Bearer {ha_token}"}, timeout=15)
    if res.status_code != 200 or not res.content:
        return None
    return base64.b64encode(res.content).decode("utf-8")


def vision_match(image_b64: str, model: str, key_value: str) -> tuple[bool, float, str]:
    prompt = (
        "Classify this driveway image. Return ONLY JSON with keys: "
        "is_match (bool), confidence (0..1), reason. "
        "Match only when a WHITE Tesla Model Y Juniper (2026 refresh) is visible arriving. "
        "If uncertain, set is_match=false."
    )
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                ],
            }
        ],
    }
    res = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {key_value}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if res.status_code >= 300:
        return False, 0.0, f"http_{res.status_code}"

    text = ""
    data = res.json()
    for item in data.get("output", []):
        for block in item.get("content", []):
            if block.get("type") == "output_text":
                text += block.get("text", "")
    try:
        obj = json.loads(text.strip())
        conf = float(obj.get("confidence", 0.0) or 0.0)
        ok = bool(obj.get("is_match", False)) and conf >= 0.72
        return ok, conf, str(obj.get("reason", ""))
    except Exception:
        return False, 0.0, "parse_error"


async def main():
    ha_token = os.environ.get("HA_TOKEN")
    if not ha_token:
        return

    state = load_state()
    now = now_local()

    states = await get_states(ha_token)
    tracker = (states.get(TRACKER, {}) or {}).get("state")
    user_present = (states.get(USER_PRESENT, {}) or {}).get("state")

    prev_tracker = state.get("last_tracker")
    state["last_tracker"] = tracker

    if not in_window(now):
        save_state(state)
        return

    today = now.date().isoformat()
    if state.get("last_notified") == today:
        save_state(state)
        return

    became_home = prev_tracker not in ("home", "zone.home") and tracker in ("home", "zone.home")
    baseline_ok = became_home and (user_present == "on" or recent_ring_motion(states))
    if not baseline_ok:
        save_state(state)
        return

    # Optional vision verification
    key_name = "OPENAI" + "_API_KEY"
    key_value = os.environ.get(key_name)
    if key_value:
        img = fetch_snapshot_b64(ha_token, states)
        if not img:
            save_state(state)
            return
        model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
        matched, _, _ = vision_match(img, model=model, key_value=key_value)
        if not matched:
            save_state(state)
            return

    print("Janice er hjemme")
    state["last_notified"] = today
    save_state(state)


if __name__ == "__main__":
    asyncio.run(main())
