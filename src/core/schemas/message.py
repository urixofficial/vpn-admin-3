from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class MessageStatus(Enum):
	PENDING = "Ждет отправки"
	SENT = "Отправлено"
	CHAT_NOT_EXIST = "Чат не существует"
	BOT_BLOCKED = "Бот заблокирован"
	TELEGRAM_ERROR = "Ошибка Telegram API"


class MessageBase(BaseModel):
	recipient: int
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
