import asyncio

from aiogram import Dispatcher, Bot

from src.core.config import settings
from src.core.logger import log

from src.core.database import init_db
from src.user.handlers import router as user_router
# from src.transaction.handlers import router as transaction_router



async def main():
	log.debug("Запуск {} {}".format(settings.APP_NAME, settings.APP_VERSION))

	await init_db()

	dp = Dispatcher()
	dp.include_router(user_router)
	# dp.include_router(transaction_router)
	# dp.include_router(core_router)

	bot = Bot(settings.TELEGRAM_TOKEN)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
