import logging
from datetime import date, timedelta

from telegram import Bot

from awb import get_pickups_for_date
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from formatting import format_notification

logger = logging.getLogger(__name__)


async def check_and_notify() -> None:
    """Send a Telegram notification if tomorrow has a trash pickup."""
    tomorrow = date.today() + timedelta(days=1)
    types = get_pickups_for_date(tomorrow)

    if not types:
        logger.info("No pickup tomorrow (%s), skipping notification.", tomorrow)
        return

    message = format_notification(tomorrow, types)
    logger.info("Sending notification for %s: %s", tomorrow, types)

    async with Bot(TELEGRAM_BOT_TOKEN) as bot:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
