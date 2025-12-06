from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.awg import awg_repo

from telegram.handlers.keyboards import get_confirmation_keyboard
from .keyboards import get_awg_control_keyboard
from .states import AwgCrudStates

router = Router(name="delete_awg_router")


@router.message(F.from_user.id == settings.tg.admin_id, AwgCrudStates.show_profile, F.text == "Удалить")
async def delete_awg_record_ste1(message: Message, state: FSMContext):
	log.info("Удаление записи AWG. Запрос подтверждения...")
	await message.answer("Удалить запись AWG?", reply_markup=get_confirmation_keyboard())
	await state.set_state(AwgCrudStates.delete_confirmation)


@router.message(F.from_user.id == settings.tg.admin_id, AwgCrudStates.delete_confirmation, F.text == "Да")
async def delete_confirmation_yes(message: Message, state: FSMContext):
	log.info("Подтверждение удаления получено")
	data = await state.get_data()
	awg_record_id = data["awg_record_id"]
	await awg_repo.delete(awg_record_id)
	log.info("Запись AWG {} успешно удалена".format(awg_record_id))
	await message.answer("Запись AWG успешно удалена.", reply_markup=get_awg_control_keyboard())


@router.message(F.from_user.id == settings.tg.admin_id, AwgCrudStates.delete_confirmation, F.text == "Нет")
async def delete_confirmation_no(message: Message, state: FSMContext):
	log.info("Удаление отменено")
	await message.answer("Удаление отменено.", reply_markup=get_awg_control_keyboard())
	await state.clear()
