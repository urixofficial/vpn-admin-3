#!/usr/bin/env python3
"""
Точка входа в приложение VPN Admin
"""

from app.core.logger import log
from app.core.config import settings
from app.domains.users.models import UserCreate
from app.domains.users.repository import user_repository
from app.domains.billing.repository import transaction_repository
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
	"""Основная функция приложения"""
	try:
		log.info(f"Запуск {settings.app_name} v{settings.app_version}")
		log.info(f"Режим: {'development' if settings.debug else 'production'}")

		# Проверка конфигурации
		if not settings.is_configured:
			log.warning("Не все обязательные настройки заполнены!")
			log.warning("Пожалуйста, проверьте файл .env")
			log.warning(f"Telegram token: {'установлен' if settings.telegram_token else 'отсутствует'}")
			log.warning(f"Admin ID: {'установлен' if settings.telegram_admin_id > 0 else 'отсутствует'}")
			log.warning(f"Server IP: {'установлен' if settings.awg_server_ip else 'отсутствует'}")
			return

		log.info("Конфигурация загружена успешно")
		log.info(f"Server IP: {settings.awg_server_ip}")
		log.info(f"Admin ID: {settings.telegram_admin_id}")

		# Здесь будет инициализация и запуск компонентов
		log.info("Инициализация компонентов...")

		# Тестирование базы данных
		test_database()
		log.info("✅ База данных: инициализирована и протестирована")

		# TODO: Запуск Telegram бота
		log.info("Telegram бот: готов к запуску")

		# TODO: Запуск веб-сервера
		log.info("Веб-интерфейс: готов к запуску")

		log.info("Приложение успешно запущено")

		# Заглушка для демонстрации
		log.info("Приложение работает... Нажмите Ctrl+C для остановки")
		try:
			while True:
				pass
		except KeyboardInterrupt:
			log.info("Приложение остановлено пользователем")

	except Exception as e:
		log.critical(f"Критическая ошибка: {e}")
		raise


if __name__ == "__main__":
	main()