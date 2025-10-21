from typing import List, Optional
from datetime import date as date_object
from app.core.database import db
from app.core.logger import log
from app.domains.users.models import Transaction


class TransactionRepository:
	"""Репозиторий для работы с транзакциями"""

	def __init__(self):
		self.table_name = "transactions"

	def get_all(self) -> List[Transaction]:
		"""Получает все транзакции"""
		try:
			records = db.fetch_all(f"SELECT * FROM {self.table_name} ORDER BY date DESC, id DESC")
			return [Transaction(**record) for record in records]
		except Exception as e:
			log.error(f"Ошибка получения всех транзакций: {e}")
			raise

	def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
		"""Получает транзакцию по ID"""
		try:
			record = db.fetch_one(f"SELECT * FROM {self.table_name} WHERE id = ?", (transaction_id,))
			return Transaction(**record) if record else None
		except Exception as e:
			log.error(f"Ошибка получения транзакции {transaction_id}: {e}")
			raise

	def get_by_user_id(self, user_id: int) -> List[Transaction]:
		"""Получает транзакции пользователя"""
		try:
			records = db.fetch_all(
				f"SELECT * FROM {self.table_name} WHERE user_id = ? ORDER BY date DESC, id DESC",
				(user_id,)
			)
			return [Transaction(**record) for record in records]
		except Exception as e:
			log.error(f"Ошибка получения транзакций пользователя {user_id}: {e}")
			raise

	def create(self, user_id: int, amount: int, transaction_date: date_object = None) -> Transaction:
		"""Создает новую транзакцию"""
		try:
			if transaction_date is None:
				transaction_date = date_object.today()

			db_data = {
				"user_id": user_id,
				"amount": amount,
				"date": transaction_date.isoformat()
			}

			transaction_id = db.insert(self.table_name, db_data)
			return self.get_by_id(transaction_id)

		except Exception as e:
			log.error(f"Ошибка создания транзакции для пользователя {user_id}: {e}")
			raise

	def delete(self, transaction_id: int) -> bool:
		"""Удаляет транзакцию"""
		try:
			return db.delete(self.table_name, transaction_id)
		except Exception as e:
			log.error(f"Ошибка удаления транзакции {transaction_id}: {e}")
			raise

	def get_total_amount_by_user(self, user_id: int) -> int:
		"""Получает общую сумму транзакций пользователя"""
		try:
			record = db.fetch_one(
				f"SELECT SUM(amount) as total FROM {self.table_name} WHERE user_id = ?",
				(user_id,)
			)
			return record["total"] if record and record["total"] else 0
		except Exception as e:
			log.error(f"Ошибка получения общей суммы для пользователя {user_id}: {e}")
			raise


# Глобальный экземпляр репозитория
transaction_repository = TransactionRepository()