from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.transaction import transaction_repo
from core.schemas.transaction import CreateTransaction
from telegram.handlers.admin.keyboards import get_admin_keyboard
from telegram.handlers.admin.transaction_control.states import AdminPaymentStates
from telegram.handlers.keyboards import get_confirmation_keyboard
from telegram.handlers.user.keyboards import get_user_keyboard

router = Router(name="admin_payment_router")


@router.message(F.from_user.id == settings.tg.admin_id, AdminPaymentStates.confirmation, F.text == "Да")
async def payment_confirmation_yes(message: Message, state: FSMContext):
	log.info("Оплата подтверждена администратором. Добавление транзакции")
	transaction_data = await state.get_data()
	create_transaction = CreateTransaction(**transaction_data)
	try:
		transaction = await transaction_repo.create(create_transaction)
		log.info("Транзакция добавлена в базу данных: {}".format(transaction))
		await message.answer("Транзакция успешно добавлена.", reply_markup=get_admin_keyboard())
		text = (
			"Оплата подтверждена\n"
			"-----------------------------------\n"
			f"Сумма: {transaction.amount}₽\n"
			f"Номер транзакции: {transaction.id:03d}"
		)
		await message.bot.send_message(chat_id=transaction.user_id, text=text, reply_markup=get_user_keyboard())
	except Exception as e:
		log.error("Ошибка: {}".format(e))
		await message.answer("Неизвестная ошибка.", reply_markup=get_admin_keyboard())
		# raise
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, AdminPaymentStates.confirmation, F.text == "Нет")
async def admin_registration_no(message: Message, state: FSMContext):
	log.info("Запрос на подтверждение оплаты отклонен")
	transaction_data = await state.get_data()
	user_id = transaction_data["awg_record_id"]
	await message.answer("Запрос отклонен.", reply_markup=get_admin_keyboard())
	await message.bot.send_message(user_id, "Ваша заявка на регистрацию отклонена.", reply_markup=get_user_keyboard())
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, AdminPaymentStates.confirmation)
async def admin_registration_unknown(message: Message):
	log.info("Некорректный ввод. Повторный запрос...")
	await message.answer("Выберете 'Да' или 'Нет'.", reply_markup=get_confirmation_keyboard())
