from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.logger import log

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
	log.debug("Инициализация настроек")

	# Общие настройки
	APP_NAME: str = Field(default=None, description="Название приложения")
	APP_VERSION: str = Field(default=None, description="Версия приложения")

	# Database
	DB_PATH: str = Field(default=None, description="Путь к базе данных")
	DB_ECHO: bool = Field(default=False, description="Вывод SQL-команд в терминал")

	# Telegram
	TELEGRAM_TOKEN: str = Field(default=None, description="Telegram Token")
	TELEGRAM_ADMIN_ID: int = Field(default=None, description="Admin ID")

	model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", case_sensitive=False)

	@property
	def db_url(self):
		return f"sqlite+aiosqlite:///{BASE_DIR / self.DB_PATH}"


settings = Settings()
