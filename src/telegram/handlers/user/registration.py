from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.user import user_repo
from telegram.handlers.user.keyboards import get_cancel_keyboard, get_confirmation_keyboard, get_user_keyboard
from telegram.handlers.user.states import RegistrationStates

router = Router(name="registration_router")


@router.message(F.text == "Регистрация")
async def registration_step1(message: Message, state: FSMContext):
	log.debug(
		"Пользователь {} ({}) запустил диалог регистрации".format(message.from_user.full_name, message.from_user.id)
	)
	text = "Введите уникальное имя или псевдоним:"
	await message.answer(text, reply_markup=get_cancel_keyboard())
	await state.set_state(RegistrationStates.enter_name)


@router.message(RegistrationStates.enter_name)
async def registration_step2(message: Message, state: FSMContext):
	log.debug("Получено значение: {}".format(message.text))
	name = message.text
	if not 3 < len(name) < 24:
		log.debug("Некорректный ввод. Повторный запрос")
		await message.answer("Имя должно быть от 3 до 24 символов. Попробуйте еще раз:")
		return
	user = await user_repo.get_by_name(name)
	if user:
		log.debug("Некорректный ввод. Повторный запрос")
		await message.answer("Имя не уникально. Попробуйте еще раз:")
		return
	text = "Отправить запрос администратору?"
	await message.answer(text, reply_markup=get_confirmation_keyboard())
	await state.set_state(RegistrationStates.confirmation)


@router.message(RegistrationStates.confirmation, F.text == "Да")
async def registration_confirmation_yes(message: Message, state: FSMContext):
	log.debug("Подтверждение получено")
	await message.bot.send_message(
		chat_id=settings.tg.admin_id,
		text=f"Пользователь {message.from_user.full_name} ({message.from_user.id}) отправил запрос на регистрацию.\n"
		f"----------------------------------------\n"
		f"Подтвердить?",
		reply_markup=get_confirmation_keyboard(),
	)
	await message.answer("Запрос на регистрацию отправлен")
	await state.clear()


@router.message(RegistrationStates.confirmation, F.text == "Нет")
async def registration_confirmation_no(message: Message, state: FSMContext):
	log.debug("Регистрация отменена")
	await message.answer("Регистрация отменена", reply_markup=get_user_keyboard())
	await state.clear()
