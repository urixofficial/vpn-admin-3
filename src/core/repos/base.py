from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import connection
from core.logger import log
from core.models import Base

CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
ReadSchema = TypeVar("ReadSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
Model = TypeVar("Model", bound=Base)


class BaseRepo[CreateSchema, ReadSchema, UpdateSchema, Model]:
	def __init__(
		self,
		create_schema: type[CreateSchema],
		read_schema: type[ReadSchema],
		update_schema: type[UpdateSchema],
		model: type[Model],
	):
		self.create_schema = create_schema
		self.read_schema = read_schema
		self.update_schema = update_schema
		self.model = model

	@connection
	async def get_all(self, session: AsyncSession) -> list[ReadSchema]:
		log.debug("Получение всех записей из таблицы")
		stmt = select(self.model).order_by(self.model.id)
		result: Result = await session.execute(stmt)
		item_models = result.scalars().all()
		return [self.read_schema.model_validate(item_model) for item_model in item_models]

	@connection
	async def get(self, item_id: int, session: AsyncSession) -> ReadSchema | None:
		log.debug("Получение записи по id={}".format(item_id))
		item_model = await session.get(self.model, item_id)
		return self.read_schema.model_validate(item_model) if item_model else None

	@connection
	async def create(self, create_item: CreateSchema, session: AsyncSession) -> ReadSchema:
		log.debug("Создание записи {}".format(create_item))
		item_model = self.model(**create_item.model_dump())
		session.add(item_model)
		await session.commit()
		# await session.refresh(item_model)
		return self.read_schema.model_validate(item_model)

	@connection
	async def update(self, item_id: int, update_item: UpdateSchema, session: AsyncSession) -> ReadSchema:
		log.debug("Обновление записи с id={} значениями {}".format(item_id, update_item))
		item_model = await session.get(self.model, item_id)
		if not item_model:
			raise Exception("Запись с id={} не найдена".format(item_id))
		for key, value in update_item.model_dump(exclude_unset=True).items():
			setattr(item_model, key, value)
		await session.commit()
		await session.refresh(item_model)
		return self.read_schema.model_validate(item_model)

	@connection
	async def delete(self, item_id: int, session: AsyncSession) -> ReadSchema:
		log.debug("Удаление записи по id={}".format(item_id))
		item_model = await session.get(self.model, item_id)
		if not item_model:
			raise Exception("Запись с id={} не найдена".format(item_id))
		await session.delete(item_model)
		await session.commit()
		return self.read_schema.model_validate(item_model)
