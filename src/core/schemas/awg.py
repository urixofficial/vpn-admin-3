from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AwgRecordBase(BaseModel):
	id: int
	ip: str
	mask: int
	public_key: str
	private_key: str

	model_config = ConfigDict(from_attributes=True)


class CreateAwgRecord(AwgRecordBase):
	pass


class ReadAwgRecord(AwgRecordBase):
	created_at: datetime
	updated_at: datetime


class UpdateAwgRecord(BaseModel):
	ip: str | None = None
	mask: int | None = None
	public_key: str | None = None
	private_key: str | None = None
