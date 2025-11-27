from aiogram import Dispatcher, Bot
from telegram.handlers import router as main_router

from core.config import settings
from core.logger import log


async def run_bot():
	log.debug("Запуск бота...")

	dp = Dispatcher()
	dp.include_router(main_router)

	bot = Bot(settings.TELEGRAM_TOKEN)
	await dp.start_polling(bot)
