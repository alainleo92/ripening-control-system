# app/db/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./data.db"

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True)

# Crear sesión async
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Inicializar la DB creando todas las tablas
async def init_db_():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
