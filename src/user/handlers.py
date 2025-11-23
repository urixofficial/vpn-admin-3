from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.core.logger import log

from src.user.repo import create_user
from src.user.dto import CreateUserDto

router = Router(name="user_router")

@router.message(Command("create_user"))
async def cmd_create_user(message: Message):
	log.debug(
		"Пользователь {} ({}) выполнил команду /create_user".format(
			message.from_user.full_name, message.from_user.id
		)
	)

	user = CreateUserDto(id=12345678, name="John Smith")

	user_id = await create_user(user)
	if user_id:
		log.info("Пользователь {} успешно добавлен".format(user))
		await message.answer("Пользователь успешно добавлен")
	else:
		log.error("Ошибка при добавлении пользователя {}".format(user))
		await message.answer("Ошибка при добавлении пользователя")


@router.message(Command("update_user"))
async def update_user(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /update_user".format(
		message.from_user.full_name,
		message.from_user.id
	))

@router.message(Command("delete_user"))
async def delete_user(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /delete_user".format(
		message.from_user.full_name,
		message.from_user.id
	))