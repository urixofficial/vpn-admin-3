from aiogram import Router, F
from aiogram.types import Message

from core.logger import log
from telegram.handlers.user.keyboards import get_user_keyboard

router = Router()


@router.message(F.text == "Android")
async def android(message: Message):
	log.debug(
		"Пользователь {} ({}) запросил инструкцию для Android".format(message.from_user.full_name, message.from_user.id)
	)
	text = (
		"Настройка VPN на Android (AWG)\n"
		"----------------------------------------\n"
		"1. Установите клиент Amnezia VPN через Google Play: https://play.google.com/store/apps/details?id=org.amnezia.vpn.\n"
		"2. Скачайте файл конфигурации (.conf) через бота: /get_awg_config.\n"
		"3. В приложении AmneziaWG выберете пункт 'Из файла или архива' и укажите путь к файлу конфигурации.\n"
		"4. Нажмите 'Подключиться' и дождитесь установки соединения.\n"
		"----------------------------------------\n"
		"Если возникли проблемы, обратитесь к @urixofficial."
	)
	await message.answer(text, reply_markup=get_user_keyboard())


@router.message(F.text == "iPhone")
async def ios(message: Message):
	log.debug(
		"Пользователь {} ({}) запросил инструкцию для iOS".format(message.from_user.full_name, message.from_user.id)
	)
	text = (
		"Настройка VPN на iPhone (AWG)\n"
		"----------------------------------------\n"
		"1. Установите клиент AmneziaWG из AppStore: https://apps.apple.com/ru/app/amneziawg/id6478942365.\n"
		"2. Скачайте файл конфигурации (.conf) через бота: /get_awg_config.\n"
		"3. Нажмите на полученный файл конфигурации, чтобы он открылся на весь экран.\n"
		"4. Нажмите на кнопку 'Поделиться', пролистайте список приложений до конца и нажмите на кнопку 'Еще'.\n"
		"5. В появившемся списке выберите приложение AmneziaWG. Подключение добавится автоматически.\n"
		"6. Активируйте подключение с помощью тумблера.\n"
		"----------------------------------------\n"
		"Если возникли проблемы, обратитесь к @urixofficial."
	)
	await message.answer(text, reply_markup=get_user_keyboard())


@router.message(F.text == "Windows")
async def windows(message: Message):
	log.debug(
		"Пользователь {} ({}) запросил инструкцию для Windows".format(message.from_user.full_name, message.from_user.id)
	)
	text = (
		"Настройка VPN на Windows (AWG)\n"
		"----------------------------------------\n"
		"1. Скачайте клиент Amnezia VPN для Windows: https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.10.0/AmneziaVPN_4.8.10.0_windows_x64.exe\n"
		"2. Установите приложение, следуя инструкциям установщика.\n"
		"3. Скачайте файл конфигурации (.conf), полученный через команду /get_awg_config.\n"
		"4. В приложении Amnezia VPN выберете пункт 'Файл с настройками подключения' и укажите путь к файлу, полученному в предыдущем пункте.\n"
		"5. Нажмите 'Подключиться' и дождитесь установки соединения.\n"
		"----------------------------------------\n"
		"Если возникли проблемы, обратитесь к @urixofficial."
	)
	await message.answer(text, reply_markup=get_user_keyboard())


@router.message(F.text == "MacOS")
async def macos(message: Message):
	log.debug(
		"Пользователь {} ({}) запросил инструкцию для MacOS".format(message.from_user.full_name, message.from_user.id)
	)
	text = (
		"Настройка VPN на Windows (AWG)\n"
		"----------------------------------------\n"
		"1. Скачайте клиент Amnezia VPN для Mac: https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.10.0/AmneziaVPN_4.8.10.0_macos.zip\n"
		"2. Установите приложение, следуя инструкциям установщика.\n"
		"3. Скачайте файл конфигурации (.conf), полученный через команду /get_awg_config.\n"
		"4. В приложении Amnezia VPN выберете пункт 'Файл с настройками подключения' и укажите путь к файлу, полученному в предыдущем пункте.\n"
		"5. Нажмите 'Подключиться' и дождитесь установки соединения.\n"
		"----------------------------------------\n"
		"Если возникли проблемы, обратитесь к @urixofficial."
	)
	await message.answer(text, reply_markup=get_user_keyboard())
