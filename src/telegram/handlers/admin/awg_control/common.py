from aiogram import Router, F
from aiogram.types import Message

from core.config import settings
from core.logger import log
from .keyboards import get_awg_control_keyboard

router = Router(name="common_awg_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "AWG")
async def awg_control(message: Message):
	log.debug("Вывод панели управления AWG")
	await message.answer("Управление AWG:", reply_markup=get_awg_control_keyboard())
