from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.config import settings


engine = create_async_engine(url=settings.get_db_url, echo=settings.DB_ECHO)
session_factory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Контроль миграций БД теперь выполняется с помощью alembic
# async def init_db():
# 	log.debug("Инициализация базы данных: '{}'".format(settings.get_db_url))
# 	try:
# 		async with engine.begin() as conn:
# 			# await conn.run_sync(Base.metadata.drop_all)
# 			await conn.run_sync(Base.metadata.create_all)
# 		log.debug("OK")
# 	except Exception as e:
# 		log.error("Ошибка: {}".format(e))

# Декоратор для передачи подключений
def connection(method):
	async def wrapper(*args, **kwargs):
		async with session_factory() as new_session:
			try:
				# Явно не открываем транзакции, так как они уже есть в контексте
				return await method(*args, session=new_session, **kwargs)

			except Exception as e:
				await new_session.rollback()  # Откатываем сессию при ошибке
				raise e  # Поднимаем исключение дальше
			finally:
				await new_session.close()

	return wrapper