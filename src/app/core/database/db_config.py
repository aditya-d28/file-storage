from typing import AsyncGenerator

from app.core.config import settings
from shared.logging.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

EntityBase = declarative_base()


class Database:
    def __init__(self):
        """
        Initializes the database connection by creating an asynchronous engine and a session factory.

        Logs the initialization process, sets up the async engine with the provided database URL and connection pool settings,
        and configures a sessionmaker for creating asynchronous sessions.

        Attributes:
            engine (AsyncEngine): The SQLAlchemy asynchronous engine for database connections.
            session_local (sessionmaker): Factory for creating asynchronous database sessions.
        """

        logger.info("Initializing database connection.")
        self.engine = create_async_engine(
            str(settings.DB_URL),
            pool_size=int(settings.DB_POOL_SIZE),
            max_overflow=int(settings.DB_MAX_OVERFLOW),
        )
        self.session_local = sessionmaker(
            bind=self.engine, class_=AsyncSession, autocommit=False, autoflush=True
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session as an async generator.
        This method is intended to be used as a FastAPI dependency.
        """
        async with self.session_local() as session:
            try:
                yield session
            finally:
                await session.close()


db = Database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator that provides a database session.

    Yields:
        AsyncSession: An instance of the asynchronous database session.

    Ensures:
        The session is properly closed after use, even if an exception occurs.
    """
    async with db.session_local() as session:
        try:
            yield session
        finally:
            await session.close()
