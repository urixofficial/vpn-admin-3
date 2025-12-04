from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_admin_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Пользователи")
	keyboard.button(text="Транзакции")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)
