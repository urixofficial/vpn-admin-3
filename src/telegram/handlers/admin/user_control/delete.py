from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from telegram.handlers.admin.user_control.states import UserCrudStates
from core.repos.user import user_repo

from telegram.handlers.keyboards import get_confirmation_keyboard
from .keyboards import get_user_control_keyboard

router = Router(name="delete_user_router")


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.show_profile, F.text == "Удалить")
async def delete_user_ste1(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Удаление пользователя. Запрос подтверждения...".format(
			message.from_user.full_name, message.from_user.id
		)
	)

	await message.answer("Удалить пользователя?", reply_markup=get_confirmation_keyboard())
	await state.set_state(UserCrudStates.delete_confirmation)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.delete_confirmation, F.text == "Да")
async def delete_confirmation_yes(message: Message, state: FSMContext):
	log.info("{} ({}): Подтверждение удаления получено".format(message.from_user.full_name, message.from_user.id))
	data = await state.get_data()
	user_id = data["user_id"]
	await user_repo.delete(user_id)
	log.info("Пользователь {} успешно удален".format(user_id))
	await message.answer("Пользователь успешно удален.", reply_markup=get_user_control_keyboard())


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.delete_confirmation, F.text == "Нет")
async def delete_confirmation_no(message: Message, state: FSMContext):
	log.info("{} ({}): Удаление отменено".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Удаление отменено.", reply_markup=get_user_control_keyboard())
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.delete_confirmation)
async def delete_confirmation_unknown(message: Message):
	log.info("{} ({}): Некорректный ввод".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Введите 'Да' или 'Нет':", reply_markup=get_confirmation_keyboard())
