from typing import List, Optional
from datetime import date as date_object
from app.core.database import db
from app.core.logger import log
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.domains.users.models import User, UserCreate, UserUpdate, UserStatus


class UserRepository:
	"""Репозиторий для работы с пользователями"""

	def __init__(self):
		self.table_name = "users"

	def get_all(self) -> List[User]:
		"""Получает всех пользователей"""
		try:
			records = db.fetch_all(f"SELECT * FROM {self.table_name} ORDER BY username")
			return [User(**record) for record in records]
		except Exception as e:
			log.error(f"Ошибка получения всех пользователей: {e}")
			raise

	def get_by_id(self, user_id: int) -> Optional[User]:
		"""Получает пользователя по ID"""
		try:
			record = db.fetch_one(f"SELECT * FROM {self.table_name} WHERE id = ?", (user_id,))
			return User(**record) if record else None
		except Exception as e:
			log.error(f"Ошибка получения пользователя {user_id}: {e}")
			raise

	def get_by_username(self, username: str) -> Optional[User]:
		"""Получает пользователя по имени"""
		try:
			record = db.fetch_one(f"SELECT * FROM {self.table_name} WHERE username = ?", (username,))
			return User(**record) if record else None
		except Exception as e:
			log.error(f"Ошибка получения пользователя {username}: {e}")
			raise

	def create(self, user_data: UserCreate) -> User:
		"""Создает нового пользователя"""
		try:
			# Проверяем, существует ли пользователь с таким ID или именем
			if self.get_by_id(user_data.telegram_id):
				raise UserAlreadyExistsException(f"Пользователь с ID {user_data.telegram_id} уже существует")

			if self.get_by_username(user_data.username):
				raise UserAlreadyExistsException(f"Пользователь с именем {user_data.username} уже существует")

			# Подготавливаем данные для вставки
			db_data = {
				"id": user_data.telegram_id,
				"username": user_data.username,
				"billing_start_date": user_data.billing_start_date.isoformat(),
				"billing_end_date": user_data.billing_end_date.isoformat(),
				"status": UserStatus.ACTIVE.value
			}

			# Вставляем в БД
			db.insert(self.table_name, db_data)

			# Возвращаем созданного пользователя
			return self.get_by_id(user_data.telegram_id)

		except Exception as e:
			log.error(f"Ошибка создания пользователя {user_data.username}: {e}")
			raise

	def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
		"""Обновляет пользователя"""
		try:
			existing_user = self.get_by_id(user_id)
			if not existing_user:
				raise UserNotFoundException(f"Пользователь {user_id} не найден")

			# Подготавливаем данные для обновления
			update_data = {}
			if user_data.username is not None:
				update_data["username"] = user_data.username
			if user_data.billing_end_date is not None:
				update_data["billing_end_date"] = user_data.billing_end_date.isoformat()
			if user_data.status is not None:
				update_data["status"] = user_data.status.value

			if update_data:
				db.update(self.table_name, user_id, update_data)

			return self.get_by_id(user_id)

		except Exception as e:
			log.error(f"Ошибка обновления пользователя {user_id}: {e}")
			raise

	def delete(self, user_id: int) -> bool:
		"""Удаляет пользователя"""
		try:
			if not self.get_by_id(user_id):
				raise UserNotFoundException(f"Пользователь {user_id} не найден")

			return db.delete(self.table_name, user_id)

		except Exception as e:
			log.error(f"Ошибка удаления пользователя {user_id}: {e}")
			raise

	def get_active_users(self) -> List[User]:
		"""Получает активных пользователей"""
		try:
			records = db.fetch_all(
				f"SELECT * FROM {self.table_name} WHERE status = ? ORDER BY username",
				(UserStatus.ACTIVE.value,)
			)
			return [User(**record) for record in records]
		except Exception as e:
			log.error(f"Ошибка получения активных пользователей: {e}")
			raise

	def get_expired_users(self) -> List[User]:
		"""Получает пользователей с истекшим сроком"""
		try:
			today = date_object.today().isoformat()
			records = db.fetch_all(
				f"SELECT * FROM {self.table_name} WHERE billing_end_date < ? AND status = ?",
				(today, UserStatus.ACTIVE.value)
			)
			return [User(**record) for record in records]
		except Exception as e:
			log.error(f"Ошибка получения пользователей с истекшим сроком: {e}")
			raise


# Глобальный экземпляр репозитория
user_repository = UserRepository()