from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile

from core.config import settings
from core.logger import log
from core.repos.awg import awg_repo
from core.repos.user import user_repo
from telegram.handlers.user.keyboards import get_start_keyboard, get_user_keyboard, get_instructions_keyboard

router = Router(name="common_user_router")


@router.message(CommandStart())
async def start(message: Message):
	log.info("Пользователь {} ({}) запустил бота".format(message.from_user.full_name, message.from_user.id))
	text = f"Приветствую, {message.from_user.full_name}!\n"
	user = await user_repo.get(message.from_user.id)
	if user:
		keyboard = get_user_keyboard
	else:
		text += "Вы не зарегистрированы."
		keyboard = get_start_keyboard
	await message.answer(text, reply_markup=keyboard())


@router.message(F.text == "Статус")
async def user_status(message: Message):
	log.info("Пользователь {} ({}) запросил статус".format(message.from_user.full_name, message.from_user.id))
	user = await user_repo.get(message.from_user.id)
	text = f"Статус: {'Активен' if user.is_active else 'Заблокирован'}\nБаланс: {user.balance}₽"
	await message.answer(text, reply_markup=get_user_keyboard())


@router.message(F.text == "Инструкции")
async def instructions(message: Message):
	log.info("Пользователь {} ({}) запросил инструкции".format(message.from_user.full_name, message.from_user.id))
	text = "Выберите систему:"
	await message.answer(text, reply_markup=get_instructions_keyboard())


@router.message(F.text == "Файл конфигурации AWG")
async def get_awg_config(message: Message):
	log.info(
		"Пользователь {} ({}) запросил файл конфигурации AWG".format(message.from_user.full_name, message.from_user.id)
	)
	filename = f"awg_{settings.awg.server_ip}_{message.from_user.id}.conf"
	config = await awg_repo.get_config(message.from_user.id)
	if not config:
		await message.answer("При получении файла конфигурации произошла ошибка.")
		return
	config_bytes = config.encode("utf-8")
	document = BufferedInputFile(config_bytes, filename=filename)
	await message.bot.send_document(chat_id=message.from_user.id, document=document, caption="Ваш файл конфигурации")
	log.info("Файл конфигурации отправлен пользователю")
