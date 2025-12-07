from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from core.config import settings
from core.logger import log
from core.repos.transaction import transaction_repo
from core.repos.user import user_repo

from telegram.handlers.keyboards import get_cancel_keyboard
from .keyboards import get_transaction_control_keyboard, get_profile_keyboard
from .states import TransactionCrudStates

router = Router(name="read_transaction_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Список транзакций")
async def list_transactions(message: Message):
	log.info("Вывод списка транзакций")
	transactions = await transaction_repo.get_all(settings.billing.transactions_limit)
	if not transactions:
		log.debug("Список транзакций пуст")
		await message.answer("Список транзакций пуст.")
		return
	text = (
		f"Последние {settings.billing.transactions_limit} транзакций:\n--------------------------------------------\n"
	)
	for transaction in transactions:
		line = f"{transaction.id:03d}. {transaction.created_at.date()} - {transaction.user_id:#10d}: {transaction.amount}₽\n"
		text += line
	await message.answer(text, reply_markup=get_transaction_control_keyboard())


@router.message(F.text == "Профиль транзакции")
async def show_user_step1(message: Message, state: FSMContext):
	log.info("Вывод профиля транзакции. Запрос ID...")
	await message.answer("Введите ID транзакции:", reply_markup=get_cancel_keyboard())
	await state.set_state(TransactionCrudStates.show_enter_id)


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.show_enter_id)
async def show_transaction_step2(message: Message, state: FSMContext):
	log.info("Получено значение: {}".format(message.text))
	try:
		transaction_id = int(message.text)
	except ValueError:
		log.info("ID должен быть целым числом. Повторный запрос...")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if transaction_id <= 0:
		log.info("ID должен быть больше нуля. Повторный запрос...")
		await message.answer("ID должен быть больше нуля. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	transaction = await transaction_repo.get(transaction_id)
	if not transaction:
		log.info("Запись #{} не найдена. Повторный запрос...")
		await message.answer("Запись не найдена. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(transaction_id=transaction_id)
	user = await user_repo.get(transaction.user_id)
	name = user.name if user else transaction.user_id
	text = (
		f"Транзакция {transaction.id:03d}\n"
		f"--------------------------------------------\n"
		f"Сумма: {transaction.amount}₽\n"
		f"Пользователь: {name}\n"
		f"Добавлена: {transaction.created_at.date()}\n"
		f"Обновлена: {transaction.updated_at.date()}"
	)
	await message.answer(text, reply_markup=get_profile_keyboard())
	await state.set_state(TransactionCrudStates.show_profile)
