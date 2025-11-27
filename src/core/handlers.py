from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.logger import log

router = Router()


@router.message(CommandStart)
async def command_start(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /start".format(
		message.from_user.full_name,
		message.from_user.id
	))
