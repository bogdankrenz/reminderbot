from datetime import date

from awb import WASTE_TYPES

DAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONTHS_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def format_type(t: str) -> str:
    return WASTE_TYPES.get(t, t)


def format_types(types: list[str]) -> str:
    return ", ".join(format_type(t) for t in types)


def format_date_de(d: date) -> str:
    return f"{DAYS_DE[d.weekday()]}, {d.day}. {MONTHS_DE[d.month]} {d.year}"


def format_notification(d: date, types: list[str]) -> str:
    return (
        f"\U0001f5d1\ufe0f Morgen Abfuhr:\n"
        f"{format_types(types)}\n"
        f"({format_date_de(d)})"
    )


def format_next_pickup(d: date, types: list[str]) -> str:
    return (
        f"\U0001f4c5 Nächste Abfuhr:\n"
        f"{format_date_de(d)}\n"
        f"{format_types(types)}"
    )


def format_week(pickups: dict[date, list[str]]) -> str:
    if not pickups:
        return "\U0001f4c5 Diese Woche keine Abfuhr."
    lines = ["\U0001f4c5 Abfuhrtermine diese Woche:"]
    for d, types in pickups.items():
        lines.append(f"• {format_date_de(d)}: {format_types(types)}")
    return "\n".join(lines)


def format_help() -> str:
    return (
        "\U0001f916 goldiReminder — Abfuhrkalender\n\n"
        "/naechste — Nächster Abfuhrtermin\n"
        "/woche — Abfuhrtermine diese Woche\n"
        "/hilfe — Diese Hilfe\n\n"
        "Benachrichtigungen kommen automatisch um 19 Uhr am Abend vor einem Abfuhrtermin."
    )
