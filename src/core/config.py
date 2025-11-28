from pathlib import Path

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.logger import log

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseModel):
	name: str = Field(default=None, description="Название приложения")
	version: str = Field(default=None, description="Версия приложения")


class DatabaseSettings(BaseModel):
	path: str = Field(default=None, description="Путь к базе данных")
	echo: bool = Field(default=False, description="Вывод SQL-команд в терминал")

	naming_convention: dict[str, str] = {
		"ix": "ix_%(column_0_label)s",
		"uq": "uq_%(table_name)s_%(column_0_N_name)s",
		"ck": "ck_%(table_name)s_%(constraint_name)s",
		"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
		"pk": "pk_%(table_name)s",
	}

	@property
	def url(self):
		return f"sqlite+aiosqlite:///{BASE_DIR / self.path}"


class TelegramSettings(BaseModel):
	token: str = Field(default=None, description="Telegram Token")
	admin_id: int = Field(default=None, description="Admin ID")


class Settings(BaseSettings):
	log.debug("Инициализация настроек")

	model_config = SettingsConfigDict(
		env_file=(".env.template", ".env"),
		case_sensitive=False,
		env_nested_delimiter="__",
		# env_prefix="CONFIG__",
	)

	app: AppSettings = AppSettings()
	db: DatabaseSettings = DatabaseSettings()
	tg: TelegramSettings = TelegramSettings()


settings = Settings()
