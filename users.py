import json
import logging

from config import DATA_DIR, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

USERS_FILE = DATA_DIR / "users.json"


def load_users() -> list[int]:
    """Read chat IDs from disk, return [] on missing file."""
    if not USERS_FILE.exists():
        return []
    try:
        data = json.loads(USERS_FILE.read_text())
        return [int(cid) for cid in data.get("chat_ids", [])]
    except Exception as exc:
        logger.warning("Failed to load users file: %s", exc)
        return []


def save_users(chat_ids: list[int]) -> None:
    """Write user list atomically to USERS_FILE."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = USERS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"chat_ids": chat_ids}))
    tmp.replace(USERS_FILE)


def add_user(chat_id: int) -> bool:
    """Add chat_id if not present. Returns True if newly added."""
    chat_ids = load_users()
    if chat_id in chat_ids:
        return False
    chat_ids.append(chat_id)
    save_users(chat_ids)
    return True


def remove_user(chat_id: int) -> bool:
    """Remove chat_id if present. Returns True if it was found."""
    chat_ids = load_users()
    if chat_id not in chat_ids:
        return False
    chat_ids.remove(chat_id)
    save_users(chat_ids)
    return True


def seed_owner() -> None:
    """Ensure TELEGRAM_CHAT_ID is always in the user list."""
    add_user(TELEGRAM_CHAT_ID)
