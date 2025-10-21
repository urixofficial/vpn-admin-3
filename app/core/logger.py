import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
	"""Настройка системы логирования"""

	# Удаляем стандартный обработчик
	logger.remove()

	# Консольный вывод
	logger.add(
		sys.stdout,
		level=settings.log_level,
		format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
		       "<level>{level: <8}</level> | "
		       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
		       "<level>{message}</level>",
		colorize=True
	)

	# Файловый вывод
	logger.add(
		settings.log_file_path,
		level=settings.log_level,
		format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
		rotation=settings.log_rotation,
		retention=settings.log_retention,
		compression="zip"
	)

	logger.info(f"Логирование инициализировано. Уровень: {settings.log_level}")
	return logger


# Глобальный экземпляр логгера
log = setup_logging()