from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from core.config import settings
from core.logger import log
from core.repos.awg import awg_repo
from core.repos.user import user_repo
from telegram.handlers.user.keyboards import get_start_keyboard

router = Router(name="user_configs_router")


@router.message(Command("get_awg_config"))
@router.message(F.text == "Файл конфигурации AWG")
async def get_awg_config(message: Message):
	log.info(
		"Пользователь {} ({}) запросил файлы конфигурации".format(message.from_user.full_name, message.from_user.id)
	)
	user = await user_repo.get(message.from_user.id)
	if not user:
		await message.answer("Вы не зарегистрированы.", reply_markup=get_start_keyboard())
		return
	user_config = await awg_repo.get_config(message.from_user.id)
	if not user_config:
		await message.answer("При получении файла конфигурации произошла ошибка.")
		return
	filename = f"awg_{settings.awg.server_ip}_{message.from_user.id}.conf"
	config_bytes = user_config.encode("utf-8")
	document = BufferedInputFile(config_bytes, filename=filename)
	await message.bot.send_document(chat_id=message.from_user.id, document=document, caption="Ваш файл конфигурации")
	log.info("Файлы конфигурации отправлены пользователю")
