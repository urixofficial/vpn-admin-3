from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import connection
from core.models.transaction import TransactionModel
from core.schemas.transaction import CreateTransaction

@connection
async def get_transactions(session: AsyncSession) -> list[TransactionModel]:
	stmt = select(TransactionModel).order_by(TransactionModel.id)
	result: Result = await session.execute(stmt)
	transactions = result.scalars().all()
	return list(transactions)

@connection
async def get_transaction(tx_id: int, session: AsyncSession) -> TransactionModel | None:
	return await session.get(TransactionModel, tx_id)

@connection
async def create_transaction(transaction: CreateTransaction, session: AsyncSession) -> TransactionModel:
	transaction = TransactionModel(**transaction.model_dump())
	session.add(transaction)
	await session.commit()
	await session.refresh(transaction)
	return transaction