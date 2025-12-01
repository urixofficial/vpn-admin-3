from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.transaction import TransactionModel
from core.schemas.transaction import (
	CreateTransaction,
	ReadTransaction,
	UpdateTransaction,
)

from core.logger import log
from core.database import connection

from .base import BaseRepo
from ..config import settings
from ..models import UserModel


class TransactionRepo(BaseRepo[CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel]):
	@connection
	async def get_by_user(self, user_id: int, session: AsyncSession) -> list[ReadTransaction]:
		log.debug("Получение списка транзакций по пользователю")
		query = select(TransactionModel).where(TransactionModel.user_id == user_id).order_by(TransactionModel.id.desc())
		transaction_models = await session.execute(query)
		await session.commit()
		return [ReadTransaction.model_validate(transaction_model) for transaction_model in transaction_models]

	@connection
	async def create(self, create_transaction: CreateTransaction, session: AsyncSession) -> ReadTransaction:
		log.debug(
			"Создание транзакции {}. Обновление баланса пользователя {}".format(
				create_transaction, create_transaction.user_id
			)
		)
		transaction_model = TransactionModel(**create_transaction.model_dump())
		session.add(transaction_model)
		user_model = await session.get(UserModel, transaction_model.user_id)
		user_model.balance += transaction_model.amount
		if not user_model.is_active and user_model.balance >= settings.billing.daily_payment:
			user_model.is_active = True
		await session.commit()
		# await session.refresh(item_model)
		return ReadTransaction.model_validate(transaction_model)

	@connection
	async def delete(self, transaction_id: int, session: AsyncSession) -> ReadTransaction:
		log.debug("Удаление транзакции {}. Обновление баланса пользователя".format(transaction_id))
		transaction_model = await session.get(self.model, transaction_id)
		if not transaction_model:
			raise Exception("Транзакция не найдена: {}".format(transaction_id))
		await session.delete(transaction_model)
		user_model = await session.get(UserModel, transaction_model.user_id)
		user_model.balance -= transaction_model.amount
		if user_model.is_active and user_model.balance < settings.billing.daily_payment:
			user_model.is_active = False
		await session.commit()
		return ReadTransaction.model_validate(transaction_model)


transaction_repo = TransactionRepo(CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel)
