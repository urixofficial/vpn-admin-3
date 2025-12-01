from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from core.repos.user import user_repo
from ..keyboards import get_cancel_keyboard
from .keyboards import get_user_control_keyboard, get_profile_keyboard
from .states import UserCrudStates

router = Router(name="read_user_router")


@router.message(F.text == "Список пользователей")
async def list_users(message: Message):
	log.debug("Вывод списка пользователей")
	users = await user_repo.get_all()
	if not users:
		log.debug("Список пользователей пуст")
		await message.answer("Список пользователей пуст.")
		return
	text = "Список пользователей:\n--------------------------------------------\n"
	for number, user in enumerate(users, start=1):
		line = f"{'✅' if user.is_active else '🚫'} {user.name} ({user.id}) - {user.balance}₽\n"
		text += line
	await message.answer(text, reply_markup=get_user_control_keyboard())


@router.message(F.text == "Профиль пользователя")
async def show_user_step1(message: Message, state: FSMContext):
	log.debug("Вывод профиля пользователя. Запрос ID")
	await message.answer("Введите ID пользователя:", reply_markup=get_cancel_keyboard())
	await state.set_state(UserCrudStates.show_enter_id)


@router.message(UserCrudStates.show_enter_id)
async def show_user_step2(message: Message, state: FSMContext):
	log.debug("Получено значение: {}".format(message.text))
	try:
		user_id = int(message.text)
	except ValueError:
		log.debug("ID должен быть целым числом. Повторный запрос")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if user_id <= 0:
		log.debug("ID должен быть больше нуля. Повторный запрос")
		await message.answer(
			"ID должен быть положительным числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard()
		)
		return
	user = await user_repo.get(user_id)
	if not user:
		log.debug("Пользователь не найден. Повторный запрос")
		await message.answer("Пользователь не найден. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(user_id=user_id)
	text = (
		f"Пользователь {user.name}\n"
		"--------------------------------------------\n"
		f"ID: {user.id}\n"
		f"Статус: {'Активен' if user.is_active else 'Заблокирован'}\n"
		f"Баланс: {user.balance}₽\n"
		f"Дата расчета: {user.billing_date}\n"
		f"Создан: {user.created_at.date()}\n"
		f"Обновлен: {user.updated_at.date()}"
	)
	await message.answer(text, reply_markup=get_profile_keyboard())
	await state.set_state(UserCrudStates.show_profile)
