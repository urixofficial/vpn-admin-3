from core.models.transaction import TransactionModel
from core.schemas.transaction import (
	CreateTransaction,
	ReadTransaction,
	UpdateTransaction,
)

from .base import BaseRepo


class TransactionRepo(BaseRepo[CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel]):
	def __init__(self):
		super().__init__(CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel)


transaction_repo = TransactionRepo()
