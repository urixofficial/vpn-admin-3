import asyncio

from core.config import settings
from core.logger import log
from telegram.bot import run_bot


async def main():
	log.info("Запуск {} {}".format(settings.APP_NAME, settings.APP_VERSION))

	await run_bot()


if __name__ == "__main__":
	asyncio.run(main())
