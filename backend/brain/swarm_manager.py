import asyncio
import logging
from typing import Dict, Any

# Import Agents & Brain
try:
    from backend.brain.agents.rl_agent import DRLAgent
except ImportError:
    DRLAgent = None

try:
    from backend.brain.agents.dqn_agent import DQNScalperAgent
except ImportError:
    DQNScalperAgent = None

try:
    from core.risk_engine import RiskEngine
except ImportError:
    RiskEngine = None

# ✅ NEW: Import Hybrid Brain
try:
    from core.meta_brain.hybrid_brain import HybridBrain
except ImportError:
    HybridBrain = None
    print("⚠️ HybridBrain not found. Check path 'core/meta_brain/hybrid_brain.py'")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SwarmManager")

class SwarmManager:
    """
    Enhanced Swarm Manager with Hybrid AI Decision Logic.
    Logic: 60% Technical (Agents) + 40% Fundamental (AI Brain).
    """
    def __init__(self):
        self.agents = {}
        self.risk_engine = None
        self.brain = None  # The AI Brain
        
        # ✅ Decision Weights
        self.WEIGHT_TECHNICAL = 0.6
        self.WEIGHT_AI = 0.4
        
        self._initialize_system()

    def _initialize_system(self):
        logger.info("🚀 Initializing Neural Swarm System...")
        
        # 1. Load Technical Agents
        if DQNScalperAgent:
            self.agents["scalper"] = DQNScalperAgent()
        if DRLAgent:
            self.agents["trend"] = DRLAgent()
            # self.agents["trend"].load() # Uncomment if model exists
            
        # 2. Load Risk Engine
        if RiskEngine:
            self.risk_engine = RiskEngine()
            
        # 3. ✅ Load Hybrid Brain (Gemini)
        if HybridBrain:
            self.brain = HybridBrain()
        else:
            logger.warning("❌ HybridBrain module missing. Running in Technical-Only mode.")

    async def get_swarm_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous Decision Engine.
        Executes Agents (Fast) and AI Brain (Slow) in parallel.
        """
        logger.info("--- 🧠 Swarm Deliberation Started ---")
        
        # 1. Technical Analysis (Synchronous/Fast)
        tech_score = self._get_technical_score(market_data)
        
        # 2. AI Analysis (Asynchronous/Slow) - Non-blocking
        # We pass a summary string to the brain
        market_summary = f"Price: {market_data.get('price', 0)}, Vol: {market_data.get('volume', 0)}"
        
        ai_result = {"score": 0.5, "reason": "Brain Disabled"}
        if self.brain:
            # Run AI in background while doing other checks
            ai_result = await self.brain.get_market_sentiment(market_summary)
        
        ai_score = float(ai_result.get("score", 0.5))
        
        # 3. Weighted Voting Logic (The Core Update)
        # Score Range: 0.0 (Strong Sell) to 1.0 (Strong Buy)
        final_score = (tech_score * self.WEIGHT_TECHNICAL) + (ai_score * self.WEIGHT_AI)
        
        # 4. Determine Action
        action = "HOLD"
        if final_score > 0.65:
            action = "BUY"
        elif final_score < 0.35:
            action = "SELL"
            
        # 5. Risk Veto (The Safety Net)
        risk_status = "PASS"
        if self.risk_engine:
            if self.risk_engine.check_risk(market_data.get("portfolio_value", 0), []):
                logger.warning("🛡️ Risk Engine VETOED the trade!")
                action = "HOLD" if action == "BUY" else action # Prevent buying in high risk
                risk_status = "VETO"

        # Logging the logic flow
        logger.info(f"📊 Tech Score: {tech_score:.2f} | 🧠 AI Score: {ai_score:.2f} ({ai_result.get('reason')})")
        logger.info(f"⚖️ Final Score: {final_score:.2f} -> Action: {action}")

        return {
            "action": action,
            "confidence": round(final_score, 2),
            "reason": ai_result.get("reason", "Analysis Complete"),
            "risk_status": risk_status,
            "details": {
                "tech_score": tech_score,
                "ai_reason": ai_result.get("reason"),
                "risk_status": risk_status
            }
        }

    def _get_technical_score(self, market_data: dict) -> float:
        """
        Aggregates signals from Scalper and Trend agents into a 0.0-1.0 score.
        """
        votes = []
        
        # Scalper Vote (0, 1, 2 -> Hold, Buy, Sell)
        if "scalper" in self.agents:
            raw_action = self.agents["scalper"].predict(market_data.get("features", []))
            # Normalize: Sell(2)=0.0, Hold(0)=0.5, Buy(1)=1.0
            if raw_action == 1: votes.append(1.0)
            elif raw_action == 2: votes.append(0.0)
            else: votes.append(0.5)
            
        # Trend Vote
        if "trend" in self.agents:
            raw_action = self.agents["trend"].predict(market_data.get("features", []))
            if raw_action == 1: votes.append(1.0)
            elif raw_action == 2: votes.append(0.0)
            else: votes.append(0.5)
            
        if not votes:
            return 0.5 # Default Neutral
            
        return sum(votes) / len(votes)
