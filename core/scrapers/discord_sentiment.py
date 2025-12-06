import logging
import discord
import asyncio
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger("OmniTrade.DiscordSent")

class DiscordSentiment(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        super().__init__(intents=intents)
        
        self.message_buffer = deque(maxlen=1000) # Store timestamps of last 1000 msgs
        self.fomo_keywords = ["moon", "lfg", "pump", "buy", "100x"]
        
        # NOTE: Requires Bot Token
        self.token = "YOUR_DISCORD_BOT_TOKEN"

    async def on_ready(self):
        logger.info(f'Discord Bot Connected as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        self.message_buffer.append(datetime.now())
        self.analyze_velocity(message.content)

    def analyze_velocity(self, content):
        """
        Calculates Messages Per Minute (MPM).
        High MPM + FOMO keywords = Retail Euphoria (Sell Signal).
        """
        now = datetime.now()
        one_min_ago = now - timedelta(minutes=1)
        
        # Count messages in last minute
        recent_msgs = [t for t in self.message_buffer if t > one_min_ago]
        velocity = len(recent_msgs)
        
        # Keyword check
        keyword_hit = any(k in content.lower() for k in self.fomo_keywords)
        
        if velocity > 50 and keyword_hit:
            logger.warning(f"🦍 RETAIL FOMO ALERT: Velocity {velocity} MPM! 'Moon boys' are active.")
            logger.warning("-> Potential LOCAL TOP. Recommendation: Take Profit.")

    async def start_service(self):
        if self.token == "YOUR_DISCORD_BOT_TOKEN":
            logger.warning("Discord Token not set. Skipping.")
            return
        await self.start(self.token)
