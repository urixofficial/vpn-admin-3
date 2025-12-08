from aiogram import Router, F, Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.user import user_repo
from telegram.handlers.keyboards import get_confirmation_keyboard
from telegram.handlers.admin.transaction_control.states import AdminPaymentStates
from telegram.handlers.keyboards import get_cancel_keyboard
from telegram.handlers.user.keyboards import get_start_keyboard
from telegram.handlers.user.states import UserPaymentStates

router = Router(name="user_payment_router")


@router.message(F.text == "Сообщить об оплате")
async def user_payment_step1(message: Message, state: FSMContext):
	log.info(
		"{} ({}) запустил диалог оплаты. Запрос суммы...".format(message.from_user.full_name, message.from_user.id)
	)
	user = await user_repo.get(message.from_user.id)
	if not user:
		await message.answer("Вы не зарегистрированы.", reply_markup=get_start_keyboard())
		return
	await message.answer("Введите сумму оплаты в рублях:", reply_markup=get_cancel_keyboard())
	await state.set_state(UserPaymentStates.enter_amount)


@router.message(UserPaymentStates.enter_amount)
async def user_payment_step2(message: Message, state: FSMContext, dispatcher: Dispatcher, bot: Bot):
	log.info("Получено значение: {}".format(message.text))
	try:
		amount = int(message.text)
	except ValueError:
		log.info("Сумма должна быть целым числом. Повторный запрос...")
		await message.answer("Сумма должна быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if amount <= 0:
		log.info("Сумма должна быть больше нуля. Повторный запрос...")
		await message.answer("Сумма должна быть больше нуля. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return

	log.info("Отправка запроса на подтверждение транзакции администратору")
	admin_state: FSMContext = dispatcher.fsm.get_context(
		bot=bot,
		chat_id=settings.tg.admin_id,
		user_id=settings.tg.admin_id,
	)
	await admin_state.update_data(
		user_id=message.from_user.id,
		amount=amount,
	)
	await message.bot.send_message(
		chat_id=settings.tg.admin_id,
		text="Оплата\n"
		"----------------------------------------\n"
		f"Пользователь: {message.from_user.full_name} ({message.from_user.id})\n"
		f"Сумма: {amount}₽\n"
		"----------------------------------------\n"
		f"Подтвердить?",
		reply_markup=get_confirmation_keyboard(),
	)
	await admin_state.set_state(AdminPaymentStates.confirmation)
	await message.answer("Запрос на подтверждение оплаты отправлен.")
	await state.clear()
