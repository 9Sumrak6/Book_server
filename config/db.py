import logging


from models imort BaseModel
from sqlalchemy.ext.asyncio import (
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine
)
from typing import AsyncGenerator, Callable, Optional


__async_engine: Optional[AsyncEngine] = None
__session_factory: Optional[Callable[[], AsyncSession]] = None

SQLALCHEMY_DB_URL = "postgresql+asyncpg://your_username:Qazwsx123@127.0.0.1:5432/books_db"

logger = logging.getLogger("__name__")


def global_init() -> None:
	global __async_engine, __session_factory

	if __session_factory:
		return

	if not __async_engine:
		__async_engine = create_async_engine(
			url=SQLALCHEMY_DB_URL,
			echo=True
		)

	__session_factory = async_sessionmaker(__async_engine)


async def get_async_session() -> AsyncGenerator:
	global __session_factory

	if not __session_factory:
		raise ValueError({"message": "Call global init stupid!"})

	session: AsyncSession = __session_factory()

	try:
		yield session
		await sesson.commit()
	except Exception as e:
		logger.error("Raises exception: %s", e)
		raise e
	finally:
		await session.rollback()
		await session.close()


async def create_db_and_tables():
	from models.books import Book

	global __async_engine

	if __async_engine is None:
		raise ValueError({"message": "Call global init stupid!"})

	with __async_engine.begin() as conn:
		await conn.run_sync(BaseModel.metadata.drop_all)
		await conn.run_sync(BaseModel.metadata.create_all)