import asyncio

from core.config import settings
from core.logger import log
from telegram.bot_init import bot
from telegram.bot import run_bot


async def main():
	log.info("Запуск {} {}".format(settings.app.name, settings.app.version))

	await run_bot(bot)


if __name__ == "__main__":
	asyncio.run(main())
