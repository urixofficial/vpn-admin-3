from aiogram.exceptions import TelegramNotFound, TelegramAPIError, TelegramForbiddenError

from core.logger import log
from core.schemas.message import MessageStatus
from telegram.bot_init import bot


async def send_message(chat_id: int, text: str):
	log.debug("Отправка сообщения пользователю {}".format(chat_id))
	try:
		await bot.send_message(chat_id=chat_id, text=text)
		log.info("Сообщение успешно отправлено")
		return MessageStatus.SENT
	except TelegramNotFound:
		log.error("Ошибка: {}".format(MessageStatus.CHAT_NOT_EXIST))
		return MessageStatus.CHAT_NOT_EXIST
	except TelegramForbiddenError:
		log.error("Ошибка: {}".format(MessageStatus.BOT_BLOCKED))
		return MessageStatus.BOT_BLOCKED
	except TelegramAPIError:
		log.error("Ошибка: {}".format(MessageStatus.API_ERROR))
		return MessageStatus.API_ERROR
	except Exception as e:
		log.error("Ошибка: {}".format(e))
		return MessageStatus.UNKNOWN_ERROR
