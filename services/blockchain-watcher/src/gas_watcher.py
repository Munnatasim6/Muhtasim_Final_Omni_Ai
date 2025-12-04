import logging
import aiohttp
import asyncio

logger = logging.getLogger("OmniTrade.GasWatcher")

class GasWatcher:
    def __init__(self):
        self.api_url = "https://mempool.space/api/v1/fees/recommended"
        self.last_fast_fee = 0
        self.alert_threshold_pct = 50.0 # 50% spike

    async def check_gas(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        fast_fee = data.get("fastestFee", 0)
                        
                        if self.last_fast_fee > 0:
                            change = ((fast_fee - self.last_fast_fee) / self.last_fast_fee) * 100
                            
                            # Signal Logic
                            if change > self.alert_threshold_pct:
                                logger.warning(f"⛽ GAS SPIKE ALERT: Fees up {change:.1f}% in last cycle!")
                                logger.warning("-> Signal: HIGH NETWORK ACTIVITY (Possible NFT Mint/DEX Pump)")
                        
                        self.last_fast_fee = fast_fee
                        logger.info(f"Current Gas (Sat/vB): {fast_fee}")
                    else:
                        logger.warning("Failed to fetch gas data")
            except Exception as e:
                logger.error(f"Gas Watcher Error: {e}")

    async def run_cycle(self):
        """Polls every 5 minutes."""
        while True:
            await self.check_gas()
            await asyncio.sleep(300) # 5 minutes
