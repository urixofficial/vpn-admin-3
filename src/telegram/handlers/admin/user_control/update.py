from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.user import user_repo
from core.schemas.user import UpdateUser

# from user.dto import UpdateUser
from .states import UserCrudStates
from ..keyboards import get_update_keyboard
from ...keyboards import get_cancel_keyboard

router = Router(name="update_user_router")


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.show_profile, F.text == "Изменить")
async def update_user(message: Message, state: FSMContext):
	log.debug("Обновление пользователя")
	await message.answer("Изменить свойства пользователя:", reply_markup=get_update_keyboard(UpdateUser))
	await state.set_state(UserCrudStates.update_user)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.update_user, F.text.in_(UpdateUser.model_fields))
async def edit_user_field_step1(message: Message, state: FSMContext):
	log.info("Изменение свойства пользователя: {}. Запрос значения...".format(message.text))
	await state.update_data(key=message.text)
	await message.answer(f"Введите новое значение {message.text}:", reply_markup=get_cancel_keyboard())
	await state.set_state(UserCrudStates.edit_field)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.edit_field)
async def edit_user_field_step2(message: Message, state: FSMContext):
	log.info("Изменение свойства пользователя: {}. Проверка и установка значения".format(message.text))
	data = await state.get_data()
	user_id = data["user_id"]
	key = data["key"]
	value = message.text
	update_data = {key: value}
	try:
		user = await user_repo.update(user_id, UpdateUser(**update_data))
		log.info("Запись успешно обновлена: {}".format(user))
		await message.answer("Запись успешно обновлена.", reply_markup=get_update_keyboard(UpdateUser))
	except Exception as e:
		log.error("Ошибка при обновлении значения {} = {}: {}".format(key, value, e))
		await message.answer("Некорректный ввод.", reply_markup=get_update_keyboard(UpdateUser))
	await state.set_state(UserCrudStates.update_user)
