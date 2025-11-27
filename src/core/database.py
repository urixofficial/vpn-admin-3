from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings


engine = create_async_engine(url=settings.db_url, echo=settings.DB_ECHO)
session_factory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


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
