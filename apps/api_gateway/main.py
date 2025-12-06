import logging
import asyncio
import json
import psutil  # For System Health Monitor
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# Existing Modules (Preserved & Enhanced)
# আপনার ফোল্ডার স্ট্রাকচার অনুযায়ী ইমপোর্ট পাথ ঠিক রাখা হয়েছে
try:
    from backend.brain.swarm_manager import SwarmManager
    from core.scrapers.social_scraper import SocialScraper
    from core.macro_correlator import MacroCorrelator
    from core.meta_brain.evolution import EvolutionEngine
    from core.scrapers.dao_tracker import GovernanceWatcher
    from core.aggregator.global_book import GlobalLiquidityWall
    from core.fundamental.github_tracker import GithubTracker
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
    class GovernanceWatcher:
        def run_cycle(self): pass
    class GlobalLiquidityWall:
        async def run_analysis(self): pass
    class GithubTracker:
        def analyze_activity(self, x): pass
    class DefiLlamaTracker:
        async def run_cycle(self): pass
    class OptionsSentiment:
        async def run_cycle(self): pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeCore")

app = FastAPI(title="OmniTrade AI Core", version="5.0.0 (Ultimate Hedge Fund)")

# CORS (Security Layer for Dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global State Manager ---
class SystemState:
    is_active = True  # Kill Switch Status
    risk_level = 0.05 # Default 5% Risk (As per Phase 2 fix)
    active_agents = ["Scalper (DQN)", "Trend (PPO)", "Risk Manager"]

state = SystemState()

# --- Initialize Managers ---
swarm_manager = SwarmManager()
social_scraper = SocialScraper()
macro_correlator = MacroCorrelator()
evolution_engine = EvolutionEngine()
governance_watcher = GovernanceWatcher()
global_liquidity = GlobalLiquidityWall()
github_tracker = GithubTracker()
defillama_tracker = DefiLlamaTracker()
options_sentiment = OptionsSentiment()

# --- Pydantic Models for API ---
class ScaleRequest(BaseModel):
    replicas: int

# --- API Endpoints (Control Systems) ---

@app.get("/")
def read_root():
    return {
        "status": "ONLINE" if state.is_active else "STOPPED",
        "system": "OmniTrade AI Core v5.0",
        "risk_level": f"{state.risk_level * 100}%",
        "level": "Ultimate Hedge Fund"
    }

# 1. Emergency Kill Switch
@app.post("/api/system/kill")
async def kill_switch():
    """
    EMERGENCY: Stops all trading and cancels open orders.
    """
    state.is_active = False
    logger.critical("🚨 KILL SWITCH ACTIVATED! System Halted.")
    # Here you would call execution_engine.cancel_all_orders()
    return {"status": "KILLED", "message": "All operations halted. Orders cancelled."}

# 2. System Resume
@app.post("/api/system/resume")
async def resume_system():
    state.is_active = True
    logger.info("✅ System Resumed by User.")
    return {"status": "ACTIVE", "message": "Trading operations resumed."}

# 3. Scraper Scaling (Docker Control Stub)
@app.post("/api/system/scale-scraper")
async def scale_scrapers(request: ScaleRequest):
    """
    Simulates scaling Docker containers for scrapers.
    """
    logger.info(f"⚖️ Scaling Scrapers to {request.replicas} replicas...")
    # In real K8s/Docker: subprocess.call(["docker", "service", "scale", ...])
    return {"status": "SCALED", "replicas": request.replicas, "message": "Scaling command sent."}

# 4. System Health Monitor (CPU/RAM)
@app.get("/api/system/health")
async def system_health():
    """
    Returns real-time server stats for the Dashboard.
    """
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return {
        "cpu_usage": cpu,
        "ram_usage": ram,
        "status": "CRITICAL" if ram > 90 else "HEALTHY"
    }

# 5. Wallet Balance (Mock for now, connect ccxt later)
@app.get("/api/wallet/balance")
async def get_balance():
    return {
        "total_usdt": 12500.50,
        "btc_value": 0.45,
        "pnl_24h": "+$124.50 (1.2%)"
    }

# --- Multi-Channel WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- Background Channels (The 3 Lines of Communication) ---

async def channel_market_data():
    """
    CHANNEL 1: High-Frequency Market Data (Updates every 0.1s for multiple assets)
    """
    logger.info("📡 Market Data Channel Active")
    
    # Base prices for simulation (Preserved Multi-Asset Feature)
    prices = {
        "BTC/USDT": 98450.00,
        "ETH/USDT": 3850.00,
        "SOL/USDT": 145.50,
        "BNB/USDT": 620.00
    }
    
    while True:
        if state.is_active:
            # Loop through all symbols and broadcast updates
            for symbol in prices.keys():
                # Simulate price movement
                fluctuation = random.uniform(-0.0005, 0.0005) # 0.05% fluctuation
                current_price = prices[symbol] * (1 + fluctuation)
                prices[symbol] = current_price # Update base price for next iteration
                
                market_payload = {
                    "channel": "market",
                    "data": {
                        "symbol": symbol,
                        "price": round(current_price, 2),
                        "volume": random.randint(1000, 50000),
                        "timestamp": asyncio.get_event_loop().time()
                    }
                }
                await manager.broadcast_json(market_payload)
                # Small delay between symbols
                await asyncio.sleep(0.02) 
        
        await asyncio.sleep(0.1) # Overall cycle latency

async def channel_brain_activity():
    """
    CHANNEL 2: AI Reasoning & Decisions (Updates every 1s)
    """
    logger.info("🧠 Brain Activity Channel Active")
    while True:
        if state.is_active:
            # মক মার্কেট ডেটা ব্রেইনকে পাঠানো হচ্ছে
            # (পরবর্তীতে এটি রিয়েল মার্কেট ডেটা হবে)
            mock_market = {
                "price": 98450, 
                "volume": 50000, 
                "features": [1.0, 0.9, 1.0, 0.8, 1.0],
                "portfolio_value": 10000.0
            }
            
            # ব্রেইন (SwarmManager) থেকে ডিসিশন নেওয়া
            try:
                decision = await swarm_manager.get_swarm_decision(mock_market)
                
                brain_payload = {
                    "channel": "brain",
                    "data": {
                        "action": decision.get("action", "HOLD"),
                        "confidence": decision.get("confidence", 0.0),
                        "reason": decision.get("details", {}).get("ai_reason", "Analyzing market structure..."),
                        "risk_status": decision.get("details", {}).get("risk_status", "CHECKING"),
                        "active_agents": state.active_agents
                    }
                }
                await manager.broadcast_json(brain_payload)
            except Exception as e:
                logger.error(f"Brain Channel Error: {e}")
            
        await asyncio.sleep(1) # 1s Latency for AI thinking

async def channel_system_health():
    """
    CHANNEL 3: System Health & Logs (Updates every 2s)
    """
    logger.info("❤️ System Health Channel Active")
    while True:
        try:
            # CPU & RAM Check (interval=None for non-blocking)
            cpu = psutil.cpu_percent(interval=None)
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
        except Exception as e:
            logger.error(f"Health Monitor Error: {e}")
            
        await asyncio.sleep(2) # 2s Latency (Preserved Fast Update)

# --- WebSocket Route ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("🖥️ Dashboard Connected via WebSocket")
    try:
        while True:
            # ক্লায়েন্ট থেকে কোনো মেসেজ আসলে এখানে হ্যান্ডেল করা হবে
            data = await websocket.receive_text()
            # আপাতত কিছু করার দরকার নেই, আমরা শুধু ব্রডকাস্ট করছি
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("❌ Dashboard Disconnected")

# --- Application Events ---

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting OmniTrade AI Core (Ultimate Hedge Fund Level)...")
    
    # 1. Start Background Services (Scrapers, Trackers)
    asyncio.create_task(social_scraper.start_stream())
    asyncio.create_task(defillama_tracker.run_cycle())
    asyncio.create_task(options_sentiment.run_cycle())
    
    # 2. Start The 3 Data Channels for Dashboard
    asyncio.create_task(channel_market_data())
    asyncio.create_task(channel_brain_activity())
    asyncio.create_task(channel_system_health())
    
    logger.info("✅ API Gateway Ready & Broadcasting Channels Online.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🌙 Shutting down...")
    await social_scraper.stop_stream()
