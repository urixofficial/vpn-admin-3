# [file name]: bot.py
from telegram import Update
from telegram.ext import Application
from app.core.config import settings
from app.core.logger import log
from app.core.exceptions import TelegramBotException

from .handlers.base import setup_base_handlers
from .handlers.admin import setup_admin_handlers
from .handlers.conversations import setup_conversation_handlers


class VPNBot:
    """Основной класс Telegram бота"""

    def __init__(self):
        self.token = settings.telegram_token
        self.admin_id = settings.telegram_admin_id
        self.application: Application = None

    def setup(self):
        """Настройка бота"""
        if not self.token:
            raise TelegramBotException("Telegram token не установлен в конфигурации")

        self.application = Application.builder().token(self.token).build()
        self._setup_data()
        self._setup_handlers()
        log.info("✅ Telegram бот настроен")

    def _setup_data(self):
        """Помещает данные в контекст бота"""
        if not self.application:
            raise RuntimeError("Application не инициализирован")

        self.application.bot_data["admin_id"] = self.admin_id

    def _setup_handlers(self):
        """Настраивает обработчики команд"""
        if not self.application:
            raise RuntimeError("Application не инициализирован")

        # Настройка всех обработчиков
        setup_base_handlers(self.application, self.admin_id)
        setup_conversation_handlers(self.application, self.admin_id)
        setup_admin_handlers(self.application, self.admin_id)


        log.info("✅ Все обработчики Telegram бота настроены")

    def run(self):
        """Запускает бота в режиме polling"""
        if not self.application:
            self.setup()

        log.info("🔄 Запуск Telegram бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


# Глобальный экземпляр бота
vpn_bot = VPNBot()