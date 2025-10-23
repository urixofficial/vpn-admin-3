# [file name]: conversations.py
from datetime import date, timedelta

from telegram import Update
from telegram.ext import (
	ContextTypes, MessageHandler, CommandHandler, filters, ConversationHandler, CallbackQueryHandler
)

from app.core.exceptions import UserAlreadyExistsException, NameIsNotUniqueException
from app.core.logger import log
from app.domains.users.models import UserCreate, UserStatus
from app.domains.users.repository import user_repository
from .utils import get_sender_id, get_message_func, check_for_admin, check_for_valid_id, check_for_valid_name
from ..keyboards import cancel_keyboard, confirm_keyboard

# Состояния для ConversationHandler
ASK_NEW_USER_ID, ASK_NEW_USER_NAME, ASK_USER_ID_TO_DELETE, CONFIRM_USER_DELETING = range(4)


# ======================== Добавление пользователя =======================

async def ask_new_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Начинает процесс добавления пользователя"""
	log.debug("Диалог добавления нового пользователя: запрос ID.")

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return ConversationHandler.END

	await message_func(
		"Введите ID нового пользователя:",
		reply_markup=cancel_keyboard()
	)
	return ASK_NEW_USER_ID


async def ask_new_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Обрабатывает ввод ID для добавления пользователя"""
	log.debug("Диалог добавления нового пользователя: запрос имени.")

	new_user_id_text = update.message.text

	# Валидация ID пользователя
	if not check_for_valid_id(new_user_id_text):
		await update.message.reply_text(
			"❌ Некорректный ввод.\n"
			"Введите ID нового пользователя:",
			reply_markup=cancel_keyboard()
		)
		return ASK_NEW_USER_ID

	new_user_id = int(new_user_id_text)
	context.user_data["new_user_id"] = new_user_id

	await update.message.reply_text(
		"Введите имя нового пользователя:",
		reply_markup=cancel_keyboard()
	)
	return ASK_NEW_USER_NAME


async def add_new_user_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Добавление нового пользователя в базу данных"""
	log.debug("Диалог добавления нового пользователя: добавление в БД.")

	try:
		new_user_name = update.message.text

		# Валидация имени пользователя
		if not check_for_valid_name(new_user_name):
			await update.message.reply_text(
				"❌ Некорректный ввод. Имя должно быть от 3 до 30 символов.\n"
				"Введите имя нового пользователя:",
				reply_markup=cancel_keyboard()
			)
			return ASK_NEW_USER_NAME

		new_user_id = context.user_data["new_user_id"]

		# Создаем пользователя
		user_data = UserCreate(
			telegram_id=new_user_id,
			username=new_user_name,
			billing_start_date=date.today(),
			billing_end_date=date.today() + timedelta(days=30),
			status=UserStatus.ACTIVE
		)

		new_user = user_repository.create(user_data)

		await update.message.reply_text(
			f"✅ Пользователь успешно добавлен!\n\n"
			f"👤 Имя: {new_user.username}\n"
			f"🆔 ID: {new_user.id}\n"
			f"📅 Начало: {new_user.billing_start_date}\n"
			f"📅 Конец: {new_user.billing_end_date}\n"
			f"🎯 Статус: {new_user.status.value}\n"
		)

		log.info(f"Пользователь успешно добавлен: {new_user.username} ({new_user_id})")
		return ConversationHandler.END

	except UserAlreadyExistsException as e:
		await update.message.reply_text(
			f"❌ Пользователь с ID {new_user_id} уже существует\n"
			"Попробуйте еще раз с другим ID:",
			reply_markup=cancel_keyboard()
		)
		return ASK_NEW_USER_ID

	except NameIsNotUniqueException as e:
		await update.message.reply_text(
			f"❌ Пользователь с именем '{new_user_name}' уже существует\n"
			"Введите другое имя:",
			reply_markup=cancel_keyboard()
		)
		return ASK_NEW_USER_NAME

	except Exception as e:
		log.error(f"Ошибка добавления пользователя: {e}")
		await update.message.reply_text(
			f"❌ Ошибка при добавлении пользователя: {str(e)}\n"
			"Попробуйте еще раз. Введите ID нового пользователя:",
			reply_markup=cancel_keyboard()
		)
		return ASK_NEW_USER_ID


# ======================== Удаление пользователя =======================


async def ask_user_id_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Начинает процесс удаления пользователя"""
	log.debug("Диалог удаления пользователя: запрос ID.")

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return ConversationHandler.END

	await message_func(
		"Введите ID пользователя для удаления:",
		reply_markup=cancel_keyboard()
	)
	return ASK_USER_ID_TO_DELETE


async def confirm_user_deleting(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Обрабатывает ввод ID для удаления пользователя и показывает клавиатуру подтверждения"""
	log.debug("Диалог удаления пользователя: запрос подтверждения.")

	user_id_to_delete_text = update.message.text

	# Валидация ID пользователя
	if not check_for_valid_id(user_id_to_delete_text):
		await update.message.reply_text(
			"❌ Некорректный ввод.\n"
			"Введите ID пользователя для удаления:",
			reply_markup=cancel_keyboard()
		)
		return ASK_USER_ID_TO_DELETE

	user_id_to_delete = int(user_id_to_delete_text)
	context.user_data["user_id_to_delete"] = user_id_to_delete

	user = user_repository.get_by_id(user_id_to_delete)

	if not user:
		await update.message.reply_text(
			f"❌ Пользователь с ID {user_id_to_delete} не найден\n"
			"Введите ID пользователя для удаления:",
			reply_markup=cancel_keyboard()
		)
		return ASK_USER_ID_TO_DELETE

	await update.message.reply_text(
		f"❓ Вы уверены, что хотите удалить пользователя?\n"
		f"👤 Имя: {user.username}\n"
		f"🆔 ID: {user.id}",
		reply_markup=confirm_keyboard()  # Используем инлайн-клавиатуру
	)
	return CONFIRM_USER_DELETING


async def delete_user_from_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Обрабатывает нажатие на кнопки подтверждения"""
	query = update.callback_query
	await query.answer()

	callback_data = query.data
	user_id_to_delete = context.user_data.get("user_id_to_delete")

	if not user_id_to_delete:
		await query.edit_message_text("❌ Ошибка: данные сессии утеряны.")
		return ConversationHandler.END

	user = user_repository.get_by_id(user_id_to_delete)

	if callback_data == "confirm_yes":
		if user_repository.delete(user.id):
			await query.edit_message_text(
				f"✅ Пользователь {user.username} успешно удален."
			)
			log.info(f"Пользователь успешно удален: {user.username} ({user.id})")
		else:
			await query.edit_message_text(
				f"❌ Не удалось удалить пользователя {user.username}."
			)
			log.error(f"Не удалось удалить пользователя: {user.username} ({user.id})")
	elif callback_data == "confirm_no":
		await query.edit_message_text("❌ Удаление отменено.")

	return ConversationHandler.END


# ======================== Общие операции =======================


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Отменяет текущую операцию"""
	# Обрабатываем как текстовые сообщения, так и callback queries
	message_func = get_message_func(update)
	await message_func("❌ Операция отменена")

	return ConversationHandler.END


def setup_conversation_handlers(application, admin_id: int):
	"""Настраивает обработчики диалогов"""
	admin_filter = filters.User(admin_id)

	add_user_handler = ConversationHandler(
		entry_points=[
			CallbackQueryHandler(ask_new_user_id, pattern="^users_add$")
		],
		states={
			ASK_NEW_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_user_name)],
			ASK_NEW_USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_new_user_to_db)]
		},
		fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
	)

	delete_user_handler = ConversationHandler(
		entry_points=[
			CallbackQueryHandler(ask_user_id_to_delete, pattern="^users_delete$")
		],
		states={
			ASK_USER_ID_TO_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_user_deleting)],
			CONFIRM_USER_DELETING: [CallbackQueryHandler(delete_user_from_db, pattern="^confirm_")]
		},
		fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
	)

	application.add_handler(add_user_handler)
	application.add_handler(delete_user_handler)