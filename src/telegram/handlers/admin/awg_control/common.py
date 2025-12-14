from aiogram import Router, F
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.awg import awg_repo
from .keyboards import get_awg_control_keyboard

router = Router(name="common_awg_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "AWG")
async def awg_control(message: Message):
	log.info("{} ({}): Вывод панели управления AWG".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Управление AWG:", reply_markup=get_awg_control_keyboard())


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Перезапуск интерфейса AWG")
async def restart_interface(message: Message):
	log.info("{} ({}): Перезапуск интерфейса AWG".format(message.from_user.full_name, message.from_user.id))
	status = await awg_repo.restart_interface(message.from_user.id)
	if status:
		log.info("Интерфейс AWG успешно перезапущен")
		await message.answer("Интерфейс AWG перезапущен.")
	else:
		log.error("Ошибка при перезапуске интерфейса")
		await message.answer("Ошибка при перезапуске интерфейса.")
