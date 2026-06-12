from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import yaml


INPUT_FILE = Path("races.yaml")
OUTPUT_FILE = Path("calendar.ics")
CALENDAR_NAME = "UTMB Index Races AT/DE/IT"


def escape_ics(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def make_uid(race: dict) -> str:
    raw = f"{race.get('utmb_race_id')}|{race.get('start_date')}|{race.get('name')}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"{digest}@ultra-calendar"


def make_description(race: dict) -> str:
    parts = [
        f"Country: {race.get('country', '')}",
        f"Category: {race.get('utmb_category', '')}",
        f"Distance: {race.get('distance', '')}",
        f"Elevation: {race.get('elevation', '')}",
        f"UTMB level: {race.get('utmb_level', '')}",
        f"UTMB stones: {race.get('utmb_stones', '')}",
        f"Website: {race.get('website', '')}",
        f"Source: {race.get('source_url', '')}",
        f"Last checked: {race.get('last_checked', '')}",
    ]
    return "\\n".join(part for part in parts if not part.endswith(": "))


def make_event(race: dict) -> str:
    start = parse_date(race["start_date"])
    end = start + timedelta(days=1)

    summary = race["name"]
    location = race.get("location", "")
    description = make_description(race)

    return "\n".join(
        [
            "BEGIN:VEVENT",
            f"UID:{make_uid(race)}",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{escape_ics(summary)}",
            f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
            f"LOCATION:{escape_ics(location)}",
            f"DESCRIPTION:{escape_ics(description)}",
            f"URL:{escape_ics(race.get('website', ''))}",
            "END:VEVENT",
        ]
    )


def main() -> None:
    races = yaml.safe_load(INPUT_FILE.read_text(encoding="utf-8")) or []

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ultra Calendar//UTMB Index Races//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_ics(CALENDAR_NAME)}",
        "X-WR-TIMEZONE:Europe/Berlin",
    ]

    for race in races:
        lines.append(make_event(race))

    lines.append("END:VCALENDAR")

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(races)} events to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()