from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import connection
from core.logger import log
from core.schemas.user import CreateUser, ReadUser, UpdateUser
from core.models.user import UserModel
from vpn.awg.utils import sync_server_config

from .base import BaseRepo
from ..config import settings


class UserRepo(BaseRepo[CreateUser, ReadUser, UpdateUser, UserModel]):
	@connection
	async def get_all(self, session: AsyncSession) -> list[ReadUser]:
		log.debug("Получение всех записей из таблицы '{}'".format(self.model.__tablename__))
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
		log.debug("Получение всех активных пользователей из таблицы '{}'".format(self.model.__tablename__))
		query = select(self.model).where(self.model.is_active).order_by(self.model.name)
		result: Result = await session.execute(query)
		item_models = result.scalars().all()
		return [self.read_schema.model_validate(item_model) for item_model in item_models]

	@connection
	async def set_unlimited(self, user_id: int, session: AsyncSession) -> ReadUser:
		log.debug("Установка безлимитного баланса пользователю #{}".format(user_id))
		user_model = await session.get(self.model, user_id)
		user_model.balance = None
		user_model.is_active = True
		await session.commit()
		await session.refresh(user_model)
		sync_server_config(settings.awg.interface, settings.awg.config_path)
		return self.read_schema.model_validate(user_model)

	async def block(self, user_id: int):
		log.info("Блокировка пользователя #{}".format(user_id))
		await self.update(user_id, UpdateUser(is_active=False))
		sync_server_config(settings.awg.interface, settings.awg.config_path)

	async def unblock(self, user_id: int):
		log.info("Разблокировка пользователя #{}".format(user_id))
		await self.update(user_id, UpdateUser(is_active=True))
		sync_server_config(settings.awg.interface, settings.awg.config_path)


user_repo = UserRepo(CreateUser, ReadUser, UpdateUser, UserModel)
