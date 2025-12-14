from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log

from telegram.handlers.admin.keyboards import get_admin_keyboard

router = Router(name="common_router")


@router.message(Command("admin"), F.from_user.id == settings.tg.admin_id)
async def admin_panel(message: Message, state: FSMContext):
	log.info("{} ({}): Вывод панели администратора".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Панель администратора:", reply_markup=get_admin_keyboard())
	await state.clear()
