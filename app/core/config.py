from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path


class Settings(BaseSettings):
    """Основные настройки приложения"""

    # Database
    db_path: str = Field(default="data/data.db", description="Путь к файлу БД")
    db_config_path: str = Field(default="configs/db_config.yaml", description="Путь к конфигу БД")

    # AWG VPN
    awg_server_ip: str = Field(default="", description="IP адрес сервера AWG")
    awg_port: int = Field(default=56789, description="Порт AWG")
    awg_subnet: str = Field(default="10.8.2.0/24", description="Подсеть AWG")
    awg_clients_path: str = Field(default="clients", description="Папка для клиентских конфигов AWG")

    # Telegram
    telegram_token: str = Field(default="", description="Токен бота от BotFather")
    telegram_admin_id: int = Field(description="ID администратора")

    # Logging
    log_level: str = Field(default="INFO", description="Уровень логирования")
    log_file_path: str = Field(default="logs/app.log", description="Путь к файлу логов")
    log_rotation: str = Field(default="1 MB", description="Ротация логов")
    log_retention: str = Field(default="10 days", description="Время хранения логов")

    # Общие настройки
    app_name: str = "VPN Admin"
    app_version: str = "3.0.0"
    debug: bool = Field(default=False, description="Режим отладки")  # Добавили поле debug

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("db_path")
    def ensure_data_dir_exists(cls, v):
        """Создает папку data, если не существует"""
        Path(v).parent.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("awg_clients_path")
    def ensure_clients_dir_exists(cls, v):
        """Создает папку clients, если не существует"""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("log_file_path")
    def ensure_logs_dir_exists(cls, v):
        """Создает папку logs, если не существует"""
        Path(v).parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def is_configured(self) -> bool:
        """Проверяет, что все обязательные настройки заполнены"""
        return all([
	        self.db_path,
	        self.db_config_path,
            self.telegram_token,
            self.telegram_admin_id > 0,
            self.awg_server_ip,
	        self.awg_port,
	        self.awg_subnet
        ])


# Глобальный экземпляр настроек
settings = Settings()