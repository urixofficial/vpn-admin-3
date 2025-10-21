from pydantic import BaseModel, Field, field_validator
from datetime import date as date_object
from typing import Optional, List
from enum import Enum


class UserStatus(str, Enum):
	"""Статусы пользователя"""
	ACTIVE = "active"
	BLOCKED = "blocked"
	EXPIRED = "expired"


class UserBase(BaseModel):
	"""Базовая модель пользователя"""
	username: str = Field(default="Неизвестно", min_length=1, max_length=30, description="Имя пользователя")
	billing_start_date: date_object = Field(default_factory=date_object.today, description="Начало расчетного периода")
	billing_end_date: date_object = Field(default_factory=date_object.today, description="Конец расчетного периода")

	@field_validator("billing_end_date")
	def validate_billing_dates(cls, v, values):
		"""Проверяет, что конечная дата не раньше начальной"""
		if "billing_start_date" in values.data and v < values.data["billing_start_date"]:
			raise ValueError("Конечная дата не может быть раньше начальной")
		return v


class UserCreate(UserBase):
	"""Модель для создания пользователя"""
	telegram_id: int = Field(description="ID пользователя в Telegram")


class UserUpdate(BaseModel):
	"""Модель для обновления пользователя"""
	username: Optional[str] = Field(None, min_length=1, max_length=30)
	billing_end_date: Optional[date_object] = None
	status: Optional[UserStatus] = None


class User(UserBase):
	"""Полная модель пользователя"""
	id: int = Field(description="ID пользователя (Telegram ID)")
	status: UserStatus = Field(default=UserStatus.ACTIVE, description="Статус пользователя")

	class Config:
		from_attributes = True

	def is_active(self) -> bool:
		"""Проверяет, активен ли пользователь"""
		return self.status == UserStatus.ACTIVE and self.billing_end_date >= date_object.today()

	def days_until_expiry(self) -> int:
		"""Возвращает количество дней до истечения срока"""
		return (self.billing_end_date - date_object.today()).days


class Transaction(BaseModel):
	"""Модель транзакции"""
	id: int = Field(description="ID транзакции")
	user_id: int = Field(description="ID пользователя")
	amount: int = Field(gt=0, description="Сумма транзакции")
	date: date_object = Field(default_factory=date_object.today, description="Дата транзакции")

	class Config:
		from_attributes = True


class UserWithTransactions(User):
	"""Пользователь с транзакциями"""
	transactions: List[Transaction] = Field(default_factory=list)