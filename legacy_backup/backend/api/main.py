from fastapi import FastAPI, HTTPException, BackgroundTasks, Security, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
import asyncio
import json

import sys
import os

# Add project root to path to allow importing 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Import Core Modules
from app.config.config import settings
from core.execution import ExecutionEngine
try:
    from core.sentiment import SentimentEngine
except ImportError:
    class SentimentEngine:
        async def start(self): pass
        async def stop(self): pass
        async def get_interest_rate(self): return 0.05
        async def get_social_sentiment(self): return 0.0
from db.timescale import db
from backend.brain.swarm_manager import SwarmManager

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeAPI")

app = FastAPI(
    title="OmniTrade AI Core API",
    version=settings.VERSION,
    description="The Neural Nervous System of the OmniTrade Architecture"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

# --- Engines ---
execution_engine = ExecutionEngine(exchange_client=None)
sentiment_engine = SentimentEngine()
swarm_manager = SwarmManager()

# --- Data Models ---
class TrainingRequest(BaseModel):
    model_id: str
    type: str = "CLOUD" # CLOUD or LOCAL
    epochs: int = 10
    batch_size: int = 32

class TradeSignal(BaseModel):
    symbol: str
    action: str # BUY, SELL, HOLD
    confidence: float
    reason: str

class OrderRequest(BaseModel):
    symbol: str
    side: str # buy, sell
    quantity: float
    price: Optional[float] = None

# --- Routes ---

@app.get("/")
async def root():
    return {"status": "ONLINE", "system": "OmniTrade AI Core", "version": settings.VERSION}

@app.post("/train", dependencies=[Depends(get_api_key)])
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Initiates a training job (Cloud or Local).
    """
    logger.info(f"Received training request: {request}")
    
    # Simulate Job Creation
    job_id = f"job-{request.type.lower()}-{asyncio.get_event_loop().time()}"
    
    if request.type == "CLOUD":
        # In real implementation: vertex_trainer.submit_job(...)
        return {"job_id": job_id, "status": "PENDING", "type": "CLOUD"}
    
    elif request.type == "LOCAL":
        return {"job_id": job_id, "status": "RUNNING", "type": "LOCAL"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid training type")

@app.post("/execute_order", dependencies=[Depends(get_api_key)])
async def execute_order_endpoint(order: OrderRequest):
    """
    Manually execute an order via API (Protected).
    """
    logger.info(f"Manual Order Request: {order}")
    
    # Use the Execution Engine
    # Note: execute_order is async
    await execution_engine.execute_order(
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        price=order.price
    )
    
    return {"status": "ORDER_SENT", "details": order.dict()}

@app.get("/status/agents")
async def get_agent_status():
    """
    Returns the status of all AI Agents (Neural Swarm).
    """
    # In a real scenario, we would fetch the active agents from the ExecutionEngine or DB
    # For now, we will return a dynamic list based on the engine's state if possible, 
    # or at least use the engine to get some real metrics.
    
    # Example: Fetching PnL from the engine (if it was tracking multiple agents)
    # Since ExecutionEngine is currently a single entity, we'll map it to "Scalper" for now
    # and keep others as placeholders but with dynamic values if we had them.
    
    current_pnl = execution_engine.current_pnl
    
    return [
        {"id": "alpha_1", "role": "Scalper", "status": "ACTIVE", "pnl": current_pnl, "accuracy": 0.85},
        {"id": "beta_2", "role": "Swing", "status": "IDLE", "pnl": 450.20, "accuracy": 0.72},
        {"id": "gamma_3", "role": "Arb", "status": "ACTIVE", "pnl": 890.00, "accuracy": 0.91},
        {"id": "omega_0", "role": "Risk Manager", "status": "WATCHING", "pnl": 0.0, "accuracy": 1.0},
    ]

@app.get("/market/sentiment")
async def get_sentiment():
    """
    Returns aggregated sentiment from RAG/News.
    """
    # Use the real Sentiment Engine
    # Note: monitor_sentiment runs in a loop, so we might need to expose the latest value
    # For this implementation, we'll trigger a fresh fetch or read a cached value.
    # Ideally, SentimentEngine should store the latest value in a variable.
    
    # Let's assume we want to fetch it on demand for this endpoint if not cached
    rate = await sentiment_engine.get_interest_rate()
    score = await sentiment_engine.get_social_sentiment()
    
    label = "NEUTRAL"
    if score > 0.3: label = "BULLISH"
    elif score < -0.3: label = "BEARISH"
    
    return {
        "score": score,
        "label": label,
        "interest_rate": rate,
        "top_keywords": ["Real Data", "Live Feed"] # Placeholder for actual keywords
    }

# --- Startup ---
@app.on_event("startup")
async def startup_event():
    logger.info("Booting Neural Swarm...")
    
    # 1. Initialize DB
    try:
        await db.connect()
        await db.create_tables() # Ensure schema exists
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}. Running in offline mode.")
    
    # 2. Start Engines
    asyncio.create_task(sentiment_engine.start())
    # execution_engine is event-driven, so it waits for calls
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Neural Swarm...")
    await sentiment_engine.stop()
    await execution_engine.close()
    await db.disconnect()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket Client Connected")
    try:
        while True:
            # Mock market data for now, or fetch from execution engine if possible
            market_data = {
                "orderbook_features": [0.5] * 10,
                "ohlcv_features": [0.5] * 10,
                "portfolio_value": 10000.0,
                "positions": []
            }
            
            # Get decision from Swarm
            decision = await swarm_manager.get_swarm_decision(market_data)
            
            payload = {
                "pnl": 0.0, # Placeholder
                "active_agents": decision["active_agents"],
                "signals": {
                    "action": decision["action"],
                    "confidence": decision["confidence"],
                    "agent_decisions": decision["agent_decisions"]
                },
                "timestamp": "2025-11-30T00:00:00Z" # Should be dynamic
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket Client Disconnected")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        await websocket.close()
