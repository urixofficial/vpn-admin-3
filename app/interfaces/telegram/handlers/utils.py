from telegram import Update
from telegram.ext import ContextTypes
from app.core.logger import log

def get_sender_id(update: Update):
	# Проверяем, откуда пришел запрос
	if update.callback_query:
		user_id = update.callback_query.from_user.id
	else:
		user_id = update.effective_user.id
	return user_id

def get_message_func(update: Update):
	# Проверяем, откуда пришел запрос
	if update.callback_query:
		message_func = update.callback_query.edit_message_text
	else:
		message_func = update.message.reply_text
	return message_func

def check_for_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
	# Проверка на админа
	log.debug("Проверка на админа.")
	user_id = update.effective_user.id
	admin_id = context.bot_data.get("admin_id")
	if user_id == admin_id:
		log.debug("Проверка пройдена.")
		return True
	log.warning("Проверка не пройдена.")
	return False


def check_for_valid_id(text_id: str) -> bool:
	# Проверка валидности идентификатора
	log.debug("Проверка на валидность ID.")

	if len(text_id) > 20:
		log.warning("Проверка не пройдена.")
		return False
	try:
		int_id = int(text_id)
		if int_id <= 0:
			log.warning("Проверка не пройдена.")
			return False
		log.debug("Проверка пройдена.")
		return True
	except:
		log.warning("Проверка не пройдена.")
		return False


def check_for_valid_name(name: str) -> bool:
	# Проверка валидности имени
	log.debug("Проверка на валидность имени.")

	if len(name) < 3:
		return False
	if len(name) > 30:
		return False
	return True