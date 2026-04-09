from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    from app.models import price, signal, regime  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Create hypertables (TimescaleDB extension)
        for table_name in ("prices", "signals", "regime_history"):
            try:
                await conn.execute(
                    text(
                        f"SELECT create_hypertable('{table_name}', 'time', "
                        f"if_not_exists => TRUE)"
                    )
                )
            except Exception:
                pass  # Not a TimescaleDB instance or already a hypertable
