from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.logger import log
from core.repos.transaction import transaction_repo

from .states import TransactionCrudStates
from ..keyboards import get_confirmation_keyboard
from .keyboards import get_transaction_control_keyboard

router = Router(name="delete_transaction_router")


@router.message(TransactionCrudStates.show_profile, F.text == "Удалить")
async def delete_user_ste1(message: Message, state: FSMContext):
	log.debug("Удаление транзакции. Запрос подтверждения")

	await message.answer("Удалить транзакцию?", reply_markup=get_confirmation_keyboard())
	await state.set_state(TransactionCrudStates.delete_confirmation)


@router.message(TransactionCrudStates.delete_confirmation, F.text == "Да")
async def delete_confirmation_ok(message: Message, state: FSMContext):
	log.debug("Подтверждение удаления получено")
	data = await state.get_data()
	transaction_id = data["transaction_id"]
	await transaction_repo.delete(transaction_id)
	log.debug("Транзакция успешно удалена: {}".format(transaction_id))
	await message.answer("Транзакция успешно удалена.", reply_markup=get_transaction_control_keyboard())


@router.message(TransactionCrudStates.delete_confirmation, F.text == "Нет")
async def delete_confirmation_no(message: Message, state: FSMContext):
	log.debug("Удаление отменено")
	await message.answer("Удаление отменено.", reply_markup=get_transaction_control_keyboard())
	await state.clear()
