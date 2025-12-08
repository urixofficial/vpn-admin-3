from types import NoneType

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TransactionBase(BaseModel):
	user_id: int
	amount: int

	model_config = ConfigDict(from_attributes=True)


class CreateTransaction(TransactionBase):
	pass


class ReadTransaction(TransactionBase):
	id: int
	created_at: datetime
	updated_at: datetime


class UpdateTransaction(BaseModel):
	user_id: int | None = None
	amount: int | None = None

	model_config = ConfigDict(from_attributes=True)

	def __repr__(self):
		return ", ".join(
			[f"{key}={value}" for key, value in self.model_dump().items() if not isinstance(value, NoneType)]
		)

	def __str__(self):
		return self.__repr__()
