from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TransactionBase(BaseModel):
	user_id: int
	amount: int

	model_config = ConfigDict(from_attributes=True)

class CreateTransaction(TransactionBase):
	pass

class Transaction(TransactionBase):
	id: int
	created_at: datetime
	updated_at: datetime

class UpdateTransaction(BaseModel):
	user_id: int | None = None
	amount: int | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None