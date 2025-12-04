import asyncpg
import logging
from config.config import settings

logger = logging.getLogger(__name__)

class TimescaleDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT
            )
            logger.info("Connected to TimescaleDB")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            # Enable TimescaleDB extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            
            # Market Data Table (Hypertable)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    time TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    price DOUBLE PRECISION,
                    volume DOUBLE PRECISION,
                    source TEXT
                );
            """)
            # Convert to hypertable
            await conn.execute("""
                SELECT create_hypertable('market_data', 'time', if_not_exists => TRUE);
            """)

            # Economic Indicators
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS economic_indicators (
                    time TIMESTAMPTZ NOT NULL,
                    indicator_name TEXT NOT NULL,
                    value DOUBLE PRECISION
                );
            """)
            
            # Trade History
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_history (
                    id SERIAL PRIMARY KEY,
                    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    price DOUBLE PRECISION,
                    quantity DOUBLE PRECISION,
                    strategy TEXT,
                    pnl DOUBLE PRECISION,
                    order_id TEXT,
                    status TEXT
                );
            """)
            logger.info("Database tables initialized")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("TimescaleDB connection closed")

db = TimescaleDB()
