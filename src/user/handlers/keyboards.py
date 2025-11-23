from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.user.dto import UpdateUserDto

def get_cancel_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="/cancel")
	return keyboard.as_markup(resize_keyboard=True)

def get_user_control_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Список пользователей")
	keyboard.button(text="Профиль пользователя")
	keyboard.button(text="Создать пользователя")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)

def get_user_profile_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Изменить")
	keyboard.button(text="Удалить")
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)

def get_confirmation_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Да")
	keyboard.button(text="Нет")
	keyboard.adjust(2)
	return keyboard.as_markup(resize_keyboard=True)

def get_update_user_keyboard():
	keyboard = ReplyKeyboardBuilder()
	for key in UpdateUserDto.model_fields:
		keyboard.button(text=key)
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)