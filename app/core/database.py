import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Iterator
from pathlib import Path
import yaml
from app.core.logger import log
from app.core.config import settings
from app.core.exceptions import DatabaseException


class Database:
	"""Класс для управления базой данных SQLite"""

	def __init__(self, db_path: str, db_config_path: str):
		self.db_path = db_path
		self.db_config_path = Path(db_config_path)
		self.table_config = self._load_table_config()
		self._create_tables()

	def _load_table_config(self) -> Dict[str, Any]:
		"""Загружает конфигурацию таблиц из YAML файла"""
		try:
			# Если путь относительный, делаем его абсолютным относительно корня проекта
			if not self.db_config_path.is_absolute():
				project_root = Path(__file__).parent.parent.parent
				self.db_config_path = project_root / self.db_config_path

			with open(self.db_config_path, 'r', encoding='utf-8') as file:
				config = yaml.safe_load(file) or {}
			log.info(f"Конфигурация БД загружена из {self.db_config_path}")
			return config
		except Exception as e:
			log.error(f"Ошибка загрузки конфигурации БД: {e}")
			raise DatabaseException(f"Не удалось загрузить конфигурацию БД: {e}")

	@contextmanager
	def _get_connection(self) -> Iterator[sqlite3.Connection]:
		"""Контекстный менеджер для соединения с БД"""
		conn = None
		try:
			conn = sqlite3.connect(self.db_path)
			conn.row_factory = sqlite3.Row  # Возвращает строки как словари
			yield conn
		except sqlite3.Error as e:
			log.error(f"Ошибка подключения к БД: {e}")
			raise DatabaseException(f"Ошибка БД: {e}")
		finally:
			if conn:
				conn.close()

	def _create_tables(self) -> None:
		"""Создает таблицы на основе конфигурации"""
		try:
			with self._get_connection() as conn:
				cursor = conn.cursor()

				for table_name, columns in self.table_config.items():
					# Формируем SQL для создания таблицы
					columns_def = [f"{col_name} {col_config.get('type')}" for col_name, col_config in columns.items()]
					create_sql = f"""
				                    CREATE TABLE IF NOT EXISTS {table_name} (
				                        {', '.join(columns_def)}
				                    )
				                    """

					cursor.execute(create_sql)
					log.debug(f"Таблица {table_name} создана/проверена")

				conn.commit()
				log.info("Все таблицы успешно созданы/проверены")

		except Exception as e:
			log.error(f"Ошибка создания таблиц: {e}")
			raise DatabaseException(f"Не удалось создать таблицы: {e}")

	def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
		"""Выполняет SQL запрос и возвращает курсор"""
		try:
			with self._get_connection() as conn:
				cursor = conn.cursor()
				cursor.execute(query, params)
				conn.commit()
				return cursor
		except sqlite3.Error as e:
			log.error(f"Ошибка выполнения запроса: {query} с параметрами {params}: {e}")
			raise DatabaseException(f"Ошибка выполнения запроса: {e}")

	def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
		"""Выполняет запрос и возвращает все результаты"""
		try:
			with self._get_connection() as conn:
				cursor = conn.cursor()
				cursor.execute(query, params)
				return [dict(row) for row in cursor.fetchall()]
		except sqlite3.Error as e:
			log.error(f"Ошибка получения данных: {e}")
			raise DatabaseException(f"Ошибка получения данных: {e}")

	def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
		"""Выполняет запрос и возвращает одну запись"""
		try:
			with self._get_connection() as conn:
				cursor = conn.cursor()
				cursor.execute(query, params)
				row = cursor.fetchone()
				return dict(row) if row else None
		except sqlite3.Error as e:
			log.error(f"Ошибка получения записи: {e}")
			raise DatabaseException(f"Ошибка получения записи: {e}")

	def insert(self, table: str, data: Dict[str, Any]) -> int:
		"""Вставляет запись и возвращает ID"""
		try:
			columns = ', '.join(data.keys())
			placeholders = ', '.join(['?' for _ in data])
			query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

			with self._get_connection() as conn:
				cursor = conn.cursor()
				cursor.execute(query, tuple(data.values()))
				conn.commit()
				return cursor.lastrowid
		except sqlite3.Error as e:
			log.error(f"Ошибка вставки в таблицу {table}: {e}")
			raise DatabaseException(f"Ошибка вставки данных: {e}")

	def update(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
		"""Обновляет запись по ID"""
		try:
			set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
			query = f"UPDATE {table} SET {set_clause} WHERE id = ?"

			with self._get_connection() as conn:
				cursor = conn.cursor()
				cursor.execute(query, tuple(data.values()) + (record_id,))
				conn.commit()
				return cursor.rowcount > 0
		except sqlite3.Error as e:
			log.error(f"Ошибка обновления записи {record_id} в таблице {table}: {e}")
			raise DatabaseException(f"Ошибка обновления данных: {e}")

	def delete(self, table: str, record_id: int) -> bool:
		"""Удаляет запись по ID"""
		try:
			query = f"DELETE FROM {table} WHERE id = ?"

			with self._get_connection() as conn:
				cursor = conn.cursor()
				cursor.execute(query, (record_id,))
				conn.commit()
				return cursor.rowcount > 0
		except sqlite3.Error as e:
			log.error(f"Ошибка удаления записи {record_id} из таблицы {table}: {e}")
			raise DatabaseException(f"Ошибка удаления данных: {e}")


# Глобальный экземпляр базы данных
db = Database(settings.db_path, settings.db_config_path)