from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
# from user.dto import UpdateUserDto
from .states import CrudUserStates
from .keyboards import get_update_user_keyboard

router = Router(name="update_user_router")

@router.message(CrudUserStates.show_profile, F.text == "Изменить")
async def update_user(message: Message, state: FSMContext):
	log.debug("Обновление пользователя")
	await message.answer("Изменить свойства пользователя:", reply_markup=get_update_user_keyboard())
	await state.set_state(CrudUserStates.update_user)









	# data = await state.get_data()
	# user_id = data["user_id"]

