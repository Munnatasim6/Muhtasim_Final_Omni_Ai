import logging
import asyncio
import json
import psutil  # সিস্টেম হেলথ চেকের জন্য
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# --- Import Core Modules ---
# (আপনার প্রোজেক্ট স্ট্রাকচার অনুযায়ী পাথ ঠিক আছে কি না চেক করবেন)
try:
    from backend.brain.swarm_manager import SwarmManager
    from core.scrapers.social_scraper import SocialScraper
    from core.meta_brain.evolution import EvolutionEngine
    from core.fundamental.defillama_tracker import DefiLlamaTracker
    from core.market.options_sentiment import OptionsSentiment
except ImportError as e:
    print(f"⚠️ Import Warning: {e}")
    # ডামি ক্লাস যাতে ইম্পোর্ট এরর না দেয় (ডেভেলপমেন্টের সুবিধার জন্য)
    class SwarmManager:
        async def get_swarm_decision(self, data): return {"action": "HOLD", "confidence": 0.5, "details": {}}
    class SocialScraper:
        async def start_stream(self): pass
        async def stop_stream(self): pass
    class EvolutionEngine: pass
    class DefiLlamaTracker:
        async def run_cycle(self): pass
    class OptionsSentiment:
        async def run_cycle(self): pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeGateway")

app = FastAPI(
    title="OmniTrade AI Core",
    version="5.0.0",
    description="The Ultimate Hedge Fund Grade AI System"
)

# --- CORS (Security) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # প্রোডাকশনে এটি "http://localhost:3000" করে দেবেন
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global System State ---
class SystemState:
    is_active = True        # Kill Switch
    risk_level = 0.05       # 5% Risk
    active_agents = ["Scalper (DQN)", "Trend (PPO)", "Whale Watcher"]
    
state = SystemState()

# --- Manager Initialization ---
swarm_manager = SwarmManager()
social_scraper = SocialScraper()
# অন্যান্য ম্যানেজারগুলো এখানে ইনিশিয়ালাইজ হবে...

# --- WebSocket Manager (The Broadcaster) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        # সব কানেক্টেড ক্লায়েন্টকে মেসেজ পাঠানো
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # মৃত কানেকশন ইগনোর করা
                pass

manager = ConnectionManager()

# --- Background Channels (The 3 Lines) ---

async def channel_market_data():
    """
    CHANNEL 1: High-Frequency Market Data (Updates every 0.1s)
    """
    logger.info("📡 Market Data Channel Active")
    while True:
        if state.is_active:
            # এখানে Redis থেকে আসল ডেটা আসবে। এখন মক ডেটা দেওয়া হলো।
            price_fluctuation = random.uniform(-50, 50)
            market_payload = {
                "channel": "market",
                "data": {
                    "symbol": "BTC/USDT",
                    "price": 98450.00 + price_fluctuation,
                    "volume": 50000 + random.randint(-1000, 1000),
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            await manager.broadcast_json(market_payload)
        
        await asyncio.sleep(0.1) # 100ms Latency

async def channel_brain_activity():
    """
    CHANNEL 2: AI Reasoning & Decisions (Updates every 1s)
    """
    logger.info("🧠 Brain Activity Channel Active")
    while True:
        if state.is_active:
            # মক মার্কেট ডেটা ব্রেইনকে পাঠানো হচ্ছে
            mock_market = {"price": 98450, "volume": 50000}
            
            # ব্রেইন থেকে ডিসিশন নেওয়া
            decision = await swarm_manager.get_swarm_decision(mock_market)
            
            brain_payload = {
                "channel": "brain",
                "data": {
                    "action": decision.get("action", "HOLD"),
                    "confidence": decision.get("confidence", 0.0),
                    "reason": decision.get("details", {}).get("ai_reason", "Calculating..."),
                    "risk_status": decision.get("details", {}).get("risk_status", "CHECKING"),
                    "active_agents": state.active_agents
                }
            }
            await manager.broadcast_json(brain_payload)
            
        await asyncio.sleep(1) # 1s Latency for AI thinking

async def channel_system_health():
    """
    CHANNEL 3: System Health & Logs (Updates every 5s)
    """
    logger.info("❤️ System Health Channel Active")
    while True:
        # CPU & RAM Check
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        health_payload = {
            "channel": "system",
            "data": {
                "status": "ONLINE" if state.is_active else "PAUSED",
                "cpu_usage": cpu,
                "ram_usage": ram,
                "risk_level": f"{state.risk_level * 100}%",
                "uptime": "Running..."
            }
        }
        await manager.broadcast_json(health_payload)
        await asyncio.sleep(5) # 5s Latency

# --- WebSocket Route ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # ক্লায়েন্ট থেকে কোনো মেসেজ আসলে এখানে হ্যান্ডেল করা হবে (যেমন PING)
            data = await websocket.receive_text()
            # আপাতত কিছু করার দরকার নেই
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Control API Endpoints ---

class ScaleRequest(BaseModel):
    replicas: int

@app.get("/")
def read_root():
    return {"status": "active", "system": "OmniTrade Core v5"}

@app.post("/api/system/kill")
async def kill_switch():
    """EMERGENCY STOP: Stops all broadcasting and trading."""
    state.is_active = False
    logger.critical("🚨 KILL SWITCH ACTIVATED! System Halted.")
    # এখানে ExecutionEngine.cancel_all() কল করতে হবে
    await manager.broadcast_json({"channel": "alert", "message": "SYSTEM KILLED BY USER"})
    return {"status": "KILLED", "message": "System halted successfully"}

@app.post("/api/system/resume")
async def resume_system():
    state.is_active = True
    logger.info("✅ System Resumed.")
    return {"status": "ACTIVE", "message": "System resumed"}

@app.post("/api/system/scale-scraper")
async def scale_scrapers(request: ScaleRequest):
    logger.info(f"Scaling scrapers to {request.replicas}...")
    return {"status": "SCALED", "replicas": request.replicas}

@app.get("/api/wallet/balance")
async def get_wallet_balance():
    # ভবিষ্যতে এখানে CCXT দিয়ে রিয়েল ব্যালেন্স আনা হবে
    return {
        "total_usdt": 15420.50,
        "btc_balance": 0.45,
        "pnl_daily": 12.5
    }

# --- Application Events ---

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting OmniTrade AI Core...")
    
    # Start Background Services (Scrapers, Trackers)
    asyncio.create_task(social_scraper.start_stream())
    
    # Start The 3 Data Channels
    asyncio.create_task(channel_market_data())
    asyncio.create_task(channel_brain_activity())
    asyncio.create_task(channel_system_health())
    
    logger.info("✅ All Channels Online.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🌙 Shutting down...")
    # Cleanup logic here
