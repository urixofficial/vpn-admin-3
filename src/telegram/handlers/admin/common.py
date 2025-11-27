from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log

from .keyboards import get_admin_panel_keyboard

router = Router(name="common_router")

@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
	log.debug("Действие отменено")
	await message.answer("Действие отменено.", reply_markup=get_admin_panel_keyboard())
	await state.clear()

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
	log.debug("Вывод панели администратора")
	await message.answer("Панель администратора:", reply_markup=get_admin_panel_keyboard())
	await state.clear()
