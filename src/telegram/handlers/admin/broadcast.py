from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from core.logger import log
from core.config import settings
from core.repos.message import message_repo
from core.repos.user import user_repo
from telegram.handlers.admin.keyboards import get_admin_keyboard
from telegram.handlers.keyboards import get_confirmation_keyboard, get_cancel_keyboard

router = Router(name="messages_router")


class NotificationStates(StatesGroup):
	enter_text = State()
	confirmation = State()


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Рассылка")
async def broadcast_step1(message: Message, state: FSMContext):
	log.info("Рассылка уведомлений. Запрос текста...")
	await message.answer("Введите текст уведомления:", reply_markup=get_cancel_keyboard())
	await state.set_state(NotificationStates.enter_text)


@router.message(F.from_user.id == settings.tg.admin_id, NotificationStates.enter_text)
async def broadcast_step2(message: Message, state: FSMContext):
	log.info("Получено значение: {}. Запрос подтверждения...".format(message.text))
	await state.update_data(text=message.text)
	text = "Подтверждение рассылки\n-----------------------------------\n"
	text += message.text
	text += "\n-----------------------------------\nОтправить?"
	await message.answer(text, reply_markup=get_confirmation_keyboard())
	await state.set_state(NotificationStates.confirmation)


@router.message(F.from_user.id == settings.tg.admin_id, NotificationStates.confirmation, F.text == "Да")
async def broadcast_yes(message: Message, state: FSMContext):
	log.info("Подтверждение рассылки получено. Отправка")
	active_users = await user_repo.get_active()
	active_users_ids = [user.id for user in active_users]
	fsm_data = await state.get_data()
	text = fsm_data["text"]
	await message_repo.broadcast(active_users_ids, text)
	await message.answer("Уведомления отправлены пользователям.", reply_markup=get_admin_keyboard())
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, NotificationStates.confirmation, F.text == "Нет")
async def broadcast_no(message: Message, state: FSMContext):
	log.info("Отправка рассылки отклонена")
	await message.answer("Отправка рассылки отменена.", reply_markup=get_admin_keyboard())
	await state.clear()


@router.message(F.from_user.id == settings.tg.admin_id, NotificationStates.confirmation)
async def broadcast_unknown(message: Message, state: FSMContext):
	log.info("Некорректный ввод")
	await message.answer("Введите 'Да' или 'Нет':", reply_markup=get_confirmation_keyboard())
