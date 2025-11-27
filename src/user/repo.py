from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import connection
from core.logger import log
from core.schemas.user import CreateUser, User, UpdateUser
from core.models.user import UserModel

@connection
async def get_users(session: AsyncSession) -> list[User]:
	log.debug("Получение всех записей из таблицы")
	stmt = select(UserModel).order_by(UserModel.id)
	result: Result = await session.execute(stmt)
	users_orm = result.scalars().all()
	return [User.model_validate(user_orm) for user_orm in users_orm]

@connection
async def get_user(user_id: int, session: AsyncSession) -> User | None:
	log.debug("Получение записи по id={}".format(user_id))
	user_orm = await session.get(UserModel, user_id)
	return User.model_validate(user_orm) if user_orm else None

@connection
async def get_user_by_name(name: str, session: AsyncSession):
	log.debug("Получение записи по name={}".format(name))
	stmt = select(UserModel).where(UserModel.name == name)
	user_orm: UserModel | None = await session.scalar(stmt)
	return User.model_validate(user_orm) if user_orm else None
	

@connection
async def create_user(user_dto: CreateUser, session: AsyncSession) -> User:
	log.debug("Создание записи {}".format(user_dto))
	user_orm = UserModel(**user_dto.model_dump())
	session.add(user_orm)
	await session.commit()
	await session.refresh(user_orm)
	return User.model_validate(user_orm)

@connection
async def update_user(user_id: int, update_user_dto: UpdateUser, session: AsyncSession) -> User:
	log.debug("Обновление записи с id={} значениями {}".format(user_id, update_user_dto))
	user_orm = await session.get(UserModel, user_id)
	if not user_orm:
		raise Exception("Запись с id={} не найдена".format(user_id))
	for key, value in update_user_dto.model_dump(exclude_unset=True).items():
		setattr(user_orm, key, value)
	await session.commit()
	await session.refresh(user_orm)
	return User.model_validate(user_orm)

@connection
async def delete_user(user_id: int, session: AsyncSession) -> None:
	log.debug("Удаление записи по id={}".format(user_id))
	user_orm = await session.get(UserModel, user_id)
	if not user_orm:
		raise Exception("Запись с id={} не найдена".format(user_id))
	await session.delete(user_orm)
	await session.commit()
