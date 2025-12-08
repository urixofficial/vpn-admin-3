from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from core.repos.user import user_repo
from telegram.handlers.user.keyboards import get_start_keyboard, get_user_keyboard, get_instructions_keyboard
from telegram.handlers.user.states import UserInstructionsState

router = Router(name="common_user_router")


@router.message(F.text == "Статус")
async def user_status(message: Message):
	log.info("Пользователь {} ({}) запросил статус".format(message.from_user.full_name, message.from_user.id))
	user = await user_repo.get(message.from_user.id)
	if not user:
		await message.answer("Вы не зарегистрированы.", reply_markup=get_start_keyboard())
		return
	balance = f"{user.balance}₽" if isinstance(user.balance, int) else "∞"
	text = f"Статус: {'Активен' if user.is_active else 'Заблокирован'}\nБаланс: {balance}"
	await message.answer(text, reply_markup=get_user_keyboard())


@router.message(F.text == "Инструкции")
async def instructions(message: Message, state: FSMContext):
	log.info("Пользователь {} ({}) запросил инструкции".format(message.from_user.full_name, message.from_user.id))
	user = await user_repo.get(message.from_user.id)
	if not user:
		await message.answer("Вы не зарегистрированы.", reply_markup=get_start_keyboard())
		return
	text = "Выберите систему:"
	await message.answer(text, reply_markup=get_instructions_keyboard())
	await state.set_state(UserInstructionsState.choose)


@router.message(CommandStart())
@router.message()
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
