from aiogram import Router, F
from aiogram.types import Message

from core.logger import log
from .keyboards import get_user_control_keyboard

router = Router(name="user_control_panel_router")


@router.message(F.text == "Пользователи")
async def cmd_user_control(message: Message):
	log.debug("Вывод панели управления пользователями")
	await message.answer("Управление пользователями:", reply_markup=get_user_control_keyboard())
