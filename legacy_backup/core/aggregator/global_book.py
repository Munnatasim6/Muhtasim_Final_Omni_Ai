"""
Global Liquidity Heatmap Module ("Cross-Exchange Aggregation")

This module aggregates L2 Order Books from multiple major exchanges to visualize
the "True Global Support/Resistance" levels and detect spoofing.

Dependencies:
    - ccxt
    - numpy
    - pandas
    - asyncio
"""

import asyncio
import logging
from typing import Dict, List, Tuple
import ccxt.async_support as ccxt
import numpy as np
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

class GlobalLiquidityWall:
    """
    Aggregates order books from multiple exchanges to find global liquidity walls.
    """

    def __init__(self, symbol: str = "BTC/USDT"):
        self.symbol = symbol
        self.exchanges = [
            ccxt.binance(),
            ccxt.bybit(),
            ccxt.kraken(),
            ccxt.kucoin(),
            ccxt.okx()
        ]
        self.depth_limit = 100  # Number of levels to fetch per exchange

    async def fetch_order_books(self) -> Dict[str, Dict]:
        """
        Fetches L2 order books from all configured exchanges simultaneously.

        Returns:
            Dict[str, Dict]: Dictionary mapping exchange name to its order book.
        """
        tasks = []
        for exchange in self.exchanges:
            tasks.append(self._fetch_single_book(exchange))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        books = {}
        for res in results:
            if isinstance(res, dict) and "exchange" in res:
                books[res["exchange"]] = res["book"]
        
        return books

    async def _fetch_single_book(self, exchange) -> Dict:
        """Helper to fetch a single order book safely."""
        try:
            # Check if exchange supports the symbol (simplified check)
            # In production, load_markets() should be called once at startup
            # await exchange.load_markets() 
            
            book = await exchange.fetch_order_book(self.symbol, limit=self.depth_limit)
            return {"exchange": exchange.id, "book": book}
        except Exception as e:
            logger.warning(f"Failed to fetch {self.symbol} from {exchange.id}: {e}")
            return {"error": str(e)}
        finally:
            await exchange.close()

    def aggregate_books(self, books: Dict[str, Dict]) -> pd.DataFrame:
        """
        Normalizes and aggregates bids and asks into a single global book.

        Args:
            books (Dict[str, Dict]): The fetched order books.

        Returns:
            pd.DataFrame: Aggregated book with columns ['price', 'volume', 'side', 'exchanges']
        """
        all_orders = []

        for ex_name, book in books.items():
            for bid in book['bids']:
                all_orders.append({'price': bid[0], 'volume': bid[1], 'side': 'bid', 'exchange': ex_name})
            for ask in book['asks']:
                all_orders.append({'price': ask[0], 'volume': ask[1], 'side': 'ask', 'exchange': ex_name})

        df = pd.DataFrame(all_orders)
        
        if df.empty:
            return df

        # Group by price bucket (e.g., round to nearest $1 for BTC)
        # For simplicity, we round to 0 decimals for BTC
        df['price_bucket'] = df['price'].round(0)
        
        aggregated = df.groupby(['side', 'price_bucket']).agg({
            'volume': 'sum',
            'exchange': lambda x: list(set(x)) # List of exchanges contributing to this level
        }).reset_index()

        return aggregated

    def detect_spoofing(self, aggregated_df: pd.DataFrame) -> List[Dict]:
        """
        Detects potential spoofing where a large wall exists on only 1 exchange.

        Args:
            aggregated_df (pd.DataFrame): The aggregated global book.

        Returns:
            List[Dict]: List of spoofing alerts.
        """
        alerts = []
        
        # Define "Large Wall" threshold (e.g., > 10 BTC)
        # This should be dynamic based on average volume
        VOLUME_THRESHOLD = 10.0 

        for _, row in aggregated_df.iterrows():
            if row['volume'] > VOLUME_THRESHOLD:
                # Check if it's isolated to a single exchange
                if len(row['exchange']) == 1:
                    alerts.append({
                        "type": "SPOOFING_SUSPICION",
                        "side": row['side'],
                        "price": row['price_bucket'],
                        "volume": row['volume'],
                        "exchange": row['exchange'][0]
                    })
        
        return alerts

    async def run_analysis(self):
        """
        Main execution method.
        """
        logger.info(f"Fetching Global Liquidity for {self.symbol}...")
        books = await self.fetch_order_books()
        
        if not books:
            logger.error("No order books fetched.")
            return

        agg_df = self.aggregate_books(books)
        
        # Find top support/resistance
        bids = agg_df[agg_df['side'] == 'bid'].sort_values('volume', ascending=False).head(3)
        asks = agg_df[agg_df['side'] == 'ask'].sort_values('volume', ascending=False).head(3)
        
        logger.info("\n--- GLOBAL LIQUIDITY WALLS ---")
        logger.info(f"Top Bids (Support):\n{bids}")
        logger.info(f"Top Asks (Resistance):\n{asks}")

        spoofing = self.detect_spoofing(agg_df)
        if spoofing:
            logger.warning(f"SPOOFING DETECTED: {len(spoofing)} instances")
            for s in spoofing:
                logger.warning(str(s))

if __name__ == "__main__":
    # Windows selector event loop policy fix for Python 3.8+
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    wall = GlobalLiquidityWall()
    asyncio.run(wall.run_analysis())
