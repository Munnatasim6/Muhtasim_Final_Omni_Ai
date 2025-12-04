"""
Google Trends FOMO/FUD Detector ("Retail Sentiment")

This module monitors Google Trends for specific keywords to gauge retail sentiment.
It uses the unofficial `pytrends` API (Free) to detect "FOMO" (Fear Of Missing Out)
and "FUD" (Fear, Uncertainty, Doubt).

Dependencies:
    - pytrends
    - pandas
"""

import logging
import time
from typing import Dict, List
import pandas as pd
from pytrends.request import TrendReq

# Configure logging
logger = logging.getLogger(__name__)

class TrendsEngine:
    """
    Monitors Google Trends to calculate Retail Sentiment Score.
    """

    def __init__(self, hl='en-US', tz=360):
        """
        Initialize the TrendsEngine.

        Args:
            hl (str): Host language (default: 'en-US').
            tz (int): Timezone offset (default: 360 for US CST).
        """
        # Connect to Google
        # Retries and backoff are handled internally by pytrends to some extent,
        # but we should be careful about rate limits.
        self.pytrends = TrendReq(hl=hl, tz=tz, timeout=(10,25), retries=2, backoff_factor=0.1)
        
        self.fomo_keywords = ["Buy Crypto", "Bitcoin Price", "Altcoin Gem"]
        self.fud_keywords = ["Crypto Crash", "Bitcoin Scam", "Sell Crypto"]

    def fetch_trends(self, keywords: List[str]) -> pd.DataFrame:
        """
        Fetches trend data for a list of keywords.

        Args:
            keywords (List[str]): List of keywords to search (max 5 per request).

        Returns:
            pd.DataFrame: DataFrame containing interest over time.
        """
        try:
            # pytrends allows max 5 keywords per request
            kw_list = keywords[:5]
            logger.info(f"Fetching trends for: {kw_list}")
            
            self.pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
            data = self.pytrends.interest_over_time()
            
            if data.empty:
                logger.warning(f"No trend data found for {kw_list}")
                return pd.DataFrame()
                
            return data
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return pd.DataFrame()

    def analyze_sentiment(self) -> Dict[str, float]:
        """
        Analyzes FOMO and FUD keywords to calculate a sentiment score.

        Returns:
            Dict[str, float]: Dictionary with 'score' (0-100) and 'signal'.
                              Score > 75: Extreme Greed (Sell Risk)
                              Score < 25: Extreme Fear (Buy Opportunity)
        """
        # Fetch FOMO data
        fomo_df = self.fetch_trends(self.fomo_keywords)
        time.sleep(2) # Respect rate limits
        
        # Fetch FUD data
        fud_df = self.fetch_trends(self.fud_keywords)
        
        fomo_score = 0
        fud_score = 0
        
        if not fomo_df.empty:
            # Average of the last data point for all FOMO keywords
            fomo_score = fomo_df.iloc[-1][self.fomo_keywords].mean()
            
        if not fud_df.empty:
            # Average of the last data point for all FUD keywords
            fud_score = fud_df.iloc[-1][self.fud_keywords].mean()
            
        # Calculate Net Sentiment (0 to 100)
        # Logic: High FOMO increases score, High FUD decreases score.
        # We normalize this to a 0-100 scale where 50 is neutral.
        
        # Simple formula: 50 + (FOMO - FUD) / 2
        # If FOMO=100, FUD=0 -> Score = 100 (Max Greed)
        # If FOMO=0, FUD=100 -> Score = 0 (Max Fear)
        
        sentiment_score = 50 + (fomo_score - fud_score) / 2
        sentiment_score = max(0, min(100, sentiment_score)) # Clamp between 0 and 100
        
        signal = "NEUTRAL"
        if sentiment_score > 75:
            signal = "EXTREME GREED (SELL)"
        elif sentiment_score < 25:
            signal = "EXTREME FEAR (BUY)"
        elif sentiment_score > 60:
            signal = "GREED"
        elif sentiment_score < 40:
            signal = "FEAR"
            
        logger.info(f"Retail Sentiment Analysis: Score={sentiment_score:.2f} ({signal}) [FOMO={fomo_score:.1f}, FUD={fud_score:.1f}]")
        
        return {
            "score": sentiment_score,
            "fomo_index": fomo_score,
            "fud_index": fud_score,
            "signal": signal
        }

if __name__ == "__main__":
    engine = TrendsEngine()
    result = engine.analyze_sentiment()
    print(result)
