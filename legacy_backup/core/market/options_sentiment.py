import logging
import aiohttp
import asyncio

logger = logging.getLogger("OmniTrade.OptionsSentiment")

class OptionsSentiment:
    def __init__(self):
        self.base_url = "https://www.deribit.com/api/v2/public"
        self.assets = ["BTC", "ETH"]

    async def fetch_options_data(self, asset):
        """Fetches option book summary."""
        url = f"{self.base_url}/get_book_summary_by_currency?currency={asset}&kind=option"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                logger.error(f"Deribit API Error: {e}")
        return None

    def calculate_metrics(self, data, asset):
        if not data or 'result' not in data:
            return

        total_put_oi = 0
        total_call_oi = 0
        avg_iv = 0
        count = 0

        for item in data['result']:
            instrument = item['instrument_name']
            oi = item.get('open_interest', 0)
            iv = item.get('mark_iv', 0)

            # Accumulate IV
            if iv > 0:
                avg_iv += iv
                count += 1

            # Distinguish Put vs Call
            if instrument.endswith('P'):
                total_put_oi += oi
            elif instrument.endswith('C'):
                total_call_oi += oi

        # Put/Call Ratio
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        avg_iv = avg_iv / count if count > 0 else 0

        # Generate Signals
        sentiment = "NEUTRAL"
        if pcr > 1.0:
            sentiment = "BEARISH (Fear/Hedging)"
        elif pcr < 0.6:
            sentiment = "BULLISH (Greed)"
        
        logger.info(f"OPTIONS [{asset}]: PCR={pcr:.2f} | IV={avg_iv:.2f}% | Sentiment={sentiment}")
        
        if avg_iv > 80: # High Volatility threshold
            logger.warning(f"⚠️ HIGH VOLATILITY ALERT on {asset}: IV > 80%. Prepare Grid Bots.")

    async def run_cycle(self):
        while True:
            for asset in self.assets:
                data = await self.fetch_options_data(asset)
                self.calculate_metrics(data, asset)
            await asyncio.sleep(3600) # Hourly check
