from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os
from app.models import Base

# Строка подключения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./backend.db")

# Создание движка базы данных
engine = create_async_engine(DATABASE_URL, future=True, echo=True)

# Создание фабрики сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


async def init_db():
    """
    Инициализация базы данных: создание таблиц.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """
    Получение сессии базы данных для маршрутов.
    """
    async with SessionLocal() as session:
        yield session
