from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import connection
from src.transaction.orm import TransactionOrm
from src.transaction.dto import CreateTransaction

@connection
async def get_transactions(session: AsyncSession) -> list[TransactionOrm]:
	stmt = select(TransactionOrm).order_by(TransactionOrm.id)
	result: Result = await session.execute(stmt)
	transactions = result.scalars().all()
	return list(transactions)

@connection
async def get_transaction(tx_id: int, session: AsyncSession) -> TransactionOrm | None:
	return await session.get(TransactionOrm, tx_id)

@connection
async def create_transaction(transaction: CreateTransaction, session: AsyncSession) -> TransactionOrm:
	transaction = TransactionOrm(**transaction.model_dump())
	session.add(transaction)
	await session.commit()
	await session.refresh(transaction)
	return transaction