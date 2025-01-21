from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.pool import AsyncAdaptedQueuePool
import config


class PostgresPool:
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(
            config.DB_HOST,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5,
            max_overflow=10
        )

        from sqlalchemy.ext.asyncio import async_sessionmaker

        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        self._session = None

    async def __aenter__(self) -> AsyncSession:
        self._session = self.async_session()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_type:
                await self._session.rollback()
            await self._session.close()
            self._session = None

    async def cleanup(self):
        await self.engine.dispose()