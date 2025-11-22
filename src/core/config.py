from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.logger import log

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
	log.debug("Инициализация настроек")

	model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

	# Общие настройки
	APP_NAME: str = Field(description="Название приложения")
	APP_VERSION: str = Field(description="Версия приложения")

	# Database
	DB_PATH: str = Field(description="DSM-строка для доступа к базе данных")

	# Telegram
	TELEGRAM_TOKEN: str = Field(description="Telegram Token")
	TELEGRAM_ADMIN_ID: int = Field(description="Admin ID")

	@property
	def get_db_url(self):
		return f"sqlite+aiosqlite:///{self.DB_PATH}"

settings = Settings()