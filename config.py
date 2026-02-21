import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID: int = int(os.environ["TELEGRAM_CHAT_ID"])

SCHEDULE_TIME: str = os.getenv("SCHEDULE_TIME", "19:00")
TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Berlin")
DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))

# Parse AWB address parameters from CALENDAR_URL (fragment contains JSON-encoded street data)
_calendar_url = os.getenv("CALENDAR_URL", "")
if _calendar_url:
    _fragment = urlparse(_calendar_url).fragment
    _params = parse_qs(_fragment)  # parse_qs URL-decodes values automatically
    _street_raw = _params.get("street", ["{}"])[0]
    _street = json.loads(_street_raw)
    AWB_BUILDING_NUMBER: str = _street.get("building_number", "235")
    AWB_STREET_CODE: str = _street.get("street_code", "1162")
else:
    AWB_BUILDING_NUMBER = os.getenv("AWB_BUILDING_NUMBER", "235")
    AWB_STREET_CODE = os.getenv("AWB_STREET_CODE", "1162")

_hour, _minute = SCHEDULE_TIME.split(":")
SCHEDULE_HOUR: int = int(_hour)
SCHEDULE_MINUTE: int = int(_minute)

CACHE_FILE: Path = DATA_DIR / "calendar.json"
AWB_API_BASE: str = "https://www.awbkoeln.de/api/calendar"
