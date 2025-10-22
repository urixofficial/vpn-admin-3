# [file name]: main.py
# [file content begin]
# !/usr/bin/env python3
"""
Точка входа в приложение VPN Admin
"""

import asyncio
import signal
import sys
from contextlib import AsyncExitStack

from app.core.logger import log
from app.core.config import settings
from app.domains.users.models import UserCreate
from app.domains.users.repository import user_repository
from app.domains.billing.repository import transaction_repository
from app.interfaces.telegram.bot import vpn_bot
from datetime import date, timedelta


def test_database():
	"""Тестирование функциональности базы данных"""
	try:
		log.info("🧪 Тестирование базы данных...")

		# Создаем тестового пользователя
		test_user = UserCreate(
			telegram_id=9999999939,
			username="Test User 2",
			billing_start_date=date.today(),
			billing_end_date=date.today() + timedelta(days=30)
		)

		# Создаем пользователя
		created_user = user_repository.create(test_user)
		log.info(f"✅ Создан тестовый пользователь: {created_user.username}")

		# Создаем тестовую транзакцию
		transaction = transaction_repository.create(created_user.id, 1000)
		log.info(f"✅ Создана тестовая транзакция: {transaction.amount} руб.")

		# Получаем всех пользователей
		users = user_repository.get_all()
		log.info(f"✅ Получено пользователей: {len(users)}")

		# Получаем все транзакции
		transactions = transaction_repository.get_all()
		log.info(f"✅ Получено транзакций: {len(transactions)}")

		# Очищаем тестовые данные
		transaction_repository.delete(transaction.id)
		user_repository.delete(created_user.id)
		log.info("✅ Тестовые данные очищены")

	except Exception as e:
		log.error(f"❌ Ошибка тестирования БД: {e}")


def main():
	"""Запускает основное приложение"""
	log.info(f"🚀 Запуск {settings.app_name} v{settings.app_version}")

	# Проверка конфигурации
	if not settings.is_configured:
		log.error("❌ Не все обязательные настройки заполнены!")
		log.error("Пожалуйста, проверьте файл .env")
		return False

	log.info("✅ Конфигурация загружена успешно")

	# Тестирование базы данных
	test_database()
	log.info("✅ База данных протестирована")

	# Настройка бота
	vpn_bot.setup()
	log.info("✅ Telegram бот настроен")
	try:
		# Запуск бота (это блокирующая операция)
		log.info("🔄 Запуск Telegram бота...")
		log.info("📝 Используйте Ctrl+C для остановки")

		vpn_bot.run()

	except KeyboardInterrupt:
		log.info("📝 Приложение остановлено пользователем")
	except Exception as e:
		log.critical(f"❌ Необработанная ошибка: {e}")
		sys.exit(1)


if __name__ == "__main__":
	# Простой запуск
	main()
# [file content end]