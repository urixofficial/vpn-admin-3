import asyncio


from src.core.config import settings
from src.core.logger import log

from src.core.database import init_db
from src.user.dto import CreateUserDto, UpdateUserDto
from src.user.repo import create_user, get_user, get_users, update_user, delete_user
# from src.user.handlers import router as user_router
# from src.transaction.handlers import router as transaction_router



async def main():
	log.debug("Запуск {} {}".format(settings.APP_NAME, settings.APP_VERSION))

	await init_db()
	print(await create_user(CreateUserDto(id=12345678, name="Владимир Путин")))
	# print(await create_user(CreateUserDto(id=12345678, name="Владимир Путин")))
	print(await create_user(CreateUserDto(id=6395792835, name="Борис Ельцин")))
	print(await create_user(CreateUserDto(id=234798543, name="Иосиф Сталин")))
	print(await get_user(6395792835))
	print(await get_user(6))
	print(await get_users())
	await delete_user(6395792835)
	print(await get_users())
	# await delete_user(7654)
	print(await update_user(234798543, UpdateUserDto(name="Владимир Ленин")))

	# dp = Dispatcher()
	# dp.include_router(user_router)
	# dp.include_router(transaction_router)
	# dp.include_router(core_router)

	# bot = Bot(settings.TELEGRAM_TOKEN)
	# await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
