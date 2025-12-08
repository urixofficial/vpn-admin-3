from types import NoneType
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CreateUser(BaseModel):
	id: int
	name: Annotated[str, MinLen(3), MaxLen(48)]
	model_config = ConfigDict(from_attributes=True)


class ReadUser(CreateUser):
	is_active: bool
	balance: int | None
	created_at: datetime
	updated_at: datetime


class UpdateUser(BaseModel):
	id: int | None = None
	name: Annotated[str, MinLen(3), MaxLen(48)] | None = None
	is_active: bool | None = None
	balance: int | None = None

	model_config = ConfigDict(from_attributes=True)

	def __repr__(self):
		return ", ".join(
			[f"{key}={value}" for key, value in self.model_dump().items() if not isinstance(value, NoneType)]
		)

	def __str__(self):
		return self.__repr__()
