from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def on_tick(self, market_data):
        """
        Called on every new market tick.
        """
        pass

    @abstractmethod
    async def generate_signal(self, features):
        """
        Returns signal: 0 (Hold), 1 (Buy), 2 (Sell)
        """
        pass
