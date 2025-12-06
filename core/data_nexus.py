import asyncio
import logging
import json
import redis.asyncio as redis
import os
from core.cex_feed import CEXFeed
from on_chain import OnChainMonitor
from core.sentiment import SentimentEngine

logger = logging.getLogger(__name__)

class DataNexus:
    def __init__(self):
        self.cex = CEXFeed()
        # self.on_chain = OnChainMonitor() # Uncomment if used
        self.sentiment = SentimentEngine()
        
        # Redis Subscriber Config
        self.redis_host = os.getenv("REDIS_HOST", "localhost") # Default to localhost for local dev
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_sub = None

    async def start(self):
        logger.info("Initializing Universal Data Nexus...")
        
        # Start existing feeds
        await self.cex.start()
        await self.sentiment.start()
        
        # Start Redis Subscriber for Microservices
        asyncio.create_task(self.start_redis_listener())

    async def stop(self):
        logger.info("Stopping Data Nexus...")
        await self.cex.stop()
        await self.sentiment.stop()
        if self.redis_sub:
            await self.redis_sub.close()

    async def start_redis_listener(self):
        """
        Listens for signals from standalone scrapers via Redis Pub/Sub.
        """
        logger.info(f"🔌 Connecting to Redis Sub at {self.redis_host}:{self.redis_port}...")
        while True:
            try:
                r = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
                pubsub = r.pubsub()
                await pubsub.subscribe("market_sentiment")
                self.redis_sub = r
                
                logger.info("✅ Subscribed to 'market_sentiment' channel.")
                
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        await self.handle_sentiment_signal(data)
                        
            except Exception as e:
                logger.error(f"❌ Redis Listener Error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    async def handle_sentiment_signal(self, data: dict):
        """
        Process incoming signals from scrapers.
        """
        logger.info(f"📨 Signal Received from {data.get('platform')}: {data.get('text')} (Score: {data.get('sentiment_score')})")
        
        # Integrate with your logic here
        # Example: Update global sentiment state, trigger strategy, etc.
        # await self.sentiment.update_aggregate_score(data['sentiment_score'])
