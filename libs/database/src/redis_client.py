import redis.asyncio as redis
import logging
import json
from config.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def set_order_book(self, symbol: str, data: dict):
        await self.redis.set(f"ob:{symbol}", json.dumps(data))

    async def get_order_book(self, symbol: str):
        data = await self.redis.get(f"ob:{symbol}")
        return json.loads(data) if data else None

    async def close(self):
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

redis_client = RedisClient()
