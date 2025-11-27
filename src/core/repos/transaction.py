from core.models.transaction import TransactionModel
from core.schemas.transaction import (
	CreateTransaction,
	ReadTransaction,
	UpdateTransaction,
)

from .base import BaseRepo


class TransactionRepo(BaseRepo[CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel]):
	pass


transaction_repo = TransactionRepo(CreateTransaction, ReadTransaction, UpdateTransaction, TransactionModel)
