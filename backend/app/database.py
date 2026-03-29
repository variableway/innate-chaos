"""Database configuration and session management for TimescaleDB."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Use async PostgreSQL driver (TimescaleDB is PostgreSQL)
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif database_url.startswith("sqlite"):
    # Fallback to SQLite for development
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    poolclass=NullPool if "sqlite" in database_url else None,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and hypertables."""
    async with engine.begin() as conn:
        # Create regular tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Create hypertables for time-series data (if using PostgreSQL/TimescaleDB)
        if "postgresql" in database_url and "sqlite" not in database_url:
            # Check if hypertables already exist
            result = await conn.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM timescaledb_information.hypertables
                    WHERE hypertable_name = 'prices'
                );
            """)
            prices_hypertable_exists = result.scalar()
            
            if not prices_hypertable_exists:
                logger.info("Creating TimescaleDB hypertables...")
                
                # Create hypertable for prices
                await conn.execute("""
                    SELECT create_hypertable('prices', 'time', 
                        if_not_exists => TRUE,
                        chunk_time_interval => INTERVAL '7 days'
                    );
                """)
                
                # Create hypertable for signals
                await conn.execute("""
                    SELECT create_hypertable('signals', 'time', 
                        if_not_exists => TRUE,
                        chunk_time_interval => INTERVAL '7 days'
                    );
                """)
                
                # Enable compression on prices
                await conn.execute("""
                    ALTER TABLE prices SET (
                        timescaledb.compress,
                        timescaledb.compress_segmentby = 'asset'
                    );
                """)
                
                # Add compression policy (compress after 7 days)
                await conn.execute("""
                    SELECT add_compression_policy('prices', INTERVAL '7 days', 
                        if_not_exists => TRUE
                    );
                """)
                
                # Add retention policy (drop after 90 days)
                await conn.execute("""
                    SELECT add_retention_policy('prices', INTERVAL '90 days',
                        if_not_exists => TRUE
                    );
                """)
                
                logger.info("TimescaleDB hypertables created successfully")
    
    logger.info("Database initialized")


async def create_continuous_aggregates():
    """Create continuous aggregates for common queries."""
    async with engine.begin() as conn:
        # Only for PostgreSQL/TimescaleDB
        if "postgresql" in database_url and "sqlite" not in database_url:
            logger.info("Creating continuous aggregates...")
            
            # Hourly price aggregates
            await conn.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS prices_hourly
                WITH (timescaledb.continuous) AS
                SELECT
                    time_bucket('1 hour', time) AS bucket,
                    asset,
                    first(price, time) AS open,
                    max(price) AS high,
                    min(price) AS low,
                    last(price, time) AS close,
                    avg(price) AS avg_price
                FROM prices
                GROUP BY bucket, asset;
            """)
            
            # Daily signal averages
            await conn.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS signals_daily
                WITH (timescaledb.continuous) AS
                SELECT
                    time_bucket('1 day', time) AS bucket,
                    asset,
                    avg(signal_value) AS avg_signal,
                    max(signal_value) AS max_signal,
                    min(signal_value) AS min_signal
                FROM signals
                GROUP BY bucket, asset;
            """)
            
            logger.info("Continuous aggregates created")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
