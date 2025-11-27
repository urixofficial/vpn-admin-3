from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class CreateUser(BaseModel):
	id: int
	name: Annotated[str, MinLen(3), MaxLen(24)]
	model_config = ConfigDict(from_attributes=True)

class ReadUser(CreateUser):
	balance: int
	billing_date: date
	created_at: datetime
	updated_at: datetime

class UpdateUser(BaseModel):
	id: int | None = None
	name: Annotated[str, MinLen(3), MaxLen(24)] | None = None
	balance: int | None = None
	billing_date: date | None = None
	model_config = ConfigDict(from_attributes=True)