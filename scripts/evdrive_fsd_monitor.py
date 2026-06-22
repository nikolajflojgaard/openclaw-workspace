#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "evdrive-fsd-monitor.json"
HISTORY_PATH = ROOT / "state" / "evdrive-fsd-monitor-history.jsonl"
APP_URL = "https://www.brugtbilsmodulet.dk/bbm/bbm.app.js?guid=1782cc17-fefc-6183-346d-7b9dae07e3bb"
LISTING_URL = "https://ev-drive.dk/biler"
USER_AGENT = "Mozilla/5.0 (compatible; EvDriveFsdMonitor/1.0)"
FSD_RE = re.compile(r"\bfsd\b|full self-driving|fuld selvkørende", re.IGNORECASE)


@dataclass(frozen=True)
class FsdCar:
    key: str
    make: str
    model: str
    variant: str
    year: str
    mileage: int | None
    price: int | None
    display_price: str
    registration_date: str
    color: str
    comment_headline: str
    under_budget: bool


def fetch_text(url: str, timeout: int = 60) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/javascript,text/plain,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_data(js: str) -> dict:
    marker = '$scope.data = {"ApiVersion"'
    start = js.find(marker)
    if start < 0:
        raise RuntimeError("Could not find vehicle data in brugtbilsmodulet app JS")

    i = start + len("$scope.data = ")
    while i < len(js) and js[i].isspace():
        i += 1
    if i >= len(js) or js[i] != "{":
        raise RuntimeError("Vehicle data did not start with a JSON object")

    depth = 0
    in_string = False
    escaped = False
    for pos in range(i, len(js)):
        char = js[pos]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(js[i : pos + 1])

    raise RuntimeError("Could not parse complete vehicle JSON object")


def parse_int(value: object) -> int | None:
    if value is None:
        return None
    cleaned = re.sub(r"\D", "", str(value))
    return int(cleaned) if cleaned else None


def first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def is_fsd_car(vehicle: dict) -> bool:
    fields = [
        vehicle.get("Comment", ""),
        vehicle.get("Variant", ""),
        " ".join(vehicle.get("EquipmentList") or []),
    ]
    return bool(FSD_RE.search("\n".join(fields)))


def normalize_car(vehicle: dict, budget: int) -> FsdCar:
    price = parse_int(vehicle.get("Price") or vehicle.get("CashPrice"))
    mileage = parse_int(vehicle.get("Mileage"))
    key = str(vehicle.get("VehicleId") or vehicle.get("Id"))
    return FsdCar(
        key=key,
        make=str(vehicle.get("Make") or ""),
        model=str(vehicle.get("Model") or ""),
        variant=str(vehicle.get("Variant") or ""),
        year=str(vehicle.get("Year") or ""),
        mileage=mileage,
        price=price,
        display_price=str(vehicle.get("DisplayPrice") or vehicle.get("Price") or ""),
        registration_date=str(vehicle.get("RegistrationDate") or ""),
        color=str(vehicle.get("Color") or ""),
        comment_headline=first_line(str(vehicle.get("Comment") or "")),
        under_budget=price is not None and price < budget,
    )


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"seen": {}, "budget_hits": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict, cars: list[FsdCar], budget: int, max_mileage: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    seen = state.setdefault("seen", {})
    budget_hits = state.setdefault("budget_hits", {})
    for car in cars:
        seen[car.key] = asdict(car)
        if car.under_budget:
            budget_hits[car.key] = {"price": car.price, "seenAt": budget_hits.get(car.key, {}).get("seenAt", now)}
    state.update(
        {
            "updatedAt": now,
            "source": APP_URL,
            "listingUrl": LISTING_URL,
            "budget": budget,
            "preferredMaxMileage": max_mileage,
            "currentFsdCars": [asdict(car) for car in cars],
        }
    )
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_history(cars: list[FsdCar], new_cars: list[FsdCar], new_budget_hits: list[FsdCar]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "currentFsdCount": len(cars),
        "newCars": [asdict(car) for car in new_cars],
        "newBudgetHits": [asdict(car) for car in new_budget_hits],
    }
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def format_car(car: FsdCar, budget: int, max_mileage: int) -> str:
    price_label = car.display_price or (f"{car.price:,} kr.".replace(",", ".") if car.price else "pris ukendt")
    mileage_label = f"{car.mileage:,} km".replace(",", ".") if car.mileage is not None else "km ukendt"
    budget_display = f"{budget:,}".replace(",", ".")
    budget_label = f"UNDER {budget_display}" if car.under_budget else f"over {budget_display}"
    mileage_fit = "km OK" if car.mileage is None or car.mileage <= max_mileage else f"over {max_mileage:,} km".replace(",", ".")
    return (
        f"- {car.make} {car.model} {car.variant}, {car.year}, {price_label}, "
        f"{mileage_label}, {car.color} ({budget_label}, {mileage_fit})"
    )


def format_alert(new_cars: list[FsdCar], new_budget_hits: list[FsdCar], budget: int, max_mileage: int) -> str:
    lines = ["Ny EV-Drive FSD-match fundet:"]
    if new_cars:
        lines.append("")
        lines.append("Nye FSD-annoncer:")
        lines.extend(format_car(car, budget, max_mileage) for car in new_cars)
    if new_budget_hits:
        lines.append("")
        lines.append("Nye FSD-budgethits:")
        lines.extend(format_car(car, budget, max_mileage) for car in new_budget_hits)
    lines.append("")
    lines.append(LISTING_URL)
    lines.append("Jeg ville stadig bede EV-Drive dokumentere FSD direkte i Tesla-skærmen/app før depositum.")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=280000)
    parser.add_argument("--max-mileage", type=int, default=70000)
    parser.add_argument("--init", action="store_true", help="Seed state without alerting.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = extract_data(fetch_text(APP_URL))
    cars = [normalize_car(vehicle, args.budget) for vehicle in data.get("Vehicles", []) if is_fsd_car(vehicle)]

    state = load_state()
    seen = state.get("seen", {})
    budget_hits = state.get("budget_hits", {})
    new_cars = [car for car in cars if car.key not in seen]
    new_budget_hits = [car for car in cars if car.under_budget and car.key not in budget_hits and car.key in seen]

    save_state(state, cars, args.budget, args.max_mileage)
    append_history(cars, [] if args.init else new_cars, [] if args.init else new_budget_hits)

    if args.init:
        print(f"Initialized EV-Drive FSD monitor with {len(cars)} current FSD car(s). Preferred mileage max: {args.max_mileage}.")
        return 0

    alert_new_cars = [car for car in new_cars if car.under_budget]
    if alert_new_cars or new_budget_hits:
        print(format_alert(alert_new_cars, new_budget_hits, args.budget, args.max_mileage))
    elif args.verbose:
        print(f"No new EV-Drive FSD cars. Current FSD count: {len(cars)}. Preferred mileage max: {args.max_mileage}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"EV-Drive FSD monitor failed: {exc}", file=sys.stderr)
        raise
