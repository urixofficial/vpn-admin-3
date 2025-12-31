# core/tasks/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from core.logger import log
from core.tasks.debiting import debiting_funds

# Инициализируем глобальный планировщик
scheduler = AsyncIOScheduler(timezone="Asia/Vladivostok")  # или твой часовой пояс


def setup_scheduler():
	"""Настройка планировщика задач"""
	log.debug("Настройка планировщика задач")
	scheduler.add_job(
		debiting_funds,
		trigger="cron",
		hour=settings.billing.hour,
		minute=settings.billing.minute,
	)


def start_scheduler():
	"""Запуск планировщика (вызывать один раз при старте приложения)"""
	if not scheduler.running:
		scheduler.start()
		log.debug("Планировщик задач запущен")


def stop_scheduler():
	"""Остановка при graceful shutdown"""
	if scheduler.running:
		scheduler.shutdown()
		log.debug("Планировщик задач остановлен")
