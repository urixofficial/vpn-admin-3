from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_cancel_keyboard():
	cancel_keyboard = ReplyKeyboardBuilder()
	cancel_keyboard.button(text="/cancel")
	return cancel_keyboard.as_markup(resize_keyboard=True)

def get_user_control_keyboard():
	user_control_keyboard = ReplyKeyboardBuilder()
	user_control_keyboard.button(text="/list_users")
	user_control_keyboard.button(text="/show_user")
	user_control_keyboard.button(text="/create_user")
	user_control_keyboard.adjust(1)
	return user_control_keyboard.as_markup(resize_keyboard=True)