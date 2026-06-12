# Ultra Calendar

A self-hosted calendar of ultra trail running races.

This project maintains a structured database of races in YAML format and generates a standards-compliant iCalendar (`.ics`) feed that can be subscribed to from Apple Calendar, Google Calendar, Outlook, and other calendar applications.

The goal is to maintain a personal bucket list of ultra trail races while automatically distributing updates through a calendar subscription.

<figure align="center">
  <a href="https://www.tyrol.com/activities/sport/trailrunning/trail-running-a-guide-to-getting-started">
    <img src="media/banner.svg" alt="Ultra Calendar banner" width="600" />
  </a>
  <figcaption>Source: <a href="https://www.tyrol.com/activities/sport/trailrunning/trail-running-a-guide-to-getting-started">Tyrol.com trail running guide</a></figcaption>
</figure>

## Features

* Simple YAML-based race database
* Generate iCalendar (`.ics`) feeds
* Apple Calendar compatible
* Self-hosted on any Linux server
* Git-based workflow
* Easy to extend with race date scrapers and automation
* No dependency on Airtable, Notion, or third-party services

---

## Project Structure

```text
ultra-calendar/
├── .venv/
├── races.yaml
├── generate_ics.py
├── requirements.txt
├── README.md
├── calendar.ics
└── scripts/
    └── update.sh
```

---

## Requirements

* Python 3.12+
* Linux server (recommended)
* Git
* Nginx (optional, for hosting)

---

## Installation

Clone the repository:

```bash
git clone git@github.com:luisaneubauer/ultra-calendar.git
cd ultra-calendar
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Race Database

Races are stored in `races.yaml`.

Example:

```yaml
- name: UTMB
  location: Chamonix, France
  start_date: 2027-08-27
  end_date: 2027-08-29
  website: https://utmb.world
  distance: 171 km
  elevation: 10000 m

- name: Lavaredo Ultra Trail
  location: Cortina d'Ampezzo, Italy
  start_date: 2027-06-25
  end_date: 2027-06-26
  website: https://lavaredo.utmb.world
  distance: 120 km
  elevation: 5800 m
```

---

## Generate Calendar

Run:

```bash
python generate_ics.py
```

This creates:

```text
calendar.ics
```

---

## Hosting

The generated `calendar.ics` file can be served using:

* Nginx
* Apache
* GitHub Pages
* Any static web server

Example URL:

```text
https://calendar.example.com/calendar.ics
```

---

## Apple Calendar Subscription

In Apple Calendar:

```text
File
→ New Calendar Subscription
→ Enter calendar URL
```

Example:

```text
webcal://calendar.example.com/calendar.ics
```

The calendar will automatically refresh when the feed changes.

---

## Updating

After modifying `races.yaml`:

```bash
python generate_ics.py
```

If hosted on a server, redeploy the updated `calendar.ics`.

---

## Automated Deployment

Example update script:

```bash
#!/bin/bash

set -e

cd /srv/ultra-calendar

git pull origin main

source .venv/bin/activate

python generate_ics.py
```

Schedule with cron:

```cron
0 * * * * /srv/ultra-calendar/scripts/update.sh
```

---

## Future Roadmap

### Race Metadata

* Distance
* Elevation gain
* UTMB Index
* UTMB Stones
* Qualification requirements
* Registration deadlines

### Automation

* Detect next-year race dates automatically
* Scrape official race websites
* Weekly update jobs
* Automatic feed regeneration

### Filtering

* Bucket List
* Registered
* Completed
* UTMB World Series
* Backyard Ultras

---

## License

MIT License

---

## Disclaimer

Race dates should always be verified on official race websites before making travel or registration decisions. This project is intended as a personal planning and tracking tool.
