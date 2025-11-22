import asyncio
from aiogram import Dispatcher, Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.core.config import settings
from src.core.logger import log

router = Router()

@router.message(CommandStart)
async def command_start(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /start".format(
		message.from_user.full_name,
		message.from_user.id
	))

async def main():
	log.debug("Запуск {} {}".format(settings.APP_NAME, settings.APP_VERSION))

	dp = Dispatcher()
	dp.include_router(router)
	bot = Bot(settings.TELEGRAM_TOKEN)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
