from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError

from core.config import settings
from core.logger import log
from core.schemas.user import CreateUser
from core.repos.user import user_repo
from telegram.handlers.keyboards import get_cancel_keyboard
from .keyboards import get_user_control_keyboard
from .states import UserCrudStates

router = Router(name="create_user_router")


@router.message(F.from_user.id == settings.tg.admin_id, F.text == "Создать пользователя")
async def create_user_step1(message: Message, state: FSMContext):
	log.info(
		"Пользователь {} ({}) запустил добавление пользователя. Запрос ID...".format(
			message.from_user.full_name, message.from_user.id
		)
	)
	await message.answer("Введите ID пользователя:", reply_markup=get_cancel_keyboard())
	await state.set_state(UserCrudStates.create_enter_id)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.create_enter_id)
async def create_user_step2(message: Message, state: FSMContext):
	log.info("Получено значение: {}".format(message.text))
	try:
		user_id = int(message.text)
	except ValueError:
		log.info("ID должен быть целым числом. Повторный запрос...")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if user_id <= 0:
		log.info("ID должен быть больше нуля. Повторный запрос...")
		await message.answer(
			"ID должен быть положительным числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard()
		)
		return
	user = await user_repo.get(user_id)
	if user:
		log.info("Пользователь уже существует. Повторный запрос...")
		await message.answer("Пользователь уже существует. Введите другой ID:")
		return
	await state.update_data(id=user_id)
	log.info("ID корректен. Запрос имени пользователя...")
	await message.answer("Введите имя пользователя или псевдоним:", reply_markup=get_cancel_keyboard())
	await state.set_state(UserCrudStates.create_enter_name)


@router.message(F.from_user.id == settings.tg.admin_id, UserCrudStates.create_enter_name)
async def create_user_step3(message: Message, state: FSMContext):
	log.info("Получено значение: {}".format(message.text))
	name = message.text
	if not 3 < len(name) < 24:
		log.info("Имя должно быть от 3 до 24 символов")
		await message.answer(
			"Имя должно быть от 3 до 24 символов. Попробуйте еще раз:", reply_markup=get_cancel_keyboard()
		)
		return
	user = await user_repo.get_by_name(name)
	if user:
		log.info("Имя не уникально. Повторный запрос")
		await message.answer("Имя не уникально. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(name=name)
	log.info("Имя корректно. Создание записи в базе данных")
	data = await state.get_data()
	create_user_dto = CreateUser(**data)
	try:
		user = await user_repo.create(create_user_dto)
		log.info("Пользователь успешно добавлен:\n{}".format(user))
		await message.answer("Пользователь успешно добавлен.", reply_markup=get_user_control_keyboard())
	except IntegrityError:
		log.info("Пользователь уже существует")
		await message.answer("Пользователь уже существует.", reply_markup=get_user_control_keyboard())
	except Exception as e:
		log.error("Ошибка: {}".format(e))
		await message.answer("Неизвестная ошибка.", reply_markup=get_user_control_keyboard())
	await state.clear()
