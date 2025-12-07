from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AwgRecordBase(BaseModel):
	ip: str
	mask: int
	user_id: int
	public_key: str
	private_key: str

	model_config = ConfigDict(from_attributes=True)


class CreateAwgRecord(AwgRecordBase):
	pass


class ReadAwgRecord(AwgRecordBase):
	id: int
	created_at: datetime
	updated_at: datetime


class UpdateAwgRecord(BaseModel):
	ip: str | None = None
	mask: int | None = None
	user_id: int | None = None
	public_key: str | None = None
	private_key: str | None = None

	model_config = ConfigDict(from_attributes=True)

	def __repr__(self):
		return ", ".join([f"{key}={value}" for key, value in self.model_dump().items() if value != None])

	def __str__(self):
		return self.__repr__()
