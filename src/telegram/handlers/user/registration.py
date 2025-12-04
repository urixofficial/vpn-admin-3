from aiogram import Router, F, Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.user import user_repo
from telegram.handlers.admin.user_control.states import AdminRegistrationStates
from telegram.handlers.user.keyboards import get_cancel_keyboard, get_confirmation_keyboard, get_user_keyboard
from telegram.handlers.user.states import UserRegistrationStates

router = Router(name="registration_router")


@router.message(F.text == "Регистрация")
async def registration_step1(message: Message, state: FSMContext):
	log.debug(
		"Пользователь {} ({}) запустил диалог регистрации. Запрос имени...".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	text = "Введите уникальное имя или псевдоним:"
	await message.answer(text, reply_markup=get_cancel_keyboard())
	await state.set_state(UserRegistrationStates.enter_name)


@router.message(UserRegistrationStates.enter_name)
async def registration_step2(message: Message, state: FSMContext):
	log.debug("Получено значение: {}".format(message.text))
	name = message.text
	if not 3 <= len(name) <= 24:
		log.debug("Некорректный ввод. Повторный запрос")
		await message.answer("Имя должно быть от 3 до 24 символов. Попробуйте еще раз:")
		return
	user = await user_repo.get_by_name(name)
	if user:
		log.debug("Некорректный ввод. Повторный запрос")
		await message.answer("Имя не уникально. Попробуйте еще раз:")
		return
	await state.update_data(name=name)
	text = "Отправить запрос администратору?"
	await message.answer(text, reply_markup=get_confirmation_keyboard())
	await state.set_state(UserRegistrationStates.confirmation)


@router.message(UserRegistrationStates.confirmation, F.text == "Да")
async def registration_confirmation_yes(message: Message, state: FSMContext, dispatcher: Dispatcher, bot: Bot):
	log.debug("Подтверждение регистрации от пользователя получено. Отправка запроса на подтверждение администратору...")
	data = await state.get_data()
	name = data["name"]
	admin_state: FSMContext = dispatcher.fsm.get_context(
		bot=bot,
		chat_id=settings.tg.admin_id,
		user_id=settings.tg.admin_id,
	)
	await admin_state.update_data(
		id=message.from_user.id,
		name=name,
	)
	await message.bot.send_message(
		chat_id=settings.tg.admin_id,
		text=f"Пользователь {name} ({message.from_user.id}) отправил запрос на регистрацию.\n"
		f"----------------------------------------\n"
		f"Подтвердить?",
		reply_markup=get_confirmation_keyboard(),
	)
	await admin_state.set_state(AdminRegistrationStates.confirmation)
	await message.answer("Запрос на регистрацию отправлен.")
	await state.clear()


@router.message(UserRegistrationStates.confirmation, F.text == "Нет")
async def registration_confirmation_no(message: Message, state: FSMContext):
	log.debug("Регистрация отменена")
	await message.answer("Регистрация отменена.", reply_markup=get_user_keyboard())
	await state.clear()
