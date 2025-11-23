from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import connection
from src.core.logger import log
from src.user.dto import CreateUserDto, UserDto, UpdateUserDto
from src.user.orm import UserOrm

@connection
async def get_users(session: AsyncSession) -> list[UserDto]:
	log.debug("Получение всех записей из таблицы")
	stmt = select(UserOrm).order_by(UserOrm.id)
	result: Result = await session.execute(stmt)
	users_orm = result.scalars().all()
	return [UserDto.model_validate(user_orm) for user_orm in users_orm]

@connection
async def get_user(user_id: int, session: AsyncSession) -> UserDto | None:
	log.debug("Получение записи по id={}".format(user_id))
	user_orm = await session.get(UserOrm, user_id)
	return UserDto.model_validate(user_orm) if user_orm else None

@connection
async def create_user(user_dto: CreateUserDto, session: AsyncSession) -> UserDto:
	log.debug("Создание записи {}".format(user_dto))
	user_orm = UserOrm(**user_dto.model_dump())
	session.add(user_orm)
	await session.commit()
	await session.refresh(user_orm)
	return UserDto.model_validate(user_orm)

@connection
async def update_user(user_id: int, update_user_dto: UpdateUserDto, session: AsyncSession) -> UserDto:
	log.debug("Обновление записи с id={} значениями {}".format(user_id, update_user_dto))
	user_orm = await session.get(UserOrm, user_id)
	if not user_orm:
		raise Exception("Запись с id={} не найдена".format(user_id))
	for key, value in update_user_dto.model_dump(exclude_unset=True).items():
		setattr(user_orm, key, value)
	await session.commit()
	await session.refresh(user_orm)
	return UserDto.model_validate(user_orm)

@connection
async def delete_user(user_id: int, session: AsyncSession) -> None:
	log.debug("Удаление записи по id={}".format(user_id))
	user_orm = await session.get(UserOrm, user_id)
	if not user_orm:
		raise Exception("Запись с id={} не найдена".format(user_id))
	await session.delete(user_orm)
	await session.commit()
