import asyncio
import logging
from db.timescale import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_RESET")

async def reset_database():
    logger.info("Starting database reset...")
    
    try:
        await db.connect()
        
        async with db.pool.acquire() as conn:
            logger.info("Dropping tables...")
            await conn.execute("DROP TABLE IF EXISTS market_data CASCADE;")
            await conn.execute("DROP TABLE IF EXISTS economic_indicators CASCADE;")
            await conn.execute("DROP TABLE IF EXISTS trade_history CASCADE;")
            logger.info("Tables dropped.")
            
        logger.info("Recreating tables...")
        await db.create_tables()
        logger.info("Database reset complete!")
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(reset_database())
