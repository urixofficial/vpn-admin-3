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
async def update_server_config(message: Message):
	log.info("{} ({}): Обновление конфигурации сервера".format(message.from_user.full_name, message.from_user.id))
	status = awg_repo.update_server_config()
	if status:
		log.info("Конфигурация сервера успешно обновлена")
		await message.answer("Интерфейс AWG перезапущен.", reply_markup=get_awg_control_keyboard())
	else:
		log.error("Ошибка при обновлении конфигурации сервера")
		await message.answer("Ошибка при обновлении конфигурации сервера.", reply_markup=get_awg_control_keyboard())
