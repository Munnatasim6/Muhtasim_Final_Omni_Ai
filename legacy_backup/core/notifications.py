import logging
from telegram import Bot
from config.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.bot = None
        if settings.TELEGRAM_BOT_TOKEN:
            self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async def send_alert(self, message: str):
        if not self.bot or not settings.TELEGRAM_CHAT_ID:
            logger.warning("Telegram not configured. Skipping alert.")
            return

        try:
            await self.bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=f"🚨 {message}")
            logger.info(f"Sent Telegram alert: {message}")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

notifier = NotificationService()
