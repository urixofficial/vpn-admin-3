from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_start_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Регистрация")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)


def get_user_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Статус")
	keyboard.button(text="Инструкции")
	keyboard.button(text="Внести оплату")
	keyboard.button(text="Файл конфигурации AWG")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)


def get_instructions_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Android")
	keyboard.button(text="iPhone")
	keyboard.button(text="Windows")
	keyboard.button(text="MacOS")
	keyboard.button(text="Отмена")
	keyboard.adjust(2, 2, 1)
	return keyboard.as_markup(resize_keyboard=True)
