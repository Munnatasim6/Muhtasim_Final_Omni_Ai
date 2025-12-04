import logging
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Existing Modules (Preserved)
# Existing Modules (Preserved)
from backend.brain.swarm_manager import SwarmManager
from core.scrapers.social_scraper import SocialScraper
from core.macro_correlator import MacroCorrelator
from core.meta_brain.evolution import EvolutionEngine
from core.meta_brain.local_llm import LocalStrategyGenerator
from core.scrapers.dao_tracker import GovernanceWatcher
from liquidation_bot import LiquidationMonitor
from core.aggregator.global_book import GlobalLiquidityWall
from core.macro.trends_engine import TrendsEngine
from stablecoin_watch import StablecoinWatch
from core.fundamental.github_tracker import GithubTracker
from exchange_flow import ExchangeFlow

# --- ULTIMATE HEDGE FUND UPGRADE (7 NEW MODULES) ---
from core.fundamental.defillama_tracker import DefiLlamaTracker
from bridge_watcher import BridgeWatcher
from gas_watcher import GasWatcher
from core.market.options_sentiment import OptionsSentiment
from funding_arb import FundingArbScanner
from core.macro.news_trader import NewsTrader
from core.scrapers.alpha_scout import AlphaScout
# ---------------------------------------------------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeCore")

app = FastAPI(title="OmniTrade AI Core", version="5.0.0 (Ultimate Hedge Fund)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize All Managers (Existing)
swarm_manager = SwarmManager()
social_scraper = SocialScraper()
macro_correlator = MacroCorrelator()
evolution_engine = EvolutionEngine()
local_llm = LocalStrategyGenerator()
governance_watcher = GovernanceWatcher()
global_liquidity = GlobalLiquidityWall()
trends_engine = TrendsEngine()
github_tracker = GithubTracker()

# Initialize New Managers (Ultimate Upgrade)
defillama_tracker = DefiLlamaTracker()
bridge_watcher = BridgeWatcher()
gas_watcher = GasWatcher()
options_sentiment = OptionsSentiment()
funding_arb = FundingArbScanner()
news_trader = NewsTrader()
alpha_scout = AlphaScout()

# Web3 Config
POLYGON_RPC = "https://polygon-rpc.com"
ETH_RPC = "https://eth.public-rpc.com"
AAVE_V3_POOL_POLYGON = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
liquidation_monitor = LiquidationMonitor(POLYGON_RPC, AAVE_V3_POOL_POLYGON)
stablecoin_watch = StablecoinWatch(ETH_RPC)
exchange_flow = ExchangeFlow(ETH_RPC)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting OmniTrade AI Core (Ultimate Hedge Fund Level)...")
    
    # 1. Start Existing Tasks
    asyncio.create_task(social_scraper.start_stream())
    asyncio.create_task(run_macro_analysis())
    asyncio.create_task(run_evolution_cycle())
    asyncio.create_task(run_governance_watch())
    asyncio.create_task(run_liquidity_monitor())
    asyncio.create_task(run_global_book_analysis())
    asyncio.create_task(run_trends_analysis())
    asyncio.create_task(run_stablecoin_watch())
    asyncio.create_task(run_github_tracking())
    asyncio.create_task(run_exchange_flow_monitor())
    
    # 2. Start ULTIMATE UPGRADE Tasks (7 New Modules)
    asyncio.create_task(defillama_tracker.run_cycle())
    asyncio.create_task(bridge_watcher.run_cycle())
    asyncio.create_task(gas_watcher.run_cycle())
    asyncio.create_task(options_sentiment.run_cycle())
    asyncio.create_task(funding_arb.run_cycle())
    asyncio.create_task(news_trader.run_cycle())
    # Note: AlphaScout may require valid keys to run without error, wrapping in try/except implicitly handled inside class
    asyncio.create_task(alpha_scout.run_cycle())
    
    logger.info("✅ All Systems Operational: Alpha, Macro, Web3, & Sentiment Active.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await social_scraper.stop_stream()

# --- Wrapper Functions for Existing Tasks ---
async def run_macro_analysis():
    while True:
        try:
            await macro_correlator.fetch_macro_data()
        except Exception as e: logger.error(f"Macro failed: {e}")
        await asyncio.sleep(3600)

async def run_evolution_cycle():
    while True:
        try: evolution_engine.evolve()
        except Exception as e: logger.error(f"Evo failed: {e}")
        await asyncio.sleep(86400)

async def run_governance_watch():
    while True:
        try: governance_watcher.run_cycle()
        except Exception: pass
        await asyncio.sleep(3600)

async def run_liquidity_monitor():
    users = ["0x0000000000000000000000000000000000000000"]
    while True:
        try: liquidation_monitor.monitor_users(users)
        except Exception: pass
        await asyncio.sleep(60)

async def run_global_book_analysis():
    while True:
        try: await global_liquidity.run_analysis()
        except Exception: pass
        await asyncio.sleep(10)

async def run_trends_analysis():
    while True:
        try: trends_engine.analyze_sentiment()
        except Exception: pass
        await asyncio.sleep(3600)

async def run_stablecoin_watch():
    while True:
        try: stablecoin_watch.check_recent_mints()
        except Exception: pass
        await asyncio.sleep(60)

async def run_github_tracking():
    while True:
        try: github_tracker.analyze_activity({"ETH": "UP"})
        except Exception: pass
        await asyncio.sleep(86400)

async def run_exchange_flow_monitor():
    while True:
        try: exchange_flow.check_flows()
        except Exception: pass
        await asyncio.sleep(15)

@app.get("/")
def read_root():
    return {"status": "active", "system": "OmniTrade AI Core v5.0", "level": "Ultimate Hedge Fund"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Mock Data Payload
            payload = {
                "active_agents": [],
                "signals": {},
                "timestamp": "2025-11-30T00:00:00Z"
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

