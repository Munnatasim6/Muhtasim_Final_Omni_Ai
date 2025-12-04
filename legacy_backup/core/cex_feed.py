import asyncio
import json
import logging
import aiohttp
from typing import List, Callable, Dict
from config.config import settings
from db.redis_client import redis_client
from db.timescale import db

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages WebSocket connections with auto-reconnection and heartbeat logic.
    """
    def __init__(self, url: str, on_message: Callable):
        self.url = url
        self.on_message = on_message
        self.running = False
        self.ws = None
        self.reconnect_delay = 1

    async def connect(self):
        self.running = True
        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self.url) as ws:
                        self.ws = ws
                        self.reconnect_delay = 1 # Reset delay on successful connection
                        logger.info(f"Connected to WebSocket: {self.url}")
                        
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.on_message(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"WebSocket connection closed with exception {ws.exception()}")
                                break
            except Exception as e:
                logger.error(f"WebSocket connection failed: {e}")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 60) # Exponential backoff

    async def send(self, data: dict):
        if self.ws:
            await self.ws.send_json(data)

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()

class CEXFeed:
    """
    Real-time Data Feed from Centralized Exchanges via WebSocket.
    """
    def __init__(self):
        # Binance WebSocket URL
        self.base_url = "wss://stream.binance.com:9443/ws"
        self.symbols = ['btcusdt', 'ethusdt']
        self.streams = []
        for s in self.symbols:
            self.streams.append(f"{s}@ticker")
            self.streams.append(f"{s}@depth10@100ms") # L2 Order Book
        
        self.stream_url = f"{self.base_url}/{'/'.join(self.streams)}"
        self.ws_manager = WebSocketManager(self.stream_url, self.handle_message)

    async def start(self):
        logger.info("Starting CEX WebSocket Feed...")
        await self.ws_manager.connect()

    async def handle_message(self, message: str):
        try:
            data = json.loads(message)
            stream = data.get('stream')
            payload = data.get('data')

            if not stream or not payload:
                return

            if 'ticker' in stream:
                await self.process_ticker(payload)
            elif 'depth' in stream:
                await self.process_order_book(payload)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def process_ticker(self, data: dict):
        symbol = data['s']
        price = float(data['c'])
        volume = float(data['q'])
        
        # Save to Redis for ultra-low latency access
        await redis_client.redis.set(f"ticker:{symbol}", json.dumps({
            'price': price,
            'volume': volume,
            'time': data['E']
        }))

        # Async insert to TimescaleDB (fire and forget to avoid blocking)
        asyncio.create_task(self.save_to_db(symbol, price, volume))

    async def process_order_book(self, data: dict):
        symbol = data['s']
        # data['bids'] and data['asks'] are lists of [price, quantity]
        # Snapshot to Redis
        await redis_client.set_order_book(symbol, data)

    async def save_to_db(self, symbol, price, volume):
        try:
            async with db.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO market_data (time, symbol, price, volume, source)
                    VALUES (NOW(), $1, $2, $3, 'binance_ws')
                """, symbol, price, volume)
        except Exception as e:
            logger.error(f"DB Insert Error: {e}")

    async def stop(self):
        await self.ws_manager.stop()
        logger.info("CEX Feed stopped")
