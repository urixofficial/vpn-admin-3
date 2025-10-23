# [file name]: base.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from app.core.logger import log
from app.domains.users.repository import user_repository
from ..keyboards import user_keyboard, ask_registration_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Обработчик команды /start"""
	user = update.effective_user
	user_id = user.id
	username = user.username

	try:
		db_user = user_repository.get_by_id(user_id)

		if db_user:
			if db_user.is_active():
				days_left = db_user.days_until_expiry()
				message = (
					f"👋 Привет, {username}!\n\n"
					f"✅ Ваш VPN активен.\n"
					f"📅 Осталось дней: {days_left}.\n"
					f"💰 Дата окончания: {db_user.billing_end_date}.\n\n"
				)
			else:
				message = (
					f"👋 Привет, {username}!\n\n"
					f"❌ Ваш VPN неактивен.\n"
					f"💰 Для продления внесите оплату."
				)
			keyboard = user_keyboard()
		else:
			message = (
				f"👋 Привет, {username}!\n\n"
				f"Вы не зарегистрированы в системе VPN.\n"
			)
			keyboard = ask_registration_keyboard()

		await update.message.reply_text(message, reply_markup=keyboard)

	except Exception as e:
		log.error(f"Ошибка в команде /start для {user_id}: {e}")
		await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")


async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Отправляет запрос на регистрацию пользователя"""
	user = update.effective_user
	user_id = user.id
	username = user.username
	admin_id = context.bot_data["admin_id"]

	# Сообщение админу
	context.bot.send_message(
		chat_id=admin_id,
		text=f"Пользователь {username} ({user_id}) запросил регистрацию.",
		reply_markup=ask_registration_keyboard()
	)

	# Сообщение пользователю
	await update.message.reply_text("Ваш запрос на регистрацию отправлен администратору.")


async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
		if context.bot_data.get("admin_id"):
			await context.bot.send_message(
				chat_id=context.bot_data["admin_id"],
				text=f"👤 Пользователь {db_user.username} запросил конфиг\n"
				     f"ID: {user_id}\n"
				     f"Статус: {'Активен' if db_user.is_active() else 'Неактивен'}"
			)

		log.info(f"Пользователь {db_user.username} запросил конфиг")

	except Exception as e:
		log.error(f"Ошибка получения конфига для {user_id}: {e}")
		await update.message.reply_text("❌ Ошибка при получении конфига.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

		if update.callback_query:
			await update.callback_query.message.reply_text(message)
		else:
			await update.message.reply_text(message)

	except Exception as e:
		log.error(f"Ошибка получения статистики для {user_id}: {e}")
		await update.message.reply_text("❌ Ошибка при получении статистики.")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Показывает справку"""
	message = (
		"❔ Помощь по боту VPN:\n\n"
		"📋 Доступные команды:\n"
		"❔Помощь - Вывод данного сообщения.\n"
		"📊Статус - Информация о вашей учетной записи.\n"
		"📖Инструкции - Информация о настройке VPN.\n"
		"⚙ Конфиг - Получить файл конфигурации.\n\n"
	)
	if update.callback_query:
		await update.callback_query.message.reply_text(message)
	else:
		await update.message.reply_text(message)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Показывает инструкции"""
	message = (
		"📖 Инструкции по использованию VPN:\n\n"
		"1. Установите WireGuard клиент на ваше устройство\n"
		"2. Получите конфигурационный файл через бота\n"
		"3. Импортируйте конфиг в приложение WireGuard\n"
		"4. Активируйте подключение\n\n"
		"⚠️ Если возникли проблемы, обратитесь к администратору."
	)
	if update.callback_query:
		await update.callback_query.message.reply_text(message)
	else:
		await update.message.reply_text(message)


async def handle_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Обработчик нажатий на инлайн-кнопки пользователя"""
	query = update.callback_query
	await query.answer()

	callback_data = query.data

	if callback_data == "user_help":
		await help(update, context)
	elif callback_data == "user_stats":
		await stats(update, context)
	elif callback_data == "user_instructions":
		await instructions(update, context)
	elif callback_data == "user_config":
		await get_config(update, context)


def setup_base_handlers(application, admin_id: int):
	"""Настраивает базовые обработчики"""
	application.add_handler(CommandHandler("start", start))
	application.add_handler(CommandHandler("stats", stats))
	application.add_handler(CommandHandler("get_config", get_config))
	application.add_handler(CommandHandler("help", help))
	application.add_handler(CommandHandler("instructions", instructions))
	application.add_handler(CallbackQueryHandler(handle_user_callback, pattern="^user_"))
