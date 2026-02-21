import logging
from datetime import date, timedelta

from telegram import Bot

from awb import get_pickups_for_date
from config import TELEGRAM_BOT_TOKEN
from formatting import format_notification
from users import load_users

logger = logging.getLogger(__name__)


async def send_notification_to_all(message: str) -> int:
    """Send an arbitrary message to all registered users. Returns count sent."""
    chat_ids = load_users()
    if not chat_ids:
        logger.warning("No registered users, nothing to send.")
        return 0

    sent = 0
    async with Bot(TELEGRAM_BOT_TOKEN) as bot:
        for chat_id in chat_ids:
            try:
                await bot.send_message(chat_id=chat_id, text=message)
                sent += 1
            except Exception as exc:
                logger.warning("Failed to send to %s: %s", chat_id, exc)
    return sent


async def check_and_notify() -> int:
    """Send a Telegram notification if tomorrow has a trash pickup."""
    tomorrow = date.today() + timedelta(days=1)
    types = get_pickups_for_date(tomorrow)

    if not types:
        logger.info("No pickup tomorrow (%s), skipping notification.", tomorrow)
        return 0

    message = format_notification(tomorrow, types)
    logger.info("Sending notification for %s: %s", tomorrow, types)
    return await send_notification_to_all(message)
