from aiogram import Router, F, Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.user import user_repo
from telegram.handlers.keyboards import get_confirmation_keyboard
from telegram.handlers.admin.transaction_control.states import AdminPaymentStates
from telegram.handlers.keyboards import get_cancel_keyboard
from telegram.handlers.user.keyboards import get_start_keyboard, get_user_keyboard
from telegram.handlers.user.states import UserPaymentStates

router = Router(name="user_payment_router")


@router.message(F.text == "Внести оплату")
async def user_payment_step1(message: Message, state: FSMContext):
	log.info("{} ({}): Запуск диалог оплаты. Запрос суммы...".format(message.from_user.full_name, message.from_user.id))
	user = await user_repo.get(message.from_user.id)
	if not user:
		await message.answer("Вы не зарегистрированы.", reply_markup=get_start_keyboard())
		return
	await message.answer("Введите сумму оплаты в рублях:", reply_markup=get_cancel_keyboard())
	await state.set_state(UserPaymentStates.enter_amount)


@router.message(UserPaymentStates.enter_amount)
async def user_payment_step2(message: Message, state: FSMContext):
	log.info("{} ({}): Получено значение: {}".format(message.from_user.full_name, message.from_user.id, message.text))
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
	await state.update_data(amount=amount)
	log.info("Отправка запроса на подтверждение транзакции пользователю")
	await message.answer(
		text="Выполните перевод по номеру телефона +79144158413 на Т-Банк (Юрий Б.), после чего отправьте запрос администратору.\n"
		"----------------------------------------\n"
		f"Сумма: {amount}₽\n"
		"----------------------------------------\n"
		f"Отправить запрос администратору?",
		reply_markup=get_confirmation_keyboard(),
	)
	await state.set_state(UserPaymentStates.confirmation)


@router.message(UserPaymentStates.confirmation, F.text == "Да")
async def user_payment_confirmation_yes(message: Message, state: FSMContext, dispatcher: Dispatcher, bot: Bot):
	log.info("{} ({}): Отправка запроса админу подтверждена".format(message.from_user.full_name, message.from_user.id))
	admin_state: FSMContext = dispatcher.fsm.get_context(
		bot=bot,
		chat_id=settings.tg.admin_id,
		user_id=settings.tg.admin_id,
	)
	data = await state.get_data()
	amount = data.get("amount")
	await admin_state.update_data(user_id=message.from_user.id, amount=amount)
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


@router.message(UserPaymentStates.confirmation, F.text == "Нет")
async def user_payment_confirmation_no(message: Message, state: FSMContext):
	log.info("{} ({}): Отправка запроса админу отклонена".format(message.from_user.full_name, message.from_user.id))
	await message.answer("Операция отменена.", reply_markup=get_user_keyboard())
	await state.clear()


@router.message(UserPaymentStates.confirmation)
async def user_payment_confirmation_unknown(message: Message):
	log.info(
		"{} ({}): Некорректный ввод. Повторный запрос подтверждения оплаты...".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	await message.answer("Выберете 'Да' или 'Нет'.", reply_markup=get_confirmation_keyboard())
	return
