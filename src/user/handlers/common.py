from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.core.logger import log
from .keyboards import get_user_control_keyboard

router = Router(name="user_control_router")

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
	log.debug("Действие отменено")
	await state.clear()
	await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())

@router.message(Command("user_control"))
async def cmd_user_control(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /user_control".format(
		message.from_user.full_name,
		message.from_user.id
	))
	text = "Управление пользователями:"

	await message.answer(text, reply_markup=get_user_control_keyboard())