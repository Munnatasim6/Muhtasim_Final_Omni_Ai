import asyncio
import logging
import os
import json
import random
from typing import List
import redis.asyncio as redis # Redis client

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SocialScraper")

class SocialScraper:
    """
    Real-Time Social Media Scraper (Standalone Microservice).
    Publishes sentiment/signals to Redis Pub/Sub.
    """
    def __init__(self):
        # 1. Dynamic Keyword Loading (Sharding Support)
        # Default to BTC/ETH if env var not set
        kw_env = os.getenv("TARGET_KEYWORDS", "$BTC,$ETH,Bitcoin,Ethereum")
        self.keywords = kw_env.split(",")
        
        self.running = False
        self.redis_client = None
        self.pubsub_channel = "market_sentiment"
        
        # Redis Connection Params
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))

    async def connect_redis(self):
        """Connects to Redis with retry logic."""
        while True:
            try:
                self.redis_client = redis.Redis(
                    host=self.redis_host, 
                    port=self.redis_port, 
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")
                break
            except Exception as e:
                logger.error(f"❌ Redis Connection Failed: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

    async def start_stream(self):
        """Start the scraping loop."""
        await self.connect_redis()
        self.running = True
        logger.info(f"🚀 Starting Social Scraper for keywords: {self.keywords}")
        
        # Start the mock stream
        await self._mock_stream()

    async def _mock_stream(self):
        """
        Simulate incoming social media posts and publish to Redis.
        """
        sample_texts = [
            "Bitcoin looking bullish today! $BTC",
            "Market crash incoming? $ETH dropping.",
            "Huge volume on $BTC, breakout imminent.",
            "Just bought the dip! #HODL",
            "Regulatory news might affect crypto prices."
        ]

        while self.running:
            try:
                await asyncio.sleep(5) # Simulate delay
                
                # Simulate finding a post containing one of our target keywords
                text = random.choice(sample_texts)
                platform = random.choice(["Twitter", "Telegram"])
                
                # Check if text is relevant to THIS container's keywords
                if any(k in text for k in self.keywords):
                    logger.info(f"[{platform}] Match Found: {text}")
                    
                    # Analyze (Simulated local processing)
                    sentiment_score = self.process_text(text)
                    
                    # Prepare Payload
                    payload = {
                        "platform": platform,
                        "text": text,
                        "keywords": self.keywords,
                        "sentiment_score": sentiment_score,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    
                    # Publish to Redis
                    if self.redis_client:
                        await self.redis_client.publish(self.pubsub_channel, json.dumps(payload))
                        logger.info(f"📡 Published to '{self.pubsub_channel}'")
            
            except Exception as e:
                logger.error(f"Error in stream loop: {e}")
                await asyncio.sleep(5) # Prevent crash loops

    def process_text(self, text: str) -> float:
        """
        Process raw text (Mock Sentiment Analysis).
        Returns a score between -1.0 and 1.0
        """
        # In a real scenario, integrate SentimentEngine here
        if "bullish" in text.lower() or "breakout" in text.lower():
            return 0.8
        elif "crash" in text.lower() or "dropping" in text.lower():
            return -0.8
        return 0.0

if __name__ == "__main__":
    # Standalone Entry Point
    scraper = SocialScraper()
    try:
        asyncio.run(scraper.start_stream())
    except KeyboardInterrupt:
        logger.info("Stopping Scraper...")
