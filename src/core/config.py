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


class BillingSettings(BaseModel):
	daily_payment: int = Field(default=None, description="Сумма ежедневного списания")
	hour: int = Field(default=12, description="Время проверки биллинга. Часы")
	minute: int = Field(default=0, description="Время проверки биллинга. Минуты")


class AwgSettings(BaseModel):
	server_ip: str = Field(default=None)
	server_port: int = Field(default=None)
	subnet: str = Field(default=None)
	mask: int = Field(default=None)
	dns: str = Field(default=None)
	server_public_key: str = Field(default=None)
	server_private_key: str = Field(default=None)
	config_path: str = Field(default="/etc/amnezia/amneziawg/awg0.conf")
	interface: str = Field(default=None)
	jc: int = Field(default=None)
	jmin: int = Field(default=None)
	jmax: int = Field(default=None)
	s1: int = Field(default=None)
	s2: int = Field(default=None)
	h1: int = Field(default=None)
	h2: int = Field(default=None)
	h3: int = Field(default=None)
	h4: int = Field(default=None)


class Settings(BaseSettings):
	log.debug("Инициализация настроек")

	model_config = SettingsConfigDict(
		env_file=(".env.template", ".env"),
		case_sensitive=False,
		env_nested_delimiter="__",
	)

	app: AppSettings = AppSettings()
	db: DatabaseSettings = DatabaseSettings()
	tg: TelegramSettings = TelegramSettings()
	billing: BillingSettings = BillingSettings()
	awg: AwgSettings = AwgSettings()


settings = Settings()
