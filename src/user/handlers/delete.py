from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.core.logger import log
from src.user.handlers.states import CrudUserStates
from src.user.repo import delete_user
from src.user.handlers.keyboards import (
	get_confirmation_keyboard,
	get_user_control_keyboard,
)

router = Router(name="delete_user_router")


@router.message(CrudUserStates.show_profile, F.text == "Удалить")
async def delete_user_ste1(message: Message, state: FSMContext):
	log.debug("Удаление пользователя. Запрос подтверждения")

	await message.answer("Удалить пользователя?", reply_markup=get_confirmation_keyboard())
	await state.set_state(CrudUserStates.delete_confirmation)

@router.message(CrudUserStates.delete_confirmation, F.text == "Да")
async def delete_confirmation_ok(message: Message, state: FSMContext):
	log.debug("Подтверждение удаления получено")
	data = await state.get_data()
	user_id = data["user_id"]
	await delete_user(user_id)
	log.debug("Пользователь с id={} успешно удален".format(user_id))
	await message.answer("Пользователь успешно удален.", reply_markup=get_user_control_keyboard())

@router.message(CrudUserStates.delete_confirmation, F.text == "Нет")
async def delete_confirmation_no(message: Message, state: FSMContext):
	log.debug("Удаление отменено")
	await message.answer("Удаление отменено.", reply_markup=get_user_control_keyboard())
	await state.clear()
