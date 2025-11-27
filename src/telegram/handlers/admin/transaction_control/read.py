from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from core.repos.transaction import transaction_repo
from core.repos.user import user_repo

from ..keyboards import get_cancel_keyboard
from .keyboards import get_transaction_control_keyboard, get_profile_keyboard
from .states import TransactionCrudStates

router = Router(name="read_transaction_router")


@router.message(F.text == "Список транзакций")
async def list_transactions(message: Message):
	log.debug("Вывод списка транзакций")
	transactions = await transaction_repo.get_all()
	if not transactions:
		log.debug("Нет записей")
		await message.answer("Нет записей.")
		return
	text = "Список транзакций:\n-----------------------------------\n"
	for number, transaction in enumerate(transactions, start=1):
		user = await user_repo.get(transaction.user_id)
		line = f"{number:03d}. {user.name}: {transaction.amount}₽\n"
		text += line
	await message.answer(text, reply_markup=get_transaction_control_keyboard())


@router.message(F.text == "Профиль транзакции")
async def show_user_step1(message: Message, state: FSMContext):
	log.debug("Вывод профиля транзакции. Запрос ID")
	await message.answer("Введите ID транзакции:", reply_markup=get_cancel_keyboard())
	await state.set_state(TransactionCrudStates.show_enter_id)


@router.message(TransactionCrudStates.show_enter_id)
async def show_user_step2(message: Message, state: FSMContext):
	log.debug("Получено значение: {}".format(message.text))
	try:
		transaction_id = int(message.text)
	except ValueError:
		log.debug("ID должен быть целым числом. Повторный запрос")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if transaction_id <= 0:
		log.debug("ID должен быть больше нуля. Повторный запрос")
		await message.answer("ID должен быть больше нуля. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	transaction = await transaction_repo.get(transaction_id)
	if not transaction:
		log.debug("Запись не найдена: {}. Повторный запрос")
		await message.answer("Запись не найдена. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	user = await user_repo.get(transaction.user_id)
	await state.update_data(transaction_id=transaction_id)
	text = (
		f"Транзакция {transaction.id:03d}\n"
		f"-----------------------------------\n"
		f"Сумма: {transaction.amount}\n"
		f"Пользователь: {user.name}\n"
		f"Добавлена: {transaction.created_at.date()}\n"
		f"Обновлена: {transaction.updated_at.date()}"
	)
	await message.answer(text, reply_markup=get_profile_keyboard())
	await state.set_state(TransactionCrudStates.show_profile)
