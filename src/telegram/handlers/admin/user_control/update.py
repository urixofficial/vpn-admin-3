from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.user import user_repo
from core.schemas.user import UpdateUser

# from user.dto import UpdateUser
from .states import UserCrudStates
from ..keyboards import get_update_keyboard, get_admin_keyboard
from ...keyboards import get_cancel_keyboard, get_confirmation_keyboard

router = Router(name="update_user_router")


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.show_profile, F.text == "Изменить")
async def update_user(message: Message, state: FSMContext):
	log.info("{} ({}): Обновление данных пользователя".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Выберете поле для изменения:", reply_markup=get_update_keyboard(UpdateUser))
	await state.set_state(UserCrudStates.update_user)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.update_user, F.text.in_(UpdateUser.model_fields))
async def edit_user_field_step1(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Изменение поля '{}'. Запрос значения...".format(
			message.from_user.full_name, message.from_user.id, message.text
		)
	)
	await state.update_data(key=message.text)
	await message.answer(f"Введите новое значение '{message.text}':", reply_markup=get_cancel_keyboard())
	await state.set_state(UserCrudStates.edit_field)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.edit_field)
async def edit_user_field_step2(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Получено значение: '{}'. Проверка и установка значения".format(
			message.from_user.full_name, message.from_user.id, message.text
		)
	)
	data = await state.get_data()
	user_id = data["user_id"]
	key = data["key"]
	value = message.text
	update_data = {key: value}
	try:
		user = await user_repo.update(user_id, UpdateUser(**update_data))
		log.info("Запись успешно обновлена:\n{}".format(user))
		balance = f"{user.balance}₽" if isinstance(user.balance, int) else "∞"
		text = (
			"Запись успешно обновлена\n"
			"--------------------------------------------\n"
			f"ID: {user.id}\n"
			f"Имя: {user.name}\n"
			f"Статус: {'Активен' if user.is_active else 'Заблокирован'}\n"
			f"Баланс: {balance}\n"
			f"Создан: {user.created_at.date()}\n"
			f"Обновлен: {user.updated_at.date()}"
		)
		await message.answer(text, reply_markup=get_update_keyboard(UpdateUser))
	except Exception as e:
		log.error("Ошибка при обновлении значения {} = {}: {}".format(key, value, e))
		await message.answer("Некорректный ввод.", reply_markup=get_update_keyboard(UpdateUser))
	await state.set_state(UserCrudStates.update_user)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.show_profile, F.text == "Безлимит")
async def set_user_balance_unlimited(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Установка безлимитного баланса пользователю. Запрос подтверждения...".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	fsm_data = await state.get_data()
	user_id = fsm_data["user_id"]
	user = await user_repo.get(user_id)
	await message.answer(
		f"Установить пользователю {user.name} ({user.id}) безлимитный баланс?", reply_markup=get_confirmation_keyboard()
	)
	await state.set_state(UserCrudStates.set_unlimited)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.set_unlimited, F.text == "Да")
async def set_user_balance_unlimited_yes(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Подтверждение безлимитного баланса получено. Обновление записи в базе данных".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	fsm_data = await state.get_data()
	user_id = fsm_data["user_id"]
	try:
		user = await user_repo.set_unlimited(user_id)
		balance = f"{user.balance}₽" if isinstance(user.balance, int) else "∞"
		text = (
			"Запись успешно обновлена\n"
			"--------------------------------------------\n"
			f"ID: {user.id}\n"
			f"Имя: {user.name}\n"
			f"Статус: {'Активен' if user.is_active else 'Заблокирован'}\n"
			f"Баланс: {balance}\n"
			f"Создан: {user.created_at.date()}\n"
			f"Обновлен: {user.updated_at.date()}"
		)
		await message.answer(text, reply_markup=get_admin_keyboard())
		await state.clear()
	except Exception as e:
		log.error("Ошибка при установке безлимитного баланса пользователю #{}: {}".format(user_id, e))


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.set_unlimited, F.text == "Нет")
async def set_user_balance_unlimited_no(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Установка безлимитного баланса отклонена. Вывод панели администратора".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	await message.answer("Установка безлимитного баланса отклонена.", reply_markup=get_admin_keyboard())
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.set_unlimited)
async def set_user_balance_unlimited_unknown(message: Message):
	log.info("{} ({}): Некорректный ввод".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Введите 'Да' или 'Нет':", reply_markup=get_confirmation_keyboard())
