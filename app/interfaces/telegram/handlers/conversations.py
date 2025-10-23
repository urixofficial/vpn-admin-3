# [file name]: conversations.py
from datetime import date, timedelta

from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, CommandHandler, filters, ConversationHandler, CallbackQueryHandler
)

from app.core.exceptions import UserAlreadyExistsException, NameIsNotUniqueException
from app.core.logger import log
from app.domains.users.models import UserCreate, UserUpdate, UserStatus
from app.domains.users.repository import user_repository
from .utils import get_message_func, check_for_admin, check_for_valid_id, check_for_valid_name
from ..keyboards import cancel_keyboard, confirm_keyboard

# Состояния для ConversationHandler
ASK_USER_ID, ASK_USER_NAME, CONFIRM_DELETION = range(3)

# Режимы операций
ADD_MODE = "add"
EDIT_MODE = "edit"
DELETE_MODE = "delete"


async def ask_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Общая функция для запроса ID пользователя"""
    log.debug(f"Запрос ID пользователя для режима: {context.user_data.get('mode')}")

    message_func = get_message_func(update)

    # Проверка на админа
    if not check_for_admin(update, context):
        await message_func("❌ У вас нет прав доступа.")
        return ConversationHandler.END

    mode = context.user_data.get("mode")
    action = {"add": "добавления", "edit": "редактирования", "delete": "удаления"}.get(mode, "операции")

    await message_func(
        f"Введите ID пользователя для {action}:",
        reply_markup=cancel_keyboard()
    )
    return ASK_USER_ID


async def ask_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Общая функция для запроса имени пользователя"""
    log.debug(f"Запрос имени пользователя для режима: {context.user_data.get('mode')}")

    mode = context.user_data.get("mode")
    action = {"add": "добавления", "edit": "редактирования"}.get(mode, "операции")

    await update.message.reply_text(
        f"Введите имя пользователя для {action}:",
        reply_markup=cancel_keyboard()
    )
    return ASK_USER_NAME


async def process_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод ID пользователя и определяет следующий шаг"""
    log.debug("Обработка введенного ID пользователя")

    user_id_text = update.message.text
    mode = context.user_data.get("mode")

    # Валидация ID
    if not check_for_valid_id(user_id_text):
        action = {"add": "добавления", "edit": "редактирования", "delete": "удаления"}.get(mode, "операции")
        await update.message.reply_text(
            f"❌ Некорректный ввод.\nВведите ID пользователя для {action}:",
            reply_markup=cancel_keyboard()
        )
        return ASK_USER_ID

    user_id = int(user_id_text)
    context.user_data["user_id"] = user_id
    user = user_repository.get_by_id(user_id)

    if mode == ADD_MODE:
        if user:
            # Пользователь существует, переключаемся в режим редактирования
            context.user_data["mode"] = EDIT_MODE
            await update.message.reply_text(
                f"Пользователь с ID {user_id} уже существует.\n"
                f"👤 Текущее имя: {user.username}\n"
                f"Введите новое имя пользователя:",
                reply_markup=cancel_keyboard()
            )
            return ASK_USER_NAME
        else:
            await ask_user_name(update, context)
            return ASK_USER_NAME
    elif mode == EDIT_MODE:
        if not user:
            await update.message.reply_text(
                f"❌ Пользователь с ID {user_id} не найден.\n"
                "Введите другой ID:",
                reply_markup=cancel_keyboard()
            )
            return ASK_USER_ID
        await update.message.reply_text(
            f"👤 Текущее имя: {user.username}\n"
            f"Введите новое имя пользователя:",
            reply_markup=cancel_keyboard()
        )
        return ASK_USER_NAME
    elif mode == DELETE_MODE:
        if not user:
            await update.message.reply_text(
                f"❌ Пользователь с ID {user_id} не найден.\n"
                "Введите другой ID:",
                reply_markup=cancel_keyboard()
            )
            return ASK_USER_ID
        await update.message.reply_text(
            f"❓ Вы уверены, что хотите удалить пользователя?\n"
            f"👤 Имя: {user.username}\n"
            f"🆔 ID: {user.id}",
            reply_markup=confirm_keyboard()
        )
        return CONFIRM_DELETION
    else:
        await update.message.reply_text("❌ Неизвестный режим операции.")
        return ConversationHandler.END


async def process_user_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает добавление, редактирование или удаление пользователя"""
    log.debug(f"Обработка операции: {context.user_data.get('mode')}")

    mode = context.user_data.get("mode")
    user_id = context.user_data.get("user_id")

    if mode in [ADD_MODE, EDIT_MODE]:
        new_user_name = update.message.text
        action = {"add": "добавления", "edit": "редактирования"}.get(mode, "операции")

        # Валидация имени
        if not check_for_valid_name(new_user_name):
            await update.message.reply_text(
                f"❌ Некорректный ввод. Имя должно быть от 3 до 30 символов.\n"
                f"Введите имя пользователя для {action}:",
                reply_markup=cancel_keyboard()
            )
            return ASK_USER_NAME

        try:
            if mode == ADD_MODE:
                # Добавление нового пользователя
                user_data = UserCreate(
                    telegram_id=user_id,
                    username=new_user_name,
                    billing_start_date=date.today(),
                    billing_end_date=date.today() + timedelta(days=30),
                    status=UserStatus.ACTIVE
                )
                new_user = user_repository.create(user_data)
                await update.message.reply_text(
                    f"✅ Пользователь успешно добавлен!\n\n"
                    f"👤 Имя: {new_user.username}\n"
                    f"🆔 ID: {new_user.id}\n"
                    f"📅 Начало: {new_user.billing_start_date}\n"
                    f"📅 Конец: {new_user.billing_end_date}\n"
                    f"🎯 Статус: {new_user.status.value}\n"
                )
                log.info(f"Пользователь успешно добавлен: {new_user.username} ({user_id})")
            elif mode == EDIT_MODE:
                # Редактирование пользователя
                user_data = UserUpdate(
	                username=new_user_name
                )
                user_repository.update(user_id, user_data)
                updated_user = user_repository.get_by_id(user_id)
                await update.message.reply_text(
                    f"✅ Пользователь успешно обновлен!\n\n"
                    f"👤 Имя: {updated_user.username}\n"
                    f"🆔 ID: {updated_user.id}\n"
                    f"📅 Начало: {updated_user.billing_start_date}\n"
                    f"📅 Конец: {updated_user.billing_end_date}\n"
                    f"🎯 Статус: {updated_user.status.value}\n"
                )
                log.info(f"Пользователь успешно обновлен: {updated_user.username} ({user_id})")

            return ConversationHandler.END

        except NameIsNotUniqueException:
            await update.message.reply_text(
                f"❌ Пользователь с именем '{new_user_name}' уже существует.\n"
                f"Введите другое имя для {action}:",
                reply_markup=cancel_keyboard()
            )
            return ASK_USER_NAME
        except Exception as e:
            log.error(f"Ошибка при {action} пользователя: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при {action} пользователя: {str(e)}\n"
                f"Введите ID пользователя для {action}:",
                reply_markup=cancel_keyboard()
            )
            return ASK_USER_ID

    elif mode == DELETE_MODE:
        query = update.callback_query
        await query.answer()
        callback_data = query.data

        if not user_id:
            await query.edit_message_text("❌ Ошибка: данные сессии утеряны.")
            return ConversationHandler.END

        user = user_repository.get_by_id(user_id)

        if callback_data == "confirm_yes":
            if user_repository.delete(user.id):
                await query.edit_message_text(
                    f"✅ Пользователь {user.username} успешно удален."
                )
                log.info(f"Пользователь успешно удален: {user.username} ({user.id})")
            else:
                await query.edit_message_text(
                    f"❌ Не удалось удалить пользователя {user.username}."
                )
                log.error(f"Не удалось удалить пользователя: {user.username} ({user.id})")
        elif callback_data == "confirm_no":
            await query.edit_message_text("❌ Удаление отменено.")

        return ConversationHandler.END

    else:
        await update.message.reply_text("❌ Неизвестный режим операции.")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет текущую операцию"""
    message_func = get_message_func(update)
    await message_func("❌ Операция отменена")
    return ConversationHandler.END


def setup_conversation_handlers(application, admin_id: int):
    """Настраивает обработчики диалогов"""
    admin_filter = filters.User(admin_id)

    user_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                lambda update, context: context.user_data.update({"mode": ADD_MODE}) or ask_user_id(update, context),
                pattern="^users_add$"
            ),
            CallbackQueryHandler(
                lambda update, context: context.user_data.update({"mode": EDIT_MODE}) or ask_user_id(update, context),
                pattern="^users_edit$"
            ),
            CallbackQueryHandler(
                lambda update, context: context.user_data.update({"mode": DELETE_MODE}) or ask_user_id(update, context),
                pattern="^users_delete$"
            )
        ],
        states={
            ASK_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_user_id)],
            ASK_USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_user_operation)],
            CONFIRM_DELETION: [CallbackQueryHandler(process_user_operation, pattern="^confirm_")],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )

    application.add_handler(user_handler)