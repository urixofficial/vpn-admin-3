from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pydantic import BaseModel


def get_user_control_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Список пользователей")
	keyboard.button(text="Профиль пользователя")
	keyboard.button(text="Создать пользователя")
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)


def get_profile_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Изменить")
	keyboard.button(text="Удалить")
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)


def get_update_keyboard(item_schema: type[BaseModel]):
	keyboard = ReplyKeyboardBuilder()
	for key in item_schema.model_fields:
		keyboard.button(text=key)
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)
