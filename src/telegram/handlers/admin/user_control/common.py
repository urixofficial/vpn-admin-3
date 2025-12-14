from aiogram import Router, F
from aiogram.types import Message

from core.config import settings
from core.logger import log
from .keyboards import get_user_control_keyboard

router = Router(name="user_control_panel_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Пользователи")
async def cmd_user_control(message: Message):
	log.info(
		"{} ({}): Вывод панели управления пользователями".format(message.from_user.full_name, message.from_user.id)
	)
	await message.answer("Управление пользователями:", reply_markup=get_user_control_keyboard())
