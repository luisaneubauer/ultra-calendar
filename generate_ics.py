from datetime import datetime, date, timedelta
from pathlib import Path
import hashlib
import yaml


INPUT_FILE = Path("races.yaml")
OUTPUT_FILE = Path("calendar.ics")
CALENDAR_NAME = "Ultra Trail Races"


def escape_ics(text: str) -> str:
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def parse_date(value) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def make_uid(race: dict) -> str:
    raw = f"{race['name']}|{race.get('location', '')}|{race['start_date']}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{digest}@ultra-calendar"


def format_ics_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def create_event(race: dict) -> str:
    start = parse_date(race["start_date"])

    # ICS all-day event end dates are exclusive.
    if race.get("end_date"):
        end = parse_date(race["end_date"]) + timedelta(days=1)
    else:
        end = start + timedelta(days=1)

    description_parts = []

    if race.get("distance"):
        description_parts.append(f"Distance: {race['distance']}")
    if race.get("elevation"):
        description_parts.append(f"Elevation: {race['elevation']}")
    if race.get("status"):
        description_parts.append(f"Status: {race['status']}")
    if race.get("website"):
        description_parts.append(f"Website: {race['website']}")

    description = "\\n".join(description_parts)

    return "\n".join([
        "BEGIN:VEVENT",
        f"UID:{make_uid(race)}",
        f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{escape_ics(race['name'])}",
        f"DTSTART;VALUE=DATE:{format_ics_date(start)}",
        f"DTEND;VALUE=DATE:{format_ics_date(end)}",
        f"LOCATION:{escape_ics(race.get('location', ''))}",
        f"DESCRIPTION:{escape_ics(description)}",
        f"URL:{escape_ics(race.get('website', ''))}",
        "END:VEVENT",
    ])


def main() -> None:
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        races = yaml.safe_load(f)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ultra Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_ics(CALENDAR_NAME)}",
    ]

    for race in races:
        lines.append(create_event(race))

    lines.append("END:VCALENDAR")

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main() 