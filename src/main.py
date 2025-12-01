import asyncio

from core.config import settings
from core.logger import log
from core.tasks.debeting import debiting_funds
from core.tasks.scheduler import scheduler, start_scheduler, stop_scheduler

from telegram.bot_init import bot
from telegram.bot import run_bot


def test_task():
	log.debug("Тестовая задача выполнена")


def setup_scheduler():
	# Каждый день в 10:00 утра
	scheduler.add_job(
		debiting_funds,
		trigger="cron",
		hour=settings.billing.hour,
		minute=settings.billing.minute,
	)


async def main():
	log.info("Запуск {} {}".format(settings.app.name, settings.app.version))

	setup_scheduler()
	start_scheduler()

	try:
		await run_bot(bot)
	finally:
		stop_scheduler()  # на случай Ctrl+C


if __name__ == "__main__":
	asyncio.run(main())
