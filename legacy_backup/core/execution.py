import asyncio
import logging
import math
from typing import Optional, Dict, List
import time

try:
    import rust_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    print("WARNING: rust_core not found. Running in pure Python mode. Run 'maturin develop' in rust_core/ to compile.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionEngine:
    """
    Smart Execution Engine for HFT.
    Handles order placement, risk management, and algorithmic execution (TWAP/VWAP).
    """

    def __init__(self, exchange_client):
        """
        Initialize the ExecutionEngine.

        Args:
            exchange_client: An initialized CCXT exchange instance or compatible wrapper.
        """
        self.exchange = exchange_client
        self.active_orders = {}
        self.trailing_stops = {}  # {symbol: {'entry_price': float, 'high_water_mark': float, 'trailing_pct': float}}

    async def place_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """
        Place a Limit Order to act as a Maker and save fees.

        Args:
            symbol (str): Trading pair (e.g., 'BTC/USDT').
            side (str): 'buy' or 'sell'.
            amount (float): Quantity to trade.
            price (float): Limit price.

        Returns:
            Optional[Dict]: Order response from exchange or None on failure.
        """
        try:
            # Rust-based Pre-Trade Validation (Nanosecond latency)
            if RUST_AVAILABLE:
                # Mock balance check for now, in prod fetch from account
                is_valid, msg = rust_core.validate_order(price, amount, 0.0001, 10.0, 999999.0)
                if not is_valid:
                    logger.error(f"Rust Validation Failed: {msg}")
                    return None

            logger.info(f"Placing LIMIT {side.upper()} order for {symbol}: {amount} @ {price}")
            order = await self.exchange.create_order(symbol, 'limit', side, amount, price)
            self.active_orders[order['id']] = order
            return order
        except Exception as e:
            logger.error(f"Failed to place limit order for {symbol}: {e}")
            return None

    async def execute_twap(self, symbol: str, side: str, total_amount: float, duration_minutes: int, num_splits: int):
        """
        Execute a Time-Weighted Average Price (TWAP) strategy.
        Splits a large order into smaller child orders executed over a specified duration.

        Args:
            symbol (str): Trading pair.
            side (str): 'buy' or 'sell'.
            total_amount (float): Total quantity to trade.
            duration_minutes (int): Total duration for execution in minutes.
            num_splits (int): Number of child orders.
        """
        logger.info(f"Starting TWAP execution for {symbol}: {total_amount} {side} over {duration_minutes} mins")
        
        amount_per_order = total_amount / num_splits
        delay_seconds = (duration_minutes * 60) / num_splits

        for i in range(num_splits):
            try:
                # Fetch current best bid/ask to place a competitive limit order
                ticker = await self.exchange.fetch_ticker(symbol)
                current_price = ticker['bid'] if side == 'buy' else ticker['ask']
                
                # Place child order
                await self.place_limit_order(symbol, side, amount_per_order, current_price)
                
                logger.info(f"TWAP step {i+1}/{num_splits} completed. Waiting {delay_seconds}s...")
                if i < num_splits - 1:
                    await asyncio.sleep(delay_seconds)
            except Exception as e:
                logger.error(f"TWAP execution error at step {i+1}: {e}")
                # Continue to next step despite error to attempt completion
                continue
        
        logger.info(f"TWAP execution for {symbol} completed.")

    async def execute_vwap(self, symbol: str, side: str, total_amount: float, volume_profile: List[float]):
        """
        Execute a Volume-Weighted Average Price (VWAP) strategy.
        Splits orders based on historical volume profile.
        
        Args:
            volume_profile (List[float]): List of percentages (0.0 to 1.0) summing to 1.0, 
                                          representing volume distribution over time intervals.
        """
        # Simplified implementation assuming equal time intervals matching the profile length
        logger.info(f"Starting VWAP execution for {symbol}")
        
        # This is a placeholder for the complex logic of matching real-time volume
        # In a real HFT system, this would subscribe to trade stream and execute based on volume buckets
        pass

    def set_trailing_stop(self, symbol: str, entry_price: float, trailing_percent: float):
        """
        Initialize a trailing stop for a position.

        Args:
            symbol (str): Trading pair.
            entry_price (float): The price at which the position was entered.
            trailing_percent (float): The percentage distance for the stop (e.g., 0.02 for 2%).
        """
        self.trailing_stops[symbol] = {
            'entry_price': entry_price,
            'high_water_mark': entry_price, # Initialize with entry price
            'trailing_pct': trailing_percent,
            'active': True
        }
        logger.info(f"Trailing stop set for {symbol} at {trailing_percent*100}%")

    async def check_trailing_stop(self, symbol: str, current_price: float) -> bool:
        """
        Check if the trailing stop has been triggered.
        Updates the high-water mark if price moves in favor.

        Args:
            symbol (str): Trading pair.
            current_price (float): Current market price.

        Returns:
            bool: True if stop triggered (should sell), False otherwise.
        """
        stop_data = self.trailing_stops.get(symbol)
        if not stop_data or not stop_data['active']:
            return False

        # Update high water mark (assuming long position for simplicity)
        if current_price > stop_data['high_water_mark']:
            stop_data['high_water_mark'] = current_price
            # logger.debug(f"New high water mark for {symbol}: {current_price}")

        # Calculate dynamic stop price
        stop_price = stop_data['high_water_mark'] * (1 - stop_data['trailing_pct'])
        
        if current_price <= stop_price:
            logger.warning(f"Trailing Stop Triggered for {symbol}! Price: {current_price}, Stop: {stop_price}")
            stop_data['active'] = False # Deactivate after trigger
            return True
            
        return False

    async def cancel_all_orders(self, symbol: Optional[str] = None):
        """
        Cancel all open orders. Used for emergency stop or cleanup.
        """
        try:
            if symbol:
                await self.exchange.cancel_all_orders(symbol)
            else:
                # Note: Some exchanges don't support cancel_all without symbol
                # This would need to iterate over all active symbols in a real scenario
                logger.warning("Cancel all orders without symbol might not be supported by all exchanges.")
        except Exception as e:
            logger.error(f"Failed to cancel orders: {e}")
