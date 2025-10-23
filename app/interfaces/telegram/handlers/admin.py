# [file name]: admin.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, filters

from app.core.logger import log
from app.domains.billing.repository import transaction_repository
from app.domains.users.repository import user_repository
# Импортируем функции из conversations
from .conversations import ask_new_user_id, ask_user_id_to_delete
from .utils import get_sender_id, get_message_func, check_for_admin
from ..keyboards import admin_keyboard, users_keyboard, billing_keyboard


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Панель администратора с инлайн-кнопками"""

	if not check_for_admin(update, context):
		await update.message.reply_text("❌ У вас нет прав доступа.")
		return

	keyboard = admin_keyboard()

	# Для callback query нужно редактировать сообщение
	if update.callback_query:
		await update.callback_query.edit_message_text(
			"👨‍💻 Панель администратора",
			reply_markup=keyboard
		)
	else:
		await update.message.reply_text(
			"👨‍💻 Панель администратора",
			reply_markup=keyboard
		)


async def users_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Панель управления пользователями"""

	if not check_for_admin(update, context):
		await update.message.reply_text("❌ У вас нет прав доступа.")
		return

	keyboard = users_keyboard()

	if update.callback_query:
		await update.callback_query.edit_message_text(
			"👥 Управление пользователями",
			reply_markup=keyboard
		)
	else:
		await update.message.reply_text(
			"👥 Управление пользователями",
			reply_markup=keyboard
		)


async def billing_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Панель управления биллингом"""
	if not check_for_admin(update, context):
		await update.message.reply_text("❌ У вас нет прав доступа.")
		return

	keyboard = billing_keyboard()

	if update.callback_query:
		await update.callback_query.edit_message_text(
			"💰 Управление биллингом",
			reply_markup=keyboard
		)
	else:
		await update.message.reply_text(
			"💰 Управление биллингом",
			reply_markup=keyboard
		)


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Обработчик нажатий на инлайн-кнопки"""

	query = update.callback_query
	await query.answer()

	callback_data = query.data

	if callback_data == "admin_users":
		await users_panel(update, context)
	elif callback_data == "admin_billing":
		await billing_panel(update, context)
	elif callback_data == "admin_system_stats":
		await system_stats(update, context)
	elif callback_data == "users_list":
		await list_users(update, context)
	elif callback_data == "users_add":
		await ask_new_user_id(update, context)
	elif callback_data == "users_delete":
		await ask_user_id_to_delete(update, context)
	elif callback_data == "users_block":
		await block_user(update, context)
	elif callback_data == "users_unblock":
		await unblock_user(update, context)
	elif callback_data == "billing_list":
		await billing_list(update, context)
	elif callback_data == "billing_add":
		await billing_add(update, context)
	elif callback_data == "billing_delete":
		await billing_delete(update, context)
	elif callback_data == "admin_back":
		await admin_panel(update, context)


# ======================== Управление пользователями =======================


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Показывает список пользователей"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	# Вывод списка пользователей
	try:
		users = user_repository.get_all()
		if not users:
			await message_func("📭 Пользователей нет.")
			return

		message = "👥 Список пользователей:\n\n"
		for user in users:
			status_icon = "✅" if user.is_active() else "❌"
			message += f"{status_icon} {user.username} ({user.id})\n"

		# Разбиваем сообщение если слишком длинное
		if len(message) > 4096:
			for x in range(0, len(message), 4096):
				await message_func(message[x:x + 4096])
		else:
			await message_func(message)

	except Exception as e:
		log.error(f"Ошибка получения списка пользователей: {e}.")
		await message_func("❌ Ошибка при получении списка пользователей.")


async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Заглушка для блокировки пользователя"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	await message_func("Функция в разработке")


async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Заглушка для разблокировки пользователя"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	await message_func("Функция в разработке")


# ======================== Управление биллингом =======================


async def billing_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Заглушка для списка транзакций"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	await message_func("Функция в разработке")


async def billing_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Заглушка для добавления транзакции"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	await message_func("Функция в разработке")


async def billing_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Заглушка для удаления транзакции"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	await message_func("Функция в разработке")


# ======================== Статистика =======================


async def system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Показывает статистику системы"""

	message_func = get_message_func(update)

	# Проверка на админа
	if not check_for_admin(update, context):
		await message_func("❌ У вас нет прав доступа.")
		return

	# Вывод системной статистики
	try:
		users = user_repository.get_all()
		active_users = user_repository.get_active_users()
		expired_users = user_repository.get_expired_users()

		message = (
			"📊 Статистика системы:\n\n"
			f"👤 Всего пользователей: {len(users)}.\n"
			f"✅ Активных: {len(active_users)}.\n"
			f"❌ Просроченных: {len(expired_users)}.\n"
			f"💰 Транзакций: {len(transaction_repository.get_all())}."
		)

		await message_func(message)

	except Exception as e:
		log.error(f"Ошибка получения статистики системы: {e}")
		await message_func("❌ Ошибка при получении статистики системы.")


def setup_admin_handlers(application, admin_id: int):
	"""Настраивает административные обработчики"""
	# Фильтр для админа
	admin_filter = filters.User(admin_id)

	application.add_handler(CommandHandler("admin", admin_panel))
	application.add_handler(CommandHandler("users", users_panel))
	application.add_handler(CommandHandler("billing", billing_panel))
	application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
	application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^users_"))
	application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^billing_"))
