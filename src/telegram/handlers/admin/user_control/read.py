from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from core.repos.user import get_users, get_user
from .keyboards import get_user_control_keyboard, get_cancel_keyboard, get_user_profile_keyboard
from .states import CrudUserStates

router = Router(name="read_user_router")

@router.message(F.text == "Список пользователей")
async def cmd_list_users(message: Message):
	log.debug("Вывод списка пользователей")
	users_dto = await get_users()
	if not users_dto:
		log.debug("Список пользователей пуст")
		await message.answer("Список пользователей пуст")
		return
	text = (
		"Список пользователей:\n"
		"-----------------------------------\n"
	)
	for number, user in enumerate(users_dto, start=1):
		line = f"{number:02d}. {user.name} ({user.id})\n"
		text += line
	await message.answer(text, reply_markup=get_user_control_keyboard())

@router.message(F.text == "Профиль пользователя")
async def show_user_step1(message: Message, state: FSMContext):
	log.debug("Вывод профиля пользователя. Запрос ID")
	await message.answer("Введите ID пользователя:", reply_markup=get_cancel_keyboard())
	await state.set_state(CrudUserStates.show_enter_id)

@router.message(CrudUserStates.show_enter_id)
async def show_user_step2(message: Message, state: FSMContext):
	log.debug("Введен id={}".format(message.text))
	try:
		user_id = int(message.text)
	except ValueError:
		log.error("ID должен быть целым числом")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if user_id <= 0:
		log.error("ID должен быть больше нуля")
		await message.answer("ID должен быть положительным числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	user_dto = await get_user(user_id)
	if not user_dto:
		log.error("Пользователь с id={} не найден".format(user_id))
		await message.answer("Пользователь не найден.")
		return
	await state.update_data(user_id=user_id)
	text = (
		f"Пользователь {user_dto.name}\n"
		f"-----------------------------------\n"
		f"ID: {user_dto.id}\n"
		f"Баланс: {user_dto.balance}\n"
		f"Дата расчета: {user_dto.billing_date}\n"
		f"Создан: {user_dto.created_at.date()}\n"
		f"Обновлен: {user_dto.updated_at.date()}"
	)
	await message.answer(text, reply_markup=get_user_profile_keyboard())
	await state.set_state(CrudUserStates.show_profile)