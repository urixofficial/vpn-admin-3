import asyncio

from core.config import settings
from core.logger import log

from core.tasks.scheduler import start_scheduler, stop_scheduler, setup_scheduler

from telegram.bot_init import bot
from telegram.bot import run_bot


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
