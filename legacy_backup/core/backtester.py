import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Event Definitions ---
@dataclass
class Event:
    timestamp: datetime.datetime
    type: str

@dataclass
class MarketEvent(Event):
    symbol: str
    price: float
    volume: float
    type: str = 'MARKET'

@dataclass
class SignalEvent(Event):
    symbol: str
    side: str # 'buy' or 'sell'
    strength: float
    type: str = 'SIGNAL'

@dataclass
class OrderEvent(Event):
    symbol: str
    side: str
    quantity: float
    order_type: str # 'market' or 'limit'
    price: Optional[float] = None
    type: str = 'ORDER'

@dataclass
class FillEvent(Event):
    symbol: str
    side: str
    quantity: float
    price: float
    commission: float
    slippage: float
    cost: float
    type: str = 'FILL'

# --- Backtester Engine ---
class EventDrivenBacktester:
    """
    Professional Event-Driven Backtester.
    Simulates trading tick-by-tick with Transaction Cost Analysis (TCA).
    """

    def __init__(self, initial_capital: float = 10000.0, maker_fee: float = 0.001, taker_fee: float = 0.002, slippage_model: float = 0.0005):
        """
        Args:
            initial_capital (float): Starting cash.
            maker_fee (float): Fee for limit orders (0.1% default).
            taker_fee (float): Fee for market orders (0.2% default).
            slippage_model (float): Estimated slippage percentage (0.05% default).
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {} # {symbol: quantity}
        self.events = asyncio.Queue()
        self.trades: List[FillEvent] = []
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.slippage_model = slippage_model
        self.current_market_data = {} # {symbol: price}

    async def load_data(self, data: pd.DataFrame):
        """
        Load historical data and push MarketEvents to the queue.
        Assumes DataFrame has 'timestamp', 'symbol', 'close', 'volume'.
        """
        logger.info("Loading data into event queue...")
        for index, row in data.iterrows():
            event = MarketEvent(
                timestamp=row['timestamp'],
                symbol=row['symbol'],
                price=row['close'],
                volume=row['volume']
            )
            await self.events.put(event)
        
        # Signal end of data
        await self.events.put(None) 

    async def run(self, strategy_callback):
        """
        Main Event Loop.
        
        Args:
            strategy_callback: Async function that takes (backtester, event) and generates signals.
        """
        logger.info("Starting Backtest...")
        
        while True:
            event = await self.events.get()
            if event is None:
                break
            
            if event.type == 'MARKET':
                self.current_market_data[event.symbol] = event.price
                await strategy_callback(self, event)
                
            elif event.type == 'SIGNAL':
                await self.handle_signal(event)
                
            elif event.type == 'ORDER':
                await self.process_order(event)
            
            self.events.task_done()
            
        self.generate_report()

    async def handle_signal(self, signal: SignalEvent):
        """Convert Signal to Order."""
        # Simple sizing logic: Use 10% of capital per trade
        target_allocation = 0.1
        price = self.current_market_data.get(signal.symbol)
        
        if not price:
            return

        amount = (self.current_capital * target_allocation) / price
        
        order = OrderEvent(
            timestamp=signal.timestamp,
            symbol=signal.symbol,
            side=signal.side,
            quantity=amount,
            order_type='market' # Default to market for signals
        )
        await self.events.put(order)

    async def process_order(self, order: OrderEvent):
        """Execute Order and calculate TCA."""
        price = self.current_market_data.get(order.symbol)
        if not price:
            return

        # Apply Slippage
        # Buy executes higher, Sell executes lower
        slippage_impact = price * self.slippage_model
        exec_price = price + slippage_impact if order.side == 'buy' else price - slippage_impact
        
        # Calculate Fees
        fee_rate = self.maker_fee if order.order_type == 'limit' else self.taker_fee
        commission = (exec_price * order.quantity) * fee_rate
        
        cost = (exec_price * order.quantity) + commission if order.side == 'buy' else (exec_price * order.quantity) - commission
        
        # Update Portfolio
        if order.side == 'buy':
            if self.current_capital >= cost:
                self.current_capital -= cost
                self.positions[order.symbol] = self.positions.get(order.symbol, 0) + order.quantity
                
                fill = FillEvent(
                    timestamp=order.timestamp,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=exec_price,
                    commission=commission,
                    slippage=slippage_impact,
                    cost=cost
                )
                self.trades.append(fill)
            else:
                logger.warning("Insufficient funds for buy order")
                
        elif order.side == 'sell':
            current_pos = self.positions.get(order.symbol, 0)
            if current_pos >= order.quantity:
                self.current_capital += (exec_price * order.quantity) - commission
                self.positions[order.symbol] -= order.quantity
                
                fill = FillEvent(
                    timestamp=order.timestamp,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=exec_price,
                    commission=commission,
                    slippage=slippage_impact,
                    cost=cost
                )
                self.trades.append(fill)
            else:
                logger.warning("Insufficient position for sell order")

    def generate_report(self):
        """Generate Performance Report with TCA."""
        logger.info("--- Backtest Report ---")
        total_trades = len(self.trades)
        total_commission = sum(t.commission for t in self.trades)
        total_slippage_cost = sum(t.slippage * t.quantity for t in self.trades)
        
        # Mark to Market Portfolio Value
        portfolio_value = self.current_capital
        for symbol, qty in self.positions.items():
            price = self.current_market_data.get(symbol, 0)
            portfolio_value += qty * price
            
        pnl = portfolio_value - self.initial_capital
        roi = (pnl / self.initial_capital) * 100
        
        print(f"Total Trades: {total_trades}")
        print(f"Final Portfolio Value: ${portfolio_value:.2f}")
        print(f"Total PnL: ${pnl:.2f} ({roi:.2f}%)")
        print(f"Total Fees Paid: ${total_commission:.2f}")
        print(f"Est. Slippage Cost: ${total_slippage_cost:.2f}")
        print("-----------------------")

# Example Strategy Callback
async def example_strategy(backtester, event):
    if event.type == 'MARKET':
        # Simple random signal for testing
        import random
        if random.random() < 0.05:
            side = 'buy' if random.random() > 0.5 else 'sell'
            signal = SignalEvent(
                timestamp=event.timestamp,
                symbol=event.symbol,
                side=side,
                strength=0.8
            )
            await backtester.events.put(signal)
