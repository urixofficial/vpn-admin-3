from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.logger import log

router = Router()


@router.message(CommandStart)
async def command_start(message: Message):
	user_name = message.from_user.full_name if message.from_user else "Неизвестный"
	user_id = message.from_user.id if message.from_user else "Неизвестный"
	log.debug("Пользователь {} ({}) выполнил команду /start".format(user_name, user_id))

