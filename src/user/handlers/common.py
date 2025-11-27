from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from .keyboards import get_user_control_keyboard

router = Router(name="user_control_router")

@router.message(F.text == "Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
	log.debug("Действие отменено")
	await message.answer("Действие отменено.", reply_markup=get_user_control_keyboard())
	await state.clear()

@router.message(Command("user_control"))
async def cmd_user_control(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /user_control".format(
		message.from_user.full_name,
		message.from_user.id
	))
	await message.answer("Управление пользователями:", reply_markup=get_user_control_keyboard())