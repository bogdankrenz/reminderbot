import logging
from datetime import date, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from awb import get_next_pickup, get_pickups_for_date, get_pickups_for_week
from config import TELEGRAM_CHAT_ID
from formatting import format_help, format_next_pickup, format_week, format_notification
from notifications import send_notification_to_all
from users import add_user, remove_user

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


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if add_user(chat_id):
        await update.message.reply_text(
            "✅ Registriert! Du erhältst ab jetzt Abfuhrbenachrichtigungen."
        )
    else:
        await update.message.reply_text("Du bist bereits registriert.")


async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if remove_user(chat_id):
        await update.message.reply_text(
            "🔕 Abgemeldet. Du erhältst keine Benachrichtigungen mehr."
        )
    else:
        await update.message.reply_text("Du warst nicht registriert.")


async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != TELEGRAM_CHAT_ID:
        await update.message.reply_text("Nicht autorisiert.")
        return

    tomorrow = date.today() + timedelta(days=1)
    types = get_pickups_for_date(tomorrow)

    if types:
        message = format_notification(tomorrow, types)
    else:
        message = "🔔 Test: System aktiv. Morgen keine Abfuhr."

    n = await send_notification_to_all(message)
    await update.message.reply_text(f"✅ Testnachricht an {n} Nutzer gesendet.")
