# [file name]: bot.py
# [file content begin]
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
	Application, CommandHandler, MessageHandler,
	ContextTypes, filters, ConversationHandler
)
from datetime import date, timedelta
import re

from app.core.exceptions import TelegramBotException, UserAlreadyExistsException, UserNotFoundException
from app.core.logger import log
from app.core.config import settings
from app.domains.users.repository import user_repository
from app.domains.users.models import UserCreate, UserStatus
from app.domains.billing.repository import transaction_repository


class VPNBot():
	"""Основной класс Telegram бота"""

	def __init__(self):
		self.token = settings.telegram_token
		self.admin_id = settings.telegram_admin_id
		self.application: Application = None

		# Состояния для ConversationHandler
		self.ADD_USER, self.DELETE_USER, self.EXTEND_USER = range(3)

	def setup(self):
		"""Настройка бота (синхронная)"""
		if not self.token:
			raise TelegramBotException("Telegram token не установлен в конфигурации")
		self.application = Application.builder().token(self.token).build()
		self._setup_handlers()
		log.info("✅ Telegram бот настроен")

	async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Обработчик команды /start"""
		user = update.effective_user
		user_id = user.id

		try:
			db_user = user_repository.get_by_id(user_id)

			if db_user:
				if db_user.is_active():
					days_left = db_user.days_until_expiry()
					message = (
						f"👋 Привет, {db_user.username}!\n\n"
						f"✅ Ваш VPN активен\n"
						f"📅 Осталось дней: {days_left}\n"
						f"💰 Дата окончания: {db_user.billing_end_date}\n\n"
						f"Для получения конфига используйте /get_config"
					)
				else:
					message = (
						f"👋 Привет, {db_user.username}!\n\n"
						f"❌ Ваш VPN неактивен\n"
						f"💰 Для продления обратитесь к администратору"
					)
			else:
				message = (
					f"👋 Привет, {user.first_name}!\n\n"
					f"Вы не зарегистрированы в системе VPN.\n"
					f"Для подключения обратитесь к администратору."
				)

			await update.message.reply_text(message)

		except Exception as e:
			log.error(f"Ошибка в команде /start для {user_id}: {e}")
			await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

	async def get_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Отправляет конфиг пользователю"""
		user = update.effective_user
		user_id = user.id

		try:
			db_user = user_repository.get_by_id(user_id)
			if not db_user:
				await update.message.reply_text("❌ Вы не зарегистрированы в системе.")
				return

			if not db_user.is_active():
				await update.message.reply_text("❌ Ваш VPN неактивен. Продлите доступ.")
				return

			# Временно заглушка - конфиг будет позже
			await update.message.reply_text(
				"📁 Функция получения конфига временно недоступна.\n"
				"Администратор уведомлен о вашем запросе."
			)

			# Уведомляем администратора
			if self.application:
				await self.application.bot.send_message(
					chat_id=self.admin_id,
					text=f"👤 Пользователь {db_user.username} запросил конфиг\n"
					     f"ID: {user_id}\n"
					     f"Статус: {'Активен' if db_user.is_active() else 'Неактивен'}"
				)

			log.info(f"Пользователь {db_user.username} запросил конфиг")

		except Exception as e:
			log.error(f"Ошибка получения конфига для {user_id}: {e}")
			await update.message.reply_text("❌ Ошибка при получении конфига.")

	async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Показывает статистику использования"""
		user = update.effective_user
		user_id = user.id

		try:
			db_user = user_repository.get_by_id(user_id)
			if not db_user:
				await update.message.reply_text("❌ Вы не зарегистрированы в системе.")
				return

			message = (
				f"📊 Ваша статистика:\n\n"
				f"👤 Имя: {db_user.username}\n"
				f"📅 Начало периода: {db_user.billing_start_date}\n"
				f"📅 Конец периода: {db_user.billing_end_date}\n"
				f"⏳ Осталось дней: {db_user.days_until_expiry()}\n"
				f"🎯 Статус: {'✅ Активен' if db_user.is_active() else '❌ Неактивен'}"
			)

			await update.message.reply_text(message)

		except Exception as e:
			log.error(f"Ошибка получения статистики для {user_id}: {e}")
			await update.message.reply_text("❌ Ошибка при получении статистики.")

	async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Панель администратора"""
		user = update.effective_user

		if user.id != self.admin_id:
			await update.message.reply_text("❌ У вас нет прав доступа.")
			return

		keyboard = [
			[KeyboardButton("👥 Список пользователей"), KeyboardButton("🆕 Добавить пользователя")],
			[KeyboardButton("🗑️ Удалить пользователя"), KeyboardButton("📊 Статистика системы")],
			[KeyboardButton("⏰ Продлить доступ"), KeyboardButton("🚫 Блокировать пользователя")]
		]

		reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

		await update.message.reply_text(
			"👨‍💻 Панель администратора",
			reply_markup=reply_markup
		)

	async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Показывает список пользователей"""
		if update.effective_user.id != self.admin_id:
			return

		try:
			users = user_repository.get_all()
			if not users:
				await update.message.reply_text("📭 Пользователей нет")
				return

			message = "👥 Список пользователей:\n"
			for user in users:
				status_icon = "✅" if user.is_active() else "❌"
				message += f"{status_icon} {user.username} (ID: {user.id})\n"

			# Разбиваем сообщение если слишком длинное
			if len(message) > 4096:
				for x in range(0, len(message), 4096):
					await update.message.reply_text(message[x:x + 4096])
			else:
				await update.message.reply_text(message)

		except Exception as e:
			log.error(f"Ошибка получения списка пользователей: {e}")
			await update.message.reply_text("❌ Ошибка при получении списка пользователей.")

	async def system_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Показывает статистику системы"""
		if update.effective_user.id != self.admin_id:
			return

		try:
			users = user_repository.get_all()
			active_users = user_repository.get_active_users()
			expired_users = user_repository.get_expired_users()

			message = (
				"📊 Статистика системы:\n\n"
				f"👥 Всего пользователей: {len(users)}\n"
				f"✅ Активных: {len(active_users)}\n"
				f"❌ Просроченных: {len(expired_users)}\n"
				f"💰 Транзакций: {len(transaction_repository.get_all())}"
			)

			await update.message.reply_text(message)

		except Exception as e:
			log.error(f"Ошибка получения статистики системы: {e}")
			await update.message.reply_text("❌ Ошибка при получении статистики системы.")

	# === УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ===

	async def add_user_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Начинает процесс добавления пользователя"""
		if update.effective_user.id != self.admin_id:
			return

		await update.message.reply_text(
			"👤 Добавление нового пользователя\n\n"
			"Введите данные в формате:\n"
			"<code>ID_пользователя Имя_пользователя Количество_дней</code>\n\n"
			"Пример:\n"
			"<code>123456789 ИванИванов</code>\n\n"
			"Или отправьте /cancel для отмены",
			parse_mode="HTML"
		)
		return self.ADD_USER

	async def add_user_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Обрабатывает ввод данных для добавления пользователя"""
		try:
			text = update.message.text.strip()

			# Проверяем формат ввода
			parts = text.split()
			if len(parts) != 2:
				await update.message.reply_text(
					"❌ Неверный формат. Используйте:\n"
					"<code>ID Имя Количество_дней</code>\n\n"
					"Попробуйте еще раз:",
					parse_mode="HTML"
				)
				return self.ADD_USER

			user_id_str, username = parts

			# Валидация ID пользователя
			if not user_id_str.isdigit():
				await update.message.reply_text(
					"❌ ID пользователя должен быть числом\n"
					"Попробуйте еще раз:"
				)
				return self.ADD_USER

			user_id = int(user_id_str)

			# Создаем пользователя
			user_data = UserCreate(
				telegram_id=user_id,
				username=username,
				billing_start_date=date.today(),
				billing_end_date=date.today()
			)

			created_user = user_repository.create(user_data)

			await update.message.reply_text(
				f"✅ Пользователь успешно добавлен!\n\n"
				f"👤 Имя: {created_user.username}\n"
				f"🆔 ID: {created_user.id}\n"
				f"📅 Начало: {created_user.billing_start_date}\n"
				f"📅 Конец: {created_user.billing_end_date}\n"
			)

			log.info(f"Администратор добавил пользователя: {created_user.username} (ID: {user_id})")
			return ConversationHandler.END

		except UserAlreadyExistsException as e:
			await update.message.reply_text(
				f"❌ Пользователь с ID {user_id} уже существует\n"
				"Попробуйте еще раз с другим ID:"
			)
			return self.ADD_USER
		except Exception as e:
			log.error(f"Ошибка добавления пользователя: {e}")
			await update.message.reply_text(
				f"❌ Ошибка при добавлении пользователя: {str(e)}\n"
				"Попробуйте еще раз:"
			)
			return self.ADD_USER

	async def delete_user_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Начинает процесс удаления пользователя"""
		if update.effective_user.id != self.admin_id:
			return

		# Показываем список пользователей для удобства
		users = user_repository.get_all()
		if not users:
			await update.message.reply_text("📭 Пользователей нет для удаления")
			return ConversationHandler.END

		user_list = "👥 Текущие пользователи:\n\n"
		for user in users:
			status_icon = "✅" if user.is_active() else "❌"
			user_list += f"{status_icon} {user.username} (ID: {user.id})\n"

		user_list += "\nВведите ID пользователя для удаления:\n(или /cancel для отмены)"

		await update.message.reply_text(user_list)
		return self.DELETE_USER

	async def delete_user_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Обрабатывает ввод ID для удаления пользователя"""
		try:
			text = update.message.text.strip()

			if not text.isdigit():
				await update.message.reply_text(
					"❌ ID пользователя должен быть числом\n"
					"Попробуйте еще раз:"
				)
				return self.DELETE_USER

			user_id = int(text)

			# Получаем пользователя для информации
			user = user_repository.get_by_id(user_id)
			if not user:
				await update.message.reply_text(
					f"❌ Пользователь с ID {user_id} не найден\n"
					"Попробуйте еще раз:"
				)
				return self.DELETE_USER

			# Удаляем пользователя
			user_repository.delete(user_id)

			await update.message.reply_text(
				f"✅ Пользователь успешно удален!\n\n"
				f"👤 Имя: {user.username}\n"
				f"🆔 ID: {user.id}"
			)

			log.info(f"Администратор удалил пользователя: {user.username} (ID: {user_id})")
			return ConversationHandler.END

		except Exception as e:
			log.error(f"Ошибка удаления пользователя: {e}")
			await update.message.reply_text(
				f"❌ Ошибка при удалении пользователя: {str(e)}\n"
				"Попробуйте еще раз:"
			)
			return self.DELETE_USER

	async def extend_user_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Продлевает доступ пользователю"""
		if update.effective_user.id != self.admin_id:
			return

		await update.message.reply_text(
			"⏰ Продление доступа пользователю\n\n"
			"Введите данные в формате:\n"
			"<code>ID_пользователя Количество_дней</code>\n\n"
			"Пример:\n"
			"<code>123456789 30</code>\n\n"
			"Или отправьте /cancel для отмены",
			parse_mode="HTML"
		)
		return self.EXTEND_USER

	async def extend_user_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Обрабатывает продление доступа"""
		try:
			text = update.message.text.strip()
			parts = text.split()

			if len(parts) != 2:
				await update.message.reply_text(
					"❌ Неверный формат. Используйте:\n"
					"<code>ID Количество_дней</code>\n\n"
					"Попробуйте еще раз:",
					parse_mode="HTML"
				)
				return self.EXTEND_USER

			user_id_str, days_str = parts

			if not user_id_str.isdigit():
				await update.message.reply_text("❌ ID пользователя должен быть числом")
				return self.EXTEND_USER

			if not days_str.isdigit() or int(days_str) <= 0:
				await update.message.reply_text("❌ Количество дней должно быть положительным числом")
				return self.EXTEND_USER

			user_id = int(user_id_str)
			days = int(days_str)

			user = user_repository.get_by_id(user_id)
			if not user:
				await update.message.reply_text(f"❌ Пользователь с ID {user_id} не найден")
				return self.EXTEND_USER

			# Продлеваем доступ
			new_end_date = user.billing_end_date + timedelta(days=days)
			user_repository.update(user_id, user.__class__(
				username=user.username,
				billing_start_date=user.billing_start_date,
				billing_end_date=new_end_date,
				status=user.status
			))

			await update.message.reply_text(
				f"✅ Доступ успешно продлен!\n\n"
				f"👤 Пользователь: {user.username}\n"
				f"🆔 ID: {user.id}\n"
				f"📅 Новый срок: {new_end_date}\n"
				f"⏳ Добавлено дней: {days}"
			)

			log.info(f"Администратор продлил доступ пользователю {user.username} на {days} дней")
			return ConversationHandler.END

		except Exception as e:
			log.error(f"Ошибка продления доступа: {e}")
			await update.message.reply_text(f"❌ Ошибка: {str(e)}")
			return self.EXTEND_USER

	async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""Отменяет текущую операцию"""
		await update.message.reply_text("❌ Операция отменена")
		return ConversationHandler.END

	def _setup_handlers(self):
		"""Настраивает обработчики команд"""
		if not self.application:
			raise RuntimeError("Application не инициализирован")

		# Базовые команды
		self.application.add_handler(CommandHandler("start", self.start))
		self.application.add_handler(CommandHandler("get_config", self.get_config))
		self.application.add_handler(CommandHandler("stats", self.stats))
		self.application.add_handler(CommandHandler("admin", self.admin_panel))

		# Conversation Handlers для управления пользователями
		add_user_conv = ConversationHandler(
			entry_points=[MessageHandler(filters.Regex("🆕 Добавить пользователя"), self.add_user_start)],
			states={
				self.ADD_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_user_process)]
			},
			fallbacks=[CommandHandler("cancel", self.cancel)]
		)

		delete_user_conv = ConversationHandler(
			entry_points=[MessageHandler(filters.Regex("🗑️ Удалить пользователя"), self.delete_user_start)],
			states={
				self.DELETE_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.delete_user_process)]
			},
			fallbacks=[CommandHandler("cancel", self.cancel)]
		)

		extend_user_conv = ConversationHandler(
			entry_points=[MessageHandler(filters.Regex("⏰ Продлить доступ"), self.extend_user_access)],
			states={
				self.EXTEND_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.extend_user_process)]
			},
			fallbacks=[CommandHandler("cancel", self.cancel)]
		)

		# Административные команды
		self.application.add_handler(MessageHandler(filters.Regex("👥 Список пользователей"), self.show_users))
		self.application.add_handler(MessageHandler(filters.Regex("📊 Статистика системы"), self.system_stats))

		# Добавляем Conversation Handlers
		self.application.add_handler(add_user_conv)
		self.application.add_handler(delete_user_conv)
		self.application.add_handler(extend_user_conv)

		log.info("✅ Обработчики Telegram бота настроены")

	def run(self):
		"""Запускает бота в режиме polling"""
		if not self.application:
			self.setup()

		log.info("🔄 Запуск Telegram бота...")
		self.application.run_polling(allowed_updates=Update.ALL_TYPES)


# Глобальный экземпляр бота
vpn_bot = VPNBot()
# [file content end]