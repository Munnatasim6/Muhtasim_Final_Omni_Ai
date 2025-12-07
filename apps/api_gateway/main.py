import logging
import asyncio
import json
import psutil
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# Existing Modules
from backend.brain.swarm_manager import SwarmManager
from core.scrapers.social_scraper import SocialScraper
from core.macro_correlator import MacroCorrelator
from core.meta_brain.evolution import EvolutionEngine
from core.scrapers.dao_tracker import GovernanceWatcher
from core.aggregator.global_book import GlobalLiquidityWall
from core.fundamental.github_tracker import GithubTracker
from core.fundamental.defillama_tracker import DefiLlamaTracker
from core.market.options_sentiment import OptionsSentiment
from services.blockchain_watcher.src.gas_watcher import GasWatcher # [NEW IMPORT]
from libs.database.src.timescale import db # [NEW IMPORT for History]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeCore")

app = FastAPI(title="OmniTrade AI Core", version="5.2.0 (Full Features)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global State ---
class SystemState:
    is_active = True
    risk_level = 0.05
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
gas_watcher = GasWatcher() # [NEW INSTANCE]

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ONLINE", "system": "OmniTrade AI Core"}

# --- 1. System Health (Already Done - Keeping it) ---
@app.get("/api/system/health")
async def system_health():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return {"cpu_usage": cpu, "ram_usage": ram, "status": "CRITICAL" if ram > 90 else "HEALTHY"}

@app.post("/api/system/kill")
async def kill_switch():
    state.is_active = False
    return {"status": "KILLED", "message": "System Halted."}

@app.post("/api/system/resume")
async def resume_system():
    state.is_active = True
    return {"status": "ACTIVE", "message": "System Resumed."}

class ScaleRequest(BaseModel):
    replicas: int

@app.post("/api/system/scale-scraper")
async def scale_scrapers(request: ScaleRequest):
    logger.info(f"Scaling scrapers to {request.replicas}")
    return {"status": "SCALED", "replicas": request.replicas}

# --- 2. Module Specific Endpoints (MISSING PART FIXED) ---

@app.get("/api/modules/gas")
async def get_gas_data():
    """Returns real-time Gas Fees from GasWatcher."""
    # Assuming run_cycle updates an internal variable, or we fetch live
    # For speed, we trigger a quick check
    await gas_watcher.check_gas()
    return {
        "fast_fee": gas_watcher.last_fast_fee,
        "status": "High" if gas_watcher.last_fast_fee > 50 else "Normal"
    }

@app.get("/api/modules/defi")
async def get_defi_gems():
    """Returns undervalued protocols from DeFiLlama."""
    opportunities = await defillama_tracker.analyze_market()
    return {"data": opportunities}

@app.get("/api/modules/macro")
async def get_macro_data():
    """Returns Macro Economic Correlations."""
    corr = macro_correlator.calculate_correlations()
    regime = macro_correlator.analyze_risk_regime(corr)
    return {"regime": regime, "correlations": corr}

# --- 3. Historical Data / Time Travel (MISSING PART FIXED) ---

@app.get("/api/history/trades")
async def get_trade_history(limit: int = 50):
    """Fetches past trades from TimescaleDB."""
    try:
        # Direct DB query using the existing db pool
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT time, symbol, side, price, pnl FROM trade_history ORDER BY time DESC LIMIT $1", 
                limit
            )
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return []

# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if not state.is_active:
                await websocket.send_json({"type": "ALERT", "msg": "SYSTEM HALTED"})
                await asyncio.sleep(1)
                continue
            
            # Simulated Feed
            market_data = {"price": 95000 + (asyncio.get_event_loop().time() % 10), "volume": 5000}
            decision = await swarm_manager.get_swarm_decision(market_data)
            
            await websocket.send_json({
                "type": "FULL_UPDATE",
                "market": market_data,
                "brain": decision
            })
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass

# --- Startup ---
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 System Startup...")
    await db.connect() # Ensure DB connects first
    # Start Background Tasks
    asyncio.create_task(social_scraper.start_stream())
    asyncio.create_task(defillama_tracker.run_cycle())
    asyncio.create_task(gas_watcher.run_cycle())
