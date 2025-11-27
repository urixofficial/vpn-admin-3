from aiogram.utils.keyboard import ReplyKeyboardBuilder

from core.schemas.transaction import UpdateTransaction


def get_transaction_control_keyboard():
	keyboard = ReplyKeyboardBuilder()
	keyboard.button(text="Список транзакций")
	keyboard.button(text="Профиль транзакции")
	keyboard.button(text="Добавить транзакцию")
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


def get_update_keyboard():
	keyboard = ReplyKeyboardBuilder()
	for key in UpdateTransaction.model_fields:
		keyboard.button(text=key)
	keyboard.button(text="Отмена")
	keyboard.adjust(1)
	return keyboard.as_markup(resize_keyboard=True)
