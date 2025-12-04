from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from core.config import settings
from core.repos.user import user_repo
from core.schemas.user import CreateUser
from telegram.handlers.admin.keyboards import get_admin_keyboard
from telegram.handlers.admin.user_control.states import AdminRegistrationStates
from telegram.handlers.user.keyboards import get_user_keyboard, get_start_keyboard

router = Router(name="admin_registration_router")


@router.message(F.from_user.id == settings.tg.admin_id, AdminRegistrationStates.confirmation, F.text == "Да")
async def admin_registration_yes(message: Message, state: FSMContext):
	log.debug("Заявка на регистрацию подтверждена администратором")
	user_data = await state.get_data()
	create_user = CreateUser(**user_data)
	try:
		user = await user_repo.create(create_user)
		log.info(f"Пользователь {user.name} ({user.id}) успешно зарегистрирован")
		await message.answer(
			f"Пользователь {user.name} ({user.id}) успешно зарегистрирован.", reply_markup=get_admin_keyboard()
		)
		await message.bot.send_message(
			user.id,
			"Регистрация подтверждена!",
			reply_markup=get_user_keyboard(),
		)
	except Exception as e:
		log.error(f"Ошибка создания пользователя: {e}")
		await message.answer("Ошибка при создании пользователя.", reply_markup=get_admin_keyboard())
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, AdminRegistrationStates.confirmation, F.text == "Нет")
async def admin_registration_no(message: Message, state: FSMContext):
	log.debug("Регистрация на регистрацию отклонена администратором")
	user_data = await state.get_data()
	user_id = user_data["id"]
	await message.answer("Заявка отклонена.", reply_markup=get_admin_keyboard())
	await message.bot.send_message(user_id, "Ваша заявка на регистрацию отклонена.", reply_markup=get_start_keyboard())
	await state.clear()
