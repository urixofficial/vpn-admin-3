from pathlib import Path

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.logger import log

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseModel):
	name: str = Field(default="", description="Название приложения")
	version: str = Field(default="", description="Версия приложения")


class DatabaseSettings(BaseModel):
	path: str = Field(default="data/data.db", description="Путь к базе данных")
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
	token: str = Field(default="", description="Telegram Token")
	admin_id: int = Field(default=0, description="Admin ID")


class BillingSettings(BaseModel):
	daily_rate: int = Field(default=0, description="Тариф рублей в день")
	hour: int = Field(default=12, description="Время проверки биллинга. Часы")
	minute: int = Field(default=0, description="Время проверки биллинга. Минуты")
	transactions_limit: int = Field(default=100, description="Ограничение выводимого количества транзакций")


class AwgSettings(BaseModel):
	server_ip: str = Field(default="0.0.0.0")
	server_port: int = Field(default=56789)
	subnet: str = Field(default="10.8.1.0")
	mask: int = Field(default=24)
	dns: str = Field(default="1.1.1.1")
	server_public_key: str = Field(default="")
	server_private_key: str = Field(default="")
	config_path: str = Field(default="/etc/amnezia/amneziawg/awg0.conf")
	interface: str = Field(default="awg0")
	jc: int | None = Field(default=None)
	jmin: int | None = Field(default=None)
	jmax: int | None = Field(default=None)
	s1: int | None = Field(default=None)
	s2: int | None = Field(default=None)
	s3: int | None = Field(default=None)
	s4: int | None = Field(default=None)
	h1: str | None = Field(default=None)
	h2: str | None = Field(default=None)
	h3: str | None = Field(default=None)
	h4: str | None = Field(default=None)
	i1: str | None = Field(default=None)
	i2: str | None = Field(default=None)
	i3: str | None = Field(default=None)
	i4: str | None = Field(default=None)
	i5: str | None = Field(default=None)


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
