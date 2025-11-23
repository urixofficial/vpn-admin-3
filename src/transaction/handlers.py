from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.core.logger import log
from src.transaction.dto import CreateTransaction
from src.transaction.repo import create_transaction

router = Router(name="transaction_router")

@router.message(Command("create_transaction"))
async def cmd_create_transaction(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /create_transaction".format(
		message.from_user.full_name,
		message.from_user.id
	))

	transaction = CreateTransaction(user_id=12345678, amount=300)

	transaction_orm = await create_transaction(transaction=transaction)
	await message.answer("Транзакция добавлена под номером {}".format(transaction_orm.id))

@router.message(Command("get_transactions"))
async def cmd_get_transactions(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /get_transactions".format(
		message.from_user.full_name,
		message.from_user.id
	))

@router.message(Command("get_transaction"))
async def cmd_get_transaction(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /get_transaction".format(
		message.from_user.full_name,
		message.from_user.id
	))

@router.message(Command("delete_transactions"))
async def cmd_delete_transactions(message: Message):
	log.debug("Пользователь {} ({}) выполнил команду /delete_transactions".format(
		message.from_user.full_name,
		message.from_user.id
	))