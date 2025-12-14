from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.awg import AwgRecordModel
from core.schemas.awg import (
	CreateAwgRecord,
	ReadAwgRecord,
	UpdateAwgRecord,
)

from core.config import settings
from core.logger import log
from vpn.awg.utils import (
	generate_server_config,
	save_file,
	generate_user_config,
	get_free_ip,
	generate_key_pair,
	restart_interface,
)
from core.models import UserModel
from core.database import connection
from .base import BaseRepo


class AwgRepo(BaseRepo[CreateAwgRecord, ReadAwgRecord, UpdateAwgRecord, AwgRecordModel]):
	@connection
	async def get_active(self, session: AsyncSession) -> list[ReadAwgRecord]:
		log.debug("Получение записей AWG только для активных пользователей")
		query = (
			select(AwgRecordModel).join(UserModel, AwgRecordModel.user_id == UserModel.id).where(UserModel.is_active)
		)
		result = await session.execute(query)
		records = result.scalars().all()
		return [self.read_schema.model_validate(record) for record in records]

	@connection
	async def get_by_user(self, user_id: int, session: AsyncSession) -> list[ReadAwgRecord]:
		log.debug("Получение записей AWG пользователя #{}".format(user_id))
		query = select(AwgRecordModel).where(AwgRecordModel.user_id == user_id)
		records = await session.scalars(query)
		return [self.read_schema.model_validate(record) for record in records]

	async def update_server_config(self) -> bool:
		log.debug("Обновление конфигурации сервера: {}".format(settings.awg.config_path))
		# генерация конфига
		active_awg_records = await self.get_active()
		server_config = generate_server_config(settings.awg, active_awg_records)

		# сохранение конфига в файл
		if not save_file(server_config, settings.awg.config_path):
			log.error("Ошибка сохранения конфигурации сервера в файл: {}".format(settings.awg.config_path))
			return False

		# синхронизация интерфейса с новым конфигом
		# sync_server_config(settings.awg.interface, settings.awg.config_path)
		restart_interface(settings.awg.interface)
		return True

	async def add_config(self, user_id: int) -> str | None:
		log.debug("Создание новой конфигурации AWG для пользователя #{}".format(user_id))
		# Получение свободного IP
		awg_records = await self.get_all()
		ip = get_free_ip(awg_records, settings.awg.subnet, settings.awg.mask)
		if not ip:
			log.error("Нет доступных IP-адресов")
			return None

		# Генерация ключей
		private_key, public_key = generate_key_pair()
		# private_key, public_key = "key1", "key2"

		# Формирование записи для таблицы awg
		awg_record = CreateAwgRecord(ip=ip, mask=32, user_id=user_id, public_key=public_key, private_key=private_key)

		# Создание записи в таблице AWG
		awg_record = await self.create(awg_record)

		# Обновление конфигурации сервера
		if not await self.update_server_config():
			log.error("Не удалось обновить конфигурацию сервера.")
			await self.delete(awg_record.id)
			return None

		# Генерация клиентской конфигурации
		user_config = generate_user_config(awg_record, settings.awg)

		log.debug("OK")
		return user_config

	async def del_config(self, awg_record_id: int) -> bool:
		log.debug("Удаление конфигурации AWG #{}".format(awg_record_id))
		try:
			# Проверка существования конфига
			awg_record = await self.get(awg_record_id)
			if not awg_record:
				log.warning("Конфигурация AWG #{} не найдена".format(awg_record_id))
				return False

			# Удаление записи из таблицы awg
			await self.delete(awg_record_id)
			log.info("Конфигурация AWG #{} успешно удалена".format(awg_record_id))

			# Обновление конфигурации сервера
			if not self.update_server_config():
				log.warning("Не удалось обновить конфигурацию сервера: {}".format(settings.awg.config_path))

			return True

		except Exception as e:
			log.error("Ошибка при удалении конфигурации AWG #{}: {}".format(awg_record_id, e))
			return False

	async def get_config(self, user_id: int) -> str | None:
		log.debug("Получение конфигурации AWG для пользователя #{}".format(user_id))

		try:
			awg_records = await self.get_by_user(user_id)
			if awg_records:
				awg_record = awg_records[0]
				user_config = generate_user_config(awg_record, settings.awg)
			else:
				user_config = await self.add_config(user_id)
			return user_config

		except Exception as e:
			log.error("Ошибка при создании конфигурации AWG для пользователя #{}: {}".format(user_id, e))
			return None


awg_repo = AwgRepo(CreateAwgRecord, ReadAwgRecord, UpdateAwgRecord, AwgRecordModel)
