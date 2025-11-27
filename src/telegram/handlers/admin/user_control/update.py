from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
# from user.dto import UpdateUser
from .states import UserCrudStates
from .keyboards import get_update_keyboard

router = Router(name="update_user_router")

@router.message(UserCrudStates.show_profile, F.text == "Изменить")
async def update_user(message: Message, state: FSMContext):
	log.debug("Обновление пользователя")
	await message.answer("Изменить свойства пользователя:", reply_markup=get_update_keyboard())
	await state.set_state(UserCrudStates.update_user)

	# data = await state.get_data()
	# item_id = data["item_id"]

