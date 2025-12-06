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
	create_server_interface_config,
	create_server_peers_config,
	save_file,
	create_user_config,
	get_free_ip,
	generate_key_pair,
	sync_server_config,
)
from core.models import UserModel
from core.database import connection
from .base import BaseRepo


class AwgRepo(BaseRepo[CreateAwgRecord, ReadAwgRecord, UpdateAwgRecord, AwgRecordModel]):
	@connection
	async def get_active(self, session: AsyncSession) -> list[ReadAwgRecord]:
		log.debug("Получение AWG-записей только для активных пользователей")
		query = select(AwgRecordModel).join(UserModel, AwgRecordModel.id == UserModel.id).where(UserModel.is_active)
		result = await session.execute(query)
		records = result.scalars().all()
		return [self.read_schema.model_validate(record) for record in records]

	async def update_server_config(self) -> bool:
		# генерация конфига
		interface_config = create_server_interface_config(settings.awg)
		active_awg_records = await self.get_active()
		peers_config = create_server_peers_config(active_awg_records)
		server_config = interface_config + peers_config

		# сохранение конфига в файл
		if not save_file(server_config, settings.awg.config_path):
			log.error("Ошибка сохранения конфигурации сервера в файл")
			return False

		sync_server_config(settings.awg.interface, settings.awg.config_path)
		return True

	async def add_config(self, user_id: int) -> str | None:
		log.debug("Создание новой конфигурации AWG для пользователя {}".format(user_id))
		# Получение свободного IP
		awg_records = await self.get_all()
		user_ip = get_free_ip(awg_records, settings.awg.subnet, settings.awg.mask)
		if not user_ip:
			log.error("Нет доступных IP-адресов")
			return None

		# Генерация ключей
		private_key, public_key = generate_key_pair()

		# Формирование записи для таблицы awg
		awg_record = CreateAwgRecord(id=user_id, ip=user_ip, mask=32, public_key=public_key, private_key=private_key)

		# Создание записи в таблице AWG
		awg_record = await self.create(awg_record)

		# Обновление конфигурации сервера
		if not await self.update_server_config():
			log.error("Не удалось обновить конфигурацию сервера.")
			await self.delete(awg_record.id)
			return None

		# Генерация клиентской конфигурации
		user_config = create_user_config(awg_record, settings.awg)

		log.info("OK")
		return user_config

	async def del_config(self, user_id: int) -> bool:
		log.debug("Удаление конфигурации AWG для пользователя {}".format(user_id))
		try:
			# Проверка существования конфига
			awg_record = await self.get(user_id)
			if not awg_record:
				log.warning("Конфигурация AWG для пользователя {} не найдена".format(user_id))
				return False

			# Удаление записи из таблицы awg
			await self.delete(user_id)
			log.info("Конфигурация AWG для пользователя {} успешно удалена".format(user_id))

			# Обновление конфигурации сервера
			if not self.update_server_config():
				log.warning("Не удалось обновить конфигурацию сервера.")

			return True

		except Exception as e:
			log.error("Ошибка при удалении конфигурации AWG для пользователя {}: {}".format(user_id, e))
			return False

	async def get_config(self, user_id: int) -> str | None:
		log.debug("Получение конфигурации AWG для пользователя {}".format(user_id))

		try:
			awg_record = await self.get(user_id)
			if awg_record:  # если есть запись в таблице awg
				user_config = create_user_config(awg_record, settings.awg)
			else:  # Создание новой записи
				user_config = await self.add_config(user_id)
			return user_config

		except Exception as e:
			log.error("Ошибка при создании конфигурации AWG для пользователя {}: {}".format(user_id, e))
			return None


awg_repo = AwgRepo(CreateAwgRecord, ReadAwgRecord, UpdateAwgRecord, AwgRecordModel)
