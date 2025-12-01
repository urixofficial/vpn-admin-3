from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class AwgBase(BaseModel):
	id: int
	public_key: str
	private_key: str

	model_config = ConfigDict(from_attributes=True)


class CreateAwg(AwgBase):
	pass


class ReadAwg(AwgBase):
	created_at: datetime
	updated_at: datetime


class UpdateMessage(BaseModel):
	public_key: str
	private_key: str
