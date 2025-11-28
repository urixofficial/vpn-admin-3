from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.message import MessageModel
from core.schemas.message import (
	CreateMessage,
	ReadMessage,
	UpdateMessage,
)

from core.logger import log
from core.database import connection
from telegram.message_sender import send_message as tg_send_message
from .base import BaseRepo


class MessageRepo(BaseRepo[CreateMessage, ReadMessage, UpdateMessage, MessageModel]):
	@connection
	async def get_by_user(self, user_id: int, session: AsyncSession) -> list[ReadMessage]:
		log.debug("Получение списка сообщений по пользователю")
		query = select(MessageModel).where(MessageModel.chat_id == user_id).order_by(MessageModel.id.desc())
		message_models = await session.execute(query)
		await session.commit()
		return [ReadMessage.model_validate(message_model) for message_model in message_models]

	async def send_message(self, create_message: CreateMessage):
		log.debug("Отправка сообщения пользователю {}".format(create_message.chat_id))
		message = await self.create(create_message)
		status = await tg_send_message(message.chat_id, message.text)
		await self.update(message.id, UpdateMessage(status=status))


message_repo = MessageRepo(CreateMessage, ReadMessage, UpdateMessage, MessageModel)
