from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RegistrationBase(BaseModel):
	id: int
	user_id: int
	username: str
	full_name: str

	model_config = ConfigDict(from_attributes=True)


class CreateRegistration(RegistrationBase):
	pass


class ReadRegistration(RegistrationBase):
	created_at: datetime


class UpdateRegistration(BaseModel):
	id: int | None = None
	user_id: int | None = None
	username: str | None = None
	full_name: str | None = None
