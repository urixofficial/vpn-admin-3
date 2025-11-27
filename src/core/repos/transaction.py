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


class TransactionRepo(BaseRepo[CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel]):
	@connection
	async def get_by_user(self, user_id: int, session: AsyncSession) -> list[ReadTransaction]:
		log.debug("Получение списка транзакций по пользователю")
		query = select(TransactionModel).where(TransactionModel.user_id == user_id).order_by(TransactionModel.id.desc())
		transaction_models = await session.execute(query)
		await session.commit()
		return [ReadTransaction.model_validate(transaction_model) for transaction_model in transaction_models]


transaction_repo = TransactionRepo(CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel)
