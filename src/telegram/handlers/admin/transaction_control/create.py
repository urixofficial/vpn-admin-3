from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.message import message_repo
from core.schemas.message import CreateMessage
from core.schemas.transaction import CreateTransaction
from core.repos.transaction import transaction_repo
from core.repos.user import user_repo

from telegram.handlers.keyboards import get_cancel_keyboard
from .keyboards import get_transaction_control_keyboard
from .states import TransactionCrudStates

router = Router(name="create_user_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Добавить транзакцию")
async def create_transaction_step1(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Создание транзакции. Запрос ID пользователя...".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	await message.answer("Введите ID пользователя:", reply_markup=get_cancel_keyboard())
	await state.set_state(TransactionCrudStates.create_enter_user_id)


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.create_enter_user_id)
async def create_transaction_step2(message: Message, state: FSMContext):
	log.info("{} ({}): Получено значение: {}".format(message.from_user.full_name, message.from_user.id, message.text))
	try:
		user_id = int(message.text)
	except ValueError:
		log.info("ID должен быть целым числом. Повторный запрос...")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if user_id <= 0:
		log.info("ID должен быть больше нуля. Повторный запрос...")
		await message.answer(
			"ID должен быть положительным числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard()
		)
		return
	user = await user_repo.get(user_id)
	if not user:
		log.info("Пользователь с указанным ID не найден. Повторный запрос...")
		await message.answer(
			"Пользователь с указанным ID не найден. Попробуйте еще раз:", reply_markup=get_cancel_keyboard()
		)
		return
	await state.update_data(user_id=user_id)
	log.info("Запрос суммы транзакции...")
	await message.answer("Введите сумму транзакции:", reply_markup=get_cancel_keyboard())
	await state.set_state(TransactionCrudStates.create_enter_amount)


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.create_enter_amount)
async def create_transaction_step3(message: Message, state: FSMContext):
	log.info("{} ({}): Получено значение: {}".format(message.from_user.full_name, message.from_user.id, message.text))
	try:
		amount = int(message.text)
	except ValueError:
		log.info("Сумма должна быть целым числом. Повторный запрос...")
		await message.answer("Сумма должна быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if amount <= 0:
		log.info("Сумма должна быть больше нуля. Повторный запрос...")
		await message.answer("Сумма должна быть больше нуля. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(amount=amount)
	log.debug("Создание записи в базе данных")
	data = await state.get_data()
	create_transaction = CreateTransaction(**data)
	try:
		transaction = await transaction_repo.create(create_transaction)
		log.info("Запись успешно добавлена: {}".format(transaction))
		await message.answer("Запись успешно добавлена.", reply_markup=get_transaction_control_keyboard())
		text = (
			"Оплата подтверждена\n"
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
