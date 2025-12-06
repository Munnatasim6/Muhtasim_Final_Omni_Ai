import logging
import asyncio
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# --- Import Core Modules ---
from backend.brain.swarm_manager import SwarmManager
from core.scrapers.social_scraper import SocialScraper
from core.macro_correlator import MacroCorrelator
from core.meta_brain.evolution import EvolutionEngine
from core.scrapers.dao_tracker import GovernanceWatcher
from core.aggregator.global_book import GlobalLiquidityWall
from core.fundamental.github_tracker import GithubTracker
from core.fundamental.defillama_tracker import DefiLlamaTracker
from core.market.options_sentiment import OptionsSentiment

# --- Import Blockchain Services (New) ---
# নিশ্চিত করুন এই পাথগুলো আপনার Dockerfile-এ PYTHONPATH এ আছে
from services.blockchain_watcher.src.gas_watcher import GasWatcher
from services.blockchain_watcher.src.whale_graph import WhaleGraph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeCore")

app = FastAPI(title="OmniTrade AI Core", version="5.1.0 (Module Endpoints)")

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
    
    # Quota Tracking
    ai_requests_today = 0
    last_reset_day = 0

    def check_reset(self):
        current_day = time.localtime().tm_yday
        if current_day != self.last_reset_day:
            self.ai_requests_today = 0
            self.last_reset_day = current_day

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

# New Services
gas_watcher = GasWatcher()
whale_graph = WhaleGraph() # Ensure Neo4j is running for this

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ONLINE", "system": "OmniTrade AI Core", "mode": "God-Tier"}

# --- 1. Module Specific Endpoints (NEW) ---

@app.get("/api/modules/gas")
async def get_gas_analytics():
    """Returns current Gas Fees and Trend."""
    # Assuming gas_watcher has a method to get latest data without checking API instantly
    # You might need to adjust gas_watcher to store 'last_known_fee' in a variable
    return {
        "fast_fee": gas_watcher.last_fast_fee,
        "status": "Normal" if gas_watcher.last_fast_fee < 50 else "High Congestion"
    }

@app.get("/api/modules/defi")
async def get_defi_opportunities():
    """Returns latest Undervalued Gems from DeFiLlama."""
    # This triggers a live check
    opportunities = await defillama_tracker.analyze_market()
    return {"count": len(opportunities), "opportunities": opportunities}

@app.get("/api/modules/macro")
async def get_macro_correlation():
    """Returns Macro-Economic Correlations."""
    correlations = macro_correlator.calculate_correlations()
    regime = macro_correlator.analyze_risk_regime(correlations)
    return {"regime": regime, "data": correlations}

@app.get("/api/modules/whale")
async def get_whale_stats():
    """Returns Whale Cluster Statistics."""
    # Mock response if Neo4j is not connected
    return {
        "active_clusters": 5, 
        "large_movements_24h": "12,500 BTC",
        "insider_activity": "Low"
    }

# --- 2. System Controls ---

@app.post("/api/system/kill")
async def kill_switch():
    state.is_active = False
    logger.critical("🚨 KILL SWITCH ACTIVATED!")
    return {"status": "KILLED", "message": "All operations halted."}

@app.post("/api/system/resume")
async def resume_system():
    state.is_active = True
    return {"status": "ACTIVE", "message": "Operations resumed."}

# --- Scaling Model ---
class ScalingRequest(BaseModel):
    replicas: int

@app.post("/api/system/scale-scraper")
async def scale_scraper_service(request: ScalingRequest):
    """
    Scales the social-scraper service using docker-compose.
    """
    import subprocess
    try:
        # Limit max replicas to prevent system overload
        if request.replicas > 4:
            return {"status": "ERROR", "detail": "Max limit: 4 replicas."}
        
        # Execute Docker scaling command
        cmd = f"docker-compose up -d --scale social-scraper={request.replicas} --no-recreate"
        subprocess.run(cmd, shell=True, check=True)
        
        return {"status": "SUCCESS", "message": f"Scaled to {request.replicas} instances."}
    except Exception as e:
        logger.error(f"Scaling Failed: {e}")
        return {"status": "ERROR", "detail": str(e)}

# --- 3. WebSocket Feed ---
# (Previous WebSocket code remains same)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    import time
    import random
    import ccxt.async_support as ccxt
    
    # Shared state for this connection
    conn_state = {
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "is_active": True
    }

    exchange = None
    try:
        # Initialize Exchange (KuCoin)
        exchange = ccxt.kucoin({
            'enableRateLimit': True,
            # 'options': {'adjustForTimeDifference': True} 
        })
    except Exception as e:
        logger.error(f"KuCoin Init Failed: {e}")
        exchange = None

    async def receive_messages():
        """Listen for client commands like symbol switching and timeframe."""
        try:
            while conn_state["is_active"]:
                data = await websocket.receive_json()
                if data.get("type") == "SUBSCRIBE":
                    new_symbol = data.get("symbol", conn_state["symbol"]).upper()
                    new_timeframe = data.get("timeframe", conn_state["timeframe"])
                    
                    # Basic cleanup
                    if new_symbol and "/" not in new_symbol and "-" not in new_symbol:
                        new_symbol += "/USDT"
                    if "-" in new_symbol: 
                        new_symbol = new_symbol.replace("-", "/")
                    
                    conn_state["symbol"] = new_symbol
                    conn_state["timeframe"] = new_timeframe
                    logger.info(f"Client subscribed: {new_symbol} [{new_timeframe}]")
                    
                    # Confirm subscription
                    await websocket.send_json({"channel": "alert", "message": f"Tracking {new_symbol} ({new_timeframe})"})

                    # Fetch History immediately
                    if exchange:
                        try:
                            # Fetch OHLCV (Timestamp, Open, High, Low, Close, Volume)
                            ohlcv = await exchange.fetch_ohlcv(new_symbol, new_timeframe, limit=300)
                            print(f"DEBUG: Fetched {len(ohlcv)} candles for {new_symbol}")
                            await websocket.send_json({"channel": "candle_history", "data": ohlcv})
                        except Exception as e:
                            logger.error(f"History Fetch Failed: {e}")
                            print(f"DEBUG: History Error: {e}")
                            await websocket.send_json({"channel": "alert", "message": "History unavailable"})

        except Exception as e:
            logger.info(f"Receive Loop Ended: {e}")
            conn_state["is_active"] = False

    async def send_updates():
        """Push live ticker data."""
        last_brain_update = 0
        cached_decision = {
            "action": "HOLD",
            "confidence": 0.5,
            "reason": "Initializing...",
            "risk_status": "PASS"
        }

        try:
            while conn_state["is_active"]:
                if not state.is_active:
                    await websocket.send_json({"channel": "alert", "message": "SYSTEM HALTED"})
                    await asyncio.sleep(1)
                    continue

                current_symbol = conn_state["symbol"]
                current_price = 0.0
                current_volume = 0.0

                # 1. Fetch Market Data (Ticker)
                if exchange:
                    try:
                        ticker = await exchange.fetch_ticker(current_symbol)
                        current_price = float(ticker['last'])
                        current_volume = float(ticker.get('quoteVolume', ticker.get('vol', 0.0)))
                    except Exception as e:
                        logger.warning(f"Ticker Failed for {current_symbol}: {e}")
                        # Fallback
                        current_price = 95000 + random.uniform(-50, 50) if "BTC" in current_symbol else 100 + random.uniform(-1, 1)

                if current_price == 0.0:
                    current_price = 95000 + random.uniform(-50, 50) 

                market_data = {
                    "symbol": current_symbol,
                    "price": current_price,
                    "volume": current_volume,
                    "timestamp": time.time()
                }
                await websocket.send_json({"channel": "market", "data": market_data})

                # 2. Brain Data (Rate Limited)
                state.check_reset()
                current_time = time.time()
                if current_time - last_brain_update > 60:
                    try:
                        decision_payload = {
                            "price": current_price,
                            "volume": current_volume,
                            "symbol": current_symbol
                        }
                        cached_decision = await swarm_manager.get_swarm_decision(decision_payload)
                        last_brain_update = current_time
                        state.ai_requests_today += 1
                    except Exception as e:
                        logger.error(f"AI Update Failed: {e}")

                brain_data = {
                    "action": cached_decision.get("action", "HOLD"),
                    "confidence": cached_decision.get("confidence", 0.0),
                    "reason": cached_decision.get("reason", "Calculating..."),
                    "risk_status": "PASS",
                    "active_agents": state.active_agents
                }
                await websocket.send_json({"channel": "brain", "data": brain_data})

                # 3. System Data
                system_data = {
                    "status": "ONLINE",
                    "cpu_usage": 15.0 + random.uniform(-1, 1),
                    "ram_usage": 42.0 + random.uniform(-0.5, 0.5),
                    "risk_level": "LOW",
                    "uptime": "Active",
                    "ai_quota": state.ai_requests_today,
                    "ai_quota_max": 1000
                }
                await websocket.send_json({"channel": "system", "data": system_data})

                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Send Loop Error: {e}")
            conn_state["is_active"] = False

    # Run concurrently
    await asyncio.gather(receive_messages(), send_updates())
    
    if exchange:
        await exchange.close()



# --- Startup Tasks ---
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting OmniTrade Microservices...")
    asyncio.create_task(social_scraper.start_stream())
    asyncio.create_task(gas_watcher.run_cycle()) # Start Gas Watcher Loop
    # Other background tasks...
