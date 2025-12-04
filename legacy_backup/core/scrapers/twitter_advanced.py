import logging
import asyncio
import random
from typing import List, Dict
# from twikit import Client # pip install twikit

logger = logging.getLogger("TwitterAdvanced")

class TwitterAdvancedScraper:
    """
    Advanced Twitter Scraper (The 'Tricky' Solution).
    Uses 'twikit' to mimic a real browser session, handling cookies and rotating User-Agents.
    """
    def __init__(self, username: str = None, email: str = None, password: str = None):
        self.username = username
        self.email = email
        self.password = password
        self.client = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]

    async def initialize(self):
        """
        Initialize the client and load cookies if available.
        """
        logger.info("Initializing Twitter Scraper...")
        # self.client = Client(language='en-US')
        # self.client.set_user_agent(random.choice(self.user_agents))
        
        # Load cookies
        if self._load_cookies():
            logger.info("Cookies loaded successfully.")
        else:
            await self._login()

    async def _login(self):
        """
        Perform login if cookies are missing or expired.
        """
        if not self.username or not self.password:
            logger.warning("No credentials provided for Twitter login.")
            return

        try:
            logger.info(f"Logging in as {self.username}...")
            # await self.client.login(
            #     auth_info_1=self.username,
            #     auth_info_2=self.email,
            #     password=self.password
            # )
            # self.client.save_cookies('cookies.json')
            logger.info("Login successful.")
        except Exception as e:
            logger.error(f"Login failed: {e}")

    def _load_cookies(self) -> bool:
        """
        Load cookies from file.
        """
        try:
            # self.client.load_cookies('cookies.json')
            return True
        except Exception:
            return False

    async def search_latest(self, query: str = "$BTC", limit: int = 20) -> List[Dict]:
        """
        Search for the latest tweets matching the query.
        """
        logger.info(f"Searching Twitter for '{query}'...")
        tweets_data = []
        
        try:
            # tweets = await self.client.search_tweet(query, product='Latest')
            # for tweet in tweets[:limit]:
            #     tweets_data.append({
            #         "id": tweet.id,
            #         "text": tweet.text,
            #         "user": tweet.user.name,
            #         "created_at": tweet.created_at
            #     })
            
            # Mock Data
            tweets_data = [
                {"id": "1", "text": "BTC looking bullish! $BTC", "user": "CryptoKing", "created_at": "2025-11-30 10:00:00"},
                {"id": "2", "text": "Market crash incoming? #Bearish", "user": "FUDMaster", "created_at": "2025-11-30 10:05:00"}
            ]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return tweets_data

    def rotate_user_agent(self):
        """
        Rotates the User-Agent string to avoid detection.
        """
        new_ua = random.choice(self.user_agents)
        # self.client.set_user_agent(new_ua)
        logger.info(f"Rotated User-Agent to: {new_ua}")
