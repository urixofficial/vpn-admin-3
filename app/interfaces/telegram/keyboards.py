# [file name]: keyboards.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def admin_keyboard():
	"""Инлайн клавиатура администратора (главная)"""
	keyboard = [
		[
			InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")
		],
		[
			InlineKeyboardButton("💲 Транзакции", callback_data="admin_billing")
		],
		[
			InlineKeyboardButton("📊 Статистика", callback_data="admin_system_stats")
		]
	]
	return InlineKeyboardMarkup(keyboard)


def users_keyboard():
	"""Инлайн клавиатура управления пользователями"""
	keyboard = [
		[
			InlineKeyboardButton("📋 Вывести список пользователей", callback_data="users_list")

		],
		[
			InlineKeyboardButton("➕ Добавить", callback_data="users_add"),
			InlineKeyboardButton("✏️ Изменить", callback_data="users_edit"),
			InlineKeyboardButton("➖️ Удалить", callback_data="users_delete")
		],
		[
			InlineKeyboardButton("✖️ Заблокировать", callback_data="users_block"),
			InlineKeyboardButton("✔️ Разблокировать", callback_data="users_unblock")
		],
		[
			InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
		]
	]
	return InlineKeyboardMarkup(keyboard)


def billing_keyboard():
	"""Инлайн клавиатура управления биллингом"""
	keyboard = [
		[
			InlineKeyboardButton("📋 Вывести список транзакций", callback_data="billing_list")

		],
		[
			InlineKeyboardButton("➕ Добавить", callback_data="billing_add"),
			InlineKeyboardButton("➖️ Удалить", callback_data="billing_delete")
		],
		[
			InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
		]
	]
	return InlineKeyboardMarkup(keyboard)


def user_keyboard():
	"""Инлайн клавиатура пользователя"""
	keyboard = [
		[
			InlineKeyboardButton("❔ Помощь", callback_data="user_help"),
			InlineKeyboardButton("📊 Статус", callback_data="user_stats")
		],
		[
			InlineKeyboardButton("📖 Инструкции", callback_data="user_instructions"),
			InlineKeyboardButton("⚙️ Конфиг", callback_data="user_config")
		]
	]
	return InlineKeyboardMarkup(keyboard)


def confirm_keyboard():
    """Клавиатура для подтверждения"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard():
	"""Клавиатура с кнопкой отмены"""
	keyboard = [
		[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
	]
	return InlineKeyboardMarkup(keyboard)


def ask_registration_keyboard():
	"""Злавиатура с запросом регистрации"""
	keyboard = [
		[InlineKeyboardButton("Запрос на регистрацию", callback_data="registration")]
	]
	return InlineKeyboardMarkup(keyboard)
