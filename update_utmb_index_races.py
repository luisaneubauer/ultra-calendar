from __future__ import annotations

import requests
import yaml

from datetime import date, datetime
from pathlib import Path
from tqdm import tqdm


API_URL = "https://api.utmb.world/search/races-qualifiers"
OUTPUT_FILE = Path("races.yaml")

DATE_MIN = date.today().isoformat()
DATE_MAX = f"{date.today().year + 1}-12-31"

CONFIG_FILE = Path("config.yaml")

config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}

if not config:
    raise RuntimeError(
        "config.yaml is empty or invalid. Please add countries, categories, "
        "and name_abbreviations."
    )

ALLOWED_COUNTRIES = config["countries"]
print(f"Allowed countries: {', '.join(ALLOWED_COUNTRIES.values())}")

ALLOWED_CATEGORIES = set(config["categories"]["include"])
EXCLUDED_CATEGORIES = set(config["categories"].get("exclude", []))
NAME_ABBREVIATIONS = config.get("name_abbreviations", {})

LIMIT = 100

def abbreviate_event_name(event_name: str) -> str:
    for full_name, short_name in NAME_ABBREVIATIONS.items():
        if full_name.lower() in event_name.lower():
            return short_name
    return event_name

def parse_utmb_date(value: str) -> str:
    return datetime.strptime(value, "%Y-%b-%d").date().isoformat()


def fetch_page(offset: int) -> dict:
    response = requests.get(
        API_URL,
        params={
            "lang": "en",
            "dateMin": DATE_MIN,
            "dateMax": DATE_MAX,
            "limit": LIMIT,
            "offset": offset,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def normalize_race(race: dict) -> dict:
    country_code = race["startCountry"]
    country = ALLOWED_COUNTRIES[country_code]

    return {
        "name": f"{abbreviate_event_name(race['eventName'])} - {race['name']}",
        "event_name": race["eventName"],
        "location": race.get("startPlace") or country,
        "country": country,
        "country_code": country_code,
        "start_date": parse_utmb_date(race["startDate"]),
        "website": race.get("url"),
        "distance": f"{race.get('distance')} km",
        "elevation": f"{race.get('elevationGain')} m",
        "utmb_category": race["category"].upper(),
        "utmb_level": race.get("level"),
        "utmb_stones": race.get("nbStones", 0),
        "utmb_race_id": race["id"],
        "source": "UTMB Index Races",
        "source_url": "https://utmb.world/index-races",
        "last_checked": date.today().isoformat(),
    }


def keep_race(race: dict) -> bool:
    return (
        race.get("startCountry") in ALLOWED_COUNTRIES
        and race.get("category") in ALLOWED_CATEGORIES
    )


def dedupe(races: list[dict]) -> list[dict]:
    seen = set()
    unique = []

    for race in races:
        key = race["utmb_race_id"]

        if key in seen:
            continue

        seen.add(key)
        unique.append(race)

    return sorted(unique, key=lambda r: (r["start_date"], r["country"], r["name"]))


def main() -> None:
    first_page = fetch_page(offset=0)

    total = first_page["nbHits"]
    races = []

    pages = range(0, total, LIMIT)

    for offset in tqdm(pages, desc="Downloading UTMB races"):
        page = first_page if offset == 0 else fetch_page(offset)
        for race in page.get("races", []):
            if keep_race(race):
                races.append(normalize_race(race))

    races = dedupe(races)

    OUTPUT_FILE.write_text(
        yaml.safe_dump(races, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    print(f"Wrote {len(races)} races to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()