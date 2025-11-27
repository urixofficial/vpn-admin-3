import asyncio

from aiogram import Dispatcher, Bot

from src.core.config import settings
from src.core.logger import log

from telegram.handlers import router as main_router
# from src.transaction.user_control import router as transaction_router



async def main():
	log.info("Запуск {} {}".format(settings.APP_NAME, settings.APP_VERSION))

	dp = Dispatcher()
	dp.include_router(main_router)
	# dp.include_router(transaction_router)
	# dp.include_router(core_router)

	bot = Bot(settings.TELEGRAM_TOKEN)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
