import json
import logging
from datetime import date
from typing import Optional

import httpx

from config import AWB_API_BASE, AWB_BUILDING_NUMBER, AWB_STREET_CODE, CACHE_FILE, DATA_DIR

logger = logging.getLogger(__name__)

WASTE_TYPES: dict[str, str] = {
    "grey": "Restmülltonne",
    "brown": "Biotonne",
    "blue": "Papiertonne",
    "wertstoff": "Wertstofftonne",
    "xmastree": "Weihnachtsbaum",
}


def _api_url(year: int) -> str:
    return (
        f"{AWB_API_BASE}?building_number={AWB_BUILDING_NUMBER}"
        f"&street_code={AWB_STREET_CODE}"
        f"&start_year={year}&end_year={year}"
        f"&start_month=1&end_month=12&form=json"
    )


def refresh_cache() -> None:
    """Fetch calendar data from AWB API and write to disk cache."""
    today = date.today()
    years = [today.year]
    if today.month >= 11:
        years.append(today.year + 1)

    all_entries: list[dict] = []
    with httpx.Client(timeout=30) as client:
        for year in years:
            url = _api_url(year)
            logger.info("Fetching AWB calendar for year %d", year)
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            all_entries.extend(data.get("data", []))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps({"data": all_entries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Cache written to %s (%d entries)", CACHE_FILE, len(all_entries))


def _load_cache() -> list[dict]:
    if not CACHE_FILE.exists():
        logger.warning("Cache file not found, fetching now...")
        refresh_cache()
    return json.loads(CACHE_FILE.read_text(encoding="utf-8")).get("data", [])


def get_pickups_for_date(d: date) -> list[str]:
    """Return list of waste type strings for a given date."""
    return [
        e["type"]
        for e in _load_cache()
        if e["day"] == d.day and e["month"] == d.month and e["year"] == d.year
    ]


def get_next_pickup(from_date: Optional[date] = None) -> Optional[tuple[date, list[str]]]:
    """Return (date, types) for the next pickup on or after from_date."""
    if from_date is None:
        from_date = date.today()

    pickups: dict[date, list[str]] = {}
    for e in _load_cache():
        d = date(e["year"], e["month"], e["day"])
        if d >= from_date:
            pickups.setdefault(d, []).append(e["type"])

    if not pickups:
        return None
    earliest = min(pickups)
    return earliest, pickups[earliest]


def get_pickups_for_week(week_start: Optional[date] = None) -> dict[date, list[str]]:
    """Return dict of date -> [types] for the 7 days starting at week_start (Monday)."""
    from datetime import timedelta

    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)

    result: dict[date, list[str]] = {}
    for e in _load_cache():
        d = date(e["year"], e["month"], e["day"])
        if week_start <= d <= week_end:
            result.setdefault(d, []).append(e["type"])

    return dict(sorted(result.items()))
