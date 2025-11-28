from aiogram import Dispatcher, Bot
from telegram.handlers import router as main_router

from core.logger import log


async def run_bot(bot: Bot):
	log.debug("Запуск бота...")
	dp = Dispatcher()
	dp.include_router(main_router)
	await dp.start_polling(bot)
