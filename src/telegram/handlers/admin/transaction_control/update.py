from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.transaction import transaction_repo
from core.schemas.transaction import UpdateTransaction

# from user.dto import UpdateUser
from telegram.handlers.admin.keyboards import get_update_keyboard
from .states import TransactionCrudStates
from ...keyboards import get_cancel_keyboard

router = Router(name="update_transaction_router")


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.show_profile, F.text == "Изменить")
async def update_transaction(message: Message, state: FSMContext):
	log.info("{} ({}): Обновление транзакции".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Выберите поле для изменения:", reply_markup=get_update_keyboard(UpdateTransaction))
	await state.set_state(TransactionCrudStates.update)


@router.message(
	F.from_user.id == settings.tg.admin_id, TransactionCrudStates.update, F.text.in_(UpdateTransaction.model_fields)
)
async def edit_transaction_field_step1(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Изменение поля '{}'. Запрос значения...".format(
			message.from_user.full_name, message.from_user.id, message.text
		)
	)
	await state.update_data(key=message.text)
	await message.answer(f"Введите новое значение '{message.text}':", reply_markup=get_cancel_keyboard())
	await state.set_state(TransactionCrudStates.edit_field)


@router.message(F.from_user.id == settings.tg.admin_id, TransactionCrudStates.edit_field)
async def edit_transaction_field_step2(message: Message, state: FSMContext):
	log.info(
		"{} ({}): Введено значение: {}. Проверка и установка значения".format(
			message.from_user.full_name, message.from_user.id, message.text
		)
	)
	data = await state.get_data()
	transaction_id = data["transaction_id"]
	key = data["key"]
	value = message.text
	update_data = {key: value}
	try:
		transaction = await transaction_repo.update(transaction_id, UpdateTransaction(**update_data))
		log.info("Запись успешно обновлена:\n{}".format(transaction))
		text = (
			f"Транзакция {transaction.id:03d}\n"
			f"--------------------------------------------\n"
			f"ID пользователя: {transaction.user_id}\n"
			f"Сумма: {transaction.amount}₽\n"
		)
		await message.answer(text, reply_markup=get_update_keyboard(UpdateTransaction))
	except Exception as e:
		log.error("Ошибка при обновлении значения: '{}' = '{}': {}".format(key, value, e))
		await message.answer("Некорректный ввод.", reply_markup=get_update_keyboard(UpdateTransaction))
	await state.set_state(TransactionCrudStates.update)
