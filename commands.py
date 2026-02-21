import logging
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from awb import get_next_pickup, get_pickups_for_week
from formatting import format_help, format_next_pickup, format_week

logger = logging.getLogger(__name__)


async def naechste_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = get_next_pickup(date.today())
    if result is None:
        await update.message.reply_text("Keine bevorstehenden Abfuhrtermine gefunden.")
        return
    d, types = result
    await update.message.reply_text(format_next_pickup(d, types))


async def woche_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pickups = get_pickups_for_week()
    await update.message.reply_text(format_week(pickups))


async def hilfe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_help())
