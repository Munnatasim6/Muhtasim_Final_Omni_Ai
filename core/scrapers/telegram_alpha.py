import logging
from telethon import TelegramClient, events
import asyncio

logger = logging.getLogger("OmniTrade.TelegramAlpha")

class TelegramAlpha:
    def __init__(self):
        # NOTE: User must provide these from https://my.telegram.org
        self.api_id = 12345678  # Placeholder
        self.api_hash = 'YOUR_API_HASH'
        self.session_name = 'omni_session'
        
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        # Target Channels (Whale Alert, News)
        self.target_channels = ['whale_alert_io', 'db_newswire'] 
        self.keywords = ["Listed on Binance", "Partnership", "Moved 10,000 BTC", "SEC Approval"]

    async def start(self):
        """Starts the Telegram listener."""
        try:
            # Only start if credentials are configured
            if self.api_id == 12345678: 
                logger.warning("Telegram API ID not set. Skipping module.")
                return

            await self.client.start()
            logger.info("Telegram Alpha Scout Listening...")

            @self.client.on(events.NewMessage(chats=self.target_channels))
            async def handler(event):
                await self.process_message(event.message.message)
                
            await self.client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Telegram connection failed: {e}")

    async def process_message(self, text):
        """
        Filters text for alpha keywords.
        """
        for key in self.keywords:
            if key.lower() in text.lower():
                logger.info(f"🚨 TELEGRAM ALPHA DETECTED: {key} found in message!")
                logger.info(f"Message: {text[:50]}...")
                # Immediate signal to Swarm
                self.broadcast_signal(key)
                break

    def broadcast_signal(self, trigger):
        # Logic to notify Swarm Manager
        logger.info(f"-> Injecting 'High Urgency' signal for {trigger} to Neural Swarm.")
