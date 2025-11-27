from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError

from core.logger import log
from core.schemas.user import CreateUser
from core.repos.user import create_user
from .keyboards import get_cancel_keyboard, get_user_control_keyboard
from .states import CrudUserStates

router = Router(name="create_user_router")

@router.message(F.text == "Создать пользователя")
async def create_user_step1(message: Message, state: FSMContext):
	log.debug("Пользователь {} ({}) выполнил команду /create_user".format(
		message.from_user.full_name,
		message.from_user.id
	))
	await message.answer("Введите ID пользователя:", reply_markup=get_cancel_keyboard())
	await state.set_state(CrudUserStates.create_enter_id)

@router.message(CrudUserStates.create_enter_id)
async def create_user_step2(message: Message, state: FSMContext):
	log.debug("Введен id={}".format(message.text))
	try:
		user_id = int(message.text)
	except ValueError:
		log.error("ID должен быть целым числом")
		await message.answer("ID должен быть целым числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	if user_id <= 0:
		log.error("ID должен быть больше нуля")
		await message.answer("ID должен быть положительным числом. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(id=user_id)
	log.debug("Запрос имени пользователя")
	await message.answer("Введите имя пользователя или псевдоним:", reply_markup=get_cancel_keyboard())
	await state.set_state(CrudUserStates.create_enter_name)

@router.message(CrudUserStates.create_enter_name)
async def create_user_step3(message: Message, state: FSMContext):
	log.debug("Получено имя name={}".format(message.text))
	name = message.text
	if not 3 < len(name) < 24:
		log.error("Имя должно быть от 3 до 24 символов")
		await message.answer("Имя должно быть от 3 до 24 символов. Попробуйте еще раз:", reply_markup=get_cancel_keyboard())
		return
	await state.update_data(name=name)
	log.debug("Создание записи в базе данных")
	data = await state.get_data()
	create_user_dto = CreateUser(**data)
	try:
		user_dto = await create_user(create_user_dto)
		log.debug("Запись успешно добавлена: {}".format(user_dto))
		await  message.answer("Пользователь успешно добавлен.", reply_markup=get_user_control_keyboard())
	except IntegrityError:
		log.error("Ошибка целостности данных")
		await message.answer("Пользователь уже существует.", reply_markup=get_user_control_keyboard())
	except Exception as e:
		log.error("Ошибка: {}".format(e))
		await message.answer("Неизвестная ошибка.", reply_markup=get_user_control_keyboard())
	await state.clear()