from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_cancel_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Отмена")
	return keyboard.as_markup(resize_keyboard=True)


def get_confirmation_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Да")
	keyboard.button(text="Нет")
	keyboard.adjust(2)
	return keyboard.as_markup(resize_keyboard=True)


def get_admin_panel_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Пользователи")
	keyboard.button(text="Транзакции")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)
