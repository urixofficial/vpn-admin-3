from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import connection
from core.logger import log
from core.schemas.user import CreateUser, ReadUser, UpdateUser
from core.models.user import UserModel

from .base import BaseRepo


class UserRepo(BaseRepo[CreateUser, ReadUser, UpdateUser, UserModel]):
	def __init__(self):
		super().__init__(CreateUser, ReadUser, UpdateUser, UserModel)

	@connection
	async def get_all(self, session: AsyncSession) -> list[ReadUser]:
		log.debug("Получение всех записей из таблицы")
		stmt = select(self.model).order_by(self.model.name)
		result: Result = await session.execute(stmt)
		item_models = result.scalars().all()
		return [self.read_schema.model_validate(item_model) for item_model in item_models]

	@connection
	async def get_by_name(self, name: str, session: AsyncSession):
		log.debug("Получение записи по name={}".format(name))
		stmt = select(self.model).where(self.model.name == name)
		user_model: UserModel | None = await session.scalar(stmt)
		return self.read_schema.model_validate(user_model) if user_model else None


user_repo = UserRepo()
