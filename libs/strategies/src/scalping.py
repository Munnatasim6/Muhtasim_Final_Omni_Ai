from strategies.base_strategy import BaseStrategy
from core.brain import Brain
from core.feature_engineering import FeatureEngineer
from config.config import settings
import pandas as pd
import logging
import redis
import json

logger = logging.getLogger(__name__)

class ScalpingStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Scalping Alpha")
        self.brain = Brain()
        self.fe = FeatureEngineer()
        self.data_buffer = []
        
        # Redis Connection for On-Chain Data
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def on_tick(self, market_data):
        # Accumulate data
        self.data_buffer.append(market_data)
        if len(self.data_buffer) > 50:
            self.data_buffer.pop(0)
        
        # Convert to DataFrame
        df = pd.DataFrame(self.data_buffer)
        
        # Feature Engineering
        features = self.fe.calculate_features(df)
        
        if not features.empty:
            signal = await self.generate_signal(features)
            return signal
        return 0

    async def generate_signal(self, features):
        # 1. Fetch Whale Sentiment from Redis
        whale_sentiment_score = 0
        if self.redis_client:
            try:
                data = self.redis_client.get("whale_sentiment")
                if data:
                    # Assuming data is JSON or float string
                    # If it's a simple float string:
                    whale_sentiment_score = float(data)
            except Exception as e:
                logger.warning(f"Could not read whale sentiment: {e}")

        # 2. Use ML Brain
        # Pass on-chain data to brain if needed, or just use it to adjust the output
        action = self.brain.predict(features)
        
        # 3. Adjust Logic based on Whale Sentiment
        # If Whale Sentiment is strongly positive, override HOLD/SELL to BUY or confirm BUY
        # Thresholds: > 0.5 (Bullish), < -0.5 (Bearish)
        
        original_action = action
        
        if whale_sentiment_score > 0.5:
            if action == 0: # If Hold, upgrade to Buy
                action = 1
                logger.info(f"Whale Sentiment ({whale_sentiment_score}) upgraded HOLD to BUY")
            elif action == 2: # If Sell, maybe Hold instead (avoid fighting whales)
                action = 0
                logger.info(f"Whale Sentiment ({whale_sentiment_score}) suppressed SELL to HOLD")
                
        elif whale_sentiment_score < -0.5:
            if action == 1: # If Buy, suppress to Hold
                action = 0
                logger.info(f"Whale Sentiment ({whale_sentiment_score}) suppressed BUY to HOLD")
        
        # XAI Logging
        explanation = self.brain.explain_decision(features)
        explanation['whale_sentiment'] = whale_sentiment_score
        
        logger.info(f"Strategy Decision: {action} (Orig: {original_action}) | Reason: {explanation['reason']} | Whale: {whale_sentiment_score}")
        
        return action
