import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application, CommandHandler

from awb import refresh_cache
from commands import hilfe_handler, naechste_handler, woche_handler
from config import SCHEDULE_HOUR, SCHEDULE_MINUTE, TELEGRAM_BOT_TOKEN, TIMEZONE
from notifications import check_and_notify

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

tz = pytz.timezone(TIMEZONE)
scheduler = AsyncIOScheduler(timezone=tz)


async def on_startup(application: Application) -> None:
    logger.info("Refreshing AWB calendar cache on startup...")
    try:
        refresh_cache()
        logger.info("Startup cache refresh complete.")
    except Exception as exc:
        logger.warning("Startup cache refresh failed: %s", exc)

    scheduler.start()
    logger.info("Scheduler started (19:00 notify, 03:00 cache refresh).")


async def on_shutdown(application: Application) -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")


def main() -> None:
    # Daily cache refresh at 03:00
    scheduler.add_job(
        refresh_cache,
        CronTrigger(hour=3, minute=0, timezone=tz),
        id="cache_refresh",
        name="Daily cache refresh",
    )

    # Evening notification (default 19:00, configurable via SCHEDULE_TIME)
    scheduler.add_job(
        check_and_notify,
        CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, timezone=tz),
        id="evening_notify",
        name="Evening notification",
        misfire_grace_time=300,
    )

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("naechste", naechste_handler))
    app.add_handler(CommandHandler("woche", woche_handler))
    app.add_handler(CommandHandler("hilfe", hilfe_handler))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
