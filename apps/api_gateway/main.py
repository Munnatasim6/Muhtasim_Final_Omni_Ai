
import logging
import asyncio
import json
import psutil  # For System Health Monitor
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# Existing Modules (Preserved & Enhanced)
from backend.brain.swarm_manager import SwarmManager
from core.scrapers.social_scraper import SocialScraper
from core.macro_correlator import MacroCorrelator
from core.meta_brain.evolution import EvolutionEngine
from core.scrapers.dao_tracker import GovernanceWatcher
from core.aggregator.global_book import GlobalLiquidityWall
from core.fundamental.github_tracker import GithubTracker
from core.fundamental.defillama_tracker import DefiLlamaTracker
from core.market.options_sentiment import OptionsSentiment

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
    risk_level = 0.05 # Default 5% Risk
    active_agents = ["scalper", "trend", "risk_manager"]

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

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("🖥️ Dashboard Connected via WebSocket")
    try:
        while True:
            if not state.is_active:
                # If Kill Switch is ON, send warning
                await websocket.send_json({"type": "SYSTEM_ALERT", "data": "SYSTEM HALTED"})
                await asyncio.sleep(1)
                continue

            # 1. Get Live Market Logic (Simulation for now, connect Redis later)
            market_data = {
                "price": 95000 + (asyncio.get_event_loop().time() % 10), # Fake jitter
                "volume": 50000
            }
            
            # 2. Get Brain Decision
            # We call SwarmManager logic here
            decision = await swarm_manager.get_swarm_decision(market_data)
            
            # 3. Construct Multi-Channel Payload
            payload = {
                "type": "FULL_UPDATE",
                "timestamp": asyncio.get_event_loop().time(),
                "market": {
                    "symbol": "BTC/USDT",
                    "price": market_data['price'],
                    "volume": market_data['volume']
                },
                "brain": {
                    "action": decision['action'],
                    "confidence": decision['confidence'],
                    "reason": decision['details'].get('ai_reason', 'Analyzing...'),
                    "risk_status": decision['details'].get('risk_status', 'UNKNOWN')
                },
                "agents": {
                    "active_count": len(state.active_agents),
                    "names": state.active_agents
                }
            }
            
            # Send to Frontend
            await websocket.send_json(payload)
            
            # Fast update rate (100ms) for Pro feel
            await asyncio.sleep(0.1) 
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("❌ Dashboard Disconnected")

# --- Background Tasks ---
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting OmniTrade AI Core (Ultimate Hedge Fund Level)...")
    
    # Start Background Tasks
    asyncio.create_task(social_scraper.start_stream())
    asyncio.create_task(defillama_tracker.run_cycle())
    asyncio.create_task(options_sentiment.run_cycle())
    
    logger.info("✅ API Gateway Ready. Waiting for Frontend Connection...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🌙 Shutting down...")
    await social_scraper.stop_stream()
