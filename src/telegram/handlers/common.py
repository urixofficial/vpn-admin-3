from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log

from telegram.handlers.admin.keyboards import get_admin_keyboard
from telegram.handlers.user.keyboards import get_user_keyboard

router = Router(name="common_router")


@router.message(F.text == "Отмена", F.from_user.id == settings.tg.admin_id)
async def admin_cancel(message: Message, state: FSMContext):
	log.debug("Действие отменено")
	await message.answer("Действие отменено.", reply_markup=get_admin_keyboard())
	await state.clear()


@router.message(F.text == "Отмена")
async def user_cancel(message: Message, state: FSMContext):
	log.debug("Действие отменено")
	await message.answer("Действие отменено.", reply_markup=get_user_keyboard())
	await state.clear()
