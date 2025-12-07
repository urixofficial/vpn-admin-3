from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import connection
from core.logger import log
from core.schemas.user import CreateUser, ReadUser, UpdateUser
from core.models.user import UserModel

from .base import BaseRepo


class UserRepo(BaseRepo[CreateUser, ReadUser, UpdateUser, UserModel]):
	@connection
	async def get_all(self, session: AsyncSession) -> list[ReadUser]:
		log.debug("Получение всех записей из таблицы")
		query = select(self.model).order_by(self.model.name)
		result: Result = await session.execute(query)
		item_models = result.scalars().all()
		return [self.read_schema.model_validate(item_model) for item_model in item_models]

	@connection
	async def get_by_name(self, name: str, session: AsyncSession):
		log.debug("Получение записи по имени '{}'".format(name))
		query = select(self.model).where(self.model.name == name)
		user_model: UserModel | None = await session.scalar(query)
		return self.read_schema.model_validate(user_model) if user_model else None

	@connection
	async def get_active(self, session: AsyncSession) -> list[ReadUser]:
		log.debug("Получение всех активных пользователей")
		query = select(self.model).where(self.model.is_active).order_by(self.model.name)
		result: Result = await session.execute(query)
		item_models = result.scalars().all()
		return [self.read_schema.model_validate(item_model) for item_model in item_models]

	async def block(self, user_id: int):
		log.info("Блокировка пользователя #{}".format(user_id))
		await self.update(UpdateUser(is_active=False))
		# блокировка в интерфейсе AmneziaWG

	async def unblock(self, user_id: int):
		log.info("Разблокировка пользователя #{}".format(user_id))
		await self.update(UpdateUser(is_active=True))
		# блокировка в интерфейсе AmneziaWG


user_repo = UserRepo(CreateUser, ReadUser, UpdateUser, UserModel)
