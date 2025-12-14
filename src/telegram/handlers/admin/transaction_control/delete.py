from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.message import message_repo
from core.repos.transaction import transaction_repo
from core.schemas.message import CreateMessage

from .states import TransactionCrudStates
from telegram.handlers.keyboards import get_confirmation_keyboard
from .keyboards import get_transaction_control_keyboard

router = Router(name="delete_transaction_router")


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.show_profile, F.text == "Удалить")
async def delete_user_ste1(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Удаление транзакции. Запрос подтверждения...".format(
			message.from_user.full_name, message.from_user.id
		)
	)

	await message.answer("Удалить транзакцию?", reply_markup=get_confirmation_keyboard())
	await state.set_state(TransactionCrudStates.delete_confirmation)


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.delete_confirmation, F.text == "Да")
async def delete_confirmation_ok(message: Message, state: FSMContext):
	log.info("{} ({}): Подтверждение удаления получено".format(message.from_user.full_name, message.from_user.id))
	data = await state.get_data()
	transaction_id = data["transaction_id"]
	try:
		transaction = await transaction_repo.delete(transaction_id)
		log.info("Транзакция успешно удалена:\n{}".format(transaction))
		await message.answer("Транзакция успешно удалена.", reply_markup=get_transaction_control_keyboard())
		text = (
			"Оплата отменена\n"
			"-----------------------------------\n"
			f"Сумма: {transaction.amount}₽\n"
			f"Номер транзакции: {transaction.id:03d}"
		)
		user_notification = CreateMessage(chat_id=transaction.user_id, text=text)
		await message_repo.send_message(user_notification)
	except Exception as e:
		log.error("Ошибка: {}".format(e))
		await message.answer("Неизвестная ошибка.", reply_markup=get_transaction_control_keyboard())
		# raise
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.delete_confirmation, F.text == "Нет")
async def delete_confirmation_no(message: Message, state: FSMContext):
	log.info("{} ({}): Удаление отменено".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Удаление отменено.", reply_markup=get_transaction_control_keyboard())
	await state.clear()
