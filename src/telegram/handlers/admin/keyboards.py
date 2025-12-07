from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pydantic import BaseModel


def get_admin_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Пользователи")
	keyboard.button(text="Транзакции")
	keyboard.button(text="AWG")
	keyboard.button(text="Рассылка")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)


def get_update_keyboard(item_schema: type[BaseModel]):
	keyboard = ReplyKeyboardBuilder()
	for key in item_schema.model_fields:
		keyboard.button(text=key)
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)
