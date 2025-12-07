from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class MessageStatus(Enum):
	PENDING = "Ждет отправки"
	SENT = "Отправлено"
	CHAT_NOT_EXIST = "Чат не существует"
	BOT_BLOCKED = "Бот заблокирован"
	API_ERROR = "Ошибка Telegram API"
	UNKNOWN_ERROR = "Неизвестная ошибка"


class MessageBase(BaseModel):
	chat_id: int
	text: str

	model_config = ConfigDict(from_attributes=True)


class CreateMessage(MessageBase):
	pass


class ReadMessage(MessageBase):
	id: int
	status: MessageStatus
	created_at: datetime
	updated_at: datetime


class UpdateMessage(BaseModel):
	status: MessageStatus

	model_config = ConfigDict(from_attributes=True)

	def __repr__(self):
		return ", ".join([f"{key}={value}" for key, value in self.model_dump().items() if value != None])

	def __str__(self):
		return self.__repr__()
