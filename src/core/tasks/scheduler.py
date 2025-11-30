# core/tasks/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.logger import log

# Инициализируем глобальный планировщик
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # или твой часовой пояс


def start_scheduler():
	"""Запуск планировщика (вызывать один раз при старте приложения)"""
	if not scheduler.running:
		scheduler.start()
		log.info("Планировщик задач запущен")


def stop_scheduler():
	"""Остановка при graceful shutdown"""
	if scheduler.running:
		scheduler.shutdown()
		log.info("Планировщик задач остановлен")
