from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.logger import log
from core.repos.awg import awg_repo
from core.repos.user import user_repo
from telegram.handlers.admin.awg_control.keyboards import get_awg_control_keyboard, get_awg_profile_keyboard
from telegram.handlers.admin.awg_control.states import AwgCrudStates
from telegram.handlers.keyboards import get_cancel_keyboard


router = Router(name="read_awg_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Список записей AWG")
async def list_awg_records(message: Message):
	log.info("Вывод списка записей AWG")
	awg_records = await awg_repo.get_all()
	if not awg_records:
		log.debug("Список записей AWG пуст")
		await message.answer("Список записей AWG пуст.")
		return
	text = "Список записей AWG:\n--------------------------------------------\n"
	for awg_record in awg_records:
		line = f"{awg_record.id:03d}. {awg_record.ip}/{awg_record.mask}\n"
		text += line
	await message.answer(text, reply_markup=get_awg_control_keyboard())


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Профиль записи AWG")
async def show_awg_record_step1(message: Message, state: FSMContext):
	log.info("Вывод профиля записи AWG. Запрос ID...")
	await message.answer("Введите ID записи AWG:", reply_markup=get_cancel_keyboard())
	await state.set_state(AwgCrudStates.show_enter_id)


@router.message(F.from_user.id == settings.tg.admin_id, AwgCrudStates.show_enter_id)
async def show_awg_record_step2(message: Message, state: FSMContext):
	log.debug("Получено значение: {}".format(message.text))
	try:
		awg_record_id = int(message.text)
	except ValueError:
		log.info("ID должен быть целым числом. Повторный запрос...")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if awg_record_id <= 0:
		log.info("ID должен быть больше нуля. Повторный запрос...")
		await message.answer(
			"ID должен быть положительным числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard()
		)
		return
	awg_record = await awg_repo.get(awg_record_id)
	if not awg_record:
		log.info("Запись AWG не найдена. Повторный запрос...")
		await message.answer("Запись AWG не найдена. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(awg_record_id=awg_record_id)
	user = await user_repo.get(awg_record.user_id)
	text = (
		f"Запись AWG {awg_record.id}\n"
		"--------------------------------------------\n"
		f"Пользователь: {user.name if user else awg_record.user_id}\n"
		f"IP-адрес: {awg_record.ip}/{awg_record.mask}\n"
		# f"Приватный ключ: {awg_record.private_key}\n"
		# f"Публичный ключ: {awg_record.public_key}\n"
		f"Создана: {awg_record.created_at.date()}\n"
		f"Обновлена: {awg_record.updated_at.date()}"
	)
	await message.answer(text, reply_markup=get_awg_profile_keyboard())
	await state.set_state(AwgCrudStates.show_profile)
