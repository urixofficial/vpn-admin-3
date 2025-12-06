from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_awg_control_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Список записей AWG")
	keyboard.button(text="Профиль записи AWG")
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)


def get_awg_profile_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Удалить")
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)
