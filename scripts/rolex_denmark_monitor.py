#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "rolex-denmark-dealers.json"
HISTORY_PATH = ROOT / "state" / "rolex-denmark-dealers-history.jsonl"
SITEMAP_URL = "https://www.rolex.com/api/sm/retailer-sitemap.xml"
TITLE_FETCH_PREFIX = "https://r.jina.ai/http://"
USER_AGENT = "Mozilla/5.0 (compatible; RolexDenmarkMonitor/1.0)"

KNOWN_NAME_OVERRIDES = {
    "https://www.rolex.com/rolex-dealers/klitgaard-1122/rswi_1377-aalborg-denmark": "KLITGAARD AALBORG",
    "https://www.rolex.com/rolex-dealers/knudpedersen-1124/rswi_1378-aarhus-denmark": "KNUD PEDERSEN A/S AARHUS",
    "https://www.rolex.com/rolex-dealers/klarlund-1120/rswi_1380-copenhagenv-denmark": "KLARLUND COPENHAGEN AXEL TOWERS",
    "https://www.rolex.com/rolex-dealers/ragnarurejuveler-53/rswi_1385-odense-denmark": "RAGNAR ODENSE",
    "https://www.rolex.com/rolex-dealers/bucherer-486/rswi_16227-copenhagen-denmark": "BUCHERER COPENHAGEN",
    "https://www.rolex.com/rolex-dealers/klarlund-1120/rswi_188352-copenhagen-denmark": "KLARLUND COPENHAGEN OSTERGADE 15",
}

CITY_LABELS = {
    "aalborg": "Aalborg",
    "aarhus": "Aarhus",
    "copenhagen": "Copenhagen",
    "copenhagenk": "Copenhagen K",
    "copenhagenv": "Copenhagen V",
    "odense": "Odense",
}

DEALER_URL_RE = re.compile(
    r"https://www\.rolex\.com/rolex-dealers/(?P<slug>[^/]+)/(?P<id>rswi_\d+)-(?P<city>[a-z]+)-denmark"
)
STORE_LOCATOR_DENMARK_RE = re.compile(r"https://www\.rolex\.com/store-locator/denmark(?:/[a-z]+)+")
LOC_RE = re.compile(r"<loc>(https://www\.rolex\.com/[^<]+)</loc>")
TITLE_RE = re.compile(r"^Title:\s*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Dealer:
    name: str
    city: str
    url: str


def fetch_text(url: str, timeout: int = 60) -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if "rolex.com" in url:
        headers["Referer"] = "https://www.rolex.com/"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def title_case_slug(slug: str) -> str:
    slug = re.sub(r"-\d+$", "", slug)
    return " ".join(part.upper() for part in slug.split("-"))


def parse_title_to_name(title: str) -> str | None:
    if not title or title.strip().lower() == "access denied":
        return None
    title = title.replace("| Rolex®", "").replace("| Rolex", "").strip()
    if "Official Rolex Retailer" in title:
        title = title.split("Official Rolex Retailer", 1)[0].strip(" -")
    pieces = [piece.strip() for piece in title.split(" - ") if piece.strip()]
    if not pieces:
        return None
    if len(pieces) >= 2:
        return pieces[-1]
    return pieces[0]


def fetch_title_name(url: str) -> str | None:
    try:
        page = fetch_text(TITLE_FETCH_PREFIX + url.removeprefix("https://"), timeout=60)
    except (HTTPError, URLError, TimeoutError):
        return None
    match = TITLE_RE.search(page)
    if not match:
        return None
    return parse_title_to_name(match.group(1).strip())


def extract_dealer_urls(sitemap_text: str) -> list[str]:
    legacy_matches = DEALER_URL_RE.findall(sitemap_text)
    legacy_urls = {
        f"https://www.rolex.com/rolex-dealers/{slug}/{dealer_id}-{city}-denmark"
        for slug, dealer_id, city in legacy_matches
        if not slug.startswith("rswi_")
    }
    if legacy_urls:
        return sorted(legacy_urls)

    denmark_urls = {
        url.rstrip("/")
        for url in LOC_RE.findall(sitemap_text)
        if STORE_LOCATOR_DENMARK_RE.fullmatch(url.rstrip("/")) and "/watch-care-and-service/" not in url
    }
    leaf_urls = [
        url
        for url in denmark_urls
        if not any(other != url and other.startswith(url + "/") for other in denmark_urls)
    ]
    return sorted(leaf_urls)


def city_from_url(url: str) -> str | None:
    legacy_match = DEALER_URL_RE.search(url)
    if legacy_match:
        city_slug = legacy_match.group("city")
        return CITY_LABELS.get(city_slug, city_slug.replace("-", " ").title())

    if "/store-locator/denmark/" not in url:
        return None
    city_slug = url.rstrip("/").split("/")[-1]
    return CITY_LABELS.get(city_slug, city_slug.replace("-", " ").title())


def fallback_name_from_url(url: str, city: str) -> str:
    legacy_match = DEALER_URL_RE.search(url)
    if legacy_match:
        return f"{title_case_slug(legacy_match.group('slug'))} {city.upper()}"
    return city.upper()


def normalize_dealers(urls: Iterable[str]) -> list[Dealer]:
    dealers: list[Dealer] = []
    for url in urls:
        city = city_from_url(url)
        if not city:
            continue
        name = KNOWN_NAME_OVERRIDES.get(url) or fetch_title_name(url) or fallback_name_from_url(url, city)
        dealers.append(Dealer(name=name, city=city, url=url))
    dealers.sort(key=lambda dealer: (dealer.city.lower(), dealer.name.lower(), dealer.url))
    return dealers


def load_previous_state() -> dict | None:
    if not STATE_PATH.exists():
        return None
    return json.loads(STATE_PATH.read_text())


def save_state(dealers: list[Dealer]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "Rolex retailer sitemap via r.jina.ai mirror",
        "dealers": [asdict(dealer) for dealer in dealers],
    }
    STATE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def append_history(count: int, added: list[dict], removed: list[dict], changed: bool) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": count,
        "changed": changed,
        "added": added,
        "removed": removed,
    }
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def diff(previous: dict | None, dealers: list[Dealer]) -> tuple[list[dict], list[dict]]:
    old_dealers = (previous or {}).get("dealers", [])
    old_by_url = {dealer["url"]: dealer for dealer in old_dealers}
    new_by_url = {dealer.url: asdict(dealer) for dealer in dealers}

    added = [new_by_url[url] for url in sorted(new_by_url.keys() - old_by_url.keys())]
    removed = [old_by_url[url] for url in sorted(old_by_url.keys() - new_by_url.keys())]
    return added, removed


def format_alert(added: list[dict], removed: list[dict], dealers: list[Dealer]) -> str:
    lines = ["BREAKING", ""]
    if added:
        lines.append("Added:")
        for dealer in added:
            lines.append(f"- {dealer['city']} — {dealer['name']}")
        lines.append("")
    if removed:
        lines.append("Removed:")
        for dealer in removed:
            lines.append(f"- {dealer['city']} — {dealer['name']}")
        lines.append("")
    lines.append("Current dealers:")
    for dealer in dealers:
        lines.append(f"- {dealer.city} — {dealer.name}")
    return "\n".join(lines).strip()


def format_no_change(dealers: list[Dealer]) -> str:
    lines = ["NO CHANGE", ""]
    for dealer in dealers:
        lines.append(f"- {dealer.city} — {dealer.name}")
    return "\n".join(lines).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-report", action="store_true", help="Always print a daily status message")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        sitemap_text = fetch_text(SITEMAP_URL, timeout=90)
        urls = extract_dealer_urls(sitemap_text)
        dealers = normalize_dealers(urls)
        if not dealers:
            raise RuntimeError("resolved zero dealers; refusing to overwrite state")
        previous = load_previous_state()
        added, removed = diff(previous, dealers)
        changed = bool(previous) and bool(added or removed)
        save_state(dealers)
        append_history(len(dealers), added, removed, changed)
        if changed:
            print(format_alert(added, removed, dealers))
        elif args.daily_report:
            print(format_no_change(dealers))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Rolex Denmark monitor failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
