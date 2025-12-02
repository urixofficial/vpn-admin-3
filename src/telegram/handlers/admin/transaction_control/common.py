from aiogram import Router, F
from aiogram.types import Message

from core.config import settings
from core.logger import log

from .keyboards import get_transaction_control_keyboard

router = Router(name="transaction_control_panel_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Транзакции")
async def transaction_control_panel(message: Message):
	log.debug("Вывод панели управления транзакциями")
	await message.answer("Управление транзакциями:", reply_markup=get_transaction_control_keyboard())
