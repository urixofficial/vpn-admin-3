from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings

bot = Bot(settings.tg.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
